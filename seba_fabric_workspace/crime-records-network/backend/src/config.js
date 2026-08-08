'use strict';

const path = require('path');

const NETWORK_DIR = path.resolve(__dirname, '..', '..', 'network');
const DATA_DIR = path.resolve(__dirname, '..', 'data');

if (!process.env.JWT_SECRET) {
  // eslint-disable-next-line no-console
  console.warn('[config] JWT_SECRET not set — using a dev-only default. Do not deploy like this.');
}

const ORG_CONFIG = Object.freeze({
  police: {
    mspId: 'PoliceMSP',
    domain: 'police.example.com',
    peerEndpoint: 'localhost:7051',
    peerHostAlias: 'peer0.police.example.com',
  },
  forensics: {
    mspId: 'ForensicsMSP',
    domain: 'forensics.example.com',
    peerEndpoint: 'localhost:8051',
    peerHostAlias: 'peer0.forensics.example.com',
  },
  prosecution: {
    mspId: 'ProsecutionMSP',
    domain: 'prosecution.example.com',
    peerEndpoint: 'localhost:9051',
    peerHostAlias: 'peer0.prosecution.example.com',
  },
  court: {
    mspId: 'CourtMSP',
    domain: 'court.example.com',
    peerEndpoint: 'localhost:10051',
    peerHostAlias: 'peer0.court.example.com',
  },
  audit: {
    mspId: 'AuditMSP',
    domain: 'audit.example.com',
    peerEndpoint: 'localhost:11051',
    peerHostAlias: 'peer0.audit.example.com',
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

  // Access log anchoring. Every ANCHOR_EVERY entries, the log's head hash is
  // committed to the blockchain. Anchoring is an oversight action, so it is
  // submitted as the audit organization.
  ANCHOR_EVERY: Number(process.env.ANCHOR_EVERY || 25),
  ANCHOR_ORG: process.env.ANCHOR_ORG || 'audit',
  ANCHOR_USER: process.env.ANCHOR_USER || 'aud.qureshi',


  JWT_SECRET: process.env.JWT_SECRET || 'dev-only-secret-change-me',
  JWT_EXPIRY: '8h',
  CHANNEL: 'crimechannel',
  CHAINCODE: 'crimerecords',
  NETWORK_DIR,
  DATA_DIR,
  DB_FILE: path.join(DATA_DIR, 'offchain.sqlite'),
  ORG_CONFIG,
});
