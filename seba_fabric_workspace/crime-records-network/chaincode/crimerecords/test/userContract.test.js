'use strict';

const { expect } = require('chai');
const chai = require('chai');
chai.use(require('chai-as-promised'));

const UserContract = require('../lib/userContract');
const { buildMockContext, cloneInto, CALLERS } = require('./testHelpers');

const contract = new UserContract();

const ADMIN = {
  mspId: 'PoliceMSP',
  attrs: {
    role: 'sho', rank: '4', station: 'PS-Central', jurisdiction: 'district-north',
    clearance: 'high', credentialStatus: 'active',
  },
};

const PROFILE = Object.freeze({
  displayName: 'Const. R. Verma',
  org: 'police',
  role: 'constable',
  fabricUser: 'const.verma',
  departmentId: 'police',
  rank: '1',
  station: 'PS-Central',
  jurisdiction: 'district-north',
  clearance: 'low',
  caseAssignments: [],
  credentialStatus: 'active',
});

const create = (ctx, id = 'const.verma', profile = PROFILE) =>
  contract.CreateUser(ctx, id, JSON.stringify(profile));

function asUser(state, overrides = {}) {
  const ctx = buildMockContext({
    mspId: 'PoliceMSP',
    identityId: 'const.verma',
    attrs: {
      role: 'constable', rank: '1', station: 'PS-Central',
      jurisdiction: 'district-north', clearance: 'low', credentialStatus: 'active',
    },
    ...overrides,
  });
  cloneInto(state, ctx);
  return ctx;
}

describe('UserContract', () => {
  it('creates an identity-backed authorization profile without secrets', async () => {
    const ctx = buildMockContext(ADMIN);
    const user = JSON.parse(await create(ctx));
    expect(user.userId).to.equal('const.verma');
    expect(user.departmentId).to.equal('police');
    expect(user.clearance).to.equal('low');
    expect(JSON.stringify(user)).to.not.match(/password|bcrypt/i);
    expect(ctx._events[0].name).to.equal('UserRegistered');
  });

  it('requires the department administrator and matching department mapping', async () => {
    await expect(create(buildMockContext(CALLERS.inspector)))
      .to.be.rejectedWith(/requires role in \[sho\]/);
    const ctx = buildMockContext(ADMIN);
    await expect(create(ctx, 'bad.user', { ...PROFILE, departmentId: 'court' }))
      .to.be.rejectedWith(/departmentId must match org/);
  });

  it('rejects duplicates, malformed JSON and unknown fields', async () => {
    const ctx = buildMockContext(ADMIN);
    await create(ctx);
    await expect(create(ctx)).to.be.rejectedWith(/already exists/);
    await expect(contract.CreateUser(ctx, 'x.user', 'not json')).to.be.rejectedWith(/valid JSON/);
    await expect(create(buildMockContext(ADMIN), 'x.user', { ...PROFILE, passwordHash: 'secret' }))
      .to.be.rejectedWith(/unknown fields.*passwordHash/);
  });

  it('reads, lists and reports existence', async () => {
    const ctx = buildMockContext(ADMIN);
    expect(await contract.UserExists(ctx, 'const.verma')).to.equal(false);
    await create(ctx);
    expect(await contract.UserExists(ctx, 'const.verma')).to.equal(true);
    expect(JSON.parse(await contract.ReadUser(ctx, 'const.verma')).displayName)
      .to.equal('Const. R. Verma');
    expect(JSON.parse(await contract.QueryAllUsers(ctx))).to.have.length(1);
    await expect(contract.ReadUser(ctx, 'missing')).to.be.rejectedWith(/does not exist/);
  });

  it('authenticates only the matching certificate, MSP, role and profile attributes', async () => {
    const state = buildMockContext(ADMIN);
    await create(state);
    const caller = asUser(state);
    const user = JSON.parse(await contract.AuthenticateCurrentUser(caller, 'const.verma'));
    expect(user.fabricUser).to.equal('const.verma');

    await expect(contract.AuthenticateCurrentUser(
      asUser(state, { identityId: 'other.user' }), 'const.verma'
    )).to.be.rejectedWith(/certificate does not belong/);
    await expect(contract.AuthenticateCurrentUser(
      asUser(state, { attrs: { ...CALLERS.constable.attrs, role: 'inspector' } }), 'const.verma'
    )).to.be.rejectedWith(/certificate role/);
  });

  it('keeps status changes and history on the ledger', async () => {
    const ctx = buildMockContext(ADMIN);
    await create(ctx);
    const updated = JSON.parse(await contract.SetUserStatus(ctx, 'const.verma', 'suspended'));
    expect(updated.credentialStatus).to.equal('suspended');
    const history = JSON.parse(await contract.GetUserHistory(ctx, 'const.verma'));
    expect(history.map((entry) => entry.value.credentialStatus))
      .to.deep.equal(['active', 'suspended']);
    const caller = asUser(ctx);
    await expect(contract.AuthenticateCurrentUser(caller, 'const.verma'))
      .to.be.rejectedWith(/account is suspended/);
  });

  it('rejects invalid status and non-admin status changes', async () => {
    const state = buildMockContext(ADMIN);
    await create(state);
    await expect(contract.SetUserStatus(state, 'const.verma', 'deleted'))
      .to.be.rejectedWith(/must be one of/);
    const caller = asUser(state);
    await expect(contract.SetUserStatus(caller, 'const.verma', 'revoked'))
      .to.be.rejectedWith(/requires role/);
  });
});
