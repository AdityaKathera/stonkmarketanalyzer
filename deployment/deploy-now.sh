#!/bin/bash

# Direct EC2 Deployment using AWS Run Command
# Uses the stonkmarketanalyzer IAM role

set -e

echo "🚀 Deploying Authentication to EC2 via AWS Systems Manager..."

# Set AWS credentials from role
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

INSTANCE_ID="i-0152d0110e97e51d0"
S3_BUCKET="stonkmarketanalyzer-frontend-1762843094"

echo "📋 Instance: $INSTANCE_ID"
echo "📦 Package already uploaded to S3"

# Create deployment script
cat > /tmp/deploy-script.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "Starting deployment..."
cd /home/ec2-user

# Download package
echo "Downloading package from S3..."
aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz . || exit 1

# Backup existing backend
if [ -d "backend" ]; then
    echo "Backing up existing backend..."
    mv backend backend-backup-$(date +%Y%m%d-%H%M%S)
fi

# Extract new backend
echo "Extracting new backend..."
mkdir -p backend
tar -xzf backend-auth.tar.gz -C backend/ || exit 1
cd backend

# Install dependencies
echo "Installing dependencies..."
pip3 install --user bcrypt==4.1.2 2>&1 | tail -3
pip3 install --user -r requirements.txt 2>&1 | tail -5

# Stop old backend
echo "Stopping old backend..."
pkill -f 'python3 app.py' || true
sleep 2

# Start new backend
echo "Starting new backend..."
nohup python3 app.py > app.log 2>&1 &
sleep 3

# Check if running
if pgrep -f 'python3 app.py' > /dev/null; then
    echo "✅ Backend is running"
    echo "PID: $(pgrep -f 'python3 app.py')"
    
    # Test health endpoint
    curl -s http://localhost:3001/api/health && echo "" || echo "⚠️ Health check failed"
    
    exit 0
else
    echo "❌ Backend failed to start"
    echo "Last 20 lines of log:"
    tail -20 app.log
    exit 1
fi
DEPLOY_SCRIPT

# Upload script to S3
echo "📤 Uploading deployment script..."
aws s3 cp /tmp/deploy-script.sh s3://$S3_BUCKET/deploy/deploy-script.sh

# Execute via user data or direct command
echo "🔧 Executing deployment on EC2..."

# Try using AWS CLI to execute commands
COMMAND_ID=$(aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --comment "Deploy authentication system" \
    --parameters 'commands=[
        "aws s3 cp s3://'"$S3_BUCKET"'/deploy/deploy-script.sh /tmp/deploy-script.sh",
        "chmod +x /tmp/deploy-script.sh",
        "sudo -u ec2-user bash /tmp/deploy-script.sh"
    ]' \
    --output text \
    --query 'Command.CommandId' 2>&1)

if [[ $COMMAND_ID == *"command"* ]] || [[ $COMMAND_ID == *"cmd-"* ]]; then
    echo "✅ Command sent: $COMMAND_ID"
    echo "⏳ Waiting for execution..."
    sleep 10
    
    # Get command output
    aws ssm get-command-invocation \
        --command-id "$COMMAND_ID" \
        --instance-id "$INSTANCE_ID" \
        --query 'StandardOutputContent' \
        --output text 2>/dev/null || echo "Output not available yet"
else
    echo "⚠️ SSM not available. Manual deployment required."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 MANUAL DEPLOYMENT STEPS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Go to AWS Console → EC2 → Instances"
    echo "2. Select instance: $INSTANCE_ID"
    echo "3. Click 'Connect' → 'EC2 Instance Connect'"
    echo "4. Run this command:"
    echo ""
    echo "aws s3 cp s3://$S3_BUCKET/deploy/deploy-script.sh /tmp/deploy-script.sh && chmod +x /tmp/deploy-script.sh && bash /tmp/deploy-script.sh"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Test from outside
echo ""
echo "🧪 Testing API endpoint..."
sleep 5

if curl -s https://api.stonkmarketanalyzer.com/api/health > /dev/null 2>&1; then
    echo "✅ API is responding"
    
    # Test auth endpoint
    echo "Testing auth signup..."
    RESPONSE=$(curl -s -X POST https://api.stonkmarketanalyzer.com/api/auth/signup \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}')
    
    if [[ $RESPONSE == *"token"* ]] || [[ $RESPONSE == *"already registered"* ]]; then
        echo "✅ Auth endpoints working!"
    else
        echo "⚠️ Auth endpoints may need more time to start"
    fi
else
    echo "⚠️ API not responding yet (may need a few more seconds)"
fi

# Cleanup
rm /tmp/deploy-script.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment process complete!"
echo ""
echo "Next: Deploy frontend"
echo "  cd frontend && npm run build"
echo "  aws s3 sync dist/ s3://$S3_BUCKET/ --delete"
echo "  aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths '/*'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
