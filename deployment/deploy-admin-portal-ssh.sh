#!/bin/bash

# Deploy Admin Portal Fix via Direct SSH
# Simple deployment without AWS CLI

set -e

echo "🚀 Deploying Admin Portal Fix to Production..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Your EC2 instance IP (update if needed)
EC2_IP="100.27.225.93"
EC2_USER="ec2-user"
SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"

echo -e "${YELLOW}📦 Creating deployment package...${NC}"

# Create temp directory
TEMP_DIR=$(mktemp -d)
mkdir -p $TEMP_DIR

# Copy files
cp backend/app.py $TEMP_DIR/
cp backend/analytics_comprehensive.py $TEMP_DIR/

# Create remote deployment script
cat > $TEMP_DIR/remote-deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Starting deployment on server..."

cd /opt/stonkmarketanalyzer/backend

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q psutil pyjwt bcrypt

echo "💾 Backing up current files..."
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp analytics_comprehensive.py analytics_comprehensive.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

echo "📝 Updating app.py..."
cp /tmp/admin-portal-deploy/app.py app.py

echo "📝 Updating analytics_comprehensive.py..."
cp /tmp/admin-portal-deploy/analytics_comprehensive.py analytics_comprehensive.py

echo "🔄 Restarting backend..."
# Kill existing process
pkill -f "python.*app.py" || true
sleep 2

# Start backend in background
cd /opt/stonkmarketanalyzer/backend
source venv/bin/activate
nohup python3 app.py > /opt/stonkmarketanalyzer/backend/backend.log 2>&1 &

echo "⏳ Waiting for backend to start..."
sleep 5

echo "✅ Checking if backend is running..."
ps aux | grep "python.*app.py" | grep -v grep || echo "Warning: Backend process not found"

echo "📋 Checking recent logs..."
tail -20 /opt/stonkmarketanalyzer/backend/backend.log

echo ""
echo "✅ Deployment complete!"
EOF

chmod +x $TEMP_DIR/remote-deploy.sh

echo -e "${YELLOW}📤 Uploading files to server...${NC}"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "mkdir -p /tmp/admin-portal-deploy"
scp -i $SSH_KEY -o StrictHostKeyChecking=no $TEMP_DIR/* $EC2_USER@$EC2_IP:/tmp/admin-portal-deploy/

echo -e "${YELLOW}🚀 Executing deployment on server...${NC}"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "bash /tmp/admin-portal-deploy/remote-deploy.sh"

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "🔐 Your Admin Portal:"
echo "   URL: https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg"
echo "   Username: stonker_971805"
echo "   Password: StonkerBonker@12345millibilli$"
echo ""
echo "🧪 Test it now:"
echo "   curl -X POST https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg/auth \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"stonker_971805\",\"password\":\"StonkerBonker@12345millibilli$\"}'"
echo ""
