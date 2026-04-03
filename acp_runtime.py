import os
import shutil
from pathlib import Path


def prepare_local_codex_home(base_dir: str | Path) -> str:
    """Create a writable HOME with just enough Codex state for ACP probes."""
    workspace = Path(base_dir).resolve()
    home_dir = workspace / '.codex-home'
    codex_dir = home_dir / '.codex'
    codex_dir.mkdir(parents=True, exist_ok=True)

    source_codex_dir = Path(os.environ.get('ACP_SOURCE_CODEX_DIR', Path.home() / '.codex'))
    for name in ('auth.json', 'config.toml', 'version.json', 'models_cache.json'):
        src = source_codex_dir / name
        dst = codex_dir / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)

    for dirname in ('memories', 'sessions', 'shell_snapshots', 'tmp', 'cache', 'log', 'skills', '.tmp'):
        (codex_dir / dirname).mkdir(parents=True, exist_ok=True)

    return str(home_dir)
