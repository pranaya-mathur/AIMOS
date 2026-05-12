#!/usr/bin/env bash
# =============================================================================
# AIMOS — Start Project
# Usage: ./start.sh
# Assumes Docker (db + redis) is already running.
# Starts: ComfyUI (Juggernaut XL) → Backend API → Frontend
# =============================================================================
set -e

AIMOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH="$HOME/gemini/antigravity/scratch/aimos"
LOGS="$AIMOS_ROOT/logs"
mkdir -p "$LOGS"

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BOLD="\033[1m"
RESET="\033[0m"

info() { echo -e "${GREEN}[START]${RESET} $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
fail() { echo -e "${RED}[FAIL]${RESET}  $*"; exit 1; }

wait_for() {
    local label="$1" url="$2" retries="${3:-30}" delay="${4:-2}"
    for i in $(seq 1 "$retries"); do
        if curl -sf --max-time 2 "$url" > /dev/null 2>&1; then
            info "$label is ready"
            return 0
        fi
        echo -ne "  waiting for $label ($i/$retries)...\r"
        sleep "$delay"
    done
    fail "$label did not become ready in time"
}

# ── 1. Check Docker db/redis are reachable (start only if down) ───────────────
if ! docker compose -f "$AIMOS_ROOT/docker-compose.yml" exec -T db pg_isready -U user -d aimos > /dev/null 2>&1; then
    warn "Docker db/redis not running — starting them now..."
    docker compose -f "$AIMOS_ROOT/docker-compose.yml" up -d db redis
    for i in $(seq 1 20); do
        docker compose -f "$AIMOS_ROOT/docker-compose.yml" exec -T db pg_isready -U user -d aimos > /dev/null 2>&1 && break
        sleep 2
        [[ $i -eq 20 ]] && fail "Postgres did not start"
    done
    info "Postgres ready"
else
    info "Docker db/redis already running — skipping"
fi

# ── 2. ComfyUI (Juggernaut XL) ────────────────────────────────────────────────
if curl -sf --max-time 2 "http://localhost:8188/system_stats" > /dev/null 2>&1; then
    warn "ComfyUI already running on :8188 — skipping"
else
    info "Starting ComfyUI (Juggernaut XL on :8188)..."
    cd "$SCRATCH/ComfyUI"
    nohup "$SCRATCH/venv/bin/python3" main.py \
        --normalvram --force-fp16 \
        --listen 0.0.0.0 --port 8188 \
        > "$LOGS/comfyui.log" 2>&1 &
    echo $! > "$LOGS/comfyui.pid"
    cd "$AIMOS_ROOT"
    wait_for "ComfyUI" "http://localhost:8188/system_stats" 40 3
fi

# ── 3. Backend API (uvicorn) ──────────────────────────────────────────────────
if curl -sf --max-time 2 "http://localhost:8000/" > /dev/null 2>&1; then
    warn "Backend API already running on :8000 — skipping"
else
    info "Starting Backend API (FastAPI on :8000)..."
    cd "$AIMOS_ROOT/backend"
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 \
        > "$LOGS/api.log" 2>&1 &
    echo $! > "$LOGS/api.pid"
    cd "$AIMOS_ROOT"
    wait_for "Backend API" "http://localhost:8000/" 30 2
fi

# ── 4. Frontend (Next.js) ─────────────────────────────────────────────────────
if curl -sf --max-time 2 "http://localhost:3000/" > /dev/null 2>&1; then
    warn "Frontend already running on :3000 — skipping"
else
    info "Starting Frontend (Next.js on :3000)..."
    cd "$AIMOS_ROOT/frontend"
    nohup npm run dev > "$LOGS/frontend.log" 2>&1 &
    echo $! > "$LOGS/frontend.pid"
    cd "$AIMOS_ROOT"
    wait_for "Frontend" "http://localhost:3000/" 40 3
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}✓ AIMOS is running${RESET}"
echo ""
echo -e "  ${BOLD}Frontend${RESET}    → http://localhost:3000"
echo -e "  ${BOLD}Backend API${RESET} → http://localhost:8000"
echo -e "  ${BOLD}API Docs${RESET}    → http://localhost:8000/docs"
echo -e "  ${BOLD}ComfyUI${RESET}     → http://localhost:8188"
echo ""
echo -e "  ${BOLD}Login:${RESET}  aimos-dev@example.com  /  devpass123"
echo ""
echo -e "  Logs: $LOGS/"
echo -e "  Stop: ${BOLD}./stop.sh${RESET}"
echo -e "  ${BOLD}Backend API${RESET} → http://localhost:8000"
echo -e "  ${BOLD}API Docs${RESET}   → http://localhost:8000/docs"
echo -e "  ${BOLD}ComfyUI${RESET}    → http://localhost:8188"
echo ""
echo -e "  ${BOLD}Login:${RESET}  aimos-dev@example.com  /  devpass123"
echo ""
echo -e "  Logs in: $LOGS/"
echo -e "  To stop:  ${BOLD}./stop.sh${RESET}"
