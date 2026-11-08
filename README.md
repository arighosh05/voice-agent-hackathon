# Voice Agent Hackathon

Solo build for the voice-agent hackathon (Sun 2026-11-08, San Diego). ElevenLabs is the mouth and ears, Daytona is the hands.

## User and finish line

- **User:** _TBD, one specific person in one moment_
- **Problem:** _TBD_
- **Done means:** _TBD, a real action, e.g. "a booked appointment"_
- **Track:** _TBD (01 Local Business / 02 Learning & Careers / 03 Health & Care / 04 Open)_

## How it works

1. ElevenLabs agent talks to the user.
2. A server tool calls `POST /run` on `backend/app.py`.
3. The backend runs code in a warm Daytona sandbox and returns the output.
4. The agent says the result out loud.

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

Then add a webhook server tool in the ElevenLabs agent pointing at `<public-url>/run` with a `code` string parameter.

## Timeline (local)

- Build done ~3:00 PM
- Full submission (incl. Loom) by 4:00 PM, hard deadline 4:15 PM
- Finalist demos at 5:00 PM

## Rubric (each 1-5, /40)

| Criterion | Weight | What it means |
|---|---|---|
| Works live | x2 | Replies in ~1.5s, handles interruption, no faked steps |
| Solves the problem | x2 | Does the job for the named user, reaches the finish line with a real action |
| Technical depth | x1 | Real tool calls and data beyond a configured agent |
| Handles curveballs | x1 | Recovers when a judge changes their mind or goes off-topic |
| Uses Daytona | x1 | Agent code, tools or data run in a Daytona sandbox |
| Demo | x1 | Clear, matches what you claim |

Bonus: best ElevenLabs build picked from finalists (tools, knowledge base, language, tuned turn-taking).
