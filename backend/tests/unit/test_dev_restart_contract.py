from pathlib import Path
import os
import subprocess


def test_canonical_dev_restart_is_scoped_away_from_prod_runtime():
    restart_source = (Path(__file__).resolve().parents[3] / "restart").read_text()
    dev_block = restart_source.split("# BEGIN CANONICAL DEV RESTART", 1)[1].split(
        "# END CANONICAL DEV RESTART", 1
    )[0]

    assert "criptofarol-dev-backend.service" in dev_block
    assert "criptofarol-dev-frontend.service" in dev_block
    assert 'DEV_BACKEND_PORT="8004"' in dev_block
    assert 'DEV_FRONTEND_PORT="5175"' in dev_block
    assert "criptofarol-prod" not in dev_block
    assert 'DEV_BACKEND_PORT="8003"' not in dev_block
    assert 'DEV_FRONTEND_PORT="5173"' not in dev_block


def test_discovery_worker_uses_solo_pool_for_nested_optimizer_workers():
    repo_root = Path(__file__).resolve().parents[3]
    unit_source = (repo_root / "ops/systemd/criptofarol-dev-discovery-worker.service").read_text()

    assert "--pool=solo" in unit_source
    assert "-Q discovery" in unit_source


def test_dev_worktree_restart_fails_closed_before_legacy_runtime(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    simulated_worktree = repo_root / ".restart-contract-test"
    simulated_worktree.mkdir(exist_ok=True)
    restart_copy = simulated_worktree / "restart"
    try:
        restart_source = (repo_root / "restart").read_text()
        restart_copy.write_text(
            restart_source.replace(
                "/srv/apps/dev/criptofarol/*",
                f"{repo_root}/*",
            )
        )
        restart_copy.chmod(0o755)
        result = subprocess.run(
            [str(restart_copy)],
            cwd=simulated_worktree,
            env={**os.environ, "PATH": os.environ.get("PATH", "")},
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    finally:
        restart_copy.unlink(missing_ok=True)
        simulated_worktree.rmdir()

    assert result.returncode == 2
    assert "Refusing restart outside the canonical DEV source." in result.stderr
    assert "Stopping crypto services" not in result.stdout
    assert "Starting crypto" not in result.stdout
