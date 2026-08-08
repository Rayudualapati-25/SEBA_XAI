/**
 * API client and session.
 *
 * Adding an endpoint: put it in the matching group below. Groups mirror the
 * backend routers (auth / records / access / audit / explain), so the two stay
 * easy to compare.
 *
 * Every call returns the unwrapped `data` or throws an Error carrying the
 * server's message — callers never see the {success, data, error} envelope.
 */

const BASE = '/api';
const TOKEN_KEY = 'crn.token';
const USER_KEY = 'crn.user';

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

export const session = {
  token: () => sessionStorage.getItem(TOKEN_KEY),
  user: () => {
    const raw = sessionStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },
  save: (token, user) => {
    sessionStorage.setItem(TOKEN_KEY, token);
    sessionStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: () => {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  },
};

/** Notified when the server rejects our token, so the shell can show login. */
let onSessionExpired = () => {};
export function setSessionExpiredHandler(handler) {
  onSessionExpired = handler;
}

// ---------------------------------------------------------------------------
// Transport
// ---------------------------------------------------------------------------

async function request(method, path, body) {
  const token = session.token();
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch {
    throw new Error('cannot reach the server — is the backend running?');
  }

  let json;
  try {
    json = await res.json();
  } catch {
    throw new Error(`server returned ${res.status} with no JSON body`);
  }

  if (res.status === 401 && token) {
    session.clear();
    onSessionExpired();
    throw new Error('your session expired — please sign in again');
  }
  if (!json.success) throw new Error(json.error || `request failed (${res.status})`);
  return json.data;
}

const query = (params) => {
  const usable = Object.entries(params || {}).filter(([, v]) => v !== undefined && v !== '');
  return usable.length ? `?${new URLSearchParams(usable).toString()}` : '';
};

// ---------------------------------------------------------------------------
// Endpoints, grouped to match the backend routers
// ---------------------------------------------------------------------------

export const api = {
  auth: {
    async login(username, password) {
      const data = await request('POST', '/auth/login', { username, password });
      session.save(data.token, data.user);
      return data.user;
    },
    me: () => request('GET', '/auth/me'),
  },

  records: {
    create: (payload) => request('POST', '/records', payload),
    search: (filters) => request('GET', `/records${query(filters)}`),
    get: (recordId) => request('GET', `/records/${recordId}`),
    payload: (recordId) => request('GET', `/records/${recordId}/payload`),
    seal: (recordId) => request('POST', `/records/${recordId}/seal`),
    unseal: (recordId) => request('POST', `/records/${recordId}/unseal`),
  },

  evidence: {
    list: (recordId) => request('GET', `/records/${recordId}/evidence`),
    attach: (recordId, body) => request('POST', `/records/${recordId}/evidence`, body),
    detail: (recordId, evidenceId) =>
      request('GET', `/records/${recordId}/evidence/${evidenceId}/detail`),
  },

  access: {
    request: (body) => request('POST', '/access/request', body),
    forRecord: (recordId) => request('GET', `/access/record/${recordId}`),
    pending: () => request('GET', '/access/pending'),
    approve: (recordId, decisionId, note) =>
      request('POST', `/access/${recordId}/${decisionId}/approve`, { note }),
    reject: (recordId, decisionId, note) =>
      request('POST', `/access/${recordId}/${decisionId}/reject`, { note }),
  },

  audit: {
    trail: (recordId) => request('GET', `/audit/trail/${recordId}`),
    verifyPayload: (recordId) => request('POST', `/audit/verify-payload/${recordId}`),
    verifyExplanation: (recordId, decisionId, artifact) =>
      request('POST', `/audit/verify-explanation/${recordId}/${decisionId}`, { artifact }),
    accessLog: (limit = 50) => request('GET', `/audit/access-log${query({ limit })}`),
    verifyAccessLog: () => request('GET', '/audit/access-log/verify'),
    anchor: () => request('POST', '/audit/anchor'),
  },

  explain: {
    decision: (recordId, decisionId) => request('POST', `/explain/${recordId}/${decisionId}`),
    health: () => request('GET', '/explain/health'),
  },
};
