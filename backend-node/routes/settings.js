const router = require('express').Router();
const { authenticate } = require('../middleware/auth');
const { User, Notification } = require('../models');

router.use(authenticate);

router.get('/profile', (req, res) => {
  const u = req.user;
  res.json({
    id: u.id, name: u.name || '', email: u.email, picture: u.picture,
    company_name: u.company_name || '', is_superuser: u.is_superuser,
    notif_email: u.notif_email ?? true, notif_campaigns: u.notif_campaigns ?? true,
    email_limit: u.email_limit || 1000, emails_used: u.emails_used || 0,
    is_blocked: u.is_blocked || false
  });
});

router.put('/profile', async (req, res) => {
  const { name, company_name } = req.body;
  if (name !== undefined) req.user.name = name;
  if (company_name !== undefined) req.user.company_name = company_name;
  await req.user.save();
  res.json({ success: true, name: req.user.name, company_name: req.user.company_name });
});

router.put('/notifications/preferences', async (req, res) => {
  const { notif_email, notif_campaigns } = req.body;
  if (notif_email !== undefined) req.user.notif_email = notif_email;
  if (notif_campaigns !== undefined) req.user.notif_campaigns = notif_campaigns;
  await req.user.save();
  res.json({ success: true });
});

router.get('/usage', (req, res) => {
  const limit = req.user.email_limit || 1000;
  const used = req.user.emails_used || 0;
  res.json({
    email_limit: limit, emails_used: used,
    remaining: Math.max(0, limit - used),
    percentage_used: limit > 0 ? Math.round(used / limit * 1000) / 10 : 0,
    is_blocked: req.user.is_blocked || false
  });
});

router.get('/notifications', async (req, res) => {
  const notifs = await Notification.findAll({ where: { user_id: req.user.id }, order: [['created_at', 'DESC']], limit: 50 });
  const unread_count = await Notification.count({ where: { user_id: req.user.id, is_read: false } });

  const now = new Date();
  const timeAgo = (d) => {
    if (!d) return '';
    const diff = Math.floor((now - new Date(d)) / 1000);
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  res.json({
    notifications: notifs.map(n => ({ id: n.id, type: n.type, title: n.title, message: n.message, is_read: n.is_read, campaign_id: n.campaign_id, created_at: n.createdAt, time: timeAgo(n.createdAt) })),
    unread_count
  });
});

router.post('/notifications/:id/read', async (req, res) => {
  await Notification.update({ is_read: true }, { where: { id: req.params.id, user_id: req.user.id } });
  res.json({ success: true });
});

router.post('/notifications/read-all', async (req, res) => {
  await Notification.update({ is_read: true }, { where: { user_id: req.user.id, is_read: false } });
  res.json({ success: true });
});

router.delete('/notifications/:id', async (req, res) => {
  await Notification.destroy({ where: { id: req.params.id, user_id: req.user.id } });
  res.json({ success: true });
});

module.exports = router;
