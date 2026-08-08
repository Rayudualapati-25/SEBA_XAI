'use strict';

/**
 * Off-chain store (SQLite): the "agency-controlled storage" of the paper.
 * Holds raw record payloads and web-app user accounts. The ledger only ever
 * sees SHA-256 commitments of what lives here.
 */

const fs = require('fs');
const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const { DATA_DIR, DB_FILE } = require('./config');

fs.mkdirSync(DATA_DIR, { recursive: true });
const db = new Database(DB_FILE);
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    username      TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    org           TEXT NOT NULL,
    fabric_user   TEXT NOT NULL,
    display_name  TEXT NOT NULL,
    role          TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS payloads (
    record_id  TEXT PRIMARY KEY,
    payload    TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  -- Plain-language explanations written by the local LLM (or the template when
  -- the LLM is unavailable). Kept OFF the blockchain on purpose: the ledger must
  -- not depend on a non-deterministic component. This table is just a cache plus
  -- a record of what text an officer was actually shown.
  CREATE TABLE IF NOT EXISTS explanation_renderings (
    explanation_hash TEXT NOT NULL,
    prompt_version   TEXT NOT NULL,
    decision_id      TEXT NOT NULL,
    record_id        TEXT NOT NULL,
    text             TEXT NOT NULL,
    source           TEXT NOT NULL,
    model            TEXT,
    latency_ms       INTEGER,
    problems         TEXT,
    warnings         TEXT,
    created_at       TEXT NOT NULL,
    PRIMARY KEY (explanation_hash, prompt_version)
  );
`);

db.exec(`
  -- Tamper-evident access log. Records reads and searches, which are Fabric
  -- queries and therefore leave no trace on the ledger. Each row stores the
  -- previous row's hash, so any edit or deletion breaks the chain. The head
  -- hash is periodically anchored on-chain (see src/audit/anchor.js).
  CREATE TABLE IF NOT EXISTS access_log (
    seq            INTEGER PRIMARY KEY,
    ts             TEXT NOT NULL,
    actor_username TEXT,
    actor_msp      TEXT,
    actor_role     TEXT,
    action         TEXT NOT NULL,
    target         TEXT,
    outcome        TEXT NOT NULL,
    status         INTEGER NOT NULL,
    prev_hash      TEXT NOT NULL,
    entry_hash     TEXT NOT NULL
  );
  -- How far the log has been committed to the blockchain.
  -- 'epoch' identifies one continuous life of this log. If the database is ever
  -- recreated a new epoch is generated, so anchors from the previous log are not
  -- silently compared against the new one. Resets are allowed but visible: every
  -- epoch ever anchored stays in the ledger's key history.
  CREATE TABLE IF NOT EXISTS access_log_anchor_state (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    epoch         TEXT NOT NULL,
    anchored_upto INTEGER NOT NULL,
    anchored_at   TEXT
  );
`);

// Migration for databases created before `epoch` existed. Added as nullable
// because SQLite cannot add a NOT NULL column without a constant default; it is
// backfilled immediately below.
try {
  db.exec('ALTER TABLE access_log_anchor_state ADD COLUMN epoch TEXT');
} catch {
  // Column already present.
}

// Seed (or backfill) the epoch. randomUUID means a recreated database can never
// accidentally reuse a previous epoch and have its anchors silently compared.
const newEpoch = () => `ep-${require('crypto').randomUUID()}`;
db.prepare(`
  INSERT OR IGNORE INTO access_log_anchor_state (id, epoch, anchored_upto)
  VALUES (1, ?, 0)
`).run(newEpoch());
db.prepare('UPDATE access_log_anchor_state SET epoch = ? WHERE epoch IS NULL')
  .run(newEpoch());

// Tiny migration for databases created before `warnings` existed. CREATE TABLE
// IF NOT EXISTS never adds columns to a table that is already there.
try {
  db.exec('ALTER TABLE explanation_renderings ADD COLUMN warnings TEXT');
} catch {
  // Column already present — nothing to do.
}

// Demo accounts — one web login per seeded Fabric identity. Password is the
// same for every demo account and obviously not for production use.
const DEMO_PASSWORD = 'demo123';
const DEMO_USERS = [
  ['insp.sharma', 'police', 'Insp. A. Sharma', 'inspector'],
  ['const.verma', 'police', 'Const. R. Verma', 'constable'],
  ['sho.reddy', 'police', 'SHO K. Reddy', 'sho'],
  ['io.krishnan', 'police', 'IO S. Krishnan', 'investigating-officer'],
  ['insp.rathore', 'police', 'Insp. V. Rathore (revoked)', 'inspector'],
  ['analyst.rao', 'forensics', 'Analyst P. Rao', 'lab-analyst'],
  ['dir.iyer', 'forensics', 'Dir. M. Iyer', 'lab-director'],
  ['pp.mehta', 'prosecution', 'PP D. Mehta', 'public-prosecutor'],
  ['dc.nair', 'prosecution', 'Adv. L. Nair', 'defense-counsel'],
  ['judge.rana', 'court', 'Hon. Justice Rana', 'judge'],
  ['clerk.das', 'court', 'Clerk B. Das', 'court-clerk'],
  ['aud.qureshi', 'audit', 'Auditor F. Qureshi', 'auditor'],
  ['omb.pillai', 'audit', 'Ombudsman T. Pillai', 'ombudsman'],
];

function seedUsers() {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO users (username, password_hash, org, fabric_user, display_name, role)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  const hash = bcrypt.hashSync(DEMO_PASSWORD, 10);
  const tx = db.transaction(() => {
    for (const [username, org, displayName, role] of DEMO_USERS) {
      insert.run(username, hash, org, username, displayName, role);
    }
  });
  tx();
}

seedUsers();

module.exports = {
  findUser: (username) =>
    db.prepare('SELECT * FROM users WHERE username = ?').get(username),
  savePayload: (recordId, payload, createdBy) =>
    db.prepare(`
      INSERT INTO payloads (record_id, payload, created_by, created_at)
      VALUES (?, ?, ?, ?)
    `).run(recordId, payload, createdBy, new Date().toISOString()),
  getPayload: (recordId) =>
    db.prepare('SELECT * FROM payloads WHERE record_id = ?').get(recordId),
  // For the tamper demo (P6): overwrite a stored payload out-of-band.
  tamperPayload: (recordId, payload) =>
    db.prepare('UPDATE payloads SET payload = ? WHERE record_id = ?').run(payload, recordId),

  getRendering: ({ explanationHash, promptVersion }) => {
    const row = db.prepare(`
      SELECT text, source, model, problems, warnings FROM explanation_renderings
      WHERE explanation_hash = ? AND prompt_version = ?
    `).get(explanationHash, promptVersion);
    if (!row) return undefined;
    // Return the original findings, not empty arrays — they are reported as data.
    return {
      ...row,
      problems: JSON.parse(row.problems || '[]'),
      warnings: JSON.parse(row.warnings || '[]'),
    };
  },

  // --- access log -----------------------------------------------------------

  getAccessLogHead: () =>
    db.prepare('SELECT seq, entry_hash FROM access_log ORDER BY seq DESC LIMIT 1').get(),

  appendAccessLogEntry: ({ seq, ts, actorUsername, actorMsp, actorRole, action,
    target, outcome, status, prevHash, entryHash }) =>
    db.prepare(`
      INSERT INTO access_log
        (seq, ts, actor_username, actor_msp, actor_role, action, target,
         outcome, status, prev_hash, entry_hash)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(seq, ts, actorUsername, actorMsp, actorRole, action, target,
      outcome, status, prevHash, entryHash),

  getAllAccessLogEntries: () =>
    db.prepare('SELECT * FROM access_log ORDER BY seq ASC').all(),

  getRecentAccessLogEntries: (limit = 50) =>
    db.prepare('SELECT * FROM access_log ORDER BY seq DESC LIMIT ?').all(limit),

  getAnchorState: () =>
    db.prepare('SELECT epoch, anchored_upto, anchored_at FROM access_log_anchor_state WHERE id = 1').get(),

  setAnchoredUpto: (seq) =>
    db.prepare(`
      UPDATE access_log_anchor_state SET anchored_upto = ?, anchored_at = ? WHERE id = 1
    `).run(seq, new Date().toISOString()),

  // Used only by the attack replay: corrupt the log the way an insider would.
  tamperAccessLogEntry: (seq, action) =>
    db.prepare('UPDATE access_log SET action = ? WHERE seq = ?').run(action, seq),
  deleteAccessLogEntry: (seq) =>
    db.prepare('DELETE FROM access_log WHERE seq = ?').run(seq),

  saveRendering: ({ explanationHash, promptVersion, decisionId, recordId, text,
    source, model, latencyMs, problems, warnings }) =>
    db.prepare(`
      INSERT OR REPLACE INTO explanation_renderings
        (explanation_hash, prompt_version, decision_id, record_id, text, source,
         model, latency_ms, problems, warnings, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(explanationHash, promptVersion, decisionId, recordId, text, source,
      model, latencyMs, JSON.stringify(problems || []),
      JSON.stringify(warnings || []), new Date().toISOString()),
};
