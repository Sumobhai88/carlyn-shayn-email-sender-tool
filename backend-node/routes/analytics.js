const router = require('express').Router();
const { authenticate } = require('../middleware/auth');
const { EmailLog, Campaign } = require('../models');
const { Op } = require('sequelize');

router.use(authenticate);

router.get('/stats', async (req, res) => {
  const campaigns = await Campaign.findAll({ where: { user_id: req.user.id }, attributes: ['id'] });
  const campaignIds = campaigns.map(c => c.id);
  if (!campaignIds.length) return res.json({ total_sent: 0, delivered: 0, opened: 0, bounced: 0, failed: 0, unsubscribed: 0 });

  const where = { campaign_id: { [Op.in]: campaignIds } };
  const total_sent = await EmailLog.count({ where });
  const delivered = await EmailLog.count({ where: { ...where, delivery_status: 'delivered' } });
  const opened = await EmailLog.count({ where: { ...where, opened: true } });
  const bounced = await EmailLog.count({ where: { ...where, bounced: true } });
  const failed = await EmailLog.count({ where: { ...where, delivery_status: 'failed' } });
  const unsubscribed = await EmailLog.count({ where: { ...where, unsubscribed: true } });

  res.json({ total_sent, delivered, opened, bounced, failed, unsubscribed });
});

router.get('/email-logs', async (req, res) => {
  const { limit = 1000, campaign_id, status_filter, search } = req.query;
  const campaigns = await Campaign.findAll({ where: { user_id: req.user.id }, attributes: ['id', 'campaign_name'] });
  const campaignIds = campaigns.map(c => c.id);
  const campaignMap = Object.fromEntries(campaigns.map(c => [c.id, c.campaign_name]));

  if (!campaignIds.length) return res.json({ total: 0, email_logs: [] });

  const where = { campaign_id: { [Op.in]: campaignIds } };
  if (campaign_id) where.campaign_id = parseInt(campaign_id);
  if (status_filter === 'delivered') where.delivery_status = 'delivered';
  if (status_filter === 'failed') where.delivery_status = 'failed';
  if (status_filter === 'opened') where.opened = true;
  if (status_filter === 'bounced') where.bounced = true;
  if (search) where.recipient_email = { [Op.like]: `%${search}%` };

  const logs = await EmailLog.findAll({ where, order: [['created_at', 'DESC']], limit: parseInt(limit) });
  const email_logs = logs.map(l => ({
    id: l.id, campaign_id: l.campaign_id, campaign_name: campaignMap[l.campaign_id] || '',
    contact_id: l.contact_id, recipient_email: l.recipient_email, subject: l.subject,
    delivery_status: l.delivery_status, opened: l.opened, bounced: l.bounced, unsubscribed: l.unsubscribed,
    tracking_id: l.tracking_id, sent_at: l.sent_at, delivered_at: l.delivered_at, opened_at: l.opened_at,
    created_at: l.createdAt
  }));

  res.json({ total: email_logs.length, email_logs });
});

module.exports = router;
