'use strict';

/**
 * AuditContract — verification and reconstruction for reviewers.
 *
 * Record verification and authenticated application-access events are both
 * derived from Fabric state. There is no external audit-log database to
 * anchor or reconcile.
 */

const { Contract } = require('fabric-contract-api');
const { MSP, getCaller, requireMsp } = require('./util/identity');
const { hashObject, SAFE_ID } = require('./util/validate');

const REQUEST_KEY = 'accessRequest';
const ACCESS_KEY = 'accessDecision';
const APPROVAL_KEY = 'approval';
const RECORD_KEY = 'record';
const ACCESS_EVENT_KEY = 'accessEvent';

// Reviewer orgs: auditors, the court, and prosecution can reconstruct trails.
const REVIEWER_MSPS = [MSP.AUDIT, MSP.COURT, MSP.PROSECUTION];

class AuditContract extends Contract {
  constructor() {
    super('AuditContract');
  }

  /**
   * Verify that an explanation artifact a reviewer holds off-chain still
   * matches the hash committed at decision time. The stored hash comes from
   * the ledger; only the artifact under test comes from the caller.
   * Returns { match, storedHash, computedHash }.
   */
  async VerifyExplanation(ctx, recordId, decisionId, artifactJson) {
    const key = ctx.stub.createCompositeKey(ACCESS_KEY, [recordId, decisionId]);
    const data = await ctx.stub.getState(key);
    if (!data || data.length === 0) {
      throw new Error(`access decision '${decisionId}' for record '${recordId}' does not exist`);
    }
    const event = JSON.parse(data.toString());
    const computedHash = hashObject(JSON.parse(artifactJson));
    return JSON.stringify({
      match: computedHash === event.explanationHash,
      storedHash: event.explanationHash,
      computedHash,
    });
  }

  /**
   * Compare the hash recomputed by the backend over agency-held raw content
   * with the immutable commitment in Fabric metadata.
   */
  async VerifyRecordPayload(ctx, recordId, contentHash) {
    const key = ctx.stub.createCompositeKey(RECORD_KEY, [recordId]);
    const data = await ctx.stub.getState(key);
    if (!data || data.length === 0) {
      throw new Error(`record '${recordId}' does not exist`);
    }
    const record = JSON.parse(data.toString());
    return JSON.stringify({
      match: record.contentHash === contentHash,
      storedHash: record.contentHash,
      computedHash: contentHash,
      storage: 'agency-controlled-off-chain-vault',
    });
  }

  /**
   * Commit one authenticated API access event. The actor is always derived
   * from the signing certificate; callers cannot name a different actor.
   */
  async RecordAccessEvent(ctx, action, targetJson, outcome, statusCode) {
    const caller = getCaller(ctx);
    if (!SAFE_ID.test(action || '')) {
      throw new Error('action must be a simple identifier');
    }
    if (!['ok', 'failed', 'refused', 'rejected', 'error'].includes(outcome)) {
      throw new Error('outcome is invalid');
    }
    const status = Number(statusCode);
    if (!Number.isInteger(status) || status < 100 || status > 599) {
      throw new Error('statusCode must be an HTTP status integer');
    }
    let target = null;
    try {
      target = JSON.parse(targetJson);
    } catch {
      throw new Error('target must be valid JSON');
    }
    if (Buffer.byteLength(targetJson, 'utf8') > 2048) {
      throw new Error('target exceeds 2048 byte limit');
    }

    const timestamp = ctx.stub.getDateTimestamp().toISOString();
    const event = {
      docType: 'applicationAccessEvent',
      actorIdentityHash: hashObject({ id: caller.id }),
      actorUsername: caller.enrollmentId,
      actorMsp: caller.mspId,
      actorRole: caller.role,
      action,
      target,
      outcome,
      status,
      timestamp,
      txId: ctx.stub.getTxID(),
    };
    const key = ctx.stub.createCompositeKey(ACCESS_EVENT_KEY, [timestamp, event.txId]);
    await ctx.stub.putState(key, Buffer.from(JSON.stringify(event)));
    ctx.stub.setEvent('ApplicationAccessRecorded', Buffer.from(JSON.stringify({
      action, outcome, txId: event.txId,
    })));
    return JSON.stringify(event);
  }

  /** Review the newest direct-ledger access events. */
  async QueryAccessEvents(ctx, limitText) {
    const caller = getCaller(ctx);
    requireMsp(caller, REVIEWER_MSPS, 'QueryAccessEvents');
    const requested = Number(limitText || 50);
    if (!Number.isInteger(requested) || requested < 1 || requested > 500) {
      throw new Error('limit must be an integer from 1 to 500');
    }
    const iterator = await ctx.stub.getStateByPartialCompositeKey(ACCESS_EVENT_KEY, []);
    const events = [];
    let res = await iterator.next();
    while (!res.done) {
      events.push(JSON.parse(res.value.value.toString()));
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(events.slice(-requested).reverse());
  }

  /**
   * Full reconstruction trace for one record: current metadata, its state
   * history, and every access decision with explanations. Reviewer orgs only.
   */
  async GetAuditTrail(ctx, recordId) {
    const caller = getCaller(ctx);
    requireMsp(caller, REVIEWER_MSPS, 'GetAuditTrail');

    const recordKey = ctx.stub.createCompositeKey(RECORD_KEY, [recordId]);
    const recordData = await ctx.stub.getState(recordKey);
    if (!recordData || recordData.length === 0) {
      throw new Error(`record '${recordId}' does not exist`);
    }

    const history = [];
    const histIterator = await ctx.stub.getHistoryForKey(recordKey);
    let res = await histIterator.next();
    while (!res.done) {
      history.push({
        txId: res.value.txId,
        value: res.value.value.length > 0
          ? JSON.parse(res.value.value.toString())
          : null,
      });
      res = await histIterator.next();
    }
    await histIterator.close();

    const decisions = [];
    const decIterator = await ctx.stub.getStateByPartialCompositeKey(ACCESS_KEY, [recordId]);
    res = await decIterator.next();
    while (!res.done) {
      decisions.push(JSON.parse(res.value.value.toString()));
      res = await decIterator.next();
    }
    await decIterator.close();

    const requests = [];
    for (const decision of decisions) {
      const requestData = await ctx.stub.getState(
        ctx.stub.createCompositeKey(REQUEST_KEY, [decision.requestId])
      );
      if (requestData && requestData.length > 0) {
        requests.push(JSON.parse(requestData.toString()));
      }
    }

    const approvals = [];
    for (const request of requests) {
      const approvalIterator = await ctx.stub.getStateByPartialCompositeKey(
        APPROVAL_KEY, [request.requestId]
      );
      let approvalResult = await approvalIterator.next();
      while (!approvalResult.done) {
        approvals.push(JSON.parse(approvalResult.value.value.toString()));
        approvalResult = await approvalIterator.next();
      }
      await approvalIterator.close();
    }

    return JSON.stringify({
      recordId,
      record: JSON.parse(recordData.toString()),
      recordHistory: history,
      accessRequests: requests,
      accessDecisions: decisions,
      approvals,
      generatedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
    });
  }
}

module.exports = AuditContract;
