#!/bin/bash

# Deploy Admin Portal Fix to EC2 Production Server
# Uses IAM role: arn:aws:iam::938611073268:role/stonkmarketanalyzer

set -e

echo "🚀 Deploying Admin Portal Fix to EC2..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
ROLE_ARN="arn:aws:iam::938611073268:role/stonkmarketanalyzer"
REGION="us-east-1"

echo -e "${YELLOW}🔑 Assuming IAM role...${NC}"
CREDS=$(aws sts assume-role \
    --role-arn $ROLE_ARN \
    --role-session-name admin-portal-deployment \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to assume role. Please refresh your AWS credentials.${NC}"
    exit 1
fi

export AWS_ACCESS_KEY_ID=$(echo $CREDS | awk '{print $1}')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | awk '{print $2}')
export AWS_SESSION_TOKEN=$(echo $CREDS | awk '{print $3}')
export AWS_DEFAULT_REGION=$REGION

echo -e "${YELLOW}🔍 Finding EC2 instance...${NC}"
INSTANCE_INFO=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=*stonk*" "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].[InstanceId,PublicIpAddress]' \
    --output text)

INSTANCE_ID=$(echo $INSTANCE_INFO | awk '{print $1}')
INSTANCE_IP=$(echo $INSTANCE_INFO | awk '{print $2}')

if [ -z "$INSTANCE_ID" ]; then
    echo -e "${RED}❌ No running EC2 instance found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found instance: $INSTANCE_ID ($INSTANCE_IP)${NC}"

# Create temporary deployment package
echo -e "${YELLOW}📦 Creating deployment package...${NC}"
TEMP_DIR=$(mktemp -d)
mkdir -p $TEMP_DIR/backend

# Copy updated files
cp backend/app.py $TEMP_DIR/backend/
cp backend/analytics_comprehensive.py $TEMP_DIR/backend/
cp backend/.env $TEMP_DIR/backend/

# Create deployment script for EC2
cat > $TEMP_DIR/deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "📝 Installing missing dependencies..."
cd /opt/stonkmarketanalyzer/backend
source venv/bin/activate
pip install psutil pyjwt bcrypt

echo "📝 Backing up current files..."
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)
cp analytics_comprehensive.py analytics_comprehensive.py.backup.$(date +%Y%m%d_%H%M%S)

echo "📝 Updating files..."
cp /tmp/deployment/backend/app.py app.py
cp /tmp/deployment/backend/analytics_comprehensive.py analytics_comprehensive.py

echo "🔄 Restarting backend service..."
sudo systemctl restart stonkmarketanalyzer-backend

echo "⏳ Waiting for service to start..."
sleep 5

echo "✅ Checking service status..."
sudo systemctl status stonkmarketanalyzer-backend --no-pager | head -20

echo ""
echo "✅ Deployment Complete!"
DEPLOY_SCRIPT

chmod +x $TEMP_DIR/deploy.sh

# Upload files to EC2
echo -e "${YELLOW}📤 Uploading files to EC2...${NC}"
scp -o StrictHostKeyChecking=no -r $TEMP_DIR/* ubuntu@$INSTANCE_IP:/tmp/deployment/

# Execute deployment on EC2
echo -e "${YELLOW}🚀 Executing deployment on EC2...${NC}"
ssh -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP 'bash /tmp/deployment/deploy.sh'

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "🔐 Your Admin Portal is now live:"
echo "   URL: https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg"
echo "   Username: stonker_971805"
echo "   Password: StonkerBonker@12345millibilli$"
echo ""
echo "📝 Test the portal:"
echo "   curl -X POST https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg/auth \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"stonker_971805\",\"password\":\"StonkerBonker@12345millibilli$\"}'"
echo ""
