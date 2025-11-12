#!/bin/bash

# Deploy Authentication System to EC2
# This script updates your existing EC2 instance with the new auth features

set -e

echo "🚀 Deploying Authentication System to AWS EC2..."

# Configuration
EC2_IP="100.27.225.93"
EC2_USER="ec2-user"
KEY_FILE="$HOME/.ssh/stonkmarketanalyzer-key.pem"  # Update this path
BACKEND_DIR="../backend"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo -e "${RED}❌ SSH key not found at: $KEY_FILE${NC}"
    echo "Please update KEY_FILE in this script with your actual key path"
    exit 1
fi

echo -e "${BLUE}📦 Step 1: Creating deployment package...${NC}"
cd $BACKEND_DIR

# Create temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Using temp directory: $DEPLOY_DIR"

# Copy necessary files
cp -r *.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp -r prompts $DEPLOY_DIR/ 2>/dev/null || true
cp -r services $DEPLOY_DIR/ 2>/dev/null || true
cp -r src $DEPLOY_DIR/ 2>/dev/null || true
cp .env $DEPLOY_DIR/

# Add JWT secret to .env if not present
if ! grep -q "JWT_SECRET" $DEPLOY_DIR/.env; then
    echo "" >> $DEPLOY_DIR/.env
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "JWT_SECRET=$JWT_SECRET" >> $DEPLOY_DIR/.env
    echo -e "${GREEN}✅ Generated JWT_SECRET${NC}"
fi

# Create tarball
cd $DEPLOY_DIR
tar -czf backend-auth.tar.gz *
echo -e "${GREEN}✅ Package created${NC}"

echo -e "${BLUE}📤 Step 2: Uploading to EC2...${NC}"
scp -i $KEY_FILE backend-auth.tar.gz $EC2_USER@$EC2_IP:/home/$EC2_USER/

echo -e "${BLUE}🔧 Step 3: Installing dependencies and restarting service...${NC}"
ssh -i $KEY_FILE $EC2_USER@$EC2_IP << 'ENDSSH'
    set -e
    
    echo "📦 Extracting files..."
    cd /home/ec2-user
    mkdir -p backend-new
    tar -xzf backend-auth.tar.gz -C backend-new/
    
    echo "🔄 Backing up old backend..."
    if [ -d "backend" ]; then
        mv backend backend-backup-$(date +%Y%m%d-%H%M%S)
    fi
    mv backend-new backend
    
    echo "📚 Installing Python dependencies..."
    cd backend
    
    # Install bcrypt if not already installed
    pip3 install --user bcrypt==4.1.2 || true
    pip3 install --user -r requirements.txt || true
    
    echo "🗄️ Setting up database..."
    # Database will be created automatically on first run
    
    echo "🔄 Restarting backend service..."
    # Kill existing Python process
    pkill -f "python3 app.py" || true
    
    # Start new process in background
    nohup python3 app.py > app.log 2>&1 &
    
    echo "✅ Backend restarted with PID: $!"
    
    # Wait a moment and check if it's running
    sleep 3
    if pgrep -f "python3 app.py" > /dev/null; then
        echo "✅ Backend is running"
    else
        echo "❌ Backend failed to start. Check logs:"
        tail -20 app.log
        exit 1
    fi
ENDSSH

echo -e "${GREEN}✅ Deployment complete!${NC}"

echo -e "${BLUE}🧪 Step 4: Testing endpoints...${NC}"

# Test health endpoint
echo "Testing backend health..."
if curl -s http://$EC2_IP:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is responding${NC}"
else
    echo -e "${RED}⚠️  Backend health check failed${NC}"
fi

# Test auth endpoints
echo "Testing auth signup endpoint..."
SIGNUP_RESPONSE=$(curl -s -X POST http://$EC2_IP:3001/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}' || echo "failed")

if [[ $SIGNUP_RESPONSE == *"token"* ]] || [[ $SIGNUP_RESPONSE == *"already registered"* ]]; then
    echo -e "${GREEN}✅ Auth endpoints are working${NC}"
else
    echo -e "${RED}⚠️  Auth endpoint test failed${NC}"
    echo "Response: $SIGNUP_RESPONSE"
fi

echo ""
echo -e "${GREEN}🎉 Deployment Summary:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend URL: http://$EC2_IP:3001"
echo "Auth Endpoints:"
echo "  - POST /api/auth/signup"
echo "  - POST /api/auth/login"
echo "  - GET  /api/auth/me"
echo "  - GET  /api/portfolio"
echo "  - POST /api/portfolio"
echo ""
echo "Next steps:"
echo "1. Update frontend VITE_API_URL to: http://$EC2_IP:3001"
echo "2. Rebuild and deploy frontend"
echo "3. Test authentication flow"
echo ""
echo "View logs: ssh -i $KEY_FILE $EC2_USER@$EC2_IP 'tail -f backend/app.log'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup
rm -rf $DEPLOY_DIR

echo -e "${GREEN}✅ All done!${NC}"
