#!/bin/bash
# Setup Cache Warming with Security Controls

set -e

EC2_IP="100.27.225.93"
SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"

echo "=== Setting Up Secure Cache Warming ==="
echo ""

# Step 1: Generate secure secret
echo "Step 1: Generating secure secret..."
CACHE_SECRET=$(openssl rand -hex 32)
echo "Generated secret: $CACHE_SECRET"
echo "⚠️  SAVE THIS SECRET - You'll need it to run cache warming"
echo ""

# Step 2: Upload cache warmer
echo "Step 2: Uploading cache warmer to EC2..."
scp -i "$SSH_KEY" backend/cache_warmer.py ec2-user@$EC2_IP:/tmp/
echo "✓ Uploaded"
echo ""

# Step 3: Install on EC2
echo "Step 3: Installing cache warmer..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << ENDSSH
    # Move to backend directory
    sudo mv /tmp/cache_warmer.py /opt/stonkmarketanalyzer/backend/
    sudo chown ec2-user:ec2-user /opt/stonkmarketanalyzer/backend/cache_warmer.py
    sudo chmod 750 /opt/stonkmarketanalyzer/backend/cache_warmer.py
    
    # Create logs directory
    sudo mkdir -p /opt/stonkmarketanalyzer/logs
    sudo chown ec2-user:ec2-user /opt/stonkmarketanalyzer/logs
    
    echo "✓ Cache warmer installed"
ENDSSH

# Step 4: Add secret to .env
echo ""
echo "Step 4: Adding secret to .env..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << ENDSSH
    # Add secret to .env if not already present
    if ! grep -q "CACHE_WARMER_SECRET" /opt/stonkmarketanalyzer/backend/.env; then
        echo "" | sudo tee -a /opt/stonkmarketanalyzer/backend/.env
        echo "# Cache Warmer Security" | sudo tee -a /opt/stonkmarketanalyzer/backend/.env
        echo "CACHE_WARMER_SECRET=$CACHE_SECRET" | sudo tee -a /opt/stonkmarketanalyzer/backend/.env
        echo "✓ Secret added to .env"
    else
        echo "⚠️  CACHE_WARMER_SECRET already exists in .env"
    fi
ENDSSH

# Step 5: Setup cron job
echo ""
echo "Step 5: Setting up daily cron job..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    # Create cron job to run daily at 2 AM
    CRON_JOB="0 2 * * * cd /opt/stonkmarketanalyzer/backend && /usr/bin/python3 cache_warmer.py >> /opt/stonkmarketanalyzer/logs/cache_warmer_cron.log 2>&1"
    
    # Check if cron job already exists
    if ! crontab -l 2>/dev/null | grep -q "cache_warmer.py"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        echo "✓ Cron job added (runs daily at 2 AM)"
    else
        echo "⚠️  Cron job already exists"
    fi
    
    # Show current crontab
    echo ""
    echo "Current crontab:"
    crontab -l | grep cache_warmer || echo "No cache warmer cron jobs"
ENDSSH

# Step 6: Test run (optional)
echo ""
echo "Step 6: Would you like to run a test? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Running test cache warming (this will take a few minutes)..."
    ssh -i "$SSH_KEY" ec2-user@$EC2_IP << ENDSSH
        cd /opt/stonkmarketanalyzer/backend
        /usr/bin/python3 cache_warmer.py 2>&1 | tail -20
ENDSSH
    echo ""
    echo "✓ Test completed - check logs above"
fi

echo ""
echo "=========================================="
echo "✅ CACHE WARMING SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  • Cache warmer: /opt/stonkmarketanalyzer/backend/cache_warmer.py"
echo "  • Logs: /opt/stonkmarketanalyzer/logs/cache_warmer.log"
echo "  • Cron: Daily at 2 AM"
echo "  • Secret: Stored in .env"
echo ""
echo "Manual Run:"
echo "  ssh -i $SSH_KEY ec2-user@$EC2_IP"
echo "  cd /opt/stonkmarketanalyzer/backend"
echo "  python3 cache_warmer.py"
echo ""
echo "View Logs:"
echo "  ssh -i $SSH_KEY ec2-user@$EC2_IP"
echo "  tail -f /opt/stonkmarketanalyzer/logs/cache_warmer.log"
echo ""
echo "Security:"
echo "  • Secret required to run"
echo "  • Rate limited (10 req/min)"
echo "  • Input validation"
echo "  • Comprehensive logging"
echo ""
