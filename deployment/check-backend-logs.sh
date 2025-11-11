#!/bin/bash
# Check backend logs and status

EC2_IP="100.27.225.93"
SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"

echo "=== Checking Backend Status ==="
echo ""

ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    echo "1. Service Status:"
    sudo systemctl status stonkmarketanalyzer --no-pager | head -20
    
    echo ""
    echo "2. Recent Logs (last 50 lines):"
    sudo journalctl -u stonkmarketanalyzer -n 50 --no-pager
    
    echo ""
    echo "3. Testing API Health:"
    curl -s http://localhost:3001/api/health || echo "Health check failed"
    
    echo ""
    echo "4. Checking .env file:"
    cat /opt/stonkmarketanalyzer/backend/.env | grep -v "PERPLEXITY_API_KEY"
ENDSSH
