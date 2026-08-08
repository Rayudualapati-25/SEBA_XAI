"use strict";

const crypto = require("crypto");
const { Contract } = require("fabric-contract-api");

const REQUIRED_FIELDS = [
  "requestIdHash",
  "policyVersion",
  "decision",
  "primaryReasonCode",
  "decisionHash",
  "explanationHash",
  "recordCommitment",
  "auditAnchorHash",
  "approvalReferenceHash",
  "attributeSetHash",
  "sourcePrototypeRun",
  "createdAtUtc",
];

const FORBIDDEN_FIELDS = [
  "request_id",
  "requester_officer_id",
  "requester_name",
  "target_record_id",
  "target_case_id",
  "xai_explanation",
  "raw_record",
  "record_payload",
  "victim_name",
  "witness_name",
  "juvenile_name",
];

function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map((item) => canonicalize(item));
  }
  if (value && typeof value === "object") {
    return Object.keys(value)
      .sort()
      .reduce((acc, key) => {
        acc[key] = canonicalize(value[key]);
        return acc;
      }, {});
  }
  return value;
}

function canonicalString(value) {
  return JSON.stringify(canonicalize(value));
}

function sha256Hex(value) {
  return crypto.createHash("sha256").update(canonicalString(value), "utf8").digest("hex");
}

class SebaAuditContract extends Contract {
  async InitLedger(ctx) {
    const metadata = {
      objectType: "sebaAuditLedgerMetadata",
      schemaVersion: "SEBA-FABRIC-AUDIT-EVENT-V1",
      rawRecordsOnChain: false,
      purpose: "Commitment-only audit evidence for SEBA-XAI access decisions",
      initializedTxId: ctx.stub.getTxID(),
    };
    await ctx.stub.putState("metadata:seba-audit", Buffer.from(canonicalString(metadata)));
    return JSON.stringify(metadata);
  }

  async AuditEventExists(ctx, requestIdHash) {
    const buffer = await ctx.stub.getState(this._eventKey(requestIdHash));
    return buffer && buffer.length > 0;
  }

  async RecordAccessDecision(ctx, eventJson) {
    const event = this._parseAndValidateEvent(eventJson);
    const key = this._eventKey(event.requestIdHash);

    const exists = await this.AuditEventExists(ctx, event.requestIdHash);
    if (exists) {
      throw new Error(`Audit event already exists for requestIdHash=${event.requestIdHash}`);
    }

    const txTimestamp = ctx.stub.getTxTimestamp();
    const fabricTimestamp = new Date(
      Number(txTimestamp.seconds.low) * 1000 + Math.floor(txTimestamp.nanos / 1000000),
    ).toISOString();

    const eventCommitmentHash = sha256Hex(event);
    const ledgerRecord = {
      objectType: "sebaAuditEvent",
      schemaVersion: "SEBA-FABRIC-AUDIT-EVENT-V1",
      ...event,
      eventCommitmentHash,
      fabricTxId: ctx.stub.getTxID(),
      fabricTimestamp,
      rawRecordsOnChain: false,
    };

    await ctx.stub.putState(key, Buffer.from(canonicalString(ledgerRecord)));

    const policyIndexKey = ctx.stub.createCompositeKey("policy~request", [
      event.policyVersion,
      event.requestIdHash,
    ]);
    await ctx.stub.putState(policyIndexKey, Buffer.from("\u0000"));

    const decisionIndexKey = ctx.stub.createCompositeKey("decision~request", [
      event.decision,
      event.requestIdHash,
    ]);
    await ctx.stub.putState(decisionIndexKey, Buffer.from("\u0000"));

    ctx.stub.setEvent("SebaAuditEventRecorded", Buffer.from(canonicalString(ledgerRecord)));
    return JSON.stringify(ledgerRecord);
  }

  async ReadAccessDecision(ctx, requestIdHash) {
    const buffer = await ctx.stub.getState(this._eventKey(requestIdHash));
    if (!buffer || buffer.length === 0) {
      throw new Error(`No audit event found for requestIdHash=${requestIdHash}`);
    }
    return buffer.toString("utf8");
  }

  async VerifyAuditAnchor(ctx, requestIdHash, expectedAuditAnchorHash) {
    const raw = await this.ReadAccessDecision(ctx, requestIdHash);
    const record = JSON.parse(raw);
    return JSON.stringify({
      requestIdHash,
      expectedAuditAnchorHash,
      storedAuditAnchorHash: record.auditAnchorHash,
      match: record.auditAnchorHash === expectedAuditAnchorHash,
    });
  }

  async GetHistoryForRequest(ctx, requestIdHash) {
    const iterator = await ctx.stub.getHistoryForKey(this._eventKey(requestIdHash));
    const results = [];
    try {
      while (true) {
        const response = await iterator.next();
        if (response.value) {
          results.push({
            txId: response.value.txId,
            timestamp: response.value.timestamp,
            isDelete: response.value.isDelete,
            value: response.value.value.toString("utf8"),
          });
        }
        if (response.done) {
          break;
        }
      }
    } finally {
      await iterator.close();
    }
    return JSON.stringify(results);
  }

  async QueryByDecision(ctx, decision) {
    if (!["allow", "deny", "escalate"].includes(decision)) {
      throw new Error(`Unsupported decision=${decision}`);
    }
    const iterator = await ctx.stub.getStateByPartialCompositeKey("decision~request", [decision]);
    const requestHashes = [];
    try {
      while (true) {
        const response = await iterator.next();
        if (response.value) {
          const parts = ctx.stub.splitCompositeKey(response.value.key);
          requestHashes.push(parts.attributes[1]);
        }
        if (response.done) {
          break;
        }
      }
    } finally {
      await iterator.close();
    }
    return JSON.stringify(requestHashes);
  }

  _parseAndValidateEvent(eventJson) {
    let event;
    try {
      event = JSON.parse(eventJson);
    } catch (error) {
      throw new Error(`eventJson is not valid JSON: ${error.message}`);
    }

    for (const field of REQUIRED_FIELDS) {
      if (!(field in event) || String(event[field]).trim() === "") {
        throw new Error(`Missing required field: ${field}`);
      }
    }

    for (const field of FORBIDDEN_FIELDS) {
      if (field in event) {
        throw new Error(`Forbidden raw/sensitive field present: ${field}`);
      }
    }

    if (!["allow", "deny", "escalate"].includes(event.decision)) {
      throw new Error(`Unsupported decision=${event.decision}`);
    }

    const hashFields = [
      "requestIdHash",
      "decisionHash",
      "explanationHash",
      "recordCommitment",
      "auditAnchorHash",
      "approvalReferenceHash",
      "attributeSetHash",
    ];
    for (const field of hashFields) {
      if (!/^[a-f0-9]{64}$/.test(event[field])) {
        throw new Error(`Field ${field} must be a 64-character lowercase SHA-256 hex string`);
      }
    }

    return event;
  }

  _eventKey(requestIdHash) {
    return `audit:${requestIdHash}`;
  }
}

module.exports = SebaAuditContract;
