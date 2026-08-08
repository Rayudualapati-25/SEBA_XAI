"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { createMockContext } = require("./helpers/mockStub.js");

describe("SebaAuditContract InitLedger", () => {
  let transactionContext, chaincodeStub, contract;

  beforeEach(() => {
    ({ transactionContext, chaincodeStub } = createMockContext());
    contract = new SebaAuditContract();
  });

  it("writes a sebaAuditLedgerMetadata document under metadata:seba-audit", async () => {
    chaincodeStub.getTxID.returns("init-tx-1");

    await contract.InitLedger(transactionContext);

    const stored = JSON.parse(chaincodeStub.states["metadata:seba-audit"].toString());
    expect(stored).to.eql({
      objectType: "sebaAuditLedgerMetadata",
      schemaVersion: "SEBA-FABRIC-AUDIT-EVENT-V1",
      rawRecordsOnChain: false,
      purpose: "Commitment-only audit evidence for SEBA-XAI access decisions",
      initializedTxId: "init-tx-1",
    });
  });

  it("returns the metadata document as a JSON string", async () => {
    chaincodeStub.getTxID.returns("init-tx-2");

    const result = await contract.InitLedger(transactionContext);

    expect(JSON.parse(result).initializedTxId).to.equal("init-tx-2");
    expect(JSON.parse(result).rawRecordsOnChain).to.equal(false);
  });

  it("propagates an error when the ledger write fails", async () => {
    chaincodeStub.putState.rejects(new Error("ledger unavailable"));

    let threw = false;
    try {
      await contract.InitLedger(transactionContext);
    } catch (err) {
      threw = true;
      expect(err.message).to.equal("ledger unavailable");
    }
    expect(threw).to.equal(true);
  });
});
