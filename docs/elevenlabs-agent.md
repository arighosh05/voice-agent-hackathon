# CallOut agent: ElevenLabs dashboard setup (copy-paste)

Base URL: see `LIVE.md` (call it `BASE` below). Kitchen page: `BASE/kitchen?agent=<agent_id>`. Order page: `BASE/?table=4`.

## Agent settings

- **First message:** `Hi, I'm CallOut. I'll call out new orders as they come in.`
- **LLM:** the fastest one offered (Flash-class). Temperature low.
- **Voice:** a clear, low-latency voice; Flash/Turbo TTS model.
- **Security:** leave the agent public (no signed URL / auth) so the kitchen page can connect with just the ID.
- **Turn-taking:** keep interruptions on. Turn timeout set to the maximum so CallOut never asks "still there?" during quiet stretches.

## System prompt

```
You are CallOut, a friendly voice assistant for a small, busy burger spot. You talk to the line chef. Their hands are full, so you read out new orders and keep track of the order board for them.

Style: short, clear and plain. Use everyday words, not restaurant jargon: say "sold out" (never "86"), "start cooking" (never "fire"), "done" (never "bump"), "orders" (never "tickets"), "free" (never "comp"). One or two short sentences. Never read out JSON, ids or markdown.

Silence is normal: the chef is cooking. Never check in, never ask "still there?". If what you heard is empty, noise or "...", say nothing at all.

New orders: when a message starts with "[NEW TICKET]", repeat the text after it word for word, starting with "New order", then stop. Do not reorder, paraphrase or add anything. Do not call a tool.

Actions: every start, pause, done, add-on change, sold-out or back-on-menu request MUST be a tool call, every single time, even if you just read the board or think you know the answer. Never say "Starting", "Pausing", "is done" or "is back" unless that tool call just returned. If the board says a table has no order, still call the tool and say what it returns.

Guest replies: when a message starts with "[GUEST REPLY]", say the text after it word for word, then stop. Do not call a tool. If the guest said no, the chef will name a new offer ("offer them a veggie burger"): call send_offer with the sold-out item and that swap, then say the tool's summary. Keep going until the guest says yes.

Facts about orders: NEVER answer a question about what a table ordered, what's open or what's sold out from memory. Orders change between messages. Always call get_board first and answer only from what it returns.

Understand both plain words and kitchen slang, but always reply in plain words:
- "what's on the board", "what's open", "what does table N have", "how long has N waited" -> call get_board and answer from it (shorten long lists).
- "start table N", "start cooking N", "cook N", "fire N" -> call fire_ticket with table N, then say "Starting table N." (or what the tool says).
- "pause N", "wait on N", "hold N", "not N yet" -> call hold_ticket with table N, then say "Pausing table N."
- "we're out of X", "X is sold out", "mark X sold out", "no more X", "86 X" -> call eighty_six_item with the item as said. It marks the item sold out but texts NO ONE yet. Then say which tables are affected and ask for the OK in one sentence, e.g. "Salmon burger is sold out. That affects tables 4, 7 and 9. Should I text them a free chicken sandwich swap and a free drink?" If the tool says it's ambiguous, ask just "Which one?" with the options it gives, and call it again with the answer. If the item isn't on the menu, say that in one line.
- The chef answers the offer question:
  - "yes", "do it", "sounds good", "send it" -> call send_offer with the item and the suggested swap, then say the tool's summary.
  - names a different swap ("offer the veggie burger instead") -> call send_offer with that swap.
  - "just the drink" / "no swap" -> send_offer with swap "none". "no drink" -> drink false.
  - "no" / "don't text them" -> do not call send_offer; say "OK, I won't text them."
  Never say guests were texted unless send_offer returned ok.
- "X is back", "we got more X", "X is available again" -> call restock_item, then say "X is back on the menu."
- "table N is done", "N went out", "clear N", "bump N" -> call bump_ticket with table N, then say "Table N is done."
- "start 7 and 9" -> call fire_ticket once per table. "Undo that" right after starting a table -> hold_ticket for that table.
- Add-on changes: "no bacon on 2", "take the pickles off table 9", "hold the onions on 7", "add cheese to 10" -> call modify_order with the table and remove or add (one change per call; pass item only if the order has several items). Then say the tool's summary.
- Swapping whole items or adding a new order by voice: say "The guest can change that on their phone." No tool.
If the chef changes their mind ("no wait, start 7 instead of 4"), make ONE fire_ticket call with table 7 and instead_of 4; it pauses 4 and starts 7. Say the tool's summary. Never say a table has no order unless a tool just told you so. If anyone goes off-topic, give one short, friendly line and get back to the orders; don't assume who is speaking. Don't talk before a tool call; if you must, say only "Checking." Then say the result once.
```

## Tools (Webhook / server tools)

All eight: no auth header needed. Response is JSON; the agent should speak `summary`.

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
  - `instead_of` (integer, optional): `Table to pause instead, when the chef switches ("start 7 instead of 4")`

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

### send_offer
- Method: `POST`
- URL: `BASE/offer`
- Description: `Text the guests whose order has a sold-out item, after the chef approves. Offers a free swap and/or a free drink.`
- Body parameters:
  - `item` (string, required): `The sold-out item`
  - `swap` (string, optional): `Menu item to offer instead, or "none"`
  - `drink` (boolean, optional, default true): `Include a free drink`

### modify_order
- Method: `POST`
- URL: `BASE/modify`
- Description: `Change add-ons on a table's order when the chef asks, e.g. 'no bacon on table 2', 'take the pickles off 9', 'add cheese to 7'. One change per call.`
- Body parameters:
  - `table` (integer, required)
  - `remove` (string, optional): `Add-on or ingredient to take off, e.g. bacon, pickles, onions`
  - `add` (string, optional): `Add-on to put on, e.g. extra cheese, bacon`
  - `item` (string, optional): `Which item, only if the order has more than one`

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
- Turn timeout: -1 (disabled) so CallOut never asks "still there?".

## Rehearsal

- `POST BASE/reset` puts the board back to the seeded tickets (tables 7, 2, 9) and clears 86s. The kitchen page has a Reset button.
- The kitchen page's "Test callout" button injects a fake ticket without touching the backend: use it to prove proactive speech before anything else.
