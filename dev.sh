#!/usr/bin/env bash
# Start backend + public tunnel, detached. Logs in .logs/. Stop with ./dev.sh stop
set -e
cd "$(dirname "$0")"
mkdir -p .logs
if [ "$1" = "stop" ]; then
  pkill -f "uvicorn app:app" || true
  pkill -f "cloudflared tunnel --url http://localhost:8000" || true
  echo "stopped"; exit 0
fi
(cd backend && nohup .venv/bin/uvicorn app:app --reload --port 8000 > ../.logs/server.log 2>&1 &)
nohup cloudflared tunnel --url http://localhost:8000 > .logs/tunnel.log 2>&1 &
for i in $(seq 1 20); do
  url=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' .logs/tunnel.log | head -1)
  [ -n "$url" ] && break; sleep 1
done
echo "local:  http://localhost:8000/health"
echo "public: ${url:-<see .logs/tunnel.log>}/run"
