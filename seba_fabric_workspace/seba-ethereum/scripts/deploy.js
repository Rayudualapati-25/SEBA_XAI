/**
 * Deploy the SEBA-XAI contract suite and wire the five-org trust model.
 *
 * Deploy order matters — each contract takes its dependencies in the
 * constructor: IdentityRegistry → RecordRegistry → AccessManager → AuditRegistry.
 *
 * After deployment the script appoints one MSP admin per organisation. On a
 * local network it reuses the deployer for every admin (single-signer demo);
 * on a real network, pass distinct admin addresses via the MSP_*_ADMIN env
 * vars so each organisation controls its own membership, mirroring per-org CAs.
 */
const hre = require("hardhat");

// Msp enum order in PolicyTypes.sol: None, Police, Forensics, Prosecution, Court, Audit
const MSP = { Police: 1, Forensics: 2, Prosecution: 3, Court: 4, Audit: 5 };

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const Identity = await hre.ethers.getContractFactory("IdentityRegistry");
  const identity = await Identity.deploy();
  await identity.waitForDeployment();
  console.log("IdentityRegistry:", await identity.getAddress());

  const Records = await hre.ethers.getContractFactory("RecordRegistry");
  const records = await Records.deploy(await identity.getAddress());
  await records.waitForDeployment();
  console.log("RecordRegistry:  ", await records.getAddress());

  const Access = await hre.ethers.getContractFactory("AccessManager");
  const access = await Access.deploy(
    await identity.getAddress(),
    await records.getAddress()
  );
  await access.waitForDeployment();
  console.log("AccessManager:   ", await access.getAddress());

  const Audit = await hre.ethers.getContractFactory("AuditRegistry");
  const audit = await Audit.deploy(
    await identity.getAddress(),
    await records.getAddress(),
    await access.getAddress()
  );
  await audit.waitForDeployment();
  console.log("AuditRegistry:   ", await audit.getAddress());

  // Appoint one admin per MSP. Defaults to the deployer for a local demo.
  const admins = {
    Police: process.env.MSP_POLICE_ADMIN || deployer.address,
    Forensics: process.env.MSP_FORENSICS_ADMIN || deployer.address,
    Prosecution: process.env.MSP_PROSECUTION_ADMIN || deployer.address,
    Court: process.env.MSP_COURT_ADMIN || deployer.address,
    Audit: process.env.MSP_AUDIT_ADMIN || deployer.address,
  };
  for (const [org, addr] of Object.entries(admins)) {
    const tx = await identity.setMspAdmin(MSP[org], addr);
    await tx.wait();
    console.log(`MSP admin ${org}: ${addr}`);
  }

  console.log("\nDeployment complete.");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
