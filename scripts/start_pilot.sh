#!/usr/bin/env bash
# AIMOS Pilot Mode — Local-to-Bubble Automation
# This script starts a public tunnel and automatically syncs your local environment with Bubble.io.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "🚀 Starting AIMOS Pilot Mode..."

# 1. Ensure Docker stack is up
if ! docker compose ps api | grep -q "Up"; then
  echo "📦 Starting Docker stack..."
  ./setup.sh
fi

# 2. Get local port from docker-compose or default to 8000
PORT=8000

# 3. Start Tunnel (using LocalTunnel - zero login, free)
# We use npx to avoid requiring global install
echo "🌐 Starting Public Tunnel (localtunnel)..."
LT_OUTPUT_FILE="/tmp/lt_output.txt"
rm -f "$LT_OUTPUT_FILE"

# Start lt in background and capture URL
npx localtunnel --port "$PORT" > "$LT_OUTPUT_FILE" 2>&1 &
LT_PID=$!

# Wait for URL to appear (usually 2-5 seconds)
# Format is: "your url is: https://..."
echo "⏳ Waiting for public URL..."
PUBLIC_URL=""
for _ in $(seq 1 10); do
  if grep -q "your url is:" "$LT_OUTPUT_FILE"; then
    PUBLIC_URL=$(grep "your url is:" "$LT_OUTPUT_FILE" | awk '{print $NF}')
    break
  fi
  sleep 2
done

if [[ -z "$PUBLIC_URL" ]]; then
  echo "❌ Error: Could not obtain public tunnel URL."
  kill $LT_PID
  exit 1
fi

echo "✅ Public URL obtained: $PUBLIC_URL"

# 4. Update .env (PUBLIC_API_BASE_URL and CORS_ORIGINS)
# We use Python to handle .env updates safely
python3 -c "
import os
import sys

env_path = '.env'
new_url = sys.argv[1]

with open(env_path, 'r') as f:
    lines = f.readlines()

new_lines = []
found_base = False
found_cors = False

# Normalize URL (no trailing slash)
new_url = new_url.rstrip('/')

for line in lines:
    if line.startswith('PUBLIC_API_BASE_URL='):
        new_lines.append(f'PUBLIC_API_BASE_URL={new_url}\n')
        found_base = True
    elif line.startswith('CORS_ORIGINS='):
        # We append the new URL to existing CORS origins
        current = line.split('=')[1].strip()
        origins = [o.strip() for o in current.split(',')]
        if new_url not in origins:
            origins.append(new_url)
        if 'https://bubble.io' not in origins:
            origins.append('https://bubble.io')
        if 'https://bubbleapps.io' not in origins:
            origins.append('https://bubbleapps.io')
        new_lines.append(f'CORS_ORIGINS={",".join(origins)}\n')
        found_cors = True
    else:
        new_lines.append(line)

if not found_base:
    new_lines.append(f'PUBLIC_API_BASE_URL={new_url}\n')
if not found_cors:
    new_lines.append(f'CORS_ORIGINS={new_url},https://bubble.io,https://bubbleapps.io\n')

with open(env_path, 'w') as f:
    f.writelines(new_lines)

print(f'📝 Updated .env with PUBLIC_API_BASE_URL={new_url}')
" "$PUBLIC_URL"

# 5. Restart API to pick up new OpenAPI server URL
echo "🔄 Refreshing API container..."
docker compose restart api

# 6. Final Instructions
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🎈 AIMOS PILOT IS READY!"
echo " 🔗 Public URL:      $PUBLIC_URL"
echo " 📂 OpenAPI JSON:    $PUBLIC_URL/openapi.json"
echo " 📂 Swagger UI:     $PUBLIC_URL/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👉 Paste the OpenAPI JSON link into Bubble's API Connector."
echo "👉 Press Ctrl+C to stop the tunnel (URL will expire)."
echo ""

# Keep the script alive to maintain the tunnel
wait $LT_PID
