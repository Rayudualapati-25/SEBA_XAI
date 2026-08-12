'use strict';

const path = require('path');

const NETWORK_DIR = path.resolve(__dirname, '..', '..', 'network');
const VAULT_DIR = process.env.AGENCY_VAULT_DIR
  ? path.resolve(process.env.AGENCY_VAULT_DIR)
  : path.resolve(__dirname, '..', 'data', 'agency-vault');
// The Fabric CLI binaries ship with the workspace rather than the system.
// fabric-ca-client is used to register and enrol new department users, exactly
// as scripts/seed-identities.sh does, so web-created identities are
// byte-identical to seeded ones.
const FABRIC_BIN = path.resolve(NETWORK_DIR, '..', '..', 'fabric-samples', 'bin');

if (!process.env.JWT_SECRET) {
  // eslint-disable-next-line no-console
  console.warn('[config] JWT_SECRET not set — using a dev-only default. Do not deploy like this.');
}

// caPort/caName are what fabric-ca-client needs to register and enrol a new
// user into that department; they mirror network/compose/compose-ca.yaml.
const ORG_CONFIG = Object.freeze({
  police: {
    mspId: 'PoliceMSP',
    domain: 'police.example.com',
    peerEndpoint: 'localhost:7051',
    peerHostAlias: 'peer0.police.example.com',
    caPort: 7054,
    caName: 'ca-police',
  },
  forensics: {
    mspId: 'ForensicsMSP',
    domain: 'forensics.example.com',
    peerEndpoint: 'localhost:8051',
    peerHostAlias: 'peer0.forensics.example.com',
    caPort: 8054,
    caName: 'ca-forensics',
  },
  prosecution: {
    mspId: 'ProsecutionMSP',
    domain: 'prosecution.example.com',
    peerEndpoint: 'localhost:9051',
    peerHostAlias: 'peer0.prosecution.example.com',
    caPort: 9054,
    caName: 'ca-prosecution',
  },
  court: {
    mspId: 'CourtMSP',
    domain: 'court.example.com',
    peerEndpoint: 'localhost:10051',
    peerHostAlias: 'peer0.court.example.com',
    caPort: 10054,
    caName: 'ca-court',
  },
  audit: {
    mspId: 'AuditMSP',
    domain: 'audit.example.com',
    peerEndpoint: 'localhost:11051',
    peerHostAlias: 'peer0.audit.example.com',
    caPort: 11054,
    caName: 'ca-audit',
  },
});

module.exports = Object.freeze({
  PORT: Number(process.env.PORT || 3001),

  // Local LLM used only to reword decisions into plain language.
  // Change OLLAMA_MODEL to any model you have pulled (e.g. llama3.1:8b).
  OLLAMA_URL: process.env.OLLAMA_URL || 'http://localhost:11434',
  OLLAMA_MODEL: process.env.OLLAMA_MODEL || 'llama3.2:3b',
  OLLAMA_SEED: Number(process.env.OLLAMA_SEED || 42),
  OLLAMA_TIMEOUT_MS: Number(process.env.OLLAMA_TIMEOUT_MS || 45000),

  // Signing in has to read the account before it knows which department the
  // account belongs to, so that one lookup uses a fixed identity. The audit
  // organisation is the right one to hold it: oversight already reads across
  // all five departments, and UserContract.ReadUser is evaluate-only.
  AUTH_ORG: process.env.AUTH_ORG || 'audit',
  AUTH_USER: process.env.AUTH_USER || 'aud.qureshi',

  JWT_SECRET: process.env.JWT_SECRET || 'dev-only-secret-change-me',
  JWT_EXPIRY: '8h',
  CHANNEL: 'crimechannel',
  CHAINCODE: 'crimerecords',
  NETWORK_DIR,
  VAULT_DIR,
  FABRIC_BIN,
  ORG_CONFIG,
});
