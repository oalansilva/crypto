"""Capture authorized nucleus baseline into this card's inactive candidate.

Reads the named canonical source; writes only below this script's directory.
Does not install, modify an adapter, update trust or touch an operator account.
"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = Path('/srv/apps/dev/covenant-flow-worktrees/card-1098-codex-agentes-nativos')
CONSUMER = HERE.parents[3]
PATHS = [
    'scripts/process-fsm/codex_evidence.py', 'install.sh',
    '.cursor/skills/covenant-flow/SKILL.md',
    'docs/codex-runtime-evidence.md', 'docs/codex-native-capabilities.md',
    'docs/codex-review-qualification.md',
]

if __name__ == '__main__':
    records = []
    for name in PATHS:
        raw = (SOURCE / name).read_bytes()
        dest = HERE / 'nucleus' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            raise SystemExit(f'preserve existing candidate: {dest}')
        dest.write_bytes(raw)
        records.append({'path': name, 'source_sha256': hashlib.sha256(raw).hexdigest(),
                        'consumer_base_sha256': hashlib.sha256((CONSUMER / name).read_bytes()).hexdigest()
                        if (CONSUMER / name).is_file() else None})
    (HERE / 'provenance-base.json').write_text(json.dumps({
        'source_checkout': str(SOURCE), 'source_head': '14aa9d6',
        'source_state': 'dirty #1098; captured bytes, no new revision/tag/pin claimed',
        'consumer_head': '1a06caec', 'pin_base': 'v1.1.22', 'files': records,
    }, indent=2) + '\n')
