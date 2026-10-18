"""Project only this Apply's diagnostic command references; never dump a chat.

Reads authoritative runtime rows and selected original receipts. The private
report contains locations/digests and safe result fields, never prompts/markers.
"""
from pathlib import Path
import json
import os
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / '.cursor/tmp/card-1130-candidate-test/scripts/process-fsm'))
import codex_evidence as ce


if __name__ == '__main__':
    session = os.environ['CODEX_THREAD_ID']
    source, rows, meta, turns = ce.Rollout().session(session)
    projected = []
    for ordinal, row, raw_sha in rows:
        payload = row['payload']
        item = payload.get('item', {})
        argv = item.get('command')
        if row['type'] != 'event_msg' or payload.get('type') != 'item_completed' or item.get('type') != 'CommandExecution':
            continue
        if not isinstance(argv, list) or len(argv) != 3:
            continue
        command = argv[2]
        if not any(needle in command for needle in ('codex_evidence.py preflight --root', 'codex_qualification.py discover --surface',
                                                   'gh api repos/oalansilva/crypto/issues/1117', 'issue(number:1117)')):
            continue
        output = item.get('aggregated_output', '')
        fields = {}
        try:
            result = json.loads(output)
            fields = {key: result[key] for key in ('result', 'code', 'observed', 'host', 'host_version') if key in result}
        except ValueError:
            pass
        projected.append({'ordinal': ordinal, 'raw_sha256': raw_sha, 'command': command,
                          'exit_code': item.get('exit_code'), 'status': item.get('status'),
                          'output_sha256': ce.digest(output.encode()), 'safe_result': fields})
    refs = {
        'R01': '/srv/apps/dev/criptofarol/source/.cursor/tmp/codex-bootstrap-1098/qualification-f6091d4f7a5214ef.json',
        'R02': str(ROOT / '.cursor/tmp/codex-evidence/32f38655-5392-4317-b108-25e62c18c218.evidence.json'),
        'R03': str(ROOT / '.cursor/tmp/codex-evidence/10b7fce8-c54e-4e43-8b1f-f8a8c1f7f2bf.evidence.json'),
        'R04': str(ROOT / '.cursor/tmp/codex-evidence/3783a8df-f5e9-41db-9ae8-5a3d31865c9b.birth.json'),
    }
    report = {'schema': 'card-1130-live-projection-v1', 'session': session,
              'source': str(source), 'surface': meta['originator'], 'version': meta['cli_version'],
              'references': {key: {'path': path, 'sha256': ce.digest(Path(path).read_bytes())} for key, path in refs.items()},
              'R05_native_commands': projected, 'stage_acceptance': False, 'trust_written': False}
    digest = ce.digest(report)
    target = ROOT / '.cursor/tmp' / ('card-1130-live-' + digest[:16] + '.json')
    ce.private_write(target, report)
    print(json.dumps({'private_report': str(target), 'report_sha256': ce.digest(target.read_bytes()),
                      'native_commands': len(projected)}, sort_keys=True))
