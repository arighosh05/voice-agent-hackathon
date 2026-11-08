# Expo: voice expediter for a short-staffed kitchen

**One-liner:** Marco is a line cook at a small burger spot with no one calling tickets. Expo calls every order out loud, and when he says "86 the salmon", the affected tickets get flagged and the customer gets a swap-and-comp message.

**Done means:** a judge's order is called out in the kitchen, and an 86 reaches that judge's phone as an apology plus a comp.

## Happy path (the demo, ~90s)
1. Open with Marco: hands full, no expo, tickets piling up.
2. The judge scans a QR code and orders "salmon burger, extra cheese, no pickles" on the order page.
3. About a second later, Expo says: "Ordering, table 4: salmon burger, extra cheese, hold the pickles."
4. Marco: "What's on the board?" Expo reads back the open tickets. Marco cuts in: "Fire table 4." The ticket gets marked as fired.
5. Lean-in: Marco says "We're out of salmon." Expo: "That hits tables 4, 7 and 9. I've offered chicken and comped a drink." The judge's phone shows the message.

## Build pieces (all small)
- **Backend (FastAPI, runs in a Daytona sandbox, public preview URL):** orders + inventory kept in memory or SQLite. Endpoints: `POST /order`, `GET /orders`, `POST /fire/{id}`, `POST /86/{item}` (finds affected open orders and writes a customer message), `GET /order/{id}/status`.
- **Order page:** a menu with a few items and modifiers. After submitting, it polls its own status and shows any 86 message.
- **Kitchen page:** an ElevenLabs web SDK session plus a live ticket board. It polls `/orders` and pushes each new order into the conversation (`sendUserMessage` or a contextual update) so Expo speaks on its own.
- **ElevenLabs agent:** short system prompt (terse kitchen voice: "Ordering...", "Heard."). Server tools: `get_board`, `fire_ticket`, `eighty_six_item`. Fast LLM, low-latency TTS.

## Order of work
1. Prove the risky hop: inject a new order into a live session and get Expo to speak it unprompted.
2. Backend in Daytona, with the order page posting to it.
3. Agent tools wired to the backend (board, fire, 86).
4. 86 → customer message shows on the order page.
5. Polish the demo path only. Stretch (only if all of the above works by ~2:30): Expo asks Marco to approve a mod request ("bacon on the veggie burger?").

## Fallbacks
- If proactive speech is flaky: Marco says "what's new?" and Expo reads the latest ticket. The demo still works.
- If the QR code or venue wifi fails: open the order page in a second laptop tab.
- Record a backup Loom of a clean run before 3:45.

## Out of scope
Real POS integration, auth, payments, multiple kitchens, a real menu, and mod-request mediation (stretch only).
