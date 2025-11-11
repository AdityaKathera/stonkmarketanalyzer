#!/bin/bash
# Quick Deployment Script - Run this after manual EC2 setup

set -e

echo "=== Stonk Market Analyzer Quick Deploy ==="
echo ""

# Check if AWS CLI is configured
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

# Get EC2 instance IP
echo "Looking for EC2 instance..."
EC2_IP=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=stonkmarketanalyzer-backend" "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text 2>/dev/null || echo "")

if [ "$EC2_IP" == "None" ] || [ -z "$EC2_IP" ]; then
    echo "No running EC2 instance found with tag 'stonkmarketanalyzer-backend'"
    echo ""
    read -p "Enter EC2 Public IP: " EC2_IP
    
    if [ -z "$EC2_IP" ]; then
        echo "Error: EC2 IP is required"
        exit 1
    fi
fi

echo "EC2 Instance IP: $EC2_IP"
echo ""

# Ask for SSH key
read -p "Enter path to your SSH key (.pem file): " SSH_KEY

if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key file not found: $SSH_KEY"
    exit 1
fi

# Ask for Perplexity API key
read -p "Enter your Perplexity API Key: " PERPLEXITY_KEY

echo ""
echo "=== Deploying Backend ==="

# Create backend package
echo "Creating backend package..."
cd backend
tar -czf ../backend.tar.gz .
cd ..

# Upload files to EC2
echo "Uploading files to EC2..."
scp -i "$SSH_KEY" backend.tar.gz ec2-user@$EC2_IP:/home/ec2-user/
scp -i "$SSH_KEY" deployment/backend-setup.sh ec2-user@$EC2_IP:/home/ec2-user/

# Setup backend on EC2
echo "Setting up backend on EC2..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << ENDSSH
    # Extract files
    sudo mkdir -p /opt/stonkmarketanalyzer/backend
    sudo tar -xzf backend.tar.gz -C /opt/stonkmarketanalyzer/backend
    sudo chown -R ec2-user:ec2-user /opt/stonkmarketanalyzer
    
    # Create .env file
    cat > /opt/stonkmarketanalyzer/backend/.env <<EOF
PERPLEXITY_API_KEY=$PERPLEXITY_KEY
PORT=3001
NODE_ENV=production
ALLOWED_ORIGINS=http://stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com,http://localhost:5173
EOF
    
    # Run setup script
    chmod +x backend-setup.sh
    ./backend-setup.sh
    
    # Test backend
    sleep 5
    curl -s http://localhost:3001/api/health || echo "Backend health check failed"
ENDSSH

echo ""
echo "=== Deploying Frontend ==="

# Deploy frontend
chmod +x deployment/frontend-deploy.sh
./deployment/frontend-deploy.sh "http://$EC2_IP"

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Backend API: http://$EC2_IP/api/health"
echo "Frontend: http://stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com"
echo ""
echo "Next steps:"
echo "1. Test the application"
echo "2. Set up CloudFront for HTTPS (optional but recommended)"
echo "3. Configure a custom domain with Route 53 (optional)"
