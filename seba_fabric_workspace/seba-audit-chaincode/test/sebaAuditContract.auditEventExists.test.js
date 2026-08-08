"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { createMockContext } = require("./helpers/mockStub.js");
const { buildValidEvent } = require("./fixtures/validEvent.js");

describe("SebaAuditContract AuditEventExists", () => {
  let transactionContext, chaincodeStub, contract;

  beforeEach(() => {
    ({ transactionContext, chaincodeStub } = createMockContext());
    contract = new SebaAuditContract();
  });

  it("returns a falsy value when no state has ever been written for the hash", async () => {
    // NOTE: sebaAuditContract.js:73 implements `return buffer && buffer.length > 0;`.
    // When `getState` resolves undefined (key never written), `undefined && ...`
    // short-circuits to `undefined`, not the boolean `false` the JSDoc/spec
    // promises ("returns bool"). This test documents that real, unfixed
    // behavior rather than the intended boolean contract.
    const exists = await contract.AuditEventExists(transactionContext, "unknown-hash");
    expect(exists).to.equal(undefined);
    expect(exists).to.not.be.ok;
  });

  it("returns false when the stored buffer is empty", async () => {
    chaincodeStub.states["audit:empty-hash"] = Buffer.from("");
    const exists = await contract.AuditEventExists(transactionContext, "empty-hash");
    expect(exists).to.equal(false);
  });

  it("returns true after RecordAccessDecision has written the event", async () => {
    const event = buildValidEvent();
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(event));

    const exists = await contract.AuditEventExists(transactionContext, event.requestIdHash);
    expect(exists).to.equal(true);
  });
});
