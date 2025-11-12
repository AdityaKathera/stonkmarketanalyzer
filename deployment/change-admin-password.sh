#!/bin/bash
# Change Admin Portal Password

SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"
SERVER="ec2-user@100.27.225.93"

echo "🔐 Admin Portal Password Change"
echo "================================"
echo ""

# Prompt for new password
read -sp "Enter new password: " NEW_PASSWORD
echo ""
read -sp "Confirm new password: " CONFIRM_PASSWORD
echo ""
echo ""

# Check if passwords match
if [ "$NEW_PASSWORD" != "$CONFIRM_PASSWORD" ]; then
    echo "❌ Passwords don't match!"
    exit 1
fi

# Check password strength
if [ ${#NEW_PASSWORD} -lt 12 ]; then
    echo "⚠️  Warning: Password is less than 12 characters"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔄 Generating password hash..."

# Generate hash on server
HASH=$(ssh -i "$SSH_KEY" "$SERVER" "python3 << 'EOF'
import hashlib

salt = '9e5af2ee9b82b8da88be76150666fc15'
password = '$NEW_PASSWORD'
password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
print(f'{salt}:{password_hash}')
EOF
")

if [ -z "$HASH" ]; then
    echo "❌ Failed to generate hash"
    exit 1
fi

echo "✅ Hash generated"
echo ""
echo "🔄 Updating password on server..."

# Update .env file
ssh -i "$SSH_KEY" "$SERVER" "sudo sed -i 's|PORTAL_PASSWORD_HASH=.*|PORTAL_PASSWORD_HASH=$HASH|' /opt/stonkmarketanalyzer/backend/.env"

if [ $? -ne 0 ]; then
    echo "❌ Failed to update password"
    exit 1
fi

echo "✅ Password updated in .env"
echo ""
echo "🔄 Restarting backend..."

# Restart backend
ssh -i "$SSH_KEY" "$SERVER" "sudo systemctl restart stonkmarketanalyzer"

if [ $? -ne 0 ]; then
    echo "❌ Failed to restart backend"
    exit 1
fi

echo "✅ Backend restarted"
echo ""
echo "================================"
echo "✅ Password changed successfully!"
echo ""
echo "You can now login with:"
echo "  Username: sentinel_65d3d147"
echo "  Password: [your new password]"
echo ""
echo "Admin Portal: https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html"
echo "================================"
