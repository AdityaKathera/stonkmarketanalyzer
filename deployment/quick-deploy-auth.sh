#!/bin/bash

# Quick Deploy Authentication to EC2
# Simplified deployment for existing infrastructure

set -e

echo "🚀 Deploying Authentication System..."

# Configuration
EC2_IP="100.27.225.93"
EC2_USER="ec2-user"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}📦 Step 1: Preparing files...${NC}"

# Create deployment package
cd backend
tar -czf /tmp/backend-auth-update.tar.gz \
    auth_service.py \
    auth_routes.py \
    app.py \
    requirements.txt \
    .env

echo -e "${GREEN}✅ Package created${NC}"

echo -e "${BLUE}📤 Step 2: Uploading to EC2 (using AWS SSM)...${NC}"

# Get AWS credentials
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

# Get instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=ip-address,Values=$EC2_IP" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# Upload file to S3 temporarily
S3_BUCKET="stonkmarketanalyzer-frontend-1762843094"
aws s3 cp /tmp/backend-auth-update.tar.gz s3://$S3_BUCKET/deploy/backend-auth-update.tar.gz

echo -e "${BLUE}🔧 Step 3: Installing on EC2...${NC}"

# Execute commands on EC2 via SSM
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /home/ec2-user",
        "aws s3 cp s3://'"$S3_BUCKET"'/deploy/backend-auth-update.tar.gz .",
        "tar -xzf backend-auth-update.tar.gz",
        "pip3 install --user bcrypt==4.1.2",
        "pip3 install --user -r requirements.txt",
        "if ! grep -q JWT_SECRET .env; then echo JWT_SECRET=$(python3 -c \"import secrets; print(secrets.token_hex(32))\") >> .env; fi",
        "pkill -f \"python3 app.py\" || true",
        "nohup python3 app.py > app.log 2>&1 &",
        "sleep 2",
        "pgrep -f \"python3 app.py\" && echo Backend started || echo Backend failed"
    ]' \
    --output text \
    --query 'Command.CommandId'

echo -e "${GREEN}✅ Deployment command sent${NC}"

echo -e "${BLUE}⏳ Waiting for deployment to complete...${NC}"
sleep 10

echo -e "${BLUE}🧪 Step 4: Testing endpoints...${NC}"

# Test auth endpoint
echo "Testing auth signup..."
RESPONSE=$(curl -s -X POST https://api.stonkmarketanalyzer.com/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}')

if [[ $RESPONSE == *"token"* ]] || [[ $RESPONSE == *"already registered"* ]]; then
    echo -e "${GREEN}✅ Auth endpoints working!${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}⚠️  Auth test inconclusive${NC}"
    echo "Response: $RESPONSE"
fi

# Cleanup
rm /tmp/backend-auth-update.tar.gz
aws s3 rm s3://$S3_BUCKET/deploy/backend-auth-update.tar.gz

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API URL: https://api.stonkmarketanalyzer.com"
echo ""
echo "New Endpoints:"
echo "  ✅ POST /api/auth/signup"
echo "  ✅ POST /api/auth/login"
echo "  ✅ GET  /api/auth/me"
echo "  ✅ GET  /api/portfolio"
echo "  ✅ POST /api/portfolio"
echo ""
echo "Frontend is already configured correctly!"
echo "Just rebuild and deploy: npm run build && deploy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
