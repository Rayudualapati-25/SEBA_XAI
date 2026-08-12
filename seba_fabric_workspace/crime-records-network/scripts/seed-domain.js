#!/usr/bin/env node
'use strict';

/** Deterministic ledger seed for departments and the initial demo cases. */

const fabric = require('../backend/src/fabric/gateway');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const DEPARTMENTS = [
  ['police', 'sho.reddy', { name: 'Police Department', type: 'police', jurisdiction: 'district-north', status: 'active', permittedFunctions: ['investigation', 'record-filing'] }],
  ['forensics', 'dir.iyer', { name: 'Forensic Science Laboratory', type: 'forensics', jurisdiction: 'district-north', status: 'active', permittedFunctions: ['forensic-analysis', 'evidence-review'] }],
  ['prosecution', 'pp.mehta', { name: 'Public Prosecution Department', type: 'prosecution', jurisdiction: 'district-north', status: 'active', permittedFunctions: ['prosecution', 'case-review'] }],
  ['court', 'judge.rana', { name: 'District Court', type: 'court', jurisdiction: 'district-north', status: 'active', permittedFunctions: ['judicial-proceeding', 'record-sealing'] }],
  ['audit', 'aud.qureshi', { name: 'Independent Oversight Office', type: 'oversight', jurisdiction: 'district-north', status: 'active', permittedFunctions: ['audit-review', 'ombudsman-review'] }],
];

const CASES = [
  ['CASE-2026-001', {
    owningAgency: 'police', jurisdiction: 'district-north', status: 'under-investigation',
    assignedUsers: ['insp.sharma', 'io.krishnan'], protectedClassifications: [],
  }],
  ['CASE-2026-002', {
    owningAgency: 'police', jurisdiction: 'district-north', status: 'under-investigation',
    assignedUsers: ['insp.sharma'], protectedClassifications: ['juvenile'],
  }],
];

async function submitOrSkip(org, user, contract, fn, ...args) {
  try {
    const result = await fabric.submit(org, user, contract, fn, ...args);
    console.log(`on-chain  ${fn} ${args[0]}`);
    return result;
  } catch (err) {
    const message = String(err.message || err);
    if (message.includes('already exists')) {
      console.log(`skip      ${fn} ${args[0]}: already on the ledger`);
      return null;
    }
    throw err;
  }
}

async function main() {
  const policyPath = path.resolve(
    __dirname, '..', 'chaincode', 'crimerecords', 'lib', 'policy', 'policyV1.js'
  );
  const rulesHash = crypto.createHash('sha256').update(fs.readFileSync(policyPath)).digest('hex');
  await submitOrSkip(
    'audit', 'aud.qureshi', 'PolicyContract', 'CreatePolicyVersion',
    'crime-policy-v1', rulesHash, 'Initial deterministic contextual policy'
  );
  const active = await fabric.evaluate(
    'audit', 'aud.qureshi', 'PolicyContract', 'GetActivePolicyVersion'
  );
  if (!active) {
    await fabric.submit(
      'audit', 'aud.qureshi', 'PolicyContract', 'ActivatePolicyVersion', 'crime-policy-v1'
    );
    console.log('on-chain  ActivatePolicyVersion crime-policy-v1');
  }

  for (const [org, registrar, profile] of DEPARTMENTS) {
    await submitOrSkip(
      org, registrar, 'GovernanceContract', 'CreateDepartment', org, JSON.stringify(profile)
    );
  }
  for (const [caseId, profile] of CASES) {
    await submitOrSkip(
      'police', 'sho.reddy', 'GovernanceContract', 'CreateCase', caseId,
      JSON.stringify(profile)
    );
  }
}

main().then(() => process.exit(0)).catch((err) => {
  console.error(`domain seed failed: ${err.message || err}`);
  process.exit(1);
});
