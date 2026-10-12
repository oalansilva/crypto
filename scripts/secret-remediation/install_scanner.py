#!/usr/bin/env python3
"""Install only the pinned official scanner, verifying its release checksum."""
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import urllib.request

from inventory import VERSION, SafeArgumentParser, private_root, raw_write


def main():
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--restricted-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        arch = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "x64"}[platform.machine()]
        if platform.system() != "Linux":
            raise RuntimeError()
        root = private_root(args.restricted_root, Path(__file__).resolve().parents[2])
        name = f"gitleaks_{VERSION}_linux_{arch}.tar.gz"
        base = f"https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/"
        data = urllib.request.urlopen(base + name, timeout=60).read()
        sums = urllib.request.urlopen(base + f"gitleaks_{VERSION}_checksums.txt", timeout=60).read()
        expected = next(
            line.split()[0] for line in sums.decode().splitlines() if line.split()[-1] == name
        )
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            binary = archive.extractfile("gitleaks").read()
        executable = raw_write(root, "gitleaks", binary)
        executable.chmod(0o700)
        raw_write(root, "release-checksums.txt", sums)
        print(json.dumps({"scanner": "Gitleaks", "version": VERSION, "checksum_verified": True}))
        return 0
    except Exception:
        print('{"state":"incomplete","reason":"scanner_install_failed_no_raw_output"}')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
