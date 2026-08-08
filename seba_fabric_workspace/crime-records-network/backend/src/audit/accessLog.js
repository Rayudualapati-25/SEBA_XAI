'use strict';

/**
 * Tamper-evident access log.
 *
 * The problem this solves: reading and searching are Fabric *queries*, which
 * never touch the ledger. So "who searched for this case" and "who was handed
 * this case file" were previously invisible. Writing a blockchain transaction
 * per search would be far too slow (~2 s each), so instead:
 *
 *   1. every request is appended here as a hash-chained entry
 *   2. every entry stores the hash of the entry before it
 *   3. the head hash is periodically committed to the blockchain (see anchor.js)
 *
 * Result: editing or deleting any entry changes its hash, which breaks every
 * later hash, which no longer matches the anchor already on the ledger.
 *
 *   entryHash(n) = sha256( entryHash(n-1) + canonical(entry n) )
 */

const crypto = require('crypto');

// The chain starts from a fixed value so entry 1 is verifiable like any other.
const GENESIS_HASH = '0'.repeat(64);

/** Deterministic JSON with sorted keys, so the hash never depends on key order. */
function canonicalize(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalize(value[k])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

/** The fields that are hashed. Anything outside this list is not protected. */
function signedFields(entry) {
  return {
    seq: entry.seq,
    ts: entry.ts,
    actorUsername: entry.actorUsername,
    actorMsp: entry.actorMsp,
    actorRole: entry.actorRole,
    action: entry.action,
    target: entry.target,
    outcome: entry.outcome,
    status: entry.status,
  };
}

function computeEntryHash(entry, prevHash) {
  return sha256(prevHash + canonicalize(signedFields(entry)));
}

/**
 * Append one entry. Returns the stored row.
 * @param {object} store db helpers (appendAccessLogEntry, getAccessLogHead)
 */
function append(store, { actorUsername, actorMsp, actorRole, action, target, outcome, status }) {
  const head = store.getAccessLogHead();
  const prevHash = head ? head.entry_hash : GENESIS_HASH;
  const seq = head ? head.seq + 1 : 1;

  const entry = {
    seq,
    ts: new Date().toISOString(),
    actorUsername: actorUsername || null,
    actorMsp: actorMsp || null,
    actorRole: actorRole || null,
    action,
    // Stringify so the hash is stable regardless of object key order upstream.
    target: target === undefined || target === null ? null : canonicalize(target),
    outcome,
    status: Number(status),
  };
  const entryHash = computeEntryHash(entry, prevHash);

  store.appendAccessLogEntry({ ...entry, prevHash, entryHash });
  return { ...entry, prevHash, entryHash };
}

/**
 * Recompute the whole chain and compare it against what is stored, then against
 * every anchor already on the ledger.
 *
 * @param {object} store   db helpers
 * @param {Array}  anchors on-chain anchors [{seqNo, headHash}], may be empty
 * @returns {{ok, entriesChecked, anchorsChecked, firstBadSeq, problems[]}}
 */
function verifyChain(store, anchors = [], epoch = null) {
  const rows = store.getAllAccessLogEntries();
  const problems = [];

  // Only anchors from this log's own epoch describe these entries. Anchors from
  // an earlier epoch mean the log was recreated at some point — that is
  // reported, not silently ignored, because it is exactly what wiping a log to
  // hide activity would look like.
  // Require an exact epoch match. An anchor carrying a different epoch — or no
  // epoch at all, which is how anchors written before epochs existed look —
  // cannot be shown to describe the entries in this log, so comparing against it
  // would produce a false tamper alarm.
  const currentEpochAnchors = epoch === null
    ? anchors
    : anchors.filter((a) => a.epoch === epoch);
  const priorEpochs = epoch === null
    ? []
    : [...new Set(anchors
      .filter((a) => a.epoch !== epoch)
      .map((a) => a.epoch || '(no epoch recorded)'))];
  let firstBadSeq = null;
  let prevHash = GENESIS_HASH;
  let expectedSeq = 1;

  for (const row of rows) {
    // A missing sequence number means an entry was deleted outright.
    if (row.seq !== expectedSeq) {
      problems.push(`entry ${expectedSeq} is missing (next stored is ${row.seq})`);
      if (firstBadSeq === null) firstBadSeq = expectedSeq;
      expectedSeq = row.seq;
    }
    if (row.prev_hash !== prevHash) {
      problems.push(`entry ${row.seq} does not link to the previous entry`);
      if (firstBadSeq === null) firstBadSeq = row.seq;
    }

    const recomputed = computeEntryHash({
      seq: row.seq,
      ts: row.ts,
      actorUsername: row.actor_username,
      actorMsp: row.actor_msp,
      actorRole: row.actor_role,
      action: row.action,
      target: row.target,
      outcome: row.outcome,
      status: row.status,
    }, row.prev_hash);

    if (recomputed !== row.entry_hash) {
      problems.push(`entry ${row.seq} was modified after it was written`);
      if (firstBadSeq === null) firstBadSeq = row.seq;
    }

    prevHash = row.entry_hash;
    expectedSeq += 1;
  }

  // Now check the stored chain against what the blockchain already committed.
  const bySeq = new Map(rows.map((r) => [r.seq, r]));
  let anchorsChecked = 0;
  for (const anchor of currentEpochAnchors) {
    const row = bySeq.get(anchor.seqNo);
    anchorsChecked += 1;
    if (!row) {
      problems.push(`anchored entry ${anchor.seqNo} is no longer in the log`);
      if (firstBadSeq === null) firstBadSeq = anchor.seqNo;
    } else if (row.entry_hash !== anchor.headHash) {
      problems.push(
        `entry ${anchor.seqNo} does not match the hash anchored on the blockchain`
      );
      if (firstBadSeq === null) firstBadSeq = anchor.seqNo;
    }
  }

  return {
    ok: problems.length === 0,
    entriesChecked: rows.length,
    anchorsChecked,
    firstBadSeq,
    problems,
    epoch,
    // A non-empty list means this log is not the first one to be anchored.
    // Legitimate after a rebuild; suspicious in production. Always surfaced.
    priorEpochs,
    priorEpochWarning: priorEpochs.length > 0
      ? `the ledger holds anchors from ${priorEpochs.length} earlier log epoch(s); ` +
        'those entries are not present in the current log'
      : null,
  };
}

module.exports = { append, verifyChain, canonicalize, sha256, GENESIS_HASH };
