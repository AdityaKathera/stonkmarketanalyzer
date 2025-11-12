#!/bin/bash
# Setup AWS SES for Admin Email

echo "📧 Setting up Admin Email with AWS SES"
echo "======================================"
echo ""

DOMAIN="stonkmarketanalyzer.com"
EMAIL="sentinel_65d3d147@stonkmarketanalyzer.com"

echo "Step 1: Verify domain in SES..."
aws ses verify-domain-identity --domain $DOMAIN

echo ""
echo "Step 2: Verify email address..."
aws ses verify-email-identity --email-address $EMAIL

echo ""
echo "✅ Verification emails sent!"
echo ""
echo "Next steps:"
echo "1. Check your email and click verification link"
echo "2. Add these DNS records to Route53:"
echo ""
echo "   Get DNS records:"
echo "   aws ses get-identity-verification-attributes --identities $DOMAIN"
echo ""
echo "3. Wait for verification (can take up to 72 hours)"
echo ""
echo "After verification, you can:"
echo "- Send emails from $EMAIL"
echo "- Receive admin alerts"
echo "- Get daily reports"
