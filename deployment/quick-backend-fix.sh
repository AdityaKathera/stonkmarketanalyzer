#!/bin/bash

# Quick backend fix deployment script
# This updates only the backend code without touching frontend

SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"
SERVER="ec2-user@100.27.225.93"

echo "🔧 Quick Backend Fix Deployment"
echo "================================"

# Copy updated backend files
echo "📤 Uploading backend files..."
scp -i "$SSH_KEY" backend/app.py "$SERVER:/home/ubuntu/stonkmarketanalyzer/backend/"
scp -i "$SSH_KEY" backend/services/perplexity_service.py "$SERVER:/home/ubuntu/stonkmarketanalyzer/backend/services/"

# Restart backend service
echo "🔄 Restarting backend service..."
ssh -i "$SSH_KEY" "$SERVER" "sudo systemctl restart stonk-backend"

# Wait a moment
sleep 3

# Check status
echo "✅ Checking service status..."
ssh -i "$SSH_KEY" "$SERVER" "sudo systemctl status stonk-backend --no-pager -l | head -20"

echo ""
echo "📋 Recent logs:"
ssh -i "$SSH_KEY" "$SERVER" "sudo journalctl -u stonk-backend -n 20 --no-pager"

echo ""
echo "✅ Deployment complete!"
