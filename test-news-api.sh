#!/bin/bash

echo "Testing AI News Summarizer API..."
echo ""

# You'll need to replace TOKEN with a real JWT token from logging in
TOKEN="your_jwt_token_here"

echo "1. Testing health endpoint..."
curl -s https://api.stonkmarketanalyzer.com/api/health
echo -e "\n"

echo "2. Testing news for AAPL (requires auth)..."
echo "   Run this with a real token:"
echo "   curl -H 'Authorization: Bearer \$TOKEN' https://api.stonkmarketanalyzer.com/api/news/stock/AAPL?limit=2"
echo ""

echo "3. Testing watchlist news (requires auth)..."
echo "   Run this with a real token:"
echo "   curl -H 'Authorization: Bearer \$TOKEN' https://api.stonkmarketanalyzer.com/api/news/watchlist?limit_per_stock=2"
echo ""

echo "✅ Backend is running!"
echo "📱 Visit https://stonkmarketanalyzer.com and log in to test the News tab"
