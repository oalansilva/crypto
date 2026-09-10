## ADDED Requirements

### Requirement: Cursor subagentStop destapes a mute parent after a completed waited child
`.cursor/hooks.json` SHALL register a `subagentStop` command hook invoking `.cursor/hooks/process-fsm-subagent-stop.sh`, which SHALL run `scripts/process-fsm/subagent_stop.py`. The hook MUST NOT set `failClosed` true. Matcher MUST be `generalPurpose|diff-reviewer|code-reviewer` (one entry or equivalent) and MUST include `generalPurpose`, `diff-reviewer`, and `code-reviewer`. `loop_limit` MUST be `32`. The repo MUST NOT register `subagentStart` for destape. Existing `sessionStart`, Guard (`preToolUse` failClosed Write-family, `beforeShellExecution` without failClosed), and Impeccable (`afterFileEdit`, `stop`) entries MUST remain. Grok, OpenCode, and dsh adapters MUST NOT receive this destape hook as a dual-write of T0–T17. Overlay `clients.*.auto` MUST remain `false`. Root `AGENTS.md` MUST NOT grow with this rule. `.cursor/process-fsm.yaml` MUST NOT gain a state, event, or `enabled_tools` entry from this requirement.

The hook SHALL emit JSON `followup_message` only when all of the following hold: stdin `status` is `completed`; `loop_count` is `0`; sidecar `.cursor/tmp/awaiting-task.json` exists and its fingerprint matches this stop's `task`/`description` (parent still waiting for the same Task); the child classifies as one of the four Cursor etapas (grelha / `grill-card`, Apply / `apply-coluna`, `diff-reviewer` / `code-reviewer`, QA / `qa-gate`) **or** a Design child (Design-autor / `design-autor`, Design-crítico sem-tela / `design-critic`, Assessment A/B). Classification MUST use only sidecar `description` ∪ stop `task` (the short title) ∪ `subagent_type`. It MUST NOT classify from the long prompt body (`description`). The classifier MUST NOT treat the bare word `Design` as a match. Design-autor SHALL match before crítico/A/B. Otherwise it SHALL emit `{}`. `error` and `aborted` MUST emit `{}`. A child still running MUST emit `{}`. `explore` and `shell` MUST emit `{}`. `is_parallel_worker: true` (when present) MUST emit `{}`. A crash or invalid JSON MUST fail-open (`{}`), not block the turn.

The `followup_message` SHALL be an order to finish the etapa, never a status question. It MUST NOT contain `concluiu?`, `já acabou?`, or `verifique se nao concluiu`. Exact payloads:
- grelha: `O filho grill já devolveu. Faz o relaying das Qs / handoff T1 agora. Não perguntes se concluiu. Não spawnes outro grill.`
- Apply: `O filho Apply já devolveu. Segue para o review: materializa o diff e spawna diff-reviewer + code-reviewer. Não perguntes se concluiu.`
- review: `O filho reviewer já devolveu. Segue commit / push / PR agora. Não perguntes se concluiu.`
- QA: `O filho QA já devolveu. Fecha o QA conforme o veredito (verde → integrar_develop; falhou → evidência visível). Não perguntes se concluiu.`
- Design-autor: `O filho Design-autor já devolveu. Spawna o crítico (sem-tela) ou a dupla A/B (com-tela). Não perguntes se concluiu. Não spawnes outro autor.`
- Design-crítico / Assessment: `O filho crítico de Design já devolveu. Escreve ## Design Critique, publica o Gist e chama submeter_design. Não perguntes se concluiu.`

`.cursor/skills/covenant-flow/SKILL.md` SHALL tell the Cursor parent, for those four etapas **and** Design-autor / crítico / Assessment A/B, to write the sidecar before the Task and to delete it after handling the result. The hook SHALL delete the sidecar after a poke. Pin overlay `covenant-flow` MUST stay at the existing tag unless a later card bumps it. This destape MUST NOT claim to fire for background children or to cure a host hang. Staff MUST NOT re-prompt while the child is still running.

#### Scenario: Completed grill child destapes with a relay order
- **WHEN** `subagentStop` stdin has `status=completed`, `loop_count=0`, a matching awaiting sidecar, and task/description classifying as grill
- **THEN** stdout JSON includes `followup_message` equal to the grelha order
- **AND** that message does not contain `concluiu?`

#### Scenario: Mute Apply child destapes into Code Review
- **WHEN** the same guards hold and the child classifies as Apply
- **THEN** `followup_message` is the Apply order to materialize the diff and spawn the two local reviewers

#### Scenario: Mute reviewer destapes into commit/push/PR
- **WHEN** the same guards hold and the child classifies as `diff-reviewer` or `code-reviewer`
- **THEN** `followup_message` is the review order to commit / push / PR

#### Scenario: Mute QA child destapes into closeout
- **WHEN** the same guards hold and the child classifies as QA
- **THEN** `followup_message` is the QA order to close according to the child's verdict

#### Scenario: Completed Design-autor destapes into critic or A/B
- **WHEN** the same guards hold and the child classifies as Design-autor
- **THEN** `followup_message` equals `O filho Design-autor já devolveu. Spawna o crítico (sem-tela) ou a dupla A/B (com-tela). Não perguntes se concluiu. Não spawnes outro autor.`
- **AND** that message does not contain `concluiu?`

#### Scenario: Completed Design critic destapes into critique submit
- **WHEN** the same guards hold and the child classifies as Design-crítico sem-tela or Assessment A/B
- **THEN** `followup_message` equals `O filho crítico de Design já devolveu. Escreve ## Design Critique, publica o Gist e chama submeter_design. Não perguntes se concluiu.`
- **AND** that message does not contain `concluiu?`

#### Scenario: Parent already advanced gets no extra poke
- **WHEN** `subagentStop` fires with `status=completed` but `.cursor/tmp/awaiting-task.json` is absent or does not match
- **THEN** stdout is `{}`
- **AND** no `followup_message` is emitted

#### Scenario: Child still running is not destaped
- **WHEN** the child has not reached `subagentStop` with `status=completed`
- **THEN** this hook emits no follow-up
- **AND** it MUST NOT spawn a second child of the same etapa

#### Scenario: Non-completed stop is silent
- **WHEN** stdin `status` is `error` or `aborted`
- **THEN** stdout is `{}`
- **AND** this includes a Design child that aborted (the 27 min critic abort of this session does not destape)

#### Scenario: subagentStart is not registered for destape
- **WHEN** `.cursor/hooks.json` is loaded after this change
- **THEN** it has a `subagentStop` command with `loop_limit` 32 and without `failClosed` true
- **AND** the matcher contains `generalPurpose`, `diff-reviewer`, and `code-reviewer`
- **AND** it has no `subagentStart` destape entry
- **AND** `sessionStart`, Guard, and Impeccable `afterFileEdit`/`stop` remain

#### Scenario: Pasted skill prompt does not reclassify grill
- **WHEN** sidecar is `{"task":"generalPurpose","description":"grill-card 879"}`, stop `task` is `grill-card 879`, `subagent_type` is `generalPurpose`, and stop `description` pastes skill text containing `design-autor` and `diff-reviewer`
- **THEN** `followup_message` is the grelha order
- **AND** it is not the Design-autor order

#### Scenario: Other clients do not receive this destape as law
- **WHEN** a reviewer inspects `.dsh/`, `.grok/`, and overlay `clients.*.auto`
- **THEN** none contains a T0–T17 copy of this destape
- **AND** `clients.*.auto` remains `false`
- **AND** `AGENTS.md` line count does not grow with this rule
