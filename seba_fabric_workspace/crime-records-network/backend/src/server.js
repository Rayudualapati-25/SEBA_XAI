'use strict';

const path = require('path');
const express = require('express');
const cors = require('cors');
const { PORT } = require('./config');
const authRoutes = require('./routes/auth');
const recordRoutes = require('./routes/records');
const accessRoutes = require('./routes/access');
const auditRoutes = require('./routes/audit');
const explainRoutes = require('./routes/explain');
const { accessLogger } = require('./middleware/accessLogger');
const anchor = require('./audit/anchor');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

// Records every API call in the tamper-evident access log. Mounted before the
// routes so it sees every request, but it only writes after the response is sent.
app.use('/api', accessLogger);

app.get('/api/health', (req, res) => res.json({ success: true, data: 'ok', error: null }));
app.use('/api/auth', authRoutes);
app.use('/api/records', recordRoutes);
app.use('/api/access', accessRoutes);
app.use('/api/audit', auditRoutes);
app.use('/api/explain', explainRoutes);

// Attack-replay helpers for the Phase 6 measurements. Off unless asked for.
if (process.env.ENABLE_EXPERIMENTS === '1') {
  // eslint-disable-next-line global-require
  app.use('/api/experiments', require('./routes/experiments'));
  // eslint-disable-next-line no-console
  console.warn('[server] experiment routes ENABLED — off-chain tampering endpoint is reachable');
}

// Serve the dashboard from the same origin as the API (no CORS, no build step).
app.use(express.static(path.resolve(__dirname, '..', '..', 'frontend')));

app.use('/api', (req, res) =>
  res.status(404).json({ success: false, data: null, error: 'not found' }));
app.use((req, res) => res.status(404).send('not found'));

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`crime-records backend listening on http://localhost:${PORT}`);

  // Anchor anything left unanchored by a previous run, so a restart cannot be
  // used to leave a tail of entries permanently uncommitted.
  anchor.anchorNow({ force: true })
    .then((written) => {
      if (written) {
        // eslint-disable-next-line no-console
        console.log(`[anchor] anchored access log up to entry ${written.seqNo}`);
      }
    })
    .catch(() => {});
});
