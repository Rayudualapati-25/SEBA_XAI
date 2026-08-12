/**
 * Who may see which module.
 *
 * This is a navigation filter, not an authorisation boundary. It decides what
 * appears in the sidebar. Authorisation is enforced by:
 *   1. the chaincode  (checks the caller's signed X.509 certificate)
 *   2. the backend    (requireRole in src/routes/*.js)
 * A user who hand-crafts a request still hits both. Never move a security
 * decision into this file.
 *
 * The role groups below mirror the backend's lists. If you change a
 * `requireRole(...)` in the backend, change the matching group here too.
 */

export const ORG = Object.freeze({
  POLICE: 'police',
  FORENSICS: 'forensics',
  PROSECUTION: 'prosecution',
  COURT: 'court',
  AUDIT: 'audit',
});

export const ORG_LABEL = Object.freeze({
  police: 'Police',
  forensics: 'Forensic Science Laboratory',
  prosecution: 'Prosecution',
  court: 'Judiciary',
  audit: 'Oversight & Internal Affairs',
});

/** Mirrors backend routes/records.js POST '/' */
export const FILING_ROLES = Object.freeze([
  'constable', 'sub-inspector', 'inspector', 'sho', 'investigating-officer',
]);

/** Mirrors backend routes/records.js evidence POST */
export const FORENSIC_ROLES = Object.freeze(['lab-analyst', 'lab-director']);

/** Mirrors backend routes/access.js APPROVER_ROLES */
export const APPROVER_ROLES = Object.freeze(['sho', 'judge', 'magistrate', 'ombudsman']);

/** Mirrors backend routes/audit.js REVIEWER_ROLES */
export const REVIEWER_ROLES = Object.freeze([
  'auditor', 'ombudsman', 'judge', 'magistrate', 'public-prosecutor', 'court-clerk',
]);

/** Mirrors backend routes/records.js seal/unseal */
export const JUDICIAL_ROLES = Object.freeze(['judge', 'magistrate']);

/** Oversight roles used by audit-focused navigation. */
export const OVERSIGHT_ROLES = Object.freeze(['auditor', 'ombudsman']);

/**
 * Mirrors ADMIN_ROLES_BY_MSP in chaincode/crimerecords/lib/userContract.js —
 * the senior role in each department, the only one that may admit new users.
 * The chaincode is what enforces this; here it only hides a form that would
 * fail.
 */
export const USER_ADMIN_ROLES = Object.freeze([
  'sho', 'lab-director', 'public-prosecutor', 'judge', 'auditor', 'ombudsman',
]);

/** Every role a new account can be given. Mirrors ROLES in policyV1.js. */
export const ALL_ROLES = Object.freeze([
  'constable', 'sub-inspector', 'inspector', 'sho', 'investigating-officer',
  'lab-analyst', 'lab-director', 'public-prosecutor', 'defense-counsel',
  'judge', 'magistrate', 'court-clerk', 'auditor', 'ombudsman',
]);

/** Which roles belong to which department, so the form cannot offer a
 *  combination the chaincode would reject. */
export const ROLES_BY_ORG = Object.freeze({
  police: ['constable', 'sub-inspector', 'inspector', 'sho', 'investigating-officer'],
  forensics: ['lab-analyst', 'lab-director'],
  prosecution: ['public-prosecutor', 'defense-counsel'],
  court: ['judge', 'magistrate', 'court-clerk'],
  audit: ['auditor', 'ombudsman'],
});

/**
 * Does this user satisfy a module's `allow` rule?
 *
 * `allow` shapes, in order of precedence:
 *   undefined            -> everyone signed in
 *   { roles: [...] }     -> user.role must be listed
 *   { orgs:  [...] }     -> user.org must be listed
 *   { roles, orgs }      -> BOTH must match
 *   { when: (user) => boolean } -> custom predicate, for anything unusual
 */
export function canAccess(user, allow) {
  if (!user) return false;
  if (!allow) return true;
  if (allow.roles && !allow.roles.includes(user.role)) return false;
  if (allow.orgs && !allow.orgs.includes(user.org)) return false;
  if (allow.when && !allow.when(user)) return false;
  return true;
}
