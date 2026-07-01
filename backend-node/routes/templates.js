const router = require('express').Router();
const { authenticate } = require('../middleware/auth');
const { Template } = require('../models');

router.use(authenticate);

router.get('/', async (req, res) => {
  const templates = await Template.findAll({ where: { user_id: req.user.id }, order: [['created_at', 'DESC']] });
  res.json({ templates, total: templates.length });
});

router.post('/', async (req, res) => {
  try {
    const t = await Template.create({ ...req.body, user_id: req.user.id });
    res.status(201).json(t);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

router.put('/:id', async (req, res) => {
  const t = await Template.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!t) return res.status(404).json({ detail: 'Not found' });
  await t.update(req.body);
  res.json(t);
});

router.delete('/:id', async (req, res) => {
  const t = await Template.findOne({ where: { id: req.params.id, user_id: req.user.id } });
  if (!t) return res.status(404).json({ detail: 'Not found' });
  await t.destroy();
  res.status(204).send();
});

module.exports = router;
