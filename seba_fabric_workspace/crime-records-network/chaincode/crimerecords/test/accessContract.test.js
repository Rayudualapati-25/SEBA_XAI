'use strict';

const { expect } = require('chai');
const chai = require('chai');
chai.use(require('chai-as-promised'));

const RecordContract = require('../lib/recordContract');
const AccessContract = require('../lib/accessContract');
const { buildMockContext, cloneInto, CALLERS, RECORD_META } = require('./testHelpers');

const records = new RecordContract();
const access = new AccessContract();

// Build a shared world: police create FIR-1, then hand the state map to a
// context whose identity is `caller`.
async function worldAs(caller, txId = 'TX-REQ') {
  const policeCtx = buildMockContext(CALLERS.inspector);
  await records.CreateCaseRecord(policeCtx, 'FIR-1', JSON.stringify(RECORD_META));
  const ctx = buildMockContext({ ...caller, txId });
  cloneInto(policeCtx, ctx);
  return ctx;
}

const ENV = JSON.stringify({ purpose: 'investigation' });

describe('AccessContract', () => {
  describe('RequestAccess', () => {
    it('grants an assigned inspector and stores the explanation artifact', async () => {
      const ctx = await worldAs(CALLERS.inspector);
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', ENV));
      expect(event.decision).to.equal('allow');
      expect(event.status).to.equal('granted');
      expect(event.explanation.reasonCode).to.equal('POLICY_SATISFIED');
      expect(event.explanationHash).to.match(/^[0-9a-f]{64}$/);
      expect(event.policyVersion).to.equal('crime-policy-v1');
      expect(ctx._events[0].name).to.equal('AccessDecision');
    });

    it('minimizes the stored subject: no badgeId, no cert identity', async () => {
      const ctx = await worldAs(CALLERS.inspector);
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', ENV));
      expect(event.subject).to.deep.equal({
        mspId: 'PoliceMSP', role: 'inspector', station: 'PS-Central',
        jurisdiction: 'district-north', clearance: 'high',
      });
      expect(JSON.stringify(event)).to.not.contain('B-1001');
    });

    it('stores only a hash of the approval token, never the raw value', async () => {
      const ctx = await worldAs({
        ...CALLERS.inspector,
        attrs: { ...CALLERS.inspector.attrs, jurisdiction: 'district-south' },
      });
      const env = JSON.stringify({
        purpose: 'investigation', emergencyFlag: true, approvalToken: 'SECRET-TOKEN-42',
      });
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', env));
      expect(event.decision).to.equal('allow');
      expect(event.environment.approvalTokenHash).to.match(/^[0-9a-f]{64}$/);
      expect(JSON.stringify(event)).to.not.contain('SECRET-TOKEN-42');
    });

    it('denies an unassigned defense counsel via RBAC with explanation', async () => {
      const ctx = await worldAs({
        mspId: 'ProsecutionMSP',
        attrs: {
          role: 'defense-counsel', jurisdiction: 'district-north',
          clearance: 'low', credentialStatus: 'active',
        },
      });
      const env = JSON.stringify({ purpose: 'defense-preparation' });
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', env));
      expect(event.decision).to.equal('deny');
      expect(event.status).to.equal('denied');
      expect(event.explanation.reasonCode).to.equal('RBAC_NO_PERMISSION');
    });

    it('escalates a constable with insufficient clearance', async () => {
      const ctx = await worldAs(CALLERS.constable);
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', ENV));
      expect(event.decision).to.equal('escalate');
      expect(event.status).to.equal('pending-escalation');
      expect(event.explanation.reasonCode).to.equal('INSUFFICIENT_CLEARANCE');
      expect(event.explanation.counterfactual).to.contain('clearance');
    });

    it('rejects unknown env fields, bad actions, roleless callers, missing records', async () => {
      const ctx = await worldAs(CALLERS.inspector);
      await expect(access.RequestAccess(ctx, 'FIR-1', 'view',
        JSON.stringify({ purpose: 'investigation', smuggled: 'x' })))
        .to.be.rejectedWith(/unknown fields/);
      await expect(access.RequestAccess(ctx, 'FIR-1', 'delete', ENV))
        .to.be.rejectedWith(/action must be one of/);
      await expect(access.RequestAccess(ctx, 'FIR-404', 'view', ENV))
        .to.be.rejectedWith(/does not exist/);
      const anon = buildMockContext({ mspId: 'PoliceMSP', attrs: {} });
      cloneInto(ctx, anon);
      await expect(access.RequestAccess(anon, 'FIR-1', 'view', ENV))
        .to.be.rejectedWith(/no role attribute/);
    });
  });

  describe('escalation resolution', () => {
    async function pendingEscalation() {
      const ctx = await worldAs(CALLERS.constable, 'TX-ESC');
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', ENV));
      expect(event.status).to.equal('pending-escalation');
      return { state: ctx, decisionId: event.decisionId };
    }

    function asCaller(caller, state, txId = 'TX-RES') {
      const ctx = buildMockContext({ ...caller, txId });
      cloneInto(state, ctx);
      return ctx;
    }

    it('lets a judge approve a pending escalation', async () => {
      const { state, decisionId } = await pendingEscalation();
      const ctx = asCaller(CALLERS.judge, state);
      const resolved = JSON.parse(
        await access.ApproveEscalation(ctx, 'FIR-1', decisionId, 'supervised review'));
      expect(resolved.status).to.equal('approved-after-escalation');
      expect(resolved.resolution.byRole).to.equal('judge');
      expect(resolved.resolution.resolutionTxId).to.equal('TX-RES');
    });

    it('lets an ombudsman reject a pending escalation', async () => {
      const { state, decisionId } = await pendingEscalation();
      const ctx = asCaller({
        mspId: 'AuditMSP',
        attrs: { role: 'ombudsman', credentialStatus: 'active' },
      }, state);
      const resolved = JSON.parse(
        await access.RejectEscalation(ctx, 'FIR-1', decisionId, ''));
      expect(resolved.status).to.equal('rejected-after-escalation');
      expect(resolved.resolution.note).to.equal(null);
    });

    it('blocks non-approver roles and double resolution', async () => {
      const { state, decisionId } = await pendingEscalation();
      const analystCtx = asCaller(CALLERS.analyst, state);
      await expect(access.ApproveEscalation(analystCtx, 'FIR-1', decisionId, ''))
        .to.be.rejectedWith(/requires role in/);
      const judgeCtx = asCaller(CALLERS.judge, state);
      await access.ApproveEscalation(judgeCtx, 'FIR-1', decisionId, '');
      await expect(access.ApproveEscalation(judgeCtx, 'FIR-1', decisionId, ''))
        .to.be.rejectedWith(/not pending escalation/);
    });

    it('blocks a role from approving its own escalation', async () => {
      // An SHO's own escalated request cannot be resolved by another SHO
      // of the same org (same msp + role as the requesting subject).
      const shoCaller = {
        mspId: 'PoliceMSP',
        attrs: {
          role: 'sho', jurisdiction: 'district-south', clearance: 'low',
          credentialStatus: 'active',
        },
      };
      const ctx = await worldAs(shoCaller, 'TX-SHO');
      const event = JSON.parse(await access.RequestAccess(ctx, 'FIR-1', 'view', ENV));
      expect(event.status).to.equal('pending-escalation');
      const otherSho = asCaller(shoCaller, ctx);
      await expect(access.ApproveEscalation(otherSho, 'FIR-1', event.decisionId, ''))
        .to.be.rejectedWith(/cannot approve its own escalation/);
    });
  });

  describe('queries', () => {
    it('returns decisions by record and pending escalations', async () => {
      const ctx = await worldAs(CALLERS.constable, 'TX-Q1');
      await access.RequestAccess(ctx, 'FIR-1', 'view', ENV);
      const byRecord = JSON.parse(await access.QueryDecisionsByRecord(ctx, 'FIR-1'));
      expect(byRecord).to.have.length(1);
      const pending = JSON.parse(await access.QueryPendingEscalations(ctx));
      expect(pending).to.have.length(1);
      expect(pending[0].status).to.equal('pending-escalation');
    });

    it('errors on a missing decision id', async () => {
      const ctx = await worldAs(CALLERS.inspector);
      await expect(access.GetDecision(ctx, 'FIR-1', 'TX-NOPE'))
        .to.be.rejectedWith(/does not exist/);
    });
  });
});
