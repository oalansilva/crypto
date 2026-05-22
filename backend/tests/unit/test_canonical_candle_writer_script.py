from __future__ import annotations

import fcntl
import json

import scripts.run_canonical_candle_writer_once as writer


def test_canonical_candle_writer_records_success(monkeypatch, tmp_path, capsys):
    lock_path = tmp_path / "writer.lock"
    state_path = tmp_path / "writer-state.json"
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", str(lock_path))
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_STATE_FILE", str(state_path))
    monkeypatch.setattr(writer, "run_ohlcv_ingestion_once", lambda: 7)

    assert writer.main() == 0

    assert "canonical_candle_writer_runs=7" in capsys.readouterr().out
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "success"
    assert state["runs"] == 7
    assert state["lock_path"] == str(lock_path)
    assert state["duration_seconds"] >= 0


def test_canonical_candle_writer_skips_when_lock_held(monkeypatch, tmp_path, capsys):
    lock_path = tmp_path / "writer.lock"
    state_path = tmp_path / "writer-state.json"
    calls = []
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", str(lock_path))
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_STATE_FILE", str(state_path))
    monkeypatch.setattr(writer, "run_ohlcv_ingestion_once", lambda: calls.append("run") or 1)

    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert writer.main() == 0

    assert calls == []
    assert "canonical_candle_writer_skipped=lock_held" in capsys.readouterr().out
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "skipped_lock_held"
    assert state["runs"] == 0


def test_canonical_candle_writer_records_failure(monkeypatch, tmp_path):
    lock_path = tmp_path / "writer.lock"
    state_path = tmp_path / "writer-state.json"
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", str(lock_path))
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_STATE_FILE", str(state_path))

    def _fail():
        raise RuntimeError("writer failed")

    monkeypatch.setattr(writer, "run_ohlcv_ingestion_once", _fail)

    try:
        writer.main()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected writer failure")

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "failed"
    assert state["error"] == "writer failed"
