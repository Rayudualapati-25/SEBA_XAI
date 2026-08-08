"use strict";

const { getContract } = require("./fabric_connection");

async function main() {
  const requestIdHash = process.argv[2];
  if (!requestIdHash) {
    throw new Error("Usage: node query_audit_event.js <requestIdHash>");
  }
  const { client, gateway, contract } = await getContract();
  try {
    const resultBytes = await contract.evaluateTransaction("ReadAccessDecision", requestIdHash);
    console.log(Buffer.from(resultBytes).toString("utf8"));
  } finally {
    gateway.close();
    client.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
