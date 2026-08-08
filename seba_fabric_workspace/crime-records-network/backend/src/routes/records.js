'use strict';

const express = require('express');
const crypto = require('crypto');
const { z } = require('zod');
const db = require('../db');
const fabric = require('../fabric/gateway');
const { ok, fail, asyncRoute } = require('../util/respond');
const { requireAuth, requireRole } = require('../middleware/auth');

const router = express.Router();
router.use(requireAuth);

const SAFE_ID = /^[A-Za-z0-9._-]{1,128}$/;

const createSchema = z.object({
  recordId: z.string().regex(SAFE_ID),
  payload: z.record(z.unknown()),
  meta: z.object({
    caseId: z.string().regex(SAFE_ID),
    recordType: z.enum(['fir', 'case-diary', 'evidence', 'forensic-report',
      'witness-statement', 'chargesheet', 'court-order']),
    sensitivityLevel: z.enum(['low', 'medium', 'high']),
    juvenileFlag: z.boolean().optional(),
    witnessFlag: z.boolean().optional(),
    owningStation: z.string().regex(SAFE_ID),
    jurisdiction: z.string().regex(SAFE_ID),
  }),
});

const searchSchema = z.object({
  caseId: z.string().regex(SAFE_ID).optional(),
  recordType: z.enum(['fir', 'case-diary', 'evidence', 'forensic-report',
    'witness-statement', 'chargesheet', 'court-order']).optional(),
  sensitivityLevel: z.enum(['low', 'medium', 'high']).optional(),
  owningStation: z.string().regex(SAFE_ID).optional(),
  jurisdiction: z.string().regex(SAFE_ID).optional(),
}).refine((v) => Object.values(v).some((x) => x !== undefined),
  { message: 'at least one search filter is required' });

/**
 * Case-file search. Returns on-chain metadata only — finding a record grants
 * no access to its contents; that still needs an access request.
 */
router.get('/', asyncRoute(async (req, res) => {
  const parsed = searchSchema.safeParse(req.query);
  if (!parsed.success) return fail(res, parsed.error.issues[0].message);
  const filters = Object.fromEntries(
    Object.entries(parsed.data).filter(([, v]) => v !== undefined));

  const records = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'QueryRecords',
    JSON.stringify(filters));
  return ok(res, records);
}));

/** File a record: payload -> SQLite (off-chain), hash + meta -> ledger. */
router.post('/', requireRole('constable', 'sub-inspector', 'inspector', 'sho',
  'investigating-officer'),
  asyncRoute(async (req, res) => {
    const parsed = createSchema.safeParse(req.body);
    if (!parsed.success) return fail(res, parsed.error.issues[0].message);
    const { recordId, payload, meta } = parsed.data;

    if (db.getPayload(recordId)) return fail(res, `record '${recordId}' already exists off-chain`, 409);

    const payloadText = JSON.stringify(payload);
    const payloadHash = crypto.createHash('sha256').update(payloadText, 'utf8').digest('hex');

    const record = await fabric.submit(
      req.user.org, req.user.fabricUser, 'RecordContract', 'CreateCaseRecord',
      recordId,
      JSON.stringify({ ...meta, payloadHash, offchainUri: `offchain://records/${recordId}` })
    );
    db.savePayload(recordId, payloadText, req.user.username);
    return ok(res, record, 201);
  }));

/** On-chain metadata (any authenticated department member). */
router.get('/:recordId', asyncRoute(async (req, res) => {
  const record = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'GetRecord', req.params.recordId);
  return ok(res, record);
}));

/**
 * Off-chain payload — released only when the ledger holds a granted (or
 * escalation-approved) decision for this record made by THIS subject context.
 */
router.get('/:recordId/payload', asyncRoute(async (req, res) => {
  const decisions = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'AccessContract', 'QueryDecisionsByRecord',
    req.params.recordId);
  const granted = decisions.find((d) =>
    (d.status === 'granted' || d.status === 'approved-after-escalation') &&
    d.subject.role === req.user.role);
  if (!granted) {
    return fail(res, 'no granted access decision on the ledger for this record and role', 403);
  }
  const row = db.getPayload(req.params.recordId);
  if (!row) return fail(res, 'payload not found in off-chain store', 404);
  return ok(res, {
    recordId: req.params.recordId,
    payload: JSON.parse(row.payload),
    grantedByDecision: granted.decisionId,
  });
}));

const evidenceSchema = z.object({
  evidenceId: z.string().regex(SAFE_ID),
  artifact: z.string().min(1),
  detail: z.string().max(2000).optional(),
});

/** Forensics attach an evidence commitment (detail goes to the PDC). */
router.post('/:recordId/evidence', requireRole('lab-analyst', 'lab-director'),
  asyncRoute(async (req, res) => {
    const parsed = evidenceSchema.safeParse(req.body);
    if (!parsed.success) return fail(res, parsed.error.issues[0].message);
    const { evidenceId, artifact, detail } = parsed.data;

    const evidenceHash = crypto.createHash('sha256').update(artifact, 'utf8').digest('hex');
    const transient = detail ? { evidenceDetail: Buffer.from(detail, 'utf8') } : undefined;

    const result = await fabric.submitWithTransient(
      req.user.org, req.user.fabricUser, 'RecordContract', 'AttachEvidenceHash',
      [req.params.recordId, evidenceId, evidenceHash], transient);
    return ok(res, result, 201);
  }));

router.get('/:recordId/evidence', asyncRoute(async (req, res) => {
  const list = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'ListEvidence', req.params.recordId);
  return ok(res, list);
}));

/** Private evidence detail — only Police, Forensics, and Court are members. */
router.get('/:recordId/evidence/:evidenceId/detail', asyncRoute(async (req, res) => {
  const detail = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'GetEvidenceDetail',
    req.params.recordId, req.params.evidenceId);
  return ok(res, detail);
}));

/** Court seals / unseals. */
router.post('/:recordId/seal', requireRole('judge', 'magistrate'), asyncRoute(async (req, res) => {
  const record = await fabric.submit(
    req.user.org, req.user.fabricUser, 'RecordContract', 'SealRecord', req.params.recordId);
  return ok(res, record);
}));

router.post('/:recordId/unseal', requireRole('judge', 'magistrate'), asyncRoute(async (req, res) => {
  const record = await fabric.submit(
    req.user.org, req.user.fabricUser, 'RecordContract', 'UnsealRecord', req.params.recordId);
  return ok(res, record);
}));

module.exports = router;
