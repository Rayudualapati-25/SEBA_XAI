'use strict';

const express = require('express');
const { z } = require('zod');
const fabric = require('../fabric/gateway');
const vault = require('../storage/vault');
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
    victimProtectionFlag: z.boolean().optional(),
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

/** Store raw content in the agency vault, then commit its metadata/hash to Fabric. */
router.post('/', requireRole('constable', 'sub-inspector', 'inspector', 'sho',
  'investigating-officer'),
  asyncRoute(async (req, res) => {
    const parsed = createSchema.safeParse(req.body);
    if (!parsed.success) return fail(res, parsed.error.issues[0].message);
    const { recordId, payload, meta } = parsed.data;

    const commitment = vault.save(req.user.org, recordId, payload);
    let record;
    try {
      record = await fabric.submit(
        req.user.org, req.user.fabricUser, 'RecordContract', 'CreateCaseRecord',
        recordId, JSON.stringify({
          ...meta,
          owningAgency: req.user.org,
          contentHash: commitment.contentHash,
          offChainReference: commitment.offChainReference,
          status: 'active',
        })
      );
    } catch (err) {
      if (commitment.created) vault.rollback(commitment.offChainReference);
      throw err;
    }
    return ok(res, record, 201);
  }));

/** On-chain metadata (any authenticated department member). */
router.get('/:recordId', asyncRoute(async (req, res) => {
  const record = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'GetRecord', req.params.recordId);
  return ok(res, record);
}));

/**
 * Off-chain raw content. Chaincode first verifies that the exact signing X.509
 * identity owns a grant, then the backend validates the file against Fabric's
 * content hash before release.
 */
router.get('/:recordId/payload', asyncRoute(async (req, res) => {
  const authorization = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'AuthorizeRecordRead',
    req.params.recordId);
  const stored = vault.read(authorization.offChainReference);
  if (stored.currentHash !== authorization.contentHash) {
    return fail(res, 'raw content integrity check failed', 409);
  }
  return ok(res, {
    recordId: req.params.recordId,
    payload: stored.payload,
    grantedByDecision: authorization.grantedByDecision,
    contentHash: authorization.contentHash,
  });
}));

const evidenceSchema = z.object({
  evidenceId: z.string().regex(SAFE_ID),
  artifact: z.string().min(1),
  source: z.string().min(1).max(200).default('agency-submission'),
  detail: z.string().max(2000).optional(),
});

/** Forensics attach an evidence commitment (detail goes to the PDC). */
router.post('/:recordId/evidence', requireRole('lab-analyst', 'lab-director'),
  asyncRoute(async (req, res) => {
    const parsed = evidenceSchema.safeParse(req.body);
    if (!parsed.success) return fail(res, parsed.error.issues[0].message);
    const { evidenceId, artifact, detail, source } = parsed.data;
    const vaultId = `${req.params.recordId.slice(0, 60)}--${evidenceId.slice(0, 60)}`;
    const commitment = vault.save(req.user.org, vaultId, { artifact });
    const transient = detail ? { evidenceDetail: Buffer.from(detail, 'utf8') } : undefined;
    let result;
    try {
      result = await fabric.submitWithTransient(
        req.user.org, req.user.fabricUser, 'RecordContract', 'AttachEvidenceHash',
        [req.params.recordId, evidenceId, commitment.contentHash, source,
          commitment.offChainReference], transient);
    } catch (err) {
      if (commitment.created) vault.rollback(commitment.offChainReference);
      throw err;
    }
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

const custodySchema = z.object({
  toMsp: z.enum(['PoliceMSP', 'ForensicsMSP', 'CourtMSP']),
  reason: z.string().min(1).max(500),
});
router.post('/:recordId/evidence/:evidenceId/custody', asyncRoute(async (req, res) => {
  const parsed = custodySchema.safeParse(req.body);
  if (!parsed.success) return fail(res, parsed.error.issues[0].message);
  const event = await fabric.submit(
    req.user.org, req.user.fabricUser, 'RecordContract', 'TransferEvidenceCustody',
    req.params.recordId, req.params.evidenceId, parsed.data.toMsp, parsed.data.reason);
  return ok(res, event);
}));

router.get('/:recordId/evidence/:evidenceId/custody', asyncRoute(async (req, res) => {
  const events = await fabric.evaluate(
    req.user.org, req.user.fabricUser, 'RecordContract', 'QueryEvidenceCustody',
    req.params.recordId, req.params.evidenceId);
  return ok(res, events);
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
