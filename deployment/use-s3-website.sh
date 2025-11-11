#!/bin/bash
# Deploy to S3 website (HTTP) to match HTTP backend

set -e

BUCKET_NAME="stonkmarketanalyzer-frontend-1762843094"
REGION="us-east-1"

echo "=== Using S3 Website URL (HTTP) ==="
echo ""
echo "S3 Website URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "This works because both frontend (HTTP) and backend (HTTP) match."
echo ""
echo "To use CloudFront (HTTPS), you need to add HTTPS to your backend."
echo ""
echo "Open this URL in your browser:"
echo "  http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
