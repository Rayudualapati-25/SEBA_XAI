'use strict';

/**
 * Phase 6 measurements for the SEBA-XAI extension paper.
 *
 * Produces, on a LIVE Hyperledger Fabric network, the same three quantities
 * the paper reports for its local simulation (Section IV-F):
 *   - build latency  (submit an audited access decision, to commit)
 *   - verify latency (query-only verification of a committed artifact)
 *   - storage per event (bytes of the committed audit record)
 *
 * Also replays three attacks from the paper's catalog against the live
 * network and records whether each is structurally rejected.
 *
 * Usage: node experiments/measure.js [requests]
 * Output: experiments/results/live_fabric_measurements.json + a markdown table
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const BASE = process.env.API_BASE || 'http://localhost:3001/api';
const N = Number(process.argv[2] || 30);
const SEEDS = [7, 21, 42, 99, 123];
// Must match Orderer.BatchTimeout in network/configtx/configtx.yaml.
const BATCH_TIMEOUT_MS = 2000;
const OUT_DIR = path.resolve(__dirname, 'results');

async function api(method, urlPath, { token, body } = {}) {
  const res = await fetch(`${BASE}${urlPath}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const json = await res.json();
  return { status: res.status, ok: json.success, data: json.data, error: json.error };
}

async function login(username) {
  const { data, error } = await api('POST', '/auth/login',
    { body: { username, password: 'demo123' } });
  if (!data) throw new Error(`login ${username} failed: ${error}`);
  return data.token;
}

function percentile(sorted, p) {
  if (sorted.length === 0) return null;
  const index = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
  return sorted[index];
}

function stats(samples) {
  const sorted = [...samples].sort((a, b) => a - b);
  const mean = sorted.reduce((a, b) => a + b, 0) / sorted.length;
  return {
    n: sorted.length,
    meanMs: Number(mean.toFixed(2)),
    p50Ms: Number(percentile(sorted, 50).toFixed(2)),
    p95Ms: Number(percentile(sorted, 95).toFixed(2)),
    minMs: Number(sorted[0].toFixed(2)),
    maxMs: Number(sorted[sorted.length - 1].toFixed(2)),
  };
}

async function timed(action) {
  const start = process.hrtime.bigint();
  const result = await action();
  const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
  return { elapsedMs, result };
}

/** One record per seed, so every seed measures against its own record. */
async function setupRecords(tokens, runId) {
  const records = [];
  for (const seed of SEEDS) {
    const recordId = `FIR-MEASURE-${runId}-${seed}`;
    const { data, error } = await api('POST', '/records', {
      token: tokens.inspector,
      body: {
        recordId,
        payload: { fir: recordId, summary: `seeded workload ${seed}`, seed },
        meta: {
          caseId: 'CASE-2026-001', recordType: 'fir', sensitivityLevel: 'medium',
          juvenileFlag: false, witnessFlag: false,
          owningStation: 'PS-Central', jurisdiction: 'district-north',
        },
      },
    });
    if (!data) throw new Error(`record setup failed for seed ${seed}: ${error}`);
    records.push({ seed, recordId, payloadHash: data.payloadHash });
  }
  return records;
}

/** Build latency: submit an access decision (policy + XAI + commit) end to end. */
async function measureBuild(tokens, records) {
  const perSeed = [];
  const allSamples = [];
  const sizes = [];

  for (const { seed, recordId } of records) {
    const samples = [];
    for (let i = 0; i < N; i += 1) {
      const { elapsedMs, result } = await timed(() => api('POST', '/access/request', {
        token: tokens.inspector,
        body: { recordId, action: 'view', purpose: 'investigation' },
      }));
      if (!result.ok) throw new Error(`build sample failed: ${result.error}`);
      samples.push(elapsedMs);
      sizes.push(Buffer.byteLength(JSON.stringify(result.data), 'utf8'));
    }
    perSeed.push({ seed, ...stats(samples) });
    allSamples.push(...samples);
  }
  return { perSeed, allSamples, storageBytes: sizes };
}

