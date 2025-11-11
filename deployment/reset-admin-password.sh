#!/bin/bash

# Stonk Market Analyzer - Admin Password Reset Script
# Run this script on your EC2 instance to reset the admin portal password

set -e

echo "🔒 Stonk Market Analyzer - Admin Password Reset"
echo "================================================"
echo ""

# New credentials
NEW_PASSWORD="7f16be4f677890d77e3b"
HASHED_PASSWORD="9e5af2ee9b82b8da88be76150666fc15:b574a54dda0c8efa8586f1f6cdb567343c18e9caf111a9a14b54f2b74794b9caeb82c8942aa726c4745e86c12b746a4ed5aa3020725c9c80ce23450ed6ff8d2f"
USERNAME="sentinel_65d3d147"
PORTAL_PATH="iITXdYyGypK6"

# Backend directory
BACKEND_DIR="/opt/stonkmarketanalyzer/backend"
ENV_FILE="$BACKEND_DIR/.env"

echo "📝 Updating .env file..."

# Backup existing .env
if [ -f "$ENV_FILE" ]; then
    sudo cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%s)"
    echo "✅ Backed up existing .env file"
fi

# Read existing PERPLEXITY_API_KEY
PERPLEXITY_KEY=$(grep "PERPLEXITY_API_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "")

if [ -z "$PERPLEXITY_KEY" ]; then
    echo "⚠️  Warning: PERPLEXITY_API_KEY not found in .env"
    read -p "Enter your Perplexity API key: " PERPLEXITY_KEY
fi

# Create new .env file
sudo tee "$ENV_FILE" > /dev/null <<EOF
PERPLEXITY_API_KEY=$PERPLEXITY_KEY
PORT=3001
NODE_ENV=production

# Admin Portal Credentials
ADMIN_USERNAME=$USERNAME
ADMIN_PASSWORD_HASH=$HASHED_PASSWORD
JWT_SECRET=stonk_jwt_secret_$(openssl rand -hex 32)
PORTAL_PATH=$PORTAL_PATH
EOF

echo "✅ Updated .env file with new credentials"

# Restart the service
echo "🔄 Restarting backend service..."
sudo systemctl restart stonkmarketanalyzer

# Wait for service to start
sleep 3

# Check if service is running
if sudo systemctl is-active --quiet stonkmarketanalyzer; then
    echo "✅ Backend service restarted successfully"
else
    echo "❌ Failed to restart backend service"
    echo "Check logs with: sudo journalctl -u stonkmarketanalyzer -n 50"
    exit 1
fi

echo ""
echo "🎉 Password Reset Complete!"
echo "=========================="
echo ""
echo "Your new admin credentials:"
echo "Portal URL: http://stonk-portal-1762847505.s3-website-us-east-1.amazonaws.com"
echo "Username: $USERNAME"
echo "Password: $NEW_PASSWORD"
echo ""
echo "⚠️  SAVE THESE CREDENTIALS SECURELY!"
echo ""
