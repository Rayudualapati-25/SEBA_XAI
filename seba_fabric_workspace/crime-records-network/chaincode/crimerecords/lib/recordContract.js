'use strict';

/**
 * RecordContract — crime record registry.
 *
 * Fabric stores governed metadata and a SHA-256 commitment. Raw sensitive
 * content stays in agency-controlled off-chain storage. Evidence detail uses
 * a Fabric private data collection.
 */

const { Contract } = require('fabric-contract-api');
const { MSP, getCaller, requireMsp, requireRole } = require('./util/identity');
const { validateAllowList, sha256, SHA256_HEX, SAFE_ID } = require('./util/validate');
const { ROLES, RECORD_TYPES, SENSITIVITY } = require('./policy/policyV1');

const RECORD_KEY = 'record';
const ACCESS_KEY = 'accessDecision';
const CASE_KEY = 'case';
const OFFCHAIN_REFERENCE = /^vault:\/\/[a-z]+\/[A-Za-z0-9._-]{1,128}$/;
const EVIDENCE_KEY = 'evidence';
const CUSTODY_KEY = 'custodyEvent';
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
  owningAgency: { type: 'string', required: true, pattern: SAFE_ID },
  jurisdiction: { type: 'string', required: true, pattern: SAFE_ID },
  victimProtectionFlag: { type: 'boolean', required: false, default: false },
  contentHash: { type: 'string', required: true, pattern: SHA256_HEX },
  offChainReference: { type: 'string', required: true, pattern: OFFCHAIN_REFERENCE },
  status: {
    type: 'string', required: false, enum: ['active', 'archived'], default: 'active',
  },
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

  /** Police officers file governed metadata and an off-chain commitment. */
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
    const caseData = await ctx.stub.getState(
      ctx.stub.createCompositeKey(CASE_KEY, [meta.caseId])
    );
    if (!caseData || caseData.length === 0) {
      throw new Error(`case '${meta.caseId}' does not exist`);
    }
    const caseAsset = JSON.parse(caseData.toString());
    if (caseAsset.owningAgency !== meta.owningAgency
        || caseAsset.jurisdiction !== meta.jurisdiction) {
      throw new Error('record ownership and jurisdiction must match its case');
    }
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
  // Do not use JavaScript default parameters here: Fabric Contract API uses
  // function.length to build transaction metadata and would expose only the
  // parameters before the first default.
  async AttachEvidenceHash(ctx, recordId, evidenceId, evidenceHash,
    source, offChainReference) {
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
      source: String(source || 'unspecified').slice(0, 200),
      offChainReference: offChainReference || null,
      currentCustodianMsp: caller.mspId,
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

  /** Append a custody transfer and update only the current custodian pointer. */
  async TransferEvidenceCustody(ctx, recordId, evidenceId, toMsp, reason) {
    const caller = getCaller(ctx);
    const allowedCustodians = [MSP.POLICE, MSP.FORENSICS, MSP.COURT];
    requireMsp(caller, allowedCustodians, 'TransferEvidenceCustody');
    if (!allowedCustodians.includes(toMsp)) {
      throw new Error(`toMsp must be one of [${allowedCustodians.join(', ')}]`);
    }
    const key = ctx.stub.createCompositeKey(EVIDENCE_KEY, [recordId, evidenceId]);
    const data = await ctx.stub.getState(key);
    if (!data || data.length === 0) {
      throw new Error(`evidence '${evidenceId}' does not exist on record '${recordId}'`);
    }
    const evidence = JSON.parse(data.toString());
    if (evidence.currentCustodianMsp !== caller.mspId) {
      throw new Error('unauthorized: only the current custodian may transfer evidence');
    }
    const timestamp = ctx.stub.getDateTimestamp().toISOString();
    const event = {
      docType: 'custodyEvent', recordId, evidenceId,
      fromMsp: caller.mspId, toMsp,
      reason: String(reason || '').slice(0, 500),
      actorIdentity: caller.id, actorRole: caller.role,
      timestamp, txId: ctx.stub.getTxID(),
    };
    await ctx.stub.putState(key, Buffer.from(JSON.stringify({
      ...evidence, currentCustodianMsp: toMsp,
      custodyChangedAtUtc: timestamp, txId: event.txId,
    })));
    await ctx.stub.putState(
      ctx.stub.createCompositeKey(CUSTODY_KEY, [recordId, evidenceId, timestamp, event.txId]),
      Buffer.from(JSON.stringify(event))
    );
    ctx.stub.setEvent('EvidenceCustodyTransferred', Buffer.from(JSON.stringify({
      recordId, evidenceId, fromMsp: caller.mspId, toMsp,
    })));
    return JSON.stringify(event);
  }

  async QueryEvidenceCustody(ctx, recordId, evidenceId) {
    const iterator = await ctx.stub.getStateByPartialCompositeKey(
      CUSTODY_KEY, [recordId, evidenceId]
    );
    const items = [];
    let result = await iterator.next();
    while (!result.done) {
      items.push(JSON.parse(result.value.value.toString()));
      result = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(items);
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

  /**
   * Confirm that the exact X.509 identity has a granted decision and return
   * the governed reference/hash needed by the backend to release raw content.
   * No raw content is returned by chaincode.
   */
  async AuthorizeRecordRead(ctx, recordId) {
    const record = await this._getRecord(ctx, recordId);
    const caller = getCaller(ctx);
    const identityHash = sha256(caller.id);
    const iterator = await ctx.stub.getStateByPartialCompositeKey(ACCESS_KEY, [recordId]);
    let grantedByDecision = null;
    let res = await iterator.next();
    while (!res.done) {
      const decision = JSON.parse(res.value.value.toString());
      if (decision.subject && decision.subject.identityHash === identityHash
          && (decision.status === 'granted'
            || decision.status === 'approved-after-escalation')) {
        grantedByDecision = decision.decisionId;
        break;
      }
      res = await iterator.next();
    }
    await iterator.close();
    if (!grantedByDecision) {
      throw new Error('unauthorized: no granted access decision for this identity');
    }

    return JSON.stringify({
      recordId,
      offChainReference: record.offChainReference,
      contentHash: record.contentHash,
      grantedByDecision,
    });
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
