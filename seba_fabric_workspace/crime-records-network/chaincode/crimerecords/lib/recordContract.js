'use strict';

/**
 * RecordContract — crime record registry.
 *
 * The ledger stores minimized metadata + a SHA-256 commitment of the payload;
 * raw record contents stay in agency-controlled off-chain storage. Evidence
 * detail beyond the public hash goes to the 'evidenceDetails' private data
 * collection (Police + Forensics only).
 */

const { Contract } = require('fabric-contract-api');
const { MSP, getCaller, requireMsp, requireRole } = require('./util/identity');
const { validateAllowList, SHA256_HEX, SAFE_ID } = require('./util/validate');
const { ROLES, RECORD_TYPES, SENSITIVITY } = require('./policy/policyV1');

const RECORD_KEY = 'record';
const EVIDENCE_KEY = 'evidence';
const EVIDENCE_PDC = 'evidenceDetails';
// Must mirror the collection's distribution policy in collections-config.json.
const EVIDENCE_PDC_MSPS = [MSP.POLICE, MSP.FORENSICS, MSP.COURT];

// Includes constable: in CCTNS practice, station data entry is routinely done
// by a designated constable operator. Filing is governed separately from
// reading — a constable can enter a record and still be escalated when
// requesting access to it, because access depends on clearance.
const RECORD_CREATOR_ROLES = [
  ROLES.CONSTABLE, ROLES.SUB_INSPECTOR, ROLES.INSPECTOR, ROLES.SHO,
  ROLES.INVESTIGATING_OFFICER,
];

// Fields a caller may filter on when searching. Anything else is rejected, so
// no caller-supplied CouchDB selector can reach the state database.
const SEARCH_SCHEMA = {
  caseId: { type: 'string', required: false, pattern: SAFE_ID },
  recordType: { type: 'string', required: false, enum: [...RECORD_TYPES] },
  sensitivityLevel: { type: 'string', required: false, enum: [...SENSITIVITY] },
  owningStation: { type: 'string', required: false, pattern: SAFE_ID },
  jurisdiction: { type: 'string', required: false, pattern: SAFE_ID },
  sealed: { type: 'boolean', required: false },
};
const EVIDENCE_ROLES = [ROLES.LAB_ANALYST, ROLES.LAB_DIRECTOR];
const SEAL_ROLES = [ROLES.JUDGE, ROLES.MAGISTRATE];

const RECORD_SCHEMA = {
  caseId: { type: 'string', required: true, pattern: SAFE_ID },
  recordType: { type: 'string', required: true, enum: [...RECORD_TYPES] },
  sensitivityLevel: { type: 'string', required: true, enum: [...SENSITIVITY] },
  juvenileFlag: { type: 'boolean', required: false, default: false },
  witnessFlag: { type: 'boolean', required: false, default: false },
  owningStation: { type: 'string', required: true, pattern: SAFE_ID },
  jurisdiction: { type: 'string', required: true, pattern: SAFE_ID },
  payloadHash: { type: 'string', required: true, pattern: SHA256_HEX },
  offchainUri: { type: 'string', required: true },
};

class RecordContract extends Contract {
  constructor() {
    super('RecordContract');
  }

  _recordKey(ctx, recordId) {
    return ctx.stub.createCompositeKey(RECORD_KEY, [recordId]);
  }

  async _getRecord(ctx, recordId) {
    const data = await ctx.stub.getState(this._recordKey(ctx, recordId));
    if (!data || data.length === 0) {
      throw new Error(`record '${recordId}' does not exist`);
    }
    return JSON.parse(data.toString());
  }

  async RecordExists(ctx, recordId) {
    const data = await ctx.stub.getState(this._recordKey(ctx, recordId));
    return data !== null && data.length > 0;
  }

  /** Police officers file a new record. Payload never touches the ledger. */
  async CreateCaseRecord(ctx, recordId, metaJson) {
    const caller = getCaller(ctx);
    requireMsp(caller, [MSP.POLICE], 'CreateCaseRecord');
    requireRole(caller, RECORD_CREATOR_ROLES, 'CreateCaseRecord');

    if (!SAFE_ID.test(recordId)) {
      throw new Error('recordId has invalid format');
    }
    if (await this.RecordExists(ctx, recordId)) {
      throw new Error(`record '${recordId}' already exists`);
    }

    const meta = validateAllowList(JSON.parse(metaJson), RECORD_SCHEMA, 'record');
    const record = {
      docType: 'crimeRecord',
      recordId,
      ...meta,
      sealed: false,
      owningMsp: caller.mspId,
      createdByRole: caller.role,
      createdAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      createdTxId: ctx.stub.getTxID(),
    };

    await ctx.stub.putState(
      this._recordKey(ctx, recordId), Buffer.from(JSON.stringify(record))
    );
    ctx.stub.setEvent('RecordCreated', Buffer.from(JSON.stringify({
      recordId, caseId: meta.caseId, recordType: meta.recordType,
    })));
    return JSON.stringify(record);
  }

