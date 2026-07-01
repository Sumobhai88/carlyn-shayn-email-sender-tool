const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const User = sequelize.define('User', {
  id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  email: { type: DataTypes.STRING, unique: true, allowNull: false },
  name: { type: DataTypes.STRING },
  picture: { type: DataTypes.TEXT },
  google_id: { type: DataTypes.STRING, unique: true, allowNull: false },
  is_active: { type: DataTypes.BOOLEAN, defaultValue: true },
  is_superuser: { type: DataTypes.BOOLEAN, defaultValue: false },
  company_name: { type: DataTypes.STRING },
  notif_email: { type: DataTypes.BOOLEAN, defaultValue: true },
  notif_campaigns: { type: DataTypes.BOOLEAN, defaultValue: true },
  email_limit: { type: DataTypes.INTEGER, defaultValue: 1000 },
  emails_used: { type: DataTypes.INTEGER, defaultValue: 0 },
  is_blocked: { type: DataTypes.BOOLEAN, defaultValue: false },
  last_login: { type: DataTypes.DATE, defaultValue: DataTypes.NOW }
}, { tableName: 'users' });

module.exports = User;
