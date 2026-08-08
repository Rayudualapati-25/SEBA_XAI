'use strict';

/**
 * Experiment-only routes for the Phase 6 attack replay.
 *
 * These deliberately corrupt off-chain state so the integrity check can be
 * shown to catch it. The router is only mounted when ENABLE_EXPERIMENTS=1, so
 * it cannot be reached in a normal run.
 */

const express = require('express');
const { z } = require('zod');
const db = require('../db');
const { ok, fail, asyncRoute } = require('../util/respond');
const { requireAuth, requireRole } = require('../middleware/auth');

const router = express.Router();
router.use(requireAuth);

const tamperSchema = z.object({ payload: z.record(z.unknown()) });

/**
 * Rewrite a record payload in agency storage, bypassing the ledger — the
 * "off-chain record tampering" attack. Restricted to oversight roles even
 * here, so the endpoint cannot be driven by an ordinary account.
 */
router.post('/tamper/:recordId', requireRole('auditor', 'ombudsman'),
  asyncRoute(async (req, res) => {
    const parsed = tamperSchema.safeParse(req.body);
    if (!parsed.success) return fail(res, 'payload object is required');
    if (!db.getPayload(req.params.recordId)) {
      return fail(res, 'record not found in off-chain store', 404);
    }
    const result = db.tamperPayload(req.params.recordId, JSON.stringify(parsed.data.payload));
    return ok(res, {
      recordId: req.params.recordId,
      rowsChanged: result.changes,
      warning: 'off-chain payload rewritten without any ledger transaction',
    });
  }));

/**
 * Rewrite one access-log row in place — the "hiding a search" attack. Used to
 * show that the hash chain plus its on-chain anchor still catches it.
 */
router.post('/tamper-access-log', requireRole('auditor', 'ombudsman'),
  asyncRoute(async (req, res) => {
    const entries = db.getRecentAccessLogEntries(500);
    const target = entries.find((e) => e.action === 'record.search');
    if (!target) return fail(res, 'no search entry in the log to tamper with', 404);
    const result = db.tamperAccessLogEntry(target.seq, 'auth.whoami');
    return ok(res, {
      tamperedSeq: target.seq,
      from: target.action,
      to: 'auth.whoami',
      rowsChanged: result.changes,
      warning: 'access-log row rewritten without touching the ledger',
    });
  }));

module.exports = router;
