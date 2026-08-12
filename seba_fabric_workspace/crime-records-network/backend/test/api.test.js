'use strict';

/** Live-network integration tests for the eight documented policy scenarios. */

const { expect } = require('chai');

const BASE = process.env.API_BASE || 'http://localhost:3001/api';
const RUN = Date.now();
const RECORD_ID = `FIR-API-${RUN}`;
const CASE_ID = 'CASE-2026-001';

async function api(method, path, { token, body } = {}) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  return { status: response.status, json: await response.json() };
}

async function login(username) {
  const { json } = await api('POST', '/auth/login', { body: { username } });
  expect(json.success, `login ${username}: ${json.error}`).to.equal(true);
  return json.data.token;
}

describe('SEBA-XAI API (live Fabric network)', function () {
  this.timeout(90000);

  const tokens = {};
  let crossDistrictDecisionId;
  let inspectorDecisionId;

  before(async () => {
    const health = await api('GET', '/health');
    expect(health.json.data).to.equal('ok');
    for (const user of [
      'insp.sharma', 'io.krishnan', 'const.verma', 'insp.singh',
      'analyst.rao', 'dc.nair', 'pp.mehta', 'judge.rana',
      'aud.qureshi', 'insp.rathore',
    ]) tokens[user] = await login(user);
  });

  describe('Fabric identity and governance assets', () => {
    it('selects an enrolled Fabric identity without an application password', async () => {
      const me = await api('GET', '/auth/me', { token: tokens['insp.sharma'] });
      expect(me.json.data).to.include({ org: 'police', role: 'inspector' });
      const missing = await api('POST', '/auth/login', { body: { username: 'missing.user' } });
      expect(missing.status).to.equal(401);
    });

    it('reads Department and Case assets from Fabric', async () => {
      const departments = await api('GET', '/departments', { token: tokens['aud.qureshi'] });
      expect(departments.json.data.map((item) => item.departmentId))
        .to.include.members(['police', 'forensics', 'court', 'audit']);
      const caseAsset = await api('GET', `/cases/${CASE_ID}`, { token: tokens['insp.sharma'] });
      expect(caseAsset.json.data.assignedUsers).to.include('io.krishnan');
    });
  });

  describe('RecordMetadata plus agency-controlled raw content', () => {
    it('stores only reference/hash metadata on Fabric', async () => {
      const result = await api('POST', '/records', {
        token: tokens['insp.sharma'],
        body: {
          recordId: RECORD_ID,
          payload: { synthetic: true, summary: 'integration-test narrative', complainant: 'X' },
          meta: {
            caseId: CASE_ID, recordType: 'fir', sensitivityLevel: 'medium',
            juvenileFlag: false, witnessFlag: false, victimProtectionFlag: false,
            owningStation: 'PS-Central', jurisdiction: 'district-north',
          },
        },
      });
      expect(result.status, JSON.stringify(result.json)).to.equal(201);
      expect(result.json.data.contentHash).to.match(/^[0-9a-f]{64}$/);
      expect(result.json.data.offChainReference).to.equal(`vault://police/${RECORD_ID}`);
      expect(JSON.stringify(result.json.data)).to.not.contain('integration-test narrative');
    });

    it('enforces the filing identity in chaincode/API', async () => {
      const result = await api('POST', '/records', {
        token: tokens['analyst.rao'],
        body: {
          recordId: `${RECORD_ID}-forbidden`, payload: { synthetic: true },
          meta: {
            caseId: CASE_ID, recordType: 'fir', sensitivityLevel: 'low',
            owningStation: 'PS-Central', jurisdiction: 'district-north',
          },
        },
      });
      expect(result.status).to.equal(403);
    });
  });

  describe('contextual policy scenarios', () => {
    it('1. allows an assigned investigating officer for investigation', async () => {
      const result = await api('POST', '/access/request', {
        token: tokens['io.krishnan'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(result.json.data.decision).to.equal('allow');
      expect(result.json.data.explanation.reasonCode).to.equal('POLICY_SATISFIED');
      inspectorDecisionId = result.json.data.decisionId;
    });

    it('2. denies a same-station constable without assignment', async () => {
      const result = await api('POST', '/access/request', {
        token: tokens['const.verma'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(result.json.data.decision).to.equal('deny');
      expect(result.json.data.explanation.reasonCode).to.equal('NOT_ASSIGNED');
    });

    it('3. exposes evidence metadata but denies unnecessary victim raw content', async () => {
      const metadata = await api('GET', '/records/REC-EVIDENCE-001', {
        token: tokens['analyst.rao'],
      });
      expect(metadata.status).to.equal(200);
      expect(metadata.json.data.recordType).to.equal('evidence');
      const result = await api('POST', '/access/request', {
        token: tokens['analyst.rao'],
        body: {
          recordId: 'REC-EVIDENCE-001', action: 'view', purpose: 'forensic-analysis',
        },
      });
      expect(result.json.data.decision).to.equal('deny');
      expect(result.json.data.explanation.reasonCode).to.equal('VICTIM_DATA_NOT_NECESSARY');
    });

    it('4. escalates a legitimate cross-district request', async () => {
      const result = await api('POST', '/access/request', {
        token: tokens['insp.singh'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(result.json.data.decision).to.equal('escalate');
      expect(result.json.data.explanation.reasonCode).to.equal('CROSS_JURISDICTION');
      crossDistrictDecisionId = result.json.data.decisionId;
    });

    it('5. denies juvenile-protected raw content to a high-rank inspector', async () => {
      const result = await api('POST', '/access/request', {
        token: tokens['insp.sharma'],
        body: {
          recordId: 'REC-JUVENILE-001', action: 'view', purpose: 'investigation',
        },
      });
      expect(result.json.data.decision).to.equal('deny');
      expect(result.json.data.explanation.reasonCode).to.equal('JUVENILE_PROTECTED');
    });

    it('6. links a supervisor approval and then permits release', async () => {
      const approved = await api(
        'POST', `/access/${RECORD_ID}/${crossDistrictDecisionId}/approve`, {
          token: tokens['judge.rana'], body: { note: 'legitimate supervised request' },
        }
      );
      expect(approved.json.data.status).to.equal('approved-after-escalation');
      const released = await api('GET', `/records/${RECORD_ID}/payload`, {
        token: tokens['insp.singh'],
      });
      expect(released.status, JSON.stringify(released.json)).to.equal(200);
      expect(released.json.data.payload.summary).to.equal('integration-test narrative');
    });

    it('7. denies a revoked certificate attribute', async () => {
      const result = await api('POST', '/access/request', {
        token: tokens['insp.rathore'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'investigation' },
      });
      expect(result.json.data.decision).to.equal('deny');
      expect(result.json.data.explanation.reasonCode).to.equal('CRED_NOT_ACTIVE');
    });

    it('8. reconstructs evidence for an auditor without releasing raw content', async () => {
      const trail = await api('GET', `/audit/trail/${RECORD_ID}`, {
        token: tokens['aud.qureshi'],
      });
      expect(trail.json.data.accessRequests.length).to.be.at.least(4);
      expect(trail.json.data.accessDecisions.length).to.be.at.least(4);
      expect(trail.json.data.approvals.some(
        (approval) => approval.decisionId === crossDistrictDecisionId
      )).to.equal(true);
      expect(JSON.stringify(trail.json.data)).to.not.contain('integration-test narrative');

      const request = await api('POST', '/access/request', {
        token: tokens['aud.qureshi'],
        body: { recordId: RECORD_ID, action: 'view', purpose: 'audit-review' },
      });
      expect(request.json.data.explanation.reasonCode).to.equal('AUDIT_METADATA_ONLY');
      const raw = await api('GET', `/records/${RECORD_ID}/payload`, {
        token: tokens['aud.qureshi'],
      });
      expect(raw.status).to.equal(422);
    });
  });

  describe('integrity, evidence custody, and audit events', () => {
    it('verifies agency-vault content against the Fabric commitment', async () => {
      const result = await api('POST', `/audit/verify-payload/${RECORD_ID}`, {
        token: tokens['aud.qureshi'],
      });
      expect(result.json.data.match).to.equal(true);
      expect(result.json.data.storage).to.equal('agency-controlled-off-chain-vault');
    });

    it('commits evidence metadata and a custody transfer', async () => {
      const evidenceId = `EV-${RUN}`;
      const attached = await api('POST', `/records/${RECORD_ID}/evidence`, {
        token: tokens['analyst.rao'],
        body: {
          evidenceId, artifact: 'synthetic evidence bytes', source: 'lab intake',
          detail: 'Synthetic PDC detail',
        },
      });
      expect(attached.status, JSON.stringify(attached.json)).to.equal(201);
      expect(attached.json.data.offChainReference).to.match(/^vault:\/\/forensics\//);
      const transfer = await api(
        'POST', `/records/${RECORD_ID}/evidence/${evidenceId}/custody`, {
          token: tokens['analyst.rao'],
          body: { toMsp: 'CourtMSP', reason: 'filed as synthetic exhibit' },
        }
      );
      expect(transfer.json.data.toMsp).to.equal('CourtMSP');
      const timeline = await api(
        'GET', `/records/${RECORD_ID}/evidence/${evidenceId}/custody`, {
          token: tokens['judge.rana'],
        }
      );
      expect(timeline.json.data).to.have.length(1);
    });

    it('returns direct-ledger application access events', async () => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const result = await api('GET', '/audit/access-log?limit=100', {
        token: tokens['aud.qureshi'],
      });
      expect(result.json.data.storage).to.equal('fabric-ledger');
      expect(result.json.data.entries.length).to.be.greaterThan(0);
    });

    it('verifies a genuine explanation and rejects a forged artifact', async () => {
      const trail = await api('GET', `/audit/trail/${RECORD_ID}`, {
        token: tokens['aud.qureshi'],
      });
      const decision = trail.json.data.accessDecisions
        .find((item) => item.decisionId === inspectorDecisionId);
      const genuine = await api(
        'POST', `/audit/verify-explanation/${RECORD_ID}/${decision.decisionId}`, {
          token: tokens['aud.qureshi'], body: { artifact: decision.explanation },
        }
      );
      expect(genuine.json.data.match).to.equal(true);
      const forged = await api(
        'POST', `/audit/verify-explanation/${RECORD_ID}/${decision.decisionId}`, {
          token: tokens['aud.qureshi'],
          body: { artifact: { ...decision.explanation, reasonCode: 'FORGED' } },
        }
      );
      expect(forged.json.data.match).to.equal(false);
    });
  });
});
