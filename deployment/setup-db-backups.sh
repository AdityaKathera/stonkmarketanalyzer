#!/bin/bash

# Database Backup Setup Script
# Run this to set up automated backups

echo "🔧 Setting up database backups..."

SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"
EC2_IP="100.27.225.93"
S3_BUCKET="stonkmarketanalyzer-frontend-1762843094"

# Set AWS credentials
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

# Create backup
DATE=$(date +%Y%m%d-%H%M%S)
echo "📥 Downloading database from EC2..."
scp -i $SSH_KEY ec2-user@$EC2_IP:/home/ec2-user/backend/users.db /tmp/users-backup-$DATE.db

# Upload to S3
echo "📤 Uploading to S3..."
aws s3 cp /tmp/users-backup-$DATE.db s3://$S3_BUCKET/backups/users-backup-$DATE.db

# Cleanup
rm /tmp/users-backup-$DATE.db

echo "✅ Backup complete!"
echo "📍 Location: s3://$S3_BUCKET/backups/users-backup-$DATE.db"
echo ""
echo "💡 To restore:"
echo "   aws s3 cp s3://$S3_BUCKET/backups/users-backup-$DATE.db /tmp/users.db"
echo "   scp -i $SSH_KEY /tmp/users.db ec2-user@$EC2_IP:/home/ec2-user/backend/users.db"
