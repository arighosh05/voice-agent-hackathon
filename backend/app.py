"""Server tool backend for an ElevenLabs voice agent.

The agent calls POST /run with {"code": "..."}; we run it in a Daytona
sandbox and return stdout so the agent can say the result out loud.
Run: uvicorn app:app --reload --port 8000  (expose with ngrok/cloudflared)
"""
import os
import subprocess
import sys
import time

import certifi

# python.org macOS builds ship without root certs; use certifi's bundle.
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from daytona import CreateSandboxFromSnapshotParams, Daytona
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

from expo import router as expo_router  # noqa: E402

app.include_router(expo_router)
_sandbox = None  # reuse one warm sandbox to keep voice latency low


def sandbox():
    global _sandbox
    if _sandbox is None:
        _sandbox = Daytona().create(
            CreateSandboxFromSnapshotParams(auto_stop_interval=15)  # minutes idle
        )  # reads DAYTONA_API_KEY from env
    return _sandbox


class RunRequest(BaseModel):
    code: str


@app.on_event("shutdown")
def cleanup():
    # Never leave a sandbox running after the server stops.
    global _sandbox
    if _sandbox is not None:
        try:
            _sandbox.delete()
        finally:
            _sandbox = None


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/run")
def run(req: RunRequest, x_tool_secret: str | None = Header(default=None)):
    secret = os.getenv("TOOL_SECRET")
    if secret and x_tool_secret != secret:
        raise HTTPException(status_code=401, detail="bad secret")
    t0 = time.time()
    if os.getenv("RUN_LOCAL") == "1":
        # Deployed inside a Daytona sandbox already: run the code right here.
        p = subprocess.run([sys.executable, "-c", req.code], capture_output=True, text=True, timeout=30)
        return {"exit_code": p.returncode, "output": (p.stdout + p.stderr)[:2000],
                "ms": int((time.time() - t0) * 1000)}
    sb = sandbox()
    try:
        resp = sb.process.code_run(req.code)
    except Exception:
        # Likely auto-stopped after idle: start it again and retry once.
        sb.start()
        resp = sb.process.code_run(req.code)
    return {
        "exit_code": resp.exit_code,
        "output": (resp.result or "")[:2000],
        "ms": int((time.time() - t0) * 1000),
    }
