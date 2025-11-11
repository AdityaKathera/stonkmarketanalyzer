#!/bin/bash

SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"
SERVER="ubuntu@stonkmarketanalyzer.com"

echo "🔄 Restarting backend service..."
ssh -i "$SSH_KEY" "$SERVER" << 'EOF'
sudo systemctl stop stonk-backend
sleep 2
sudo systemctl start stonk-backend
sleep 3
sudo systemctl status stonk-backend --no-pager
echo ""
echo "Recent logs:"
sudo journalctl -u stonk-backend -n 30 --no-pager
EOF
