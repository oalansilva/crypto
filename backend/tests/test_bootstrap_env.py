"""Tests for ops/bootstrap_env.py — card #752 append-only."""
import subprocess, sys
from pathlib import Path
import pytest
SCRIPT = Path(__file__).resolve().parents[2] / "ops" / "bootstrap_env.py"
assert SCRIPT.is_file()
PISO_DST = "DATABASE_URL=postgresql+psycopg2://user:pass@127.0.0.1:5432/db\nJWT_SECRET=abcdefghijklmnopqrstuvwxyz0123456789ABCDEF\n"
TELEGRAM_PATCH = "MONITOR_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11\nTELEGRAM_WEBHOOK_SECRET=supersecretwebhookvalue1234567890\nMONITOR_TELEGRAM_BOT_USERNAME=Criptofarol_bot\nMONITOR_TELEGRAM_ALERTS_ENABLED=1\n"
def run_script(dest: Path, from_file: Path | None = None, stdin_text: str | None = None):
    cmd = [sys.executable, str(SCRIPT), "--file", str(dest)]
    if from_file is not None:
        cmd += ["--from-file", str(from_file)]
    return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True)
def write_dest(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    path.chmod(0o600)
def test_ac1(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, PISO_DST + "WORKFLOW_DATABASE_URL=postgresql://wf\n")
    patch = tmp_path / "patch.env"
    patch.write_text(TELEGRAM_PATCH, encoding="utf-8")
    r1 = run_script(dest, patch)
    assert r1.returncode == 0
    assert len(list(tmp_path.glob(".env.bak-*"))) == 1
    r2 = run_script(dest, patch)
    assert r2.returncode == 0
    assert len(list(tmp_path.glob(".env.bak-*"))) == 1
def test_ac2(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, "MONITOR_TELEGRAM_BOT_TOKEN=123\nJWT_SECRET=abc1234567890123456789012345678\n")
    patch = tmp_path / "patch.env"
    patch.write_text("NEWKEY=val\n", encoding="utf-8")
    r = run_script(dest, patch)
    assert r.returncode != 0
def test_ac3(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, "DATABASE_URL=postgresql://a\n")
    patch = tmp_path / "patch.env"
    patch.write_text("NEW=1\n", encoding="utf-8")
    r = run_script(dest, patch)
    assert r.returncode != 0
def test_ac4(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, "DATABASE_URL=postgresql://a\nJWT_SECRET=mysecret1234567890123456789012\n")
    patch = tmp_path / "p.env"
    patch.write_text("NEWKEY=val\n", encoding="utf-8")
    r = run_script(dest, patch)
    assert r.returncode == 0
def test_ac5(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, "DATABASE_URL=postgresql://a\nJWT_SECRET=secret1234567890123456789012345678\n")
    patch = tmp_path / "bad.env"
    patch.write_text("JWT_SECRET=different\n", encoding="utf-8")
    r = run_script(dest, patch)
    assert r.returncode != 0
def test_ac6(tmp_path: Path):
    patch = tmp_path / "p.env"
    patch.write_text("NEW=1\n", encoding="utf-8")
    dest = tmp_path / "nonexistent.env"
    r = run_script(dest, patch)
    assert r.returncode != 0
def test_ac7(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, PISO_DST)
    from_file = tmp_path / "f.env"
    from_file.write_text("FOO=a\n", encoding="utf-8")
    r = run_script(dest, from_file, stdin_text="FOO=b\n")
    assert r.returncode == 0
    assert "FOO=b" in dest.read_text(encoding="utf-8")
def test_ac8(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, PISO_DST)
    empty = tmp_path / "empty.env"
    empty.write_text("# only comment\n", encoding="utf-8")
    r = run_script(dest, empty)
    assert r.returncode != 0
def test_ac9(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, "# header\n\nDATABASE_URL=postgresql://a\nJWT_SECRET=secret1234567890123456789012345678\nFOO=old # keep comment\n\n# footer\n")
    patch = tmp_path / "p.env"
    patch.write_text("FOO=new\nNEWKEY=val\n", encoding="utf-8")
    r = run_script(dest, patch)
    assert r.returncode == 0
    assert "FOO=new # keep comment" in dest.read_text(encoding="utf-8")
def test_ac10(tmp_path: Path):
    dest = tmp_path / ".env"
    write_dest(dest, PISO_DST)
    patch = tmp_path / "p.env"
    patch.write_text("NEWKEY=val\n", encoding="utf-8")
    r = run_script(dest, patch)
    assert r.returncode == 0
    assert oct(dest.stat().st_mode & 0o777) == "0o600"
    assert len(list(tmp_path.glob(".env.bak-*"))) == 1
