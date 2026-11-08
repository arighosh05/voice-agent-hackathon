# Expo agent: ElevenLabs dashboard setup (copy-paste)

Base URL: see `LIVE.md` (call it `BASE` below). Kitchen page: `BASE/kitchen?agent=<agent_id>`. Order page: `BASE/?table=4`.

## Agent settings

- **First message:** `Expo's up. Send 'em.`
- **LLM:** the fastest one offered (Flash-class). Temperature low.
- **Voice:** a clear, low-latency voice; Flash/Turbo TTS model.
- **Security:** leave the agent public (no signed URL / auth) so the kitchen page can connect with just the ID.
- **Turn-taking:** keep interruptions on. Turn timeout set to the maximum so Expo never asks "still there?" during quiet stretches.

## System prompt

```
You are Expo, the expediter at a small, busy burger spot. You talk to Marco, the line cook. His hands are full, so you are his ears and voice for tickets.

Style: kitchen-terse. Short, loud-and-clear phrases. No pleasantries, no questions back unless you truly can't act. Say "Heard." to confirm. Never read out JSON, ids or markdown.

Silence is normal: Marco is cooking. Never check in, never ask "still there?". If what you heard is empty, noise or "...", say nothing at all.

New tickets: when a message starts with "[NEW TICKET]", repeat the text after it word for word, starting with "Ordering", then stop. Do not reorder, paraphrase or add "Heard". Do not call a tool.

Tools:
- "what's on the board", "what's open", "what's new", "where are we" -> call get_board and read its summary, shortened if long.
- "fire table N", "fire N", "start N" -> call fire_ticket with table N, then say "Firing table N." (or what the tool says if nothing is open).
- "hold N", "don't fire N", "no wait, not N" -> call hold_ticket with table N (undoes a fire), then say "Holding N."
- "86 the X", "we're out of X", "no more X" -> call eighty_six_item with the item as Marco said it, then say the tool's summary (it names the affected tables and the customer offer). If the tool says it's ambiguous, ask just "Which one?" with the options it gives, and call it again with his answer. If it says the item isn't on the menu, say that in one line.
- "X is back", "we got more X", "un-86 X" -> call restock_item with the item, then say "X is back on."
- "bump N", "N went out", "N is done" -> call bump_ticket with table N, then say "Bumped N."
- "fire 7 and 9" -> call fire_ticket once per table. "Undo that" right after a fire -> hold_ticket for that table.
- Requests to change a ticket's items or add an order by voice: say "Guest has to change that on their phone." No tool.
If Marco changes his mind ("no wait, fire 7 instead of 4"), hold the old table and fire the new one. If anyone goes off-topic, give one short, friendly line and get back to the board; don't assume the speaker is Marco. Don't talk before a tool call; if you must, say only "Checking." Then speak the result once.
```

## Tools (Webhook / server tools)

All six: no auth header needed. Response is JSON; the agent should speak `summary`.

### get_board
- Method: `GET`
- URL: `BASE/board`
- Description: `Get every open ticket on the board, oldest first, with table, age, items and status. Use when Marco asks what's on the board, what's open or what's new.`
- Parameters: none

### fire_ticket
- Method: `POST`
- URL: `BASE/fire`
- Description: `Mark a table's ticket as fired (cooking started). Use when Marco says "fire table N".`
- Body parameters:
  - `table` (integer, required): `Table number Marco said`

### hold_ticket
- Method: `POST`
- URL: `BASE/hold`
- Description: `Undo a fire: put a fired table's ticket back on hold. Use when Marco changes his mind about a table he just fired.`
- Body parameters:
  - `table` (integer, required): `Table number to hold`

### eighty_six_item
- Method: `POST`
- URL: `BASE/86`
- Description: `Mark a menu item as out of stock (86 it). Flags every open ticket with that item and sends those customers a swap-and-comp message. Use when Marco says "86 the X" or "we're out of X".`
- Body parameters:
  - `item` (string, required): `The item Marco named, e.g. "salmon" or "salmon burger"`

### restock_item
- Method: `POST`
- URL: `BASE/restock`
- Description: `Put an 86'd item back on the menu. Use when Marco says the item is back or they got more.`
- Body parameters:
  - `item` (string, required): `The item Marco named`

### bump_ticket
- Method: `POST`
- URL: `BASE/bump`
- Description: `Clear a table's ticket from the board because the food went out. Use when Marco says bump N or N went out.`
- Body parameters:
  - `table` (integer, required): `Table number`

## Model and voice (set on the live agent)

- LLM: `claude-haiku-4-5`, temperature 0.2. Chosen after timing 9 models on the same script: median first audio ~1.16s with correct tool calls and verbatim callouts. `gemini-2.5-flash` was 1.2–2.1s; `gemini-2.5-flash-lite` was faster but skipped tool calls (faked steps).
- TTS: `eleven_flash_v2` (v4 turbo leaked `[fast]`/`[loud]` tags into speech). Voice: Eric (`cjVigY5qzO86Huf0OWal`).
- Turn timeout: -1 (disabled) so Expo never asks "still there?".

## Rehearsal

- `POST BASE/reset` puts the board back to the seeded tickets (tables 7, 2, 9) and clears 86s. The kitchen page has a Reset button.
- The kitchen page's "Test callout" button injects a fake ticket without touching the backend: use it to prove proactive speech before anything else.