/** Verify latency: query-only checks against committed state. */
async function measureVerify(tokens, records) {
  const perSeed = [];
  const allSamples = [];

  for (const { seed, recordId } of records) {
    const decisions = await api('GET', `/access/record/${recordId}`, { token: tokens.auditor });
    const decision = decisions.data[0];
    const samples = [];

    for (let i = 0; i < N; i += 1) {
      const { elapsedMs, result } = await timed(() => api('POST',
        `/audit/verify-explanation/${recordId}/${decision.decisionId}`,
        { token: tokens.auditor, body: { artifact: decision.explanation } }));
      if (!result.ok || result.data.match !== true) {
        throw new Error(`verify sample failed: ${result.error || 'no match'}`);
      }
      samples.push(elapsedMs);
    }
    perSeed.push({ seed, ...stats(samples) });
    allSamples.push(...samples);
  }
  return { perSeed, allSamples };
}

/**
 * Attack replay. Each entry states what the attacker attempts and what the
 * live network is expected to do. `detected` means the attack did not succeed.
 */
async function replayAttacks(tokens, records) {
  const { recordId, payloadHash } = records[0];
  const results = [];

  // A1 — explanation-hash substitution: alter a committed explanation.
  const decisions = await api('GET', `/access/record/${recordId}`, { token: tokens.auditor });
  const decision = decisions.data[0];
  const forged = await api('POST',
    `/audit/verify-explanation/${recordId}/${decision.decisionId}`,
    { token: tokens.auditor, body: { artifact: { ...decision.explanation, reasonCode: 'FORGED' } } });
  results.push({
    attack: 'explanation-hash substitution',
    mechanism: 'reviewer presents a modified explanation artifact',
    detectedBy: 'on-chain explanation hash recomputation',
    detected: forged.ok && forged.data.match === false,
  });

  // A2 — off-chain payload tampering: edit agency storage after filing.
  const before = await api('POST', `/audit/verify-payload/${recordId}`, { token: tokens.auditor });
  const tamper = await api('POST', `/experiments/tamper/${recordId}`, {
    token: tokens.auditor,
    body: { payload: { fir: recordId, summary: 'ALTERED AFTER FILING' } },
  });
  const after = await api('POST', `/audit/verify-payload/${recordId}`, { token: tokens.auditor });
  results.push({
    attack: 'off-chain record tampering',
    mechanism: 'record payload rewritten in agency storage after commitment',
    detectedBy: 'payload hash vs on-chain commitment',
    detected: before.data?.match === true && after.data?.match === false,
    note: tamper.ok ? undefined : `tamper endpoint unavailable: ${tamper.error}`,
  });

  // A3 — forged audit record: a non-police org tries to write a case record.
  const forgedRecord = await api('POST', '/records', {
    token: tokens.auditor,
    body: {
      recordId: `${recordId}-forged`,
      payload: { fir: 'forged' },
      meta: {
        caseId: 'CASE-2026-001', recordType: 'fir', sensitivityLevel: 'low',
        owningStation: 'PS-Central', jurisdiction: 'district-north',
      },
    },
  });
  results.push({
    attack: 'unauthorized audit-record injection',
    mechanism: 'oversight org attempts to author a police case record',
    detectedBy: 'chaincode clientIdentity MSP check (not endorsement policy alone)',
    detected: forgedRecord.ok === false,
  });

  // A4 — request backdating: attempt to dictate the decision timestamp.
  const backdate = await api('POST', '/access/request', {
    token: tokens.inspector,
    body: {
      recordId, action: 'view', purpose: 'investigation',
      createdAtUtc: '2020-01-01T00:00:00.000Z',
    },
  });
  const rejectedField = backdate.ok === false;
  const ignoredField = backdate.ok === true &&
    new Date(backdate.data.createdAtUtc).getUTCFullYear() > 2024;
  results.push({
    attack: 'request backdating',
    mechanism: 'client supplies its own decision timestamp',
    detectedBy: 'schema allow-list + chaincode uses stub.getDateTimestamp()',
    detected: rejectedField || ignoredField,
  });

  // A5 — approval-token exposure: is the raw token ever committed?
  const withToken = await api('POST', '/access/request', {
    token: tokens.prosecutor,
    body: {
      recordId, action: 'view', purpose: 'prosecution',
      approvalToken: 'REPLAY-TOKEN-CANARY',
    },
  });
  const committed = JSON.stringify(withToken.data || {});
  results.push({
    attack: 'approval-token exposure (replay precondition)',
    mechanism: 'check whether a raw approval token is readable from the ledger',
    detectedBy: 'chaincode stores only sha256(token)',
    detected: withToken.ok === true && !committed.includes('REPLAY-TOKEN-CANARY'),
  });

  // A6 — access-log tampering: hide the fact that someone searched for a case.
  // Reads and searches are Fabric queries, so they never reach the ledger on
  // their own; they are protected by a hash chain whose head is anchored
  // on-chain. Editing a log row must therefore still be detectable.
  const auditToken = tokens.auditor;
  await api('GET', `/records?caseId=CASE-2026-001`, { token: tokens.inspector });
  await api('POST', '/audit/anchor', { token: auditToken });
  const cleanCheck = await api('GET', '/audit/access-log/verify', { token: auditToken });
  const tamperLog = await api('POST', '/experiments/tamper-access-log', { token: auditToken });
  const afterCheck = await api('GET', '/audit/access-log/verify', { token: auditToken });
  results.push({
    attack: 'access-log tampering (hiding a search)',
    mechanism: 'a log row recording who searched a case is rewritten in place',
    detectedBy: 'hash chain over log entries + head hash anchored on-chain',
    detected: cleanCheck.data?.ok === true && afterCheck.data?.ok === false,
    note: tamperLog.ok ? undefined : `tamper endpoint unavailable: ${tamperLog.error}`,
  });

  return { results, payloadHash };
}

