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

## 🆕 Latest Features Deployed (November 13, 2024)

### ✅ Google SSO - LIVE & WORKING (Nov 13, 2024)
- **Client ID**: `735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com`
- **Status**: ✅ Working on https://stonkmarketanalyzer.com
- **Files**: `frontend/src/components/AuthModal.jsx`, `backend/auth_routes.py`
- **Package**: `@react-oauth/google` installed
- **Backend Endpoint**: `/api/auth/google`
- **Fix Applied**: Removed `useOneTap` prop that was causing authorization errors
- **Google Console Setup**:
  - Publishing status: In production
  - Authorized domains: `stonkmarketanalyzer.com`
  - JavaScript origins: `https://stonkmarketanalyzer.com`, `https://www.stonkmarketanalyzer.com`
- **Note**: Add www version to Google Console for full support
- **Troubleshooting**: See `GOOGLE_SSO_FINAL_FIX.md` for complete guide

### ✅ Enhanced Portfolio - LIVE & WORKING
- **Component**: `frontend/src/components/PortfolioEnhanced.jsx`
- **Backend Service**: `backend/portfolio_service.py`
- **New Endpoints**: 
  - `/api/portfolio/summary` - Real-time prices and metrics
  - `/api/portfolio/allocation` - Portfolio breakdown
- **Features**: 
  - Real-time stock prices (1-min cache)
  - Automatic P/L calculations
  - Portfolio summary cards
  - Auto-refresh every 60 seconds
  - Color-coded performance
- **Status**: ✅ Fully functional and tested

### ✅ Phase 1 Account Features - LIVE (Nov 13, 2024)
- **Component**: `frontend/src/components/Profile.jsx`
- **Backend**: `backend/auth_service.py`, `backend/auth_routes.py`
- **New Endpoints**:
  - `PUT /api/auth/profile` - Update user name
  - `POST /api/auth/change-password` - Change password
  - `GET /api/auth/me` - Get full user data (used by profile page)
- **Features**:
  - **Remember Me**: Checkbox on login (7 days vs 30 days JWT)
  - **Profile Page**: View/edit name, change password, account stats
  - **Profile Header**: Large avatar (100px), prominent name (32px), badges, email icon
  - **Profile Tabs**: Profile Info & Security
  - **Account Stats**: Member since date, last login time with icons (📅 🕐)
  - **User Menu**: Profile button in header, logout button
  - **Dark Mode**: Full support throughout
  - **Responsive**: Mobile-friendly design
- **Recent Fixes** (Nov 13, 2024):
  - ✅ Fixed N/A dates by fetching full user data from `/api/auth/me`
  - ✅ Improved profile header design (larger, more visible)
  - ✅ Added profile badges and stat icons
  - ✅ Better date formatting with fallbacks
- **Documentation**: See `PHASE1_ACCOUNT_FEATURES.md` and `PHASE1_DEPLOYMENT_COMPLETE.md`
- **Status**: ✅ Deployed and working in production

### ⚠️ CloudFront Cache - TEMPORARY SETTING
- **Distribution ID**: E2UZFZ0XAK8XWJ
- **Current TTL**: 0 seconds (no caching)
- **Reason**: Faster deployments during testing
- **Action Required**: Restore to 3600 seconds (1 hour) after testing
- **Restore Commands**: See `CLOUDFRONT_CACHE_REMINDER.md`
- **Note**: Stock data caching (backend) is separate and unaffected

