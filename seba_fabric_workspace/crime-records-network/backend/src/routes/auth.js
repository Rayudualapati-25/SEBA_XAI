'use strict';

const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { z } = require('zod');
const db = require('../db');
const { JWT_SECRET, JWT_EXPIRY } = require('../config');
const { ok, fail, asyncRoute } = require('../util/respond');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

const loginSchema = z.object({
  username: z.string().min(1).max(64),
  password: z.string().min(1).max(128),
});

router.post('/login', asyncRoute(async (req, res) => {
  const parsed = loginSchema.safeParse(req.body);
  if (!parsed.success) return fail(res, 'username and password are required');

  const { username, password } = parsed.data;
  const user = db.findUser(username);
  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return fail(res, 'invalid credentials', 401);
  }

  const claims = {
    username: user.username,
    org: user.org,
    fabricUser: user.fabric_user,
    role: user.role,
    displayName: user.display_name,
  };
  const token = jwt.sign(claims, JWT_SECRET, { expiresIn: JWT_EXPIRY });
  return ok(res, { token, user: claims });
}));

router.get('/me', requireAuth, (req, res) => ok(res, req.user));

module.exports = router;
