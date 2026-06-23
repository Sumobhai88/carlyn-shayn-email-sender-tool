# ⚡ Quick Deployment Steps - Hostinger VPS

## 🎯 Prerequisites
- Hostinger VPS running Ubuntu
- Domain name pointing to VPS IP
- SSH access to VPS
- Root or sudo access

---

## 📋 Super Quick Steps (30 Minutes)

### 1️⃣ Connect to VPS
```bash
ssh root@your-vps-ip
```

### 2️⃣ Run Setup Script
```bash
# Update system
apt update && apt upgrade -y

# Install all dependencies at once
apt install -y curl wget git build-essential python3.11 python3.11-venv python3-pip nodejs npm nginx certbot python3-certbot-nginx

# Install PM2
npm install -g pm2
```

### 3️⃣ Setup Application
```bash
# Create directory
mkdir -p /var/www/emailapp
cd /var/www/emailapp

# Upload your files OR clone from git
# Option A: Upload via SFTP/SCP to /var/www/emailapp
# Option B: Git clone
git clone <your-repo-url> .
```

### 4️⃣ Setup Backend
```bash
cd /var/www/emailapp/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.production.example .env
nano .env
# Update: SECRET_KEY, CORS_ORIGINS, SMTP settings

# Initialize database
python init_db.py

# Start with PM2
pm2 start "python run.py" --name emailapp-backend
pm2 save
pm2 startup  # Run the command it shows
```

### 5️⃣ Setup Frontend
```bash
cd /var/www/emailapp

# Install dependencies
npm install

# Create production env
echo "VITE_API_URL=https://your-domain.com/api" > .env.production

# Build
npm run build

# Copy to nginx
mkdir -p /var/www/emailapp/html
cp -r dist/* /var/www/emailapp/html/
chown -R www-data:www-data /var/www/emailapp/html
```

### 6️⃣ Setup Nginx
```bash
# Create config file
nano /etc/nginx/sites-available/emailapp
```

Paste this (replace `your-domain.com`):
```nginx
upstream backend_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    root /var/www/emailapp/html;
    index index.html;

    location /api {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/emailapp /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test and restart
nginx -t
systemctl restart nginx
```

### 7️⃣ Setup SSL
```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
# Follow prompts, choose redirect HTTP to HTTPS
```

### 8️⃣ Setup Firewall
```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

---

## ✅ Verify Deployment

### Check Services
```bash
# Backend status
pm2 status

# Nginx status
systemctl status nginx

# Check backend logs
pm2 logs emailapp-backend

# Check if API responds
curl http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/
```

### Test in Browser
```
1. Visit: https://your-domain.com
2. Check if app loads
3. Try login/dashboard
4. Test email sending
```

---

## 🔄 Update App (Future Updates)

Create this script: `/var/www/emailapp/update.sh`
```bash
#!/bin/bash
cd /var/www/emailapp

# Update code
git pull  # If using git

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart emailapp-backend

# Update frontend
cd ..
npm install
npm run build
cp -r dist/* html/

echo "✅ App updated!"
```

Make executable:
```bash
chmod +x /var/www/emailapp/update.sh
```

Run updates:
```bash
/var/www/emailapp/update.sh
```

---

## 🆘 Quick Troubleshooting

### Backend not working?
```bash
pm2 logs emailapp-backend
# Check for errors

pm2 restart emailapp-backend
# Restart it
```

### Frontend not loading?
```bash
ls -la /var/www/emailapp/html/
# Check files exist

tail -f /var/log/nginx/error.log
# Check nginx errors
```

### 502 Bad Gateway?
```bash
# Backend is down
pm2 restart emailapp-backend

# Check if backend is running on port 8000
netstat -tlnp | grep 8000
```

### CORS errors?
```bash
# Update backend .env
nano /var/www/emailapp/backend/.env

# Add your domain to CORS_ORIGINS
CORS_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# Restart
pm2 restart emailapp-backend
```

---

## 📞 Important Commands

```bash
# View all services
pm2 list

# View logs
pm2 logs emailapp-backend

# Restart backend
pm2 restart emailapp-backend

# Restart nginx
systemctl restart nginx

# Check nginx config
nginx -t

# Monitor backend
pm2 monit
```

---

## 🎉 Done!

Your app should now be live at: **https://your-domain.com**

API docs at: **https://your-domain.com/api/docs**

---

## 📚 Need More Details?

See `HOSTINGER_VPS_DEPLOYMENT_GUIDE.md` for:
- Detailed explanations
- Security setup
- Backup configuration
- Advanced troubleshooting
- Monitoring setup

---

## 🔐 Security Checklist

After deployment, make sure:
- [ ] Changed SECRET_KEY in backend .env
- [ ] SSL certificate installed (https working)
- [ ] Firewall enabled (ufw)
- [ ] Strong passwords used
- [ ] Root login disabled (optional but recommended)
- [ ] SSH key authentication enabled (optional)
- [ ] Regular backups scheduled

---

## 📊 Monitor Your App

```bash
# CPU/Memory usage
pm2 monit

# Check disk space
df -h

# Check memory
free -h

# Check active connections
netstat -an | grep :443 | wc -l
```

---

**Happy Deploying! 🚀**
