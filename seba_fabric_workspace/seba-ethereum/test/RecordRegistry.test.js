const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const E = require("./enums");
const { deploySeba, recordArgs, createRecord } = require("./fixtures");

/** Port of recordContract.test.js — creation, evidence, sealing, history. */
describe("RecordRegistry", () => {
  describe("createCaseRecord", () => {
    it("lets a police officer file a record and reads it back", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);

      expect(await records.recordExists("REC-1")).to.equal(true);
      const rec = await records.getRecord("REC-1");
      expect(rec.caseId).to.equal("CASE-1");
      expect(rec.recordType).to.equal(BigInt(E.RecordType.Fir));
      expect(rec.owningMsp).to.equal(BigInt(E.Msp.Police));
      expect(rec.sealed_).to.equal(false);
    });

    it("emits RecordCreated", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await expect(createRecord(records, who.inspector))
        .to.emit(records, "RecordCreated")
        .withArgs("REC-1", "CASE-1", BigInt(E.RecordType.Fir));
    });

    it("rejects a non-police caller", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await expect(createRecord(records, who.analyst)).to.be.revertedWith(
        "unauthorized: wrong MSP for CreateCaseRecord"
      );
    });

    it("rejects duplicate record ids", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      await expect(createRecord(records, who.inspector)).to.be.revertedWith(
        "record already exists"
      );
    });

    it("rejects an unsafe record id", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await expect(
        createRecord(records, who.inspector, { recordId: "bad id!" })
      ).to.be.revertedWith("recordId has invalid format");
    });
  });

  describe("attachEvidenceHash", () => {
    it("lets forensics attach an evidence hash", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      const h = ethers.sha256(ethers.toUtf8Bytes("evidence blob"));
      await expect(
        records.connect(who.analyst).attachEvidenceHash("REC-1", "EV-1", h)
      )
        .to.emit(records, "EvidenceAttached")
        .withArgs("REC-1", "EV-1");

      const list = await records.listEvidence("REC-1");
      expect(list.length).to.equal(1);
      expect(list[0].evidenceHash).to.equal(h);
      expect(list[0].labMsp).to.equal(BigInt(E.Msp.Forensics));
    });

    it("rejects a non-forensics caller", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      const h = ethers.sha256(ethers.toUtf8Bytes("x"));
      await expect(
        records.connect(who.inspector).attachEvidenceHash("REC-1", "EV-1", h)
      ).to.be.revertedWith("unauthorized: wrong MSP for AttachEvidenceHash");
    });

    it("rejects attaching to a missing record", async () => {
      const { records, who } = await loadFixture(deploySeba);
      const h = ethers.sha256(ethers.toUtf8Bytes("x"));
      await expect(
        records.connect(who.analyst).attachEvidenceHash("NOPE", "EV-1", h)
      ).to.be.revertedWith("record does not exist");
    });

    it("rejects duplicate evidence ids", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      const h = ethers.sha256(ethers.toUtf8Bytes("x"));
      await records.connect(who.analyst).attachEvidenceHash("REC-1", "EV-1", h);
      await expect(
        records.connect(who.analyst).attachEvidenceHash("REC-1", "EV-1", h)
      ).to.be.revertedWith("evidence already attached");
    });
  });

  describe("seal / unseal", () => {
    it("lets a judge seal and unseal, recording history", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);

      await expect(records.connect(who.judge).sealRecord("REC-1"))
        .to.emit(records, "RecordSealed")
        .withArgs("REC-1");
      expect((await records.getRecord("REC-1")).sealed_).to.equal(true);

      await expect(records.connect(who.judge).unsealRecord("REC-1"))
        .to.emit(records, "RecordUnsealed")
        .withArgs("REC-1");
      expect((await records.getRecord("REC-1")).sealed_).to.equal(false);

      const hist = await records.getRecordHistory("REC-1");
      expect(hist.map((h) => h.note)).to.deep.equal([
        "created",
        "sealed",
        "unsealed",
      ]);
    });

    it("rejects a non-court sealer", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      await expect(
        records.connect(who.inspector).sealRecord("REC-1")
      ).to.be.revertedWith("unauthorized: wrong MSP for SealRecord");
    });

    it("rejects double-sealing", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector);
      await records.connect(who.judge).sealRecord("REC-1");
      await expect(
        records.connect(who.judge).sealRecord("REC-1")
      ).to.be.revertedWith("record is already sealed");
    });
  });

  describe("queryRecords", () => {
    const emptyFilter = {
      byCaseId: false,
      caseId: "",
      byRecordType: false,
      recordType: 0,
      bySensitivity: false,
      sensitivity: 0,
      byJurisdiction: false,
      jurisdiction: "",
      bySealed: false,
      sealed_: false,
    };

    it("filters by allow-listed metadata", async () => {
      const { records, who } = await loadFixture(deploySeba);
      await createRecord(records, who.inspector, { recordId: "REC-1" });
      await createRecord(records, who.inspector, {
        recordId: "REC-2",
        caseId: "CASE-2",
        recordType: E.RecordType.Chargesheet,
      });

      const byCase = await records.queryRecords({
        ...emptyFilter,
        byCaseId: true,
        caseId: "CASE-2",
      });
      expect(byCase).to.deep.equal(["REC-2"]);

      const byType = await records.queryRecords({
        ...emptyFilter,
        byRecordType: true,
        recordType: E.RecordType.Fir,
      });
      expect(byType).to.deep.equal(["REC-1"]);
    });

    it("requires at least one filter", async () => {
      const { records } = await loadFixture(deploySeba);
      await expect(records.queryRecords(emptyFilter)).to.be.revertedWith(
        "search: at least one filter is required"
      );
    });
  });
});
