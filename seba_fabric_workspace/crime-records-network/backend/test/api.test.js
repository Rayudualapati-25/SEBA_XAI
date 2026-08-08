'use strict';

/**
 * Integration tests against a RUNNING backend + live Fabric network.
 * Start the network (../bootstrap.sh + deployCC + seed-identities) and the
 * server (npm start) first.
 */

const { expect } = require('chai');
const crypto = require('crypto');

const BASE = process.env.API_BASE || 'http://localhost:3001/api';
const RUN = Date.now();
const RECORD_ID = `FIR-API-${RUN}`;
const CASE_ID = 'CASE-2026-001';

async function api(method, path, { token, body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  return { status: res.status, json: await res.json() };
}

async function login(username, password = 'demo123') {
  const { json } = await api('POST', '/auth/login', { body: { username, password } });
  expect(json.success, `login ${username}: ${json.error}`).to.equal(true);
  return json.data.token;
}

describe('Crime Records API (live network)', function () {
  this.timeout(60000);

  const tokens = {};
  let escalationId;

  before(async () => {
    const { json } = await api('GET', '/health');
    expect(json.data).to.equal('ok');
    for (const u of ['insp.sharma', 'const.verma', 'analyst.rao', 'dc.nair',
      'pp.mehta', 'judge.rana', 'aud.qureshi', 'insp.rathore']) {
      tokens[u] = await login(u);
    }
  });

  describe('auth', () => {
    it('rejects a wrong password and a missing token', async () => {
      const bad = await api('POST', '/auth/login',
        { body: { username: 'insp.sharma', password: 'wrong' } });
      expect(bad.status).to.equal(401);
      const noToken = await api('GET', '/records/anything');
      expect(noToken.status).to.equal(401);
    });

    it('returns the caller profile with org and role', async () => {
      const { json } = await api('GET', '/auth/me', { token: tokens['insp.sharma'] });
      expect(json.data.org).to.equal('police');
      expect(json.data.role).to.equal('inspector');
    });
  });

  describe('record filing', () => {
    it('files a record: payload off-chain, hash on-chain', async () => {
      const { status, json } = await api('POST', '/records', {
        token: tokens['insp.sharma'],
        body: {
          recordId: RECORD_ID,
          payload: { fir: RECORD_ID, summary: 'synthetic burglary', complainant: 'X' },
          meta: {
            caseId: CASE_ID, recordType: 'fir', sensitivityLevel: 'medium',
            juvenileFlag: false, witnessFlag: false,
            owningStation: 'PS-Central', jurisdiction: 'district-north',
          },
        },
      });
      expect(status, JSON.stringify(json)).to.equal(201);
      expect(json.data.recordId).to.equal(RECORD_ID);
      expect(json.data.payloadHash).to.match(/^[0-9a-f]{64}$/);
      // The ledger must not carry the payload text.
      expect(JSON.stringify(json.data)).to.not.contain('synthetic burglary');
    });

    it('blocks a forensics analyst from filing (role gate)', async () => {
      const { status } = await api('POST', '/records', {
        token: tokens['analyst.rao'],
        body: {
          recordId: `${RECORD_ID}-x`,
          payload: { x: 1 },
          meta: {
            caseId: CASE_ID, recordType: 'fir', sensitivityLevel: 'low',
            owningStation: 'PS-Central', jurisdiction: 'district-north',
          },
        },
      });
      expect(status).to.equal(403);
    });

    it('rejects an invalid record type at the API boundary', async () => {
      const { status, json } = await api('POST', '/records', {
        token: tokens['insp.sharma'],
        body: {
          recordId: `${RECORD_ID}-bad`,
          payload: { x: 1 },
          meta: {
            caseId: CASE_ID, recordType: 'gossip', sensitivityLevel: 'low',
            owningStation: 'PS-Central', jurisdiction: 'district-north',
          },
        },
      });
      expect(status).to.equal(400);
      expect(json.success).to.equal(false);
    });
  });

  describe('evidence', () => {
    it('lets forensics attach an evidence hash with private detail', async () => {
      const { status, json } = await api('POST', `/records/${RECORD_ID}/evidence`, {
        token: tokens['analyst.rao'],
        body: {
          evidenceId: 'EV-API-1',
          artifact: 'dna-profile-blob',
          detail: 'DNA matched sample S-77',
        },
      });
      expect(status, JSON.stringify(json)).to.equal(201);
      const expected = crypto.createHash('sha256').update('dna-profile-blob').digest('hex');
      expect(json.data.evidenceHash).to.equal(expected);
      expect(JSON.stringify(json.data)).to.not.contain('S-77');
    });

    it('releases private detail to a collection member (forensics)', async () => {
      const { status, json } = await api('GET',
        `/records/${RECORD_ID}/evidence/EV-API-1/detail`, { token: tokens['analyst.rao'] });
      expect(status, JSON.stringify(json)).to.equal(200);
      expect(json.data.detail).to.equal('DNA matched sample S-77');
    });

    it('withholds private detail from a non-member org (audit)', async () => {
      const { status, json } = await api('GET',
        `/records/${RECORD_ID}/evidence/EV-API-1/detail`, { token: tokens['aud.qureshi'] });
      expect(status).to.equal(422);
      expect(json.error).to.contain('requires membership in');
    });
  });

  describe('access decisions with explanations', () => {
    it('grants an assigned inspector', async () => {
      const { json } = await api('POST', '/access/request', {
        token: tokens['insp.sharma'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(json.data.decision).to.equal('allow');
      expect(json.data.explanation.reasonCode).to.equal('POLICY_SATISFIED');
      expect(json.data.explanationHash).to.match(/^[0-9a-f]{64}$/);
    });

    it('denies defense counsel with an RBAC explanation', async () => {
      const { json } = await api('POST', '/access/request', {
        token: tokens['dc.nair'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'defense-preparation' },
      });
      expect(json.data.decision).to.equal('deny');
      expect(json.data.explanation.reasonCode).to.equal('RBAC_NO_PERMISSION');
    });

    it('denies a revoked credential', async () => {
      const { json } = await api('POST', '/access/request', {
        token: tokens['insp.rathore'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(json.data.decision).to.equal('deny');
      expect(json.data.explanation.reasonCode).to.equal('CRED_NOT_ACTIVE');
    });

    it('escalates a constable and records a counterfactual', async () => {
      const { json } = await api('POST', '/access/request', {
        token: tokens['const.verma'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(json.data.decision).to.equal('escalate');
      expect(json.data.explanation.reasonCode).to.equal('INSUFFICIENT_CLEARANCE');
      expect(json.data.explanation.counterfactual).to.be.a('string');
      escalationId = json.data.decisionId;
    });

    it('never stores the raw approval token', async () => {
      const { json } = await api('POST', '/access/request', {
        token: tokens['pp.mehta'],
        body: {
          recordId: RECORD_ID, action: 'view', purpose: 'prosecution',
          approvalToken: 'RAW-SECRET-99',
        },
      });
      expect(json.data.environment.approvalTokenHash).to.match(/^[0-9a-f]{64}$/);
      expect(JSON.stringify(json.data)).to.not.contain('RAW-SECRET-99');
    });
  });

  describe('escalation workflow', () => {
    it('shows the pending escalation to a judge, hides the queue from others', async () => {
      const { json } = await api('GET', '/access/pending', { token: tokens['judge.rana'] });
      expect(json.data.some((d) => d.decisionId === escalationId)).to.equal(true);
      const forbidden = await api('GET', '/access/pending', { token: tokens['const.verma'] });
      expect(forbidden.status).to.equal(403);
    });

    it('lets the judge approve it', async () => {
      const { json } = await api('POST', `/access/${RECORD_ID}/${escalationId}/approve`, {
        token: tokens['judge.rana'],
        body: { note: 'reviewed and approved' },
      });
      expect(json.data.status).to.equal('approved-after-escalation');
      expect(json.data.resolution.byRole).to.equal('judge');
    });
  });

  describe('payload release is gated by the ledger', () => {
    it('releases the payload to a granted requester', async () => {
      const { status, json } = await api('GET', `/records/${RECORD_ID}/payload`,
        { token: tokens['insp.sharma'] });
      expect(status, JSON.stringify(json)).to.equal(200);
      expect(json.data.payload.summary).to.equal('synthetic burglary');
    });

    it('withholds it from a denied requester', async () => {
      const { status, json } = await api('GET', `/records/${RECORD_ID}/payload`,
        { token: tokens['dc.nair'] });
      expect(status).to.equal(403);
      expect(json.error).to.contain('no granted access decision');
    });
  });

  describe('audit', () => {
    it('reconstructs the trail for an auditor and blocks non-reviewers', async () => {
      const { json } = await api('GET', `/audit/trail/${RECORD_ID}`,
        { token: tokens['aud.qureshi'] });
      expect(json.data.accessDecisions.length).to.be.at.least(4);
      expect(json.data.record.recordId).to.equal(RECORD_ID);
      const forbidden = await api('GET', `/audit/trail/${RECORD_ID}`,
        { token: tokens['analyst.rao'] });
      expect(forbidden.status).to.equal(403);
    });

    it('confirms payload integrity while untampered', async () => {
      const { json } = await api('POST', `/audit/verify-payload/${RECORD_ID}`,
        { token: tokens['aud.qureshi'] });
      expect(json.data.match).to.equal(true);
    });

    it('detects a forged explanation artifact', async () => {
      const trail = await api('GET', `/audit/trail/${RECORD_ID}`,
        { token: tokens['aud.qureshi'] });
      const decision = trail.json.data.accessDecisions[0];

      const genuine = await api('POST',
        `/audit/verify-explanation/${RECORD_ID}/${decision.decisionId}`,
        { token: tokens['aud.qureshi'], body: { artifact: decision.explanation } });
      expect(genuine.json.data.match).to.equal(true);

      const forged = await api('POST',
        `/audit/verify-explanation/${RECORD_ID}/${decision.decisionId}`,
        {
          token: tokens['aud.qureshi'],
          body: { artifact: { ...decision.explanation, reasonCode: 'FORGED' } },
        });
      expect(forged.json.data.match).to.equal(false);
    });
  });
});
