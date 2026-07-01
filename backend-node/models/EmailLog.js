const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const EmailLog = sequelize.define('EmailLog', {
  id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  campaign_id: { type: DataTypes.INTEGER, allowNull: false },
  contact_id: { type: DataTypes.INTEGER, allowNull: false },
  recipient_email: { type: DataTypes.STRING(255), allowNull: false },
  subject: { type: DataTypes.STRING(500), allowNull: false },
  body: { type: DataTypes.TEXT, allowNull: false },
  delivery_status: { type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed', 'bounced'), defaultValue: 'pending' },
  opened: { type: DataTypes.BOOLEAN, defaultValue: false },
  bounced: { type: DataTypes.BOOLEAN, defaultValue: false },
  unsubscribed: { type: DataTypes.BOOLEAN, defaultValue: false },
  error_message: { type: DataTypes.TEXT },
  tracking_id: { type: DataTypes.STRING(100), unique: true },
  open_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  sent_at: { type: DataTypes.DATE },
  delivered_at: { type: DataTypes.DATE },
  opened_at: { type: DataTypes.DATE },
  bounced_at: { type: DataTypes.DATE }
}, { tableName: 'email_logs' });

module.exports = EmailLog;
