"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { createMockContext } = require("./helpers/mockStub.js");
const { buildValidEvent } = require("./fixtures/validEvent.js");

describe("SebaAuditContract VerifyAuditAnchor", () => {
  let transactionContext, contract;

  beforeEach(() => {
    ({ transactionContext } = createMockContext());
    contract = new SebaAuditContract();
  });

  it("reports match=true when the expected anchor hash matches the stored one", async () => {
    const event = buildValidEvent();
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(event));

    const raw = await contract.VerifyAuditAnchor(
      transactionContext,
      event.requestIdHash,
      event.auditAnchorHash,
    );
    const result = JSON.parse(raw);

    expect(result).to.eql({
      requestIdHash: event.requestIdHash,
      expectedAuditAnchorHash: event.auditAnchorHash,
      storedAuditAnchorHash: event.auditAnchorHash,
      match: true,
    });
  });

  it("reports match=false when the expected anchor hash differs from the stored one", async () => {
    const event = buildValidEvent();
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(event));

    const wrongAnchor = "f".repeat(64);
    const raw = await contract.VerifyAuditAnchor(transactionContext, event.requestIdHash, wrongAnchor);
    const result = JSON.parse(raw);

    expect(result.match).to.equal(false);
    expect(result.storedAuditAnchorHash).to.equal(event.auditAnchorHash);
    expect(result.expectedAuditAnchorHash).to.equal(wrongAnchor);
  });

  it("propagates the ReadAccessDecision not-found error for an unknown requestIdHash", async () => {
    let threw = false;
    try {
      await contract.VerifyAuditAnchor(transactionContext, "unknown-hash", "f".repeat(64));
    } catch (err) {
      threw = true;
      expect(err.message).to.equal("No audit event found for requestIdHash=unknown-hash");
    }
    expect(threw).to.equal(true);
  });
});
