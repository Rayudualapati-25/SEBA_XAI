"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { createMockContext } = require("./helpers/mockStub.js");
const { buildValidEvent } = require("./fixtures/validEvent.js");

describe("SebaAuditContract GetHistoryForRequest", () => {
  let transactionContext, chaincodeStub, contract;

  beforeEach(() => {
    ({ transactionContext, chaincodeStub } = createMockContext());
    contract = new SebaAuditContract();
  });

  it("returns an empty array when the key has never been written", async () => {
    const raw = await contract.GetHistoryForRequest(transactionContext, "never-written-hash");
    expect(JSON.parse(raw)).to.eql([]);
  });

  it("returns every historic version of the audit:<requestIdHash> key", async () => {
    const event = buildValidEvent();
    chaincodeStub.getTxID.returns("history-tx-1");
    await contract.RecordAccessDecision(transactionContext, JSON.stringify(event));

    // Simulate a second ledger-level write of the same key (e.g. state db
    // compaction/rehydration) purely to exercise the multi-entry history path;
    // the contract itself never updates an existing audit event.
    const key = contract._eventKey(event.requestIdHash);
    chaincodeStub.history[key].push({
      txId: "history-tx-2",
      timestamp: { seconds: { low: 1700000000 }, nanos: 0 },
      isDelete: false,
      value: Buffer.from(JSON.stringify({ note: "second-version" })),
    });

    const raw = await contract.GetHistoryForRequest(transactionContext, event.requestIdHash);
    const results = JSON.parse(raw);

    expect(results).to.have.lengthOf(2);
    expect(results[0].txId).to.equal("history-tx-1");
    expect(results[0].isDelete).to.equal(false);
    expect(JSON.parse(results[0].value).requestIdHash).to.equal(event.requestIdHash);
    expect(results[1].txId).to.equal("history-tx-2");
    expect(JSON.parse(results[1].value)).to.eql({ note: "second-version" });
  });
});
