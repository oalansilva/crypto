from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path


def _load_scan_module(name: str):
    module_path = Path(__file__).resolve().parents[3] / "ops" / "run_monitor_telegram_alert_scan.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cron_wrapper_block_prod_bot_ignores_json_and_token_leftovers(tmp_path, monkeypatch, capsys):
    module = _load_scan_module("run_monitor_telegram_alert_scan_block_test")

    secret_path = tmp_path / "runtime-secrets.json"
    secret_path.write_text(
        json.dumps({"env": {"TELEGRAM_BOT_TOKEN": "leftover-prod-token"}}),
        encoding="utf-8",
    )
    module.SECRETS_CANDIDATES = (secret_path,)
    monkeypatch.setenv("CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT", "1")
    monkeypatch.setenv("MONITOR_TELEGRAM_BOT_TOKEN", "prod-like-token")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "leftover-prod-token")
    monkeypatch.setenv("MONITOR_TELEGRAM_SECRETS_FILE", str(secret_path))

    assert module._load_telegram_token() is None
    assert os.getenv("MONITOR_TELEGRAM_BOT_TOKEN") == ""
    assert os.getenv("TELEGRAM_BOT_TOKEN") == ""
    assert os.getenv("MONITOR_TELEGRAM_SECRETS_FILE") == ""

    rc = module.main()
    captured = capsys.readouterr()
    assert rc == 1
    assert "CONFIG_INCOMPLETE" in captured.out
    assert "DEV_ISOLATION" in captured.out
    assert "ANNOUNCE_SKIP" not in captured.out
    assert "SENT" not in captured.out
    assert "SENT" not in captured.err