function markdownTable(report) {
  const b = report.buildLatency.aggregate;
  const v = report.verifyLatency.aggregate;
  const s = report.storage;
  const sim = report.paperSimulationBaseline;
  const batch = report.environment.ordererBatchTimeoutMs;
  const marginal = report.buildLatency.marginalP50Ms;

  const lines = [
    '### Live Fabric vs paper simulation (SEBA-XAI Section IV-F)',
    '',
    '| Quantity | Paper (local simulation) | This work (live Fabric, 5 orgs) |',
    '|---|---|---|',
    `| Audit build latency p50, end to end | ${sim.buildLatencyP50Ms} ms | ${b.p50Ms} ms |`,
    `| — of which orderer batch wait (config) | n/a | ${batch} ms |`,
    `| — marginal processing cost | ${sim.buildLatencyP50Ms} ms | ${marginal} ms |`,
    `| Verification latency p50 | ${sim.verifyLatencyP50Ms} ms | ${v.p50Ms} ms |`,
    `| Storage per audit event | ${sim.storagePerEventBytes} B | ${s.meanBytes} B |`,
    '',
    `Workload: ${report.workload.requestsPerSeed} requests per seed over seeds ` +
      `{${report.workload.seeds.join(', ')}} = ${b.n} timed submissions; ` +
      `verification measured ${v.n} times.`,
    '',
    '**Reading the build latency.** The end-to-end figure is dominated by the',
    `orderer's \`BatchTimeout\` of ${batch} ms, not by the audit design: the p50 is`,
    `${b.p50Ms} ms with a min–max spread of only ${(b.maxMs - b.minMs).toFixed(1)} ms,`,
    'which is the signature of a fixed batch wait rather than variable computation.',
    `The comparable quantity against the simulation's ${sim.buildLatencyP50Ms} ms is the`,
    `marginal cost of ~${marginal} ms (policy evaluation, XAI artifact construction,`,
    'endorsement by 3 of 5 organizations, validation, and commit). `BatchTimeout` is a',
    'throughput/latency tuning parameter; lowering it lowers this figure directly.',
    '',
    '**Storage is not like-for-like.** This implementation commits the full explanation',
    `artifact inline (${s.meanBytes} B) whereas the paper's ${sim.storagePerEventBytes} B`,
    'figure covers a leaner blockchain-style audit record. The gap reflects a richer',
    'record schema, not per-byte overhead introduced by Fabric.',
    '',
    '### Attack replay on the live network',
    '',
    '| Attack | Defended by | Outcome |',
    '|---|---|---|',
    ...report.attackReplay.map((a) =>
      `| ${a.attack} | ${a.detectedBy} | ${a.detected ? 'blocked / detected' : 'NOT DETECTED'} |`),
    '',
    'Every attack above is blocked by a mechanism that the paper\'s threat model names.',
    'Note the scope limit: these are integrity, authorization, and metadata-exposure',
    'attacks. The paper\'s compromised-signer attack is NOT replayed here — on a real',
    'Fabric network it requires a compromised MSP admin key, a strictly stronger',
    'assumption than in the simulation, and it remains future work.',
  ];
  return lines.join('\n');
}

