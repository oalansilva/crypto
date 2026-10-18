"""Build/check inactive nucleus and consumer patches, without applying them.

Reject a changed baseline. The consumer patch excludes the nucleus installer;
actual distribution still requires a real nucleus revision/tag and pin. Neither
patch nor manifest is installed, and no trust/registration is written.
"""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUTPUT = ROOT / '.cursor/tmp/card-1130-delivery'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def delta(path, before, after, *, exists):
    if before == after:
        return ''
    lines = difflib.unified_diff(before.decode().splitlines(keepends=True), after.decode().splitlines(keepends=True),
                                fromfile='a/' + path if exists else '/dev/null', tofile='b/' + path)
    return 'diff --git a/' + path + ' b/' + path + '\n' + ('new file mode 100644\n' if not exists else '') + ''.join(lines)


if __name__ == '__main__':
    if any(path.is_symlink() for path in (OUTPUT, *OUTPUT.parents)):
        raise SystemExit('unsafe package output directory')
    OUTPUT.mkdir(parents=True, mode=0o700, exist_ok=True)
    provenance = json.loads((HERE / 'provenance-base.json').read_text())
    source = Path(provenance['source_checkout'])
    records = {entry['path']: entry for entry in provenance['files']}
    nucleus_delta, consumer_delta, inventory = [], [], []
    for path in sorted((HERE / 'nucleus').rglob('*')):
        if path.is_symlink():
            raise SystemExit('unsafe candidate symlink: ' + str(path))
        if not path.is_file():
            continue
        name = path.relative_to(HERE / 'nucleus').as_posix()
        after = path.read_bytes()
        before = (source / name).read_bytes() if (source / name).is_file() else b''
        expected = records.get(name, {}).get('source_sha256')
        if (expected is not None and sha(before) != expected) or (expected is None and (source / name).exists()):
            raise SystemExit('source baseline changed; preserve and reconcile: ' + name)
        nucleus_delta.append(delta(name, before, after, exists=(source / name).exists()))
        current = (ROOT / name).read_bytes() if (ROOT / name).is_file() else b''
        expected_consumer = records.get(name, {}).get('consumer_base_sha256')
        if expected_consumer is not None and sha(current) != expected_consumer:
            raise SystemExit('consumer baseline changed; preserve and reconcile: ' + name)
        if expected_consumer is None and name != 'install.sh' and (ROOT / name).exists():
            raise SystemExit('new candidate target already exists; preserve: ' + name)
        if name != 'install.sh':
            consumer_delta.append(delta(name, current, after, exists=(ROOT / name).exists()))
        inventory.append({'path': name, 'candidate_sha256': sha(after), 'bytes': len(after),
                          'source_before_sha256': sha(before) if (source / name).exists() else None,
                          'consumer_before_sha256': sha(current) if (ROOT / name).exists() else None,
                          'consumer_target': name != 'install.sh'})
    patches = {}
    for name, pieces, cwd in (('nucleus.patch', nucleus_delta, source), ('consumer.patch', consumer_delta, ROOT)):
        raw = ''.join(pieces).encode()
        target = OUTPUT / name
        target.write_bytes(raw)
        target.chmod(0o600)
        result = subprocess.run(['git', 'apply', '--check', '--whitespace=error', '-'], input=raw, cwd=cwd,
                                capture_output=True, check=False)
        if result.returncode:
            raise SystemExit(name + ': git apply --check failed: ' + result.stderr.decode())
        patches[name] = {'sha256': sha(raw), 'bytes': len(raw), 'apply_check': 'PASS',
                         'artifact': target.relative_to(ROOT).as_posix()}
    manifest = {'schema': 'card-1130-inactive-delta-v1', 'source': provenance,
                'activation': 'inactive; neither patch applied; adapter/trust/account unchanged',
                'new_revision_tag_pin': None, 'patches': patches, 'files': inventory}
    raw = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    (HERE / 'package.json').write_bytes(raw)
    print(json.dumps({'files': len(inventory), 'package_sha256': sha(raw), 'patches': patches}, sort_keys=True))
