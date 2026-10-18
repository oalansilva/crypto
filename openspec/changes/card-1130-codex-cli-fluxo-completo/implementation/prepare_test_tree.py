"""Build an inactive, disposable test distribution inside the bound worktree.

Uses original nucleus files plus this candidate delta. Never installs into the
active consumer, updates account registration, launches agents or grants trust.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
CONSUMER = HERE.parents[3]
SOURCE = Path('/srv/apps/dev/covenant-flow-worktrees/card-1098-codex-agentes-nativos')
DEST = CONSUMER / '.cursor/tmp/card-1130-candidate-test'


if __name__ == '__main__':
    DEST.mkdir(parents=True, exist_ok=True)
    for name in ('scripts', '.cursor', '.codex', '.grok', '.opencode', '.dsh', '.agents', '.claude', 'nucleus', 'docs'):
        if (SOURCE / name).is_dir():
            shutil.copytree(SOURCE / name, DEST / name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('tmp', '__pycache__', '.pytest_cache', '.git', 'node_modules'))
    for name in ('install.sh', 'AGENTS.md', 'CLAUDE.md', 'rules.md'):
        if (SOURCE / name).is_file():
            shutil.copy2(SOURCE / name, DEST / name)
    shutil.copytree(HERE / 'nucleus', DEST, dirs_exist_ok=True)
    (DEST / 'install.sh').chmod(0o755)
    print(DEST)
