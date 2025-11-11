# Deployment Scripts

This directory contains all the scripts and configurations needed to deploy Stonk Market Analyzer to AWS.

## Files Overview

- **DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
- **quick-deploy.sh** - Automated deployment script (recommended)
- **backend-setup.sh** - EC2 backend setup script
- **frontend-deploy.sh** - S3 frontend deployment script
- **cloudfront-setup.sh** - CloudFront HTTPS setup (optional)
- **production.env.example** - Production environment variables template

## Quick Start (Recommended)

### Prerequisites

1. AWS CLI installed and configured
2. EC2 instance launched with security group allowing ports 22, 80, 443
3. SSH key pair for EC2 access
4. Perplexity API key

### One-Command Deployment

```bash
# Make script executable
chmod +x deployment/quick-deploy.sh

# Run deployment
./deployment/quick-deploy.sh
```

The script will:
1. Find your EC2 instance (or ask for IP)
2. Ask for your SSH key path
3. Ask for your Perplexity API key
4. Deploy backend to EC2
5. Deploy frontend to S3
6. Configure everything automatically

## Manual Deployment

If you prefer manual control, follow the detailed guide in `DEPLOYMENT_GUIDE.md`.

## Post-Deployment

### Test Your Application

```bash
# Test backend
curl http://<EC2_IP>/api/health

# Access frontend
open http://stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com
```

### Set Up HTTPS (Recommended)

```bash
chmod +x deployment/cloudfront-setup.sh
./deployment/cloudfront-setup.sh
```

## Architecture

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  S3 Bucket  │   │ EC2 Instance│
│  (Frontend) │   │  (Backend)  │
│   React     │   │    Flask    │
└─────────────┘   └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Perplexity  │
                  │     API     │
                  └─────────────┘
```

## Cost Estimate

- EC2 t2.micro: ~$8-10/month (free tier eligible)
- S3 + Data Transfer: ~$1-2/month
- CloudFront (optional): ~$1-5/month
- **Total: ~$10-15/month**

## Support

For issues or questions, refer to the troubleshooting section in `DEPLOYMENT_GUIDE.md`.
