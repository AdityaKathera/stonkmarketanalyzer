#!/bin/bash

# Test Analytics - Generate Sample Data
# This script simulates user activity to populate the admin portal

API_URL="https://api.stonkmarketanalyzer.com"

echo "🧪 Generating sample analytics data..."

# Simulate different users
USER_IDS=("user_001" "user_002" "user_003" "user_004" "user_005")
SESSION_IDS=("session_a" "session_b" "session_c" "session_d" "session_e")
STOCKS=("AAPL" "TSLA" "GOOGL" "MSFT" "AMZN" "NVDA" "META")

# Function to track event
track_event() {
    local event=$1
    local user=$2
    local session=$3
    local ticker=$4
    
    curl -s -X POST "$API_URL/api/analytics" \
        -H "Content-Type: application/json" \
        -d "{
            \"event\": \"$event\",
            \"userId\": \"$user\",
            \"sessionId\": \"$session\",
            \"ticker\": \"$ticker\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }" > /dev/null
}

# Simulate page views
echo "📊 Simulating page views..."
for i in {1..5}; do
    user=${USER_IDS[$((i-1))]}
    session=${SESSION_IDS[$((i-1))]}
    track_event "page_view" "$user" "$session" ""
    sleep 0.2
done

# Simulate stock searches
echo "🔍 Simulating stock searches..."
for i in {1..20}; do
    user=${USER_IDS[$((RANDOM % 5))]}
    session=${SESSION_IDS[$((RANDOM % 5))]}
    stock=${STOCKS[$((RANDOM % 7))]}
    track_event "stock_search" "$user" "$session" "$stock"
    sleep 0.1
done

# Simulate research queries
echo "📈 Simulating research queries..."
RESEARCH_TYPES=("fundamentals" "news" "technical" "overview")
for i in {1..15}; do
    user=${USER_IDS[$((RANDOM % 5))]}
    session=${SESSION_IDS[$((RANDOM % 5))]}
    stock=${STOCKS[$((RANDOM % 7))]}
    research=${RESEARCH_TYPES[$((RANDOM % 4))]}
    track_event "research_$research" "$user" "$session" "$stock"
    sleep 0.1
done

# Simulate chat queries
echo "💬 Simulating chat queries..."
for i in {1..10}; do
    user=${USER_IDS[$((RANDOM % 5))]}
    session=${SESSION_IDS[$((RANDOM % 5))]}
    stock=${STOCKS[$((RANDOM % 7))]}
    track_event "chat_query" "$user" "$session" "$stock"
    sleep 0.1
done

# Simulate comparisons
echo "⚖️  Simulating stock comparisons..."
for i in {1..5}; do
    user=${USER_IDS[$((RANDOM % 5))]}
    session=${SESSION_IDS[$((RANDOM % 5))]}
    stock1=${STOCKS[$((RANDOM % 7))]}
    stock2=${STOCKS[$((RANDOM % 7))]}
    track_event "stock_comparison" "$user" "$session" "$stock1,$stock2"
    sleep 0.1
done

echo ""
echo "✅ Sample data generated!"
echo ""
echo "📊 Now refresh your admin portal to see:"
echo "   - User activity"
echo "   - Popular stocks (AAPL, TSLA, GOOGL, etc.)"
echo "   - Research queries"
echo "   - Chat interactions"
echo "   - Stock comparisons"
echo ""
echo "🌐 Admin Portal: https://api.stonkmarketanalyzer.com/portal/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg"
echo ""
