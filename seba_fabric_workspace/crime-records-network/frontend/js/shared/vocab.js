/**
 * Domain vocabulary, in one place.
 *
 * These lists must match the chaincode. When you add a record type, purpose or
 * reason code to `chaincode/crimerecords/lib/policy/policyV1.js`, add it here
 * too — that is the only frontend change needed for the dropdowns and wording.
 */

export const RECORD_TYPES = Object.freeze([
  'fir', 'case-diary', 'evidence', 'forensic-report',
  'witness-statement', 'chargesheet', 'court-order',
]);

export const SENSITIVITY = Object.freeze(['low', 'medium', 'high']);

export const ACTIONS = Object.freeze(['view', 'export', 'annotate']);

export const PURPOSES = Object.freeze([
  'investigation', 'forensic-analysis', 'prosecution',
  'judicial-proceeding', 'audit-review', 'defense-preparation',
]);

/** The purpose a given role would normally state, used to preselect dropdowns. */
export const DEFAULT_PURPOSE_BY_ROLE = Object.freeze({
  'lab-analyst': 'forensic-analysis',
  'lab-director': 'forensic-analysis',
  'public-prosecutor': 'prosecution',
  'defense-counsel': 'defense-preparation',
  judge: 'judicial-proceeding',
  magistrate: 'judicial-proceeding',
  'court-clerk': 'judicial-proceeding',
  auditor: 'audit-review',
  ombudsman: 'audit-review',
});

export function defaultPurpose(role) {
  return DEFAULT_PURPOSE_BY_ROLE[role] || 'investigation';
}

/** Plain-English sentence per reason code returned by the policy engine. */
export const REASON_TEXT = Object.freeze({
  POLICY_SATISFIED: 'All policy gates passed for this role, purpose, and record sensitivity.',
  CRED_NOT_ACTIVE: 'The requester credential is not active (suspended or revoked).',
  INVALID_PURPOSE: 'No valid declared purpose was supplied with the request.',
  RBAC_NO_PERMISSION: 'This role has no permission for that action on that record type.',
  SEALED_RECORD: 'The record is sealed by the court, so a review authority must decide.',
  JUVENILE_PROTECTED: 'The record involves a juvenile and needs supervisory approval.',
  CROSS_JURISDICTION: 'The request crosses a jurisdiction boundary.',
  EMERGENCY_CROSS_JURISDICTION: 'Allowed as an emergency with a valid approval token.',
  NOT_ASSIGNED: 'The requester is not assigned to this case.',
  INSUFFICIENT_CLEARANCE: 'The requester clearance is below the record sensitivity level.',
});

/** What each decision means for the requester, shown under the explanation. */
export const DECISION_CONSEQUENCE = Object.freeze({
  allow: 'The file can be opened.',
  deny: 'The file stays closed. The reason above is what an auditor will see.',
  escalate: 'Held for review. A supervisor or judicial authority must approve it before the file opens.',
});

/** Human labels for access-log action names. */
export const ACTION_LABEL = Object.freeze({
  'record.search': 'searched case files',
  'record.read': 'opened record metadata',
  'record.create': 'filed a record',
  'record.seal': 'sealed a record',
  'record.unseal': 'unsealed a record',
  'payload.release': 'received the case file',
  'evidence.attach': 'attached evidence',
  'evidence.list': 'listed evidence',
  'evidence.detail.read': 'read private evidence detail',
  'access.request': 'requested access',
  'escalation.approve': 'approved an escalation',
  'escalation.reject': 'rejected an escalation',
  'escalation.queue.read': 'viewed the escalation queue',
  'audit.trail.read': 'read the audit trail',
  'audit.verify.payload': 'verified payload integrity',
  'audit.verify.explanation': 'verified an explanation',
  'audit.accesslog.read': 'read the access log',
  'explanation.render': 'viewed a plain-language explanation',
  'auth.login': 'signed in',
  'auth.login_failed': 'failed sign-in',
  'auth.whoami': 'checked their profile',
});

export function actionLabel(action) {
  return ACTION_LABEL[action] || action;
}

/** Colour for an outcome pill. */
export function outcomeKind(outcome) {
  if (outcome === 'ok') return 'allow';
  if (outcome === 'refused' || outcome === 'failed') return 'deny';
  if (outcome === 'rejected') return 'escalate';
  return 'neutral';
}
