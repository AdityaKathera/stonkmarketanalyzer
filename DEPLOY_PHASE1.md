# Deploy Phase 1 - Account Features

## Quick Deployment Guide

### Step 1: Test Locally (Recommended)

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` and test:
1. Login with "Remember me" checkbox
2. Navigate to Profile page
3. Update your name
4. Change your password
5. Verify everything works

### Step 2: Deploy Backend

```bash
# Upload modified backend files
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/auth_service.py \
  ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/

scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/auth_routes.py \
  ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/

# Restart backend
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

### Step 3: Deploy Frontend

```bash
cd frontend

# Build production bundle
npm run build

# Upload to S3
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E2UZFZ0XAK8XWJ \
  --paths "/*"
```

### Step 4: Verify Production

1. Go to https://stonkmarketanalyzer.com
2. Sign in to your account
3. Test "Remember me" checkbox
4. Click "⚙️ Profile" tab
5. Update your name
6. Go to Security tab
7. Change your password
8. Verify all features work

## What's New for Users

### Remember Me Feature
- New checkbox on login: "Remember me for 30 days"
- Stay logged in longer on trusted devices
- Default is still 7 days if unchecked

### Profile Page
- New "⚙️ Profile" tab in navigation
- Click your name in header to go to profile
- Two tabs: Profile Info and Security

**Profile Info Tab**:
- View account creation date
- View last login time
- Edit your name
- Email is read-only

**Security Tab**:
- Change your password
- Requires current password
- New password must be 8+ characters

## Rollback Plan (If Needed)

If something goes wrong:

### Rollback Backend
```bash
# SSH into server
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93

# Restore from git
cd /opt/stonkmarketanalyzer/backend
git checkout HEAD~1 auth_service.py auth_routes.py

# Restart
bash /tmp/restart-backend-remote.sh
```

### Rollback Frontend
```bash
# Locally, checkout previous version
git checkout HEAD~1 frontend/

# Rebuild and redeploy
cd frontend
npm run build
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete
aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
```

## Monitoring

### Check Backend Logs
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "tail -100 /opt/stonkmarketanalyzer/backend/backend.log"
```

### Check Backend Status
```bash
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "ps aux | grep 'python.*app.py' | grep -v grep"
```

### Test API Endpoints
```bash
# Test profile endpoint
curl -X GET https://api.stonkmarketanalyzer.com/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return user info with name, email, dates
```

## Expected Behavior

### Remember Me
- ✅ Checkbox appears on login form
- ✅ Checked = 30 day token
- ✅ Unchecked = 7 day token
- ✅ Works with email/password login
- ✅ Google SSO users get 7 day token (no checkbox shown)

### Profile Page
- ✅ Profile tab appears when logged in
- ✅ Avatar shows first letter of name/email
- ✅ Can update name successfully
- ✅ Can change password successfully
- ✅ Success/error messages display
- ✅ Dark mode works correctly
- ✅ Responsive on mobile

## Troubleshooting

### "Profile tab not showing"
- Make sure you're logged in
- Refresh the page
- Clear browser cache

### "Failed to update profile"
- Check backend logs
- Verify JWT token is valid
- Check network tab for errors

### "Password change not working"
- Verify current password is correct
- New password must be 8+ characters
- Passwords must match
- Check backend logs for errors

### "Remember me not working"
- Check JWT token expiration in browser
- Verify backend has updated code
- Test with fresh login

## Success Criteria

Phase 1 is successful when:
- ✅ Users can check "Remember me" and stay logged in 30 days
- ✅ Users can access Profile page
- ✅ Users can update their name
- ✅ Users can change their password
- ✅ All features work in dark mode
- ✅ Mobile responsive design works
- ✅ No console errors
- ✅ Backend logs show no errors

---

**Ready to deploy?** Follow the steps above in order!
