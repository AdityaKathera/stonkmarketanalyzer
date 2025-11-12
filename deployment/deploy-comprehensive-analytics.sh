#!/bin/bash
# Deploy Comprehensive Analytics Backend Update

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
    echo "Please check:"
    echo "  1. EC2 instance is running"
    echo "  2. SSH key path is correct"
    echo "  3. Security group allows SSH from your IP"
    exit 1
fi

echo ""
echo "Step 2: Backing up current backend..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    cd /opt/stonkmarketanalyzer
    
    # Create backup
    BACKUP_DIR="/home/ec2-user/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    sudo cp -r backend "$BACKUP_DIR/"
    echo "✓ Backup created at: $BACKUP_DIR"
ENDSSH

echo ""
echo "Step 3: Pulling latest code from GitHub..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    cd /opt/stonkmarketanalyzer
    
    # Pull latest changes
    sudo git fetch origin
    sudo git pull origin main
    
    echo "✓ Code updated from GitHub"
ENDSSH

echo ""
echo "Step 4: Installing dependencies..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    cd /opt/stonkmarketanalyzer/backend
    
    # Install psutil for system health monitoring
    sudo pip3 install psutil
    
    echo "✓ Dependencies installed"
ENDSSH

echo ""
echo "Step 5: Verifying new files..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    cd /opt/stonkmarketanalyzer/backend
    
    echo "Checking for new files:"
    if [ -f "analytics_comprehensive.py" ]; then
        echo "  ✓ analytics_comprehensive.py found"
    else
        echo "  ❌ analytics_comprehensive.py NOT found"
        exit 1
    fi
    
    echo "Checking app.py for comprehensive analytics import:"
    if grep -q "ComprehensiveAnalytics" app.py; then
        echo "  ✓ app.py uses ComprehensiveAnalytics"
    else
        echo "  ❌ app.py does NOT use ComprehensiveAnalytics"
        exit 1
    fi
    
    echo "Checking secure_portal.py for new endpoints:"
    if grep -q "analytics/revenue" secure_portal.py; then
        echo "  ✓ New endpoints found in secure_portal.py"
    else
        echo "  ❌ New endpoints NOT found"
        exit 1
    fi
ENDSSH

echo ""
echo "Step 6: Restarting backend service..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    # Restart the service
    sudo systemctl restart stonkmarketanalyzer
    
    # Wait for service to start
    sleep 3
    
    # Check if service is running
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
echo "Step 7: Verifying API health..."
sleep 2
HEALTH_CHECK=$(curl -s https://api.stonkmarketanalyzer.com/api/health)
if echo "$HEALTH_CHECK" | grep -q "ok"; then
    echo "✓ API is responding correctly"
    echo "Response: $HEALTH_CHECK"
else
    echo "❌ API health check failed"
    echo "Response: $HEALTH_CHECK"
    exit 1
fi

echo ""
echo "Step 8: Testing new endpoints..."
echo "Note: You'll need to login to admin portal to get auth token for full testing"
echo ""
echo "Testing public endpoints:"

# Test if new endpoints exist (will return 401 without auth, which is expected)
REVENUE_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/revenue)
if [ "$REVENUE_TEST" == "401" ]; then
    echo "  ✓ Revenue endpoint exists (requires auth)"
else
    echo "  ⚠️  Revenue endpoint returned: $REVENUE_TEST (expected 401)"
fi

BEHAVIOR_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/analytics/user-behavior)
if [ "$BEHAVIOR_TEST" == "401" ]; then
    echo "  ✓ User behavior endpoint exists (requires auth)"
else
    echo "  ⚠️  User behavior endpoint returned: $BEHAVIOR_TEST (expected 401)"
fi

HEALTH_FULL_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6/system/health-full)
if [ "$HEALTH_FULL_TEST" == "401" ]; then
    echo "  ✓ System health endpoint exists (requires auth)"
else
    echo "  ⚠️  System health endpoint returned: $HEALTH_FULL_TEST (expected 401)"
fi

echo ""
echo "Step 9: Checking backend logs..."
ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    echo "Last 10 lines of backend logs:"
    sudo journalctl -u stonkmarketanalyzer -n 10 --no-pager
ENDSSH

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Login to admin portal: https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html"
echo "2. All new sections should now show real data instead of 'N/A'"
echo "3. Use the main site to generate activity"
echo "4. Watch the metrics populate in real-time"
echo ""
echo "New Features Now Active:"
echo "  ✓ Revenue & Usage Metrics"
echo "  ✓ User Behavior Analytics"
echo "  ✓ System Health Monitoring"
echo "  ✓ Performance Tracking"
echo "  ✓ Enhanced Activity Feed"
echo "  ✓ Clear Cache Action"
echo ""
echo "If you see any issues, check logs with:"
echo "  ssh -i $SSH_KEY ec2-user@$EC2_IP"
echo "  sudo journalctl -u stonkmarketanalyzer -f"
echo ""
