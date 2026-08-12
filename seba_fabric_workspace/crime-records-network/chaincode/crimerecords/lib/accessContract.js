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
const { MSP, getCaller, requireRole } = require('./util/identity');
const { validateAllowList, hashObject, sha256, SAFE_ID } = require('./util/validate');
const { evaluate } = require('./policy/policyEngine');
const {
  ACTIONS, ESCALATION_APPROVERS, PURPOSES, POLICY_VERSION,
} = require('./policy/policyV1');

const REQUEST_KEY = 'accessRequest';
const ACCESS_KEY = 'accessDecision';
const APPROVAL_KEY = 'approval';
const RECORD_KEY = 'record';
const USER_KEY = 'user';
const CASE_KEY = 'case';
const ACTIVE_POLICY_KEY = 'activePolicyVersion';

const ORG_TO_MSP = Object.freeze({
  police: MSP.POLICE,
  forensics: MSP.FORENSICS,
  prosecution: MSP.PROSECUTION,
  court: MSP.COURT,
  audit: MSP.AUDIT,
});

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
   * Bind the certificate to its active UserProfile, then derive assignment
   * from the current Case asset. Certificate attributes remain the
   * cryptographic identity source; Fabric state supplies revocation and
   * mutable governance facts that must take effect without reissuing a cert.
   */
  async _governedSubject(ctx, caller, record) {
    if (!caller.enrollmentId) {
      throw new Error('unauthorized: caller certificate has no enrollment identity');
    }
    const userData = await ctx.stub.getState(
      ctx.stub.createCompositeKey(USER_KEY, [caller.enrollmentId])
    );
    if (!userData || userData.length === 0) {
      throw new Error('unauthorized: caller has no UserProfile on the ledger');
    }
    const user = JSON.parse(userData.toString());
    if (user.fabricUser !== caller.enrollmentId
        || ORG_TO_MSP[user.org] !== caller.mspId
        || user.role !== caller.role) {
      throw new Error('unauthorized: certificate does not match the UserProfile');
    }
    for (const attribute of ['rank', 'station', 'jurisdiction', 'clearance']) {
      if (user[attribute] && caller[attribute] !== user[attribute]) {
        throw new Error(`unauthorized: certificate ${attribute} does not match UserProfile`);
      }
    }

    const caseData = await ctx.stub.getState(
      ctx.stub.createCompositeKey(CASE_KEY, [record.caseId])
    );
    if (!caseData || caseData.length === 0) {
      throw new Error(`case '${record.caseId}' does not exist`);
    }
    const caseAsset = JSON.parse(caseData.toString());
    const assigned = Array.isArray(caseAsset.assignedUsers)
      && caseAsset.assignedUsers.includes(caller.enrollmentId);
    const credentialStatus = user.credentialStatus !== 'active'
      ? user.credentialStatus
      : caller.credentialStatus !== 'active'
        ? caller.credentialStatus || 'inactive'
        : 'active';

    return Object.freeze({
      ...caller,
      credentialStatus,
      caseAssignments: assigned ? record.caseId : null,
    });
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
    const activePolicyData = await ctx.stub.getState(ACTIVE_POLICY_KEY);
    if (activePolicyData && activePolicyData.length > 0) {
      const activePolicy = JSON.parse(activePolicyData.toString());
      if (activePolicy.version !== POLICY_VERSION) {
        throw new Error(
          `active policy '${activePolicy.version}' does not match deployed policy code`
        );
      }
    }
    const subject = await this._governedSubject(ctx, caller, record);
    const outcome = evaluate(subject, record, action, env);

    const explanation = {
      decision: outcome.decision,
      reasonCode: outcome.reasonCode,
      decisiveAttributes: outcome.decisiveAttributes,
      counterfactual: outcome.counterfactual,
      policyVersion: outcome.policyVersion,
    };

    const decisionId = ctx.stub.getTxID();
    const request = {
      docType: 'accessRequest',
      requestId: decisionId,
      recordId,
      requesterIdentityHash: sha256(subject.id),
      requesterMsp: subject.mspId,
      requesterRole: subject.role,
      action,
      purpose: env.purpose,
      context: {
        timeWindow: env.timeWindow,
        emergencyFlag: env.emergencyFlag,
        courtLink: env.courtLink,
        approvalTokenHash: env.approvalToken ? sha256(env.approvalToken) : null,
      },
      status: outcome.decision === 'escalate' ? STATUS.PENDING : 'decided',
      submittedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      txId: decisionId,
    };
    const eventBase = {
      docType: 'accessDecision',
      decisionId,
      requestId: request.requestId,
      recordId,
      caseId: record.caseId,
      action,
      decision: outcome.decision,
      status: outcome.decision === 'allow' ? STATUS.GRANTED
        : outcome.decision === 'deny' ? STATUS.DENIED
          : STATUS.PENDING,
      // The one-way identity commitment binds a grant to the exact certificate
      // without placing its distinguished name in the decision record.
      subject: {
        identityHash: sha256(subject.id),
        mspId: subject.mspId,
        role: subject.role,
        station: subject.station,
        jurisdiction: subject.jurisdiction,
        clearance: subject.clearance,
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
    const event = { ...eventBase, decisionHash: hashObject(eventBase) };

    await ctx.stub.putState(
      ctx.stub.createCompositeKey(REQUEST_KEY, [request.requestId]),
      Buffer.from(JSON.stringify(request))
    );
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
    const approval = {
      docType: 'approval',
      approvalId: ctx.stub.getTxID(),
      requestId: event.requestId,
      decisionId,
      recordId,
      outcome: approve ? 'approved' : 'rejected',
      supervisorIdentityHash: sha256(caller.id),
      supervisorMsp: caller.mspId,
      supervisorRole: caller.role,
      reason: typeof note === 'string' && note.length > 0 ? note.slice(0, 500) : null,
      timestamp: ctx.stub.getDateTimestamp().toISOString(),
      status: 'active',
    };
    await ctx.stub.putState(
      this._decisionKey(ctx, recordId, decisionId),
      Buffer.from(JSON.stringify(resolved))
    );
    await ctx.stub.putState(
      ctx.stub.createCompositeKey(APPROVAL_KEY, [event.requestId, approval.approvalId]),
      Buffer.from(JSON.stringify(approval))
    );
    const requestKey = ctx.stub.createCompositeKey(REQUEST_KEY, [event.requestId]);
    const requestData = await ctx.stub.getState(requestKey);
    if (requestData && requestData.length > 0) {
      const request = JSON.parse(requestData.toString());
      await ctx.stub.putState(requestKey, Buffer.from(JSON.stringify({
        ...request,
        status: approve ? STATUS.APPROVED : STATUS.REJECTED,
        resolvedByApproval: approval.approvalId,
      })));
    }
    ctx.stub.setEvent('EscalationResolved', Buffer.from(JSON.stringify({
      decisionId, recordId, approved: approve,
    })));
    return JSON.stringify(resolved);
  }

  async GetDecision(ctx, recordId, decisionId) {
    return JSON.stringify(await this._getDecision(ctx, recordId, decisionId));
  }

  async GetRequest(ctx, requestId) {
    const data = await ctx.stub.getState(
      ctx.stub.createCompositeKey(REQUEST_KEY, [requestId])
    );
    if (!data || data.length === 0) {
      throw new Error(`access request '${requestId}' does not exist`);
    }
    return data.toString();
  }

  async QueryApprovalsByRequest(ctx, requestId) {
    const iterator = await ctx.stub.getStateByPartialCompositeKey(APPROVAL_KEY, [requestId]);
    const items = [];
    let res = await iterator.next();
    while (!res.done) {
      items.push(JSON.parse(res.value.value.toString()));
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(items);
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
