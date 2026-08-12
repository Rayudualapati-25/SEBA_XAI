const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const E = require("./enums");
const { deploySeba, createRecord } = require("./fixtures");

const NO_TOKEN = "0x";

/** Port of accessContract.test.js — request flow + escalation resolution. */
describe("AccessManager", () => {
  async function withRecord(overrides) {
    const ctx = await loadFixture(deploySeba);
    await createRecord(ctx.records, ctx.who.inspector, overrides);
    return ctx;
  }

  it("grants a fully compliant request and stores the explanation", async () => {
    const { access, who } = await withRecord();
    await expect(
      access
        .connect(who.inspector)
        .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN)
    ).to.emit(access, "AccessDecisionMade");

    const d = await access.getDecision("REC-1", 1);
    expect(d.decision).to.equal(BigInt(E.Decision.Allow));
    expect(d.status).to.equal(BigInt(E.Status.Granted));
    expect(d.reasonCode).to.equal("POLICY_SATISFIED");
    expect(d.explanationHash).to.not.equal(ethers.ZeroHash);
  });

  it("denies a request the RBAC matrix forbids", async () => {
    const { access, records, who } = await withRecord();
    await createRecord(records, who.inspector, {
      recordId: "REC-CD",
      recordType: E.RecordType.CaseDiary,
    });
    await access
      .connect(who.constable)
      .requestAccess("REC-CD", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    const d = await access.getDecision("REC-CD", 1);
    expect(d.decision).to.equal(BigInt(E.Decision.Deny));
    expect(d.reasonCode).to.equal("RBAC_NO_PERMISSION");
    expect(d.status).to.equal(BigInt(E.Status.Denied));
  });

  it("escalates and lists the pending decision", async () => {
    const { access, who } = await withRecord();
    // Constable (low clearance) on a medium record → INSUFFICIENT_CLEARANCE.
    await access
      .connect(who.constable)
      .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    const d = await access.getDecision("REC-1", 1);
    expect(d.decision).to.equal(BigInt(E.Decision.Escalate));
    expect(d.status).to.equal(BigInt(E.Status.Pending));

    const pending = await access.queryPendingEscalations();
    expect(pending.length).to.equal(1);
    expect(pending[0].decisionId).to.equal(1n);
  });

  it("lets a supervisor approve an escalation", async () => {
    const { access, who } = await withRecord();
    await access
      .connect(who.constable)
      .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    await expect(access.connect(who.sho).approveEscalation("REC-1", 1, "ok"))
      .to.emit(access, "EscalationResolved")
      .withArgs(1, "REC-1", true);
    const d = await access.getDecision("REC-1", 1);
    expect(d.status).to.equal(BigInt(E.Status.Approved));
    expect(d.resolvedByRole).to.equal(BigInt(E.Role.Sho));
  });

  it("lets a supervisor reject an escalation", async () => {
    const { access, who } = await withRecord();
    await access
      .connect(who.constable)
      .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    await access.connect(who.sho).rejectEscalation("REC-1", 1, "no");
    const d = await access.getDecision("REC-1", 1);
    expect(d.status).to.equal(BigInt(E.Status.Rejected));
  });

  it("blocks a non-approver from resolving", async () => {
    const { access, who } = await withRecord();
    await access
      .connect(who.constable)
      .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    await expect(
      access.connect(who.analyst).approveEscalation("REC-1", 1, "x")
    ).to.be.revertedWith("unauthorized: role may not resolve escalations");
  });

  it("blocks the requester from approving its own escalation", async () => {
    const { access, records, who } = await withRecord();
    // Seal the record so even the SHO (an approver) escalates on it.
    await records.connect(who.judge).sealRecord("REC-1");
    await access
      .connect(who.sho)
      .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    const d = await access.getDecision("REC-1", 1);
    expect(d.reasonCode).to.equal("SEALED_RECORD");
    await expect(
      access.connect(who.sho).approveEscalation("REC-1", 1, "self")
    ).to.be.revertedWith(
      "unauthorized: requester cannot approve its own escalation"
    );
    // A different approver (the judge) can resolve it.
    await access.connect(who.judge).approveEscalation("REC-1", 1, "ok");
    expect((await access.getDecision("REC-1", 1)).status).to.equal(
      BigInt(E.Status.Approved)
    );
  });

  it("rejects a caller with no registered role", async () => {
    const { access, who } = await withRecord();
    await expect(
      access
        .connect(who.outsider)
        .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN)
    ).to.be.revertedWith("unauthorized: caller has no role");
  });

  it("commits only a hash of the approval token, allowing emergency access", async () => {
    const { access, records, who } = await withRecord({
      recordId: "REC-S",
      jurisdiction: "district-south",
    });
    const token = ethers.toUtf8Bytes("emergency-token-xyz");
    await access
      .connect(who.inspector)
      .requestAccess("REC-S", E.Action.View, E.Purpose.Investigation, true, "court-42", token);
    const d = await access.getDecision("REC-S", 1);
    expect(d.decision).to.equal(BigInt(E.Decision.Allow));
    expect(d.reasonCode).to.equal("EMERGENCY_CROSS_JURISDICTION");
    expect(d.approvalTokenHash).to.equal(ethers.sha256(token));
    expect(d.courtLink).to.equal("court-42");
  });
});
