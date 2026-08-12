'use strict';

const path = require('path');
const express = require('express');
const cors = require('cors');
const { PORT } = require('./config');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const departmentRoutes = require('./routes/departments');
const caseRoutes = require('./routes/cases');
const recordRoutes = require('./routes/records');
const accessRoutes = require('./routes/access');
const auditRoutes = require('./routes/audit');
const explainRoutes = require('./routes/explain');
const { accessLogger } = require('./middleware/accessLogger');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

// Records authenticated API calls as Fabric transactions. Mounted before the
// routes so it sees every request; it submits after the response is sent.
app.use('/api', accessLogger);

app.get('/api/health', (req, res) => res.json({ success: true, data: 'ok', error: null }));
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/departments', departmentRoutes);
app.use('/api/cases', caseRoutes);
app.use('/api/records', recordRoutes);
app.use('/api/access', accessRoutes);
app.use('/api/audit', auditRoutes);
app.use('/api/explain', explainRoutes);

// Serve the dashboard from the same origin as the API (no CORS, no build step).
app.use(express.static(path.resolve(__dirname, '..', '..', 'frontend')));

app.use('/api', (req, res) =>
  res.status(404).json({ success: false, data: null, error: 'not found' }));
app.use((req, res) => res.status(404).send('not found'));

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`crime-records backend listening on http://localhost:${PORT}`);
});
