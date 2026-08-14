"""Testes do cursor incremental de GET /api/logs/tail (card #502)."""

from __future__ import annotations

from pathlib import Path

import pytest

import app.routes.logs as logs_route
from app.routes.logs import MAX_INCREMENTAL_BYTES


def _snapshot(path: Path) -> dict:
    return logs_route._file_snapshot(path)


class TestIncrementalCursor:
    def test_capture_cursor_and_increment(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text("linha-1\nlinha-2\n", encoding="utf-8")
        snap = _snapshot(log)
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=snap["file_id"])
        assert base["content"] == "linha-1\nlinha-2\n"
        assert base["next_offset"] == log.stat().st_size

        log.write_text("linha-1\nlinha-2\nlinha-3\nlinha-4\n", encoding="utf-8")
        inc = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc["content"] == "linha-3\nlinha-4\n"
        assert inc["cursor_reset"] is False
        assert inc["next_offset"] == log.stat().st_size

    def test_no_new_bytes_returns_empty_and_stable_offset(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text("conteudo\n", encoding="utf-8")
        snap = _snapshot(log)
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=snap["file_id"])
        inc = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc["content"] == ""
        assert inc["next_offset"] == base["next_offset"]

    def test_burst_above_limit_continues_without_duplication(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_bytes(b"a" * 10)
        snap = _snapshot(log)
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=snap["file_id"])
        assert base["next_offset"] == 10

        log.write_bytes(b"a" * 10 + b"a" * 10 + b"b" * (MAX_INCREMENTAL_BYTES + 512))
        inc1 = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc1["cursor_reset"] is False
        assert len(inc1["content"]) == MAX_INCREMENTAL_BYTES
        assert inc1["next_offset"] == base["next_offset"] + MAX_INCREMENTAL_BYTES

        inc2 = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=inc1["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc2["content"] == "b" * 522
        combined = base["content"] + inc1["content"] + inc2["content"]
        assert combined.count("a") == 20
        assert combined.count("b") == MAX_INCREMENTAL_BYTES + 512

    def test_utf8_split_retains_suffix(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_bytes("x".encode() + "🔒".encode()[:2])
        snap = _snapshot(log)
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=snap["file_id"])
        assert base["content"] == "x"
        assert base["next_offset"] == 1

        log.write_bytes("x".encode() + "🔒".encode())
        inc = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc["content"] == "🔒"
        assert inc["next_offset"] == log.stat().st_size

    def test_truncation_resets_cursor(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text("0123456789", encoding="utf-8")
        snap = _snapshot(log)
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=snap["file_id"])
        log.write_text("novo", encoding="utf-8")  # truncado para 4 bytes
        inc = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc["cursor_reset"] is True
        assert inc["content"] == ""

    def test_recreated_file_with_same_or_larger_size_detected_by_identity(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_bytes(b"a" * 100)
        snap = _snapshot(log)
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=snap["file_id"])
        assert base["next_offset"] == 100

        replacement = tmp_path / "replacement.log"
        replacement.write_bytes(b"b" * 200)  # inode novo garantido via os.replace
        import os

        os.replace(replacement, log)
        new_snap = _snapshot(log)
        assert new_snap["file_id"] != snap["file_id"]
        inc = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc["cursor_reset"] is True

    def test_legacy_tail_unchanged_with_additive_fields(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text("l1\nl2\nl3\n", encoding="utf-8")
        legacy = logs_route.tail_log(name="custom", lines=2)
        assert legacy["name"] == "custom"
        assert legacy["content"] == "l2\nl3"
        assert legacy["lines"] == 2
        assert legacy["path"] == str(log)
        assert legacy["next_offset"] == log.stat().st_size
        assert legacy["file_id"]
        assert legacy["cursor_reset"] is False

    def test_missing_file_returns_empty_session(self, tmp_path):
        logs_route.LOG_MAP["custom"].unlink()
        legacy = logs_route.tail_log(name="custom", lines=10)
        assert legacy["content"] == ""
        assert legacy["next_offset"] == 0
        assert legacy["file_id"] == ""
        assert legacy["cursor_reset"] is False

        incremental = logs_route.tail_log(name="custom", lines=10, after_offset=0, file_id=None)
        assert incremental["content"] == ""
        assert incremental["next_offset"] == 0
        assert incremental["cursor_reset"] is False

    def test_direct_call_without_file_id_defaults_to_none(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text("x\n", encoding="utf-8")
        snap = _snapshot(log)
        # Chamada direta sem file_id: o default real é None (Annotated), não Query(None).
        base = logs_route.tail_log(name="custom", lines=10, after_offset=0)
        assert base["content"] == "x\n"
        assert base["cursor_reset"] is False
        assert base["next_offset"] == log.stat().st_size
        inc = logs_route.tail_log(
            name="custom",
            lines=10,
            after_offset=base["next_offset"],
            file_id=snap["file_id"],
        )
        assert inc["content"] == ""
        assert inc["cursor_reset"] is False


@pytest.fixture(autouse=True)
def _custom_log_map(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("", encoding="utf-8")
    logs_route.LOG_MAP["custom"] = log
    yield
    logs_route.LOG_MAP.pop("custom", None)
