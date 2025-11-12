# 🚀 Deploy Authentication - Simple Instructions

## ✅ What's Ready

1. ✅ Backend package uploaded to S3
2. ✅ Deployment script created
3. ✅ JWT secret generated
4. ✅ All files prepared

## 🎯 Deploy Now (Choose One Method)

### Method 1: AWS Console (Easiest - No SSH Key Needed)

1. **Open AWS Console**: https://console.aws.amazon.com/ec2/
2. **Go to EC2 → Instances**
3. **Select instance**: `i-0152d0110e97e51d0` (stonkmarketanalyzer-backend)
4. **Click "Connect"** → Choose **"EC2 Instance Connect"**
5. **Copy and paste this command** in the browser terminal:

```bash
aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/deploy-script.sh /tmp/deploy-script.sh && chmod +x /tmp/deploy-script.sh && bash /tmp/deploy-script.sh
```

6. **Wait 30 seconds** for deployment to complete
7. **You should see**: "✅ Backend is running"

### Method 2: If You Have SSH Key

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93 'aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/deploy-script.sh /tmp/deploy-script.sh && chmod +x /tmp/deploy-script.sh && bash /tmp/deploy-script.sh'
```

### Method 3: Manual Step-by-Step

If you're already SSH'd into the instance:

```bash
cd /home/ec2-user
aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz .
mv backend backend-backup-$(date +%Y%m%d) 2>/dev/null || true
mkdir -p backend && tar -xzf backend-auth.tar.gz -C backend/
cd backend
pip3 install --user bcrypt==4.1.2
pip3 install --user -r requirements.txt
pkill -f 'python3 app.py' || true
nohup python3 app.py > app.log 2>&1 &
sleep 3
pgrep -f 'python3 app.py' && echo '✅ Running' || echo '❌ Failed'
curl http://localhost:3001/api/health
```

## 🧪 Test Backend (After Deployment)

```bash
# Test health
curl https://api.stonkmarketanalyzer.com/api/health

# Test signup
curl -X POST https://api.stonkmarketanalyzer.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'

# Should return: {"success":true,"token":"..."}
```

## 📱 Deploy Frontend (After Backend Works)

Run these commands from your local machine:

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

# Build frontend
cd frontend
npm run build

# Deploy to S3
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
```

## ✅ Verification

After both deployments:

1. Go to: https://stonkmarketanalyzer.com
2. Click "Sign In" button
3. Create a new account
4. Should see "Account created successfully"
5. Click "Portfolio" tab
6. Add a stock
7. Verify it appears in your portfolio

## 🐛 Troubleshooting

### Backend not starting?

```bash
# SSH into EC2
ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93

# Check logs
tail -50 /home/ec2-user/backend/app.log

# Check if Python modules installed
python3 -c "import bcrypt, jwt; print('OK')"

# Restart manually
cd /home/ec2-user/backend
pkill -f 'python3 app.py'
nohup python3 app.py > app.log 2>&1 &
```

### Auth endpoints not working?

- Wait 30 seconds after deployment
- Check backend logs
- Verify JWT_SECRET is in .env file
- Test health endpoint first

### Frontend not updating?

- Wait 2-3 minutes for CloudFront invalidation
- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
- Check browser console for errors

## 📊 What Gets Deployed

### Backend Files:
- `auth_service.py` - Authentication logic
- `auth_routes.py` - API endpoints
- `app.py` - Updated main app
- `.env` - With JWT_SECRET
- All existing files (analytics, cache, etc.)

### New Endpoints:
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/portfolio`
- `POST /api/portfolio`
- `PUT /api/portfolio/:id`
- `DELETE /api/portfolio/:id`

### Frontend Updates:
- AuthModal component
- Portfolio component
- User menu in header
- Portfolio tab

## 🎉 Success!

When you see:
- ✅ Backend health check passes
- ✅ Can create account via API
- ✅ Can login and get token
- ✅ Frontend sign-up works
- ✅ Portfolio page loads

**You're done!** 🎊

---

**Need help?** Check the logs or reach out!
