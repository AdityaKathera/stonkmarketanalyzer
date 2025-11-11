#!/bin/bash
# Fix CloudFront Access to S3 Bucket

set -e

echo "=== Fixing CloudFront S3 Access ==="

BUCKET_NAME="stonkmarketanalyzer-frontend-1762843094"
DISTRIBUTION_ID="E2UZFZ0XAK8XWJ"

# Get the CloudFront OAI canonical user ID
echo "Getting CloudFront distribution details..."
OAI_ID=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID \
    --query 'Distribution.DistributionConfig.Origins.Items[0].S3OriginConfig.OriginAccessIdentity' \
    --output text | sed 's/origin-access-identity\/cloudfront\///')

echo "OAI ID: $OAI_ID"

# Get OAI canonical user
CANONICAL_USER=$(aws cloudfront get-cloud-front-origin-access-identity \
    --id $OAI_ID \
    --query 'CloudFrontOriginAccessIdentity.S3CanonicalUserId' \
    --output text)

echo "Canonical User: $CANONICAL_USER"

# Create correct bucket policy
echo "Creating bucket policy..."
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontOAI",
            "Effect": "Allow",
            "Principal": {
                "CanonicalUser": "$CANONICAL_USER"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

# Apply bucket policy
echo "Applying bucket policy..."
aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

echo ""
echo "✓ Bucket policy updated!"
echo ""
echo "Wait 2-3 minutes for changes to propagate, then try:"
echo "  https://d3manxs3wrxea.cloudfront.net"
echo ""
echo "If still not working, invalidate CloudFront cache:"
echo "  aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths '/*'"
