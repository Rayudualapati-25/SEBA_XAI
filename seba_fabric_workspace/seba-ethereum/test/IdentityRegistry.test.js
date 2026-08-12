const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const E = require("./enums");
const { deploySeba, createRecord } = require("./fixtures");

const NO_TOKEN = "0x";

/** The on-chain replacement for Fabric's MSP + certificate attributes. */
describe("IdentityRegistry", () => {
  async function fresh() {
    const [owner, policeAdmin, member, other] = await ethers.getSigners();
    const Identity = await ethers.getContractFactory("IdentityRegistry");
    const identity = await Identity.deploy();
    await identity.waitForDeployment();
    return { identity, owner, policeAdmin, member, other };
  }

  it("sets the deployer as owner", async () => {
    const { identity, owner } = await fresh();
    expect(await identity.owner()).to.equal(owner.address);
  });

  it("only the owner may appoint MSP admins", async () => {
    const { identity, policeAdmin } = await fresh();
    await expect(
      identity.connect(policeAdmin).setMspAdmin(E.Msp.Police, policeAdmin.address)
    ).to.be.revertedWith("identity: caller is not owner");
  });

  it("an MSP admin may register members only within its own MSP", async () => {
    const { identity, policeAdmin, member } = await fresh();
    await identity.setMspAdmin(E.Msp.Police, policeAdmin.address);

    await identity
      .connect(policeAdmin)
      .registerIdentity(member.address, E.Msp.Police, E.Role.Inspector, "S", "j", E.Clearance.High);
    expect(await identity.mspOf(member.address)).to.equal(BigInt(E.Msp.Police));

    // Same admin cannot register into a different MSP.
    await expect(
      identity
        .connect(policeAdmin)
        .registerIdentity(member.address, E.Msp.Court, E.Role.Judge, "S", "j", E.Clearance.High)
    ).to.be.revertedWith("identity: caller is not an admin for this MSP");
  });

  it("rejects a role that does not belong to the MSP", async () => {
    const { identity, member } = await fresh();
    await expect(
      identity.registerIdentity(member.address, E.Msp.Police, E.Role.Judge, "S", "j", E.Clearance.High)
    ).to.be.revertedWith("identity: role does not belong to MSP");
  });

  it("validates register inputs", async () => {
    const { identity, member } = await fresh();
    await expect(
      identity.registerIdentity(ethers.ZeroAddress, E.Msp.Police, E.Role.Inspector, "S", "j", E.Clearance.High)
    ).to.be.revertedWith("identity: zero subject");
    await expect(
      identity.registerIdentity(member.address, E.Msp.None, E.Role.Inspector, "S", "j", E.Clearance.High)
    ).to.be.revertedWith("identity: invalid MSP");
    await expect(
      identity.registerIdentity(member.address, E.Msp.Police, E.Role.None, "S", "j", E.Clearance.High)
    ).to.be.revertedWith("identity: invalid role");
  });

  it("updates attributes and enforces MSP-consistent roles", async () => {
    const { identity, member } = await fresh();
    await identity.registerIdentity(member.address, E.Msp.Police, E.Role.Constable, "S", "j", E.Clearance.Low);
    await identity.updateAttributes(member.address, E.Role.Inspector, "S2", "j2", E.Clearance.High);
    const id = await identity.getIdentity(member.address);
    expect(id.role).to.equal(BigInt(E.Role.Inspector));
    expect(id.jurisdiction).to.equal("j2");
    await expect(
      identity.updateAttributes(member.address, E.Role.Judge, "S", "j", E.Clearance.High)
    ).to.be.revertedWith("identity: role does not belong to MSP");
  });

  it("assigns and revokes case membership", async () => {
    const { identity, member } = await fresh();
    await identity.registerIdentity(member.address, E.Msp.Police, E.Role.Inspector, "S", "j", E.Clearance.High);
    await identity.assignCase(member.address, "CASE-7");
    expect(await identity.isAssignedToCase(member.address, "CASE-7")).to.equal(true);
    await identity.revokeCase(member.address, "CASE-7");
    expect(await identity.isAssignedToCase(member.address, "CASE-7")).to.equal(false);
  });

  it("builds a subject snapshot for the policy engine", async () => {
    const { identity, member } = await fresh();
    await identity.registerIdentity(member.address, E.Msp.Police, E.Role.Inspector, "S", "north", E.Clearance.Medium);
    await identity.assignCase(member.address, "CASE-1");
    const s = await identity.subjectFor(member.address, "CASE-1");
    expect(s.role).to.equal(BigInt(E.Role.Inspector));
    expect(s.jurisdiction).to.equal("north");
    expect(s.clearance).to.equal(BigInt(E.Clearance.Medium));
    expect(s.active).to.equal(true);
    expect(s.assignedToCase).to.equal(true);
  });

  it("requireMsp passes members and rejects non-members", async () => {
    const { identity, member } = await fresh();
    await identity.registerIdentity(member.address, E.Msp.Police, E.Role.Inspector, "S", "j", E.Clearance.High);
    await expect(identity.requireMsp(member.address, [E.Msp.Police], "X")).to.not.be.reverted;
    await expect(
      identity.requireMsp(member.address, [E.Msp.Court], "X")
    ).to.be.revertedWith("unauthorized: wrong MSP for X");
  });

  it("transfers ownership", async () => {
    const { identity, other } = await fresh();
    await identity.transferOwnership(other.address);
    expect(await identity.owner()).to.equal(other.address);
  });

  it("revocation (setActive false) makes the policy engine deny (rule 1)", async () => {
    const { identity, access, records, who } = await loadFixture(deploySeba);
    await createRecord(records, who.inspector);
    await identity.setActive(who.inspector.address, false);
    await access
      .connect(who.inspector)
      .requestAccess("REC-1", E.Action.View, E.Purpose.Investigation, false, "", NO_TOKEN);
    const d = await access.getDecision("REC-1", 1);
    expect(d.reasonCode).to.equal("CRED_NOT_ACTIVE");
    expect(d.decision).to.equal(BigInt(E.Decision.Deny));
  });
});
