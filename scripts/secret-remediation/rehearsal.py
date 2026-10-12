#!/usr/bin/env python3
"""Rewrite rehearsal creates its own synthetic repos; accepts no real repo/ref."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile

from inventory import SafeArgumentParser


def run(args, cwd, log):
    p = subprocess.run(args, cwd=cwd, capture_output=True)
    with log.open("ab") as f:
        f.write(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError("synthetic_operation_failed")
    return p.stdout


def rehearse(filter_repo, directory):
    os.umask(0o077)
    base = Path(tempfile.mkdtemp(prefix="synthetic-1071-", dir=directory))
    log = base / "operations.log"
    src = base / "source"
    src.mkdir(mode=0o700)
    marker = "synthetic-only-" + secrets.token_hex(12)
    run(["git", "init", "-b", "main"], src, log)
    run(["git", "config", "user.name", "Synthetic Test"], src, log)
    run(["git", "config", "user.email", "synthetic@example.invalid"], src, log)
    (src / ".env.binance").write_text("JWT_SECRET=" + marker)
    (src / ".local_backups").mkdir()
    (src / ".local_backups/fixture.bin").write_bytes(marker.encode())
    (src / "keep.txt").write_text("preserved base\n")
    (src / "embedded.txt").write_text("prefix " + marker + " suffix\n")
    run(["git", "add", "."], src, log)
    run(["git", "commit", "-m", "fixture " + marker], src, log)
    run(["git", "tag", "fixture-tag"], src, log)
    run(["git", "checkout", "-b", "pending-card"], src, log)
    (src / "pending.txt").write_text("preserved committed work\n")
    run(["git", "add", "."], src, log)
    run(["git", "commit", "-m", "pending work"], src, log)
    # Preserve staged, unstaged, untracked and stash state separately from refs.
    (src / "stash.txt").write_text("preserved stash\n")
    run(["git", "add", "stash.txt"], src, log)
    run(["git", "stash", "push", "-m", "fixture-stash"], src, log)
    (src / "keep.txt").write_text("preserved base\nstaged work\n")
    run(["git", "add", "keep.txt"], src, log)
    (src / "keep.txt").write_text("preserved base\nstaged work\nunstaged work\n")
    (src / "untracked.txt").write_text("preserved untracked work\n")
    staged = run(["git", "diff", "--cached", "--binary"], src, log)
    unstaged = run(["git", "diff", "--binary"], src, log)
    (base / "staged.patch").write_bytes(staged)
    (base / "unstaged.patch").write_bytes(unstaged)
    (base / "untracked.txt").write_bytes((src / "untracked.txt").read_bytes())
    bundle = base / "recovery.bundle"
    run(["git", "bundle", "create", str(bundle), "--all"], src, log)
    passfile = base / "encryption-key"
    passfile.write_text(secrets.token_hex(32))
    encrypted = base / "recovery.enc"
    run(
        [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-pbkdf2",
            "-salt",
            "-in",
            str(bundle),
            "-out",
            str(encrypted),
            "-pass",
            "file:" + str(passfile),
        ],
        base,
        log,
    )
    restored_bundle = base / "restored.bundle"
    run(
        [
            "openssl",
            "enc",
            "-d",
            "-aes-256-cbc",
            "-pbkdf2",
            "-in",
            str(encrypted),
            "-out",
            str(restored_bundle),
            "-pass",
            "file:" + str(passfile),
        ],
        base,
        log,
    )
    assert restored_bundle.read_bytes() == bundle.read_bytes()
    run(["git", "bundle", "verify", str(restored_bundle)], src, log)
    restored = base / "restored"
    run(["git", "clone", str(restored_bundle), str(restored)], base, log)
    run(["git", "fetch", str(restored_bundle), "refs/stash:refs/stash"], restored, log)
    run(["git", "apply", "--index", str(base / "staged.patch")], restored, log)
    run(["git", "apply", str(base / "unstaged.patch")], restored, log)
    (restored / "untracked.txt").write_bytes((base / "untracked.txt").read_bytes())
    assert (restored / "keep.txt").read_bytes() == (src / "keep.txt").read_bytes()
    assert run(["git", "rev-parse", "refs/stash"], restored, log) == run(
        ["git", "rev-parse", "refs/stash"], src, log
    )
    clean = base / "rewrite"
    # Frozen synthetic upstream advertises heads/tags only. SDR fetches all refs
    # from origin: do not make local recovery stashes an advertised upstream ref.
    frozen = base / "frozen-upstream"
    run(["git", "clone", "--no-local", "--bare", str(src), str(frozen)], base, log)
    run(["git", "clone", "--no-local", "--mirror", str(frozen), str(clean)], base, log)
    expressions = base / "replacement.txt"
    expressions.write_text("literal:" + marker + "==>REMOVED\n")
    run(
        [
            str(filter_repo),
            "--sensitive-data-removal",
            "--invert-paths",
            "--path",
            ".env.binance",
            "--path",
            ".local_backups/",
            "--replace-text",
            str(expressions),
            "--replace-message",
            str(expressions),
        ],
        clean,
        log,
    )
    run(["git", "fsck", "--full"], clean, log)
    refs = set(
        run(["git", "for-each-ref", "--format=%(refname)"], clean, log).decode().splitlines()
    )
    assert {"refs/heads/main", "refs/heads/pending-card", "refs/tags/fixture-tag"} <= refs
    assert "refs/stash" not in refs
    commits = run(["git", "rev-list", "--all"], clean, log).decode().splitlines()
    for commit in commits:
        names = run(["git", "ls-tree", "-r", "--name-only", commit], clean, log)
        assert b".env.binance" not in names and b".local_backups/" not in names
        assert marker.encode() not in run(["git", "show", "--format=%B", commit], clean, log)
        for name in names.decode().splitlines():
            assert marker.encode() not in run(["git", "show", commit + ":" + name], clean, log)
    assert (
        run(["git", "show", "refs/heads/pending-card:pending.txt"], clean, log)
        == b"preserved committed work\n"
    )
    independent = base / "independent-clean"
    run(["git", "clone", "--no-local", str(clean), str(independent)], base, log)
    run(["git", "fsck", "--full"], independent, log)
    run(["git", "apply", "--index", str(base / "staged.patch")], independent, log)
    run(["git", "apply", str(base / "unstaged.patch")], independent, log)
    (independent / "untracked.txt").write_bytes((base / "untracked.txt").read_bytes())
    stash_patch = run(["git", "diff", "refs/stash^1", "refs/stash"], src, log)
    (base / "stash.patch").write_bytes(stash_patch)
    run(["git", "apply", str(base / "stash.patch")], independent, log)
    assert (independent / "keep.txt").read_bytes() == (src / "keep.txt").read_bytes()
    assert (independent / "stash.txt").read_bytes() == b"preserved stash\n"
    assert (independent / "untracked.txt").read_bytes() == (src / "untracked.txt").read_bytes()
    assert not (independent / ".env.binance").exists()
    assert marker.encode() not in run(["git", "log", "--all", "--format=%B"], independent, log)
    result = {
        "synthetic_only": True,
        "encrypted_recovery_verified": True,
        "staged_unstaged_untracked_restored": True,
        "stash_preserved": True,
        "branches_tags_preserved": True,
        "paths_blobs_messages_removed": True,
        "pending_commit_preserved": True,
        "independent_clean_clone_verified": True,
        "pending_work_reapplied_to_clean_base": True,
        "git_integrity": "PASS",
        "real_refs_modified": False,
    }
    (base / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    p = SafeArgumentParser(description=__doc__)
    p.add_argument("--filter-repo", required=True, type=Path)
    p.add_argument("--restricted-root", required=True, type=Path)
    a = p.parse_args()
    try:
        # Reuse storage validation. Rehearsal refuses existing nonempty roots.
        from inventory import private_root

        root = private_root(a.restricted_root, Path(__file__).resolve().parents[2])
        print(json.dumps(rehearse(a.filter_repo.resolve(), root)))
        return 0
    except Exception:
        print(
            '{"synthetic_only":true,"state":"incomplete","reason":"rehearsal_failed_no_raw_output"}'
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
