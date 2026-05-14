#!/usr/bin/env python3
"""Run the daily Monitor Telegram alert scan from OpenClaw cron."""

from __future__ import annotations

import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from io import StringIO

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
SECRETS_PATH = Path("/root/.openclaw/secrets/runtime-secrets.json")

for path in (str(ROOT_DIR), str(BACKEND_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)


def _load_telegram_token() -> str | None:
    token = os.getenv("MONITOR_TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        return token.strip()
    try:
        payload = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    env_payload = payload.get("env", {})
    return (
        str(
            env_payload.get("MONITOR_TELEGRAM_BOT_TOKEN")
            or env_payload.get("TELEGRAM_BOT_TOKEN")
            or ""
        ).strip()
        or None
    )


def main() -> int:
    token = _load_telegram_token()
    if token:
        os.environ["MONITOR_TELEGRAM_BOT_TOKEN"] = token

    from app.database import SessionLocal
    from app.services.monitor_telegram_alerts import (
        load_monitor_telegram_alert_settings,
        run_monitor_telegram_alert_scan,
    )

    with SessionLocal() as db:
        settings = load_monitor_telegram_alert_settings(db)
        noisy_output = StringIO()
        with redirect_stdout(noisy_output), redirect_stderr(noisy_output):
            summary = run_monitor_telegram_alert_scan(
                db,
                user_id="openclaw-cron",
                settings=settings,
                force_dry_run=False,
            )

    if summary.get("sent", 0) > 0:
        results = ", ".join(
            f"{item.get('symbol')} {item.get('timeframe')} {item.get('status')}"
            for item in summary.get("results", [])
            if item.get("result") == "sent"
        )
        print(f"SENT {summary['sent']}: {results}")
        return 0

    if summary.get("failed", 0) > 0:
        print(f"FAILED {summary['failed']}: {summary.get('results', [])}")
        return 1

    if summary.get("dry_run_count", 0) > 0 and not summary.get("can_send"):
        print(
            "CONFIG_INCOMPLETE: "
            f"dry_run={summary.get('dry_run_count', 0)} "
            f"token_configured={summary.get('token_configured')} "
            f"destination_allowed={summary.get('destination_allowed')} "
            f"chat_id={summary.get('destination_chat_id')} "
            f"thread_id={summary.get('destination_thread_id')}"
        )
        return 1

    print("ANNOUNCE_SKIP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