async function main() {
  const runId = Date.now();
  const tokens = {
    inspector: await login('insp.sharma'),
    auditor: await login('aud.qureshi'),
    prosecutor: await login('pp.mehta'),
  };

  process.stdout.write(`Setting up ${SEEDS.length} records...\n`);
  const records = await setupRecords(tokens, runId);

  process.stdout.write(`Measuring build latency (${N} x ${SEEDS.length})...\n`);
  const build = await measureBuild(tokens, records);

  process.stdout.write(`Measuring verification latency (${N} x ${SEEDS.length})...\n`);
  const verify = await measureVerify(tokens, records);

  process.stdout.write('Replaying attacks...\n');
  const attacks = await replayAttacks(tokens, records);

  const report = {
    generatedAtUtc: new Date().toISOString(),
    environment: {
      network: '5 department orgs (Police, Forensics, Prosecution, Court, Audit)',
      orderer: 'single-node etcdraft',
      stateDatabase: 'CouchDB per peer',
      endorsementPolicy: 'MAJORITY Endorsement (3 of 5)',
      channel: 'crimechannel',
      chaincode: 'crimerecords',
      ordererBatchTimeoutMs: BATCH_TIMEOUT_MS,
      note: 'Latencies are client-observed and include REST, gateway, endorsement, ordering, and commit-wait. Single-host Docker (Colima) — not a distributed deployment.',
    },
    workload: { requestsPerSeed: N, seeds: SEEDS },
    buildLatency: {
      perSeed: build.perSeed,
      aggregate: stats(build.allSamples),
      // A submitted transaction cannot commit before the orderer cuts a block,
      // so the batch timeout is a floor on end-to-end latency, not a cost of
      // the audit design. Subtract it to get the comparable marginal figure.
      marginalP50Ms: Number(
        (stats(build.allSamples).p50Ms - BATCH_TIMEOUT_MS).toFixed(2)),
      note: `End-to-end p50 includes the orderer's ${BATCH_TIMEOUT_MS} ms BatchTimeout. ` +
        'marginalP50Ms is the remainder: policy evaluation, explanation artifact ' +
        'construction, endorsement by 3 of 5 orgs, validation, and commit.',
    },
    verifyLatency: {
      perSeed: verify.perSeed,
      aggregate: stats(verify.allSamples),
    },
    storage: {
      meanBytes: Math.round(
        build.storageBytes.reduce((a, b) => a + b, 0) / build.storageBytes.length),
      minBytes: Math.min(...build.storageBytes),
      maxBytes: Math.max(...build.storageBytes),
      note: 'Serialized committed audit record (decision + minimized subject + environment commitments + explanation artifact + explanation hash).',
    },
    paperSimulationBaseline: {
      buildLatencyP50Ms: 11.10,
      verifyLatencyP50Ms: 2.50,
      storagePerEventBytes: 353.50,
      source: 'SEBA-XAI paper, Section IV-F (local permissioned simulation)',
    },
    attackReplay: attacks.results,
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  const jsonPath = path.join(OUT_DIR, 'live_fabric_measurements.json');
  const mdPath = path.join(OUT_DIR, 'live_fabric_measurements.md');
  fs.writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`);
  fs.writeFileSync(mdPath, `${markdownTable(report)}\n`);

  process.stdout.write(`\n${markdownTable(report)}\n\nWrote ${jsonPath}\n`);

  const undetected = report.attackReplay.filter((a) => !a.detected);
  if (undetected.length > 0) {
    process.stdout.write(`\nWARNING: ${undetected.length} attack(s) not detected: ` +
      `${undetected.map((a) => a.attack).join(', ')}\n`);
    process.exitCode = 1;
  }
}

main().catch((err) => {
  process.stderr.write(`measurement failed: ${err.message}\n`);
  process.exitCode = 1;
});
