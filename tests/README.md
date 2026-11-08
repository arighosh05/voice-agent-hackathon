# Expo self-tests (run against the LIVE agent + Daytona backend)

All three reset the live board first. Keys come from `.env` at the repo root.
In the Claude cloud container add `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt` (and `NODE_EXTRA_CA_CERTS` for node).

- `agent_text_test.py AGENT_ID '[lines...]'` — talks to the agent over its websocket with text turns.
  A line `ORDER {json}` places a real order and sends the `[NEW TICKET]` callout. `GAP` = seconds between lines.
  Curveball suite used on 2026-11-08: see docs/demo-script.md section 3.
- `llm_latency.py MODEL [MODEL...]` — switches the agent's LLM, runs the demo lines, prints time to first audio
  and which tools were called. Leaves the agent on the LAST model given, so end with the one you want live.
- `voice_e2e.js [websocket]` — headless kitchen page + phone page; mic is a WAV (`WAV=...`) of ElevenLabs-TTS
  "Marco" lines (fake-capture). Needs Playwright's Chromium. Prints a timeline with reply latency.
