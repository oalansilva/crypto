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
    fork_turns: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": model,
        "effort": effort,
        "sandbox_policy": {"type": sandbox},
        "permission_profile": {"type": permission},
    }
    if fork_turns is not None:
        payload["fork_turns"] = fork_turns
    return {
        "type": "turn_context",
        "payload": payload,
    }


def test_primary_session_is_pinned_to_sol_high() -> None:
    config = load_toml(ROOT / ".codex" / "config.toml")

    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "high"
    assert config["agents"]["max_depth"] == 1  # type: ignore[index]


def test_stage_profiles_pin_exact_model_effort_and_declared_sandbox_intent() -> None:
    expected = {
        "crypto-luna-implementer.toml": (
            "crypto_luna_implementer",
            "workspace-write",
            (
                "Em desenvolvimento",
                "OpenSpec",
                "focused verification",
                "Behavioral containment",
                "before-state",
                "only assigned paths",
                "out-of-scope mutation",
                'fork_turns="none"',
                "inspect-agent-runtime.sh",
                "must not be cited as fork evidence",
                "operating-system",
            ),
        ),
        "crypto-luna-reviewer.toml": (
            "crypto_luna_reviewer",
            "read-only",
            (
                "strictly read-only",
                "exact diff",
                "Never review from inherited",
                "behavioral contract",
                "before-state",
                "after-state",
                "Any mutation",
                "sandbox-equality gate",
                'fork_turns="none"',
                "mandatory inventory",
                "refs/branches/tags",
                "config and hooks",
                "tracked/untracked and ignored",
                "no mutation observed within the required inventory",
                "not zero global mutation",
                "undeclared exclusion",
                "operating-system isolation",
            ),
        ),
        "crypto-luna-release-manager.toml": (
            "crypto_luna_release_manager",
            "danger-full-access",
            (
                "explicitly",
                "Homologado",
                "Do not edit product code",
                "Behavioral containment",
                "package inventory",
                "out-of-package mutation",
                "residual risk",
                'fork_turns="none"',
                "inspect-agent-runtime.sh",
                "must not be cited as fork evidence",
                "operating-system isolation",
            ),
        ),
    }

    for filename, (name, sandbox, instruction_fragments) in expected.items():
        profile = load_toml(AGENTS_DIR / filename)
        assert profile["name"] == name
        assert profile["model"] == "gpt-5.6-luna"
        assert profile["model_reasoning_effort"] == "max"
        assert profile["sandbox_mode"] == sandbox
        instructions = str(profile["developer_instructions"])
        instructions_contract = " ".join(instructions.split())
        for fragment in instruction_fragments:
            assert fragment in instructions_contract


def test_routing_contract_covers_fixed_stages_bootstrap_and_activation() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    skill_contract = " ".join(skill.split())
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
        "Behavioral containment (option 2)",
        "Before spawn",
        "After return",
        "Any unclassified mutation or action outside the packet blocks the stage",
        '`fork_turns="none"` is separate control-plane evidence',
        "explicit spawn request and the native spawn result",
        "allowlists only five runtime fields",
        "does not inspect or prove `fork_turns`",
        "A new thread id is not proof",
        "Reviewer mandatory inventory",
        "GIT_OPTIONAL_LOCKS=0",
        "git worktree list",
        "refs/branches/tags",
        "repository's config and hooks",
        "tracked/untracked and ignored",
        "no mutation observed within the required inventory",
        "does not mean zero global mutation",
        "Ignored roots explicitly excluded for cost",
        "Any observed difference or undeclared exclusion blocks",
        "sandbox-equality gate",
        "operating-system isolation",
        "Implementer",
        "Reviewer",
        "Release manager",
    ):
        assert required in skill_contract

    assert "não existe fallback" in agents_md.lower()
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
    assert "contenção comportamental" in agents_md
    assert "sandbox efetivo mais amplo que o pedido não bloqueia sozinho" in agents_md
    assert "estado relevante registrado antes do spawn" in agents_md
    assert '`fork_turns="none"` é evidência separada' in agents_md
    assert "inspector local `inspect-agent-runtime.sh` prova somente os cinco campos" in agents_md
    assert "nenhuma mutação observada dentro do inventário obrigatório" in agents_md
    assert "não significa zero mutação global" in agents_md
    assert "sandbox efetivo mais amplo" in rules
    assert "Toda lane Luna usa contenção comportamental" in rules
    assert '`fork_turns="none"` deve ser provado separadamente' in rules
    assert "nenhuma mutação observada dentro do inventário obrigatório" in rules


