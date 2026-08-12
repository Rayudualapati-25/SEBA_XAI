'use strict';

const { expect } = require('chai');
const chai = require('chai');
chai.use(require('chai-as-promised'));

const RecordContract = require('../lib/recordContract');
const { sha256 } = require('../lib/util/validate');
const { buildMockContext, cloneInto, seedCase, CALLERS, RECORD_META } = require('./testHelpers');

const contract = new RecordContract();

async function createRecord(ctx, recordId = 'FIR-1', meta = RECORD_META) {
  const caseKey = ctx.stub.createCompositeKey('case', [meta.caseId]);
  const existingCase = await ctx.stub.getState(caseKey);
  if (!existingCase || existingCase.length === 0) await seedCase(ctx, meta.caseId);
  return contract.CreateCaseRecord(ctx, recordId, JSON.stringify(meta));
}

describe('RecordContract', () => {
  describe('CreateCaseRecord', () => {
    it('creates a record for an authorized police role', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      const stored = JSON.parse(await createRecord(ctx));
      expect(stored.recordId).to.equal('FIR-1');
      expect(stored.sealed).to.equal(false);
      expect(stored.owningMsp).to.equal('PoliceMSP');
      expect(stored.createdAtUtc).to.equal('2026-08-05T12:00:00.000Z');
      expect(ctx._events[0].name).to.equal('RecordCreated');
    });

    it('rejects non-police MSPs', async () => {
      const ctx = buildMockContext(CALLERS.analyst);
      await expect(createRecord(ctx)).to.be.rejectedWith(/requires membership in \[PoliceMSP\]/);
    });

    it('allows a constable to file (CCTNS station data entry)', async () => {
      const ctx = buildMockContext(CALLERS.constable);
      const stored = JSON.parse(await createRecord(ctx));
      expect(stored.createdByRole).to.equal('constable');
    });

    it('still rejects police roles outside the filing set', async () => {
      const ctx = buildMockContext({
        mspId: 'PoliceMSP',
        attrs: { role: 'traffic-warden', credentialStatus: 'active' },
      });
      await expect(createRecord(ctx)).to.be.rejectedWith(/requires role in/);
    });

    it('rejects a caller with no role attribute', async () => {
      const ctx = buildMockContext({ mspId: 'PoliceMSP', attrs: {} });
      await expect(createRecord(ctx)).to.be.rejectedWith(/caller role is missing/);
    });

    it('rejects unknown fields (allow-list, not denylist)', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      const meta = { ...RECORD_META, victimName: 'REAL PII' };
      await expect(createRecord(ctx, 'FIR-1', meta))
        .to.be.rejectedWith(/unknown fields not permitted: victimName/);
    });

    it('rejects a malformed content hash and a bad enum', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await expect(createRecord(ctx, 'FIR-1', { ...RECORD_META, contentHash: 'zz' }))
        .to.be.rejectedWith(/invalid format/);
      await expect(createRecord(ctx, 'FIR-1', { ...RECORD_META, sensitivityLevel: 'ultra' }))
        .to.be.rejectedWith(/must be one of/);
    });

    it('rejects non-boolean flags (type checking, not presence checking)', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await expect(createRecord(ctx, 'FIR-1', { ...RECORD_META, juvenileFlag: 'yes' }))
        .to.be.rejectedWith(/must be a boolean/);
    });

    it('rejects duplicates', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await createRecord(ctx);
      await expect(createRecord(ctx)).to.be.rejectedWith(/already exists/);
    });
  });

  describe('AttachEvidenceHash', () => {
    async function withRecord() {
      const policeCtx = buildMockContext(CALLERS.inspector);
      await createRecord(policeCtx);
      // Re-use the same backing state through a forensics identity.
      const ctx = buildMockContext(CALLERS.analyst);
      cloneInto(policeCtx, ctx);
      return ctx;
    }

    it('attaches evidence for a forensics analyst', async () => {
      const ctx = await withRecord();
      const out = JSON.parse(await contract.AttachEvidenceHash(
        ctx, 'FIR-1', 'EV-1', 'b'.repeat(64)));
      expect(out.evidenceHash).to.equal('b'.repeat(64));
      expect(out.labMsp).to.equal('ForensicsMSP');
    });

    it('writes transient detail to the private collection only', async () => {
      const ctx = await withRecord();
      ctx._setTransient(new Map([['evidenceDetail', Buffer.from('DNA profile detail')]]));
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'b'.repeat(64));
      const pdcKeys = [...ctx._privateState.keys()];
      expect(pdcKeys).to.have.length(1);
      expect(pdcKeys[0]).to.match(/^evidenceDetails:/);
      // Public state must not contain the detail text.
      const publicJson = [...ctx._state.values()].join(' ');
      expect(publicJson).to.not.contain('DNA profile detail');
    });

    it('rejects police callers and bad hashes', async () => {
      const ctx = await withRecord();
      const policeCtx = buildMockContext(CALLERS.inspector);
      cloneInto(ctx, policeCtx);
      await expect(contract.AttachEvidenceHash(policeCtx, 'FIR-1', 'EV-1', 'b'.repeat(64)))
        .to.be.rejectedWith(/requires membership in \[ForensicsMSP\]/);
      await expect(contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'nothex'))
        .to.be.rejectedWith(/sha256/);
    });

    it('rejects duplicate evidence ids and missing records', async () => {
      const ctx = await withRecord();
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'b'.repeat(64));
      await expect(contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'c'.repeat(64)))
        .to.be.rejectedWith(/already attached/);
      await expect(contract.AttachEvidenceHash(ctx, 'FIR-404', 'EV-2', 'b'.repeat(64)))
        .to.be.rejectedWith(/does not exist/);
    });

    it('reads private detail back for a collection member', async () => {
      const ctx = await withRecord();
      ctx._setTransient(new Map([['evidenceDetail', Buffer.from('DNA matched S-77')]]));
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'b'.repeat(64));
      const out = JSON.parse(await contract.GetEvidenceDetail(ctx, 'FIR-1', 'EV-1'));
      expect(out.detail).to.equal('DNA matched S-77');
      expect(out.readByMsp).to.equal('ForensicsMSP');
    });

    it('blocks non-collection orgs from reading private detail', async () => {
      const ctx = await withRecord();
      ctx._setTransient(new Map([['evidenceDetail', Buffer.from('DNA matched S-77')]]));
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'b'.repeat(64));
      const auditorCtx = buildMockContext(CALLERS.auditor);
      cloneInto(ctx, auditorCtx);
      await expect(contract.GetEvidenceDetail(auditorCtx, 'FIR-1', 'EV-1'))
        .to.be.rejectedWith(/requires membership in/);
    });

    it('errors when no private detail was supplied', async () => {
      const ctx = await withRecord();
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-2', 'c'.repeat(64));
      await expect(contract.GetEvidenceDetail(ctx, 'FIR-1', 'EV-2'))
        .to.be.rejectedWith(/no private detail/);
    });

    it('lists attached evidence', async () => {
      const ctx = await withRecord();
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'b'.repeat(64));
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-2', 'c'.repeat(64));
      const list = JSON.parse(await contract.ListEvidence(ctx, 'FIR-1'));
      expect(list).to.have.length(2);
    });

    it('records custody transfers and enforces the current custodian', async () => {
      const ctx = await withRecord();
      await contract.AttachEvidenceHash(
        ctx, 'FIR-1', 'EV-1', 'b'.repeat(64), 'lab intake',
        'vault://forensics/EV-1');
      const event = JSON.parse(await contract.TransferEvidenceCustody(
        ctx, 'FIR-1', 'EV-1', 'CourtMSP', 'filed as exhibit'));
      expect(event.fromMsp).to.equal('ForensicsMSP');
      expect(event.toMsp).to.equal('CourtMSP');
      const timeline = JSON.parse(await contract.QueryEvidenceCustody(ctx, 'FIR-1', 'EV-1'));
      expect(timeline).to.have.length(1);
      await expect(contract.TransferEvidenceCustody(
        ctx, 'FIR-1', 'EV-1', 'PoliceMSP', 'take back'))
        .to.be.rejectedWith(/current custodian/);
    });

    it('rejects invalid custody destinations and unknown evidence', async () => {
      const ctx = await withRecord();
      await contract.AttachEvidenceHash(ctx, 'FIR-1', 'EV-1', 'b'.repeat(64));
      await expect(contract.TransferEvidenceCustody(
        ctx, 'FIR-1', 'EV-1', 'MediaMSP', 'publish'))
        .to.be.rejectedWith(/toMsp/);
      await expect(contract.TransferEvidenceCustody(
        ctx, 'FIR-1', 'EV-404', 'CourtMSP', 'file'))
        .to.be.rejectedWith(/does not exist/);
    });
  });

  describe('SealRecord / UnsealRecord', () => {
    async function recordInCourtCtx() {
      const policeCtx = buildMockContext(CALLERS.inspector);
      await createRecord(policeCtx);
      const ctx = buildMockContext(CALLERS.judge);
      cloneInto(policeCtx, ctx);
      return ctx;
    }

    it('lets a judge seal and unseal without mutating history', async () => {
      const ctx = await recordInCourtCtx();
      const sealed = JSON.parse(await contract.SealRecord(ctx, 'FIR-1'));
      expect(sealed.sealed).to.equal(true);
      const unsealed = JSON.parse(await contract.UnsealRecord(ctx, 'FIR-1'));
      expect(unsealed.sealed).to.equal(false);
      const history = JSON.parse(await contract.GetRecordHistory(ctx, 'FIR-1'));
      expect(history.map((h) => h.value.sealed)).to.deep.equal([false, true, false]);
    });

    it('rejects double-sealing and non-court callers', async () => {
      const ctx = await recordInCourtCtx();
      await contract.SealRecord(ctx, 'FIR-1');
      await expect(contract.SealRecord(ctx, 'FIR-1')).to.be.rejectedWith(/already sealed/);
      const policeCtx = buildMockContext(CALLERS.inspector);
      cloneInto(ctx, policeCtx);
      await expect(contract.SealRecord(policeCtx, 'FIR-1'))
        .to.be.rejectedWith(/requires membership in \[CourtMSP\]/);
    });
  });

  describe('QueryRecords (case-file search)', () => {
    async function seeded() {
      const ctx = buildMockContext(CALLERS.inspector);
      await createRecord(ctx, 'FIR-1', RECORD_META);
      await createRecord(ctx, 'FIR-2', { ...RECORD_META, recordType: 'case-diary' });
      await createRecord(ctx, 'FIR-3', {
        ...RECORD_META, caseId: 'CASE-9', owningStation: 'PS-East',
      });
      return ctx;
    }

    it('finds every record belonging to a case', async () => {
      const ctx = await seeded();
      const found = JSON.parse(await contract.QueryRecords(ctx,
        JSON.stringify({ caseId: 'CASE-1' })));
      expect(found.map((r) => r.recordId).sort()).to.deep.equal(['FIR-1', 'FIR-2']);
    });

    it('combines filters', async () => {
      const ctx = await seeded();
      const found = JSON.parse(await contract.QueryRecords(ctx,
        JSON.stringify({ caseId: 'CASE-1', recordType: 'case-diary' })));
      expect(found).to.have.length(1);
      expect(found[0].recordId).to.equal('FIR-2');
    });

    it('returns an empty list when nothing matches', async () => {
      const ctx = await seeded();
      const found = JSON.parse(await contract.QueryRecords(ctx,
        JSON.stringify({ caseId: 'CASE-404' })));
      expect(found).to.deep.equal([]);
    });

    it('refuses an unfiltered search and unknown filter fields', async () => {
      const ctx = await seeded();
      await expect(contract.QueryRecords(ctx, '{}'))
        .to.be.rejectedWith(/at least one filter/);
      await expect(contract.QueryRecords(ctx, JSON.stringify({ $where: 'evil' })))
        .to.be.rejectedWith(/unknown fields/);
    });

    it('requires an identity with a role', async () => {
      const ctx = buildMockContext({ mspId: 'PoliceMSP', attrs: {} });
      await expect(contract.QueryRecords(ctx, JSON.stringify({ caseId: 'CASE-1' })))
        .to.be.rejectedWith(/no role attribute/);
    });
  });

  describe('GetRecord', () => {
    it('errors for a missing record (real-shim empty Buffer semantics)', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await expect(contract.GetRecord(ctx, 'FIR-404')).to.be.rejectedWith(/does not exist/);
      expect(await contract.RecordExists(ctx, 'FIR-404')).to.equal(false);
    });
  });

  describe('AuthorizeRecordRead', () => {
    it('returns only the governed off-chain reference after an identity-bound grant', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await createRecord(ctx);
      const decision = {
        docType: 'accessDecision', decisionId: 'D-1', recordId: 'FIR-1',
        status: 'granted',
        subject: {
          identityHash: sha256(ctx.clientIdentity.getID()),
        },
      };
      await ctx.stub.putState(
        ctx.stub.createCompositeKey('accessDecision', ['FIR-1', 'D-1']),
        Buffer.from(JSON.stringify(decision))
      );
      const result = JSON.parse(await contract.AuthorizeRecordRead(ctx, 'FIR-1'));
      expect(result.offChainReference).to.equal('vault://police/FIR-1');
      expect(result).to.not.have.property('payload');
    });

    it('rejects a caller without an identity-bound grant', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await createRecord(ctx);
      await expect(contract.AuthorizeRecordRead(ctx, 'FIR-1'))
        .to.be.rejectedWith(/no granted access decision/);
    });
  });
});
