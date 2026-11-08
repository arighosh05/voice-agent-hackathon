# Live endpoints (source of truth)

Updated by Claude whenever a deploy changes. If this file and anything else disagree, this file wins.

| What | Value |
|---|---|
| Backend base URL | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net |
| ElevenLabs tool URL | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net/run |
| Kitchen page (laptop) | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net/kitchen?agent=AGENT_ID |
| Order page (phone/QR) | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net/?table=4 |
| Expo agent tools | `GET /board`, `POST /fire`, `POST /86`, no auth (see docs/elevenlabs-agent.md) |
| Auth header (/run only) | `x-tool-secret` = `TOOL_SECRET` in `.env` (never committed) |
| Where it runs | Daytona sandbox labeled `app=hackathon-backend` (public, never auto-stops) |

Redeploy after code changes: `backend/.venv/bin/python scripts/deploy_daytona.py` (URL stays the same).
Local dev only: `./dev.sh` (temporary trycloudflare URL, not for ElevenLabs).
