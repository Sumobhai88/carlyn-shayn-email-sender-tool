require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { sequelize, syncDatabase } = require('./config/database');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || '*',
  credentials: true
}));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// API Routes
app.use('/api/v1/auth', require('./routes/auth'));
app.use('/api/v1/campaigns', require('./routes/campaigns'));
app.use('/api/v1/smtp-profiles', require('./routes/smtpProfiles'));
app.use('/api/v1/templates', require('./routes/templates'));
app.use('/api/v1/analytics', require('./routes/analytics'));
app.use('/api/v1/exports', require('./routes/exports'));
app.use('/api/v1/settings', require('./routes/settings'));
app.use('/api/v1/admin', require('./routes/admin'));
app.use('/api/v1/tracking', require('./routes/tracking'));
app.use('/api/v1/unsubscribe', require('./routes/unsubscribe'));

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Serve React frontend (production)
const publicPath = path.join(__dirname, 'public');
app.use(express.static(publicPath));

// SPA fallback — all non-API routes serve index.html
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api/')) {
    res.sendFile(path.join(publicPath, 'index.html'));
  } else {
    res.status(404).json({ detail: 'API endpoint not found' });
  }
});

// Start server
async function start() {
  try {
    await sequelize.authenticate();
    console.log('✓ Database connected');
    await syncDatabase();
    console.log('✓ Tables synced');
    app.listen(PORT, () => {
      console.log(`✓ Server running on port ${PORT}`);
    });
  } catch (err) {
    console.error('✗ Failed to start:', err.message);
    process.exit(1);
  }
}

start();
