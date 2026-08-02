from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[3]
AGENTS_DIR = ROOT / ".codex" / "agents"
SKILL_DIR = ROOT / ".codex" / "skills" / "stage-model-routing"
INSPECTOR = SKILL_DIR / "scripts" / "inspect-agent-runtime.sh"


def load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def run_inspector(
    sessions_dir: Path,
    thread_id: str,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(INSPECTOR), "--sessions-dir", str(sessions_dir), thread_id],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def rollout_path(sessions_dir: Path, thread_id: str, day: str = "2026/08/02") -> Path:
    target = sessions_dir / day
    target.mkdir(parents=True, exist_ok=True)
    return target / f"rollout-fixture-{thread_id}.jsonl"


def write_rollout(
    sessions_dir: Path,
    thread_id: str,
    *records: dict[str, object],
    day: str = "2026/08/02",
) -> None:
    rollout_path(sessions_dir, thread_id, day).write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def write_raw_rollout(
    sessions_dir: Path,
    thread_id: str,
    content: str,
    day: str = "2026/08/02",
) -> None:
    rollout_path(sessions_dir, thread_id, day).write_text(content, encoding="utf-8")


def session_meta(thread_id: str, agent_type: str = "crypto_luna_reviewer") -> dict[str, object]:
    return {
        "type": "session_meta",
        "payload": {"id": thread_id, "agent_role": agent_type},
    }


def turn_context(
    *,
    model: str = "gpt-5.6-luna",
    effort: str = "max",
    sandbox: str = "read-only",
    permission: str = "disabled",
) -> dict[str, object]:
    return {
        "type": "turn_context",
        "payload": {
            "model": model,
            "effort": effort,
            "sandbox_policy": {"type": sandbox},
            "permission_profile": {"type": permission},
        },
    }


def test_primary_session_is_pinned_to_sol_high() -> None:
    config = load_toml(ROOT / ".codex" / "config.toml")

    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "high"
    assert config["agents"]["max_depth"] == 1  # type: ignore[index]


def test_stage_profiles_have_exact_model_effort_and_sandbox() -> None:
    expected = {
        "crypto-luna-implementer.toml": (
            "crypto_luna_implementer",
            "workspace-write",
            ("Em desenvolvimento", "OpenSpec", "focused verification"),
        ),
        "crypto-luna-reviewer.toml": (
            "crypto_luna_reviewer",
            "read-only",
            ("strictly read-only", "exact diff", "Never review from inherited"),
        ),
        "crypto-luna-release-manager.toml": (
            "crypto_luna_release_manager",
            "danger-full-access",
            ("explicitly", "Homologado", "Do not edit product code"),
        ),
    }

    for filename, (name, sandbox, instruction_fragments) in expected.items():
        profile = load_toml(AGENTS_DIR / filename)
        assert profile["name"] == name
        assert profile["model"] == "gpt-5.6-luna"
        assert profile["model_reasoning_effort"] == "max"
        assert profile["sandbox_mode"] == sandbox
        instructions = str(profile["developer_instructions"])
        for fragment in instruction_fragments:
            assert fragment in instructions


def test_routing_contract_covers_fixed_stages_bootstrap_and_activation() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    agents_md = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    rules = (ROOT / "rules.md").read_text(encoding="utf-8")

    for agent_type in (
        "crypto_luna_implementer",
        "crypto_luna_reviewer",
        "crypto_luna_release_manager",
    ):
        assert agent_type in skill
        assert agent_type in agents_md

    for required in (
        'fork_turns="none"',
        "CARD AND GATE",
        "WORKSPACE",
        "OBJECTIVE",
        "FILES AND OWNERSHIP",
        "INTERFACES",
        "CONSTRAINTS",
        "INPUT EVIDENCE",
        "VERIFICATION",
        "RETURN",
        "Do not fall back",
        "do not use this skill outside Codex",
        "static bootstrap acceptance",
        "independent read-only Codex review",
        "Do not pre-spawn",
        "Do not change AppArmor, sysctl, bubblewrap",
        "After the profiles are versioned and loaded by a new task",
        "Collect runtime evidence only when a post-activation Luna lane is naturally used",
        "omit any required field—agent type, model, effort, sandbox policy type or permission profile type",
        "Only this authorized release lane may run OpenSpec sync/archive",
        "${CODEX_HOME:-$HOME/.codex}/models_cache.json",
        "supported_reasoning_levels",
    ):
        assert required in skill

    assert "não existe fallback" in agents_md
    assert "Exceção de bootstrap do roteamento" in agents_md
    assert "Nenhuma lane é pre-spawned" in agents_md
    assert "sync/archive somente dentro de release explicitamente autorizada" in agents_md
    assert "Não alterar AppArmor, sysctl, bubblewrap" in agents_md
    assert "Nao selecionar por complexidade" in rules
    assert "O bootstrap que instala os perfis e aceito" in rules
    assert "runtime e exigido somente quando a lane Luna for usada naturalmente" in rules
    assert "sync/archive so podem ocorrer dentro de release explicitamente autorizada" in rules
    assert "Nao alterar AppArmor, sysctl, bubblewrap" in rules
    assert "Cursor e outros clientes ficam fora" in rules


