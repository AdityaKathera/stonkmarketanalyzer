#!/bin/bash
# CloudFront Setup for HTTPS and Better Performance

set -e

echo "=== Setting up CloudFront Distribution ==="

BUCKET_NAME="stonkmarketanalyzer-frontend"
REGION="us-east-1"

# Get EC2 backend URL
read -p "Enter your EC2 backend URL (e.g., http://ec2-xx-xx-xx-xx.compute.amazonaws.com): " BACKEND_URL

# Create CloudFront distribution
echo "Creating CloudFront distribution..."

DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "stonkmarketanalyzer-$(date +%s)",
    "Comment": "Stonk Market Analyzer Frontend",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-stonkmarketanalyzer",
                "DomainName": "$BUCKET_NAME.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultRootObject": "index.html",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-stonkmarketanalyzer",
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
        "Compress": true
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

# Create distribution
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config "$DISTRIBUTION_CONFIG" \
    --query 'Distribution.Id' \
    --output text)

echo "CloudFront Distribution ID: $DISTRIBUTION_ID"

# Get CloudFront domain
CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
    --id $DISTRIBUTION_ID \
    --query 'Distribution.DomainName' \
    --output text)

echo ""
echo "=== CloudFront Setup Complete! ==="
echo ""
echo "CloudFront Domain: https://$CLOUDFRONT_DOMAIN"
echo "Distribution ID: $DISTRIBUTION_ID"
echo ""
echo "Note: It may take 15-20 minutes for the distribution to deploy globally"
echo ""
echo "Next steps:"
echo "1. Update backend CORS to allow: https://$CLOUDFRONT_DOMAIN"
echo "2. Wait for distribution to deploy (check status in AWS Console)"
echo "3. Access your app at: https://$CLOUDFRONT_DOMAIN"
