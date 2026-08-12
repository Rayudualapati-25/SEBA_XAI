const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const E = require("./enums");
const { deploySeba, recordArgs, createRecord } = require("./fixtures");

const NO_TOKEN = "0x";
const decisionString = (d) =>
  d === BigInt(E.Decision.Allow)
    ? "allow"
    : d === BigInt(E.Decision.Deny)
    ? "deny"
    : "escalate";

/** Port of auditContract.test.js — verification, anchoring, reconstruction. */
describe("AuditRegistry", () => {
  describe("verifyRecordPayload", () => {
    it("matches the committed payload hash and rejects a wrong one", async () => {
      const { records, audit, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      const good = recordArgs().payloadHash;
      const bad = ethers.sha256(ethers.toUtf8Bytes("tampered"));

      const okRes = await audit.verifyRecordPayload("REC-1", good);
      expect(okRes.match_).to.equal(true);
      expect(okRes.storedHash).to.equal(good);

      const badRes = await audit.verifyRecordPayload("REC-1", bad);
      expect(badRes.match_).to.equal(false);
    });
  });

  describe("verifyExplanation", () => {
    it("confirms an untampered explanation and flags a tampered one", async () => {
      const { records, access, audit, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      await access
        .connect(who.inspector)
        .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
      const d = await access.getDecision("REC-1", 1);

      const good = await audit.verifyExplanation(
        "REC-1",
        1,
        decisionString(d.decision),
        d.reasonCode,
        d.decisiveAttributes,
        d.counterfactual,
        d.policyVersion
      );
      expect(good.match_).to.equal(true);
      expect(good.computedHash).to.equal(good.storedHash);

      const bad = await audit.verifyExplanation(
        "REC-1",
        1,
        decisionString(d.decision),
        "TAMPERED_REASON",
        d.decisiveAttributes,
        d.counterfactual,
        d.policyVersion
      );
      expect(bad.match_).to.equal(false);
    });
  });

  describe("anchorAccessLog", () => {
    const HEAD = ethers.sha256(ethers.toUtf8Bytes("log-head-1"));

    it("lets the auditor anchor and advance the sequence", async () => {
      const { audit, who } = await loadFixture(deploySeba);
      await expect(audit.connect(who.auditor).anchorAccessLog(1, HEAD, 10, "epoch1"))
        .to.emit(audit, "AccessLogAnchored")
        .withArgs(1, HEAD);

      const latest = await audit.getLatestAccessLogAnchor();
      expect(latest.seqNo).to.equal(1n);
      expect(latest.epoch).to.equal("epoch1");

      const HEAD2 = ethers.sha256(ethers.toUtf8Bytes("log-head-2"));
      await audit.connect(who.auditor).anchorAccessLog(2, HEAD2, 20, "epoch1");
      expect((await audit.getAccessLogAnchors()).length).to.equal(2);
    });

    it("rejects a non-audit caller", async () => {
      const { audit, who } = await loadFixture(deploySeba);
      await expect(
        audit.connect(who.inspector).anchorAccessLog(1, HEAD, 10, "epoch1")
      ).to.be.revertedWith("unauthorized: AnchorAccessLog requires AuditMSP");
    });

    it("refuses to re-anchor an equal-or-lower sequence within an epoch", async () => {
      const { audit, who } = await loadFixture(deploySeba);
      await audit.connect(who.auditor).anchorAccessLog(2, HEAD, 10, "epoch1");
      await expect(
        audit.connect(who.auditor).anchorAccessLog(2, HEAD, 10, "epoch1")
      ).to.be.revertedWith("seqNo must advance within an epoch");
    });

    it("allows a sequence restart under a new epoch", async () => {
      const { audit, who } = await loadFixture(deploySeba);
      await audit.connect(who.auditor).anchorAccessLog(5, HEAD, 10, "epoch1");
      await audit.connect(who.auditor).anchorAccessLog(1, HEAD, 3, "epoch2");
      expect((await audit.getLatestAccessLogAnchor()).epoch).to.equal("epoch2");
    });
  });

  describe("getAuditTrail", () => {
    it("returns record, history and decisions for a reviewer", async () => {
      const { records, access, audit, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      await records.connect(who.judge).sealRecord("REC-1");
      await access
        .connect(who.inspector)
        .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);

      const trail = await audit.connect(who.auditor).getAuditTrail("REC-1");
      expect(trail.record.recordId).to.equal("REC-1");
      expect(trail.history.length).to.equal(2); // created + sealed
      expect(trail.decisions.length).to.equal(1);
    });

    it("rejects a non-reviewer MSP", async () => {
      const { records, audit, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      await expect(
        audit.connect(who.inspector).getAuditTrail("REC-1")
      ).to.be.revertedWith("unauthorized: GetAuditTrail requires a reviewer MSP");
    });
  });
});
