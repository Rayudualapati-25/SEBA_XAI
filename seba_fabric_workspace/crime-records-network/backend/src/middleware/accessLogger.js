'use strict';

/**
 * Records every API call in the tamper-evident access log.
 *
 * Runs AFTER the response has been sent, so logging never slows a request down
 * and never turns a logging bug into a failed request.
 *
 * Only who/what/when is recorded — never the case narrative, the payload
 * contents, a password or a token. Search filters ARE recorded, because "who
 * went looking for this case" is exactly the signal an auditor needs.
 */

const db = require('../db');
const accessLog = require('../audit/accessLog');
const anchor = require('../audit/anchor');

/**
 * Map a request to a stable action name and a safe target.
 * Returns null for requests that are not worth logging (health checks, statics).
 *
 * Takes a snapshot { method, path, query, body } rather than the live request:
 * Express rewrites req.url while nested routers dispatch, so by the time the
 * response has finished the path no longer identifies the route.
 */
function describe(snapshot) {
  const path = snapshot.path;
  const method = snapshot.method;
  const req = { query: snapshot.query || {}, body: snapshot.body || {} };

  if (path === '/health' || path.startsWith('/explain/health')) return null;

  // Auth
  if (path === '/auth/login') {
    return { action: 'auth.login', target: { username: req.body && req.body.username } };
  }
  if (path === '/auth/me') return { action: 'auth.whoami', target: null };

  // Records
  if (path === '/records' && method === 'GET') {
    // The search filters are the investigative signal, so they are logged.
    return { action: 'record.search', target: { filters: req.query } };
  }
  if (path === '/records' && method === 'POST') {
    return { action: 'record.create', target: { recordId: req.body && req.body.recordId } };
  }
  const recordMatch = path.match(/^\/records\/([^/]+)(\/.*)?$/);
  if (recordMatch) {
    const recordId = recordMatch[1];
    const rest = recordMatch[2] || '';
    if (rest === '/payload') return { action: 'payload.release', target: { recordId } };
    if (rest.endsWith('/detail')) return { action: 'evidence.detail.read', target: { recordId } };
    if (rest === '/evidence') {
      return {
        action: method === 'POST' ? 'evidence.attach' : 'evidence.list',
        target: { recordId },
      };
    }
    if (rest === '/seal') return { action: 'record.seal', target: { recordId } };
    if (rest === '/unseal') return { action: 'record.unseal', target: { recordId } };
    return { action: 'record.read', target: { recordId } };
  }

  // Access decisions
  if (path === '/access/request') {
    return {
      action: 'access.request',
      target: { recordId: req.body && req.body.recordId, purpose: req.body && req.body.purpose },
    };
  }
  if (path === '/access/pending') return { action: 'escalation.queue.read', target: null };
  const resolveMatch = path.match(/^\/access\/([^/]+)\/([^/]+)\/(approve|reject)$/);
  if (resolveMatch) {
    return {
      action: `escalation.${resolveMatch[3]}`,
      target: { recordId: resolveMatch[1], decisionId: resolveMatch[2] },
    };
  }
  if (path.startsWith('/access/record/')) {
    return { action: 'decision.list', target: { recordId: path.split('/').pop() } };
  }

  // Audit
  if (path.startsWith('/audit/trail/')) {
    return { action: 'audit.trail.read', target: { recordId: path.split('/').pop() } };
  }
  if (path.startsWith('/audit/verify-payload/')) {
    return { action: 'audit.verify.payload', target: { recordId: path.split('/').pop() } };
  }
  if (path.startsWith('/audit/verify-explanation/')) {
    return { action: 'audit.verify.explanation', target: null };
  }
  if (path.startsWith('/audit/access-log')) {
    return { action: 'audit.accesslog.read', target: null };
  }

  // Explanations
  if (path.startsWith('/explain/')) {
    return { action: 'explanation.render', target: { recordId: path.split('/')[2] } };
  }

  return { action: `api${path.replace(/\//g, '.')}`, target: null };
}

function outcomeFor(status, action) {
  if (status >= 500) return 'error';
  if (status === 401 || status === 403) {
    return action === 'auth.login' ? 'failed' : 'refused';
  }
  if (status >= 400) return 'rejected';
  return 'ok';
}

function accessLogger(req, res, next) {
  // Snapshot now: req.url is mutated by nested routers before 'finish' fires.
  // req.originalUrl is the one field Express never rewrites.
  const snapshot = {
    method: req.method,
    path: req.originalUrl.split('?')[0].replace(/^\/api/, '') || '/',
    query: { ...req.query },
    body: req.body && typeof req.body === 'object' ? { ...req.body } : {},
  };

  res.on('finish', () => {
    try {
      const described = describe(snapshot);
      if (!described) return;

      const user = req.user || {};
      const action = described.action === 'auth.login' && res.statusCode !== 200
        ? 'auth.login_failed'
        : described.action;

      accessLog.append(db, {
        actorUsername: user.username || snapshot.body.username || null,
        actorMsp: user.org ? `${user.org}` : null,
        actorRole: user.role || null,
        action,
        target: described.target,
        outcome: outcomeFor(res.statusCode, described.action),
        status: res.statusCode,
      });

      // Fire and forget: anchoring must not delay anything.
      anchor.anchorNow().catch(() => {});
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('[accessLogger] failed to record entry:', err.message);
    }
  });
  next();
}

module.exports = { accessLogger, describe };
