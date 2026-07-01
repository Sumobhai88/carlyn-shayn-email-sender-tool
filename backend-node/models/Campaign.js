const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Campaign = sequelize.define('Campaign', {
  id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  user_id: { type: DataTypes.INTEGER, allowNull: true },
  campaign_name: { type: DataTypes.STRING(200), allowNull: false },
  subject: { type: DataTypes.STRING(500), allowNull: false },
  template: { type: DataTypes.TEXT, allowNull: false },
  status: { type: DataTypes.ENUM('draft', 'scheduled', 'running', 'paused', 'completed', 'failed'), defaultValue: 'draft' },
  total_emails: { type: DataTypes.INTEGER, defaultValue: 0 },
  sent_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  delivered_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  failed_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  opened_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  bounced_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  unsubscribed_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  started_at: { type: DataTypes.DATE },
  completed_at: { type: DataTypes.DATE }
}, { tableName: 'campaigns' });

module.exports = Campaign;
