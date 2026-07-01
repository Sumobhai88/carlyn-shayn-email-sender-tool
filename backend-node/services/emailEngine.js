const nodemailer = require('nodemailer');
const { v4: uuidv4 } = require('uuid');
const { Campaign, Contact, EmailLog, SmtpProfile, User, Notification } = require('../models');

// Active campaigns (for pause/stop)
const activeCampaigns = new Map();

function personalize(template, contact) {
  return template
    .replace(/\{\{?first_name\}?\}/g, contact.first_name || '')
    .replace(/\{\{?last_name\}?\}/g, contact.last_name || '')
    .replace(/\{\{?email\}?\}/g, contact.email || '')
    .replace(/\{\{?phone\}?\}/g, contact.phone || '')
    .replace(/\{\{?company\}?\}/g, contact.company || '');
}

async function sendCampaignEmails(campaignId, userId) {
  activeCampaigns.set(campaignId, 'running');

  try {
    const campaign = await Campaign.findByPk(campaignId);
    if (!campaign) return;

    // Get active SMTP profile
    const smtp = await SmtpProfile.findOne({ where: { user_id: userId, is_active: true } });
    if (!smtp) {
      await campaign.update({ status: 'failed' });
      return;
    }

    // Create transporter
    const transporter = nodemailer.createTransport({
      host: smtp.smtp_host,
      port: smtp.smtp_port,
      secure: smtp.smtp_port === 465,
      auth: { user: smtp.username, pass: smtp.password },
      tls: { rejectUnauthorized: false }
    });

    // Get unsent contacts
    const sentContactIds = (await EmailLog.findAll({
      where: { campaign_id: campaignId, delivery_status: ['sent', 'delivered'] },
      attributes: ['contact_id']
    })).map(l => l.contact_id);

    const contacts = await Contact.findAll({
      where: { campaign_id: campaignId, id: { [require('sequelize').Op.notIn]: sentContactIds } }
    });

    for (const contact of contacts) {
      // Check if paused/stopped
      const state = activeCampaigns.get(campaignId);
      if (state !== 'running') break;

      // Refresh campaign status from DB
      const freshCampaign = await Campaign.findByPk(campaignId);
      if (freshCampaign.status !== 'running') break;

      const trackingId = uuidv4();
      const subject = personalize(campaign.subject, contact);
      let htmlBody = personalize(campaign.template, contact).replace(/\n/g, '<br>');

      // Add tracking pixel
      const backendUrl = process.env.BACKEND_URL || `http://localhost:${process.env.PORT || 3001}`;
      htmlBody += `<br><br><div style="font-size:12px;color:#666;border-top:1px solid #ddd;padding-top:10px;margin-top:20px;">`;
      htmlBody += `<a href="${backendUrl}/api/v1/unsubscribe/${trackingId}">Unsubscribe</a>`;
      htmlBody += `</div>`;
      htmlBody += `<img src="${backendUrl}/api/v1/tracking/open/${trackingId}" width="1" height="1" style="display:none"/>`;

      // Create log entry
      const log = await EmailLog.create({
        campaign_id: campaignId, contact_id: contact.id,
        recipient_email: contact.email, subject, body: htmlBody,
        tracking_id: trackingId, delivery_status: 'pending'
      });

      try {
        await transporter.sendMail({
          from: `"${smtp.sender_name}" <${smtp.sender_email}>`,
          to: contact.email,
          subject,
          html: htmlBody,
          text: personalize(campaign.template, contact)
        });

        await log.update({ delivery_status: 'delivered', sent_at: new Date(), delivered_at: new Date() });
        await campaign.increment(['sent_count', 'delivered_count']);
        await User.increment('emails_used', { where: { id: userId } });
      } catch (sendErr) {
        await log.update({ delivery_status: 'failed', error_message: sendErr.message });
        await campaign.increment('failed_count');
      }

      // Small delay between emails (1-2 seconds)
      await new Promise(r => setTimeout(r, 1000 + Math.random() * 1000));
    }

    // Mark complete
    const finalCampaign = await Campaign.findByPk(campaignId);
    if (finalCampaign.status === 'running') {
      await finalCampaign.update({ status: 'completed', completed_at: new Date() });

      // Create notification
      await Notification.create({
        user_id: userId, type: 'success',
        title: 'Campaign Completed',
        message: `'${campaign.campaign_name}' — ${finalCampaign.sent_count} emails sent.`,
        campaign_id: campaignId
      });
    }
  } catch (err) {
    console.error('[EmailEngine] Error:', err.message);
    await Campaign.update({ status: 'failed' }, { where: { id: campaignId } });
  } finally {
    activeCampaigns.delete(campaignId);
  }
}

module.exports = { sendCampaignEmails, activeCampaigns };
