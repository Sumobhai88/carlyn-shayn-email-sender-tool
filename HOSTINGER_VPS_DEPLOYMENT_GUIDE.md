# 🚀 Hostinger VPS Deployment Guide - Complete Step by Step

## 📋 Table of Contents
1. [VPS Setup](#1-vps-setup)
2. [Install Dependencies](#2-install-dependencies)
3. [Backend Deployment](#3-backend-deployment)
4. [Frontend Deployment](#4-frontend-deployment)
5. [Domain & SSL Setup](#5-domain--ssl-setup)
6. [Process Management](#6-process-management)
7. [Troubleshooting](#7-troubleshooting)

---

## 🎯 Overview

**Tech Stack:**
- Frontend: React + Vite
- Backend: FastAPI (Python)
- Database: SQLite
- Server: Hostinger VPS (Ubuntu)

**Deployment Strategy:**
- Backend: FastAPI with Uvicorn + Nginx reverse proxy
- Frontend: Static build served by Nginx
- Process Manager: PM2 or systemd
- SSL: Let's Encrypt (Certbot)

---

## 1. VPS Setup

### Step 1.1: Connect to VPS
```bash
# SSH into your VPS
ssh root@your-vps-ip

# Or if you have username
ssh username@your-vps-ip
```

### Step 1.2: Update System
```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git build-essential software-properties-common
```

### Step 1.3: Create App User (Optional but Recommended)
```bash
# Create user for app
sudo adduser emailapp

# Add to sudo group
sudo usermod -aG sudo emailapp

# Switch to new user
su - emailapp
```

---

## 2. Install Dependencies

### Step 2.1: Install Python 3.11+
```bash
# Add deadsnakes PPA (if needed)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify installation
python3.11 --version
```

### Step 2.2: Install Node.js 18+
```bash
# Install Node.js using NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

### Step 2.3: Install Nginx
```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 2.4: Install PM2 (Process Manager)
```bash
# Install PM2 globally
sudo npm install -g pm2

# Verify installation
pm2 --version
```

---

## 3. Backend Deployment

### Step 3.1: Clone Repository
```bash
# Create app directory
sudo mkdir -p /var/www/emailapp
sudo chown -R $USER:$USER /var/www/emailapp

# Clone your repository
cd /var/www/emailapp
git clone <your-repo-url> .

# Or upload files via SFTP/SCP
```

### Step 3.2: Setup Python Virtual Environment
```bash
# Navigate to backend
cd /var/www/emailapp/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3.3: Configure Backend
```bash
# Create .env file
nano .env

# Add these configurations:
```

**backend/.env:**
```env
# Database
DATABASE_URL=sqlite:///./carlyn_shayn.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
RELOAD=false

# CORS Origins (add your domain)
CORS_ORIGINS=["http://localhost:3000","http://your-domain.com","https://your-domain.com"]

# Email Settings (if needed)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
SECRET_KEY=your-super-secret-key-here-change-this
```

### Step 3.4: Initialize Database
```bash
# Still in backend directory with venv activated
python init_db.py

# Verify database created
ls -la *.db
```

### Step 3.5: Test Backend
```bash
# Run backend manually to test
python run.py

# In another terminal, test API
curl http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/

# If working, stop it (Ctrl+C)
```

### Step 3.6: Setup PM2 for Backend
```bash
# Create PM2 ecosystem file
nano /var/www/emailapp/backend/ecosystem.config.js
```

**backend/ecosystem.config.js:**
```javascript
module.exports = {
  apps: [{
    name: 'emailapp-backend',
    script: 'venv/bin/python',
    args: 'run.py',
    cwd: '/var/www/emailapp/backend',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 8000
    },
    error_file: './logs/error.log',
    out_file: './logs/output.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
```

```bash
# Create logs directory
mkdir -p /var/www/emailapp/backend/logs

# Start backend with PM2
cd /var/www/emailapp/backend
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs emailapp-backend

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Run the command it outputs (usually starts with sudo)
```

---

## 4. Frontend Deployment

### Step 4.1: Build Frontend
```bash
# Navigate to frontend root
cd /var/www/emailapp

# Install dependencies
npm install

# Create production .env file
nano .env.production
```

**.env.production:**
```env
VITE_API_URL=https://your-domain.com/api
```

```bash
# Build for production
npm run build

# This creates a 'dist' folder with static files
ls -la dist/
```

### Step 4.2: Move Build to Nginx Directory
```bash
# Create nginx web directory
sudo mkdir -p /var/www/emailapp/html

# Copy build files
sudo cp -r dist/* /var/www/emailapp/html/

# Set permissions
sudo chown -R www-data:www-data /var/www/emailapp/html
sudo chmod -R 755 /var/www/emailapp/html
```

---

## 5. Domain & SSL Setup

### Step 5.1: Configure Nginx
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/emailapp
```

**/etc/nginx/sites-available/emailapp:**
```nginx
# Backend API Server
upstream backend_api {
    server 127.0.0.1:8000;
}

# HTTP Server (will redirect to HTTPS)
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf;
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Root directory for frontend
    root /var/www/emailapp/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # API Proxy
    location /api {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Frontend - React Router (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/emailapp /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 5.2: Update Frontend API URL
```bash
# Update the API URL in built files (if hardcoded)
cd /var/www/emailapp

# Rebuild with production API URL
VITE_API_URL=https://your-domain.com/api npm run build

# Copy to nginx directory
sudo cp -r dist/* /var/www/emailapp/html/
```

### Step 5.3: Point Domain to VPS
```
In your domain registrar (Hostinger/Godaddy/etc):

1. Go to DNS settings
2. Add/Update A Record:
   - Type: A
   - Name: @ (for root domain)
   - Value: YOUR_VPS_IP
   - TTL: 3600

3. Add/Update A Record for www:
   - Type: A
   - Name: www
   - Value: YOUR_VPS_IP
   - TTL: 3600

Wait 5-30 minutes for DNS propagation
```

### Step 5.4: Install SSL Certificate
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Enter your email when prompted
# Agree to terms
# Choose redirect HTTP to HTTPS (option 2)

# Test auto-renewal
sudo certbot renew --dry-run

# Certificate will auto-renew
```

---

## 6. Process Management

### PM2 Commands
```bash
# View all processes
pm2 list

# View logs
pm2 logs emailapp-backend

# Restart backend
pm2 restart emailapp-backend

# Stop backend
pm2 stop emailapp-backend

# Delete process
pm2 delete emailapp-backend

# Monitor
pm2 monit

# Save process list
pm2 save

# View startup script
pm2 startup
```

### Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload (without downtime)
sudo nginx -s reload

# Restart
sudo systemctl restart nginx

# Stop
sudo systemctl stop nginx

# Start
sudo systemctl start nginx

# Status
sudo systemctl status nginx
```

### System Service Commands
```bash
# View all running services
systemctl list-units --type=service --state=running

# Check logs
sudo journalctl -u nginx -f
```

---

## 7. Troubleshooting

### Issue 1: Backend Not Starting
```bash
# Check logs
pm2 logs emailapp-backend

# Test manually
cd /var/www/emailapp/backend
source venv/bin/activate
python run.py

# Check port
sudo netstat -tlnp | grep 8000
```

### Issue 2: Nginx 502 Bad Gateway
```bash
# Check backend is running
pm2 status

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check if port 8000 is accessible
curl http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/
```

### Issue 3: Frontend Not Loading
```bash
# Check Nginx is serving files
ls -la /var/www/emailapp/html/

# Check Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Test configuration
sudo nginx -t
```

### Issue 4: CORS Errors
```bash
# Update backend .env
nano /var/www/emailapp/backend/.env

# Add your domain to CORS_ORIGINS
CORS_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# Restart backend
pm2 restart emailapp-backend
```

### Issue 5: SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check Nginx SSL config
sudo nano /etc/nginx/sites-available/emailapp
```

### Issue 6: Database Issues
```bash
# Check database file permissions
ls -la /var/www/emailapp/backend/*.db

# Fix permissions if needed
sudo chown emailapp:emailapp /var/www/emailapp/backend/*.db
sudo chmod 644 /var/www/emailapp/backend/*.db
```

---

## 8. Maintenance

### Update Application
```bash
# Pull latest code
cd /var/www/emailapp
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart emailapp-backend

# Update frontend
cd /var/www/emailapp
npm install
npm run build
sudo cp -r dist/* /var/www/emailapp/html/
```

### Backup Database
```bash
# Create backup script
nano /var/www/emailapp/backup.sh
```

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/var/www/emailapp/backups"
DB_FILE="/var/www/emailapp/backend/carlyn_shayn.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/db_backup_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "db_backup_*.db" -mtime +7 -delete
```

```bash
# Make executable
chmod +x /var/www/emailapp/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add this line:
0 2 * * * /var/www/emailapp/backup.sh
```

### Monitor Logs
```bash
# Backend logs
pm2 logs emailapp-backend --lines 100

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -xe
```

---

## 9. Security Checklist

- [ ] Firewall configured (UFW)
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```

- [ ] SSH key authentication enabled
- [ ] Root login disabled
- [ ] SSL certificate installed
- [ ] Database file permissions set correctly
- [ ] Strong passwords used
- [ ] Regular backups scheduled
- [ ] PM2 process monitoring enabled
- [ ] Nginx security headers configured
- [ ] CORS properly configured
- [ ] Environment variables secured

---

## 10. Quick Reference

### File Locations
```
Application Root: /var/www/emailapp
Backend: /var/www/emailapp/backend
Frontend Build: /var/www/emailapp/html
Nginx Config: /etc/nginx/sites-available/emailapp
Backend Logs: /var/www/emailapp/backend/logs
Nginx Logs: /var/log/nginx/
Database: /var/www/emailapp/backend/carlyn_shayn.db
```

### Important Commands
```bash
# Restart everything
pm2 restart emailapp-backend
sudo systemctl restart nginx

# View logs
pm2 logs emailapp-backend
sudo tail -f /var/log/nginx/error.log

# Check status
pm2 status
sudo systemctl status nginx

# Update app
cd /var/www/emailapp && git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt
pm2 restart emailapp-backend
cd .. && npm run build && sudo cp -r dist/* html/
```

---

## 11. Post-Deployment Testing

### Test Checklist
```bash
# 1. Test API directly
curl https://your-domain.com/api/v1/campaigns/

# 2. Test frontend loads
curl https://your-domain.com/

# 3. Test from browser
# Open: https://your-domain.com
# - Check if login works
# - Check if dashboard loads
# - Test email sending
# - Check analytics page

# 4. Check SSL
curl -I https://your-domain.com/

# 5. Check logs for errors
pm2 logs emailapp-backend --lines 50
sudo tail -n 50 /var/log/nginx/error.log
```

---

## 📞 Support

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Backend not running - `pm2 restart emailapp-backend` |
| CORS Error | Update CORS_ORIGINS in backend .env |
| SSL not working | Re-run certbot: `sudo certbot --nginx` |
| Database locked | Stop backend, delete .db-shm and .db-wal files |
| Permission denied | Fix ownership: `sudo chown -R $USER:$USER /var/www/emailapp` |

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Code tested locally
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Frontend build successful
- [ ] API endpoints documented

### Deployment
- [ ] VPS access confirmed
- [ ] Dependencies installed
- [ ] Backend deployed and running
- [ ] Frontend built and deployed
- [ ] Nginx configured
- [ ] Domain pointed to VPS
- [ ] SSL certificate installed

### Post-Deployment
- [ ] Application accessible via domain
- [ ] SSL working (HTTPS)
- [ ] API responding correctly
- [ ] Frontend loading properly
- [ ] Email sending working
- [ ] Logs monitored
- [ ] Backup configured
- [ ] PM2 startup enabled

---

**🎉 Congratulations! Your app is now live on Hostinger VPS! 🚀**

**Access your app at:** https://your-domain.com

**API Docs:** https://your-domain.com/api/docs
