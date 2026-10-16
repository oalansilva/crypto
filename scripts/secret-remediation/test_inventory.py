import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess

import pytest

SPEC = importlib.util.spec_from_file_location("inventory", Path(__file__).with_name("inventory.py"))
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)
SENTINEL = "SYNTHETIC-ONLY-DO-NOT-EXPORT-7f9ab"


def test_allowlist_discards_every_untrusted_field():
    record = {
        key: SENTINEL
        for key in (
            "Secret",
            "Match",
            "File",
            "Commit",
            "Message",
            "Fingerprint",
            "RuleID",
            "Author",
            "Email",
            "StartLine",
            "Description",
            "classification",
        )
    }
    result = inventory.export_findings([record], 10, "history", "2026-10-12")
    encoded = json.dumps(result)
    assert SENTINEL not in encoded
    assert result["findings"][0]["result"] == "pendente"
    assert set(result["findings"][0]) == {
        "id",
        "service",
        "presence",
        "environment",
        "date",
        "classification",
        "result",
        "reason",
        "owner",
    }


def test_publication_ranges_account_for_every_pending_alert():
    scan = inventory.export_findings([{"Secret": SENTINEL}] * 3, 10, "history", "2026-10-12")
    report = inventory.publication_report({"scans": [scan], "overall": "incomplete"})
    group = report["scans"][0]["pending_alerts"]
    assert (group["first_id"], group["last_id"], group["count"]) == (
        "history-000001",
        "history-000003",
        3,
    )
    assert group["invalidation_DEV"] == group["invalidation_PROD"] == "pendente"
    assert SENTINEL not in json.dumps(report)


@pytest.mark.parametrize("code,records", [(1, []), (2, []), (None, []), (10, []), (0, [{}])])
def test_incomplete_never_means_clean(code, records):
    assert (
        inventory.export_findings(records, code, "history", "2026-10-12")["state"] == "incomplete"
    )


@pytest.mark.parametrize("source,date", [(SENTINEL, "2026-10-12"), ("history", SENTINEL)])
def test_caller_metadata_is_validated(source, date):
    with pytest.raises(inventory.CollectionError):
        inventory.export_findings([], 0, source, date)


def test_malformed_report_is_rejected():
    for records in ({"Secret": SENTINEL}, [SENTINEL]):
        with pytest.raises(inventory.CollectionError):
            inventory.export_findings(records, 10, "history", "2026-10-12")


def test_paginated_metadata_counts_without_exporting_values():
    assert inventory.api_count('[{"private":"' + SENTINEL + '"}]\n[{}]') == 2
    assert inventory.api_count('{"artifacts":[{}]}\n{"artifacts":[{},{}]}', "artifacts") == 3


def test_known_history_survives_tip_removal_and_keeps_variants_private(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
    for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")):
        subprocess.run(["git", "config", key, value], cwd=repo, capture_output=True, check=True)
    (repo / "backend").mkdir()
    config = repo / "backend/.env"
    config.write_text("JWT_SECRET=" + SENTINEL + "\n")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "synthetic config"], cwd=repo, capture_output=True, check=True
    )
    subprocess.run(["git", "rm", "backend/.env"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "remove tip"], cwd=repo, capture_output=True, check=True)
    raw = tmp_path / "raw"
    raw.mkdir(mode=0o700)
    report = inventory.known_history(repo, raw, "2026-10-12")
    assert report["keys"][0]["service"] == "JWT_SECRET"
    assert len(report["variant_matrix"]) == 2
    assert {r["environment"] for r in report["variant_matrix"]} == {"DEV", "PROD"}
    assert SENTINEL not in json.dumps(report)
    assert SENTINEL in (raw / "known-variant-map.json").read_text()


def test_scanner_output_and_errors_stay_restricted(tmp_path, capsys):
    raw = tmp_path / "raw"
    raw.mkdir(mode=0o700)
    scanner = tmp_path / "fake-scanner"
    scanner.write_text(
        "#!/usr/bin/env python3\nimport sys,json\np=next(x.split('=',1)[1] for x in sys.argv if x.startswith('--report-path='))\nopen(p,'w').write(json.dumps([{'Secret': '"
        + SENTINEL
        + "', 'File':'"
        + SENTINEL
        + "'}]))\nprint('"
        + SENTINEL
        + "')\nprint('"
        + SENTINEL
        + "',file=sys.stderr)\nsys.exit(10)\n"
    )
    scanner.chmod(0o700)
    result = inventory.scan(scanner, tmp_path, raw, "dir", "tracked_content", "2026-10-12")
    assert result["state"] == "findings"
    assert SENTINEL not in json.dumps(result)
    captured = capsys.readouterr()
    assert not captured.out and not captured.err
    assert SENTINEL in (raw / "tracked_content.stderr").read_text()
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in raw.iterdir())


