const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const SmtpProfile = sequelize.define('SmtpProfile', {
  id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  user_id: { type: DataTypes.INTEGER, allowNull: true },
  profile_name: { type: DataTypes.STRING(100), allowNull: false },
  sender_name: { type: DataTypes.STRING(200), allowNull: false },
  sender_email: { type: DataTypes.STRING(255), allowNull: false },
  smtp_host: { type: DataTypes.STRING(255), allowNull: false },
  smtp_port: { type: DataTypes.INTEGER, allowNull: false },
  username: { type: DataTypes.STRING(255), allowNull: false },
  password: { type: DataTypes.TEXT, allowNull: false },
  tls_enabled: { type: DataTypes.BOOLEAN, defaultValue: true },
  is_active: { type: DataTypes.BOOLEAN, defaultValue: false },
  status: { type: DataTypes.STRING(20), defaultValue: 'connected' }
}, { tableName: 'smtp_profiles' });

module.exports = SmtpProfile;
