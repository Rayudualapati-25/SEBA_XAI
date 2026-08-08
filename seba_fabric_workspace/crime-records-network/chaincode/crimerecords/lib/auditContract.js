'use strict';

/**
 * AuditContract — verification and reconstruction for reviewers.
 *
 * Fixes the "caller-supplied vs caller-supplied" anchor check from the
 * previous chaincode: verification always recomputes from LEDGER state and
 * compares against what the caller claims to hold, never claim-vs-claim.
 */

const { Contract } = require('fabric-contract-api');
const { MSP, getCaller, requireMsp } = require('./util/identity');
const { hashObject, SHA256_HEX, SAFE_ID } = require('./util/validate');

const ACCESS_KEY = 'access';
const RECORD_KEY = 'record';

// Single key holding the newest access-log anchor. Fabric keeps the history of
// every key, so getHistoryForKey on this one key returns every anchor ever
// written — no composite keys or indexes needed.
const ACCESS_LOG_HEAD = 'accessLogHead';

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
   * Verify an off-chain record payload against its on-chain commitment.
   * The claimed hash is recomputed by the CLIENT over the payload it holds;
   * the reference hash always comes from ledger state.
   */
  async VerifyRecordPayload(ctx, recordId, payloadHashHex) {
    const key = ctx.stub.createCompositeKey(RECORD_KEY, [recordId]);
    const data = await ctx.stub.getState(key);
    if (!data || data.length === 0) {
      throw new Error(`record '${recordId}' does not exist`);
    }
    const record = JSON.parse(data.toString());
    return JSON.stringify({
      match: record.payloadHash === payloadHashHex,
      storedHash: record.payloadHash,
    });
  }

  /**
   * Commit the head hash of the off-chain access log to the ledger.
   *
   * The access log (who searched, who read a record, who received a case file)
   * lives off-chain as a hash chain, because writing a blockchain transaction
   * per search would be far too slow. Anchoring its head hash here binds that
   * chain to the ledger: the log cannot be rewritten afterwards without
   * contradicting an anchor that is already immutable.
   *
   * Oversight function, so AuditMSP only. The sequence number must advance,
   * otherwise an attacker could re-anchor an older head to hide later entries.
   */
  async AnchorAccessLog(ctx, seqNo, headHash, entryCount, epoch) {
    const caller = getCaller(ctx);
    requireMsp(caller, [MSP.AUDIT], 'AnchorAccessLog');

    const seq = Number(seqNo);
    const count = Number(entryCount);
    if (!Number.isInteger(seq) || seq < 1) {
      throw new Error('seqNo must be a positive integer');
    }
    if (!Number.isInteger(count) || count < 1) {
      throw new Error('entryCount must be a positive integer');
    }
    if (!SHA256_HEX.test(headHash)) {
      throw new Error('headHash must be a sha256 hex digest');
    }
    if (!SAFE_ID.test(epoch || '')) {
      throw new Error('epoch is required and must be a simple identifier');
    }

    // The epoch identifies one continuous run of the log. If the off-chain log
    // is ever recreated the epoch changes, and the sequence may legitimately
    // restart. That is allowed but never hidden: every epoch ever anchored stays
    // in this key's history, so an auditor can see the log was reset and when.
    const existing = await ctx.stub.getState(ACCESS_LOG_HEAD);
    if (existing && existing.length > 0) {
      const previous = JSON.parse(existing.toString());
      if (previous.epoch === epoch && seq <= previous.seqNo) {
        throw new Error(
          `seqNo must advance within an epoch: ${seq} is not greater than the anchored ${previous.seqNo}`
        );
      }
    }

    const anchor = {
      docType: 'accessLogAnchor',
      epoch,
      seqNo: seq,
      headHash,
      entryCount: count,
      anchoredByMsp: caller.mspId,
      anchoredAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      txId: ctx.stub.getTxID(),
    };
    await ctx.stub.putState(ACCESS_LOG_HEAD, Buffer.from(JSON.stringify(anchor)));
    ctx.stub.setEvent('AccessLogAnchored', Buffer.from(JSON.stringify({
      seqNo: seq, headHash,
    })));
    return JSON.stringify(anchor);
  }

  /** The newest anchor, or null if the log has never been anchored. */
  async GetLatestAccessLogAnchor(ctx) {
    const data = await ctx.stub.getState(ACCESS_LOG_HEAD);
    if (!data || data.length === 0) return JSON.stringify(null);
    return data.toString();
  }

  /**
   * Every anchor ever written, oldest first. Comes free from Fabric's key
   * history, so an auditor can check the log against each historical anchor
   * rather than only the newest one.
   */
  async GetAccessLogAnchors(ctx) {
    const iterator = await ctx.stub.getHistoryForKey(ACCESS_LOG_HEAD);
    const anchors = [];
    let res = await iterator.next();
    while (!res.done) {
      if (res.value.value.length > 0) {
        anchors.push({
          txId: res.value.txId,
          ...JSON.parse(res.value.value.toString()),
        });
      }
      res = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(anchors);
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

    return JSON.stringify({
      recordId,
      record: JSON.parse(recordData.toString()),
      recordHistory: history,
      accessDecisions: decisions,
      generatedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
    });
  }
}

module.exports = AuditContract;
