'use strict';

/**
 * Tests for the tamper-evident access log.
 * Pure hash logic against an in-memory store — no network, no Ollama needed.
 */

const { expect } = require('chai');
const accessLog = require('../src/audit/accessLog');
const { describe: describeRequest } = require('../src/middleware/accessLogger');

/** Minimal stand-in for the SQLite helpers, so tests need no database. */
function makeStore() {
  const rows = [];
  return {
    rows,
    getAccessLogHead: () =>
      (rows.length ? { seq: rows[rows.length - 1].seq, entry_hash: rows[rows.length - 1].entry_hash } : undefined),
    appendAccessLogEntry: (e) => rows.push({
      seq: e.seq,
      ts: e.ts,
      actor_username: e.actorUsername,
      actor_msp: e.actorMsp,
      actor_role: e.actorRole,
      action: e.action,
      target: e.target,
      outcome: e.outcome,
      status: e.status,
      prev_hash: e.prevHash,
      entry_hash: e.entryHash,
    }),
    getAllAccessLogEntries: () => [...rows].sort((a, b) => a.seq - b.seq),
  };
}

function seed(store, count = 5) {
  for (let i = 1; i <= count; i += 1) {
    accessLog.append(store, {
      actorUsername: 'const.verma',
      actorMsp: 'police',
      actorRole: 'constable',
      action: 'record.search',
      target: { filters: { caseId: `CASE-${i}` } },
      outcome: 'ok',
      status: 200,
    });
  }
}

describe('access log hash chain', () => {
  it('links each entry to the one before it', () => {
    const store = makeStore();
    seed(store, 3);
    expect(store.rows[0].prev_hash).to.equal(accessLog.GENESIS_HASH);
    expect(store.rows[1].prev_hash).to.equal(store.rows[0].entry_hash);
    expect(store.rows[2].prev_hash).to.equal(store.rows[1].entry_hash);
    expect(store.rows.map((r) => r.seq)).to.deep.equal([1, 2, 3]);
  });

  it('verifies a clean chain', () => {
    const store = makeStore();
    seed(store, 5);
    const result = accessLog.verifyChain(store, []);
    expect(result.ok).to.equal(true);
    expect(result.entriesChecked).to.equal(5);
    expect(result.firstBadSeq).to.equal(null);
  });

  it('detects an edited entry and names the first bad one', () => {
    const store = makeStore();
    seed(store, 5);
    // An insider quietly rewrites what they searched for.
    store.rows[2].action = 'auth.whoami';
    const result = accessLog.verifyChain(store, []);
    expect(result.ok).to.equal(false);
    expect(result.firstBadSeq).to.equal(3);
    expect(result.problems.join(' ')).to.contain('modified');
  });

  it('detects a deleted entry', () => {
    const store = makeStore();
    seed(store, 5);
    store.rows.splice(2, 1); // remove entry 3
    const result = accessLog.verifyChain(store, []);
    expect(result.ok).to.equal(false);
    expect(result.firstBadSeq).to.equal(3);
    expect(result.problems.join(' ')).to.contain('missing');
  });

  it('detects a truncated tail once it has been anchored', () => {
    // Deleting the newest entries leaves a chain that is internally consistent,
    // so only the on-chain anchor reveals the loss. This is exactly why the
    // head hash is committed to the ledger.
    const store = makeStore();
    seed(store, 5);
    const anchored = [{ seqNo: 5, headHash: store.rows[4].entry_hash }];
    expect(accessLog.verifyChain(store, anchored).ok).to.equal(true);

    store.rows.splice(4, 1); // drop entry 5 after it was anchored
    const result = accessLog.verifyChain(store, anchored);
    expect(result.ok).to.equal(false);
    expect(result.problems.join(' ')).to.contain('no longer in the log');
  });

  it('detects an entry that no longer matches its blockchain anchor', () => {
    const store = makeStore();
    seed(store, 3);
    const anchored = [{ seqNo: 3, headHash: 'f'.repeat(64) }];
    const result = accessLog.verifyChain(store, anchored);
    expect(result.ok).to.equal(false);
    expect(result.anchorsChecked).to.equal(1);
    expect(result.problems.join(' ')).to.contain('anchored on the blockchain');
  });

  it('is insensitive to key order in the target', () => {
    const store = makeStore();
    const a = accessLog.append(store, {
      actorUsername: 'u', actorMsp: 'police', actorRole: 'constable',
      action: 'record.search', target: { b: 2, a: 1 }, outcome: 'ok', status: 200,
    });
    const store2 = makeStore();
    const b = accessLog.append(store2, {
      actorUsername: 'u', actorMsp: 'police', actorRole: 'constable',
      action: 'record.search', target: { a: 1, b: 2 }, outcome: 'ok', status: 200,
    });
    expect(a.entryHash).to.equal(b.entryHash);
  });
});

describe('what the middleware records', () => {
  const asReq = (method, path, extra = {}) =>
    ({ method, path, query: {}, body: {}, ...extra });

  it('names the previously invisible actions', () => {
    expect(describeRequest(asReq('GET', '/records')).action).to.equal('record.search');
    expect(describeRequest(asReq('GET', '/records/FIR-1/payload')).action).to.equal('payload.release');
    expect(describeRequest(asReq('GET', '/records/FIR-1')).action).to.equal('record.read');
    expect(describeRequest(asReq('GET', '/audit/trail/FIR-1')).action).to.equal('audit.trail.read');
    expect(describeRequest(asReq('GET', '/records/FIR-1/evidence/EV-1/detail')).action)
      .to.equal('evidence.detail.read');
  });

  it('records search filters, because that is the investigative signal', () => {
    const described = describeRequest(
      asReq('GET', '/records', { query: { caseId: 'CASE-2026-001' } }));
    expect(described.target.filters.caseId).to.equal('CASE-2026-001');
  });

  it('skips health checks', () => {
    expect(describeRequest(asReq('GET', '/health'))).to.equal(null);
  });

  it('never records the case narrative, a password or a token', () => {
    // The record-creation request carries the narrative and the login carries a
    // password. Neither may reach the log.
    const create = describeRequest(asReq('POST', '/records', {
      body: {
        recordId: 'FIR-1',
        payload: { summary: 'CANARY-NARRATIVE', complainant: 'CANARY-NAME' },
      },
    }));
    const login = describeRequest(asReq('POST', '/auth/login', {
      body: { username: 'insp.sharma', password: 'CANARY-PASSWORD' },
    }));
    const access = describeRequest(asReq('POST', '/access/request', {
      body: { recordId: 'FIR-1', purpose: 'investigation', approvalToken: 'CANARY-TOKEN' },
    }));

    const serialized = JSON.stringify([create, login, access]);
    for (const canary of ['CANARY-NARRATIVE', 'CANARY-NAME', 'CANARY-PASSWORD', 'CANARY-TOKEN']) {
      expect(serialized).to.not.contain(canary);
    }
    // ...while still recording who logged in and which record was touched.
    expect(login.target.username).to.equal('insp.sharma');
    expect(create.target.recordId).to.equal('FIR-1');
  });
});