def test_operational_failure_report_cannot_look_clean(tmp_path):
    scanner = tmp_path / "fake-scanner"
    scanner.write_text(
        "#!/usr/bin/env python3\nimport sys\np=next(x.split('=',1)[1] for x in sys.argv if x.startswith('--report-path='))\nopen(p,'w').write('[]')\nprint('"
        + SENTINEL
        + "',file=sys.stderr)\nsys.exit(2)\n"
    )
    scanner.chmod(0o700)
    result = inventory.scan(scanner, tmp_path, tmp_path, "dir", "tracked_content", "2026-10-12")
    assert result["state"] == "incomplete"
    assert SENTINEL not in json.dumps(result)


def test_directory_source_with_fingerprint_file_fails_closed(tmp_path):
    (tmp_path / ".gitleaksignore").write_text(SENTINEL)
    result = inventory.scan(
        tmp_path / "not-executed", tmp_path, tmp_path, "dir", "tracked_content", "2026-10-12"
    )
    assert result["state"] == "incomplete"
    assert SENTINEL not in json.dumps(result)


def test_storage_rejects_checkout_symlink_and_world_readable(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
    with pytest.raises(inventory.CollectionError):
        inventory.private_root(repo / "raw", repo)
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o755)
    with pytest.raises(inventory.CollectionError):
        inventory.private_root(outside, repo)
    link = tmp_path / "link"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(inventory.CollectionError):
        inventory.private_root(link / "raw", repo)
    raw = inventory.private_root(tmp_path / "fresh", repo)
    assert raw.stat().st_mode & 0o777 == 0o700


def test_backup_all_cells_json_binary_and_hostile_names(tmp_path):
    source = tmp_path / "source.db"
    c = sqlite3.connect(source)
    hostile = 'table"' + SENTINEL
    quoted = '"' + hostile.replace('"', '""') + '"'
    c.execute("CREATE TABLE " + quoted + " (n INTEGER, txt TEXT, data TEXT, blob BLOB)")
    c.execute(
        "INSERT INTO " + quoted + " VALUES(?,?,?,?)",
        (
            1,
            "private@example.invalid",
            '{"nested":{"password":"' + SENTINEL + '"}}',
            SENTINEL.encode(),
        ),
    )
    c.execute(
        "INSERT INTO " + quoted + " VALUES(?,?,?,?)",
        (2, "arbitrary text", '{"trading":{"window":10}}', None),
    )
    c.commit()
    c.close()
    original = source.read_bytes()
    raw = tmp_path / "raw"
    raw.mkdir(mode=0o700)
    report = inventory.inspect_backup(source, raw)
    assert source.read_bytes() == original
    assert (raw / "backup.sqlite").stat().st_mode & 0o777 == 0o400
    assert SENTINEL not in json.dumps(report)
    assert "private@example.invalid" not in json.dumps(report)
    assert report["tables"][0]["rows"] == 2
    cols = report["tables"][0]["columns"]
    assert cols[1]["categories"] == {"personal_candidate": 1, "text_pending": 1}
    assert cols[2]["categories"] == {"credential_candidate": 1, "json_pending": 1}
    assert cols[3]["categories"] == {"binary_pending": 1, "null": 1}
    assert all(c["result"] == "pendente" for c in cols)


def test_cli_errors_never_print_path_or_exception(tmp_path):
    p = subprocess.run(
        [
            "python3",
            str(Path(__file__).with_name("inventory.py")),
            "--repo",
            str(tmp_path),
            "--restricted-root",
            str(tmp_path / SENTINEL),
            "--scanner",
            str(tmp_path / SENTINEL),
        ],
        capture_output=True,
        text=True,
    )
    assert p.returncode == 2
    assert SENTINEL not in p.stdout + p.stderr
    assert json.loads(p.stdout)["state"] == "incomplete"


@pytest.mark.parametrize("script", ["inventory.py", "install_scanner.py", "rehearsal.py"])
def test_invalid_cli_arguments_cannot_echo_sensitive_input(script):
    p = subprocess.run(
        ["python3", str(Path(__file__).with_name(script)), "--" + SENTINEL],
        capture_output=True,
        text=True,
    )
    assert p.returncode == 2
    assert SENTINEL not in p.stdout + p.stderr
    assert not p.stderr
    assert json.loads(p.stdout)["reason"] == "invalid_arguments_no_raw_output"


