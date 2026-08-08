'use strict';

/**
 * Policy v1 — declarative tables for the access-governance rules.
 *
 * RBAC:  which roles may perform which actions on which record types.
 * ABAC:  contextual constraints (jurisdiction, assignment, clearance, flags).
 * PBAC:  policy versioning + approval/escalation requirements.
 *
 * Mirrors the layered policy of the SEBA-XAI paper (Section III-C).
 */

const POLICY_VERSION = 'crime-policy-v1';

const ROLES = Object.freeze({
  // Police
  CONSTABLE: 'constable',
  SUB_INSPECTOR: 'sub-inspector',
  INSPECTOR: 'inspector',
  SHO: 'sho',
  INVESTIGATING_OFFICER: 'investigating-officer',
  // Forensics
  LAB_ANALYST: 'lab-analyst',
  LAB_DIRECTOR: 'lab-director',
  // Prosecution
  PUBLIC_PROSECUTOR: 'public-prosecutor',
  DEFENSE_COUNSEL: 'defense-counsel',
  // Court
  JUDGE: 'judge',
  MAGISTRATE: 'magistrate',
  COURT_CLERK: 'court-clerk',
  // Audit
  AUDITOR: 'auditor',
  OMBUDSMAN: 'ombudsman',
});

const ACTIONS = Object.freeze(['view', 'export', 'annotate']);

const RECORD_TYPES = Object.freeze([
  'fir', 'case-diary', 'evidence', 'forensic-report', 'witness-statement',
  'chargesheet', 'court-order',
]);

const SENSITIVITY = Object.freeze(['low', 'medium', 'high']);

// Clearance attribute value needed to access each sensitivity level without
// escalation. Requester clearance is one of the same three values.
const CLEARANCE_RANK = Object.freeze({ low: 0, medium: 1, high: 2 });

// RBAC base matrix: role -> record types it may request at all, per action.
// A role/type pair absent here is a deny before any ABAC rule runs.
const RBAC = Object.freeze({
  [ROLES.CONSTABLE]: { view: ['fir'] },
  [ROLES.SUB_INSPECTOR]: { view: ['fir', 'case-diary', 'witness-statement'] },
  [ROLES.INSPECTOR]: {
    view: RECORD_TYPES,
    annotate: ['fir', 'case-diary'],
    export: ['fir', 'case-diary', 'chargesheet'],
  },
  [ROLES.SHO]: {
    view: RECORD_TYPES,
    annotate: ['fir', 'case-diary'],
    export: RECORD_TYPES,
  },
  [ROLES.INVESTIGATING_OFFICER]: {
    view: RECORD_TYPES,
    annotate: ['fir', 'case-diary', 'evidence'],
    export: ['fir', 'case-diary', 'evidence', 'forensic-report'],
  },
  [ROLES.LAB_ANALYST]: { view: ['evidence', 'forensic-report'], annotate: ['forensic-report'] },
  [ROLES.LAB_DIRECTOR]: { view: ['evidence', 'forensic-report'], export: ['forensic-report'] },
  [ROLES.PUBLIC_PROSECUTOR]: { view: RECORD_TYPES, export: ['chargesheet', 'court-order'] },
  [ROLES.DEFENSE_COUNSEL]: { view: ['chargesheet', 'court-order'] },
  [ROLES.JUDGE]: { view: RECORD_TYPES, annotate: ['court-order'], export: RECORD_TYPES },
  [ROLES.MAGISTRATE]: { view: RECORD_TYPES, annotate: ['court-order'], export: RECORD_TYPES },
  [ROLES.COURT_CLERK]: { view: ['chargesheet', 'court-order'] },
  [ROLES.AUDITOR]: { view: RECORD_TYPES },
  [ROLES.OMBUDSMAN]: { view: RECORD_TYPES },
});

// Roles that may resolve an escalated request.
const ESCALATION_APPROVERS = Object.freeze([
  ROLES.SHO, ROLES.JUDGE, ROLES.MAGISTRATE, ROLES.OMBUDSMAN,
]);

// Roles exempt from case-assignment checks (their duty is cross-case review).
const ASSIGNMENT_EXEMPT = Object.freeze([
  ROLES.JUDGE, ROLES.MAGISTRATE, ROLES.AUDITOR, ROLES.OMBUDSMAN,
  ROLES.PUBLIC_PROSECUTOR, ROLES.SHO,
]);

// Roles allowed to see juvenile-flagged records without escalation.
const JUVENILE_ALLOWED = Object.freeze([
  ROLES.INVESTIGATING_OFFICER, ROLES.JUDGE, ROLES.MAGISTRATE,
  ROLES.PUBLIC_PROSECUTOR, ROLES.OMBUDSMAN,
]);

const PURPOSES = Object.freeze([
  'investigation', 'forensic-analysis', 'prosecution', 'judicial-proceeding',
  'audit-review', 'defense-preparation',
]);

module.exports = {
  POLICY_VERSION, ROLES, ACTIONS, RECORD_TYPES, SENSITIVITY, CLEARANCE_RANK,
  RBAC, ESCALATION_APPROVERS, ASSIGNMENT_EXEMPT, JUVENILE_ALLOWED, PURPOSES,
};
