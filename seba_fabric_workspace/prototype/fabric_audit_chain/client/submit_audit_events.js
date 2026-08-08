"use strict";

const fs = require("fs/promises");
const path = require("path");
const { performance } = require("perf_hooks");
const { getContract } = require("./fabric_connection");

function parseArgs(argv) {
  const args = {
    input: path.resolve(__dirname, "../runs/20260702_fabric_audit_event_prep/artifacts/fabric_audit_events.jsonl"),
    output: path.resolve(__dirname, "../runs/20260702_fabric_submit/artifacts/fabric_submit_results.json"),
    limit: 25,
  };
  for (let i = 2; i < argv.length; i += 1) {
    const current = argv[i];
    if (current === "--input") args.input = argv[++i];
    else if (current === "--output") args.output = argv[++i];
    else if (current === "--limit") args.limit = Number(argv[++i]);
    else throw new Error(`Unknown argument: ${current}`);
  }
  return args;
}

async function readJsonl(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

async function main() {
  const args = parseArgs(process.argv);
  const events = (await readJsonl(args.input)).slice(0, args.limit);
  await fs.mkdir(path.dirname(args.output), { recursive: true });

  const { client, gateway, contract, channelName, chaincodeName } = await getContract();
  const submitted = [];
  const started = performance.now();

  try {
    for (const event of events) {
      const eventJson = JSON.stringify(event);
      const eventStart = performance.now();
      const resultBytes = await contract.submitTransaction("RecordAccessDecision", eventJson);
      const eventEnd = performance.now();
      const result = JSON.parse(Buffer.from(resultBytes).toString("utf8"));
      submitted.push({
        requestIdHash: event.requestIdHash,
        fabricTxId: result.fabricTxId,
        eventCommitmentHash: result.eventCommitmentHash,
        latencyMs: eventEnd - eventStart,
      });
    }
  } finally {
    gateway.close();
    client.close();
  }

  const finished = performance.now();
  const latencies = submitted.map((row) => row.latencyMs).sort((a, b) => a - b);
  const p50 = latencies.length ? latencies[Math.floor(latencies.length * 0.5)] : null;
  const p95 = latencies.length ? latencies[Math.floor(latencies.length * 0.95)] : null;
  const output = {
    artifactType: "fabric_submit_results",
    input: args.input,
    channelName,
    chaincodeName,
    eventsRequested: events.length,
    eventsSubmitted: submitted.length,
    elapsedMs: finished - started,
    p50SubmitLatencyMs: p50,
    p95SubmitLatencyMs: p95,
    submitted,
    limitations: [
      "These are Fabric test-network measurements only.",
      "No real police records or CCTNS/ICJS logs are used.",
      "Only commitment hashes and minimal audit metadata are submitted.",
    ],
  };
  await fs.writeFile(args.output, JSON.stringify(output, null, 2), "utf8");
  console.log(`Submitted ${submitted.length} audit events to ${channelName}/${chaincodeName}`);
  console.log(args.output);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
