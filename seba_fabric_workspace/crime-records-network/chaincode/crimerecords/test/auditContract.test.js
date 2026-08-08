'use strict';

const { expect } = require('chai');
const chai = require('chai');
chai.use(require('chai-as-promised'));

const RecordContract = require('../lib/recordContract');
const AccessContract = require('../lib/accessContract');
const AuditContract = require('../lib/auditContract');
const { buildMockContext, cloneInto, CALLERS, RECORD_META } = require('./testHelpers');

const records = new RecordContract();
const access = new AccessContract();
const audit = new AuditContract();

async function worldWithDecision() {
  const policeCtx = buildMockContext(CALLERS.inspector);
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
        ctx, 'FIR-1', RECORD_META.payloadHash));
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

  describe('AnchorAccessLog', () => {
    const HEAD = 'a'.repeat(64);
    const HEAD2 = 'b'.repeat(64);

    it('lets an auditor anchor the off-chain log head', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      const anchor = JSON.parse(await audit.AnchorAccessLog(ctx, '25', HEAD, '25', 'ep-test'));
      expect(anchor.seqNo).to.equal(25);
      expect(anchor.headHash).to.equal(HEAD);
      expect(anchor.anchoredByMsp).to.equal('AuditMSP');
      expect(ctx._events[0].name).to.equal('AccessLogAnchored');
    });

    it('is restricted to the oversight organization', async () => {
      const ctx = buildMockContext(CALLERS.inspector);
      await expect(audit.AnchorAccessLog(ctx, '25', HEAD, '25', 'ep-test'))
        .to.be.rejectedWith(/requires membership in \[AuditMSP\]/);
    });

    it('refuses a sequence number that does not advance', async () => {
      // Re-anchoring an older head is how an attacker would try to hide the
      // entries written after it.
      const ctx = buildMockContext(CALLERS.auditor);
      await audit.AnchorAccessLog(ctx, '50', HEAD, '50', 'ep-test');
      await expect(audit.AnchorAccessLog(ctx, '50', HEAD2, '50', 'ep-test'))
        .to.be.rejectedWith(/must advance/);
      await expect(audit.AnchorAccessLog(ctx, '20', HEAD2, '20', 'ep-test'))
        .to.be.rejectedWith(/must advance/);
    });

    it('rejects malformed hashes and counts', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      await expect(audit.AnchorAccessLog(ctx, '1', 'not-a-hash', '1', 'ep-test'))
        .to.be.rejectedWith(/sha256/);
      await expect(audit.AnchorAccessLog(ctx, '0', HEAD, '1', 'ep-test'))
        .to.be.rejectedWith(/seqNo must be a positive integer/);
      await expect(audit.AnchorAccessLog(ctx, '1', HEAD, 'x', 'ep-test'))
        .to.be.rejectedWith(/entryCount must be a positive integer/);
    });

    it('returns null before anything is anchored, then the newest anchor', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      expect(JSON.parse(await audit.GetLatestAccessLogAnchor(ctx))).to.equal(null);
      await audit.AnchorAccessLog(ctx, '10', HEAD, '10', 'ep-test');
      await audit.AnchorAccessLog(ctx, '20', HEAD2, '10', 'ep-test');
      const latest = JSON.parse(await audit.GetLatestAccessLogAnchor(ctx));
      expect(latest.seqNo).to.equal(20);
    });

    it('lets a new epoch restart the sequence, and records which epoch', async () => {
      // Recreating the off-chain log legitimately restarts numbering. The epoch
      // change is permanently visible on-chain, so a wipe cannot be hidden.
      const ctx = buildMockContext(CALLERS.auditor);
      await audit.AnchorAccessLog(ctx, '80', HEAD, '80', 'ep-first');
      const restarted = JSON.parse(
        await audit.AnchorAccessLog(ctx, '5', HEAD2, '5', 'ep-second'));
      expect(restarted.seqNo).to.equal(5);
      expect(restarted.epoch).to.equal('ep-second');
      const anchors = JSON.parse(await audit.GetAccessLogAnchors(ctx));
      expect(anchors.map((a) => a.epoch)).to.deep.equal(['ep-first', 'ep-second']);
    });

    it('requires an epoch identifier', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      await expect(audit.AnchorAccessLog(ctx, '1', HEAD, '1', ''))
        .to.be.rejectedWith(/epoch is required/);
    });

    it('keeps every past anchor, so older ranges stay checkable', async () => {
      const ctx = buildMockContext(CALLERS.auditor);
      await audit.AnchorAccessLog(ctx, '10', HEAD, '10', 'ep-test');
      await audit.AnchorAccessLog(ctx, '20', HEAD2, '10', 'ep-test');
      const anchors = JSON.parse(await audit.GetAccessLogAnchors(ctx));
      expect(anchors.map((a) => a.seqNo)).to.deep.equal([10, 20]);
    });
  });

  describe('GetAuditTrail', () => {
    it('reconstructs record history + decisions for an auditor', async () => {
      const { state, event } = await worldWithDecision();
      const ctx = asCaller(CALLERS.auditor, state);
      const trail = JSON.parse(await audit.GetAuditTrail(ctx, 'FIR-1'));
      expect(trail.record.recordId).to.equal('FIR-1');
      expect(trail.recordHistory).to.have.length(1);
      expect(trail.accessDecisions).to.have.length(1);
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
