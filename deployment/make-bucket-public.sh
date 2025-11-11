#!/bin/bash
# Make S3 bucket public for website hosting

set -e

echo "=== Making S3 Bucket Public ==="

BUCKET_NAME="stonkmarketanalyzer-frontend-1762843094"
REGION="us-east-1"

# Disable block public access
echo "Disabling block public access..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

sleep 2

# Configure for static website hosting
echo "Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html

# Set public read policy
echo "Setting public read policy..."
cat > /tmp/public-policy.json <<EOF
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
    --policy file:///tmp/public-policy.json

# Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "=== Bucket is now public! ==="
echo ""
echo "S3 Website URL: $WEBSITE_URL"
echo "CloudFront URL: https://d3manxs3wrxea.cloudfront.net"
echo ""
echo "You can use either URL. S3 website URL works immediately."
echo "CloudFront URL provides HTTPS and better performance."
echo ""
echo "Test it now:"
echo "  curl -I $WEBSITE_URL"
