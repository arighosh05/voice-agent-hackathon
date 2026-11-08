# Live endpoints (source of truth)

Updated by Claude whenever a deploy changes. If this file and anything else disagree, this file wins.

| What | Value |
|---|---|
| Backend base URL | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net |
| ElevenLabs tool URL | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net/run |
| Auth header | `x-tool-secret` = `TOOL_SECRET` in `.env` (never committed) |
| Where it runs | Daytona sandbox labeled `app=hackathon-backend` (public, never auto-stops) |

Redeploy after code changes: `backend/.venv/bin/python scripts/deploy_daytona.py` (URL stays the same).
Local dev only: `./dev.sh` (temporary trycloudflare URL, not for ElevenLabs).
