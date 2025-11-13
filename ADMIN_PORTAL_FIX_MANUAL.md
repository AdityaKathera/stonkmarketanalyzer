# Admin Portal Fix - Manual Deployment Guide

## Problem
The admin portal URL was returning 404 because:
1. Backend wasn't running
2. Missing Python dependencies (psutil, pyjwt, bcrypt)
3. `.env` file was loaded AFTER imports (so PORTAL_PATH wasn't being read)
4. Analytics directory path was hardcoded incorrectly

## Solution Applied Locally ✅
All fixes have been tested and work on your local machine:
- Backend is running on `http://localhost:3001`
- Admin portal accessible at: `http://localhost:3001/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg`
- Credentials work correctly

## Deploy to Production Server

### Option 1: SSH Deployment (Recommended)

If you have SSH access to your EC2 instance, run:

```bash
./deployment/deploy-admin-portal-ssh.sh
```

**Note**: You'll need your EC2 SSH key. If you don't have it locally, use Option 2.

### Option 2: Manual Steps on Server

SSH into your server and run these commands:

```bash
# 1. Navigate to backend directory
cd /opt/stonkmarketanalyzer/backend

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install missing dependencies
pip install psutil pyjwt bcrypt

# 4. Backup current files
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)
cp analytics_comprehensive.py analytics_comprehensive.py.backup.$(date +%Y%m%d_%H%M%S)

# 5. Update app.py - Move load_dotenv() before imports
nano app.py
```

In `app.py`, change the imports section to:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import hashlib

# Load environment variables FIRST before any other imports
load_dotenv()

from services.perplexity_service import PerplexityService
from services.stock_price_service import stock_price_service
from prompts.templates import prompt_templates, free_chat_template
from analytics import AnalyticsService
from analytics_comprehensive import ComprehensiveAnalytics
from secure_portal import setup_portal_routes
from cache import SimpleCache
from cache_enhanced import EnhancedCache
from auth_routes import auth_bp
import time
from functools import wraps
```

```bash
# 6. Update analytics_comprehensive.py - Fix directory path
nano analytics_comprehensive.py
```

In `analytics_comprehensive.py`, change line 16 from:
```python
self.analytics_dir = Path('/opt/stonkmarketanalyzer/analytics')
```

To:
```python
# Use relative path from backend directory
self.analytics_dir = Path(__file__).parent / 'analytics_data'
```

```bash
# 7. Restart the backend service
sudo systemctl restart stonkmarketanalyzer-backend

# 8. Check service status
sudo systemctl status stonkmarketanalyzer-backend

# 9. Check logs
sudo journalctl -u stonkmarketanalyzer-backend -n 50 --no-pager
```

### Option 3: Use AWS Systems Manager (If Configured)

```bash
# Get instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=*stonk*" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

# Run commands via SSM
aws ssm send-command \
  --instance-ids $INSTANCE_ID \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=[
    "cd /opt/stonkmarketanalyzer/backend",
    "source venv/bin/activate",
    "pip install psutil pyjwt bcrypt",
    "sudo systemctl restart stonkmarketanalyzer-backend"
  ]'
```

## Verify Deployment

After deployment, test the admin portal:

```bash
curl -X POST https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg/auth \
  -H 'Content-Type: application/json' \
  -d '{"username":"stonker_971805","password":"StonkerBonker@12345millibilli$"}'
```

You should get a response with a JWT token:
```json
{
  "token": "eyJhbGci...",
  "expires_in": 7200
}
```

## Your Admin Portal Credentials

**URL**: `https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg`

**Username**: `stonker_971805`

**Password**: `StonkerBonker@12345millibilli$`

## Files Changed

1. **backend/app.py** - Moved `load_dotenv()` before imports
2. **backend/analytics_comprehensive.py** - Fixed analytics directory path
3. **Dependencies added**: psutil, pyjwt, bcrypt

## Troubleshooting

### If portal still returns 404:
```bash
# Check if backend is running
sudo systemctl status stonkmarketanalyzer-backend

# Check logs for errors
sudo journalctl -u stonkmarketanalyzer-backend -n 100 --no-pager

# Verify .env file has correct values
cat /opt/stonkmarketanalyzer/backend/.env | grep PORTAL
```

### If you see "Module not found" errors:
```bash
cd /opt/stonkmarketanalyzer/backend
source venv/bin/activate
pip install psutil pyjwt bcrypt
sudo systemctl restart stonkmarketanalyzer-backend
```

### If portal path is wrong:
```bash
# Check what path is being used
sudo journalctl -u stonkmarketanalyzer-backend -n 20 | grep "Secure portal"

# Should show:
# 🔒 Secure portal initialized at: /api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg
```

## Next Steps

Once deployed, you can access your admin portal and view:
- Real-time analytics
- User activity
- System health
- Cache statistics
- Popular stocks
- Error logs
- Performance metrics

The portal is secured with:
- JWT authentication
- Rate limiting (10 requests/minute)
- Brute force protection (3 failed attempts = 15 min lockout)
- Secure random URL (impossible to guess)
