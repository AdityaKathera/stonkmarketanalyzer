#!/bin/bash
# Deploy Comprehensive Analytics Backend Update (Direct Upload)

set -e

EC2_IP="100.27.225.93"
SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"

echo "=== Deploying Comprehensive Analytics Backend ==="
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found at: $SSH_KEY"
    echo "Please update the SSH_KEY variable in this script"
    exit 1
fi

echo "Step 1: Testing SSH connection..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=5 ec2-user@$EC2_IP "echo 'Connection successful'" 2>/dev/null; then
    echo "✓ SSH connection successful"
else
    echo "❌ Cannot connect to EC2 instance"
    exit 1
fi

echo ""
echo "Step 2: Creating backup..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    cd /opt/stonkmarketanalyzer
    BACKUP_DIR="/home/ec2-user/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    sudo cp -r backend "$BACKUP_DIR/"
    echo "✓ Backup created at: $BACKUP_DIR"
ENDSSH

echo ""
echo "Step 3: Preparing files for upload..."
cd "$(dirname "$0")/.."

# Create temp directory with files to upload
TEMP_DIR=$(mktemp -d)
cp backend/analytics_comprehensive.py "$TEMP_DIR/"
cp backend/app.py "$TEMP_DIR/"
cp backend/secure_portal.py "$TEMP_DIR/"

echo "✓ Files prepared"

echo ""
echo "Step 4: Uploading new files to EC2..."
scp -i "$SSH_KEY" "$TEMP_DIR/analytics_comprehensive.py" ec2-user@$EC2_IP:/tmp/
scp -i "$SSH_KEY" "$TEMP_DIR/app.py" ec2-user@$EC2_IP:/tmp/
scp -i "$SSH_KEY" "$TEMP_DIR/secure_portal.py" ec2-user@$EC2_IP:/tmp/

echo "✓ Files uploaded"

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo ""
echo "Step 5: Installing files on EC2..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    # Move files to backend directory
    sudo mv /tmp/analytics_comprehensive.py /opt/stonkmarketanalyzer/backend/
    sudo mv /tmp/app.py /opt/stonkmarketanalyzer/backend/
    sudo mv /tmp/secure_portal.py /opt/stonkmarketanalyzer/backend/
    
    # Set proper ownership
    sudo chown ec2-user:ec2-user /opt/stonkmarketanalyzer/backend/*.py
    
    echo "✓ Files installed"
ENDSSH

echo ""
echo "Step 6: Installing dependencies..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    # Install psutil for system health monitoring
    sudo pip3 install psutil
    echo "✓ Dependencies installed"
ENDSSH

echo ""
echo "Step 7: Verifying installation..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    cd /opt/stonkmarketanalyzer/backend
    
    echo "Checking files:"
    if [ -f "analytics_comprehensive.py" ]; then
        echo "  ✓ analytics_comprehensive.py"
    else
        echo "  ❌ analytics_comprehensive.py NOT found"
        exit 1
    fi
    
    if grep -q "ComprehensiveAnalytics" app.py; then
        echo "  ✓ app.py uses ComprehensiveAnalytics"
    else
        echo "  ❌ app.py does NOT use ComprehensiveAnalytics"
        exit 1
    fi
    
    if grep -q "analytics/revenue" secure_portal.py; then
        echo "  ✓ New endpoints in secure_portal.py"
    else
        echo "  ❌ New endpoints NOT found"
        exit 1
    fi
ENDSSH

echo ""
echo "Step 8: Restarting backend service..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    sudo systemctl restart stonkmarketanalyzer
    sleep 3
    
    if sudo systemctl is-active --quiet stonkmarketanalyzer; then
        echo "✓ Service restarted successfully"
    else
        echo "❌ Service failed to start"
        echo "Checking logs:"
        sudo journalctl -u stonkmarketanalyzer -n 20 --no-pager
        exit 1
    fi
ENDSSH

echo ""
echo "Step 9: Verifying API health..."
sleep 2
HEALTH_CHECK=$(curl -s https://api.stonkmarketanalyzer.com/api/health)
if echo "$HEALTH_CHECK" | grep -q "ok"; then
    echo "✓ API is responding"
    echo "Response: $HEALTH_CHECK"
else
    echo "❌ API health check failed"
    echo "Response: $HEALTH_CHECK"
    exit 1
fi

echo ""
echo "Step 10: Testing new endpoints..."
REVENUE_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/revenue)
if [ "$REVENUE_TEST" == "401" ]; then
    echo "  ✓ Revenue endpoint exists (requires auth)"
else
    echo "  ⚠️  Revenue endpoint: $REVENUE_TEST"
fi

BEHAVIOR_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/user-behavior)
if [ "$BEHAVIOR_TEST" == "401" ]; then
    echo "  ✓ User behavior endpoint exists (requires auth)"
else
    echo "  ⚠️  User behavior endpoint: $BEHAVIOR_TEST"
fi

echo ""
echo "Step 11: Checking logs..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    echo "Recent logs:"
    sudo journalctl -u stonkmarketanalyzer -n 10 --no-pager
ENDSSH

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🎉 All new features are now active!"
echo ""
echo "Test it now:"
echo "1. Go to: https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html"
echo "2. Login to admin portal"
echo "3. All sections should show real data"
echo "4. Use main site to generate activity"
echo "5. Watch metrics update in real-time"
echo ""
echo "New Features Active:"
echo "  ✓ Revenue & Usage Metrics"
echo "  ✓ User Behavior Analytics"
echo "  ✓ System Health Monitoring"
echo "  ✓ Performance Tracking"
echo "  ✓ Enhanced Activity Feed"
echo "  ✓ Clear Cache Action"
echo ""
