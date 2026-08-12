'use strict';

/**
 * Minimal agency-controlled raw-content vault for the research prototype.
 *
 * This is deliberately a filesystem, not an application database. Fabric is
 * authoritative for the record metadata, reference, hash and access decision;
 * this module only holds the sensitive bytes that must not be replicated to
 * every channel peer. A production deployment would replace this adapter with
 * each agency's encrypted object/document store.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { VAULT_DIR } = require('../config');

const SAFE = /^[A-Za-z0-9._-]{1,128}$/;
const REFERENCE = /^vault:\/\/([a-z]+)\/([A-Za-z0-9._-]{1,128})$/;

function canonicalize(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return `{${keys.map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function hashPayload(payload) {
  return crypto.createHash('sha256').update(canonicalize(payload), 'utf8').digest('hex');
}

function location(org, recordId) {
  if (!SAFE.test(org) || !SAFE.test(recordId)) throw new Error('invalid vault identifier');
  return path.join(VAULT_DIR, org, `${recordId}.json`);
}

function save(org, recordId, payload) {
  const file = location(org, recordId);
  const contentHash = hashPayload(payload);
  const offChainReference = `vault://${org}/${recordId}`;
  if (fs.existsSync(file)) {
    const existing = read(offChainReference);
    if (existing.currentHash === contentHash) {
      return { contentHash, offChainReference, created: false };
    }
    throw new Error(`record '${recordId}' already exists in agency vault`);
  }
  const envelope = { recordId, owningAgency: org, contentHash, payload };

  fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 });
  const temporary = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(envelope), { encoding: 'utf8', mode: 0o600 });
  fs.renameSync(temporary, file);
  return { contentHash, offChainReference, created: true };
}

function read(offChainReference) {
  const match = REFERENCE.exec(offChainReference || '');
  if (!match) throw new Error('unsupported off-chain reference');
  const [, org, recordId] = match;
  const file = location(org, recordId);
  if (!fs.existsSync(file)) throw new Error(`raw content for '${recordId}' is unavailable`);
  const envelope = JSON.parse(fs.readFileSync(file, 'utf8'));
  return { ...envelope, currentHash: hashPayload(envelope.payload) };
}

/** Roll back only the exact newly-created file when its Fabric transaction fails. */
function rollback(offChainReference) {
  const match = REFERENCE.exec(offChainReference || '');
  if (!match) return;
  const file = location(match[1], match[2]);
  if (fs.existsSync(file)) fs.unlinkSync(file);
}

module.exports = { save, read, rollback, hashPayload, canonicalize };
