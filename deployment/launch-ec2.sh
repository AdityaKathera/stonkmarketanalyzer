#!/bin/bash
# Launch EC2 Instance for Stonk Market Analyzer

set -e

echo "=== Launching EC2 Instance for Stonk Market Analyzer ==="
echo ""

# Configuration
INSTANCE_TYPE="t2.micro"
REGION="us-east-1"
AMI_ID="ami-0c55b159cbfafe1f0"  # Amazon Linux 2 in us-east-1

# Check if AWS CLI is configured
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

# Get or create key pair
echo "Checking for SSH key pair..."
read -p "Enter your SSH key pair name (or press Enter to create new): " KEY_NAME

if [ -z "$KEY_NAME" ]; then
    KEY_NAME="stonkmarketanalyzer-key"
    echo "Creating new key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "Key saved to: ${KEY_NAME}.pem"
else
    echo "Using existing key pair: $KEY_NAME"
fi

# Get default VPC
echo "Getting default VPC..."
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text \
    --region $REGION)

if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
    echo "Error: No default VPC found. Please create one or specify a VPC ID."
    exit 1
fi

echo "Using VPC: $VPC_ID"

# Create security group
echo "Creating security group..."
SG_NAME="stonkmarketanalyzer-sg"

# Check if security group exists
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SG_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region $REGION 2>/dev/null || echo "None")

if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
    echo "Creating new security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for Stonk Market Analyzer" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Add inbound rules
    echo "Adding security group rules..."
    
    # SSH
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # HTTP
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # HTTPS
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "Security group created: $SG_ID"
else
    echo "Using existing security group: $SG_ID"
fi

# Get latest Amazon Linux 2 AMI
echo "Getting latest Amazon Linux 2 AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region $REGION)

echo "Using AMI: $AMI_ID"

# Launch instance
echo ""
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=stonkmarketanalyzer-backend}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance launched: $INSTANCE_ID"
echo "Waiting for instance to be running..."

# Wait for instance to be running
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region $REGION)

echo ""
echo "=== EC2 Instance Launched Successfully! ==="
echo ""
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "SSH Key: ${KEY_NAME}.pem (if newly created)"
echo "Security Group: $SG_ID"
echo ""
echo "Wait 1-2 minutes for the instance to fully initialize, then run:"
echo ""
echo "  ./deployment/quick-deploy.sh"
echo ""
echo "Or connect via SSH:"
echo ""
echo "  ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""

# Save instance info
cat > deployment/instance-info.txt <<EOF
Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
SSH Key: ${KEY_NAME}.pem
Security Group: $SG_ID
Region: $REGION
Launched: $(date)
EOF

echo "Instance info saved to: deployment/instance-info.txt"
