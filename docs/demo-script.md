# CallOut: demo script, submission text, curveballs

URLs are in `LIVE.md`.

**Once before the demo (it lasts 24h):** open the kitchen URL on the laptop and the order URL on your phone, and click through Daytona's one-time preview warning on each. If a judge wants to order themselves, press **Q** for the QR code; they'll see the warning once and tap Continue.

**Before every run:** click **Reset** on the kitchen page (the board goes back to tables 7, 2 and 9, with nothing sold out). Load the kitchen page once to warm up the sandbox, and have the order page open on your phone (`BASE/`). The phone gets the next free table, starting at 10, and shows "You're at table N". The script assumes table 10, so say whatever number your phone shows. For a projector or the Loom, add `&stage` to the kitchen URL (or press **S**) to get bigger type.

## 1. Demo / Loom script (~100s)

**Mic:** your narration (in quotes below, no speaker label) is for the judges. Press **M** to mute CallOut before you narrate, and press **M** again before you speak to it. The kitchen page shows "Mic muted" while it's off. If that's too much juggling, pause for a second after each narration line instead; CallOut ignores chatter that isn't a command.

| Time | On screen | Say / do | Rubric beat |
|---|---|---|---|
| 0:00–0:15 | Kitchen board, tables 7, 2 and 9 under To start (mic muted) | "Meet the Line Chef at a small burger spot. They're the only one in the kitchen tonight. Nobody reads the orders out to them, their hands are full, and every new order means stopping to look at a screen. CallOut reads the orders out for them." | Named user + problem |
| 0:15–0:25 | Click **Start CallOut**. CallOut: "Hi, I'm CallOut. I'll call out new orders as they come in." | "CallOut is an ElevenLabs voice agent. Everything it manages (orders, the board, what's sold out) runs in a Daytona sandbox." | Uses Daytona |
| 0:25–0:40 | Hold up your phone ("You're at table 10") and order a salmon burger with extra cheese and no pickles | "I'm a guest, ordering from my table." (stop talking) About a second later, without being asked, CallOut says: "New order, table 10: salmon burger, extra cheese, hold the pickles." | Works live: speaks on its own |
| 0:40–0:55 | Board (unmute) | Line Chef: "What's on the board?" CallOut starts reading. Cut in: "Start cooking table 10." CallOut: "Starting table 10." The order moves to Cooking. Mute, then point at the transcript chips: "Those are real tool calls to the Daytona backend, timed live." | Interruption + real tool call, visible |
| 0:55–1:05 | Board (unmute) | Line Chef: "No wait, start 7 instead of 10." CallOut: "Pausing table 10. Starting table 7." | Handles a change of mind |
| 1:05–1:25 | Board | Line Chef: "We're out of salmon." CallOut: "Salmon burger is sold out. That affects tables 7, 9 and 10. Should I text them a free chicken sandwich swap and a free drink?" The three orders get a red outline and "Waiting on chef's OK" right where they are. Line Chef: "Yes, send it." CallOut: "Texted tables 7, 9 and 10: a free swap to a chicken sandwich and a drink on us." The orders now show "Guest texted", with "→ Chicken Sandwich" under the struck-through salmon burger. | Finish line, with the chef deciding |
| 1:25–1:35 | Phone close-up (mute) | The order page shows "An item is unavailable" with the free swap and a free drink. Tap **Check status**, type 10, and tap **Check** to see the same order and offer. "The guest sees it right away, and can check on their table at any time." | A real action reaches the customer |
| 1:35–1:45 | Kitchen and phone side by side | "Every order read out loud, and one sentence plus a yes from the Line Chef took care of three tables. The chef stays in charge of what customers get." | Solves the problem |

Optional extra beat (about 5s, if you have time): "No bacon on 2." CallOut updates table 2 and its card gets a blue "Updated" badge.

Other ways to answer the offer: "Offer the veggie burger instead" texts that swap, "Just the drink" skips the swap, and "No, don't text them" gets "OK, I won't text them."

Notes: keep the mic close and pause after each line so the reply comes back within about 1.5s. Orders placed before you click Start are still read out once CallOut connects. If an order isn't read out, ask "What's on the board?" and keep going. Older kitchen slang ("fire", "86") still works, but plain words read better on stage.

## 2. Submission text

**Name:** CallOut, a voice assistant for short-staffed kitchens
**Track:** 01 Local Business

**User:** The Line Chef at a small burger spot, working the kitchen alone. Nobody reads the orders out to them, and their hands are always full.

**Finish line:** Every order is read out loud the moment it lands. When the Line Chef says "we're out of salmon", every affected order is flagged and CallOut proposes a free swap and a free drink. Once the chef says yes, those customers get the offer on their phone, and they can look up their table status there.

