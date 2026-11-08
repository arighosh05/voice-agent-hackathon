import asyncio, json, sys, time, ssl, urllib.request, statistics
import websockets
AG="agent_9201m6yj0n8fehp8xtmfvks0ztjb"; B="https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net"
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
env = dict(l.split("=",1) for l in open(__import__("pathlib").Path(__file__).resolve().parent.parent / ".env").read().splitlines() if "=" in l and not l.startswith("#"))
K = env["ELEVENLABS_API_KEY"].strip()
def el(method, path, body=None):
    r = urllib.request.Request("https://api.elevenlabs.io"+path, method=method, data=json.dumps(body).encode() if body else None, headers={"xi-api-key":K,"content-type":"application/json"})
    try: return json.load(urllib.request.urlopen(r, timeout=60, context=ctx))
    except urllib.error.HTTPError as e: return {"error": e.read().decode()[:300]}
def http(method, path, body=None):
    r = urllib.request.Request(B+path, method=method, data=json.dumps(body).encode() if body else None, headers={"content-type":"application/json"})
    return json.load(urllib.request.urlopen(r, timeout=20, context=ctx))
LINES = ["[NEW TICKET] Ordering, table 4: salmon burger, extra cheese, hold the pickles.", "What's on the board?", "Fire table four.", "No wait, fire seven instead of four.", "We're out of salmon."]
async def run():
    http("POST","/reset"); http("POST","/order",{"table":4,"items":[{"name":"salmon burger","mods":["extra cheese","no pickles"]}]})
    res=[]; log=[]
    async with websockets.connect(f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={AG}", ssl=ctx, max_size=None) as ws:
        await ws.send(json.dumps({"type":"conversation_initiation_client_data"}))
        state={"sent":None,"first_audio":None,"tools":[],"text":[]}
        async def reader():
            async for raw in ws:
                m=json.loads(raw); t=m.get("type")
                if t=="ping": await ws.send(json.dumps({"type":"pong","event_id":m["ping_event"]["event_id"]}))
                elif t=="audio" and state["sent"] and state["first_audio"] is None: state["first_audio"]=time.time()-state["sent"]
                elif t=="agent_tool_response": state["tools"].append(m["agent_tool_response"]["tool_name"])
                elif t=="agent_response": state["text"].append(m["agent_response_event"]["agent_response"])
        rt=asyncio.create_task(reader()); await asyncio.sleep(3)
        for line in LINES:
            state.update(sent=time.time(), first_audio=None, tools=[], text=[])
            await ws.send(json.dumps({"type":"user_message","text":line}))
            await asyncio.sleep(9 if "board" in line else 6)
            res.append(state["first_audio"]); log.append((line[:28], round(state["first_audio"] or -1,2), state["tools"], " | ".join(state["text"])[:90]))
        rt.cancel()
    return res, log, http("GET","/board")["summary"]
for llm in sys.argv[1:]:
    r = el("PATCH", f"/v1/convai/agents/{AG}", {"conversation_config":{"agent":{"prompt":{"llm":llm}}}})
    if "error" in r: print(llm, "REJECTED", r["error"][:150]); continue
    res, log, board = asyncio.run(run())
    ok = [x for x in res if x]
    print(f"\n=== {llm}: median first-audio {statistics.median(ok):.2f}s, max {max(ok):.2f}s")
    for l in log: print("  ", l)
    print("   board:", board[:160])
