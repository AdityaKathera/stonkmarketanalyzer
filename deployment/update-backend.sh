#!/bin/bash
# Quick Backend Update Script

set -e

echo "=== Updating Backend ==="

# Get inputs
read -p "Enter EC2 Public IP: " EC2_IP
read -p "Enter path to SSH key: " SSH_KEY

if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found"
    exit 1
fi

# Create package
echo "Creating backend package..."
cd backend
tar -czf ../backend-update.tar.gz .
cd ..

# Upload and update
echo "Uploading to EC2..."
scp -i "$SSH_KEY" backend-update.tar.gz ec2-user@$EC2_IP:/home/ec2-user/

echo "Updating backend on EC2..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    sudo systemctl stop stonkmarketanalyzer
    sudo tar -xzf backend-update.tar.gz -C /opt/stonkmarketanalyzer/backend
    sudo systemctl start stonkmarketanalyzer
    sleep 3
    sudo systemctl status stonkmarketanalyzer
ENDSSH

echo ""
echo "Backend updated successfully!"
echo "Check logs: ssh -i $SSH_KEY ec2-user@$EC2_IP 'sudo journalctl -u stonkmarketanalyzer -f'"
