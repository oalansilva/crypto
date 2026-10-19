#!/usr/bin/env python3
"""Build only the correction delta from clean v1.1.23 and a tested candidate.

No checkout, account config, manifest or trust is modified. The candidate may
contain test caches/logs: only the tag's tracked paths and NEW_FILES are inputs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

BASE_COMMIT = "c10fb7cf50bb09c87f7da8734f92688df8b1b789"
PRE_PIN = "cfaa6d949614b8d9b43b906e6b758530a5ef1287"
NEW_FILES = ["scripts/process-fsm/test_pin_correction.py"]


def run(*args):
    return subprocess.check_output(args)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def content(path, mode):
    return os.readlink(path).encode() if mode == "120000" else path.read_bytes()


def object_id(kind, data):
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).digest()


def tree_id(entries):
    tree = {}
    for path, (mode, data) in entries.items():
        cursor = tree
        parts = path.split("/")
        for name in parts[:-1]:
            cursor = cursor.setdefault(name, {})
        cursor[parts[-1]] = (mode, object_id("blob", data))

    def encode(directory):
        body = b""
        for name, value in sorted(directory.items(), key=lambda pair: pair[0] + ("/" if isinstance(pair[1], dict) else "")):
            mode, oid = ("40000", encode(value)) if isinstance(value, dict) else value
            body += mode.encode() + b" " + name.encode() + b"\0" + oid
        return object_id("tree", body)

    return encode(tree).hex()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nucleus", type=Path, required=True)
    parser.add_argument("--consumer", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    nucleus, consumer, base, candidate = (path.resolve() for path in (args.nucleus, args.consumer, args.base, args.candidate))
    assert run("git", "-C", str(nucleus), "rev-parse", "v1.1.23^{commit}").decode().strip() == BASE_COMMIT
    expected_tree = run("git", "-C", str(nucleus), "rev-parse", BASE_COMMIT + "^{tree}").decode().strip()
    base_entries, target_entries = {}, {}
    for record in run("git", "-C", str(nucleus), "ls-tree", "-rz", BASE_COMMIT).split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        path = raw_path.decode()
        assert kind == "blob", "submodules are outside this correction"
        original = content(base / path, mode)
        assert object_id("blob", original).hex() == oid, path + ": base differs"
        base_entries[path] = (mode, original)
        target_entries[path] = (mode, content(candidate / path, mode))
    assert tree_id(base_entries) == expected_tree
    for path in NEW_FILES:
        assert path not in base_entries
        target_entries[path] = ("100644", (candidate / path).read_bytes())
    inventory, parts = [], []
    for path, (mode, target) in sorted(target_entries.items()):
        original = base_entries.get(path)
        if original == (mode, target):
            continue
        assert not path.startswith(".covenant-flow/"), "consumer overlay/manifest must not enter nucleus"
        source = str(base / path) if original else "/dev/null"
        destination = str(candidate / path)
        completed = subprocess.run(["git", "diff", "--no-index", "--binary", "--", source, destination], capture_output=True)
        assert completed.returncode == 1, completed.stderr.decode()
        patch = completed.stdout
        # --no-index prefixes absolute paths without the leading slash.
        patch = patch.replace(("a/" + source.lstrip("/")).encode(), ("a/" + path).encode())
        patch = patch.replace(("b/" + destination.lstrip("/")).encode(), ("b/" + path).encode())
        if original is None:
            patch = patch.replace(("a/" + destination.lstrip("/")).encode(), ("a/" + path).encode())
        parts.append(patch)
        previous = subprocess.run(["git", "-C", str(consumer), "show", PRE_PIN + ":" + path], capture_output=True)
        inventory.append({"path": path, "mode": mode,
            "base_sha256": digest(original[1]) if original else None,
            "target_sha256": digest(target), "target_bytes": len(target),
            "provenance": "restored-pre-pin-generic" if previous.returncode == 0 and previous.stdout == target else "reconciled-or-new",
            "pre_pin_sha256": digest(previous.stdout) if previous.returncode == 0 else None})
    args.output.mkdir(parents=True, exist_ok=True)
    patch = b"".join(parts)
    patch_path = args.output / "nucleus.patch"
    patch_path.write_bytes(patch)
    # The scratch tree lives inside a consumer repo. Stop Git discovery so
    # apply cannot silently skip paths based on the consumer's cwd prefix.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_CEILING_DIRECTORIES"] = str(base.parent)
    checked = subprocess.run(["git", "apply", "--check", "--whitespace=error-all", str(patch_path.resolve())], cwd=base, env=env, capture_output=True)
    assert checked.returncode == 0, checked.stderr.decode()
    applied = candidate.parent / "applied-check"
    if applied.exists():
        shutil.rmtree(applied)
    shutil.copytree(base, applied, symlinks=True)
    env["GIT_CEILING_DIRECTORIES"] = str(applied.parent)
    checked = subprocess.run(["git", "apply", str(patch_path.resolve())], cwd=applied, env=env, capture_output=True)
    assert checked.returncode == 0, checked.stderr.decode()
    actual = {path: (mode, content(applied / path, mode)) for path, (mode, _) in target_entries.items()}
    assert actual == target_entries, "applied tree differs from tested candidate"
    manifest = {"schema": "card-1130-pin-correction-v1", "base_tag": "v1.1.23", "base_commit": BASE_COMMIT,
        "base_tree": expected_tree, "consumer_pre_pin": PRE_PIN,
        "target_tree": tree_id(target_entries), "patch_sha256": digest(patch), "patch_bytes": len(patch),
        "changed_files": len(inventory), "git_apply_check": "PASS", "applied_tree_equals_tested_candidate": True, "files": inventory}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: value for key, value in manifest.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()
