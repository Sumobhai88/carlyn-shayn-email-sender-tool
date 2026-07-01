const router = require('express').Router();
const { authenticate } = require('../middleware/auth');
const { EmailLog, Campaign, Contact } = require('../models');
const { Op } = require('sequelize');

router.use(authenticate);

router.get('/email-logs', async (req, res) => {
  try {
    const { format = 'csv', status, campaign_id } = req.query;
    const campaigns = await Campaign.findAll({ where: { user_id: req.user.id }, attributes: ['id', 'campaign_name'] });
    const campaignIds = campaigns.map(c => c.id);
    const campaignMap = Object.fromEntries(campaigns.map(c => [c.id, c.campaign_name]));

    const where = { campaign_id: { [Op.in]: campaignIds } };
    if (status && status !== 'all') {
      if (status === 'opened') where.opened = true;
      else if (status === 'bounced') where.bounced = true;
      else where.delivery_status = status;
    }
    if (campaign_id) where.campaign_id = parseInt(campaign_id);

    const logs = await EmailLog.findAll({ where, include: [{ model: Contact, attributes: ['first_name', 'last_name'] }] });

    let csv = 'Email,First Name,Last Name,Campaign,Subject,Status,Sent At,Opened\n';
    for (const l of logs) {
      const name1 = l.Contact ? l.Contact.first_name : '';
      const name2 = l.Contact ? l.Contact.last_name : '';
      csv += `"${l.recipient_email}","${name1}","${name2}","${campaignMap[l.campaign_id] || ''}","${l.subject}","${l.delivery_status}","${l.sent_at || ''}","${l.opened}"\n`;
    }

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=email-logs.csv');
    res.send(csv);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Category-based exports
['delivered', 'opened', 'bounced', 'unsubscribed', 'all'].forEach(category => {
  router.get(`/${category}`, async (req, res) => {
    try {
      const campaigns = await Campaign.findAll({ where: { user_id: req.user.id }, attributes: ['id', 'campaign_name'] });
      const campaignIds = campaigns.map(c => c.id);
      const campaignMap = Object.fromEntries(campaigns.map(c => [c.id, c.campaign_name]));

      const where = { campaign_id: { [Op.in]: campaignIds } };
      if (category === 'delivered') where.delivery_status = 'delivered';
      if (category === 'opened') where.opened = true;
      if (category === 'bounced') where.bounced = true;
      if (category === 'unsubscribed') where.unsubscribed = true;

      const logs = await EmailLog.findAll({ where, include: [{ model: Contact, attributes: ['first_name', 'last_name'] }] });

      let csv = 'Email,First Name,Last Name,Campaign,Subject,Status,Sent At\n';
      for (const l of logs) {
        csv += `"${l.recipient_email}","${l.Contact?.first_name || ''}","${l.Contact?.last_name || ''}","${campaignMap[l.campaign_id] || ''}","${l.subject}","${l.delivery_status}","${l.sent_at || ''}"\n`;
      }

      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename=${category}-emails.csv`);
      res.send(csv);
    } catch (err) {
      res.status(500).json({ detail: err.message });
    }
  });
});

module.exports = router;
