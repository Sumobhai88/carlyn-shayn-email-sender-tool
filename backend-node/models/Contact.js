const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Contact = sequelize.define('Contact', {
  id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  campaign_id: { type: DataTypes.INTEGER, allowNull: false },
  first_name: { type: DataTypes.STRING(100), allowNull: false },
  last_name: { type: DataTypes.STRING(100), allowNull: false },
  email: { type: DataTypes.STRING(255), allowNull: false },
  phone: { type: DataTypes.STRING(20) },
  company: { type: DataTypes.STRING(200) },
  unsubscribed: { type: DataTypes.BOOLEAN, defaultValue: false },
  unsubscribe_token: { type: DataTypes.STRING(64), unique: true }
}, { tableName: 'contacts' });

module.exports = Contact;
