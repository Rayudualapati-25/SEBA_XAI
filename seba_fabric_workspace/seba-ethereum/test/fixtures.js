const { ethers } = require("hardhat");
const E = require("./enums");

/**
 * Deploy the full SEBA-XAI suite and register a cast of identities across the
 * five organisations. The deployer is owner and is set as admin for every MSP
 * (single-signer test setup), so it can register members of any org.
 *
 * Returns the contracts and a `who` map of role → signer.
 */
async function deploySeba() {
  const signers = await ethers.getSigners();
  const [
    deployer,
    inspector,
    constable,
    analyst,
    judge,
    prosecutor,
    auditor,
    sho,
    outsider,
  ] = signers;

  const Identity = await ethers.getContractFactory("IdentityRegistry");
  const identity = await Identity.deploy();
  await identity.waitForDeployment();

  const Records = await ethers.getContractFactory("RecordRegistry");
  const records = await Records.deploy(await identity.getAddress());
  await records.waitForDeployment();

  const Access = await ethers.getContractFactory("AccessManager");
  const access = await Access.deploy(
    await identity.getAddress(),
    await records.getAddress()
  );
  await access.waitForDeployment();

  const Audit = await ethers.getContractFactory("AuditRegistry");
  const audit = await Audit.deploy(
    await identity.getAddress(),
    await records.getAddress(),
    await access.getAddress()
  );
  await audit.waitForDeployment();

  // Deployer administers every MSP in tests.
  for (const msp of [
    E.Msp.Police,
    E.Msp.Forensics,
    E.Msp.Prosecution,
    E.Msp.Court,
    E.Msp.Audit,
  ]) {
    await identity.setMspAdmin(msp, deployer.address);
  }

  const reg = (who, msp, role, jur, clr) =>
    identity.registerIdentity(who.address, msp, role, "STN", jur, clr);

  await reg(inspector, E.Msp.Police, E.Role.Inspector, "district-north", E.Clearance.High);
  await reg(constable, E.Msp.Police, E.Role.Constable, "district-north", E.Clearance.Low);
  await reg(analyst, E.Msp.Forensics, E.Role.LabAnalyst, "district-north", E.Clearance.Medium);
  await reg(judge, E.Msp.Court, E.Role.Judge, "district-north", E.Clearance.High);
  await reg(prosecutor, E.Msp.Prosecution, E.Role.PublicProsecutor, "district-north", E.Clearance.High);
  await reg(auditor, E.Msp.Audit, E.Role.Auditor, "district-north", E.Clearance.High);
  await reg(sho, E.Msp.Police, E.Role.Sho, "district-north", E.Clearance.High);

  // Case assignments for the non-exempt officers used in access tests.
  await identity.assignCase(inspector.address, "CASE-1");
  await identity.assignCase(constable.address, "CASE-1");

  return {
    identity,
    records,
    access,
    audit,
    who: {
      deployer,
      inspector,
      constable,
      analyst,
      judge,
      prosecutor,
      auditor,
      sho,
      outsider,
    },
  };
}

// Standard record metadata used across tests.
function recordArgs(overrides = {}) {
  return {
    recordId: "REC-1",
    caseId: "CASE-1",
    recordType: E.RecordType.Fir,
    sensitivity: E.Sensitivity.Medium,
    juvenile: false,
    witness: false,
    owningStation: "PS-Central",
    jurisdiction: "district-north",
    payloadHash: ethers.sha256(ethers.toUtf8Bytes("the real record payload")),
    offchainUri: "ipfs://Qm-example",
    ...overrides,
  };
}

async function createRecord(records, signer, overrides = {}) {
  const a = recordArgs(overrides);
  return records
    .connect(signer)
    .createCaseRecord(
      a.recordId,
      a.caseId,
      a.recordType,
      a.sensitivity,
      a.juvenile,
      a.witness,
      a.owningStation,
      a.jurisdiction,
      a.payloadHash,
      a.offchainUri
    );
}

module.exports = { deploySeba, recordArgs, createRecord };
