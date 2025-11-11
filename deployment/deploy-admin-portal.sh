#!/bin/bash
# Automated Admin Portal Deployment

set -e

EC2_IP="100.27.225.93"
SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"

echo "=== Deploying Secure Admin Portal ==="
echo ""

# Step 1: Generate secure credentials
echo "Step 1: Generating secure credentials..."
CREDENTIALS=$(python3 << 'EOF'
import secrets
portal_path = secrets.token_urlsafe(12).replace('-', '').replace('_', '')[:12]
portal_username = f"sentinel_{secrets.token_hex(4)}"
portal_salt = secrets.token_hex(32)
portal_secret = secrets.token_urlsafe(64)

print(f"{portal_path}|{portal_username}|{portal_salt}|{portal_secret}")
EOF
)

IFS='|' read -r PORTAL_PATH PORTAL_USERNAME PORTAL_SALT PORTAL_SECRET <<< "$CREDENTIALS"

echo "✓ Credentials generated"
echo ""

# Step 2: Package and upload backend
echo "Step 2: Packaging backend..."
tar -czf backend-portal.tar.gz -C backend .

echo "Step 3: Uploading to EC2..."
scp -i "$SSH_KEY" backend-portal.tar.gz ec2-user@$EC2_IP:/home/ec2-user/

# Step 4: Deploy on EC2
echo "Step 4: Deploying on EC2..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << ENDSSH
    # Stop service
    sudo systemctl stop stonkmarketanalyzer
    
    # Extract
    sudo tar -xzf backend-portal.tar.gz -C /opt/stonkmarketanalyzer/backend
    
    # Install dependencies
    cd /opt/stonkmarketanalyzer/backend
    pip3 install --quiet pyjwt==2.8.0 psutil==5.9.6
    
    # Update .env
    sudo tee -a /opt/stonkmarketanalyzer/backend/.env > /dev/null <<EOF

# Secure Admin Portal Configuration
PORTAL_PATH=$PORTAL_PATH
PORTAL_USERNAME=$PORTAL_USERNAME
PORTAL_SALT=$PORTAL_SALT
PORTAL_SECRET_KEY=$PORTAL_SECRET
EOF
    
    # Start service
    sudo systemctl start stonkmarketanalyzer
    
    sleep 3
    echo "Backend deployed"
ENDSSH

echo "✓ Backend deployed"
echo ""

# Step 5: Set password
echo "Step 5: Setting up password..."
echo "Enter a strong password for the admin portal (20+ characters recommended):"
read -s PORTAL_PASSWORD
echo ""

# First time setup to get password hash
HASH_RESPONSE=$(curl -s -X POST https://api.stonkmarketanalyzer.com/api/$PORTAL_PATH/auth \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$PORTAL_USERNAME\",\"password\":\"$PORTAL_PASSWORD\"}")

PASSWORD_HASH=$(echo $HASH_RESPONSE | grep -o '"password_hash":"[^"]*"' | cut -d'"' -f4)

if [ -z "$PASSWORD_HASH" ]; then
    echo "Error: Failed to generate password hash"
    echo "Response: $HASH_RESPONSE"
    exit 1
fi

# Update .env with password hash
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << ENDSSH
    echo "PORTAL_PASSWORD_HASH=$PASSWORD_HASH" | sudo tee -a /opt/stonkmarketanalyzer/backend/.env > /dev/null
    sudo systemctl restart stonkmarketanalyzer
ENDSSH

echo "✓ Password configured"
echo ""

# Step 6: Update and deploy frontend
echo "Step 6: Deploying admin portal frontend..."

# Update portal path in HTML
sed "s/const PORTAL_PATH = 'x9k2m7p4q8w1'/const PORTAL_PATH = '$PORTAL_PATH'/" \
    admin-portal/index.html > /tmp/portal-index.html

# Create S3 bucket
PORTAL_BUCKET="stonk-portal-$(date +%s)"
aws s3 mb s3://$PORTAL_BUCKET --region us-east-1

# Upload
aws s3 cp /tmp/portal-index.html s3://$PORTAL_BUCKET/index.html \
    --content-type "text/html" \
    --cache-control "no-cache"

# Configure website
aws s3 website s3://$PORTAL_BUCKET \
    --index-document index.html

# Make public
cat > /tmp/portal-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::$PORTAL_BUCKET/*"
    }]
}
EOF

aws s3api put-public-access-block \
    --bucket $PORTAL_BUCKET \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

aws s3api put-bucket-policy \
    --bucket $PORTAL_BUCKET \
    --policy file:///tmp/portal-policy.json

PORTAL_URL="http://$PORTAL_BUCKET.s3-website-us-east-1.amazonaws.com"

echo "✓ Frontend deployed"
echo ""

# Save credentials
cat > deployment/portal-credentials.txt <<EOF
=== STONK MARKET ANALYZER - ADMIN PORTAL CREDENTIALS ===
Generated: $(date)

Portal URL: $PORTAL_URL
API Endpoint: https://api.stonkmarketanalyzer.com/api/$PORTAL_PATH
Username: $PORTAL_USERNAME
Password: [the password you entered]
Portal Path: $PORTAL_PATH

KEEP THIS FILE SECURE AND DELETE AFTER SAVING TO PASSWORD MANAGER!

=== END ===
EOF

echo "=== Deployment Complete! ==="
echo ""
echo "🔒 SAVE THESE CREDENTIALS SECURELY:"
echo ""
echo "Portal URL: $PORTAL_URL"
echo "Username: $PORTAL_USERNAME"
echo "Password: [the password you entered]"
echo ""
echo "Credentials also saved to: deployment/portal-credentials.txt"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Save credentials in a password manager"
echo "2. Delete portal-credentials.txt after saving"
echo "3. Access the portal and verify it works"
echo "4. Consider adding IP whitelist for extra security"
echo ""
echo "Access your portal now at: $PORTAL_URL"
