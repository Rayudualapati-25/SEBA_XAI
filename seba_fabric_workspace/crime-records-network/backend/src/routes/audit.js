'use strict';

const express = require('express');
const crypto = require('crypto');
const { z } = require('zod');
const db = require('../db');
const fabric = require('../fabric/gateway');
const accessLog = require('../audit/accessLog');
const anchor = require('../audit/anchor');
const { ok, fail, asyncRoute } = require('../util/respond');
const { requireAuth, requireRole } = require('../middleware/auth');

const router = express.Router();
router.use(requireAuth);

const REVIEWER_ROLES = ['auditor', 'ombudsman', 'judge', 'magistrate',
  'public-prosecutor', 'court-clerk'];

/** Full reconstruction trace: record history + every decision + explanations. */
router.get('/trail/:recordId', requireRole(...REVIEWER_ROLES), asyncRoute(async (req, res) => {
  const trail = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'AuditContract', 'GetAuditTrail',
    req.params.recordId);
  return ok(res, trail);
}));

/**
 * Verify the off-chain payload against the on-chain commitment. The hash is
 * recomputed here over what the store actually holds right now — if anyone
 * edited the database, this is where it shows.
 */
router.post('/verify-payload/:recordId', requireRole(...REVIEWER_ROLES),
  asyncRoute(async (req, res) => {
    const row = db.getPayload(req.params.recordId);
    if (!row) return fail(res, 'payload not found in off-chain store', 404);
    const currentHash = crypto.createHash('sha256').update(row.payload, 'utf8').digest('hex');
    const result = await fabric.evaluate(
      req.user.org, req.user.fabricUser, 'AuditContract', 'VerifyRecordPayload',
      req.params.recordId, currentHash);
    return ok(res, { ...result, verifiedAt: new Date().toISOString() });
  }));

/**
 * The access log: who searched, who read a record, who was handed a case file.
 * These are Fabric queries, so they never appear on the ledger by themselves —
 * this log plus its on-chain anchors is what makes them auditable.
 */
router.get('/access-log', requireRole(...REVIEWER_ROLES), asyncRoute(async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 50, 500);
  const entries = db.getRecentAccessLogEntries(limit);
  const state = db.getAnchorState();
  return ok(res, {
    entries,
    anchoredUpto: state.anchored_upto,
    anchoredAt: state.anchored_at,
    pendingAnchor: anchor.pendingCount(),
  });
}));

/**
 * Recompute the whole hash chain and compare it with every anchor on the
 * blockchain. This is the check that catches an edited or deleted log entry.
 */
router.get('/access-log/verify', requireRole(...REVIEWER_ROLES), asyncRoute(async (req, res) => {
  let anchors = [];
  let anchorError = null;
  try {
    anchors = await anchor.fetchAnchors(req.user.org, req.user.fabricUser);
  } catch (err) {
    // Report this rather than silently verifying against nothing — an
    // unreachable ledger means the strongest part of the check did not run.
    anchorError = err.message;
  }
  const state = db.getAnchorState();
  const result = accessLog.verifyChain(db, anchors || [], state.epoch);
  return ok(res, { ...result, anchorError, verifiedAt: new Date().toISOString() });
}));

/** Force an anchor now instead of waiting for the batch threshold. */
router.post('/anchor', requireRole('auditor', 'ombudsman'), asyncRoute(async (req, res) => {
  const written = await anchor.anchorNow({ force: true });
  if (!written) return ok(res, { anchored: false, reason: 'nothing new to anchor' });
  return ok(res, { anchored: true, anchor: written });
}));

const explanationSchema = z.object({ artifact: z.record(z.unknown()) });

/** Verify a held explanation artifact against its committed hash. */
router.post('/verify-explanation/:recordId/:decisionId', requireRole(...REVIEWER_ROLES),
  asyncRoute(async (req, res) => {
    const parsed = explanationSchema.safeParse(req.body);
    if (!parsed.success) return fail(res, 'artifact object is required');
    const result = await fabric.evaluate(
      req.user.org, req.user.fabricUser, 'AuditContract', 'VerifyExplanation',
      req.params.recordId, req.params.decisionId, JSON.stringify(parsed.data.artifact));
    return ok(res, result);
  }));

module.exports = router;
