#!/bin/bash

# Complete SSL Setup for Stonk Market Analyzer
# Run this script once the ACM certificate is validated

set -e

CERT_ARN="arn:aws:acm:us-east-1:938611073268:certificate/ad6daf32-6c76-4fe3-bf96-844a86ed8ce7"
CF_DIST_ID="E2UZFZ0XAK8XWJ"
HOSTED_ZONE_ID="Z07899091G39QGMKGKW2P"

echo "🔍 Checking certificate status..."
CERT_STATUS=$(aws acm describe-certificate --certificate-arn $CERT_ARN --region us-east-1 --query 'Certificate.Status' --output text)

if [ "$CERT_STATUS" != "ISSUED" ]; then
    echo "❌ Certificate is not yet validated. Status: $CERT_STATUS"
    echo "Please wait for AWS to validate the certificate (usually 5-30 minutes)"
    echo "Check status with: aws acm describe-certificate --certificate-arn $CERT_ARN --region us-east-1 --query 'Certificate.Status'"
    exit 1
fi

echo "✅ Certificate is validated!"

# Get current CloudFront config
echo "📥 Getting CloudFront distribution config..."
aws cloudfront get-distribution-config --id $CF_DIST_ID > /tmp/cf-config.json
ETAG=$(jq -r '.ETag' /tmp/cf-config.json)

# Update config with custom domains and SSL
echo "🔧 Updating CloudFront configuration..."
jq '.DistributionConfig.Aliases = {
    "Quantity": 2,
    "Items": ["stonkmarketanalyzer.com", "www.stonkmarketanalyzer.com"]
} | .DistributionConfig.ViewerCertificate = {
    "ACMCertificateArn": "'$CERT_ARN'",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021",
    "Certificate": "'$CERT_ARN'",
    "CertificateSource": "acm"
}' /tmp/cf-config.json | jq '.DistributionConfig' > /tmp/cf-update.json

# Update CloudFront
echo "☁️  Updating CloudFront distribution..."
aws cloudfront update-distribution \
    --id $CF_DIST_ID \
    --distribution-config file:///tmp/cf-update.json \
    --if-match $ETAG > /dev/null

echo "✅ CloudFront updated! Waiting for deployment..."

# Wait for CloudFront to deploy
echo "⏳ This may take 5-15 minutes..."
aws cloudfront wait distribution-deployed --id $CF_DIST_ID

# Get CloudFront domain
CF_DOMAIN=$(aws cloudfront get-distribution --id $CF_DIST_ID --query 'Distribution.DomainName' --output text)
echo "✅ CloudFront deployed: $CF_DOMAIN"

# Update Route53 A records
echo "🌐 Updating DNS records..."

# Update stonkmarketanalyzer.com
aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "stonkmarketanalyzer.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "'$CF_DOMAIN'",
        "EvaluateTargetHealth": false
      }
    }
  }]
}' > /dev/null

# Update www.stonkmarketanalyzer.com
aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "www.stonkmarketanalyzer.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "'$CF_DOMAIN'",
        "EvaluateTargetHealth": false
      }
    }
  }]
}' > /dev/null

echo "✅ DNS records updated!"

# Cleanup
rm -f /tmp/cf-config.json /tmp/cf-update.json

echo ""
echo "🎉 SSL Setup Complete!"
echo "========================"
echo ""
echo "Your site will be available at:"
echo "  https://stonkmarketanalyzer.com"
echo "  https://www.stonkmarketanalyzer.com"
echo ""
echo "Note: DNS propagation may take a few minutes."
echo "Test with: curl -I https://stonkmarketanalyzer.com"
echo ""
