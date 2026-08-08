"use strict";

const chai = require("chai");
const sinonChai = require("sinon-chai");
const expect = chai.expect;
chai.use(sinonChai);

const SebaAuditContract = require("../lib/sebaAuditContract.js");
const { buildValidEvent } = require("./fixtures/validEvent.js");

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

const HASH_FIELDS = [
  "requestIdHash",
  "decisionHash",
  "explanationHash",
  "recordCommitment",
  "auditAnchorHash",
  "approvalReferenceHash",
  "attributeSetHash",
];

describe("SebaAuditContract private helpers", () => {
  let contract;

  beforeEach(() => {
    contract = new SebaAuditContract();
  });

  describe("_eventKey", () => {
    it("prefixes the requestIdHash with audit:", () => {
      expect(contract._eventKey("abc123")).to.equal("audit:abc123");
    });

    it("produces distinct keys for distinct hashes", () => {
      expect(contract._eventKey("hash-a")).to.not.equal(contract._eventKey("hash-b"));
    });
  });

  describe("_parseAndValidateEvent", () => {
    it("throws when the payload is not valid JSON", () => {
      expect(() => contract._parseAndValidateEvent("{not-json")).to.throw(
        /eventJson is not valid JSON/,
      );
    });

    it("returns the parsed event when every rule is satisfied", () => {
      const event = buildValidEvent();
      const parsed = contract._parseAndValidateEvent(JSON.stringify(event));
      expect(parsed).to.eql(event);
    });

    REQUIRED_FIELDS.forEach((field) => {
      it(`rejects a payload missing required field: ${field}`, () => {
        const event = buildValidEvent();
        delete event[field];
        expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
          `Missing required field: ${field}`,
        );
      });

      it(`rejects a payload with a blank value for required field: ${field}`, () => {
        const event = buildValidEvent({ [field]: "   " });
        expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
          `Missing required field: ${field}`,
        );
      });
    });

    FORBIDDEN_FIELDS.forEach((field) => {
      it(`rejects a payload carrying forbidden raw/PII field: ${field}`, () => {
        const event = buildValidEvent({ [field]: "raw-value" });
        expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
          `Forbidden raw/sensitive field present: ${field}`,
        );
      });
    });

    it("rejects a decision outside allow/deny/escalate", () => {
      const event = buildValidEvent({ decision: "maybe" });
      expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
        "Unsupported decision=maybe",
      );
    });

    ["allow", "deny", "escalate"].forEach((decision) => {
      it(`accepts decision=${decision}`, () => {
        const event = buildValidEvent({ decision });
        const parsed = contract._parseAndValidateEvent(JSON.stringify(event));
        expect(parsed.decision).to.equal(decision);
      });
    });

    HASH_FIELDS.forEach((field) => {
      it(`rejects ${field} that is not a 64-char lowercase hex sha-256`, () => {
        const event = buildValidEvent({ [field]: "not-a-hash" });
        expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
          `Field ${field} must be a 64-character lowercase SHA-256 hex string`,
        );
      });

      it(`rejects ${field} that is uppercase hex (case-sensitive check)`, () => {
        const event = buildValidEvent({ [field]: "A".repeat(64) });
        expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
          `Field ${field} must be a 64-character lowercase SHA-256 hex string`,
        );
      });

      it(`rejects ${field} that is one character short of 64`, () => {
        const event = buildValidEvent({ [field]: "a".repeat(63) });
        expect(() => contract._parseAndValidateEvent(JSON.stringify(event))).to.throw(
          `Field ${field} must be a 64-character lowercase SHA-256 hex string`,
        );
      });
    });
  });
});
