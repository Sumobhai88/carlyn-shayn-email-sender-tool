const router = require('express').Router();
const nodemailer = require('nodemailer');
const { authenticate } = require('../middleware/auth');
const { SmtpProfile } = require('../models');

router.use(authenticate);

router.get('/', async (req, res) => {
  const profiles = await SmtpProfile.findAll({ where: { user_id: req.user.id }, order: [['created_at', 'DESC']] });
  res.json(profiles);
});

router.post('/', async (req, res) => {
  try {
    const existing = await SmtpProfile.findOne({ where: { user_id: req.user.id, profile_name: req.body.profile_name } });
    if (existing) return res.status(400).json({ detail: `Profile '${req.body.profile_name}' already exists` });

    const profile = await SmtpProfile.create({ ...req.body, user_id: req.user.id });
    res.status(201).json(profile);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

router.put('/:id', async (req, res) => {
  const profile = await SmtpProfile.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!profile) return res.status(404).json({ detail: 'Not found' });
  await profile.update(req.body);
  res.json(profile);
});

router.delete('/:id', async (req, res) => {
  const profile = await SmtpProfile.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!profile) return res.status(404).json({ detail: 'Not found' });
  if (profile.is_active) return res.status(400).json({ detail: 'Cannot delete active profile' });
  await profile.destroy();
  res.status(204).send();
});

router.post('/:id/set-active', async (req, res) => {
  await SmtpProfile.update({ is_active: false }, { where: { user_id: req.user.id } });
  const profile = await SmtpProfile.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!profile) return res.status(404).json({ detail: 'Not found' });
  await profile.update({ is_active: true });
  res.json(profile);
});

router.post('/:id/test', async (req, res) => {
  const profile = await SmtpProfile.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!profile) return res.status(404).json({ detail: 'Not found' });

  try {
    const transporter = nodemailer.createTransport({
      host: profile.smtp_host, port: profile.smtp_port,
      secure: profile.smtp_port === 465,
      auth: { user: profile.username, pass: profile.password },
      tls: { rejectUnauthorized: false }
    });
    await transporter.verify();
    await profile.update({ status: 'connected' });
    res.json({ success: true, message: 'Connection successful', status: 'connected', profile_id: profile.id });
  } catch (err) {
    await profile.update({ status: 'failed' });
    res.json({ success: false, message: err.message, status: 'failed', profile_id: profile.id, error_details: err.message });
  }
});

module.exports = router;
