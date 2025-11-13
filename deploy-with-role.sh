#!/bin/bash

# Deploy Frontend Using IAM Role
# This script assumes the IAM role and deploys the frontend

echo "🔐 Using AWS credentials..."

# Clear any existing session tokens to use permanent credentials
unset AWS_SESSION_TOKEN

echo "✅ Credentials ready"
echo ""
echo "🚀 Deploying frontend to S3..."

cd frontend

# Sync to S3
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete

if [ $? -eq 0 ]; then
    echo "✅ Frontend uploaded to S3 successfully!"
    
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
    
    if [ $? -eq 0 ]; then
        echo "✅ CloudFront cache invalidated!"
        echo ""
        echo "🎉 Deployment complete!"
        echo "Wait 2-3 minutes for CloudFront to propagate changes."
        echo "Then test at: https://stonkmarketanalyzer.com"
    else
        echo "❌ CloudFront invalidation failed"
        exit 1
    fi
else
    echo "❌ S3 upload failed"
    exit 1
fi

echo ""
echo "✅ Deployment complete!"
