const router = require('express').Router();
const { EmailLog } = require('../models');

// 1x1 transparent GIF
const PIXEL = Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64');

router.get('/open/:trackingId', async (req, res) => {
  try {
    const log = await EmailLog.findOne({ where: { tracking_id: req.params.trackingId } });
    if (log) {
      await log.update({ opened: true, opened_at: log.opened_at || new Date(), open_count: (log.open_count || 0) + 1 });
    }
  } catch (e) { /* ignore */ }

  res.set({ 'Content-Type': 'image/gif', 'Cache-Control': 'no-store' });
  res.send(PIXEL);
});

module.exports = router;
