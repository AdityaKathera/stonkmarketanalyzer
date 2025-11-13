#!/bin/bash

# Get current admin portal information

SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"
EC2_IP="100.27.225.93"

echo "🔍 Getting Admin Portal Information..."
echo ""

# Get portal info from backend logs
ssh -i $SSH_KEY ec2-user@$EC2_IP << 'GET_INFO'
echo "📋 Current Portal Configuration:"
echo "================================"
echo ""

# Get portal path and username from logs
PORTAL_PATH=$(tail -100 /home/ec2-user/backend/app.log | grep "Secure portal initialized" | tail -1 | sed 's/.*at: \/api\///' | tr -d '\r\n')
PORTAL_USERNAME=$(tail -100 /home/ec2-user/backend/app.log | grep "Portal username" | tail -1 | sed 's/.*username: //' | tr -d '\r\n')

echo "🌐 Portal URL:"
echo "https://stonkmarketanalyzer.com/admin.html"
echo ""
echo "🔗 API Endpoint:"
echo "https://api.stonkmarketanalyzer.com/api/$PORTAL_PATH"
echo ""
echo "👤 Username:"
echo "$PORTAL_USERNAME"
echo ""
echo "🔑 Password:"
echo "Use the password you set previously, or set a new one:"
echo ""
echo "To set/reset password:"
echo "1. Visit: https://api.stonkmarketanalyzer.com/api/$PORTAL_PATH/auth"
echo "2. POST with: {\"username\":\"$PORTAL_USERNAME\",\"password\":\"your-new-password\"}"
echo "3. Copy the password_hash from response"
echo "4. Add to .env: PORTAL_PASSWORD_HASH=<hash>"
echo "5. Restart backend"
echo ""
echo "================================"
GET_INFO

echo ""
echo "💡 Quick Password Reset:"
echo "Run: ./deployment/reset-admin-password.sh"
