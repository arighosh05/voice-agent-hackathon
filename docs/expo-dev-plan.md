# Expo dev plan: race to "built once" by 3:00 PM

Written 1:26 PM. You have about 95 minutes of build time. Scope is callouts + 86 only. Stretch (mod requests) is cut unless every checkpoint is green by 2:30, which is unlikely, so plan as if it's gone.

**"Built once" means:** a phone order hits the backend running in Daytona, Expo says it out loud without being asked, Marco can say "what's on the board" / "fire table 4" / "86 the salmon" by voice, and the 86 message shows up on that phone. Everything after that is polish and rehearsal.

## Architecture (one decision to lock now)

- **One FastAPI file (`backend/expo.py`)** holds orders + inventory in memory and also serves the two pages as static HTML. One process, one URL.
  - `POST /order`, `GET /orders`, `POST /fire/{table}`, `POST /86/{item}`, `GET /order/{id}/status`, `GET /` (order page), `GET /kitchen` (kitchen page).
- **It runs inside a Daytona sandbox** and is reached through the sandbox's public preview URL (create the sandbox with `public=True` so ElevenLabs and phones need no preview token). That URL is used by the phone, the kitchen page, and the agent's server tools. This is the "Uses Daytona" story: the whole kitchen backend lives in the sandbox.
- **The kitchen page** runs on your laptop (open `<preview-url>/kitchen`, https so the mic works). It uses the ElevenLabs JS client from a CDN, polls `/orders` every second, and for each new order calls `conversation.sendUserMessage("NEW ORDER table 4: salmon burger, extra cheese, no pickles")`. `sendUserMessage` makes the agent respond; `sendContextualUpdate` does not, so use the former.
- **ElevenLabs agent:** three webhook server tools (`get_board`, `fire_ticket`, `eighty_six_item`) pointing at the preview URL. Public agent (no signed URL) so the page only needs the agent ID.

## Build steps, in order

| # | Time | Step | Who | Checkpoint |
|---|---|---|---|---|
| 0 | 1:30–1:40 | Create the agent in the ElevenLabs dashboard: terse expo prompt, fast LLM (Flash-class), low-latency TTS voice, first message "Expo's up." Copy the agent ID. | Ari | Agent talks in the dashboard test widget. |
| 1 | 1:40–2:00 | **Risky hop.** `kitchen.html` with Start button + a "fake order" button that calls `sendUserMessage`. Open on localhost first, talk to it, click the button mid-silence. | Claude writes, Ari tests | **2:00: Expo speaks a fake order without being asked.** |
| 1b | 1:30–2:00 (parallel) | `expo.py` backend + order page (menu of 4 items, 3 mods, table number, polls its status and shows any 86 message). Seed tables 7 and 9 with salmon orders so the 86 hits three tickets. | Claude | Works locally with curl. |
| 2 | 2:00–2:20 | Deploy `expo.py` into a Daytona sandbox (script: create public sandbox, upload file, pip install, start uvicorn in a background session, print preview URL). Kitchen page switches from fake button to polling `/orders`. | Claude writes, Ari runs | **2:20: order from your phone is called out by Expo within ~2s.** |
| 3 | 2:20–2:45 | Add the 3 server tools in the dashboard (URL + JSON schema, I'll give copy-paste text). Add prompt lines for when to call each. | Ari (dashboard), Claude (schemas) | **2:45: board, fire, and 86 all work by voice.** |
| 4 | 2:45–3:00 | 86 end to end: "we're out of salmon" → Expo names tables 4, 7, 9 → phone shows "Sorry, we're out of salmon. Want chicken instead? Drink's on us." Fix whatever broke. | Both | **3:00: full happy path runs once, start to finish.** |

After 3:00: 3:00–3:30 tune the prompt (shorter callouts, interruption behavior), rehearse 3x, make the QR code. 3:30 record the backup Loom. 3:45 submit. 4:15 hard deadline.

## What runs in parallel

- 1:30–2:00 is the big win: you do the dashboard agent + mic test while I write the backend, the order page and the kitchen page. These don't touch each other until step 2.
- During step 3, while you click through the dashboard, I write the deploy script fixes and the seed data.

## Cut lines (decide at the clock, don't drift)

- **2:05, proactive speech still not working:** stop. Use the fallback: Marco says "what's new?" and Expo calls `get_board` and reads the newest ticket. Add a chime on the kitchen page when an order lands so it still feels live. Move on to step 2.
- **2:30, Daytona deploy not serving:** stop. Run `expo.py` on your Mac with a cloudflared tunnel, and keep Daytona in the story by running the 86 matching inside the sandbox through the existing `/run` endpoint. Daytona is only x1 on the rubric; "works live" is x2.
- **2:45, a server tool is flaky:** convert it to a client tool (the kitchen page calls the backend itself). Same behavior, no webhook in the way.
- **3:00, anything still broken:** cut it from the demo script, don't fix it. Rehearsal time is worth more.

## Known gotchas to pre-empt

- Mic needs https or localhost. The preview URL is https, so that's fine.
- If an order arrives while Marco is mid-sentence, `sendUserMessage` can talk over him. Queue new orders on the page and send them only when the agent isn't speaking (the SDK reports mode changes).
- Phones on venue wifi: test the preview URL on cellular before the demo.
- Already live: local backend + cloudflared tunnel (`/run`, warm ~0.2s), started detached by `./dev.sh` on Ari's Mac (`./dev.sh stop` stops both and deletes the sandbox). Closing the laptop lid pauses it, which is another reason to host the Expo backend in Daytona. That's the ready-made fallback for the 2:30 cut line. The trycloudflare URL changes if the tunnel restarts, so update the agent's tool URLs if it does. A cold sandbox takes ~13s on first call: always make a warm-up call right before a demo or recording.
- Daytona sandbox auto-stops after idle; set the auto-stop interval high (or 0) for the demo sandbox, and delete it after judging.
