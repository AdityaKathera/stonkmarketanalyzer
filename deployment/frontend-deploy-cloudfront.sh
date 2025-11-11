#!/bin/bash
# Frontend S3 + CloudFront Deployment (No public bucket needed)

set -e

echo "=== Stonk Market Analyzer Frontend Deployment (CloudFront) ==="

# Configuration
BUCKET_NAME="stonkmarketanalyzer-frontend-$(date +%s)"
REGION=$(aws configure get region 2>/dev/null || echo "us-east-1")
BACKEND_URL="" # Will be set after EC2 deployment

# Check if backend URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./frontend-deploy-cloudfront.sh <BACKEND_URL>"
    echo "Example: ./frontend-deploy-cloudfront.sh http://100.27.225.93"
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

# Create S3 bucket (private)
echo "Creating private S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION || echo "Bucket already exists"

# Upload files to S3 (no public access needed)
echo "Uploading files to S3..."
aws s3 sync dist/ s3://$BUCKET_NAME \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html"

# Upload index.html with no-cache
aws s3 cp dist/index.html s3://$BUCKET_NAME/index.html \
    --cache-control "no-cache, no-store, must-revalidate"

# Create CloudFront Origin Access Identity
echo "Creating CloudFront Origin Access Identity..."
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
    --cloud-front-origin-access-identity-config \
    "CallerReference=stonkmarketanalyzer-$(date +%s),Comment=OAI for Stonk Market Analyzer" \
    --query 'CloudFrontOriginAccessIdentity.Id' \
    --output text 2>/dev/null || echo "")

if [ -z "$OAI_ID" ]; then
    echo "Note: Using existing OAI or creating new one..."
    OAI_ID="origin-access-identity/cloudfront/E127EXAMPLE51Z"
fi

# Create bucket policy for CloudFront OAI only
echo "Setting bucket policy for CloudFront access..."
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontOAI",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $OAI_ID"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json 2>/dev/null || echo "Bucket policy set"

# Create CloudFront distribution
echo "Creating CloudFront distribution..."
DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "stonkmarketanalyzer-$(date +%s)",
    "Comment": "Stonk Market Analyzer Frontend",
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": "origin-access-identity/cloudfront/$OAI_ID"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true,
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        }
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "PriceClass": "PriceClass_100"
}
EOF
)

DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config "$DISTRIBUTION_CONFIG" \
    --query 'Distribution.Id' \
    --output text 2>/dev/null || echo "")

if [ -z "$DISTRIBUTION_ID" ]; then
    echo "Error creating CloudFront distribution"
    echo "You can create it manually in AWS Console"
    echo "S3 Bucket: $BUCKET_NAME"
    exit 1
fi

# Get CloudFront domain
CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
    --id $DISTRIBUTION_ID \
    --query 'Distribution.DomainName' \
    --output text)

# Save deployment info
cat > ../deployment/deployment-info.txt <<EOF
Deployment Information
=====================
Date: $(date)
Backend URL: $BACKEND_URL
S3 Bucket: $BUCKET_NAME
CloudFront Distribution ID: $DISTRIBUTION_ID
CloudFront Domain: https://$CLOUDFRONT_DOMAIN
Region: $REGION

Frontend URL: https://$CLOUDFRONT_DOMAIN
Backend API: $BACKEND_URL/api/health

Note: CloudFront distribution takes 15-20 minutes to deploy globally.
EOF

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "S3 Bucket: $BUCKET_NAME (private)"
echo "CloudFront Domain: https://$CLOUDFRONT_DOMAIN"
echo "Distribution ID: $DISTRIBUTION_ID"
echo ""
echo "⚠️  IMPORTANT: CloudFront takes 15-20 minutes to deploy globally"
echo ""
echo "Check deployment status:"
echo "  aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.Status'"
echo ""
echo "Once deployed, access your app at:"
echo "  https://$CLOUDFRONT_DOMAIN"
echo ""
echo "Update backend CORS to allow:"
echo "  https://$CLOUDFRONT_DOMAIN"
echo ""
echo "Deployment info saved to: deployment/deployment-info.txt"
