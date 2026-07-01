const router = require('express').Router();
const multer = require('multer');
const { parse } = require('csv-parse/sync');
const XLSX = require('xlsx');
const { v4: uuidv4 } = require('uuid');
const { authenticate } = require('../middleware/auth');
const { Campaign, Contact, EmailLog, User } = require('../models');
const { sendCampaignEmails } = require('../services/emailEngine');

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } });

router.use(authenticate);

// Create campaign
router.post('/', async (req, res) => {
  try {
    const campaign = await Campaign.create({
      user_id: req.user.id,
      campaign_name: req.body.campaign_name,
      subject: req.body.subject,
      template: req.body.template,
      status: 'draft'
    });
    res.status(201).json(campaign);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Get all campaigns for user
router.get('/', async (req, res) => {
  try {
    const campaigns = await Campaign.findAll({
      where: { user_id: req.user.id },
      order: [['created_at', 'DESC']]
    });
    res.json({ campaigns });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Fix stats
router.post('/fix-stats', async (req, res) => {
  try {
    const campaigns = await Campaign.findAll({ where: { user_id: req.user.id } });
    for (const c of campaigns) {
      const total = await EmailLog.count({ where: { campaign_id: c.id } });
      const delivered = await EmailLog.count({ where: { campaign_id: c.id, delivery_status: 'delivered' } });
      const failed = await EmailLog.count({ where: { campaign_id: c.id, delivery_status: 'failed' } });
      const opened = await EmailLog.count({ where: { campaign_id: c.id, opened: true } });
      const bounced = await EmailLog.count({ where: { campaign_id: c.id, bounced: true } });
      const unsub = await EmailLog.count({ where: { campaign_id: c.id, unsubscribed: true } });
      await c.update({ sent_count: total, delivered_count: delivered, failed_count: failed, opened_count: opened, bounced_count: bounced, unsubscribed_count: unsub });
    }
    res.json({ success: true, message: `Fixed ${campaigns.length} campaigns`, campaigns_fixed: campaigns.length });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Get stats
router.get('/stats', async (req, res) => {
  try {
    const { sequelize } = require('../config/database');
    const campaigns = await Campaign.findAll({ where: { user_id: req.user.id } });
    const totalSent = campaigns.reduce((s, c) => s + (c.sent_count || 0), 0);
    const totalDelivered = campaigns.reduce((s, c) => s + (c.delivered_count || 0), 0);
    const totalFailed = campaigns.reduce((s, c) => s + (c.failed_count || 0), 0);
    res.json({
      total_campaigns: campaigns.length,
      active_campaigns: campaigns.filter(c => c.status === 'running').length,
      total_sent: totalSent, total_delivered: totalDelivered, total_failed: totalFailed,
      average_open_rate: 0, average_click_rate: 0
    });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Upload recipients
router.post('/:id/upload-recipients', upload.single('file'), async (req, res) => {
  try {
    const campaign = await Campaign.findOne({ where: { id: req.params.id, user_id: req.user.id } });
    if (!campaign) return res.status(404).json({ detail: 'Campaign not found' });

    const ext = req.file.originalname.split('.').pop().toLowerCase();
    let rows = [];

    if (ext === 'csv') {
      rows = parse(req.file.buffer.toString(), { columns: true, skip_empty_lines: true, trim: true });
    } else if (ext === 'xlsx') {
      const wb = XLSX.read(req.file.buffer);
      const ws = wb.Sheets[wb.SheetNames[0]];
      rows = XLSX.utils.sheet_to_json(ws);
    } else {
      return res.status(400).json({ detail: 'Only CSV/XLSX supported' });
    }

    let valid = 0, invalid = 0, duplicates = 0;
    const existingEmails = new Set(
      (await Contact.findAll({ where: { campaign_id: campaign.id }, attributes: ['email'] }))
        .map(c => c.email.toLowerCase())
    );
    const seen = new Set();

    for (const row of rows) {
      const email = (row.email || '').trim().toLowerCase();
      const firstName = (row.first_name || '').trim();
      const lastName = (row.last_name || '').trim();

      if (!email || !firstName || !lastName || !email.includes('@')) { invalid++; continue; }
      if (existingEmails.has(email) || seen.has(email)) { duplicates++; continue; }
      seen.add(email);

      await Contact.create({
        campaign_id: campaign.id,
        first_name: firstName, last_name: lastName, email,
        phone: (row.phone || '').trim() || null,
        company: (row.company || '').trim() || null,
        unsubscribe_token: uuidv4()
      });
      valid++;
    }

    await campaign.update({ total_emails: (campaign.total_emails || 0) + valid });
    res.json({
      success: true, total_contacts: rows.length,
      valid_contacts: valid, invalid_contacts: invalid, duplicate_contacts: duplicates,
      errors: [], campaign_id: campaign.id
    });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Start campaign
router.post('/:id/start', async (req, res) => {
  try {
    const campaign = await Campaign.findOne({ where: { id: req.params.id, user_id: req.user.id } });
    if (!campaign) return res.status(404).json({ detail: 'Campaign not found' });
    if (campaign.status === 'running') return res.status(409).json({ detail: 'Already running' });

    const contactCount = await Contact.count({ where: { campaign_id: campaign.id } });
    if (!contactCount) return res.status(400).json({ detail: 'No contacts uploaded' });

    // Check limits
    const user = req.user;
    if (user.is_blocked) return res.status(403).json({ detail: 'Your service is blocked by admin.' });
    const remaining = (user.email_limit || 1000) - (user.emails_used || 0);
    if (remaining <= 0) return res.status(403).json({ detail: `Email limit reached (${user.emails_used}/${user.email_limit})` });
    if (contactCount > remaining) return res.status(403).json({ detail: `Campaign has ${contactCount} recipients but only ${remaining} remaining.` });

    await campaign.update({ status: 'running', started_at: new Date() });

    // Start sending in background
    sendCampaignEmails(campaign.id, user.id);

    res.json({ message: 'Campaign started', campaign_id: campaign.id, started: true });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Pause
router.post('/:id/pause', async (req, res) => {
  const campaign = await Campaign.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!campaign) return res.status(404).json({ detail: 'Not found' });
  await campaign.update({ status: 'paused' });
  res.json({ message: 'Campaign paused', paused: true, campaign_id: campaign.id });
});

// Resume
router.post('/:id/resume', async (req, res) => {
  const campaign = await Campaign.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!campaign) return res.status(404).json({ detail: 'Not found' });
  await campaign.update({ status: 'running' });
  sendCampaignEmails(campaign.id, req.user.id);
  res.json({ message: 'Campaign resumed', resumed: true, campaign_id: campaign.id });
});

// Stop
router.post('/:id/stop', async (req, res) => {
  const campaign = await Campaign.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!campaign) return res.status(404).json({ detail: 'Not found' });
  await campaign.update({ status: 'completed', completed_at: new Date() });
  res.json({ message: 'Campaign stopped', stopped: true, campaign_id: campaign.id });
});

// Progress
router.get('/:id/progress', async (req, res) => {
  const campaign = await Campaign.findOne({ where: { id: req.params.id } });
  if (!campaign) return res.status(404).json({ detail: 'Not found' });

  const pending = await Contact.count({ where: { campaign_id: campaign.id } }) - (campaign.sent_count || 0) - (campaign.failed_count || 0);
  const progressPct = campaign.total_emails > 0 ? (((campaign.sent_count || 0) + (campaign.failed_count || 0)) / campaign.total_emails * 100) : 0;

  res.json({
    campaign_id: campaign.id, campaign_name: campaign.campaign_name,
    status: campaign.status, total: campaign.total_emails || 0,
    sent: campaign.sent_count || 0, delivered: campaign.delivered_count || 0,
    failed: campaign.failed_count || 0, pending: Math.max(0, pending),
    progress_pct: Math.round(progressPct * 100) / 100,
    is_running: campaign.status === 'running', is_paused: campaign.status === 'paused',
    started_at: campaign.started_at, completed_at: campaign.completed_at
  });
});

// Get single campaign
router.get('/:id', async (req, res) => {
  const campaign = await Campaign.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!campaign) return res.status(404).json({ detail: 'Not found' });
  res.json(campaign);
});

// Progress all
router.get('/progress/all', async (req, res) => {
  const campaigns = await Campaign.findAll({ where: { user_id: req.user.id, status: ['running', 'paused'] } });
  res.json({ active_count: campaigns.filter(c => c.status === 'running').length, paused_count: campaigns.filter(c => c.status === 'paused').length, campaigns });
});

module.exports = router;
