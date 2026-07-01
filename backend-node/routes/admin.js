const router = require('express').Router();
const { authenticate, requireAdmin } = require('../middleware/auth');
const { User, Campaign, EmailLog } = require('../models');
const { sequelize } = require('../config/database');
const { fn, col } = require('sequelize');

router.use(authenticate, requireAdmin);

router.get('/users', async (req, res) => {
  const users = await User.findAll({ order: [['created_at', 'DESC']] });
  const result = [];

  for (const u of users) {
    const campaign_count = await Campaign.count({ where: { user_id: u.id } });
    const total_sent = await Campaign.sum('sent_count', { where: { user_id: u.id } }) || 0;
    result.push({
      id: u.id, name: u.name || '', email: u.email, picture: u.picture,
      company_name: u.company_name || '', is_active: u.is_active,
      is_superuser: u.is_superuser, is_blocked: u.is_blocked || false,
      email_limit: u.email_limit || 1000, emails_used: u.emails_used || 0,
      campaign_count, total_sent,
      created_at: u.createdAt, last_login: u.last_login
    });
  }

  res.json({
    users: result, total_users: result.length,
    blocked_users: result.filter(u => u.is_blocked).length,
    admin_users: result.filter(u => u.is_superuser).length
  });
});

router.put('/users/:id/limit', async (req, res) => {
  const u = await User.findByPk(req.params.id);
  if (!u) return res.status(404).json({ detail: 'User not found' });
  await u.update({ email_limit: req.body.email_limit });
  res.json({ success: true, email_limit: u.email_limit });
});

router.post('/users/:id/block', async (req, res) => {
  const u = await User.findByPk(req.params.id);
  if (!u) return res.status(404).json({ detail: 'User not found' });
  if (u.id === req.user.id) return res.status(400).json({ detail: 'Cannot block yourself' });
  await u.update({ is_blocked: req.body.is_blocked });
  res.json({ success: true, is_blocked: u.is_blocked });
});

router.post('/users/:id/reset-usage', async (req, res) => {
  const u = await User.findByPk(req.params.id);
  if (!u) return res.status(404).json({ detail: 'User not found' });
  await u.update({ emails_used: 0 });
  res.json({ success: true });
});

router.post('/users/:id/make-admin', async (req, res) => {
  const u = await User.findByPk(req.params.id);
  if (!u) return res.status(404).json({ detail: 'User not found' });
  await u.update({ is_superuser: !u.is_superuser });
  res.json({ success: true, is_superuser: u.is_superuser });
});

module.exports = router;
