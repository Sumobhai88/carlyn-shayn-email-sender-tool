const User = require('./User');
const Campaign = require('./Campaign');
const Contact = require('./Contact');
const EmailLog = require('./EmailLog');
const SmtpProfile = require('./SmtpProfile');
const Template = require('./Template');
const Notification = require('./Notification');

// Associations
Campaign.belongsTo(User, { foreignKey: 'user_id' });
Campaign.hasMany(Contact, { foreignKey: 'campaign_id', onDelete: 'CASCADE' });
Campaign.hasMany(EmailLog, { foreignKey: 'campaign_id', onDelete: 'CASCADE' });
Contact.belongsTo(Campaign, { foreignKey: 'campaign_id' });
EmailLog.belongsTo(Campaign, { foreignKey: 'campaign_id' });
EmailLog.belongsTo(Contact, { foreignKey: 'contact_id' });
SmtpProfile.belongsTo(User, { foreignKey: 'user_id' });
Template.belongsTo(User, { foreignKey: 'user_id' });
Notification.belongsTo(User, { foreignKey: 'user_id' });

module.exports = { User, Campaign, Contact, EmailLog, SmtpProfile, Template, Notification };