  /**
   * Forensics attaches an evidence commitment. The public part is the hash;
   * free-text detail (if supplied) goes only to the Police+Forensics PDC via
   * transient data so it never appears on the shared ledger.
   */
  async AttachEvidenceHash(ctx, recordId, evidenceId, evidenceHash) {
    const caller = getCaller(ctx);
    requireMsp(caller, [MSP.FORENSICS], 'AttachEvidenceHash');
    requireRole(caller, EVIDENCE_ROLES, 'AttachEvidenceHash');

    if (!SAFE_ID.test(evidenceId)) {
      throw new Error('evidenceId has invalid format');
    }
    if (!SHA256_HEX.test(evidenceHash)) {
      throw new Error('evidenceHash must be a sha256 hex digest');
    }
    await this._getRecord(ctx, recordId); // must exist

    const key = ctx.stub.createCompositeKey(EVIDENCE_KEY, [recordId, evidenceId]);
    const existing = await ctx.stub.getState(key);
    if (existing && existing.length > 0) {
      throw new Error(`evidence '${evidenceId}' already attached to '${recordId}'`);
    }

    const evidence = {
      docType: 'evidence',
      recordId,
      evidenceId,
      evidenceHash,
      labMsp: caller.mspId,
      attachedByRole: caller.role,
      attachedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      txId: ctx.stub.getTxID(),
    };
    await ctx.stub.putState(key, Buffer.from(JSON.stringify(evidence)));

    const transient = ctx.stub.getTransient();
    const detail = transient.get('evidenceDetail');
    if (detail && detail.length > 0) {
      await ctx.stub.putPrivateData(EVIDENCE_PDC, key, detail);
    }

    ctx.stub.setEvent('EvidenceAttached', Buffer.from(JSON.stringify({
      recordId, evidenceId,
    })));
    return JSON.stringify(evidence);
  }

  /** Court seals a record; access to sealed records escalates in policy. */
  async SealRecord(ctx, recordId) {
    return this._setSealed(ctx, recordId, true);
  }

  async UnsealRecord(ctx, recordId) {
    return this._setSealed(ctx, recordId, false);
  }

  async _setSealed(ctx, recordId, sealed) {
    const caller = getCaller(ctx);
    requireMsp(caller, [MSP.COURT], sealed ? 'SealRecord' : 'UnsealRecord');
    requireRole(caller, SEAL_ROLES, sealed ? 'SealRecord' : 'UnsealRecord');

    const record = await this._getRecord(ctx, recordId);
    if (record.sealed === sealed) {
      throw new Error(`record '${recordId}' is already ${sealed ? 'sealed' : 'unsealed'}`);
    }
    const updated = {
      ...record,
      sealed,
      sealChangedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      sealChangedByRole: caller.role,
    };
    await ctx.stub.putState(
      this._recordKey(ctx, recordId), Buffer.from(JSON.stringify(updated))
    );
    ctx.stub.setEvent(sealed ? 'RecordSealed' : 'RecordUnsealed',
      Buffer.from(JSON.stringify({ recordId })));
    return JSON.stringify(updated);
  }

  async GetRecord(ctx, recordId) {
    return JSON.stringify(await this._getRecord(ctx, recordId));
  }

  async GetRecordHistory(ctx, recordId) {
    const iterator = await ctx.stub.getHistoryForKey(this._recordKey(ctx, recordId));
    const history = [];
    let res = await iterator.next();
    while (!res.done) {
      history.push({
        txId: res.value.txId,
        isDelete: res.value.isDelete,
        value: res.value.value.length > 0
          ? JSON.parse(res.value.value.toString())
          : null,
      });
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(history);
  }

  /**
   * Read evidence detail from the private collection. Fabric enforces
   * memberOnlyRead at the peer, but an explicit MSP check gives a clear error
   * instead of an opaque empty read for a non-member org.
   */
  async GetEvidenceDetail(ctx, recordId, evidenceId) {
    const caller = getCaller(ctx);
    requireMsp(caller, EVIDENCE_PDC_MSPS, 'GetEvidenceDetail');

    const key = ctx.stub.createCompositeKey(EVIDENCE_KEY, [recordId, evidenceId]);
    const data = await ctx.stub.getPrivateData(EVIDENCE_PDC, key);
    if (!data || data.length === 0) {
      throw new Error(
        `no private detail for evidence '${evidenceId}' on record '${recordId}'`
      );
    }
    return JSON.stringify({
      recordId,
      evidenceId,
      detail: data.toString(),
      readByMsp: caller.mspId,
    });
  }

  /**
   * Search records by case and other allow-listed metadata fields (CouchDB
   * rich query). Returns metadata only — no payloads, and no access is granted
   * by searching. Finding a record still requires a separate access request.
   */
  async QueryRecords(ctx, filtersJson) {
    const caller = getCaller(ctx);
    if (caller.role === null) {
      throw new Error('unauthorized: caller identity has no role attribute');
    }

    const filters = validateAllowList(JSON.parse(filtersJson), SEARCH_SCHEMA, 'search');
    const selector = { docType: 'crimeRecord' };
    for (const [field, value] of Object.entries(filters)) {
      if (value !== null) selector[field] = value;
    }
    if (Object.keys(selector).length === 1) {
      throw new Error('search: at least one filter is required');
    }

    const iterator = await ctx.stub.getQueryResult(JSON.stringify({ selector }));
    const items = [];
    let res = await iterator.next();
    while (!res.done) {
      items.push(JSON.parse(res.value.value.toString()));
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(items);
  }

  async ListEvidence(ctx, recordId) {
    const iterator = await ctx.stub.getStateByPartialCompositeKey(
      EVIDENCE_KEY, [recordId]
    );
    const items = [];
    let res = await iterator.next();
    while (!res.done) {
      items.push(JSON.parse(res.value.value.toString()));
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(items);
  }
}

module.exports = RecordContract;
