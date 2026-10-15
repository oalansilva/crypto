"""Freeze unchanged selection logic from the immutable #1093 baseline."""

import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory")
BASELINE = "99a3070cd9d117539fe6de734361f07d5e1c4611"
source = subprocess.check_output(
    ["git", "show", BASELINE + ":backend/app/services/combo_optimizer.py"],
    cwd=ROOT,
    text=True,
)
method = next(
    node
    for node in ast.walk(ast.parse(source))
    if isinstance(node, ast.FunctionDef) and node.name == "_select_top_candidates"
)
record = {
    "baseline": BASELINE,
    "source": ast.unparse(method),
    "ast_sha256": hashlib.sha256(ast.dump(method).encode()).hexdigest(),
}
target = ROOT / "backend/tests/fixtures/discovery_memory/historical_diversity.json"
target.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"baseline": BASELINE, "ast_sha256": record["ast_sha256"]}), flush=True)
