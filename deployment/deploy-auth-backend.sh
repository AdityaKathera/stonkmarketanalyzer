#!/bin/bash

# Deploy Authentication Backend to EC2
# Based on existing deployment patterns

set -e

echo "🚀 Deploying Authentication Backend to EC2"
echo "=========================================="

# Configuration
EC2_IP="100.27.225.93"
EC2_USER="ec2-user"
BACKEND_DIR="/home/ec2-user/backend"

# Set AWS credentials
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

echo "📦 Step 1: Creating backend package..."
cd backend
tar -czf /tmp/backend-auth-deploy.tar.gz \
    auth_service.py \
    auth_routes.py \
    app.py \
    requirements.txt \
    .env \
    prompts/ \
    services/ \
    analytics.py \
    analytics_comprehensive.py \
    analytics_enhanced.py \
    cache.py \
    cache_enhanced.py \
    secure_portal.py \
    email_service.py \
    cache_warmer.py

cd ..

echo "✅ Package created"

echo "📤 Step 2: Uploading to S3..."
aws s3 cp /tmp/backend-auth-deploy.tar.gz s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth-deploy.tar.gz

echo "✅ Uploaded to S3"

echo "🔧 Step 3: Deploying to EC2..."

# Create deployment commands
cat > /tmp/ec2-deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "📥 Downloading package from S3..."
cd /home/ec2-user
aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth-deploy.tar.gz .

echo "💾 Backing up current backend..."
if [ -d "backend" ]; then
    mv backend backend-backup-$(date +%Y%m%d-%H%M%S)
fi

echo "📦 Extracting new backend..."
mkdir -p backend
tar -xzf backend-auth-deploy.tar.gz -C backend/
cd backend

echo "📚 Installing dependencies..."
pip3 install --user bcrypt==4.1.2 2>&1 | tail -3
pip3 install --user -r requirements.txt 2>&1 | tail -5

echo "🔄 Restarting backend..."
pkill -f 'python3 app.py' || true
sleep 2

nohup python3 app.py > app.log 2>&1 &
sleep 3

if pgrep -f 'python3 app.py' > /dev/null; then
    echo "✅ Backend is running (PID: $(pgrep -f 'python3 app.py'))"
    curl -s http://localhost:3001/api/health && echo "" || echo "⚠️ Health check failed"
    exit 0
else
    echo "❌ Backend failed to start"
    tail -20 app.log
    exit 1
fi
DEPLOY_SCRIPT

# Upload deployment script
aws s3 cp /tmp/ec2-deploy.sh s3://stonkmarketanalyzer-frontend-1762843094/deploy/ec2-deploy.sh

echo "✅ Deployment script uploaded"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 MANUAL STEP REQUIRED:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Go to AWS Console → EC2 → Instance Connect"
echo "Or run this command if you have SSH access:"
echo ""
echo "ssh -i ~/.ssh/your-key.pem ec2-user@$EC2_IP 'aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/ec2-deploy.sh /tmp/ec2-deploy.sh && chmod +x /tmp/ec2-deploy.sh && bash /tmp/ec2-deploy.sh'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup
rm /tmp/backend-auth-deploy.tar.gz /tmp/ec2-deploy.sh

echo ""
echo "✅ Backend package ready for deployment!"
