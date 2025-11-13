# 🚀 Deployment Quick Start Guide

## Essential Information for New Sessions

### 🔑 AWS Configuration

**IAM Role**: `arn:aws:iam::938611073268:role/stonkmarketanalyzer`

**SSH Key Location**: `/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem`

**EC2 Details**:
- IP: `100.27.225.93`
- Domain: `api.stonkmarketanalyzer.com`
- User: `ec2-user`
- Region: `us-east-1`

### 📦 Quick Deployment Commands

#### Deploy Backend Changes
```bash
# Upload files and restart backend
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/app.py \
  backend/analytics_comprehensive.py \
  backend/secure_portal.py \
  ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/

# Restart backend
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

#### Deploy Frontend Changes
```bash
# Build and deploy frontend
cd frontend
npm run build
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  -r dist/* ec2-user@100.27.225.93:/var/www/stonkmarketanalyzer/
```

#### Restart Backend (Simple)
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 \
  "cd /opt/stonkmarketanalyzer/backend && \
   pkill -9 -f 'python.*app.py' && \
   source venv/bin/activate && \
   nohup python3 app.py > backend.log 2>&1 &"
```

### 🌐 Important URLs

**Main App**: https://stonkmarketanalyzer.com  
**API**: https://api.stonkmarketanalyzer.com  
**Admin Portal**: https://api.stonkmarketanalyzer.com/portal/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg

### 🔐 Admin Portal Credentials

**Username**: `stonker_971805`  
**Password**: `StonkerBonker@12345millibilli$`  
**Portal Path**: `6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg`

### 📁 Key File Locations

#### On EC2 Server
- Backend: `/opt/stonkmarketanalyzer/backend/`
- Frontend: `/var/www/stonkmarketanalyzer/`
- Admin Portal: `/var/www/admin-portal/`
- Nginx Config: `/etc/nginx/conf.d/stonkmarketanalyzer.conf`
- Backend Logs: `/opt/stonkmarketanalyzer/backend/backend.log`
- Analytics Data: `/opt/stonkmarketanalyzer/backend/analytics_data/`

#### Local Project
- Backend: `./backend/`
- Frontend: `./frontend/`
- Deployment Scripts: `./deployment/`
- Admin Portal: `./admin-portal/`

### 🛠️ Common Tasks

#### Check Backend Status
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ps aux | grep 'python.*app.py' | grep -v grep"
```

#### View Backend Logs
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "tail -50 /opt/stonkmarketanalyzer/backend/backend.log"
```

#### Check Nginx Status
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "sudo systemctl status nginx"
```

#### Reload Nginx
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "sudo systemctl reload nginx"
```

### 🔧 Backend Dependencies

Required Python packages (already installed):
```
flask
flask-cors
python-dotenv
psutil
pyjwt
bcrypt
```

Install if missing:
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 \
  "cd /opt/stonkmarketanalyzer/backend && \
   source venv/bin/activate && \
   pip install psutil pyjwt bcrypt"
```

### 📊 Project Structure

```
stonkmarketanalyzer/
├── backend/
│   ├── app.py                          # Main Flask app
│   ├── analytics_comprehensive.py      # Analytics engine
│   ├── secure_portal.py                # Admin portal API
│   ├── auth_routes.py                  # Authentication routes
│   ├── auth_service.py                 # Auth service
│   ├── password_reset_service.py       # Password reset
│   ├── cache_enhanced.py               # Caching system
│   ├── .env                            # Environment variables
│   └── services/
│       ├── perplexity_service.py       # AI service
│       └── stock_price_service.py      # Stock data
├── frontend/
│   └── src/
│       ├── App.jsx                     # Main React app
│       └── components/                 # React components
├── admin-portal/
│   └── index.html                      # Admin dashboard
└── deployment/
    ├── deploy-admin-portal-ssh.sh      # Deploy admin portal
    ├── restart-backend-remote.sh       # Restart backend
    └── test-analytics.sh               # Generate test data
```

### 🚨 Troubleshooting

#### Backend Not Running
```bash
# Check logs
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "tail -100 /opt/stonkmarketanalyzer/backend/backend.log"

# Restart
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

#### Admin Portal Not Loading
```bash
# Check nginx
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "sudo nginx -t && sudo systemctl reload nginx"

# Check file exists
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ls -la /var/www/admin-portal/"
```

#### 404 Errors
- Check nginx configuration
- Verify backend is running on port 3001
- Check .env file has correct values

### 📝 Environment Variables (.env)

**Location**: `/opt/stonkmarketanalyzer/backend/.env` on server

**Note**: Sensitive values are stored securely on the server. Check `backend/.env` locally for reference.

Required variables:
- `PERPLEXITY_API_KEY` - API key for Perplexity AI
- `PORT` - Backend port (3001)
- `NODE_ENV` - Environment (production)
- `ALLOWED_ORIGINS` - CORS origins
- `JWT_SECRET` - JWT signing secret
- `PORTAL_PATH` - Admin portal secure path
- `PORTAL_USERNAME` - Admin username
- `PORTAL_PASSWORD` - Admin password
- `PORTAL_SECRET_KEY` - Portal JWT secret

### 🎯 Quick Commands Reference

```bash
# SSH into server
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93

# Copy file to server
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem LOCAL_FILE ec2-user@100.27.225.93:REMOTE_PATH

# Run command on server
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93 "COMMAND"

# Restart backend
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

### 💡 Tips for New Sessions

1. **Always check if backend is running first**
2. **Use the restart script** (`/tmp/restart-backend-remote.sh`) instead of manual commands
3. **Check logs** if something doesn't work
4. **Verify .env file** has correct values on server
5. **Test locally first** before deploying to production

### 📚 Related Documentation

- `ADMIN_PORTAL_SECURE_ACCESS.md` - Admin portal access guide
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `ADMIN_CREDENTIALS_SECURE.txt` - Secure credentials backup
- `CURRENT_STATUS.md` - Current system status

---

**Last Updated**: November 13, 2024  
**Status**: Production Ready ✅
