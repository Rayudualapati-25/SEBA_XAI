"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { createMockContext } = require("./helpers/mockStub.js");
const { buildValidEvent } = require("./fixtures/validEvent.js");

describe("SebaAuditContract ReadAccessDecision", () => {
  let transactionContext, chaincodeStub, contract;

  beforeEach(() => {
    ({ transactionContext, chaincodeStub } = createMockContext());
    contract = new SebaAuditContract();
  });

  it("throws when no audit event exists for the requestIdHash", async () => {
    let threw = false;
    try {
      await contract.ReadAccessDecision(transactionContext, "missing-hash");
    } catch (err) {
      threw = true;
      expect(err.message).to.equal("No audit event found for requestIdHash=missing-hash");
    }
    expect(threw).to.equal(true);
  });

  it("throws when the stored buffer is empty", async () => {
    chaincodeStub.states["audit:empty-hash"] = Buffer.from("");

    let threw = false;
    try {
      await contract.ReadAccessDecision(transactionContext, "empty-hash");
    } catch (err) {
      threw = true;
      expect(err.message).to.equal("No audit event found for requestIdHash=empty-hash");
    }
    expect(threw).to.equal(true);
  });

  it("returns the previously recorded ledger record as a JSON string", async () => {
    const event = buildValidEvent();
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(event));

    const raw = await contract.ReadAccessDecision(transactionContext, event.requestIdHash);
    const parsed = JSON.parse(raw);

    expect(parsed.requestIdHash).to.equal(event.requestIdHash);
    expect(parsed.decision).to.equal(event.decision);
    expect(parsed.objectType).to.equal("sebaAuditEvent");
  });
});
