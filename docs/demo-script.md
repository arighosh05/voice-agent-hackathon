# Expo: demo script, submission text, curveballs

Draft. URLs live in `LIVE.md`. Once before the demo (lasts 24h): open the kitchen URL on the laptop and the order URL on your phone, and click through Daytona's one-time preview warning on each. Judges who scan the QR will see it too and tap Continue once; mention it if they hesitate. Before every run: hit **Reset** on the kitchen page (board back to tables 7, 2, 9, no 86s), load the kitchen page once to warm the sandbox, and have the order page open on a phone (`BASE/?table=4`). For a projector or the Loom, add `&stage` to the kitchen URL (or press **S**) for bigger type.

## 1. Demo / Loom script (~90s)

| Time | On screen | Say / do | Rubric beat |
|---|---|---|---|
| 0:00–0:15 | Kitchen line board, tables 7, 2, 9 in New | "This is Marco. He's the only cook on the line at a small burger spot tonight. No expediter, hands in the fryer, and every ticket that prints is one he has to stop and read. Expo is the expediter he doesn't have." | Named user + problem |
| 0:15–0:25 | Click **Start Expo**. Expo: "Expo's up. Send 'em." | "Expo is an ElevenLabs voice agent. The kitchen it manages, orders, tickets, inventory, runs in a Daytona sandbox." | Uses Daytona |
| 0:25–0:40 | Press **Q** for the Guest ordering QR; phone scans it and orders salmon burger, extra cheese, no pickles | (stop talking) Expo, unprompted, about a second later: "Ordering, table 4: salmon burger, extra cheese, no pickles." | Works live: proactive callout |
| 0:40–0:55 | Board | Marco: "What's on the board?" Expo starts reading. Marco cuts in: "Fire table 4." Expo: "Firing table 4." Ticket moves to the Firing column. Point at the transcript chips: the tool call and its latency, plus "Called out in 1.1s" on the earlier callout. "Those are real tool calls against the Daytona backend, timed live." | Interruption + real tool call, visible |
| 0:55–1:05 | Board | Marco: "No wait, fire 7 instead." Expo holds 4, fires 7. | Handles curveballs |
| 1:05–1:20 | Board, then phone close-up | Marco: "We're out of salmon." Expo: "86 salmon burger. That hits tables 4, 7 and 9. I've offered them a chicken sandwich and comped a drink." Tickets move to Needs attention with "Guest notified · drink comped"; the 86 list counter ticks up; the phone shows "An item is unavailable" with the swap and a comped drink. | Finish line: real action reaches the customer |
| 1:20–1:30 | Kitchen + phone side by side (86 item chip with its ms visible) | "Every order called out, and one sentence from Marco handled three tables and three customers without him touching a screen." | Solves the problem |

Notes: keep the mic close and pause after each line so the reply lands inside ~1.5s. Orders placed before Start are still called out when Expo connects. If a callout doesn't fire, say "What's new?" (Expo reads the newest ticket) and keep going.

## 2. Submission text

**Name:** Expo, a voice expediter for short-staffed kitchens
**Track:** 01 Local Business

**User:** Marco, the only line cook at a small burger spot. No one is calling tickets, and his hands are always full.

**Finish line:** Every order is called out by voice the moment it lands, and when Marco says "86 the salmon", every affected ticket is flagged and those customers get a swap-and-comp message on their phone.

**What it does:** A customer orders from their phone. About a second later Expo calls the ticket out in the kitchen, unprompted. Marco runs the line by voice: "what's on the board", "fire table 4", "no wait, fire 7 instead", "we're out of salmon". An 86 marks the item sold out, flags each open ticket that has it, and sends those customers an apology with a free swap and a comped drink.

**How we used ElevenLabs:** A Conversational AI agent with a terse expediter prompt, Claude Haiku 4.5 as the LLM and Flash TTS for low latency, interruptions on, and the silence timeout off so it never asks "still there?" mid-service. It has webhook tools (get_board, fire_ticket, hold_ticket, eighty_six_item, restock, bump) that act on real kitchen state, and the kitchen transcript shows each tool call with its latency. The kitchen page uses the web SDK and pushes each new order into the live session so Expo speaks without being asked. Measured: callouts about 1.1s after an order, replies about 1.2s after Marco stops talking.

**How we used Daytona:** The whole kitchen backend (FastAPI, order and ticket state, inventory, 86 matching, customer messages, and the two pages) runs in a public Daytona sandbox. The agent's tools, the kitchen page and the customer's phone all talk to that sandbox URL. We also used Daytona sandboxes to self-test: a headless kitchen page with a synthetic Marco voice talking to the real agent.

## 3. Curveballs to rehearse

All of these passed against the live agent (PR #14).

| Judge does | Expo should | If it doesn't |
|---|---|---|
| Orders before you click Start | Order is queued and called out about 0.6s after Expo connects | Say "What's new?" |
| Two orders land at once | Both called out in turn, not talking over each other | "What's on the board?" |
| Talks over Expo mid-callout or mid-board-read ("fire table four") | Expo stops and fires 4 within about 0.7s | Repeat the line |
| "No wait, fire 7 instead of 4" | Holds 4, fires 7 | "Hold 4." then "Fire 7." |
| Fires a table that has no ticket ("fire 12") | "No open ticket for table 12." | Nothing needed, that is correct |
| 86 an item not on the menu ("86 the lobster") | "Lobster isn't on the menu." | Nothing needed |
| 86 with slang ("no more fish", "out of plant burgers", "86 the chips") | Maps to the menu item (fish to salmon burger, plant to veggie, chips to fries) | Say the full item name |
| "We're out of burgers" (ambiguous) | Expo asks "Which one?" and retries with the answer | Name the burger |
| 86 something with no open tickets ("86 the veggie") | "No open tickets affected." | Nothing needed |
| Tries to order salmon after the 86 | Order page refuses it as sold out | Point at it: inventory is real state |
| Off-topic ("what's the weather?", "tell me a joke") | One friendly line, back to the board; doesn't assume the speaker is Marco | Move to the next beat |
| Chatty line ("the salmon's selling great") | Does not 86 anything | |
| "Fire 7 and 9" | Fires both | Fire them one at a time |
| "Undo that" right after a fire | Holds the last fired table | "Hold N." |
| "Change table 4 to no cheese" | "Guest has to change that on their phone." | |
| "How long has 7 been waiting?" | Answers from the board (may say "Checking." first) | |
| Asks "is this scripted?" | Let the judge say a line to Expo themselves, or place their own order | |
| Long silence | Expo stays quiet, no "still there?" | |
| "Salmon's back" after an 86 | Restocks it; guests already messaged keep their offer | |
| "Table 2 is out" / "bump 2" | Clears table 2 from the board | |
| Venue wifi drops or Expo goes silent | Reload the kitchen page and click Start Expo again (it connects over websocket by default) | Order from a second laptop tab |
| Judge's phone shows a Daytona warning page after scanning | Tap Continue (one time only), then the order page loads | Order from your phone instead |
| Daytona sandbox is cold or slow | Load the kitchen page once before going on | Wait a beat, re-ask |