def test_behavioral_containment_contract_rejects_scope_and_review_mutation() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    skill_contract = " ".join(skill.split())
    implementer = (AGENTS_DIR / "crypto-luna-implementer.toml").read_text(encoding="utf-8")
    reviewer = (AGENTS_DIR / "crypto-luna-reviewer.toml").read_text(encoding="utf-8")
    release_manager = (AGENTS_DIR / "crypto-luna-release-manager.toml").read_text(encoding="utf-8")

    # These assertions are the static contract for the absent runtime
    # orchestrator: a lane is accepted only after independent before/after
    # inspection, and a mutation is a blocker rather than something the lane
    # repairs itself.
    assert "Only assigned paths changed" in skill_contract
    assert "Any out-of-scope mutation" in implementer
    reviewer_contract = " ".join(reviewer.split())
    assert (
        "Any mutation, new artifact or unauthorized external action observed in that inventory rejects"
        in reviewer_contract
    )
    assert "Any code change, unhomologated content" in release_manager
    assert "Any unclassified mutation or action outside the packet blocks" in skill_contract
    assert "the reviewer does not repair it" in skill_contract
    assert "do not repair" in reviewer.lower()
    assert "mandatory inventory" in reviewer_contract
    assert "GIT_OPTIONAL_LOCKS=0" in reviewer_contract
    assert "refs/branches/tags" in reviewer_contract
    assert "repository config and hooks" in reviewer_contract
    assert "tracked/untracked and ignored" in reviewer_contract
    assert "no mutation observed within the required inventory" in reviewer_contract
    assert "not zero global mutation" in reviewer_contract
    assert "Any observed difference or undeclared exclusion" in reviewer_contract
    assert "stop and return the technical work" in " ".join(release_manager.split())


def test_fork_control_is_separate_from_allowlisted_runtime_inspector() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    skill_contract = " ".join(skill.split())
    inspector = (SKILL_DIR / "scripts" / "inspect-agent-runtime.sh").read_text(encoding="utf-8")

    assert '`fork_turns="none"` is separate control-plane evidence' in skill_contract
    assert "explicit spawn request and the native spawn result" in skill_contract
    assert "allowlists only five runtime fields" in skill_contract
    assert "does not inspect or prove `fork_turns`" in skill_contract
    assert "fork_turns" not in inspector


def test_sandbox_broadening_is_risk_evidence_not_an_equality_gate() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    agents_md = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    rules = (ROOT / "rules.md").read_text(encoding="utf-8")
    forbidden_active_gate = (
        "Require observed `read-only` sandbox",
        "observed read-only sandbox",
        "whose observed sandbox is read-only",
    )

    for text in (skill, agents_md, rules):
        for phrase in forbidden_active_gate:
            assert phrase not in text

    assert "a broader value does not block solely" in skill
    assert "sandbox efetivo mais amplo que o pedido não bloqueia sozinho" in agents_md
    assert "sandbox efetivo mais amplo" in rules


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


def test_runtime_inspector_never_claims_fork_turns_evidence(tmp_path: Path) -> None:
    thread_id = "12121212-1212-7121-8121-121212121212"
    write_rollout(
        tmp_path,
        thread_id,
        session_meta(thread_id),
        turn_context(sandbox="danger-full-access", fork_turns="full"),
    )

    result = run_inspector(tmp_path, thread_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert set(output) == {
        "agent_type",
        "model",
        "effort",
        "sandbox_policy_type",
        "permission_profile_type",
    }
    assert "fork_turns" not in output
    assert "fork_turns" not in result.stdout


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
    contract = " ".join(contract.split())
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

    # The global skill is versioned in its own worktree. When the caller points
    # this test at that worktree, require the option-2 language as well; the
    # default installed skill may be the pre-change baseline until integration.
    if "ALAN_WORKFLOW_SKILL_PATH" in os.environ:
        for required in (
            "behavioral read-only contract",
            "broader effective sandbox",
            "Behavioral containment is the standard option 2",
            "before spawn",
            "after return",
            "out-of-scope mutation",
            "not operating-system isolation",
            "local inspector allowlists only those five runtime fields",
            "explicit spawn request/result",
            "GIT_OPTIONAL_LOCKS=0",
            "git worktree list",
            "refs/branches/tags",
            "repository config/hooks",
            "tracked/untracked and ignored",
            "no mutation observed within the required inventory",
            "not zero global mutation",
            "undeclared exclusion blocks",
        ):
            assert required in contract
