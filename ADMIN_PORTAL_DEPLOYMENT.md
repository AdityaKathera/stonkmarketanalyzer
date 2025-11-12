# Admin Portal Comprehensive Update - Deployment Guide

## 🎉 What's New

### Enhanced Admin Portal Features
1. **💰 Revenue & Usage Metrics**
   - API calls per day tracking
   - Estimated cost calculation
   - Average calls per user
   - Peak usage hours identification

2. **📊 User Behavior Analytics**
   - Guided Mode vs Chat Mode vs Compare Mode usage
   - Percentage breakdown of feature usage
   - Total interactions tracking

3. **🏥 System Health Monitoring**
   - Real-time CPU usage
   - Memory usage monitoring
   - Disk usage tracking
   - System status indicators

4. **⚙️ Admin Actions**
   - Clear cache button
   - Refresh all data button
   - CSV export functionality

5. **🔴 Improved Activity Feed**
   - Better formatted event descriptions
   - User identification
   - Meaningful activity summaries
   - Filters out noise (page_hidden, heartbeat events)

6. **⚡ Performance Tracking**
   - API response times tracked
   - Slow query detection
   - Error tracking with context

## 📦 Files Updated

### Frontend
- `admin-portal/index.html` - Enhanced with all new features

### Backend
- `backend/analytics_comprehensive.py` - NEW: Comprehensive analytics system
- `backend/secure_portal.py` - Added new API endpoints
- `backend/app.py` - Integrated performance tracking

## 🚀 Deployment Steps

### 1. Frontend Deployment (Already Done ✅)
The enhanced admin portal is already deployed to:
```
https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html
```

### 2. Backend Deployment (Required)

#### Option A: Deploy to EC2 (Recommended)
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@your-instance

# Navigate to backend directory
cd /opt/stonkmarketanalyzer/backend

# Pull latest changes
git pull origin main

# Install new dependencies (if any)
pip install psutil  # For system health monitoring

# Restart the backend service
sudo systemctl restart stonkmarketanalyzer
# OR
sudo pm2 restart stonkmarketanalyzer
```

#### Option B: Deploy with Docker
```bash
# Rebuild the container
docker-compose down
docker-compose build
docker-compose up -d
```

### 3. Verify Deployment

#### Test New Endpoints
```bash
# Get your auth token first by logging into the admin portal

# Test revenue metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/revenue

# Test user behavior
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/user-behavior

# Test system health
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/system/health-full

# Test peak hours
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/peak-hours
```

## 🔧 Configuration

### Environment Variables
No new environment variables required! The system uses existing configuration.

### Dependencies
Make sure `psutil` is installed for system health monitoring:
```bash
pip install psutil
```

## 📊 New API Endpoints

All endpoints require authentication with Bearer token.

### Revenue Metrics
```
GET /api/{PORTAL_PATH}/analytics/revenue
Response: {
  "total_api_calls": 1234,
  "estimated_cost": 1.23,
  "calls_by_endpoint": {...},
  "avg_calls_per_user": 12.5
}
```

### Peak Usage Hours
```
GET /api/{PORTAL_PATH}/analytics/peak-hours
Response: {
  "peak_hours": [
    {"hour": "2025-11-12T14", "events": 450, "users": 23, "sessions": 45}
  ]
}
```

### User Behavior
```
GET /api/{PORTAL_PATH}/analytics/user-behavior
Response: {
  "guided_mode": {"count": 100, "percentage": 45.5},
  "chat_mode": {"count": 80, "percentage": 36.4},
  "compare_mode": {"count": 40, "percentage": 18.1},
  "total_interactions": 220
}
```

### System Health (Full)
```
GET /api/{PORTAL_PATH}/system/health-full
Response: {
  "cpu_percent": 25.5,
  "memory_percent": 45.2,
  "memory_available_gb": 2.5,
  "disk_percent": 60.0,
  "disk_free_gb": 15.3,
  "status": "healthy"
}
```

### Cache Management
```
POST /api/{PORTAL_PATH}/cache/clear
Response: {
  "success": true,
  "message": "Cache cleared"
}
```

## 🎯 Auto-Refresh Schedule

The admin portal automatically refreshes data:
- **Every 5 seconds**: Activity feed
- **Every 10 seconds**: Performance stats, cache stats, system health
- **Every 30 seconds**: Analytics, revenue metrics, user behavior, errors

## 🐛 Troubleshooting

### Issue: Performance metrics showing 0
**Solution**: The backend needs to be restarted to start tracking. Once restarted, metrics will populate as API calls are made.

### Issue: System health not showing
**Solution**: Install psutil: `pip install psutil`

### Issue: Activity feed shows raw events
**Solution**: Backend needs to use `ComprehensiveAnalytics` class. Check that `backend/app.py` imports and uses it.

### Issue: New sections not loading
**Solution**: 
1. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
2. Wait 1-2 minutes for CloudFront cache invalidation
3. Check browser console for errors

## 📝 Notes

- All analytics data is stored in `/opt/stonkmarketanalyzer/analytics/`
- Daily files are created automatically: `analytics_YYYY-MM-DD.jsonl`
- In-memory tracking is limited to recent data (configurable in code)
- Cache statistics track hits/misses for performance optimization

## 🎉 Success Indicators

After deployment, you should see:
1. ✅ Activity feed with meaningful descriptions
2. ✅ Performance metrics populating with real data
3. ✅ Revenue metrics showing API call counts
4. ✅ User behavior percentages
5. ✅ System health with CPU/memory/disk stats
6. ✅ Admin actions working (clear cache, refresh)

## 🔐 Security

- All endpoints require JWT authentication
- Rate limiting is enforced
- Brute force protection is active
- IP whitelisting available (optional)

## 📞 Support

If you encounter issues:
1. Check backend logs: `sudo journalctl -u stonkmarketanalyzer -f`
2. Check browser console for frontend errors
3. Verify API endpoints are responding
4. Ensure backend is using latest code from git

---

**Deployment Date**: November 12, 2025
**Version**: 2.0 - Comprehensive Analytics
