"""Minimal Trace Viewer (dev) for Strategy Lab.

This is NOT LangGraph Studio.

Purpose: provide a clickable URL (`LAB_TRACE_PUBLIC_URL`) that the Lab UI can link to.
We serve a simple HTML page that renders the stored Lab trace events.

URL format:
- /lab-<run_id>

Data source:
- backend/app/logs/lab_runs/<run_id>.jsonl (trace events)

Security:
- Single-tenant MVP; no auth.
- Intended for dev usage only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Lab Trace Viewer", version="0.1")


def _runs_dir() -> Path:
    # trace_viewer.py -> backend/app -> backend
    base = Path(__file__).resolve().parents[1]
    d = base / "logs" / "lab_runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _trace_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.jsonl"


def _read_trace(run_id: str, limit: int = 2000) -> List[Dict[str, Any]]:
    p = _trace_path(run_id)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    out: List[Dict[str, Any]] = []
    for line in lines[-limit:]:
        line = (line or "").strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/{thread_id}")
async def view(thread_id: str) -> HTMLResponse:
    # Expected: lab-<run_id>
    tid = (thread_id or "").strip()
    if not tid.startswith("lab-") or len(tid) < 10:
        raise HTTPException(status_code=400, detail="invalid thread_id")

    run_id = tid[len("lab-") :]
    events = _read_trace(run_id)

    # Render a tiny HTML page.
    data = json.dumps(events, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang=\"pt-br\">
<head>
  <meta charset=\"utf-8\"/>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
  <title>Lab Trace — {tid}</title>
  <style>
    body {{ background:#0b0b0f; color:#eaeaf0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 20px; }}
    a {{ color:#9ae6b4; }}
    .muted {{ color:#a0aec0; font-size: 12px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background:#111827; border:1px solid #1f2937; padding: 12px; border-radius: 12px; }}
  </style>
</head>
<body>
  <h2>Trace (dev) — {tid}</h2>
  <div class=\"muted\">Leitura direta de <code>backend/logs/lab_runs/{run_id}.jsonl</code> • eventos: {len(events)}</div>
  <p class=\"muted\">Observação: isto é um viewer mínimo (não é LangGraph Studio).</p>
  <pre id=\"out\"></pre>
  <script>
    const events = {data};
    document.getElementById('out').textContent = JSON.stringify(events, null, 2);
  </script>
</body>
</html>"""

    return HTMLResponse(content=html)


@app.get("/{thread_id}.json")
async def view_json(thread_id: str) -> JSONResponse:
    tid = (thread_id or "").strip()
    if not tid.startswith("lab-") or len(tid) < 10:
        raise HTTPException(status_code=400, detail="invalid thread_id")
    run_id = tid[len("lab-") :]
    return JSONResponse(_read_trace(run_id))
