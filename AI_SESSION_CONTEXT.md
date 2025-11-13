# 🤖 AI Assistant Session Context

## Quick Context for New AI Sessions

### Project Overview
**Stonk Market Analyzer** - A stock research platform with AI-powered analysis, real-time data, and admin analytics dashboard.

### Tech Stack
- **Frontend**: React + Vite (deployed to stonkmarketanalyzer.com)
- **Backend**: Python Flask (deployed to api.stonkmarketanalyzer.com)
- **Server**: AWS EC2 (Amazon Linux 2)
- **Web Server**: Nginx with SSL/TLS
- **Analytics**: Custom analytics system with file-based storage

### Deployment Configuration

**AWS IAM Role**: `arn:aws:iam::938611073268:role/stonkmarketanalyzer`

**EC2 Server**:
- IP: `100.27.225.93`
- User: `ec2-user`
- SSH Key: `/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem`

**Important**: Always use the IAM role for AWS operations. Never use SSM - use direct SSH with the key.

### Deployment Commands

#### Deploy Backend Changes
```bash
# 1. Upload files
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/FILE.py ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/

# 2. Restart backend
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

#### Restart Backend Script Location
The restart script is already on the server at `/tmp/restart-backend-remote.sh`

If it doesn't exist, create it:
```bash
cat > /tmp/restart.sh << 'EOF'
#!/bin/bash
cd /opt/stonkmarketanalyzer/backend
source venv/bin/activate
pkill -9 -f "python.*app.py" 2>/dev/null || true
sleep 2
nohup python3 app.py > backend.log 2>&1 &
sleep 3
echo "Backend restarted. Checking logs..."
tail -30 backend.log
EOF
chmod +x /tmp/restart.sh
bash /tmp/restart.sh
```

### Key File Paths

**On Server**:
- Backend: `/opt/stonkmarketanalyzer/backend/`
- Frontend: `/var/www/stonkmarketanalyzer/`
- Admin Portal: `/var/www/admin-portal/`
- Nginx Config: `/etc/nginx/conf.d/stonkmarketanalyzer.conf`
- Backend Logs: `/opt/stonkmarketanalyzer/backend/backend.log`

**Local**:
- Backend: `./backend/`
- Frontend: `./frontend/`
- Deployment Scripts: `./deployment/`

### Admin Portal

**URL**: `https://api.stonkmarketanalyzer.com/portal/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg`

**Credentials**:
- Username: `stonker_971805`
- Password: `StonkerBonker@12345millibilli$`

**Security**: 43-character random URL, JWT auth, rate limiting, brute force protection

### Common Issues & Solutions

#### Backend Not Running
```bash
# Check status
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ps aux | grep 'python.*app.py' | grep -v grep"

# Check logs
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "tail -50 /opt/stonkmarketanalyzer/backend/backend.log"

# Restart
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

#### Missing Dependencies
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 \
  "cd /opt/stonkmarketanalyzer/backend && \
   source venv/bin/activate && \
   pip install psutil pyjwt bcrypt"
```

#### .env File Issues
The `.env` file must be loaded BEFORE other imports in `app.py`:
```python
from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables FIRST before any other imports
load_dotenv()

# Then import other modules
from services.perplexity_service import PerplexityService
# ... rest of imports
```

### Important Notes

1. **Always use SSH key** - Never try to use AWS SSM
2. **Backend runs as simple Python process** - No systemd service
3. **Analytics data is file-based** - Stored in `analytics_data/` directory
4. **Admin portal uses secure random URL** - Not `/admin` or `/admin-portal`
5. **Nginx serves both API and admin portal** - Check nginx config for routing

### Testing

#### Test Backend Health
```bash
curl https://api.stonkmarketanalyzer.com/api/health
# Should return: {"status":"ok","message":"Stock Research API is running"}
```

#### Test Admin Portal
```bash
curl -X POST https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg/auth \
  -H 'Content-Type: application/json' \
  -d '{"username":"stonker_971805","password":"StonkerBonker@12345millibilli$"}'
# Should return JWT token
```

### Git Workflow

```bash
# Commit changes
git add -A
git commit -m "Description of changes"
git push origin main
```

### Quick Reference

**SSH Command**:
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93
```

**SCP Command**:
```bash
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem LOCAL_FILE ec2-user@100.27.225.93:REMOTE_PATH
```

**Restart Backend**:
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

---

## For AI Assistants: How to Use This Context

1. **Read this file first** when starting a new session about deployment
2. **Use the exact commands** provided - they are tested and working
3. **Always use the SSH key** - Don't try AWS SSM or other methods
4. **Check backend logs** if something doesn't work
5. **Refer to DEPLOYMENT_QUICKSTART.md** for more detailed information

**Last Updated**: November 13, 2024
