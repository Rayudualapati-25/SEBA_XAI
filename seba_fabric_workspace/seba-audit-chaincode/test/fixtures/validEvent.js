"use strict";

const crypto = require("crypto");

function sha256Hex(seed) {
  return crypto.createHash("sha256").update(String(seed), "utf8").digest("hex");
}

/**
 * Builds a syntactically valid SEBA audit event (commitment-only,
 * no raw/PII fields) that satisfies every REQUIRED_FIELDS /
 * hash-format / decision-enum rule in sebaAuditContract.js.
 *
 * @param {object} overrides fields to override on top of the valid base event
 * @returns {object} a plain event object (not yet JSON.stringify'd)
 */
function buildValidEvent(overrides = {}) {
  const base = {
    requestIdHash: sha256Hex("request-1"),
    policyVersion: "policy-v1",
    decision: "allow",
    primaryReasonCode: "ROLE_MATCH",
    decisionHash: sha256Hex("decision-1"),
    explanationHash: sha256Hex("explanation-1"),
    recordCommitment: sha256Hex("record-1"),
    auditAnchorHash: sha256Hex("anchor-1"),
    approvalReferenceHash: sha256Hex("approval-1"),
    attributeSetHash: sha256Hex("attributes-1"),
    sourcePrototypeRun: "run-42",
    createdAtUtc: "2026-08-03T00:00:00.000Z",
  };
  return { ...base, ...overrides };
}

module.exports = { buildValidEvent, sha256Hex };
