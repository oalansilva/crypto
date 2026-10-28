"""Cadeia de migrações do Alembic com uma única head (sem banco).

PRs paralelos que partem do mesmo pai deixam duas heads, e o ``alembic upgrade head`` do
``./restart`` recusa a cadeia. Este teste lê só os arquivos de ``backend/alembic/versions``.
"""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND = Path(__file__).parents[2]


def _script_directory() -> ScriptDirectory:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return ScriptDirectory.from_config(config)


def test_migration_chain_has_a_single_head():
    heads = _script_directory().get_heads()
    assert len(heads) == 1, f"mais de uma head no Alembic: {sorted(heads)}"


def test_merge_revision_joins_1122_and_1123_heads():
    merge = _script_directory().get_revision("20261028_0002")
    assert set(merge.down_revision) == {"20261027_0001", "20261028_0001"}
