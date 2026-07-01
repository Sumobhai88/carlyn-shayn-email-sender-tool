const { Sequelize } = require('sequelize');
const path = require('path');

let sequelize;

if (process.env.DB_HOST && process.env.DB_NAME && process.env.NODE_ENV === 'production') {
  // Production: MySQL (Hostinger)
  sequelize = new Sequelize(
    process.env.DB_NAME,
    process.env.DB_USER || 'root',
    process.env.DB_PASS || '',
    {
      host: process.env.DB_HOST,
      port: process.env.DB_PORT || 3306,
      dialect: 'mysql',
      logging: false,
      pool: { max: 10, min: 0, acquire: 30000, idle: 10000 },
      define: { timestamps: true, underscored: true }
    }
  );
} else {
  // Local development: SQLite
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: path.join(__dirname, '..', 'database.sqlite'),
    logging: false,
    define: { timestamps: true, underscored: true }
  });
}

async function syncDatabase() {
  // SQLite doesn't handle alter well with FKs — use force for fresh DB
  const fs = require('fs');
  const dbPath = path.join(__dirname, '..', 'database.sqlite');
  const isNewDb = !fs.existsSync(dbPath) || fs.statSync(dbPath).size === 0;
  
  if (isNewDb || process.env.DB_FORCE_SYNC === 'true') {
    await sequelize.sync({ force: true });
  } else {
    await sequelize.sync();
  }
}

module.exports = { sequelize, syncDatabase };
