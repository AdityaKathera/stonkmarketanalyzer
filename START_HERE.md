# 👋 Start Here - New AI Session Guide

## For AI Assistants Starting a New Session

If you're an AI assistant helping with this project and need context, **read these files in order**:

### 1️⃣ **AI_SESSION_CONTEXT.md** (Read First!)
Essential context for deployment:
- AWS IAM role and SSH configuration
- Quick deployment commands
- Common issues and solutions
- File paths and structure

### 2️⃣ **DEPLOYMENT_QUICKSTART.md** (Detailed Reference)
Comprehensive deployment guide:
- All deployment commands
- Troubleshooting steps
- Environment configuration
- Project structure

### 3️⃣ **ADMIN_PORTAL_SECURE_ACCESS.md** (Admin Portal)
Admin portal access and security:
- Secure URL and credentials
- Security features
- How to access
- API endpoints

## Quick Commands for Common Tasks

### Deploy Backend Changes
```bash
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/FILE.py ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/

ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

### Check Backend Status
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ps aux | grep 'python.*app.py' | grep -v grep"
```

### View Logs
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "tail -50 /opt/stonkmarketanalyzer/backend/backend.log"
```

## Key Information

**AWS IAM Role**: `arn:aws:iam::938611073268:role/stonkmarketanalyzer`  
**SSH Key**: `/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem`  
**EC2 User**: `ec2-user`  
**EC2 IP**: `100.27.225.93`

**Admin Portal**: https://api.stonkmarketanalyzer.com/portal/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg

## For Users

If you're the project owner:

1. **To deploy changes**: Use the commands in `DEPLOYMENT_QUICKSTART.md`
2. **To access admin portal**: See `ADMIN_PORTAL_SECURE_ACCESS.md`
3. **For troubleshooting**: Check the troubleshooting sections in the guides

## Project Status

✅ **Production Ready**
- Frontend: https://stonkmarketanalyzer.com
- API: https://api.stonkmarketanalyzer.com
- Admin Portal: Fully functional with real-time analytics
- Security: Multi-layer authentication and rate limiting

## 🆕 Latest Features (November 13, 2024)

### Google SSO
- One-click sign-in with Google
- Automatic account creation
- No password needed
- OAuth 2.0 secure flow

### Enhanced Portfolio
- Real-time stock prices (1-minute cache)
- Automatic P/L calculations
- Portfolio summary dashboard
- Best/worst performer tracking
- Auto-refresh every 60 seconds
- Color-coded performance indicators

### CloudFront Configuration
⚠️ **IMPORTANT**: CloudFront cache temporarily set to 0 for testing
- See `CLOUDFRONT_CACHE_REMINDER.md` for details
- **Must restore to 1 hour after testing**
- Stock data caching (backend) is separate and unaffected

---

**Last Updated**: November 13, 2024
