#!/usr/bin/env python3
"""Local forensics: only closed-vocabulary evidence leaves restricted storage."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
from urllib.parse import urlsplit

VERSION = "8.24.3"
CONFIG = Path(__file__).with_name("gitleaks.toml")
KEYS = (
    "BINANCE_API_KEY",
    "BINANCE_API_SECRET",
    "JWT_SECRET",
    "DATABASE_URL",
    "WORKFLOW_DATABASE_URL",
    "VITE_API_URL",
)
KNOWN = (".env.binance", "backend/.env", "frontend/.env")
SOURCES = ("history", "tracked_content", "messages")
SERVICES = {"historical-config-key": "credencial_config", "database-url-password": "PostgreSQL"}


class CollectionError(Exception):
    """Contains no raw subprocess output, source path or SQL error."""


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes invalid user arguments, which may be sensitive.
        print('{"state":"incomplete","reason":"invalid_arguments_no_raw_output"}')
        raise SystemExit(2)


def private_root(path, repo):
    path = Path(path).absolute()
    repo = Path(repo).resolve()
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise CollectionError()
    path = path.resolve()
    if path == repo or repo in path.parents:
        raise CollectionError()
    ancestor = path
    while not ancestor.exists():
        ancestor = ancestor.parent
    # Reject storage in any Git checkout, not only the scanned repo.
    if (
        subprocess.run(
            ["git", "-C", str(ancestor), "rev-parse", "--git-dir"], capture_output=True
        ).returncode
        == 0
    ):
        raise CollectionError()
    os.umask(0o077)
    if path.exists():
        s = path.stat()
        if not path.is_dir() or s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) != 0o700:
            raise CollectionError()
        if any(path.iterdir()):
            raise CollectionError()
    else:
        path.mkdir(mode=0o700, parents=True)
    return path


def raw_write(root, name, data):
    p = root / name
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode())
    return p


def command(argv, root, label, cwd=None, timeout=900):
    env = os.environ.copy()
    for name in list(env):
        if name.startswith("GITLEAKS_") or name in ("GIT_EXTERNAL_DIFF", "GIT_DIFF_OPTS"):
            env.pop(name)
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=timeout)
        raw_write(root, label + ".stdout", p.stdout)
        raw_write(root, label + ".stderr", p.stderr)
        return p
    except (OSError, subprocess.TimeoutExpired):
        raw_write(root, label + ".error", "execution_incomplete")
        return None


def export_findings(records, exit_code, source, date):
    """Never export supplied names, paths, messages, classifications or RuleID text."""
    if source not in SOURCES or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise CollectionError()
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise CollectionError()
    if (
        exit_code not in (0, 10)
        or (exit_code == 0 and records)
        or (exit_code == 10 and not records)
    ):
        return {"source": source, "state": "incomplete", "count": len(records), "findings": []}
    rows = []
    for i, record in enumerate(records, 1):
        rule = record.get("RuleID")
        service = (
            SERVICES.get(rule, "possivel_segredo") if isinstance(rule, str) else "possivel_segredo"
        )
        rows.append(
            {
                "id": f"{source}-{i:06d}",
                "service": service,
                "presence": True,
                "environment": "indeterminado",
                "date": date,
                "classification": "possivel_segredo",
                "result": "pendente",
                "reason": "exige_classificacao_e_prova_de_invalidacao",
                "owner": "operador",
            }
        )
    return {
        "source": source,
        "state": "findings" if rows else "no_findings",
        "count": len(rows),
        "findings": rows,
    }


def publication_report(evidence):
    """Compact only our constructed evidence; ranges assign every alert a pending owner.

    Caller must use the in-memory collector result, never an arbitrary scanner JSON.
    Full per-alert mapping remains in the private evidence file.
    """
    result = dict(evidence)
    result["scans"] = []
    for scan_result in evidence["scans"]:
        summary = {k: scan_result[k] for k in ("source", "state", "count")}
        findings = scan_result["findings"]
        if findings:
            summary["pending_alerts"] = {
                "first_id": findings[0]["id"],
                "last_id": findings[-1]["id"],
                "count": len(findings),
                "classification": "possivel_segredo",
                "result": "pendente",
                "owner": "operador",
                "environment": "indeterminado",
                "invalidation_DEV": "pendente",
                "invalidation_PROD": "pendente",
                "proof_required": "classificacao_e_revogacao_autoritativa_ou_teste_conclusivo",
                "service_counts": dict(Counter(f["service"] for f in findings)),
            }
        result["scans"].append(summary)
    return result


def scan(scanner, repo, root, mode, label, date):
    source = Path(repo)
    # 8.24.3 also loads source/.gitleaksignore regardless of the explicit flag.
    if mode == "git":
        gitdir = command(["git", "rev-parse", "--absolute-git-dir"], root, label + "-gitdir", repo)
        if gitdir is None or gitdir.returncode:
            return {"source": label, "state": "incomplete", "count": 0, "findings": []}
        source = root / (label + "-git-source")
        source.mkdir(mode=0o700)
        raw_write(source, ".git", b"gitdir: " + gitdir.stdout.strip() + b"\n")
    elif (source / ".gitleaksignore").exists() or (source / ".gitleaksignore").is_symlink():
        # Directory callers must provide the collector's opaque, neutral snapshot.
        return {"source": label, "state": "incomplete", "count": 0, "findings": []}
    report = root / (label + ".json")
    report.touch(mode=0o600, exist_ok=False)
    # The incident scan must not inherit repository/cwd fingerprint suppressions.
    ignore = raw_write(root, label + "-gitleaks.ignore", b"")
    args = [
        str(scanner),
        mode,
        str(source),
        "--config",
        str(CONFIG),
        "--redact=100",
        "--exit-code=10",
        "--report-format=json",
        "--report-path=" + str(report),
        "--ignore-gitleaks-allow",
        "--gitleaks-ignore-path=" + str(ignore),
        "--max-target-megabytes=0",
        "--no-banner",
    ]
    if mode == "git":
        args += ["--log-opts=--all --full-history -m"]
    p = command(args, root, label, root)
    try:
        return export_findings(
            json.loads(report.read_text()), None if p is None else p.returncode, label, date
        )
    except (ValueError, CollectionError):
        return {"source": label, "state": "incomplete", "count": 0, "findings": []}


def coverage_entry(source, p, count=None):
    return {
        "source": source,
        "state": "collected" if p is not None and p.returncode == 0 else "incomplete",
        "count": count,
        "owner": "operador",
        "limitation": "revisao_controlada_pendente",
    }


def known_history(repo, root, date):
    p = command(
        ["git", "log", "--all", "--full-history", "--format=%H", "--", *KNOWN],
        root,
        "known-commits",
        repo,
    )
    if p is None or p.returncode:
        return {"state": "incomplete", "keys": []}
    found = Counter()
    versions = []
    variants = []
    seen = set()
    for commit in sorted(set(p.stdout.decode().splitlines())):
        for name in KNOWN:
            data = subprocess.run(
                ["git", "show", commit + ":" + name], cwd=repo, capture_output=True
            )
            if data.returncode:
                continue
            versions.append(
                {"commit": commit, "path": name, "content": data.stdout.decode(errors="replace")}
            )
            for key in KEYS:
                if re.search(rb"(?m)^\s*" + key.encode() + rb"\s*=", data.stdout):
                    found[key] += 1
            for line in data.stdout.decode(errors="replace").splitlines():
                match = re.match(
                    r"\s*(BINANCE_API_KEY|BINANCE_API_SECRET|JWT_SECRET|WORKFLOW_DATABASE_URL)\s*=\s*(.*?)\s*$",
                    line,
                )
                if not match:
                    continue
                key, value = match.groups()
                value = value.strip("\"'")
                if key.endswith("DATABASE_URL"):
                    try:
                        value = urlsplit(value).password or ""
                    except ValueError:
                        value = ""
                if value and (key, value) not in seen:
                    seen.add((key, value))
                    variants.append(
                        {"id": f"VAR-{len(variants)+1:03d}", "service": key, "value": value}
                    )
    raw_write(root, "known-versions.json", json.dumps(versions))
    raw_write(root, "known-variant-map.json", json.dumps(variants))
    return {
        "state": "collected",
        "keys": [
            {
                "id": f"KEY-{i:03d}",
                "service": key,
                "presence": True,
                "versions": count,
                "environment": "indeterminado",
                "date": date,
                "classification": (
                    "configuracao_publica_a_confirmar"
                    if key == "VITE_API_URL"
                    else "possivel_segredo"
                ),
                "result": "pendente",
                "reason": "comparacao_runtime_nao_autorizada",
                "owner": "operador",
            }
            for i, (key, count) in enumerate(sorted(found.items()), 1)
        ],
        "variant_matrix": [
            {
                "id": v["id"],
                "service": v["service"],
                "presence": True,
                "environment": env,
                "date": date,
                "classification": "possivel_segredo",
                "result": "pendente",
                "reason": "comparacao_runtime_e_prova_de_invalidacao_nao_executadas",
                "owner": "Alan_e_operador" if v["service"].startswith("BINANCE") else "operador",
            }
            for v in variants
            for env in ("DEV", "PROD")
        ],
        "limitation": "aliases_renames_valores_distintos_e_runtime_exigem_revisao_controlada",
    }


def api_count(data, key=None):
    """gh --paginate produces adjacent JSON documents; never export their contents."""
    decoder = json.JSONDecoder()
    position = 0
    count = 0
    while position < len(data):
        while position < len(data) and data[position].isspace():
            position += 1
        if position == len(data):
            break
        value, position = decoder.raw_decode(data, position)
        count += len(value[key]) if key else len(value)
    return count


def classify_value(value):
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return "numeric"
    if isinstance(value, bytes):
        return "binary_pending"
    if value == "":
        return "empty"
    text = str(value)
    if re.search(
        r"(?i)(secret|password|senha|api[_ -]?key|token|postgres(?:ql)?://[^\s]+:[^\s]+@)", text
    ):
        return "credential_candidate"
    if re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", text):
        return "personal_candidate"
    try:
        obj = json.loads(text)
    except (ValueError, TypeError):
        return "text_pending"
    # All JSON and arbitrary text require semantic review; no clean claim from heuristics.
    return "json_pending" if isinstance(obj, (dict, list)) else "text_pending"


def inspect_backup(source, root):
    copy = root / "backup.sqlite"
    fd = os.open(copy, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with open(source, "rb") as src, os.fdopen(fd, "wb") as dst:
        shutil.copyfileobj(src, dst)
    os.chmod(copy, 0o400)
    conn = sqlite3.connect(copy.as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        conn.execute("PRAGMA trusted_schema=OFF")
        conn.execute("PRAGMA query_only=ON")
        conn.enable_load_extension(False)
        schema = conn.execute("SELECT name, type, sql FROM sqlite_schema ORDER BY name").fetchall()
        raw_write(root, "backup-schema.json", json.dumps(schema))
        tables = []
        for name, kind, sql in schema:
            if kind != "table":
                continue
            if re.search(r"(?i)^\s*CREATE\s+VIRTUAL", sql or ""):
                tables.append(
                    {
                        "id": f"TABLE-{len(tables)+1:03d}",
                        "state": "incomplete",
                        "reason": "virtual_table_not_executed",
                    }
                )
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            columns = conn.execute("PRAGMA table_xinfo(" + quoted + ")").fetchall()
            counts = [Counter() for _ in columns]
            n = 0
            selection = ",".join('"' + c[1].replace('"', '""') + '"' for c in columns)
            for row in conn.execute("SELECT " + selection + " FROM " + quoted):
                n += 1
                for i, cell in enumerate(row):
                    counts[i][classify_value(cell)] += 1
            tables.append(
                {
                    "id": f"TABLE-{len(tables)+1:03d}",
                    "state": "classified",
                    "rows": n,
                    "columns": [
                        {
                            "id": f"COL-{i+1:03d}",
                            "categories": dict(c),
                            "result": "pendente",
                            "owner": "operador",
                        }
                        for i, c in enumerate(counts)
                    ],
                    "result": "pendente",
                    "reason": "validacao_semantica_retencao_e_remocao_historica",
                }
            )
        return {
            "state": (
                "classified" if all(t["state"] == "classified" for t in tables) else "incomplete"
            ),
            "tables": tables,
            "non_table_objects": sum(s[1] != "table" for s in schema),
            "copy_read_only": True,
            "extensions_disabled": True,
            "result": "pendente",
        }
    finally:
        conn.close()


def inventory(repo, root, scanner, remote=False, backup=None):
    date = datetime.now(timezone.utc).date().isoformat()
    version = command([str(scanner), "version"], root, "scanner-version")
    if version is None or version.returncode or version.stdout.decode().strip() != VERSION:
        raise CollectionError()
    raw_write(root, "scanner-config.toml", CONFIG.read_bytes())
    sources = []
    cmds = [
        ("local_refs", ["git", "for-each-ref", "--format=%(refname) %(objectname)"]),
        ("worktrees", ["git", "worktree", "list", "--porcelain"]),
        ("stash", ["git", "stash", "list"]),
        ("reflogs", ["git", "reflog", "show", "--all"]),
        ("reachable_objects", ["git", "rev-list", "--objects", "--all", "--reflog"]),
        ("tracked_tree", ["git", "ls-files", "-z"]),
        ("metadata", ["git", "log", "--all", "--format=%B"]),
        ("shallow", ["git", "rev-parse", "--is-shallow-repository"]),
    ]
    for label, argv in cmds:
        p = command(argv, root, label, repo)
        count = (
            len(p.stdout.split(b"\0")) - 1
            if label == "tracked_tree" and p
            else (
                p.stdout.count(b"worktree ")
                if label == "worktrees" and p
                else len(p.stdout.splitlines()) if p else None
            )
        )
        sources.append(coverage_entry(label, p, count))
        if label == "shallow" and p and p.stdout.strip() != b"false":
            sources[-1]["state"] = "incomplete"
            sources[-1]["limitation"] = "checkout_shallow_historico_anterior_nao_comprovado"
    if remote:
        operations = [
            (
                "remote_refs",
                ["git", "ls-remote", "origin", "refs/heads/*", "refs/tags/*", "refs/pull/*"],
            ),
            (
                "pull_requests",
                ["gh", "api", "--paginate", "repos/oalansilva/crypto/pulls?state=all&per_page=100"],
            ),
            (
                "releases",
                ["gh", "api", "--paginate", "repos/oalansilva/crypto/releases?per_page=100"],
            ),
            (
                "actions_artifacts",
                [
                    "gh",
                    "api",
                    "--paginate",
                    "repos/oalansilva/crypto/actions/artifacts?per_page=100",
                ],
            ),
            (
                "actions_runs",
                ["gh", "api", "--paginate", "repos/oalansilva/crypto/actions/runs?per_page=100"],
            ),
            (
                "actions_caches",
                ["gh", "api", "--paginate", "repos/oalansilva/crypto/actions/caches?per_page=100"],
            ),
            ("lfs", ["git", "lfs", "ls-files", "--all"]),
        ]
        for label, argv in operations:
            p = command(argv, root, label, repo)
            sources.append(coverage_entry(label, p))
            if p is not None and p.returncode == 0:
                try:
                    key = {
                        "actions_artifacts": "artifacts",
                        "actions_runs": "workflow_runs",
                        "actions_caches": "actions_caches",
                    }.get(label)
                    sources[-1]["count"] = (
                        len(p.stdout.splitlines())
                        if label in ("remote_refs", "lfs")
                        else api_count(p.stdout.decode(), key)
                    )
                except (ValueError, KeyError, TypeError):
                    sources[-1]["state"] = "incomplete"
    for name in (
        "remote_only_refs_content",
        "other_worktrees_content",
        "reflog_only_content",
        "actions_payloads_logs",
        "provider_caches",
        "lfs_payloads",
        "runtime_DEV",
        "runtime_PROD",
        "tag_messages",
        "path_ref_metadata",
        "current_untracked_content",
    ):
        sources.append(
            {
                "source": name,
                "state": "incomplete",
                "count": None,
                "owner": "operador",
                "limitation": "acesso_ou_operacao_separada_necessaria_sem_contorno",
            }
        )
    scans = [scan(scanner, repo, root, "git", "history", date)]
    snapshot = root / "tracked-snapshot"
    snapshot.mkdir(mode=0o700)
    names = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True)
    tree_complete = names.returncode == 0
    for index, name in enumerate(names.stdout.split(b"\0")):
        if not name:
            continue
        relative = Path(os.fsdecode(name))
        src = Path(repo)
        if relative.is_absolute() or ".." in relative.parts or src.is_symlink():
            tree_complete = False
            continue
        for component in relative.parts:
            src /= component
            if src.is_symlink():
                tree_complete = False
                break
        else:
            if src.is_file():
                shutil.copyfile(src, snapshot / f"file-{index:06d}")
                continue
            tree_complete = False
    scans.append(scan(scanner, snapshot, root, "dir", "tracked_content", date))
    if not tree_complete:
        scans[-1]["state"] = "incomplete"
    messages = root / "metadata-snapshot"
    messages.mkdir(mode=0o700)
    shutil.copyfile(root / "metadata.stdout", messages / "messages.txt")
    scans.append(scan(scanner, messages, root, "dir", "messages", date))
    result = {
        "schema": 1,
        "date": date,
        "scanner": {
            "name": "Gitleaks",
            "version": VERSION,
            "configuration": "default_plus_known_keys_v1",
            "baseline": False,
            "fingerprint_suppressions": False,
        },
        "coverage": sources,
        "scans": scans,
        "known_history": known_history(repo, root, date),
        "overall": "incomplete",
        "revocation_proven": False,
    }
    if backup:
        try:
            result["backup"] = inspect_backup(backup, root)
        except (OSError, sqlite3.Error, ValueError):
            result["backup"] = {"state": "incomplete", "result": "pendente", "owner": "operador"}
    raw_write(root, "evidence.json", json.dumps(result, indent=2) + "\n")
    raw_write(root, "publication.json", json.dumps(publication_report(result), indent=2) + "\n")
    return result


def main():
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--restricted-root", required=True, type=Path)
    parser.add_argument("--scanner", required=True, type=Path)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--remote", action="store_true")
    args = parser.parse_args()
    try:
        root = private_root(args.restricted_root, args.repo)
        result = inventory(
            args.repo.resolve(), root, args.scanner.resolve(), args.remote, args.backup
        )
        print(
            json.dumps(
                {
                    "state": result["overall"],
                    "scans": [
                        {"source": s["source"], "state": s["state"], "count": s["count"]}
                        for s in result["scans"]
                    ],
                    "backup_state": result.get("backup", {}).get("state", "not_requested"),
                }
            )
        )
        # Exit zero means collection ran; it never means complete/contained.
        return (
            2
            if any(s["state"] == "incomplete" for s in result["scans"])
            or result.get("backup", {}).get("state") == "incomplete"
            else 0
        )
    except Exception:
        print('{"state":"incomplete","reason":"collection_failed_no_raw_output"}')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
