# Deploy New Features Guide

## Features Ready to Deploy

1. ✅ Interactive Stock Charts
2. ✅ Price Alerts System
3. ✅ Enhanced Watchlist with Live Prices
4. ✅ Market Overview Dashboard

## Quick Deploy (5 minutes)

### Step 1: Deploy Backend

```bash
# SSH into EC2
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93

# Navigate to backend
cd /opt/stonkmarketanalyzer

# Pull latest code
git pull origin main

# Activate virtual environment
cd backend
source venv/bin/activate

# Install any new dependencies (if needed)
pip install -r requirements.txt

# Restart backend
pkill -9 -f "python.*app.py" 2>/dev/null || true
sleep 2
nohup python3 app.py > backend.log 2>&1 &

# Check logs
tail -30 backend.log

# Exit SSH
exit
```

### Step 2: Deploy Frontend

```bash
# On your local machine
cd frontend

# Install new dependency
npm install

# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
```

### Step 3: Test Features

1. **Stock Charts**: Go to https://stonkmarketanalyzer.com, enter a ticker (e.g., AAPL), see chart below analysis
2. **Market Overview**: Click "🌍 Market" button in navigation
3. **Enhanced Watchlist**: Add stocks to watchlist, see live prices
4. **Price Alerts**: Sign in, click "⚠️ Alerts", create an alert

## Optional: Configure Email Alerts

To enable email notifications for price alerts, add to backend `.env`:

```bash
# SSH into EC2
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93

# Edit .env file
cd /opt/stonkmarketanalyzer/backend
nano .env

# Add these lines:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Save and restart backend
pkill -9 -f "python.*app.py" 2>/dev/null || true
sleep 2
nohup python3 app.py > backend.log 2>&1 &
```

**Note**: For Gmail, you need to create an "App Password" in your Google Account settings.

## Verify Deployment

### Check Backend Health
```bash
curl https://api.stonkmarketanalyzer.com/api/health
```

### Check New Endpoints
```bash
# Test stock price
curl https://api.stonkmarketanalyzer.com/api/stock/price/AAPL

# Test chart data
curl https://api.stonkmarketanalyzer.com/api/stock/chart/AAPL?timeframe=1M

# Test market overview
curl https://api.stonkmarketanalyzer.com/api/market/overview
```

### Check Frontend
Visit https://stonkmarketanalyzer.com and test:
- Enter a ticker and see the chart
- Click "🌍 Market" to see market overview
- Add stocks to watchlist and see live prices
- Sign in and create a price alert

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "tail -50 /opt/stonkmarketanalyzer/backend/backend.log"

# Check if running
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ps aux | grep 'python.*app.py' | grep -v grep"
```

### Import Errors
```bash
# Make sure all new files are uploaded
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ls -la /opt/stonkmarketanalyzer/backend/*.py"

# Should see:
# - chart_service.py
# - price_alerts_service.py
# - market_overview_service.py
# - stock_routes.py
```

### Charts Not Showing
- Clear browser cache
- Check browser console for errors
- Verify lightweight-charts is installed: `npm list lightweight-charts`

### Alerts Not Working
- Check if user is signed in
- Verify backend endpoint: `curl https://api.stonkmarketanalyzer.com/api/alerts` (with auth token)
- Check backend logs for errors

## Rollback (If Needed)

### Backend Rollback
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93
cd /opt/stonkmarketanalyzer
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>
cd backend
pkill -9 -f "python.*app.py" 2>/dev/null || true
nohup python3 app.py > backend.log 2>&1 &
```

### Frontend Rollback
```bash
# Checkout previous version locally
git log --oneline -5
git checkout <previous-commit-hash>

# Rebuild and deploy
cd frontend
npm run build
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete
aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"

# Return to latest
git checkout main
```

## Success Checklist

- [ ] Backend deployed and running
- [ ] Frontend deployed to S3
- [ ] CloudFront cache invalidated
- [ ] Stock charts visible when entering ticker
- [ ] Market overview page loads
- [ ] Watchlist shows live prices
- [ ] Price alerts page accessible (when signed in)
- [ ] All API endpoints responding
- [ ] No errors in browser console
- [ ] No errors in backend logs

## Next Steps

After successful deployment:
1. Monitor backend logs for any errors
2. Test all features thoroughly
3. Consider adding remaining features:
   - Dividend Tracker
   - Export/Import Portfolio
   - Stock Screener
4. Update documentation if needed

---

**Deployment Time**: ~5 minutes
**Downtime**: None (rolling deployment)
**Risk Level**: Low (all features are additive, no breaking changes)
