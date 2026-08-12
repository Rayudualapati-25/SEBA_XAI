'use strict';

const { expect } = require('chai');
const chai = require('chai');
chai.use(require('chai-as-promised'));

const PolicyContract = require('../lib/policyContract');
const { buildMockContext, CALLERS } = require('./testHelpers');

const contract = new PolicyContract();
const HASH = 'a'.repeat(64);

describe('PolicyContract', () => {
  it('creates and explicitly activates a version with history fields', async () => {
    const ctx = buildMockContext(CALLERS.auditor);
    const draft = JSON.parse(await contract.CreatePolicyVersion(
      ctx, 'crime-policy-v1', HASH, 'deterministic policy v1'));
    expect(draft.status).to.equal('draft');
    expect(JSON.parse(await contract.GetActivePolicyVersion(ctx))).to.equal(null);
    const active = JSON.parse(await contract.ActivatePolicyVersion(ctx, 'crime-policy-v1'));
    expect(active.status).to.equal('active');
    expect(active.previousVersion).to.equal(null);
    expect(JSON.parse(await contract.GetActivePolicyVersion(ctx)).version)
      .to.equal('crime-policy-v1');
  });

  it('never silently reactivates or overwrites a version', async () => {
    const ctx = buildMockContext(CALLERS.auditor);
    await contract.CreatePolicyVersion(ctx, 'crime-policy-v1', HASH, 'v1');
    await expect(contract.CreatePolicyVersion(ctx, 'crime-policy-v1', HASH, 'changed'))
      .to.be.rejectedWith(/already exists/);
    await contract.ActivatePolicyVersion(ctx, 'crime-policy-v1');
    await expect(contract.ActivatePolicyVersion(ctx, 'crime-policy-v1'))
      .to.be.rejectedWith(/already active/);
  });

  it('supersedes the previous active version explicitly', async () => {
    const ctx = buildMockContext(CALLERS.auditor);
    await contract.CreatePolicyVersion(ctx, 'crime-policy-v1', HASH, 'v1');
    await contract.ActivatePolicyVersion(ctx, 'crime-policy-v1');
    await contract.CreatePolicyVersion(ctx, 'crime-policy-v2', 'b'.repeat(64), 'v2');
    const active = JSON.parse(await contract.ActivatePolicyVersion(ctx, 'crime-policy-v2'));
    expect(active.previousVersion).to.equal('crime-policy-v1');
    const versions = JSON.parse(await contract.QueryPolicyVersions(ctx));
    expect(versions.find((item) => item.version === 'crime-policy-v1').status)
      .to.equal('superseded');
  });

  it('requires an oversight/court policy administrator and valid fields', async () => {
    await expect(contract.CreatePolicyVersion(
      buildMockContext(CALLERS.inspector), 'crime-policy-v1', HASH, 'v1'
    )).to.be.rejectedWith(/requires membership/);
    const ctx = buildMockContext(CALLERS.auditor);
    await expect(contract.CreatePolicyVersion(ctx, 'bad version', HASH, 'x'))
      .to.be.rejectedWith(/invalid format/);
    await expect(contract.CreatePolicyVersion(ctx, 'v1', 'bad', 'x'))
      .to.be.rejectedWith(/sha256/);
    await expect(contract.ActivatePolicyVersion(ctx, 'missing'))
      .to.be.rejectedWith(/does not exist/);
  });
});
