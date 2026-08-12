'use strict';

const express = require('express');
const { z } = require('zod');
const fabric = require('../fabric/gateway');
const vault = require('../storage/vault');
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
 * Recompute the agency-held raw-content hash and compare it with Fabric's
 * immutable metadata commitment.
 */
router.post('/verify-payload/:recordId', requireRole(...REVIEWER_ROLES),
  asyncRoute(async (req, res) => {
    const record = await fabric.evaluate(
      req.user.org, req.user.fabricUser, 'RecordContract', 'GetRecord',
      req.params.recordId);
    const stored = vault.read(record.offChainReference);
    const result = await fabric.evaluate(
      req.user.org, req.user.fabricUser, 'AuditContract', 'VerifyRecordPayload',
      req.params.recordId, stored.currentHash);
    return ok(res, { ...result, verifiedAt: new Date().toISOString() });
  }));

/**
 * Direct Fabric access events: who searched, read or received a case file.
 */
router.get('/access-log', requireRole(...REVIEWER_ROLES), asyncRoute(async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 50, 500);
  const entries = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'AuditContract', 'QueryAccessEvents', String(limit));
  return ok(res, {
    entries,
    storage: 'fabric-ledger',
    integrity: 'validated by Fabric block history and endorsement',
  });
}));

/** Report the integrity mechanism now that no external log needs anchoring. */
router.get('/access-log/verify', requireRole(...REVIEWER_ROLES), asyncRoute(async (req, res) => {
  const entries = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'AuditContract', 'QueryAccessEvents', '500');
  return ok(res, {
    ok: true,
    entriesChecked: entries.length,
    storage: 'fabric-ledger',
    mechanism: 'Fabric endorsement, ordering, block hashes, and immutable key history',
    verifiedAt: new Date().toISOString(),
  });
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
