#!/usr/bin/env bash
# One-command local bootstrap: .env → validate → docker compose → seed dev user.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example — set OPENAI_API_KEY and JWT_SECRET before running agents."
fi

python3 scripts/validate_env.py

docker compose up -d --build

echo "Waiting for /health/ready …"
for _ in $(seq 1 90); do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready')" 2>/dev/null; then
    break
  fi
  sleep 2
done

if ! python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready')"; then
  echo "ERROR: API did not become ready. Check: docker compose logs api" >&2
  exit 1
fi

docker compose exec -T api python /app/scripts/db_init.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " AIMOS is ready → http://localhost:8000/docs"
echo " Health:         http://localhost:8000/health/ready"
echo " Dev login:      aimos-dev@example.com / devpass123  (after db_init)"
echo " E2E test:       python3 scripts/test_full_campaign.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
