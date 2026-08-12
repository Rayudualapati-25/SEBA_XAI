#!/usr/bin/env node
'use strict';

/**
 * Write the seeded department identities onto the ledger.
 *
 * scripts/seed-identities.sh does half the job: it registers and enrols the
 * thirteen officers with their departments' Fabric CAs, which gives each of
 * them an X.509 certificate. That is the CA's business and does not create an
 * application authorization profile on the blockchain.
 *
 * This script does the other half: a CreateUser transaction per officer, so
 * each one has an account on the ledger. Until that runs, nobody can sign in,
 * because sign-in verifies the selected certificate against that ledger
 * profile and there is no user/password database to fall back on.
 *
 * Each department admits its own people, signed by that department's senior
 * officer, because that is what UserContract requires. The senior officer
 * registers themselves first; the chaincode authorises on the role in their
 * certificate, not on an account that does not exist yet.
 *
 * Usage: node scripts/seed-users-onchain.js   (from crime-records-network/)
 */

const users = require('../backend/src/fabric/users');
const ca = require('../backend/src/fabric/ca');

// The roster must stay in step with network/scripts/seed-identities.sh: the
// role here is the account's role, the role there is signed into the
// certificate, and UserContract will happily store a mismatch that then fails
// every access check. Keep them equal.
// org -> the senior officer who admits that department's users.
const REGISTRAR = Object.freeze({
  police: 'sho.reddy',
  forensics: 'dir.iyer',
  prosecution: 'pp.mehta',
  court: 'judge.rana',
  audit: 'aud.qureshi',
});

const ROSTER = [
  // [username, org, displayName, role, credentialStatus]
  ['sho.reddy', 'police', 'SHO K. Reddy', 'sho', 'active'],
  ['insp.sharma', 'police', 'Insp. A. Sharma', 'inspector', 'active'],
  ['const.verma', 'police', 'Const. R. Verma', 'constable', 'active'],
  ['io.krishnan', 'police', 'IO S. Krishnan', 'investigating-officer', 'active'],
  // Deliberately an ACTIVE account despite the name. Two different things are
  // called revoked here and only one of them applies:
  //   - the certificate attribute credentialStatus=revoked, set in
  //     seed-identities.sh, which makes the access policy deny every request
  //     with reason CRED_NOT_ACTIVE. That is the case the paper measures.
  //   - the account status below, which decides whether they can sign in.
  // Rathore has to be able to sign in for that denial to be observable, so the
  // account stays active and the revocation lives in the certificate.
  ['insp.rathore', 'police', 'Insp. V. Rathore (revoked credential)', 'inspector', 'active'],
  ['insp.singh', 'police', 'Insp. P. Singh (cross-district)', 'inspector', 'active'],
  ['dir.iyer', 'forensics', 'Dir. M. Iyer', 'lab-director', 'active'],
  ['analyst.rao', 'forensics', 'Analyst P. Rao', 'lab-analyst', 'active'],
  ['pp.mehta', 'prosecution', 'PP D. Mehta', 'public-prosecutor', 'active'],
  ['dc.nair', 'prosecution', 'Adv. L. Nair', 'defense-counsel', 'active'],
  ['judge.rana', 'court', 'Hon. Justice Rana', 'judge', 'active'],
  ['clerk.das', 'court', 'Clerk B. Das', 'court-clerk', 'active'],
  ['aud.qureshi', 'audit', 'Auditor F. Qureshi', 'auditor', 'active'],
  ['omb.pillai', 'audit', 'Ombudsman T. Pillai', 'ombudsman', 'active'],
];

// Must mirror the ecert attributes in network/scripts/seed-identities.sh.
const USER_CONTEXT = Object.freeze({
  'sho.reddy': { rank: '4', station: 'PS-Central', jurisdiction: 'district-north', clearance: 'high' },
  'insp.sharma': { rank: '3', station: 'PS-Central', jurisdiction: 'district-north', clearance: 'high', caseAssignments: ['CASE-2026-001', 'CASE-2026-002'] },
  'const.verma': { rank: '1', station: 'PS-Central', jurisdiction: 'district-north', clearance: 'low' },
  'io.krishnan': { rank: '3', station: 'PS-Central', jurisdiction: 'district-north', clearance: 'high', caseAssignments: ['CASE-2026-001'] },
  'insp.rathore': { rank: '3', station: 'PS-East', jurisdiction: 'district-north', clearance: 'high', caseAssignments: ['CASE-2026-001'] },
  'insp.singh': { rank: '3', station: 'PS-South', jurisdiction: 'district-south', clearance: 'high', caseAssignments: ['CASE-2026-001'] },
  'dir.iyer': { station: 'FSL-North', jurisdiction: 'district-north', clearance: 'high' },
  'analyst.rao': { station: 'FSL-North', jurisdiction: 'district-north', clearance: 'medium', caseAssignments: ['CASE-2026-001'] },
  'pp.mehta': { jurisdiction: 'district-north', clearance: 'high' },
  'dc.nair': { jurisdiction: 'district-north', clearance: 'low' },
  'judge.rana': { jurisdiction: 'district-north', clearance: 'high' },
  'clerk.das': { jurisdiction: 'district-north', clearance: 'low' },
  'aud.qureshi': { jurisdiction: 'district-north', clearance: 'high' },
  'omb.pillai': { jurisdiction: 'district-north', clearance: 'high' },
});

const blue = (s) => `[0;34m${s}[0m`;
const red = (s) => `[0;31m${s}[0m`;

async function main() {
  const missing = ROSTER
    .filter(([username, org]) => !ca.isEnrolled(org, username))
    .map(([username, org]) => `${org}/${username}`);
  if (missing.length > 0) {
    console.error(red('These identities are not enrolled yet:'));
    missing.forEach((m) => console.error(`  ${m}`));
    console.error('\nRun `make seed` first — it registers and enrols them with the CAs.');
    process.exit(1);
  }

  let created = 0;
  let skipped = 0;

  for (const [username, org, displayName, role, credentialStatus] of ROSTER) {
    const registrar = REGISTRAR[org];
    try {
      await users.create(org, registrar, username, {
        displayName,
        org,
        role,
        fabricUser: username,
        departmentId: org,
        ...USER_CONTEXT[username],
        caseAssignments: USER_CONTEXT[username].caseAssignments || [],
        credentialStatus,
      });
      console.log(blue(`on-chain  ${org}/${username}  (${role})`));
      created += 1;
    } catch (err) {
      const message = String(err.message || err);
      if (message.includes('already exists')) {
        console.log(`skip      ${org}/${username}: already on the ledger`);
        skipped += 1;
        continue;
      }
      console.error(red(`failed    ${org}/${username}: ${message}`));
      throw err;
    }
  }

  console.log(`\n${created} account(s) written to the ledger, ${skipped} already present.`);
  console.log('Open http://localhost:3001 and select any enrolled identity above.');
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(red(`\nSeeding failed: ${err.message || err}`));
    process.exit(1);
  });