def test_runtime_inspector_emits_only_allowlisted_fields(tmp_path: Path) -> None:
    thread_id = "11111111-1111-7111-8111-111111111111"
    write_rollout(
        tmp_path,
        thread_id,
        {"type": "response_item", "payload": {"secret": "DO_NOT_LEAK"}},
        session_meta(thread_id),
        {
            "type": "turn_context",
            "payload": {
                "model": "gpt-5.6-luna",
                "effort": "max",
                "sandbox_policy": {"type": "read-only", "secret": "DO_NOT_LEAK"},
                "permission_profile": {"type": "disabled", "secret": "DO_NOT_LEAK"},
            },
        },
    )

    result = run_inspector(tmp_path, thread_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output == {
        "agent_type": "crypto_luna_reviewer",
        "model": "gpt-5.6-luna",
        "effort": "max",
        "sandbox_policy_type": "read-only",
        "permission_profile_type": "disabled",
    }
    assert set(output) == {
        "agent_type",
        "model",
        "effort",
        "sandbox_policy_type",
        "permission_profile_type",
    }
    assert "DO_NOT_LEAK" not in result.stdout
    assert "DO_NOT_LEAK" not in result.stderr
    assert thread_id not in result.stdout


def test_runtime_inspector_fails_on_missing_metadata(tmp_path: Path) -> None:
    missing_id = "22222222-2222-7222-8222-222222222222"
    write_rollout(
        tmp_path,
        missing_id,
        session_meta(missing_id, "crypto_luna_implementer"),
        {"type": "turn_context", "payload": {"effort": "max"}},
    )
    assert run_inspector(tmp_path, missing_id).returncode != 0


def test_runtime_inspector_fails_on_invalid_json(tmp_path: Path) -> None:
    thread_id = "33333333-3333-7333-8333-333333333333"
    write_raw_rollout(
        tmp_path,
        thread_id,
        json.dumps(session_meta(thread_id)) + "\n{not-valid-json\n",
    )

    result = run_inspector(tmp_path, thread_id)

    assert result.returncode != 0
    assert result.stdout == ""
    assert thread_id not in result.stderr


def test_runtime_inspector_fails_on_multiple_session_metadata(tmp_path: Path) -> None:
    thread_id = "66666666-6666-7666-8666-666666666666"
    write_rollout(
        tmp_path,
        thread_id,
        session_meta(thread_id),
        session_meta(thread_id),
        turn_context(),
    )

    assert run_inspector(tmp_path, thread_id).returncode != 0


def test_runtime_inspector_fails_on_mismatched_thread_identity(tmp_path: Path) -> None:
    thread_id = "77777777-7777-7777-8777-777777777777"
    different_id = "88888888-8888-7888-8888-888888888888"
    write_rollout(tmp_path, thread_id, session_meta(different_id), turn_context())

    assert run_inspector(tmp_path, thread_id).returncode != 0


def test_runtime_inspector_fails_on_conflicting_required_metadata(tmp_path: Path) -> None:
    cases = (
        (
            "99999999-9999-7999-8999-999999999999",
            turn_context(model="gpt-5.6-luna"),
            turn_context(model="gpt-5.6-sol"),
        ),
        (
            "aaaaaaaa-aaaa-7aaa-8aaa-aaaaaaaaaaaa",
            turn_context(effort="max"),
            turn_context(effort="high"),
        ),
        (
            "bbbbbbbb-bbbb-7bbb-8bbb-bbbbbbbbbbbb",
            turn_context(sandbox="read-only"),
            turn_context(sandbox="workspace-write"),
        ),
        (
            "cccccccc-cccc-7ccc-8ccc-cccccccccccc",
            turn_context(permission="disabled"),
            turn_context(permission="untrusted"),
        ),
    )

    for thread_id, first_context, second_context in cases:
        write_rollout(
            tmp_path,
            thread_id,
            session_meta(thread_id),
            first_context,
            second_context,
        )
        assert run_inspector(tmp_path, thread_id).returncode != 0


def test_runtime_inspector_fails_on_zero_or_multiple_matches(tmp_path: Path) -> None:
    zero_id = "dddddddd-dddd-7ddd-8ddd-dddddddddddd"
    assert run_inspector(tmp_path, zero_id).returncode != 0

    duplicate_id = "eeeeeeee-eeee-7eee-8eee-eeeeeeeeeeee"
    record = session_meta(duplicate_id)
    write_rollout(tmp_path, duplicate_id, record, day="2026/08/01")
    write_rollout(tmp_path, duplicate_id, record, day="2026/08/02")
    assert run_inspector(tmp_path, duplicate_id).returncode != 0


def test_runtime_inspector_hides_native_enumeration_errors(tmp_path: Path) -> None:
    thread_id = "ffffffff-ffff-7fff-8fff-ffffffffffff"
    sessions_dir = tmp_path / "private-session-location"
    sessions_dir.mkdir()
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_find = fake_bin / "find"
    fake_find.write_text(
        "#!/bin/sh\nprintf 'native find failure: %s\\n' \"$*\" >&2\nexit 1\n",
        encoding="utf-8",
    )
    fake_find.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = run_inspector(sessions_dir, thread_id, env=env)

    assert result.returncode != 0
    assert result.stdout == ""
    assert str(sessions_dir) not in result.stderr
    assert thread_id not in result.stderr
    assert "could not enumerate rollout filenames" in result.stderr


def test_global_workflow_contract_matches_project_routing_when_available() -> None:
    global_skill = Path(
        os.environ.get(
            "ALAN_WORKFLOW_SKILL_PATH",
            "/srv/knowledge/hermes-second-brain/skills/alan-workflow/SKILL.md",
        )
    )
    if not global_skill.is_file():
        return

    contract = global_skill.read_text(encoding="utf-8")
    for required in (
        "gpt-5.6-sol",
        "high",
        "gpt-5.6-luna",
        "max",
        "independent read-only Codex review",
        "runtime routing evidence only when a configured lane is naturally used",
        "Do not weaken or change AppArmor, sysctl, bubblewrap, sandbox launchers, or other server-security policy",
    ):
        assert required in contract
