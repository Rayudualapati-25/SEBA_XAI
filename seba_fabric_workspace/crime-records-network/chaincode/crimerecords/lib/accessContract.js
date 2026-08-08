'use strict';

/**
 * AccessContract — the paper's access-request flow.
 *
 * RequestAccess builds the structured request (subject attributes from the
 * caller's certificate, object attributes from the ledger, environment from
 * arguments), runs the deterministic policy engine, and stores the decision
 * WITH its explanation artifact and explanation hash as one audit event.
 */

const { Contract } = require('fabric-contract-api');
const { getCaller, requireRole } = require('./util/identity');
const { validateAllowList, hashObject, sha256, SAFE_ID } = require('./util/validate');
const { evaluate } = require('./policy/policyEngine');
const { ACTIONS, ESCALATION_APPROVERS, PURPOSES } = require('./policy/policyV1');

const ACCESS_KEY = 'access';
const RECORD_KEY = 'record';

const ENV_SCHEMA = {
  purpose: { type: 'string', required: true, enum: [...PURPOSES] },
  timeWindow: { type: 'string', required: false },
  emergencyFlag: { type: 'boolean', required: false, default: false },
  courtLink: { type: 'string', required: false, pattern: SAFE_ID },
  approvalToken: { type: 'string', required: false },
};

const STATUS = Object.freeze({
  GRANTED: 'granted',
  DENIED: 'denied',
  PENDING: 'pending-escalation',
  APPROVED: 'approved-after-escalation',
  REJECTED: 'rejected-after-escalation',
});

class AccessContract extends Contract {
  constructor() {
    super('AccessContract');
  }

  _decisionKey(ctx, recordId, decisionId) {
    return ctx.stub.createCompositeKey(ACCESS_KEY, [recordId, decisionId]);
  }

  async _getDecision(ctx, recordId, decisionId) {
    const data = await ctx.stub.getState(this._decisionKey(ctx, recordId, decisionId));
    if (!data || data.length === 0) {
      throw new Error(`access decision '${decisionId}' for record '${recordId}' does not exist`);
    }
    return JSON.parse(data.toString());
  }

  /**
   * Request access to a record. Returns the stored decision event, including
   * the explanation artifact ("why was this allowed/denied/escalated?").
   */
  async RequestAccess(ctx, recordId, action, envJson) {
    const caller = getCaller(ctx);
    if (caller.role === null) {
      throw new Error('unauthorized: caller identity has no role attribute');
    }
    if (!ACTIONS.includes(action)) {
      throw new Error(`action must be one of [${ACTIONS.join(', ')}]`);
    }

    const recordData = await ctx.stub.getState(
      ctx.stub.createCompositeKey(RECORD_KEY, [recordId])
    );
    if (!recordData || recordData.length === 0) {
      throw new Error(`record '${recordId}' does not exist`);
    }
    const record = JSON.parse(recordData.toString());

    const env = validateAllowList(JSON.parse(envJson), ENV_SCHEMA, 'environment');
    const outcome = evaluate(caller, record, action, env);

    const explanation = {
      decision: outcome.decision,
      reasonCode: outcome.reasonCode,
      decisiveAttributes: outcome.decisiveAttributes,
      counterfactual: outcome.counterfactual,
      policyVersion: outcome.policyVersion,
    };

    const decisionId = ctx.stub.getTxID();
    const event = {
      docType: 'accessDecision',
      decisionId,
      recordId,
      caseId: record.caseId,
      action,
      decision: outcome.decision,
      status: outcome.decision === 'allow' ? STATUS.GRANTED
        : outcome.decision === 'deny' ? STATUS.DENIED
          : STATUS.PENDING,
      // Subject snapshot is minimized: role/context only, no personal fields.
      subject: {
        mspId: caller.mspId,
        role: caller.role,
        station: caller.station,
        jurisdiction: caller.jurisdiction,
        clearance: caller.clearance,
      },
      environment: {
        purpose: env.purpose,
        timeWindow: env.timeWindow,
        emergencyFlag: env.emergencyFlag,
        courtLink: env.courtLink,
        // Never store the raw token — only a commitment to it.
        approvalTokenHash: env.approvalToken ? sha256(env.approvalToken) : null,
      },
      explanation,
      explanationHash: hashObject(explanation),
      policyVersion: outcome.policyVersion,
      createdAtUtc: ctx.stub.getDateTimestamp().toISOString(),
    };

    await ctx.stub.putState(
      this._decisionKey(ctx, recordId, decisionId),
      Buffer.from(JSON.stringify(event))
    );
    ctx.stub.setEvent('AccessDecision', Buffer.from(JSON.stringify({
      decisionId, recordId, decision: outcome.decision, reasonCode: outcome.reasonCode,
    })));
    return JSON.stringify(event);
  }

  /** A supervisory/judicial role resolves an escalated request. */
  async ApproveEscalation(ctx, recordId, decisionId, note) {
    return this._resolveEscalation(ctx, recordId, decisionId, note, true);
  }

  async RejectEscalation(ctx, recordId, decisionId, note) {
    return this._resolveEscalation(ctx, recordId, decisionId, note, false);
  }

  async _resolveEscalation(ctx, recordId, decisionId, note, approve) {
    const caller = getCaller(ctx);
    requireRole(caller, [...ESCALATION_APPROVERS], 'ResolveEscalation');

    const event = await this._getDecision(ctx, recordId, decisionId);
    if (event.status !== STATUS.PENDING) {
      throw new Error(
        `decision '${decisionId}' is not pending escalation (status: ${event.status})`
      );
    }
    if (event.subject.mspId === caller.mspId && event.subject.role === caller.role) {
      throw new Error('unauthorized: requester role cannot approve its own escalation');
    }

    const resolved = {
      ...event,
      status: approve ? STATUS.APPROVED : STATUS.REJECTED,
      resolution: {
        decision: approve ? 'approved' : 'rejected',
        byMsp: caller.mspId,
        byRole: caller.role,
        note: typeof note === 'string' && note.length > 0 ? note.slice(0, 500) : null,
        resolvedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
        resolutionTxId: ctx.stub.getTxID(),
      },
    };
    await ctx.stub.putState(
      this._decisionKey(ctx, recordId, decisionId),
      Buffer.from(JSON.stringify(resolved))
    );
    ctx.stub.setEvent('EscalationResolved', Buffer.from(JSON.stringify({
      decisionId, recordId, approved: approve,
    })));
    return JSON.stringify(resolved);
  }

  async GetDecision(ctx, recordId, decisionId) {
    return JSON.stringify(await this._getDecision(ctx, recordId, decisionId));
  }

  async QueryDecisionsByRecord(ctx, recordId) {
    const iterator = await ctx.stub.getStateByPartialCompositeKey(ACCESS_KEY, [recordId]);
    const items = [];
    let res = await iterator.next();
    while (!res.done) {
      items.push(JSON.parse(res.value.value.toString()));
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(items);
  }

  /** Pending escalations across all records (CouchDB rich query). */
  async QueryPendingEscalations(ctx) {
    const query = {
      selector: { docType: 'accessDecision', status: STATUS.PENDING },
    };
    const iterator = await ctx.stub.getQueryResult(JSON.stringify(query));
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

module.exports = AccessContract;
module.exports.STATUS = STATUS;
