#!/bin/bash

# Deploy Admin Portal Fix to Production
# This script updates the backend code and restarts the service

set -e

echo "🚀 Deploying Admin Portal Fix..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to backend directory
cd /opt/stonkmarketanalyzer/backend

echo -e "${YELLOW}📦 Installing missing dependencies...${NC}"
source venv/bin/activate
pip install psutil pyjwt bcrypt

echo -e "${YELLOW}📝 Updating app.py (load .env before imports)...${NC}"
# Backup current file
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)

# Update the import order to load .env first
cat > /tmp/app_fix.py << 'EOF'
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import hashlib

# Load environment variables FIRST before any other imports
load_dotenv()

from services.perplexity_service import PerplexityService
from services.stock_price_service import stock_price_service
from prompts.templates import prompt_templates, free_chat_template
from analytics import AnalyticsService
from analytics_comprehensive import ComprehensiveAnalytics
from secure_portal import setup_portal_routes
from cache import SimpleCache
from cache_enhanced import EnhancedCache
from auth_routes import auth_bp
import time
from functools import wraps
EOF

# Replace the import section in app.py
head -n 1 app.py > /tmp/app_new.py
cat /tmp/app_fix.py >> /tmp/app_new.py
tail -n +20 app.py >> /tmp/app_new.py
mv /tmp/app_new.py app.py

echo -e "${YELLOW}📝 Updating analytics_comprehensive.py (fix directory path)...${NC}"
# Backup current file
cp analytics_comprehensive.py analytics_comprehensive.py.backup.$(date +%Y%m%d_%H%M%S)

# Fix the analytics directory path
sed -i "s|self.analytics_dir = Path('/opt/stonkmarketanalyzer/analytics')|self.analytics_dir = Path(__file__).parent / 'analytics_data'|g" analytics_comprehensive.py

echo -e "${YELLOW}🔄 Restarting backend service...${NC}"
sudo systemctl restart stonkmarketanalyzer-backend

echo -e "${YELLOW}⏳ Waiting for service to start...${NC}"
sleep 5

echo -e "${YELLOW}✅ Checking service status...${NC}"
sudo systemctl status stonkmarketanalyzer-backend --no-pager

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "🔐 Your Admin Portal:"
echo "   URL: https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg"
echo "   Username: stonker_971805"
echo "   Password: StonkerBonker@12345millibilli$"
echo ""
echo "📝 Test the portal:"
echo "   curl -X POST https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg/auth \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"stonker_971805\",\"password\":\"StonkerBonker@12345millibilli$\"}'"
echo ""
