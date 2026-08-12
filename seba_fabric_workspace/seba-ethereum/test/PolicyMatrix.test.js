const { expect } = require("chai");
const { ethers } = require("hardhat");
const E = require("./enums");

/**
 * Exercises the RBAC base matrix (PolicyV1.rbacMask) across roles, actions and
 * record types via the pure engine. Every subject here clears the ABAC/PBAC
 * gates (active, declared purpose, matching jurisdiction, sufficient clearance,
 * assigned), so the decision turns purely on whether the role/action/type is
 * permitted — an allow means the pair is in the matrix, RBAC_NO_PERMISSION
 * means it is not.
 */
describe("PolicyV1 RBAC matrix", () => {
  let engine;

  before(async () => {
    const Harness = await ethers.getContractFactory("PolicyEngineHarness");
    engine = await Harness.deploy();
    await engine.waitForDeployment();
  });

  const subject = (role) => ({
    msp: E.Msp.Police,
    role,
    jurisdiction: "district-north",
    clearance: E.Clearance.High,
    active: true,
    assignedToCase: true,
  });
  const record = (recordType) => ({
    recordType,
    sensitivity: E.Sensitivity.Low,
    juvenile: false,
    sealed_: false,
    jurisdiction: "district-north",
    caseId: "CASE-1",
  });
  const env = { purpose: E.Purpose.Investigation, emergencyFlag: false, hasApprovalToken: false };

  async function decisionFor(role, action, recordType) {
    const r = await engine.evaluate(subject(role), record(recordType), action, env);
    return { decision: r.decision, reasonCode: r.reasonCode };
  }
  const isAllow = async (...a) =>
    (await decisionFor(...a)).decision === BigInt(E.Decision.Allow);
  const isRbacDeny = async (...a) =>
    (await decisionFor(...a)).reasonCode === "RBAC_NO_PERMISSION";

  const R = E.Role;
  const A = E.Action;
  const T = E.RecordType;

  it("Constable: view fir only", async () => {
    expect(await isAllow(R.Constable, A.View, T.Fir)).to.equal(true);
    expect(await isRbacDeny(R.Constable, A.Annotate, T.Fir)).to.equal(true);
    expect(await isRbacDeny(R.Constable, A.View, T.CaseDiary)).to.equal(true);
  });

  it("SubInspector: view fir/case-diary/witness-statement", async () => {
    expect(await isAllow(R.SubInspector, A.View, T.WitnessStatement)).to.equal(true);
    expect(await isRbacDeny(R.SubInspector, A.View, T.Evidence)).to.equal(true);
  });

  it("Inspector: export fir/case-diary/chargesheet, not court-order", async () => {
    expect(await isAllow(R.Inspector, A.Export, T.Chargesheet)).to.equal(true);
    expect(await isRbacDeny(R.Inspector, A.Export, T.CourtOrder)).to.equal(true);
    expect(await isAllow(R.Inspector, A.Annotate, T.CaseDiary)).to.equal(true);
  });

  it("Sho: view/export all, annotate fir/case-diary", async () => {
    expect(await isAllow(R.Sho, A.Export, T.Evidence)).to.equal(true);
    expect(await isAllow(R.Sho, A.View, T.CourtOrder)).to.equal(true);
    expect(await isRbacDeny(R.Sho, A.Annotate, T.Evidence)).to.equal(true);
  });

  it("InvestigatingOfficer: annotate evidence, export forensic-report", async () => {
    expect(await isAllow(R.InvestigatingOfficer, A.Annotate, T.Evidence)).to.equal(true);
    expect(await isAllow(R.InvestigatingOfficer, A.Export, T.ForensicReport)).to.equal(true);
    expect(await isRbacDeny(R.InvestigatingOfficer, A.Annotate, T.CourtOrder)).to.equal(true);
  });

  it("LabAnalyst: view+annotate forensic-report, no export", async () => {
    expect(await isAllow(R.LabAnalyst, A.View, T.Evidence)).to.equal(true);
    expect(await isAllow(R.LabAnalyst, A.Annotate, T.ForensicReport)).to.equal(true);
    expect(await isRbacDeny(R.LabAnalyst, A.Export, T.ForensicReport)).to.equal(true);
  });

  it("LabDirector: export forensic-report, no annotate", async () => {
    expect(await isAllow(R.LabDirector, A.Export, T.ForensicReport)).to.equal(true);
    expect(await isRbacDeny(R.LabDirector, A.Annotate, T.ForensicReport)).to.equal(true);
  });

  it("PublicProsecutor: view all, export chargesheet/court-order", async () => {
    expect(await isAllow(R.PublicProsecutor, A.Export, T.CourtOrder)).to.equal(true);
    expect(await isRbacDeny(R.PublicProsecutor, A.Export, T.Fir)).to.equal(true);
  });

  it("DefenseCounsel: view chargesheet/court-order only", async () => {
    expect(await isAllow(R.DefenseCounsel, A.View, T.CourtOrder)).to.equal(true);
    expect(await isRbacDeny(R.DefenseCounsel, A.View, T.Fir)).to.equal(true);
  });

  it("Judge/Magistrate: annotate court-order, export all", async () => {
    expect(await isAllow(R.Judge, A.Annotate, T.CourtOrder)).to.equal(true);
    expect(await isAllow(R.Magistrate, A.Export, T.Fir)).to.equal(true);
    expect(await isRbacDeny(R.Magistrate, A.Annotate, T.Fir)).to.equal(true);
  });

  it("CourtClerk: view chargesheet/court-order only", async () => {
    expect(await isAllow(R.CourtClerk, A.View, T.Chargesheet)).to.equal(true);
    expect(await isRbacDeny(R.CourtClerk, A.View, T.Fir)).to.equal(true);
  });

  it("Auditor/Ombudsman: view all, nothing else", async () => {
    expect(await isAllow(R.Auditor, A.View, T.Evidence)).to.equal(true);
    expect(await isAllow(R.Ombudsman, A.View, T.CourtOrder)).to.equal(true);
    expect(await isRbacDeny(R.Auditor, A.Export, T.Fir)).to.equal(true);
  });
});
