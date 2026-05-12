#!/usr/bin/env bash
# =============================================================================
# AIMOS — Stop Everything
# Usage: ./stop.sh
# Stops: Frontend → Backend API → ComfyUI → Docker (db + redis)
# =============================================================================

AIMOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS="$AIMOS_ROOT/logs"

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RESET="\033[0m"

info() { echo -e "${GREEN}[STOP]${RESET}  $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }

kill_pid_file() {
    local name="$1" pidfile="$2"
    if [[ -f "$pidfile" ]]; then
        local pid
        pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && info "$name (pid $pid) stopped"
        else
            warn "$name pid $pid not found (already stopped)"
        fi
        rm -f "$pidfile"
    fi
}

# ── 1. Frontend ───────────────────────────────────────────────────────────────
info "Stopping Frontend (Next.js)..."
kill_pid_file "Frontend" "$LOGS/frontend.pid"
# Belt-and-suspenders: kill any remaining next-server processes
pkill -f "next dev" 2>/dev/null && info "  (killed lingering next dev)" || true
pkill -f "next-server" 2>/dev/null || true

# ── 2. Backend API ────────────────────────────────────────────────────────────
info "Stopping Backend API (uvicorn)..."
kill_pid_file "Backend API" "$LOGS/api.pid"
pkill -f "uvicorn main:app" 2>/dev/null && info "  (killed lingering uvicorn)" || true

# ── 3. ComfyUI ────────────────────────────────────────────────────────────────
info "Stopping ComfyUI..."
kill_pid_file "ComfyUI" "$LOGS/comfyui.pid"
pkill -f "ComfyUI/main.py" 2>/dev/null && info "  (killed lingering ComfyUI)" || true

# ── 4. Docker ─────────────────────────────────────────────────────────────────
info "Stopping Docker services (db + redis)..."
docker compose -f "$AIMOS_ROOT/docker-compose.yml" stop db redis 2>/dev/null && info "Docker services stopped" || warn "Docker stop had issues (may already be down)"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✓ AIMOS stack stopped${RESET}"
