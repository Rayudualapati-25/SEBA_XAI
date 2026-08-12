'use strict';

/**
 * Deterministic policy engine: evaluates a structured access request and
 * returns { decision, reasonCode, decisiveAttributes, counterfactual }.
 *
 * decision  : 'allow' | 'deny' | 'escalate'
 * Rules run in a fixed order; the first terminal rule wins, and the rule
 * that fired names the decisive attributes — this is what makes the
 * explanation artifact reviewable rather than decorative.
 */

const {
  POLICY_VERSION, CLEARANCE_RANK, RBAC, ASSIGNMENT_EXEMPT, JUVENILE_ALLOWED,
  PURPOSES,
} = require('./policyV1');

function result(decision, reasonCode, decisiveAttributes, counterfactual) {
  return Object.freeze({
    decision,
    reasonCode,
    decisiveAttributes: Object.freeze([...decisiveAttributes]),
    counterfactual: counterfactual || null,
    policyVersion: POLICY_VERSION,
  });
}

/**
 * @param {object} subject  caller attribute snapshot (from identity.getCaller)
 * @param {object} record   record metadata from the ledger
 * @param {string} action   'view' | 'export' | 'annotate'
 * @param {object} env      { purpose, emergencyFlag, courtLink, approvalToken }
 */
function evaluate(subject, record, action, env) {
  // Rule 1 — credential state (PBAC: revocation handling).
  if (subject.credentialStatus !== 'active') {
    return result('deny', 'CRED_NOT_ACTIVE', ['subject.credentialStatus'],
      'decision would change if the requester credential status were "active"');
  }

  // Rule 2 — purpose is mandatory and must be a declared purpose.
  if (!env.purpose || !PURPOSES.includes(env.purpose)) {
    return result('deny', 'INVALID_PURPOSE', ['env.purpose'],
      `decision would change if purpose were one of [${PURPOSES.join(', ')}]`);
  }

  // Rule 3 — RBAC base matrix: the role must permit this action on this type.
  const rolePerms = RBAC[subject.role];
  const permittedTypes = rolePerms ? rolePerms[action] : undefined;
  if (!permittedTypes || !permittedTypes.includes(record.recordType)) {
    return result('deny', 'RBAC_NO_PERMISSION',
      ['subject.role', 'action', 'object.recordType'],
      `role '${subject.role}' has no '${action}' permission on '${record.recordType}'`);
  }

  // Rule 3b — oversight reconstructs metadata, decisions and hashes through
  // AuditContract. It never receives protected raw case content.
  if (['auditor', 'ombudsman'].includes(subject.role) && action === 'view') {
    return result('deny', 'AUDIT_METADATA_ONLY', ['subject.role', 'action'],
      'use the audit-trail query, which excludes protected raw content');
  }

  // Rule 4 — sealed records escalate for everyone except the court itself.
  if (record.sealed && subject.mspId !== 'CourtMSP') {
    return result('escalate', 'SEALED_RECORD', ['object.sealed', 'subject.mspId'],
      'decision would be evaluated normally if the record were not sealed');
  }

  // Rule 5 — juvenile protection is a hard deny except for the narrowly
  // enumerated legal roles. Rank alone never overrides this rule.
  if (record.juvenileFlag && !JUVENILE_ALLOWED.includes(subject.role)) {
    return result('deny', 'JUVENILE_PROTECTED',
      ['object.juvenileFlag', 'subject.role'],
      'access requires a role explicitly authorized by the juvenile-protection policy');
  }

  // Rule 5b — data minimization for forensic work. Evidence metadata remains
  // queryable, but a forensic identity does not receive a victim-protected raw
  // record merely because it has an evidence-analysis role.
  if (record.victimProtectionFlag
      && [ 'lab-analyst', 'lab-director' ].includes(subject.role)) {
    return result('deny', 'VICTIM_DATA_NOT_NECESSARY',
      ['object.victimProtectionFlag', 'subject.role', 'env.purpose'],
      'request a purpose-specific evidence artifact that excludes victim identity data');
  }

  // Rule 6 — jurisdiction: cross-jurisdiction requests escalate unless the
  // request is an emergency carrying an approval token (PBAC exception).
  if (subject.jurisdiction !== record.jurisdiction &&
      !ASSIGNMENT_EXEMPT.includes(subject.role)) {
    if (env.emergencyFlag && env.approvalToken) {
      return result('allow', 'EMERGENCY_CROSS_JURISDICTION',
        ['env.emergencyFlag', 'env.approvalToken', 'subject.jurisdiction', 'object.jurisdiction']);
    }
    return result('escalate', 'CROSS_JURISDICTION',
      ['subject.jurisdiction', 'object.jurisdiction'],
      `decision would change if requester jurisdiction were '${record.jurisdiction}'`);
  }

  // Rule 7 — case assignment (ABAC): non-exempt roles must be assigned.
  if (!ASSIGNMENT_EXEMPT.includes(subject.role)) {
    // Split on comma or pipe: Fabric CA's --id.attrs uses commas as the
    // attribute separator, so certificates carry assignments pipe-separated.
    const assignments = subject.caseAssignments
      ? subject.caseAssignments.split(/[,|]/).map((s) => s.trim())
      : [];
    if (!assignments.includes(record.caseId)) {
      return result('deny', 'NOT_ASSIGNED',
        ['subject.caseAssignments', 'object.caseId'],
        `decision would change if case '${record.caseId}' were in the requester's assignments`);
    }
  }

  // Rule 8 — sensitivity vs clearance: insufficient clearance escalates.
  const needed = CLEARANCE_RANK[record.sensitivityLevel] ?? 2;
  const held = CLEARANCE_RANK[subject.clearance] ?? -1;
  if (held < needed) {
    return result('escalate', 'INSUFFICIENT_CLEARANCE',
      ['subject.clearance', 'object.sensitivityLevel'],
      `decision would change if requester clearance were '${record.sensitivityLevel}' or higher`);
  }

  // Default — every gate passed.
  return result('allow', 'POLICY_SATISFIED', [
    'subject.role', 'subject.jurisdiction', 'subject.clearance', 'env.purpose',
  ]);
}

module.exports = { evaluate, POLICY_VERSION };
