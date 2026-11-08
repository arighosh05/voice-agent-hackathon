# Live endpoints (source of truth)

Updated by Claude whenever a deploy changes. If this file and anything else disagree, this file wins.

| What | Value |
|---|---|
| Backend base URL | _pending first deploy_ |
| ElevenLabs tool URL | _pending_ |
| Auth header | `x-tool-secret` = `TOOL_SECRET` in `.env` (never committed) |
| Where it runs | Daytona sandbox labeled `app=hackathon-backend` (public, never auto-stops) |

Redeploy after code changes: `backend/.venv/bin/python scripts/deploy_daytona.py` (URL stays the same).
Local dev only: `./dev.sh` (temporary trycloudflare URL, not for ElevenLabs).