def test_pinned_real_scanner_detects_fixture(tmp_path):
    scanner = os.environ.get("CARD1071_GITLEAKS")
    if not scanner:
        pytest.skip("Set CARD1071_GITLEAKS for pinned scanner integration")
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "config.txt").write_text(
        "JWT_SECRET="
        + SENTINEL
        + "\nWORKFLOW_DATABASE_URL=postgresql://synthetic:synthetic-password@localhost/test\n"
    )
    raw = tmp_path / "raw"
    raw.mkdir(mode=0o700)
    result = inventory.scan(Path(scanner), fixture, raw, "dir", "tracked_content", "2026-10-12")
    assert result["state"] == "findings"
    assert result["count"] >= 2
    assert SENTINEL not in json.dumps(result)


@pytest.mark.parametrize("mode,label", [("git", "history"), ("dir", "tracked_content")])
def test_pinned_scanner_ignores_repository_fingerprint_suppressions(
    tmp_path, monkeypatch, mode, label
):
    scanner = os.environ.get("CARD1071_GITLEAKS")
    if not scanner:
        pytest.skip("Set CARD1071_GITLEAKS for pinned scanner integration")
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    subprocess.run(["git", "init", str(fixture)], capture_output=True, check=True)
    for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")):
        subprocess.run(["git", "config", key, value], cwd=fixture, capture_output=True, check=True)
    (fixture / "config.txt").write_text("JWT_SECRET=" + SENTINEL + "\n")
    subprocess.run(["git", "add", "."], cwd=fixture, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "synthetic fixture"], cwd=fixture, capture_output=True, check=True
    )
    if mode == "git":
        worktree = tmp_path / "worktree"
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree)],
            cwd=fixture,
            capture_output=True,
            check=True,
        )
        fixture = worktree
    inherited_cwd = fixture if mode == "git" else tmp_path / "inherited-cwd"
    if mode == "dir":
        inherited_cwd.mkdir()
    monkeypatch.chdir(inherited_cwd)
    initial = tmp_path / "initial"
    initial.mkdir(mode=0o700)
    first = inventory.scan(Path(scanner), fixture, initial, mode, label, "2026-10-12")
    assert first["state"] == "findings"
    records = json.loads((initial / (label + ".json")).read_text())
    (inherited_cwd / ".gitleaksignore").write_text(
        "\n".join(r["Fingerprint"] for r in records) + "\n"
    )
    default_report = initial / "default.json"
    args = [
        scanner,
        mode,
        str(fixture),
        "--config",
        str(inventory.CONFIG),
        "--redact=100",
        "--ignore-gitleaks-allow",
        "--exit-code=10",
        "--report-format=json",
        "--report-path=" + str(default_report),
        "--no-banner",
    ]
    if mode == "git":
        args.append("--log-opts=--all --full-history -m")
    default = inventory.command(args, initial, "default")
    assert default.returncode == 0
    assert json.loads(default_report.read_text()) == []
    corrected = tmp_path / "corrected"
    corrected.mkdir(mode=0o700)
    result = inventory.scan(Path(scanner), fixture, corrected, mode, label, "2026-10-12")
    assert result["state"] == "findings"
    assert result["count"] == first["count"]
    assert SENTINEL not in json.dumps(result)
    ignore = corrected / (label + "-gitleaks.ignore")
    assert ignore.read_bytes() == b""
    assert ignore.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("symlink_kind", ["ancestor", "file"])
def test_tracked_snapshot_rejects_all_symlink_components(tmp_path, symlink_kind):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
    tracked_dir = repo / "nested"
    tracked_dir.mkdir()
    tracked = tracked_dir / "config.txt"
    tracked.write_text("synthetic tracked content\n")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    external = outside / "config.txt"
    external.write_text(SENTINEL)
    tracked.unlink()
    if symlink_kind == "ancestor":
        tracked_dir.rmdir()
        tracked_dir.symlink_to(outside, target_is_directory=True)
    else:
        tracked.symlink_to(external)
    scanner = tmp_path / "fake-scanner"
    scanner.write_text(
        "#!/usr/bin/env python3\nimport sys\n"
        "if sys.argv[1] == 'version':\n print('" + inventory.VERSION + "')\n"
        "else:\n p=next(x.split('=',1)[1] for x in sys.argv if x.startswith('--report-path='))\n"
        " open(p,'w').write('[]')\n"
    )
    scanner.chmod(0o700)
    raw = tmp_path / "raw"
    raw.mkdir(mode=0o700)
    result = inventory.inventory(repo, raw, scanner)
    tracked_result = next(s for s in result["scans"] if s["source"] == "tracked_content")
    assert tracked_result["state"] == "incomplete"
    assert result["overall"] == "incomplete"
    assert not any((raw / "tracked-snapshot").iterdir())
    assert external.read_text() == SENTINEL
    assert SENTINEL not in json.dumps(result)
