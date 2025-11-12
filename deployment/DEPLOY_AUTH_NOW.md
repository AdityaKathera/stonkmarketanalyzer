# 🚀 Deploy Authentication - Quick Guide

## Current Status
- ✅ EC2 Instance: `100.27.225.93` (running)
- ✅ API Domain: `https://api.stonkmarketanalyzer.com`
- ✅ Frontend: Already configured to use the API
- ✅ Route53: DNS configured correctly

## Option 1: Automated Deployment (Recommended)

### Step 1: Add JWT Secret to Backend .env

```bash
# Generate a secure secret
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_hex(32))"

# Add the output to backend/.env
echo "JWT_SECRET=<generated-secret>" >> backend/.env
```

### Step 2: Create Deployment Package

```bash
cd backend
tar -czf backend-auth.tar.gz \
    auth_service.py \
    auth_routes.py \
    app.py \
    requirements.txt \
    .env \
    prompts/ \
    services/
```

### Step 3: Upload to S3 (Temporary Storage)

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

# Upload
aws s3 cp backend-auth.tar.gz s3://stonkmarketanalyzer-frontend-1762843094/deploy/
```

### Step 4: SSH and Deploy

```bash
# SSH into EC2 (you'll need your key)
ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93

# On EC2:
cd /home/ec2-user

# Download from S3
aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz .

# Backup current backend
mv backend backend-backup-$(date +%Y%m%d)

# Extract new files
mkdir backend
tar -xzf backend-auth.tar.gz -C backend/
cd backend

# Install new dependencies
pip3 install --user bcrypt==4.1.2
pip3 install --user -r requirements.txt

# Restart backend
pkill -f "python3 app.py"
nohup python3 app.py > app.log 2>&1 &

# Check if running
sleep 2
pgrep -f "python3 app.py" && echo "✅ Backend running" || echo "❌ Failed"

# Test locally
curl http://localhost:3001/api/health

# Exit SSH
exit
```

### Step 5: Test from Outside

```bash
# Test health
curl https://api.stonkmarketanalyzer.com/api/health

# Test auth signup
curl -X POST https://api.stonkmarketanalyzer.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'

# Should return a token or "already registered"
```

### Step 6: Deploy Frontend

```bash
cd frontend

# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
```

## Option 2: Super Quick (If you have SSH access)

Just run this one command:

```bash
./deployment/deploy-auth-simple.sh
```

## Option 3: Manual File Upload

If you don't have SSH key access:

1. **Update backend/.env** - Add JWT_SECRET
2. **Use AWS Console**:
   - Go to EC2 → Instances
   - Select your instance
   - Actions → Connect → EC2 Instance Connect
3. **Upload files** via SCP or AWS Console
4. **Install bcrypt**: `pip3 install --user bcrypt`
5. **Restart**: `pkill -f python3 && nohup python3 app.py &`

## Verification Checklist

After deployment, verify:

- [ ] Backend health: `curl https://api.stonkmarketanalyzer.com/api/health`
- [ ] Auth signup works
- [ ] Auth login works
- [ ] Portfolio endpoints respond (with auth token)
- [ ] Frontend can sign up users
- [ ] Frontend can login users
- [ ] Portfolio page loads for logged-in users

## Troubleshooting

### Backend not starting?
```bash
# SSH into EC2
ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93

# Check logs
tail -50 /home/ec2-user/backend/app.log

# Check if Python modules installed
python3 -c "import bcrypt; import jwt; print('OK')"
```

### Auth endpoints returning 404?
- Check if auth_routes.py is uploaded
- Check if app.py has `app.register_blueprint(auth_bp)`
- Restart backend

### Database errors?
- Database (users.db) is created automatically
- Check permissions: `ls -la /home/ec2-user/backend/users.db`

## Quick Test Script

Save this as `test-auth.sh`:

```bash
#!/bin/bash
API="https://api.stonkmarketanalyzer.com"

echo "Testing health..."
curl -s $API/api/health | jq

echo -e "\nTesting signup..."
curl -s -X POST $API/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345","name":"Test"}' | jq

echo -e "\nTesting login..."
TOKEN=$(curl -s -X POST $API/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}' | jq -r '.token')

echo "Token: $TOKEN"

echo -e "\nTesting portfolio (authenticated)..."
curl -s $API/api/portfolio \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Next Steps After Deployment

1. ✅ Test authentication flow on live site
2. ✅ Create a test account
3. ✅ Add stocks to portfolio
4. ✅ Verify data persists
5. 🎉 Share with users!

## Rollback (If Needed)

```bash
# SSH into EC2
ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93

# Restore backup
cd /home/ec2-user
pkill -f "python3 app.py"
rm -rf backend
mv backend-backup-YYYYMMDD backend
cd backend
nohup python3 app.py > app.log 2>&1 &
```

## Support

If you encounter issues:
1. Check backend logs: `tail -f /home/ec2-user/backend/app.log`
2. Check if all files uploaded correctly
3. Verify bcrypt is installed: `pip3 list | grep bcrypt`
4. Test locally first before deploying
