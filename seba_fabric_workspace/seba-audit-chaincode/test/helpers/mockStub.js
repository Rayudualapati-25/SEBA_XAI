"use strict";

/**
 * Test double for the Hyperledger Fabric ChaincodeStub.
 *
 * Follows the same pattern used by the official fabric-samples
 * asset-transfer-basic chaincode-javascript test suite: a sinon stub
 * instance of `ChaincodeStub`, wired to an in-memory state map via
 * `callsFake`. Extended here with composite-key indexing and history
 * support so the SebaAuditContract's index/history/query methods can be
 * exercised without a live peer.
 */

const sinon = require("sinon");
const { Context } = require("fabric-contract-api");
const { ChaincodeStub } = require("fabric-shim");

const DEFAULT_TX_ID = "tx-0";
const DEFAULT_TX_TIMESTAMP = {
  seconds: { low: 1690000000 },
  nanos: 500000000,
};

function buildIterator(entries) {
  let index = 0;
  return {
    next: async () => {
      if (index < entries.length) {
        const value = entries[index];
        index += 1;
        return { value, done: false };
      }
      return { value: undefined, done: true };
    },
    close: async () => {},
  };
}

function createMockContext() {
  const transactionContext = new Context();
  const chaincodeStub = sinon.createStubInstance(ChaincodeStub);
  transactionContext.setChaincodeStub(chaincodeStub);

  chaincodeStub.states = {};
  chaincodeStub.history = {};
  chaincodeStub.events = [];

  // createCompositeKey / splitCompositeKey are pure functions on the real
  // ChaincodeStub prototype (no gRPC handler involved), so we can let the
  // stub call through to the real implementation instead of re-modelling it.
  chaincodeStub.createCompositeKey.callThrough();
  chaincodeStub.splitCompositeKey.callThrough();

  chaincodeStub.putState.callsFake(async (key, value) => {
    chaincodeStub.states[key] = value;
    if (!chaincodeStub.history[key]) {
      chaincodeStub.history[key] = [];
    }
    chaincodeStub.history[key].push({
      txId: chaincodeStub.getTxID() || DEFAULT_TX_ID,
      timestamp: DEFAULT_TX_TIMESTAMP,
      isDelete: false,
      value,
    });
  });

  chaincodeStub.getState.callsFake(async (key) => chaincodeStub.states[key]);

  chaincodeStub.deleteState.callsFake(async (key) => {
    delete chaincodeStub.states[key];
  });

  chaincodeStub.getHistoryForKey.callsFake(async (key) =>
    buildIterator(chaincodeStub.history[key] || []),
  );

  chaincodeStub.getStateByPartialCompositeKey.callsFake(async (objectType, attributes) => {
    const prefix = chaincodeStub.createCompositeKey(objectType, attributes);
    const entries = Object.keys(chaincodeStub.states)
      .filter((key) => key.startsWith(prefix))
      .map((key) => ({ key, value: chaincodeStub.states[key] }));
    return buildIterator(entries);
  });

  chaincodeStub.setEvent.callsFake((name, payload) => {
    chaincodeStub.events.push({ name, payload });
  });

  chaincodeStub.getTxID.returns(DEFAULT_TX_ID);
  chaincodeStub.getTxTimestamp.returns(DEFAULT_TX_TIMESTAMP);

  return { transactionContext, chaincodeStub };
}

module.exports = { createMockContext, buildIterator, DEFAULT_TX_ID, DEFAULT_TX_TIMESTAMP };