**What it does:** A customer orders from their phone, and about a second later CallOut reads the order out in the kitchen without being asked. The Line Chef runs the kitchen by voice: "what's on the board", "start cooking table 10", "no wait, start 7 instead", "we're out of salmon", "table 2 is done". When something sells out, CallOut marks it sold out, flags each open order that has it, and proposes an offer (a free swap and a free drink). It only texts those customers after the chef approves the offer or picks a different swap. Customers can type their table number on the order page to see their status and any offer.

**How we used ElevenLabs:** A Conversational AI agent with a short, plain-spoken prompt. It uses Claude Haiku 4.5 as the LLM and Flash TTS for low latency, keeps interruptions on, and turns the silence timeout off so it never asks "still there?" during a busy service. Its webhook tools (board, start, pause, sold out, send offer, back on the menu, done) change real kitchen state, and the kitchen transcript shows each tool call with its latency. The kitchen page uses the web SDK and pushes each new order into the live session, so CallOut speaks without being asked. Measured: orders are read out about 1.1s after they're placed, and replies come about 1.2s after the Line Chef stops talking.

**How we used Daytona:** The whole kitchen backend runs in a public Daytona sandbox: FastAPI, orders and the board, what's sold out, matching an item to its orders, customer messages, table status lookups, and both pages. The agent's tools, the kitchen page and the customer's phone all talk to that sandbox URL. We also used Daytona sandboxes to test ourselves, with a headless kitchen page where a synthetic Line Chef voice talks to the real agent.

## 3. Curveballs to rehearse

All of these passed against the live agent.

| Judge does | CallOut should | If it doesn't |
|---|---|---|
| Orders before you click Start | The order is read out about 0.6s after CallOut connects | Ask "What's on the board?" |
| Two orders land at once | Reads both out in turn, without talking over itself | "What's on the board?" |
| Talks over CallOut mid-sentence ("start table ten") | Stops and starts table 10 within about 0.7s | Repeat the line |
| "No wait, start 7 instead of 10" | "Pausing table 10. Starting table 7." | "Pause 10." then "Start 7." |
| "Start table 12" (no such order) | Says there's no open order for table 12 | Nothing needed, that's correct |
| "What does table 5 have?" | Checks the board and answers from it (never from memory) | |
| "We're out of lobster" (not on the menu) | "Lobster isn't on the menu." | Nothing needed |
| "No more fish", "out of plant burgers", "no more chips" | Matches the menu item (fish is the salmon burger, plant is veggie, chips are fries) | Say the full item name |
| "We're out of burgers" (unclear) | Asks "Which one?", then acts on the answer | Name the burger |
| Sold out on something no open order has ("we're out of veggie burgers") | Marks it sold out and says no orders are affected | Nothing needed |
| Tries to order salmon after it's sold out | The order page shows it as Sold out and won't take it | Point at it: the stock is real |
| Chef says no to the offer, or names another swap | "No" sends nothing; "offer the veggie burger" texts that swap; a sold-out swap gets refused and CallOut asks again | |
| Judge asks how the guest knows | Tap Check status on the phone and type the table number | |
| "Salmon is back" | "Salmon burger is back on the menu." Customers already texted keep their offer | |
| "Table 2 is done" | "Table 2 is done." and the order moves to Done | Click Mark done |
| "Start 7 and 9" | Starts both | One at a time |
| "Undo that" right after a start | Pauses the last table it started | "Pause N." |
| "No bacon on 2" / "take the pickles off 9" / "add cheese to 10" | Changes the add-on: "Updated table 2: classic burger." The card gets a blue "Updated" badge | Say one change at a time |
| Change an add-on that isn't on the order ("no onions on 2") | Says it couldn't make that change and reads the order back | Nothing needed |
| Swap a whole item by voice ("table 10 wants fries instead") | "The guest can change that on their phone." | |
| Chatty line ("the salmon's selling great") | Doesn't mark anything sold out | |
| Off-topic ("what's the weather?", "tell me a joke") | One friendly line, then back to the board. It doesn't assume who is speaking | Move to the next beat |
| Asks "is this scripted?" | Let the judge talk to CallOut themselves, or place their own order | |
| Long silence | Stays quiet and never asks "still there?" | |
| Wifi drops or CallOut goes silent | Reload the kitchen page and click Start CallOut again | Order from a second laptop tab |
| Judge's phone shows a Daytona warning after scanning | Tap Continue (only once), and the order page loads | Order from your phone instead |
| Sandbox is slow on the first load | Load the kitchen page once before you go on | Wait a beat, then ask again |
