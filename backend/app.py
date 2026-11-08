"""Server tool backend for an ElevenLabs voice agent.

The agent calls POST /run with {"code": "..."}; we run it in a Daytona
sandbox and return stdout so the agent can say the result out loud.
Run: uvicorn app:app --reload --port 8000  (expose with ngrok/cloudflared)
"""
import os
import time

from daytona import Daytona
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

load_dotenv()
app = FastAPI()
_sandbox = None  # reuse one warm sandbox to keep voice latency low


def sandbox():
    global _sandbox
    if _sandbox is None:
        _sandbox = Daytona().create()  # reads DAYTONA_API_KEY from env
    return _sandbox


class RunRequest(BaseModel):
    code: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/run")
def run(req: RunRequest, x_tool_secret: str | None = Header(default=None)):
    secret = os.getenv("TOOL_SECRET")
    if secret and x_tool_secret != secret:
        raise HTTPException(status_code=401, detail="bad secret")
    t0 = time.time()
    resp = sandbox().process.code_run(req.code)
    return {
        "exit_code": resp.exit_code,
        "output": (resp.result or "")[:2000],
        "ms": int((time.time() - t0) * 1000),
    }
