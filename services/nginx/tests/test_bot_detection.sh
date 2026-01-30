#!/bin/bash
# Test script for verifying bot detection in nginx config
# Run this against a running nginx instance

set -e

NGINX_URL="${NGINX_URL:-http://localhost:8080}"
ENTITY_PATH="/MONDO:0005148"

echo "Testing bot detection at $NGINX_URL$ENTITY_PATH"
echo "================================================"

# Test 1: Regular browser should get index.html (200, text/html, contains Vue app markers)
echo -n "Test 1: Regular browser request... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    "$NGINX_URL$ENTITY_PATH")
if [ "$RESPONSE" = "200" ]; then
    echo "PASS (HTTP $RESPONSE)"
else
    echo "FAIL (HTTP $RESPONSE, expected 200)"
    exit 1
fi

# Test 2: Slackbot should be proxied to backend (check for og: tags in response)
echo -n "Test 2: Slackbot request... "
RESPONSE=$(curl -s \
    -H "User-Agent: Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

# Test 3: Twitterbot should be proxied to backend
echo -n "Test 3: Twitterbot request... "
RESPONSE=$(curl -s \
    -H "User-Agent: Twitterbot/1.0" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

# Test 4: Facebook crawler should be proxied to backend
echo -n "Test 4: Facebook crawler request... "
RESPONSE=$(curl -s \
    -H "User-Agent: facebookexternalhit/1.1" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

# Test 5: Discord bot should be proxied to backend
echo -n "Test 5: Discordbot request... "
RESPONSE=$(curl -s \
    -H "User-Agent: Discordbot/2.0" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

# Test 6: LinkedIn bot should be proxied to backend
echo -n "Test 6: LinkedInBot request... "
RESPONSE=$(curl -s \
    -H "User-Agent: LinkedInBot/1.0" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

# Test 7: Mastodon should be proxied to backend
echo -n "Test 7: Mastodon request... "
RESPONSE=$(curl -s \
    -H "User-Agent: Mastodon/4.3.2 (+https://mastodon.social/)" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

# Test 8: Bluesky should be proxied to backend
echo -n "Test 8: Bluesky request... "
RESPONSE=$(curl -s \
    -H "User-Agent: Mozilla/5.0 (compatible; Bluesky Cardyb/1.1; +mailto:support@bsky.app)" \
    "$NGINX_URL$ENTITY_PATH")
if echo "$RESPONSE" | grep -q "og:title"; then
    echo "PASS (contains og:title)"
else
    echo "FAIL (no og:title in response)"
    exit 1
fi

echo ""
echo "All tests passed!"
