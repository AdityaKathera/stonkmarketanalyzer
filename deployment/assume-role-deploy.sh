#!/bin/bash
# Deploy with assumed IAM role

set -e

echo "=== Assuming IAM Role ==="

ROLE_ARN="arn:aws:iam::938611073268:role/stonkmarketanalyzer"
SESSION_NAME="stonk-deployment-$(date +%s)"

echo "Role: $ROLE_ARN"
echo "Session: $SESSION_NAME"
echo ""

# Assume the role
echo "Assuming role..."
CREDENTIALS=$(aws sts assume-role \
    --role-arn $ROLE_ARN \
    --role-session-name $SESSION_NAME \
    --output json)

# Extract credentials
export AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDENTIALS | jq -r '.Credentials.SessionToken')

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ "$AWS_ACCESS_KEY_ID" == "null" ]; then
    echo "Error: Failed to assume role. Check your permissions."
    exit 1
fi

echo "✓ Role assumed successfully!"
echo ""

# Verify credentials
echo "Verifying credentials..."
IDENTITY=$(aws sts get-caller-identity)
echo "Current identity:"
echo "$IDENTITY" | jq '.'
echo ""

# Now run the deployment
echo "=== Starting Deployment ==="
echo ""

# Get EC2 IP
read -p "Enter EC2 Public IP: " EC2_IP

if [ -z "$EC2_IP" ]; then
    echo "Error: EC2 IP is required"
    exit 1
fi

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

# Deploy frontend with assumed role credentials
chmod +x deployment/frontend-deploy.sh
./deployment/frontend-deploy.sh "http://$EC2_IP"

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Backend API: http://$EC2_IP/api/health"
echo "Frontend: http://stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com"
echo ""
echo "Note: The assumed role session will expire in 1 hour"
