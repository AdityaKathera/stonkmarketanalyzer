#!/bin/bash

# Simple Auth Deployment Script
# Deploys authentication system to your EC2 instance

set -e

echo "🚀 Deploying Authentication System to EC2..."

# Check if JWT_SECRET exists in .env
if ! grep -q "JWT_SECRET" backend/.env; then
    echo "📝 Generating JWT_SECRET..."
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "" >> backend/.env
    echo "JWT_SECRET=$JWT_SECRET" >> backend/.env
    echo "✅ JWT_SECRET added to .env"
fi

# Create deployment package
echo "📦 Creating deployment package..."
cd backend
tar -czf /tmp/backend-auth.tar.gz \
    auth_service.py \
    auth_routes.py \
    app.py \
    requirements.txt \
    .env \
    prompts/ \
    services/ \
    analytics.py \
    analytics_comprehensive.py \
    cache.py \
    cache_enhanced.py \
    secure_portal.py \
    email_service.py

cd ..

# Set AWS credentials
echo "🔑 Setting AWS credentials..."
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

# Upload to S3
echo "📤 Uploading to S3..."
aws s3 cp /tmp/backend-auth.tar.gz s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz

echo ""
echo "✅ Package uploaded to S3!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NEXT STEPS - Run these commands on EC2:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "# 1. SSH into EC2"
echo "ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93"
echo ""
echo "# 2. Download and extract"
echo "cd /home/ec2-user"
echo "aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz ."
echo "mv backend backend-backup-\$(date +%Y%m%d) 2>/dev/null || true"
echo "mkdir -p backend && tar -xzf backend-auth.tar.gz -C backend/"
echo ""
echo "# 3. Install dependencies"
echo "cd backend"
echo "pip3 install --user bcrypt==4.1.2"
echo "pip3 install --user -r requirements.txt"
echo ""
echo "# 4. Restart backend"
echo "pkill -f 'python3 app.py' || true"
echo "nohup python3 app.py > app.log 2>&1 &"
echo "sleep 2 && pgrep -f 'python3 app.py' && echo '✅ Running' || echo '❌ Failed'"
echo ""
echo "# 5. Test"
echo "curl http://localhost:3001/api/health"
echo "curl -X POST http://localhost:3001/api/auth/signup -H 'Content-Type: application/json' -d '{\"email\":\"test@test.com\",\"password\":\"test1234\",\"name\":\"Test\"}'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Or copy-paste this one-liner:"
echo ""
echo "ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93 'cd /home/ec2-user && aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz . && mv backend backend-backup-\$(date +%Y%m%d) 2>/dev/null || true && mkdir -p backend && tar -xzf backend-auth.tar.gz -C backend/ && cd backend && pip3 install --user bcrypt==4.1.2 && pip3 install --user -r requirements.txt && pkill -f \"python3 app.py\" || true && nohup python3 app.py > app.log 2>&1 & && sleep 2 && pgrep -f \"python3 app.py\" && echo \"✅ Backend running\" || echo \"❌ Failed\"'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup
rm /tmp/backend-auth.tar.gz

echo ""
echo "💡 Tip: After EC2 deployment, rebuild and deploy frontend:"
echo "   cd frontend && npm run build"
echo "   aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete"
echo "   aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths '/*'"
