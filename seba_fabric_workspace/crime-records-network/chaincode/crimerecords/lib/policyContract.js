'use strict';

/** Versioned activation records for deterministic chaincode policy. */

const { Contract } = require('fabric-contract-api');
const { MSP, getCaller, requireMsp, requireRole } = require('./util/identity');
const { SHA256_HEX, SAFE_ID } = require('./util/validate');
const { ROLES } = require('./policy/policyV1');

const POLICY_KEY = 'policyVersion';
const ACTIVE_POLICY_KEY = 'activePolicyVersion';

class PolicyContract extends Contract {
  constructor() {
    super('PolicyContract');
  }

  _requirePolicyAdmin(ctx, action) {
    const caller = getCaller(ctx);
    requireMsp(caller, [MSP.AUDIT, MSP.COURT], action);
    requireRole(caller, [ROLES.AUDITOR, ROLES.OMBUDSMAN, ROLES.JUDGE], action);
    return caller;
  }

  async CreatePolicyVersion(ctx, version, rulesHash, description) {
    const caller = this._requirePolicyAdmin(ctx, 'CreatePolicyVersion');
    if (!SAFE_ID.test(version)) throw new Error('version has invalid format');
    if (!SHA256_HEX.test(rulesHash)) throw new Error('rulesHash must be a sha256 hex digest');
    const key = ctx.stub.createCompositeKey(POLICY_KEY, [version]);
    const existing = await ctx.stub.getState(key);
    if (existing && existing.length > 0) throw new Error(`policy '${version}' already exists`);
    const policy = {
      docType: 'policyVersion', version, rulesHash,
      description: String(description || '').slice(0, 500),
      status: 'draft', createdByIdentity: caller.id,
      createdAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      txId: ctx.stub.getTxID(),
    };
    await ctx.stub.putState(key, Buffer.from(JSON.stringify(policy)));
    ctx.stub.setEvent('PolicyVersionCreated', Buffer.from(JSON.stringify({ version, rulesHash })));
    return JSON.stringify(policy);
  }

  async ActivatePolicyVersion(ctx, version) {
    const caller = this._requirePolicyAdmin(ctx, 'ActivatePolicyVersion');
    const key = ctx.stub.createCompositeKey(POLICY_KEY, [version]);
    const data = await ctx.stub.getState(key);
    if (!data || data.length === 0) throw new Error(`policy '${version}' does not exist`);
    const previousData = await ctx.stub.getState(ACTIVE_POLICY_KEY);
    const previous = previousData && previousData.length > 0
      ? JSON.parse(previousData.toString()) : null;
    if (previous && previous.version === version) {
      throw new Error(`policy '${version}' is already active`);
    }
    if (previous) {
      const previousKey = ctx.stub.createCompositeKey(POLICY_KEY, [previous.version]);
      const previousPolicyData = await ctx.stub.getState(previousKey);
      if (previousPolicyData && previousPolicyData.length > 0) {
        const previousPolicy = JSON.parse(previousPolicyData.toString());
        await ctx.stub.putState(previousKey, Buffer.from(JSON.stringify({
          ...previousPolicy, status: 'superseded', supersededBy: version,
        })));
      }
    }
    const policy = JSON.parse(data.toString());
    const active = {
      ...policy, status: 'active', previousVersion: previous ? previous.version : null,
      activatedByIdentity: caller.id,
      activatedAtUtc: ctx.stub.getDateTimestamp().toISOString(),
      activationTxId: ctx.stub.getTxID(),
    };
    await ctx.stub.putState(key, Buffer.from(JSON.stringify(active)));
    await ctx.stub.putState(ACTIVE_POLICY_KEY, Buffer.from(JSON.stringify(active)));
    ctx.stub.setEvent('PolicyVersionActivated', Buffer.from(JSON.stringify({ version })));
    return JSON.stringify(active);
  }

  async GetActivePolicyVersion(ctx) {
    const data = await ctx.stub.getState(ACTIVE_POLICY_KEY);
    if (!data || data.length === 0) return JSON.stringify(null);
    return data.toString();
  }

  async QueryPolicyVersions(ctx) {
    const iterator = await ctx.stub.getStateByPartialCompositeKey(POLICY_KEY, []);
    const items = [];
    let result = await iterator.next();
    while (!result.done) {
      items.push(JSON.parse(result.value.value.toString()));
      result = await iterator.next();
    }
    await iterator.close();
    return JSON.stringify(items);
  }
}

module.exports = PolicyContract;
