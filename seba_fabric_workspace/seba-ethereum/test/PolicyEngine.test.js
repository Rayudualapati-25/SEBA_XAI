const { expect } = require("chai");
const { ethers } = require("hardhat");
const E = require("./enums");

/**
 * Port of the chaincode's policyEngine.test.js. Same base subject/record/env
 * and the same fifteen rule cases, exercised against the pure engine via the
 * PolicyEngineHarness wrapper.
 */
describe("PolicyEngine.evaluate", () => {
  let engine;

  const baseSubject = {
    msp: E.Msp.Police,
    role: E.Role.Inspector,
    jurisdiction: "district-north",
    clearance: E.Clearance.High,
    active: true,
    assignedToCase: true,
  };
  const baseRecord = {
    recordType: E.RecordType.Fir,
    sensitivity: E.Sensitivity.Medium,
    juvenile: false,
    sealed_: false,
    jurisdiction: "district-north",
    caseId: "CASE-1",
  };
  const baseEnv = {
    purpose: E.Purpose.Investigation,
    emergencyFlag: false,
    hasApprovalToken: false,
  };

  const run = (s, r, action, env) => engine.evaluate(s, r, action, env);

  before(async () => {
    const Harness = await ethers.getContractFactory("PolicyEngineHarness");
    engine = await Harness.deploy();
    await engine.waitForDeployment();
  });

  it("allows a fully compliant request with decisive attributes", async () => {
    const r = await run(baseSubject, baseRecord, E.Action.View, baseEnv);
    expect(r.decision).to.equal(BigInt(E.Decision.Allow));
    expect(r.reasonCode).to.equal("POLICY_SATISFIED");
    expect(r.policyVersion).to.equal(E.POLICY_VERSION);
    expect(r.decisiveAttributes).to.contain("subject.role");
  });

  it("denies when credential is not active (rule 1)", async () => {
    const r = await run(
      { ...baseSubject, active: false },
      baseRecord,
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Deny));
    expect(r.reasonCode).to.equal("CRED_NOT_ACTIVE");
    expect(r.counterfactual).to.contain("active");
  });

  it("denies a missing/undeclared purpose (rule 2)", async () => {
    const r = await run(baseSubject, baseRecord, E.Action.View, {
      ...baseEnv,
      purpose: E.Purpose.Unset,
    });
    expect(r.reasonCode).to.equal("INVALID_PURPOSE");
  });

  it("denies when RBAC gives the role no such permission (rule 3)", async () => {
    const constable = {
      ...baseSubject,
      role: E.Role.Constable,
      clearance: E.Clearance.Low,
    };
    const r = await run(
      constable,
      { ...baseRecord, recordType: E.RecordType.CaseDiary },
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Deny));
    expect(r.reasonCode).to.equal("RBAC_NO_PERMISSION");
    expect(r.decisiveAttributes).to.contain("object.recordType");
  });

  it("denies an unknown role entirely", async () => {
    const r = await run(
      { ...baseSubject, role: E.Role.None },
      baseRecord,
      E.Action.View,
      baseEnv
    );
    expect(r.reasonCode).to.equal("RBAC_NO_PERMISSION");
  });

  it("escalates sealed records for non-court callers (rule 4)", async () => {
    const r = await run(
      baseSubject,
      { ...baseRecord, sealed_: true },
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Escalate));
    expect(r.reasonCode).to.equal("SEALED_RECORD");
  });

  it("lets the court view sealed records without escalation (rule 4)", async () => {
    const judge = {
      ...baseSubject,
      msp: E.Msp.Court,
      role: E.Role.Judge,
      jurisdiction: "district-north",
    };
    const r = await run(
      judge,
      { ...baseRecord, sealed_: true },
      E.Action.View,
      { ...baseEnv, purpose: E.Purpose.JudicialProceeding }
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Allow));
  });

  it("escalates juvenile records for non-privileged roles (rule 5)", async () => {
    const r = await run(
      baseSubject,
      { ...baseRecord, juvenile: true },
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Escalate));
    expect(r.reasonCode).to.equal("JUVENILE_PROTECTED");
  });

  it("escalates cross-jurisdiction requests (rule 6)", async () => {
    const r = await run(
      { ...baseSubject, jurisdiction: "district-south" },
      baseRecord,
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Escalate));
    expect(r.reasonCode).to.equal("CROSS_JURISDICTION");
    expect(r.counterfactual).to.contain("district-north");
  });

  it("allows emergency cross-jurisdiction with an approval token (rule 6)", async () => {
    const r = await run(
      { ...baseSubject, jurisdiction: "district-south" },
      baseRecord,
      E.Action.View,
      { ...baseEnv, emergencyFlag: true, hasApprovalToken: true }
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Allow));
    expect(r.reasonCode).to.equal("EMERGENCY_CROSS_JURISDICTION");
  });

  it("denies unassigned officers (rule 7) with a counterfactual", async () => {
    const r = await run(
      { ...baseSubject, assignedToCase: false },
      baseRecord,
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Deny));
    expect(r.reasonCode).to.equal("NOT_ASSIGNED");
    expect(r.counterfactual).to.contain("CASE-1");
  });

  it("exempts judges and auditors from assignment checks (rule 7)", async () => {
    const auditor = {
      ...baseSubject,
      msp: E.Msp.Audit,
      role: E.Role.Auditor,
      assignedToCase: false,
    };
    const r = await run(auditor, baseRecord, E.Action.View, {
      ...baseEnv,
      purpose: E.Purpose.AuditReview,
    });
    expect(r.decision).to.equal(BigInt(E.Decision.Allow));
  });

  it("escalates insufficient clearance (rule 8)", async () => {
    const r = await run(
      { ...baseSubject, clearance: E.Clearance.Low },
      { ...baseRecord, sensitivity: E.Sensitivity.High },
      E.Action.View,
      baseEnv
    );
    expect(r.decision).to.equal(BigInt(E.Decision.Escalate));
    expect(r.reasonCode).to.equal("INSUFFICIENT_CLEARANCE");
  });

  it("treats a missing clearance attribute as no clearance (rule 8)", async () => {
    const r = await run(
      { ...baseSubject, clearance: E.Clearance.Unset },
      baseRecord,
      E.Action.View,
      baseEnv
    );
    expect(r.reasonCode).to.equal("INSUFFICIENT_CLEARANCE");
  });

  it("is deterministic: same input, same output", async () => {
    const a = await run(baseSubject, baseRecord, E.Action.View, baseEnv);
    const b = await run(baseSubject, baseRecord, E.Action.View, baseEnv);
    expect(a.reasonCode).to.equal(b.reasonCode);
    expect(a.decision).to.equal(b.decision);
    expect(a.decisiveAttributes).to.equal(b.decisiveAttributes);
  });
});
