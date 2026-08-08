'use strict';

/**
 * Commits the access log's head hash to the blockchain.
 *
 * One blockchain write per batch of entries, not per request — a per-search
 * transaction would cost ~2 seconds each. Once a head hash is on the ledger,
 * the log entries up to that point can no longer be rewritten unnoticed.
 *
 * Anchoring is an oversight action, so it is submitted as the audit
 * organization's identity (see ANCHOR_ORG / ANCHOR_USER in config).
 */

const db = require('../db');
const fabric = require('../fabric/gateway');
const { ANCHOR_EVERY, ANCHOR_ORG, ANCHOR_USER } = require('../config');

let inFlight = false;

/**
 * Anchor the current head if there are unanchored entries.
 * Never throws: a failed anchor must not break the request that triggered it.
 * @returns {Promise<object|null>} the anchor written, or null if nothing to do
 */
async function anchorNow({ force = false } = {}) {
  if (inFlight) return null;

  const head = db.getAccessLogHead();
  if (!head) return null;

  const state = db.getAnchorState();
  const pending = head.seq - state.anchored_upto;
  if (pending <= 0) return null;
  if (!force && pending < ANCHOR_EVERY) return null;

  inFlight = true;
  try {
    const anchor = await fabric.submit(
      ANCHOR_ORG, ANCHOR_USER, 'AuditContract', 'AnchorAccessLog',
      String(head.seq), head.entry_hash, String(pending), state.epoch);
    db.setAnchoredUpto(head.seq);
    return anchor;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(`[anchor] failed to anchor access log at seq ${head.seq}:`, err.message);
    return null;
  } finally {
    inFlight = false;
  }
}

/** How many entries are waiting to be anchored. */
function pendingCount() {
  const head = db.getAccessLogHead();
  const state = db.getAnchorState();
  return head ? head.seq - state.anchored_upto : 0;
}

/** Read every anchor the ledger holds, oldest first. */
async function fetchAnchors(org, user) {
  return fabric.evaluate(org, user, 'AuditContract', 'GetAccessLogAnchors');
}

module.exports = { anchorNow, pendingCount, fetchAnchors };
