#!/bin/bash
cd /opt/stonkmarketanalyzer/backend
source venv/bin/activate
pkill -9 -f "python.*app.py" 2>/dev/null || true
sleep 2
nohup python3 app.py > backend.log 2>&1 &
sleep 3
echo "Backend restarted. Checking logs..."
tail -30 backend.log
