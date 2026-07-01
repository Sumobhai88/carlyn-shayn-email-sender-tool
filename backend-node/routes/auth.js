const router = require('express').Router();
const jwt = require('jsonwebtoken');
const { OAuth2Client } = require('google-auth-library');
const { User } = require('../models');
const { authenticate } = require('../middleware/auth');

const googleClient = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

router.post('/google', async (req, res) => {
  try {
    const { token } = req.body;
    const ticket = await googleClient.verifyIdToken({
      idToken: token,
      audience: process.env.GOOGLE_CLIENT_ID
    });
    const payload = ticket.getPayload();

    let user = await User.findOne({ where: { google_id: payload.sub } });

    if (user) {
      user.last_login = new Date();
      user.name = payload.name;
      user.picture = payload.picture;
      await user.save();
    } else {
      // First user becomes admin automatically
      const userCount = await User.count();
      user = await User.create({
        google_id: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
        is_superuser: userCount === 0  // First user = admin
      });
    }

    if (user.is_blocked || !user.is_active) {
      return res.status(403).json({ detail: 'Account disabled' });
    }

    const accessToken = jwt.sign(
      { userId: user.id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    res.json({
      access_token: accessToken,
      token_type: 'bearer',
      user: {
        id: user.id, email: user.email, name: user.name,
        picture: user.picture, google_id: user.google_id,
        is_active: user.is_active, is_superuser: user.is_superuser,
        email_limit: user.email_limit || 1000,
        emails_used: user.emails_used || 0,
        is_blocked: user.is_blocked || false,
        created_at: user.createdAt, last_login: user.last_login
      }
    });
  } catch (err) {
    console.error('Google auth error:', err.message);
    res.status(401).json({ detail: 'Invalid Google token' });
  }
});

router.get('/me', authenticate, (req, res) => {
  const u = req.user;
  res.json({
    id: u.id, email: u.email, name: u.name, picture: u.picture,
    google_id: u.google_id, is_active: u.is_active,
    is_superuser: u.is_superuser, email_limit: u.email_limit || 1000,
    emails_used: u.emails_used || 0, is_blocked: u.is_blocked || false,
    created_at: u.createdAt, last_login: u.last_login
  });
});

router.post('/logout', (req, res) => {
  res.json({ message: 'Successfully logged out' });
});

module.exports = router;
