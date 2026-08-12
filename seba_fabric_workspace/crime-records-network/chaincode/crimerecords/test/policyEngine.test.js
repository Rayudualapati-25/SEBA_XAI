'use strict';

const { expect } = require('chai');
const { evaluate, POLICY_VERSION } = require('../lib/policy/policyEngine');

const baseSubject = {
  mspId: 'PoliceMSP', role: 'inspector', station: 'PS-Central',
  jurisdiction: 'district-north', clearance: 'high',
  credentialStatus: 'active', caseAssignments: 'CASE-1,CASE-2',
};
const baseRecord = {
  caseId: 'CASE-1', recordType: 'fir', sensitivityLevel: 'medium',
  juvenileFlag: false, sealed: false, jurisdiction: 'district-north',
};
const baseEnv = { purpose: 'investigation', emergencyFlag: false };

describe('policyEngine.evaluate', () => {
  it('allows a fully compliant request with decisive attributes', () => {
    const r = evaluate(baseSubject, baseRecord, 'view', baseEnv);
    expect(r.decision).to.equal('allow');
    expect(r.reasonCode).to.equal('POLICY_SATISFIED');
    expect(r.policyVersion).to.equal(POLICY_VERSION);
    expect(r.decisiveAttributes).to.include('subject.role');
  });

  it('denies when credential is not active (rule 1)', () => {
    const r = evaluate({ ...baseSubject, credentialStatus: 'revoked' },
      baseRecord, 'view', baseEnv);
    expect(r.decision).to.equal('deny');
    expect(r.reasonCode).to.equal('CRED_NOT_ACTIVE');
    expect(r.counterfactual).to.contain('active');
  });

  it('denies a missing or unknown purpose (rule 2)', () => {
    expect(evaluate(baseSubject, baseRecord, 'view', {}).reasonCode)
      .to.equal('INVALID_PURPOSE');
    expect(evaluate(baseSubject, baseRecord, 'view', { purpose: 'curiosity' }).reasonCode)
      .to.equal('INVALID_PURPOSE');
  });

  it('denies when RBAC gives the role no such permission (rule 3)', () => {
    const constable = { ...baseSubject, role: 'constable', clearance: 'low' };
    const r = evaluate(constable, { ...baseRecord, recordType: 'case-diary' }, 'view', baseEnv);
    expect(r.decision).to.equal('deny');
    expect(r.reasonCode).to.equal('RBAC_NO_PERMISSION');
    expect(r.decisiveAttributes).to.include('object.recordType');
  });

  it('denies an unknown role entirely', () => {
    const r = evaluate({ ...baseSubject, role: 'janitor' }, baseRecord, 'view', baseEnv);
    expect(r.reasonCode).to.equal('RBAC_NO_PERMISSION');
  });

  it('escalates sealed records for non-court callers (rule 4)', () => {
    const r = evaluate(baseSubject, { ...baseRecord, sealed: true }, 'view', baseEnv);
    expect(r.decision).to.equal('escalate');
    expect(r.reasonCode).to.equal('SEALED_RECORD');
  });

  it('lets the court view sealed records without escalation (rule 4)', () => {
    const judge = {
      ...baseSubject, mspId: 'CourtMSP', role: 'judge', jurisdiction: 'district-north',
    };
    const r = evaluate(judge, { ...baseRecord, sealed: true }, 'view',
      { purpose: 'judicial-proceeding' });
    expect(r.decision).to.equal('allow');
  });

  it('denies juvenile records for roles outside the narrow legal exception (rule 5)', () => {
    const r = evaluate(baseSubject, { ...baseRecord, juvenileFlag: true }, 'view', baseEnv);
    expect(r.decision).to.equal('deny');
    expect(r.reasonCode).to.equal('JUVENILE_PROTECTED');
  });

  it('denies victim-protected raw content to forensics under data minimization', () => {
    const analyst = {
      ...baseSubject, mspId: 'ForensicsMSP', role: 'lab-analyst',
      caseAssignments: 'CASE-1', clearance: 'medium',
    };
    const result = evaluate(analyst, {
      ...baseRecord, recordType: 'evidence', victimProtectionFlag: true,
    }, 'view', { purpose: 'forensic-analysis' });
    expect(result.decision).to.equal('deny');
    expect(result.reasonCode).to.equal('VICTIM_DATA_NOT_NECESSARY');
  });

  it('escalates cross-jurisdiction requests (rule 6)', () => {
    const r = evaluate({ ...baseSubject, jurisdiction: 'district-south' },
      baseRecord, 'view', baseEnv);
    expect(r.decision).to.equal('escalate');
    expect(r.reasonCode).to.equal('CROSS_JURISDICTION');
    expect(r.counterfactual).to.contain('district-north');
  });

  it('allows emergency cross-jurisdiction with an approval token (rule 6)', () => {
    const r = evaluate({ ...baseSubject, jurisdiction: 'district-south' },
      baseRecord, 'view',
      { ...baseEnv, emergencyFlag: true, approvalToken: 'tok-1' });
    expect(r.decision).to.equal('allow');
    expect(r.reasonCode).to.equal('EMERGENCY_CROSS_JURISDICTION');
  });

  it('denies unassigned officers (rule 7) with a counterfactual', () => {
    const r = evaluate({ ...baseSubject, caseAssignments: 'CASE-9' },
      baseRecord, 'view', baseEnv);
    expect(r.decision).to.equal('deny');
    expect(r.reasonCode).to.equal('NOT_ASSIGNED');
    expect(r.counterfactual).to.contain('CASE-1');
  });

  it('treats a null assignment list as unassigned (rule 7)', () => {
    const r = evaluate({ ...baseSubject, caseAssignments: null },
      baseRecord, 'view', baseEnv);
    expect(r.reasonCode).to.equal('NOT_ASSIGNED');
  });

  it('denies raw content to auditors while retaining metadata-only review', () => {
    const auditor = {
      ...baseSubject, mspId: 'AuditMSP', role: 'auditor', caseAssignments: null,
    };
    const r = evaluate(auditor, baseRecord, 'view', { purpose: 'audit-review' });
    expect(r.decision).to.equal('deny');
    expect(r.reasonCode).to.equal('AUDIT_METADATA_ONLY');
  });

  it('escalates insufficient clearance (rule 8)', () => {
    const r = evaluate({ ...baseSubject, clearance: 'low' },
      { ...baseRecord, sensitivityLevel: 'high' }, 'view', baseEnv);
    expect(r.decision).to.equal('escalate');
    expect(r.reasonCode).to.equal('INSUFFICIENT_CLEARANCE');
  });

  it('treats a missing clearance attribute as no clearance (rule 8)', () => {
    const r = evaluate({ ...baseSubject, clearance: null },
      baseRecord, 'view', baseEnv);
    expect(r.reasonCode).to.equal('INSUFFICIENT_CLEARANCE');
  });

  it('is deterministic: same input, same output', () => {
    const a = evaluate(baseSubject, baseRecord, 'view', baseEnv);
    const b = evaluate(baseSubject, baseRecord, 'view', baseEnv);
    expect(a).to.deep.equal(b);
  });
});