### Frontend Deployment (S3 + CloudFront)
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete
aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
```

**S3 Bucket**: `stonkmarketanalyzer-frontend-1762843094`  
**CloudFront**: E2UZFZ0XAK8XWJ

---

## For AI Assistants: How to Use This Context

1. **Read this file first** when starting a new session about deployment
2. **Use the exact commands** provided - they are tested and working
3. **Always use the SSH key** - Don't try AWS SSM or other methods
4. **Check backend logs** if something doesn't work
5. **Refer to DEPLOYMENT_QUICKSTART.md** for more detailed information
6. **New Features**: Google SSO and Enhanced Portfolio are deployed and working
7. **CloudFront**: Cache is temporarily 0 - restore after testing
8. **Google SSO Issues**: Check `GOOGLE_SSO_TROUBLESHOOTING.md` for solutions

## Key Documentation Files

- **START_HERE.md** - Quick start guide for new sessions
- **AI_SESSION_CONTEXT.md** - This file, essential deployment context
- **DEPLOYMENT_QUICKSTART.md** - Comprehensive deployment guide
- **PHASE1_ACCOUNT_FEATURES.md** - Phase 1 features documentation
- **PHASE1_DEPLOYMENT_COMPLETE.md** - Phase 1 deployment summary
- **GOOGLE_SSO_TROUBLESHOOTING.md** - Google OAuth error solutions
- **TROUBLESHOOTING_DEPLOYMENT.md** - General deployment issues

**Last Updated**: November 13, 2024 (Phase 1 Account Features - Profile UI Improvements)


## AWS Deployment Notes (Nov 13, 2024)

- **AWS Region**: us-east-1 (fixed typo from use-east-1)
- **Deployment Script**: `deploy-with-role.sh` (uses permanent AWS credentials)
- **S3 Bucket**: stonkmarketanalyzer-frontend-1762843094
- **CloudFront Distribution**: E2UZFZ0XAK8XWJ
- **IAM Role**: arn:aws:iam::938611073268:role/stonkmarketanalyzer

## Latest Session Summary (Nov 13, 2024)

### ✅ Completed
- Google SSO working on https://stonkmarketanalyzer.com
- Profile page with improved header design (100px avatar, white text)
- Remember Me checkbox (7 vs 30 day sessions)
- CORS fixed for PUT/DELETE methods
- Profile name visibility fixed (white text on gradient)
- User menu styling fixed (white text for username and logout button)
- Deployment script created (deploy-with-role.sh)
- Profile update now properly refreshes user state in header

### 🎨 UI Improvements
- Profile header: Large avatar, white text, gradient background
- User menu: White text on colored backgrounds for visibility
- Profile button: Purple/blue background with white text
- Logout button: Solid red background with white text
- All buttons have hover effects and shadows
- Full dark mode support

### 📝 Notes for Next Session
- Google SSO works on main domain, add www support if needed
- Use `deploy-with-role.sh` for frontend deployments
- AWS credentials configured with permanent access keys
- All Phase 1 account features deployed and working
- User menu styling complete with proper visibility

### ✅ Account Linking - COMPLETE & TESTED (Nov 13, 2024)
- **Status**: ✅ Fully deployed, tested, and working in production
- **Component**: `frontend/src/components/Profile.jsx` (Linked Accounts tab)
- **Backend**: `backend/auth_service.py`, `backend/auth_routes.py`
- **New Endpoints**:
  - `GET /api/auth/linked-accounts` - Get linked providers
  - `POST /api/auth/link-google` - Link Google to account (via auto-link)
  - `DELETE /api/auth/unlink-google` - Unlink Google
  - `PUT /api/auth/primary-method` - Set primary login method
- **Database**: Added `google_id`, `auth_provider`, `primary_auth_method` columns
- **Features**:
  - ✅ Auto-linking: Sign in with Google using same email to link accounts
  - ✅ Unlink Google account (must keep at least one method)
  - ✅ Set primary authentication method
  - ✅ View all linked providers with status badges
  - ✅ Clear instructions for users without Google accounts
  - ✅ Works with ANY email (Gmail, Yahoo, Outlook, etc.)
  - ✅ Full dark mode support
  - ✅ Mobile responsive design
- **User Flow**:
  1. User creates account with email/password
  2. Goes to Profile → Linked Accounts tab
  3. Follows instructions to create Google account (if needed)
  4. Logs out and signs in with Google using same email
  5. Google account automatically links - all data preserved
- **Documentation**: 
  - `ACCOUNT_LINKING_COMPLETE.md` - Full feature documentation
  - `ACCOUNT_LINKING_TEST_GUIDE.md` - Testing scenarios
  - `DEPLOYMENT_SUMMARY_ACCOUNT_LINKING.md` - Deployment details

### ✅ Smart Portfolio Insights - COMPLETE (Nov 13, 2024)
- **Status**: ✅ Deployed and working in production
- **Component**: `frontend/src/components/PortfolioInsights.jsx`
- **Backend**: `backend/portfolio_insights_service.py`
- **New Endpoint**: `GET /api/portfolio/insights` - AI-powered portfolio analysis
- **Features**:
  - 🎯 Diversification Score (0-100) with detailed breakdown
  - ⚠️ Risk Warnings (concentration, sector exposure)
  - 📈 Performance Analysis (best/worst performers, total P/L)
  - 💡 AI Recommendations powered by Perplexity API
  - 🏆 Portfolio Strengths highlighting
  - 🔄 Refresh button to regenerate insights
  - ⏱️ 1-hour caching per user
- **UI Features**:
  - Portfolio summary cards (value, holdings, diversification, sectors)
  - Color-coded insight cards (success/warning/info)
  - Excellent text visibility in both light and dark modes
  - Loading states and error handling
  - Mobile responsive design
- **AI Integration**:
  - Uses Perplexity API for intelligent recommendations
  - Analyzes portfolio composition and metrics
  - Provides specific, actionable advice
  - Fallback insights if API fails
- **Documentation**: `SMART_PORTFOLIO_INSIGHTS_PLAN.md`

### 🎯 Next Task: AI News Summarizer
Ready to build personalized news feed for watchlist stocks!


---

## Session Update: Account Linking Complete (Nov 13, 2024 - Final)

### 🎉 Feature Fully Implemented and Tested

**Implementation Time**: ~3 hours (including iterations and UI improvements)

**What Was Built**:
- Complete account linking system for Google OAuth
- Auto-link flow: Users sign in with Google using same email to link accounts
- Unlink functionality with validation (must keep at least one method)
- Primary authentication method selection
- Comprehensive user instructions with 2-step process
- Support for ALL email providers (not just Gmail)

**Files Modified**:
- `backend/auth_service.py` - 6 new functions, database migration
- `backend/auth_routes.py` - 4 new API endpoints
- `frontend/src/components/Profile.jsx` - New Linked Accounts tab
- `frontend/src/components/Profile.css` - Complete styling with dark mode
- `backend/users.db` - 3 new columns added

**UI Improvements Made**:
- Profile tabs now have white text for visibility
- Clear 2-step instructions for account linking
- Prominent "Don't have a Google account?" section
- Clickable link to create Google account
- Card-based design for linked accounts
- Primary badge highlighting
- Full dark mode support
- Mobile responsive

**Testing Status**: ✅ Tested and working in production
- Auto-linking works correctly
- Unlinking validates properly
- Primary method switching functional
- Instructions clear and helpful
- UI looks great in light and dark modes

**Deployment Status**: ✅ Complete
- Backend deployed and running
- Frontend deployed to S3
- CloudFront cache cleared
- All changes committed to git

**Documentation**: 4 comprehensive documents created

**Ready for**: Production use by all users

---

## Latest Features Added (Nov 13, 2024 - Afternoon Session)

### ✅ Smart Portfolio Insights (Phase 2 - AI Features)
**Implementation Time**: ~2 hours

**What Was Built**:
- Complete AI-powered portfolio analysis system
- Diversification scoring algorithm (0-100 scale)
- Risk detection for concentration and sector exposure
- Performance tracking with best/worst performers
- Perplexity AI integration for personalized recommendations
- Beautiful insight cards with color coding
- 1-hour caching for performance

**Files Created**:
- `backend/portfolio_insights_service.py` - Analysis engine
- `frontend/src/components/PortfolioInsights.jsx` - UI component
- `frontend/src/components/PortfolioInsights.css` - Styling
- `SMART_PORTFOLIO_INSIGHTS_PLAN.md` - Documentation

**Files Modified**:
- `backend/auth_routes.py` - Added `/api/portfolio/insights` endpoint
- `frontend/src/components/PortfolioEnhanced.jsx` - Integrated insights

**UI Improvements**:
- Revamped text colors for excellent visibility
- Light mode: Dark navy titles, clear contrast
- Dark mode: White titles, bright text on rich backgrounds
- All text weights increased for readability
- Card shadows and borders enhanced
- Summary stats: Pure white text with !important overrides
- Labels: Bold uppercase with letter spacing
- Values: Extra bold (800) with text shadow

**Status**: ✅ Deployed and working in production
**Latest Update**: Fixed summary stats visibility with forced white text (Nov 13, 9:41 AM)

### UI Polish (Nov 13, 9:41 AM)
- Fixed summary stats text visibility
- Added `!important` overrides for white text
- Increased font weights and opacity
- Enhanced text shadows for better contrast
- All text now crystal clear in both modes

---

**Last Updated**: November 13, 2024, 9:41 AM UTC
