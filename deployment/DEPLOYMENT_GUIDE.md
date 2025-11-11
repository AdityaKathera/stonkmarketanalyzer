# Stonk Market Analyzer - AWS Deployment Guide

This guide will help you deploy the Stonk Market Analyzer to AWS with the backend on EC2 and frontend on S3.

## Prerequisites

1. AWS CLI installed and configured
2. AWS account with appropriate permissions
3. IAM role: `arn:aws:iam::938611073268:role/stonkmarketanalyzer`
4. SSH key pair for EC2 access

## Architecture

- **Backend**: Flask API on EC2 instance (with Nginx reverse proxy)
- **Frontend**: React app on S3 (static website hosting)
- **API**: Perplexity AI for stock analysis

## Step 1: Prepare Your Environment

### Assume the AWS Role

```bash
# Configure AWS CLI to assume the role
aws sts assume-role \
    --role-arn arn:aws:iam::938611073268:role/stonkmarketanalyzer \
    --role-session-name stonk-deployment

# Export the credentials (replace with actual values from above command)
export AWS_ACCESS_KEY_ID=<AccessKeyId>
export AWS_SECRET_ACCESS_KEY=<SecretAccessKey>
export AWS_SESSION_TOKEN=<SessionToken>
```

## Step 2: Deploy Backend to EC2

### 2.1 Launch EC2 Instance

```bash
# Create security group
aws ec2 create-security-group \
    --group-name stonkmarketanalyzer-sg \
    --description "Security group for Stonk Market Analyzer" \
    --vpc-id <your-vpc-id>

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-name stonkmarketanalyzer-sg \
    --protocol tcp --port 22 --cidr 0.0.0.0/0  # SSH

aws ec2 authorize-security-group-ingress \
    --group-name stonkmarketanalyzer-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0  # HTTP

aws ec2 authorize-security-group-ingress \
    --group-name stonkmarketanalyzer-sg \
    --protocol tcp --port 443 --cidr 0.0.0.0/0  # HTTPS

# Launch EC2 instance (Amazon Linux 2)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name <your-key-pair-name> \
    --security-groups stonkmarketanalyzer-sg \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=stonkmarketanalyzer-backend}]'
```

### 2.2 Connect to EC2 and Setup Backend

```bash
# Get the public IP
EC2_IP=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=stonkmarketanalyzer-backend" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "EC2 Public IP: $EC2_IP"

# SSH into the instance
ssh -i <your-key.pem> ec2-user@$EC2_IP
```

### 2.3 Upload Backend Files

From your local machine:

```bash
# Create a deployment package
cd backend
tar -czf backend.tar.gz .

# Upload to EC2
scp -i <your-key.pem> backend.tar.gz ec2-user@$EC2_IP:/home/ec2-user/

# Upload setup script
scp -i <your-key.pem> ../deployment/backend-setup.sh ec2-user@$EC2_IP:/home/ec2-user/
```

### 2.4 Run Setup Script on EC2

SSH back into EC2:

```bash
ssh -i <your-key.pem> ec2-user@$EC2_IP

# Extract backend files
sudo mkdir -p /opt/stonkmarketanalyzer/backend
sudo tar -xzf backend.tar.gz -C /opt/stonkmarketanalyzer/backend
sudo chown -R ec2-user:ec2-user /opt/stonkmarketanalyzer

# Create .env file with your Perplexity API key
cat > /opt/stonkmarketanalyzer/backend/.env <<EOF
PERPLEXITY_API_KEY=your_actual_api_key_here
PORT=3001
NODE_ENV=production
EOF

# Run setup script
chmod +x backend-setup.sh
./backend-setup.sh

# Verify backend is running
curl http://localhost:3001/api/health
```

## Step 3: Deploy Frontend to S3

From your local machine:

```bash
# Make the deployment script executable
chmod +x deployment/frontend-deploy.sh

# Deploy frontend (replace with your EC2 public IP or domain)
./deployment/frontend-deploy.sh http://$EC2_IP
```

## Step 4: Configure CORS

Update the backend to allow requests from your S3 website URL:

```bash
# SSH into EC2
ssh -i <your-key.pem> ec2-user@$EC2_IP

# Edit app.py to update CORS settings
sudo nano /opt/stonkmarketanalyzer/backend/app.py
```

Update the CORS configuration:

```python
CORS(app, origins=[
    "http://stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com",
    "http://localhost:5173"  # Keep for local development
])
```

Restart the service:

```bash
sudo systemctl restart stonkmarketanalyzer
```

## Step 5: Access Your Application

Your application is now live!

- **Frontend**: http://stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com
- **Backend API**: http://<EC2_PUBLIC_IP>/api/health

## Optional: Set Up CloudFront (Recommended)

For HTTPS and better performance:

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name stonkmarketanalyzer-frontend.s3-website-us-east-1.amazonaws.com \
    --default-root-object index.html
```

## Optional: Set Up Route 53 (Custom Domain)

If you have a domain:

1. Create a hosted zone in Route 53
2. Point your domain to CloudFront distribution
3. Request SSL certificate in ACM
4. Update CloudFront to use custom domain and SSL

## Monitoring and Maintenance

### Check Backend Logs

```bash
ssh -i <your-key.pem> ec2-user@$EC2_IP
sudo journalctl -u stonkmarketanalyzer -f
```

### Update Backend

```bash
# On your local machine
cd backend
tar -czf backend.tar.gz .
scp -i <your-key.pem> backend.tar.gz ec2-user@$EC2_IP:/home/ec2-user/

# On EC2
ssh -i <your-key.pem> ec2-user@$EC2_IP
sudo systemctl stop stonkmarketanalyzer
sudo tar -xzf backend.tar.gz -C /opt/stonkmarketanalyzer/backend
sudo systemctl start stonkmarketanalyzer
```

### Update Frontend

```bash
./deployment/frontend-deploy.sh http://$EC2_IP
```

## Cost Estimation

- **EC2 t2.micro**: ~$8-10/month (free tier eligible)
- **S3 Storage**: ~$0.50/month for typical usage
- **Data Transfer**: Variable based on traffic
- **Total**: ~$10-15/month

## Security Best Practices

1. ✅ Use HTTPS (CloudFront + ACM)
2. ✅ Restrict EC2 security group to specific IPs if possible
3. ✅ Store API keys in AWS Secrets Manager
4. ✅ Enable CloudWatch monitoring
5. ✅ Set up automated backups
6. ✅ Use IAM roles instead of access keys where possible

## Troubleshooting

### Backend not responding

```bash
sudo systemctl status stonkmarketanalyzer
sudo journalctl -u stonkmarketanalyzer -n 50
```

### Frontend not loading

- Check S3 bucket policy
- Verify public access settings
- Check browser console for CORS errors

### API errors

- Verify Perplexity API key is correct
- Check backend logs for errors
- Test API directly: `curl http://<EC2_IP>/api/health`

## Cleanup (To Remove Everything)

```bash
# Delete S3 bucket
aws s3 rb s3://stonkmarketanalyzer-frontend --force

# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids <instance-id>

# Delete security group
aws ec2 delete-security-group --group-name stonkmarketanalyzer-sg
```
