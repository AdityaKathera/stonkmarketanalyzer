#!/bin/bash

SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"
SERVER="ec2-user@100.27.225.93"

echo "🚀 Building and Deploying Frontend"
echo "==================================="

# Build frontend locally
echo "📦 Building frontend..."
cd frontend
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"

# Create tarball
echo "📦 Creating deployment package..."
cd dist
tar -czf ../../frontend-dist.tar.gz .
cd ../..

# Upload to server
echo "📤 Uploading to server..."
scp -i "$SSH_KEY" frontend-dist.tar.gz "$SERVER:/tmp/"

# Deploy on server
echo "🔧 Deploying on server..."
ssh -i "$SSH_KEY" "$SERVER" << 'EOF'
    sudo rm -rf /usr/share/nginx/html/*
    sudo tar -xzf /tmp/frontend-dist.tar.gz -C /usr/share/nginx/html/
    sudo chown -R nginx:nginx /usr/share/nginx/html/
    rm /tmp/frontend-dist.tar.gz
    echo "✅ Frontend deployed!"
EOF

# Cleanup
rm frontend-dist.tar.gz

echo ""
echo "✅ Deployment complete!"
echo "🌐 Visit: http://100.27.225.93"
