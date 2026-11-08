"""Deploy backend/ to a long-lived public Daytona sandbox. Re-run to redeploy.

The sandbox is found by label, so redeploys keep the SAME public URL.
Usage (from repo root):  backend/.venv/bin/python scripts/deploy_daytona.py
Needs DAYTONA_API_KEY (and optionally TOOL_SECRET) in .env.
Writes the live URL to .live.json (gitignored) and prints it.
"""
import json
import os
import pathlib
import time
import urllib.request

import certifi

os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from daytona import CreateSandboxFromSnapshotParams, Daytona, ListSandboxesQuery, SessionExecuteRequest
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABEL = {"app": "hackathon-backend"}
PORT = 8000
SESSION = "server"

load_dotenv(ROOT / ".env")
d = Daytona()


def find_sandbox():
    return next(iter(d.list(ListSandboxesQuery(labels=LABEL))), None)


sb = find_sandbox()
if sb is None:
    print("creating sandbox...")
    sb = d.create(
        CreateSandboxFromSnapshotParams(
            language="python",
            labels=LABEL,
            public=True,  # URL needs no Daytona token; /run is guarded by TOOL_SECRET
            auto_stop_interval=0,  # never auto-stop: this is the live backend
        )
    )
elif str(getattr(sb, "state", "")).lower().endswith("stopped"):
    print("starting stopped sandbox...")
    sb.start()

home = sb.process.exec("pwd").result.strip()
app_dir = f"{home}/backend"
sb.process.exec(f"mkdir -p {app_dir}")
for f in (ROOT / "backend").rglob("*"):
    if f.is_file() and ".venv" not in f.parts and "__pycache__" not in f.parts:
        rel = f.relative_to(ROOT / "backend")
        sb.process.exec(f"mkdir -p {app_dir}/{rel.parent}")
        sb.fs.upload_file(f.read_bytes(), f"{app_dir}/{rel}")
print("uploaded backend/")

r = sb.process.exec("pip install -q -r requirements.txt", cwd=app_dir, timeout=300)
if r.exit_code != 0:
    raise SystemExit(f"pip install failed:\n{r.result}")

env = f"RUN_LOCAL=1 TOOL_SECRET='{os.getenv('TOOL_SECRET', '')}'"
sb.process.exec("pkill -f 'uvicorn app:app' || true")
try:
    sb.process.create_session(SESSION)
except Exception:
    pass  # session already exists from a previous deploy
sb.process.execute_session_command(
    SESSION,
    SessionExecuteRequest(
        command=f"cd {app_dir} && {env} nohup uvicorn app:app --host 0.0.0.0 --port {PORT} > {home}/server.log 2>&1 &",
        run_async=True,
    ),
)

url = sb.get_preview_link(PORT).url.rstrip("/")
for _ in range(30):
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=5) as resp:
            if resp.status == 200:
                break
    except Exception:
        time.sleep(1)
else:
    log = sb.process.exec(f"tail -50 {home}/server.log").result
    raise SystemExit(f"server did not come up:\n{log}")

live = {"sandbox_id": sb.id, "base_url": url, "run_url": f"{url}/run",
        "secret_header": "x-tool-secret (value = TOOL_SECRET in .env)",
        "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
(ROOT / ".live.json").write_text(json.dumps(live, indent=2))
print(json.dumps(live, indent=2))
