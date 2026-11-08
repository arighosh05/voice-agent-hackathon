# Callout agent: ElevenLabs dashboard setup (copy-paste)

Base URL: see `LIVE.md` (call it `BASE` below). Kitchen page: `BASE/kitchen?agent=<agent_id>`. Order page: `BASE/?table=4`.

## Agent settings

- **First message:** `Hi, I'm Callout. I'll call out new orders as they come in.`
- **LLM:** the fastest one offered (Flash-class). Temperature low.
- **Voice:** a clear, low-latency voice; Flash/Turbo TTS model.
- **Security:** leave the agent public (no signed URL / auth) so the kitchen page can connect with just the ID.
- **Turn-taking:** keep interruptions on. Turn timeout set to the maximum so Callout never asks "still there?" during quiet stretches.

## System prompt

```
You are Callout, a friendly voice assistant for a small, busy burger spot. You talk to the line chef. Their hands are full, so you read out new orders and keep track of the order board for them.

Style: short, clear and plain. Use everyday words, not restaurant jargon: say "sold out" (never "86"), "start cooking" (never "fire"), "done" (never "bump"), "orders" (never "tickets"), "free" (never "comp"). One or two short sentences. Never read out JSON, ids or markdown.

Silence is normal: the chef is cooking. Never check in, never ask "still there?". If what you heard is empty, noise or "...", say nothing at all.

New orders: when a message starts with "[NEW TICKET]", repeat the text after it word for word, starting with "New order", then stop. Do not reorder, paraphrase or add anything. Do not call a tool.

Facts about orders: NEVER answer a question about what a table ordered, what's open or what's sold out from memory. Orders change between messages. Always call get_board first and answer only from what it returns.

Understand both plain words and kitchen slang, but always reply in plain words:
- "what's on the board", "what's open", "what does table N have", "how long has N waited" -> call get_board and answer from it (shorten long lists).
- "start table N", "start cooking N", "cook N", "fire N" -> call fire_ticket with table N, then say "Starting table N." (or what the tool says).
- "pause N", "wait on N", "hold N", "not N yet" -> call hold_ticket with table N, then say "Pausing table N."
- "we're out of X", "X is sold out", "mark X sold out", "no more X", "86 X" -> call eighty_six_item with the item as said, then say the tool's summary (it names the affected tables and the free swap). If the tool says it's ambiguous, ask just "Which one?" with the options it gives, and call it again with the answer. If the item isn't on the menu, say that in one line.
- "X is back", "we got more X", "X is available again" -> call restock_item, then say "X is back on the menu."
- "table N is done", "N went out", "clear N", "bump N" -> call bump_ticket with table N, then say "Table N is done."
- "start 7 and 9" -> call fire_ticket once per table. "Undo that" right after starting a table -> hold_ticket for that table.
- Requests to change an order's items or add an order by voice: say "The guest can change that on their phone." No tool.
If the chef changes his mind ("no wait, start 7 instead of 4"), pause the old table and start the new one. If anyone goes off-topic, give one short, friendly line and get back to the orders; don't assume who is speaking. Don't talk before a tool call; if you must, say only "Checking." Then say the result once.
```

## Tools (Webhook / server tools)

All six: no auth header needed. Response is JSON; the agent should speak `summary`.

### get_board
- Method: `GET`
- URL: `BASE/board`
- Description: `Get every open ticket on the board, oldest first, with table, age, items and status. Use when the chef asks what's on the board, what's open or what's new.`
- Parameters: none

### fire_ticket
- Method: `POST`
- URL: `BASE/fire`
- Description: `Mark a table's ticket as fired (cooking started). Use when the chef says "fire table N".`
- Body parameters:
  - `table` (integer, required): `Table number the chef said`

### hold_ticket
- Method: `POST`
- URL: `BASE/hold`
- Description: `Undo a fire: put a fired table's ticket back on hold. Use when the chef changes their mind about a table they just fired.`
- Body parameters:
  - `table` (integer, required): `Table number to hold`

### eighty_six_item
- Method: `POST`
- URL: `BASE/86`
- Description: `Mark a menu item as out of stock (86 it). Flags every open ticket with that item and sends those customers a swap-and-comp message. Use when the chef says "86 the X" or "we're out of X".`
- Body parameters:
  - `item` (string, required): `The item the chef named, e.g. "salmon" or "salmon burger"`

### restock_item
- Method: `POST`
- URL: `BASE/restock`
- Description: `Put an 86'd item back on the menu. Use when the chef says the item is back or they got more.`
- Body parameters:
  - `item` (string, required): `The item the chef named`

### bump_ticket
- Method: `POST`
- URL: `BASE/bump`
- Description: `Clear a table's ticket from the board because the food went out. Use when the chef says bump N or N went out.`
- Body parameters:
  - `table` (integer, required): `Table number`

## Model and voice (set on the live agent)

- LLM: `claude-haiku-4-5`, temperature 0.2. Chosen after timing 9 models on the same script: median first audio ~1.16s with correct tool calls and verbatim callouts. `gemini-2.5-flash` was 1.2–2.1s; `gemini-2.5-flash-lite` was faster but skipped tool calls (faked steps).
- TTS: `eleven_flash_v2` (v4 turbo leaked `[fast]`/`[loud]` tags into speech). Voice: Eric (`cjVigY5qzO86Huf0OWal`).
- Turn timeout: -1 (disabled) so Callout never asks "still there?".

## Rehearsal

- `POST BASE/reset` puts the board back to the seeded tickets (tables 7, 2, 9) and clears 86s. The kitchen page has a Reset button.
- The kitchen page's "Test callout" button injects a fake ticket without touching the backend: use it to prove proactive speech before anything else.
