# Expo: demo script, submission text, curveballs

URLs are in `LIVE.md`.

**Once before the demo (it lasts 24h):** open the kitchen URL on the laptop and the order URL on your phone, and click through Daytona's one-time preview warning on each. Judges who scan the QR code will see it too and tap Continue once.

**Before every run:** click **Reset** on the kitchen page (the board goes back to tables 7, 2 and 9, with nothing sold out). Load the kitchen page once to warm up the sandbox, and have the order page open on your phone (`BASE/?table=4`). For a projector or the Loom, add `&stage` to the kitchen URL (or press **S**) to get bigger type.

## 1. Demo / Loom script (~90s)

| Time | On screen | Say / do | Rubric beat |
|---|---|---|---|
| 0:00–0:15 | Kitchen board, tables 7, 2 and 9 under New | "This is Marco. He's the only cook at a small burger spot tonight. Nobody is reading orders out to him, his hands are full, and every new order means stopping to look at a screen. Expo reads them out for him." | Named user + problem |
| 0:15–0:25 | Click **Start Expo**. Expo: "Hi, I'm Expo. I'll call out new orders as they come in." | "Expo is an ElevenLabs voice agent. Everything it manages (orders, the board, what's sold out) runs in a Daytona sandbox." | Uses Daytona |
| 0:25–0:40 | Press **Q** to show the Guest ordering QR code. The phone scans it and orders a salmon burger with extra cheese and no pickles | (stop talking) About a second later, without being asked, Expo says: "New order, table 4: salmon burger, extra cheese, hold the pickles." | Works live: speaks on its own |
| 0:40–0:55 | Board | Marco: "What's on the board?" Expo starts reading. Marco cuts in: "Start cooking table 4." Expo: "Starting table 4." The order moves to Cooking. Point at the transcript chips, which show each tool call with its timing: "Those are real tool calls to the Daytona backend, timed live." | Interruption + real tool call, visible |
| 0:55–1:05 | Board | Marco: "No wait, start 7 instead of 4." Expo: "Pausing table 4. Starting table 7." | Handles a change of mind |
| 1:05–1:20 | Board, then a close-up of the phone | Marco: "We're out of salmon." Expo: "Salmon burger is sold out. That affects tables 4, 7 and 9. I've texted them a free swap to a chicken sandwich and a drink on us." Those orders move to Needs attention and show "Guest texted", and the Sold out count goes up. The phone shows "An item is unavailable" with the free swap and a free drink. | Finish line: a real action reaches the customer |
| 1:20–1:30 | Kitchen and phone side by side | "Every order read out loud, and one sentence from Marco took care of three tables and three customers without him touching a screen." | Solves the problem |

Notes: keep the mic close and pause after each line so the reply comes back within about 1.5s. Orders placed before you click Start are still read out once Expo connects. If an order isn't read out, ask "What's on the board?" and keep going. Older kitchen slang ("fire", "86") still works, but plain words read better on stage.

## 2. Submission text

**Name:** Expo, a voice assistant for short-staffed kitchens
**Track:** 01 Local Business

**User:** Marco, the only cook at a small burger spot. Nobody reads the orders out to him, and his hands are always full.

**Finish line:** Every order is read out loud the moment it lands. When Marco says "we're out of salmon", every affected order is flagged and those customers get a message on their phone offering a free swap and a free drink.

**What it does:** A customer orders from their phone, and about a second later Expo reads the order out in the kitchen without being asked. Marco runs the kitchen by voice: "what's on the board", "start cooking table 4", "no wait, start 7 instead", "we're out of salmon", "table 2 is done". When something sells out, Expo marks it sold out, flags each open order that has it, and texts those customers an apology with a free swap and a free drink.

**How we used ElevenLabs:** A Conversational AI agent with a short, plain-spoken prompt. It uses Claude Haiku 4.5 as the LLM and Flash TTS for low latency, keeps interruptions on, and turns the silence timeout off so it never asks "still there?" during a busy service. Its webhook tools (board, start, pause, sold out, back on the menu, done) change real kitchen state, and the kitchen transcript shows each tool call with its latency. The kitchen page uses the web SDK and pushes each new order into the live session, so Expo speaks without being asked. Measured: orders are read out about 1.1s after they're placed, and replies come about 1.2s after Marco stops talking.

**How we used Daytona:** The whole kitchen backend runs in a public Daytona sandbox: FastAPI, orders and the board, what's sold out, matching an item to its orders, customer messages, and both pages. The agent's tools, the kitchen page and the customer's phone all talk to that sandbox URL. We also used Daytona sandboxes to test ourselves, with a headless kitchen page where a synthetic Marco voice talks to the real agent.

## 3. Curveballs to rehearse

All of these passed against the live agent.

| Judge does | Expo should | If it doesn't |
|---|---|---|
| Orders before you click Start | The order is read out about 0.6s after Expo connects | Ask "What's on the board?" |
| Two orders land at once | Reads both out in turn, without talking over itself | "What's on the board?" |
| Talks over Expo mid-sentence ("start table four") | Stops and starts table 4 within about 0.7s | Repeat the line |
| "No wait, start 7 instead of 4" | "Pausing table 4. Starting table 7." | "Pause 4." then "Start 7." |
| "Start table 12" (no such order) | Says there's no open order for table 12 | Nothing needed, that's correct |
| "What does table 5 have?" | Checks the board and answers from it (never from memory) | |
| "We're out of lobster" (not on the menu) | "Lobster isn't on the menu." | Nothing needed |
| "No more fish", "out of plant burgers", "no more chips" | Matches the menu item (fish is the salmon burger, plant is veggie, chips are fries) | Say the full item name |
| "We're out of burgers" (unclear) | Asks "Which one?", then acts on the answer | Name the burger |
| Sold out on something no open order has ("we're out of veggie burgers") | Marks it sold out and says no orders are affected | Nothing needed |
| Tries to order salmon after it's sold out | The order page shows it as Sold out and won't take it | Point at it: the stock is real |
| "Salmon is back" | "Salmon burger is back on the menu." Customers already texted keep their offer | |
| "Table 2 is done" | "Table 2 is done." and the order leaves the board | Click Mark done |
| "Start 7 and 9" | Starts both | One at a time |
| "Undo that" right after a start | Pauses the last table it started | "Pause N." |
| "Table 4 wants no cheese" | "The guest can change that on their phone." | |
| Chatty line ("the salmon's selling great") | Doesn't mark anything sold out | |
| Off-topic ("what's the weather?", "tell me a joke") | One friendly line, then back to the board. It doesn't assume the speaker is Marco | Move to the next beat |
| Asks "is this scripted?" | Let the judge talk to Expo themselves, or place their own order | |
| Long silence | Stays quiet and never asks "still there?" | |
| Wifi drops or Expo goes silent | Reload the kitchen page and click Start Expo again | Order from a second laptop tab |
| Judge's phone shows a Daytona warning after scanning | Tap Continue (only once), and the order page loads | Order from your phone instead |
| Sandbox is slow on the first load | Load the kitchen page once before you go on | Wait a beat, then ask again |
