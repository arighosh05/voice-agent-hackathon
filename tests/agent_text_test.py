"""Drive the Expo agent over its websocket with text turns; print what it says and tool calls."""
import asyncio, json, sys, time, ssl, urllib.request, os
import websockets
AGENT = sys.argv[1]
B = "https://8000-b0415f9d-03f3-42cc-a0fa-61e0450a7c64.daytonaproxy01.net"
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
def http(method, path, body=None):
    r = urllib.request.Request(B+path, method=method, data=json.dumps(body).encode() if body else None, headers={"content-type":"application/json"})
    return json.load(urllib.request.urlopen(r, timeout=20, context=ctx))
STEPS = json.loads(sys.argv[2])
async def main():
    http("POST","/reset")
    async with websockets.connect(f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={AGENT}", ssl=ctx, max_size=None) as ws:
        await ws.send(json.dumps({"type":"conversation_initiation_client_data"}))
        t0=time.time(); last_agent=time.time()
        async def reader():
            nonlocal last_agent
            async for raw in ws:
                m=json.loads(raw); t=m.get("type")
                if t=="ping": await ws.send(json.dumps({"type":"pong","event_id":m["ping_event"]["event_id"]}))
                elif t=="agent_response": last_agent=time.time(); print(f"[{time.time()-t0:5.1f}] EXPO: {m['agent_response_event']['agent_response']}", flush=True)
                elif t in ("agent_tool_response","client_tool_call","agent_tool_request"): print(f"[{time.time()-t0:5.1f}] TOOL {t}: {json.dumps(m)[:300]}", flush=True)
                elif t=="user_transcript": pass
        rt=asyncio.create_task(reader())
        await asyncio.sleep(4)
        for s in STEPS:
            if s.startswith("ORDER "):
                o=http("POST","/order",json.loads(s[6:])); msg=f"[NEW TICKET] {o['callout']}"
            else: msg=s
            print(f"[{time.time()-t0:5.1f}] >> {msg}", flush=True)
            sent=time.time()
            await ws.send(json.dumps({"type":"user_message","text":msg}))
            await asyncio.sleep(float(os.environ.get("GAP","6")))
        rt.cancel()
    print("BOARD:", http("GET","/board")["summary"])
    pass
asyncio.run(main())
