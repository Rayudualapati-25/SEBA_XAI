'use strict';

const express = require('express');
const { z } = require('zod');
const fabric = require('../fabric/gateway');
const { ok, fail, asyncRoute } = require('../util/respond');
const { requireAuth, requireRole } = require('../middleware/auth');

const router = express.Router();
router.use(requireAuth);

const requestSchema = z.object({
  recordId: z.string().min(1).max(128),
  action: z.enum(['view', 'export', 'annotate']),
  purpose: z.enum(['investigation', 'forensic-analysis', 'prosecution',
    'judicial-proceeding', 'audit-review', 'defense-preparation']),
  timeWindow: z.string().max(64).optional(),
  emergencyFlag: z.boolean().optional(),
  courtLink: z.string().max(128).optional(),
  approvalToken: z.string().max(256).optional(),
});

/** Submit an access request; returns the on-chain decision + explanation. */
router.post('/request', asyncRoute(async (req, res) => {
  const parsed = requestSchema.safeParse(req.body);
  if (!parsed.success) return fail(res, parsed.error.issues[0].message);
  const { recordId, action, ...env } = parsed.data;

  const decision = await fabric.submit(
    req.user.org, req.user.fabricUser, 'AccessContract', 'RequestAccess',
    recordId, action, JSON.stringify(env));
  return ok(res, decision, 201);
}));

router.get('/record/:recordId', asyncRoute(async (req, res) => {
  const decisions = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'AccessContract', 'QueryDecisionsByRecord',
    req.params.recordId);
  return ok(res, decisions);
}));

const APPROVER_ROLES = ['sho', 'judge', 'magistrate', 'ombudsman'];

router.get('/pending', requireRole(...APPROVER_ROLES), asyncRoute(async (req, res) => {
  const pending = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'AccessContract', 'QueryPendingEscalations');
  return ok(res, pending);
}));

const resolveSchema = z.object({ note: z.string().max(500).optional() });

router.post('/:recordId/:decisionId/approve', requireRole(...APPROVER_ROLES),
  asyncRoute(async (req, res) => {
    const parsed = resolveSchema.safeParse(req.body || {});
    if (!parsed.success) return fail(res, parsed.error.issues[0].message);
    const resolved = await fabric.submit(
      req.user.org, req.user.fabricUser, 'AccessContract', 'ApproveEscalation',
      req.params.recordId, req.params.decisionId, parsed.data.note || '');
    return ok(res, resolved);
  }));

router.post('/:recordId/:decisionId/reject', requireRole(...APPROVER_ROLES),
  asyncRoute(async (req, res) => {
    const parsed = resolveSchema.safeParse(req.body || {});
    if (!parsed.success) return fail(res, parsed.error.issues[0].message);
    const resolved = await fabric.submit(
      req.user.org, req.user.fabricUser, 'AccessContract', 'RejectEscalation',
      req.params.recordId, req.params.decisionId, parsed.data.note || '');
    return ok(res, resolved);
  }));

module.exports = router;
