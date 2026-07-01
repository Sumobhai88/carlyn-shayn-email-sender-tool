const router = require('express').Router();
const { EmailLog, Contact } = require('../models');

router.get('/:trackingId', async (req, res) => {
  try {
    const log = await EmailLog.findOne({ where: { tracking_id: req.params.trackingId } });
    if (log) {
      await log.update({ unsubscribed: true });
      const contact = await Contact.findByPk(log.contact_id);
      if (contact) await contact.update({ unsubscribed: true });
    }

    res.send(`
      <html>
      <body style="font-family:Arial;text-align:center;padding:50px">
        <h2>✓ Unsubscribed Successfully</h2>
        <p>You have been removed from our mailing list.</p>
        <p style="color:#666;font-size:12px">You will no longer receive emails from this campaign.</p>
      </body>
      </html>
    `);
  } catch (e) {
    res.status(500).send('Error processing request');
  }
});

module.exports = router;
