#!/bin/bash
# Frontend S3 Deployment Script for Stonk Market Analyzer

set -e

echo "=== Stonk Market Analyzer Frontend Deployment ==="

# Configuration
BUCKET_NAME="stonkmarketanalyzer-frontend"
# Get AWS region from CLI config or use default
REGION=$(aws configure get region 2>/dev/null || echo "us-east-1")
BACKEND_URL="" # Will be set after EC2 deployment

echo "Using AWS Region: $REGION"

# Check if backend URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./frontend-deploy.sh <BACKEND_URL>"
    echo "Example: ./frontend-deploy.sh http://ec2-xx-xx-xx-xx.compute.amazonaws.com"
    exit 1
fi

BACKEND_URL=$1

echo "Backend URL: $BACKEND_URL"
echo "S3 Bucket: $BUCKET_NAME"
echo "Region: $REGION"

# Navigate to frontend directory
cd frontend

# Create .env file with backend URL
echo "Creating frontend .env file..."
cat > .env.production <<EOF
VITE_API_URL=$BACKEND_URL
EOF

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building frontend..."
npm run build

# Create S3 bucket
echo "Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION || echo "Bucket already exists"

# Configure bucket for static website hosting
echo "Configuring S3 bucket for static website hosting..."
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html

# Set bucket policy for public access
echo "Setting bucket policy..."
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

# Disable block public access (must be done before setting bucket policy)
echo "Configuring public access settings..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" 2>/dev/null || echo "Note: Public access block settings may need manual adjustment"

# Wait a moment for settings to propagate
sleep 2

# Upload files to S3
echo "Uploading files to S3..."
aws s3 sync dist/ s3://$BUCKET_NAME \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html"

# Upload index.html with no-cache
aws s3 cp dist/index.html s3://$BUCKET_NAME/index.html \
    --cache-control "no-cache, no-store, must-revalidate"

# Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "=== Deployment Complete! ==="
echo "Website URL: $WEBSITE_URL"
echo ""
echo "Note: You may want to set up CloudFront for HTTPS and better performance"
