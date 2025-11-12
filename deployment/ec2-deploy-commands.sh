#!/bin/bash
# Commands to run on EC2 - Copy and paste into SSH session

cd /home/ec2-user
aws s3 cp s3://stonkmarketanalyzer-frontend-1762843094/deploy/backend-auth.tar.gz .
mv backend backend-backup-$(date +%Y%m%d) 2>/dev/null || true
mkdir -p backend && tar -xzf backend-auth.tar.gz -C backend/
cd backend
pip3 install --user bcrypt==4.1.2
pip3 install --user -r requirements.txt
pkill -f 'python3 app.py' || true
nohup python3 app.py > app.log 2>&1 &
sleep 2 && pgrep -f 'python3 app.py' && echo '✅ Backend running' || echo '❌ Failed'
curl http://localhost:3001/api/health
