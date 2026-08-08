"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { createMockContext } = require("./helpers/mockStub.js");
const { buildValidEvent } = require("./fixtures/validEvent.js");

describe("SebaAuditContract QueryByDecision", () => {
  let transactionContext, contract;

  beforeEach(() => {
    ({ transactionContext } = createMockContext());
    contract = new SebaAuditContract();
  });

  it("rejects an unsupported decision value", async () => {
    let threw = false;
    try {
      await contract.QueryByDecision(transactionContext, "maybe");
    } catch (err) {
      threw = true;
      expect(err.message).to.equal("Unsupported decision=maybe");
    }
    expect(threw).to.equal(true);
  });

  it("returns an empty array when no events match the decision", async () => {
    const raw = await contract.QueryByDecision(transactionContext, "deny");
    expect(JSON.parse(raw)).to.eql([]);
  });

  it("returns only the requestIdHashes recorded under the given decision", async () => {
    const allowed = buildValidEvent({ decision: "allow" });
    const denied = buildValidEvent({
      decision: "deny",
      requestIdHash: "b".repeat(64),
      decisionHash: "c".repeat(64),
    });
    const escalated = buildValidEvent({
      decision: "escalate",
      requestIdHash: "d".repeat(64),
      decisionHash: "e".repeat(64),
    });

    await contract.RecordAccessDecision(transactionContext, JSON.stringify(allowed));
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(denied));
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(escalated));

    const allowResult = JSON.parse(await contract.QueryByDecision(transactionContext, "allow"));
    expect(allowResult).to.eql([allowed.requestIdHash]);

    const denyResult = JSON.parse(await contract.QueryByDecision(transactionContext, "deny"));
    expect(denyResult).to.eql([denied.requestIdHash]);

    const escalateResult = JSON.parse(await contract.QueryByDecision(transactionContext, "escalate"));
    expect(escalateResult).to.eql([escalated.requestIdHash]);
  });

  it("returns multiple requestIdHashes for the same decision", async () => {
    const first = buildValidEvent({ decision: "allow" });
    const second = buildValidEvent({
      decision: "allow",
      requestIdHash: "b".repeat(64),
      decisionHash: "c".repeat(64),
    });

    await contract.RecordAccessDecision(transactionContext, JSON.stringify(first));
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(second));

    const result = JSON.parse(await contract.QueryByDecision(transactionContext, "allow"));
    expect(result.sort()).to.eql([first.requestIdHash, second.requestIdHash].sort());
  });
});
