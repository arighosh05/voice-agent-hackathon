# CallOut

**A voice assistant for short-staffed kitchens.** Track 01, Local Business.

## Try it live

| | Link |
|---|---|
| 📱 **Ordering page** (open on a phone) | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net/ |
| 🎙️ **CallOut kitchen + voice agent** (open on a laptop) | https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net/kitchen?agent=agent_9201m6yj0n8fehp8xtmfvks0ztjb |

> Daytona shows a one-time preview warning on each device; click **Continue**.

**How to demo:** open the kitchen page, press **Start** and allow the mic, then place an order on the phone. CallOut reads it out about a second later. Try "what's on the board", "start cooking table 10", "we're out of salmon", "table 10 is done".

## User and finish line

- **User:** the Line Chef at a small burger spot, working the kitchen alone. Nobody reads the orders out to them, and their hands are always full.
- **Done means:** every order is read out loud the moment it lands. When the chef says "we're out of salmon", every affected order is flagged and CallOut proposes a free swap and a free drink. Once the chef says yes, those customers get the offer on their phone.

## How it works

1. A customer orders on the phone page; the kitchen page pushes the new order into the live ElevenLabs session, so CallOut speaks without being asked.
2. The Line Chef talks to CallOut (ElevenLabs Conversational AI, Claude Haiku 4.5, Flash TTS).
3. CallOut's webhook tools (board, start, pause, sold out, send offer, back on the menu, modify, done) change real kitchen state in a FastAPI backend running in a **Daytona** sandbox.
4. Measured: callouts ~1.1s after an order, replies ~1.2s after the chef stops talking.

Agent setup: [docs/elevenlabs-agent.md](docs/elevenlabs-agent.md). Demo script: [docs/demo-script.md](docs/demo-script.md). Live endpoints: [LIVE.md](LIVE.md).

## Run it

```bash
cp .env.example .env   # fill in keys
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# or, from the repo root, start server + tunnel detached: ./dev.sh  (stop: ./dev.sh stop)
# expose: cloudflared tunnel --url http://localhost:8000  (or ngrok http 8000)
```


