'use strict';

const { expect } = require('chai');
const chai = require('chai');
chai.use(require('chai-as-promised'));

const RecordContract = require('../lib/recordContract');
const AccessContract = require('../lib/accessContract');
const AuditContract = require('../lib/auditContract');
const { buildMockContext, cloneInto, seedCase, CALLERS, RECORD_META } = require('./testHelpers');

const records = new RecordContract();
const access = new AccessContract();
const audit = new AuditContract();

async function worldWithDecision() {
  const policeCtx = buildMockContext(CALLERS.inspector);
  await seedCase(policeCtx, 'CASE-1', { assignedUsers: [CALLERS.inspector.identityId] });
  await policeCtx.stub.putState(
    policeCtx.stub.createCompositeKey('user', [CALLERS.inspector.identityId]),
    Buffer.from(JSON.stringify({
      docType: 'user', userId: CALLERS.inspector.identityId,
      fabricUser: CALLERS.inspector.identityId, org: 'police',
      role: CALLERS.inspector.attrs.role,
      rank: CALLERS.inspector.attrs.rank,
      station: CALLERS.inspector.attrs.station,
      jurisdiction: CALLERS.inspector.attrs.jurisdiction,
      clearance: CALLERS.inspector.attrs.clearance,
      credentialStatus: 'active',
    }))
  );
  await records.CreateCaseRecord(policeCtx, 'FIR-1', JSON.stringify(RECORD_META));
  const event = JSON.parse(await access.RequestAccess(
    policeCtx, 'FIR-1', 'view', JSON.stringify({ purpose: 'investigation' })));
  return { state: policeCtx, event };
}

function asCaller(caller, state) {
  const ctx = buildMockContext(caller);
  cloneInto(state, ctx);
  return ctx;
}

describe('AuditContract', () => {
  describe('VerifyExplanation', () => {
    it('matches an untampered artifact against the ledger hash', async () => {
      const { state, event } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      const result = JSON.parse(await audit.VerifyExplanation(
        ctx, 'FIR-1', event.decisionId, JSON.stringify(event.explanation)));
      expect(result.match).to.equal(true);
      expect(result.storedHash).to.equal(event.explanationHash);
    });

    it('catches a substituted explanation (explanation-hash substitution attack)', async () => {
      const { state, event } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      const tampered = { ...event.explanation, reasonCode: 'POLICY_SATISFIED_v2' };
      const result = JSON.parse(await audit.VerifyExplanation(
        ctx, 'FIR-1', event.decisionId, JSON.stringify(tampered)));
      expect(result.match).to.equal(false);
    });

    it('is key-order independent (canonical hashing)', async () => {
      const { state, event } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      const reordered = {};
      for (const key of Object.keys(event.explanation).sort().reverse()) {
        reordered[key] = event.explanation[key];
      }
      const result = JSON.parse(await audit.VerifyExplanation(
        ctx, 'FIR-1', event.decisionId, JSON.stringify(reordered)));
      expect(result.match).to.equal(true);
    });

    it('errors for an unknown decision', async () => {
      const { state } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      await expect(audit.VerifyExplanation(ctx, 'FIR-1', 'TX-NOPE', '{}'))
        .to.be.rejectedWith(/does not exist/);
    });
  });

  describe('VerifyRecordPayload', () => {
    it('confirms a matching payload hash and flags a tampered one', async () => {
      const { state } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      const good = JSON.parse(await audit.VerifyRecordPayload(
        ctx, 'FIR-1', RECORD_META.contentHash));
      expect(good.match).to.equal(true);
      const bad = JSON.parse(await audit.VerifyRecordPayload(
        ctx, 'FIR-1', 'f'.repeat(64)));
      expect(bad.match).to.equal(false);
    });

    it('errors for an unknown record', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      await expect(audit.VerifyRecordPayload(ctx, 'FIR-404', 'a'.repeat(64)))
        .to.be.rejectedWith(/does not exist/);
    });
  });

  describe('direct-ledger access events', () => {
    it('derives the actor from the signing identity and stores the event', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      const event = JSON.parse(await audit.RecordAccessEvent(
        ctx, 'record.read', JSON.stringify({ recordId: 'FIR-1' }), 'ok', '200'));
      expect(event.actorUsername).to.equal('insp.test');
      expect(event.actorMsp).to.equal('PoliceMSP');
      expect(event.action).to.equal('record.read');
      expect(ctx._events[0].name).to.equal('ApplicationAccessRecorded');
    });

    it('allows reviewers to query and rejects ordinary departments', async () => {
      const state = buildMockContext(CALLERS.inspector);
      await audit.RecordAccessEvent(state, 'record.read', '{}', 'ok', '200');
      const reviewer = asCaller(CALLERS.auditor, state);
      const events = JSON.parse(await audit.QueryAccessEvents(reviewer, '50'));
      expect(events).to.have.length(1);
      await expect(audit.QueryAccessEvents(state, '50'))
        .to.be.rejectedWith(/requires membership in/);
    });

    it('rejects malformed event fields and limits', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await expect(audit.RecordAccessEvent(ctx, 'bad action!', '{}', 'ok', '200'))
        .to.be.rejectedWith(/action/);
      await expect(audit.RecordAccessEvent(ctx, 'record.read', '{}', 'maybe', '200'))
        .to.be.rejectedWith(/outcome/);
      await expect(audit.RecordAccessEvent(ctx, 'record.read', '{}', 'ok', '999'))
        .to.be.rejectedWith(/statusCode/);
      const reviewer = buildMockContext(CALLERS.auditor);
      await expect(audit.QueryAccessEvents(reviewer, '0')).to.be.rejectedWith(/limit/);
    });
  });

  describe('GetAuditTrail', () => {
    it('reconstructs record history + decisions for an auditor', async () => {
      const { state, event } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      const trail = JSON.parse(await audit.GetAuditTrail(ctx, 'FIR-1'));
      expect(trail.record.recordId).to.equal('FIR-1');
      expect(trail.recordHistory).to.have.length(1);
      expect(trail.accessRequests).to.have.length(1);
      expect(trail.accessDecisions).to.have.length(1);
      expect(trail.approvals).to.deep.equal([]);
      expect(trail.accessDecisions[0].decisionId).to.equal(event.decisionId);
      expect(trail.accessDecisions[0].explanation).to.exist;
    });

    it('is limited to reviewer orgs', async () => {
      const { state } = await worldWithDecision();
      const ctx = asCaller(CALLERS.analyst, state);
      await expect(audit.GetAuditTrail(ctx, 'FIR-1'))
        .to.be.rejectedWith(/requires membership in/);
    });

    it('errors for an unknown record', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      await expect(audit.GetAuditTrail(ctx, 'FIR-404'))
        .to.be.rejectedWith(/does not exist/);
    });
  });
});
