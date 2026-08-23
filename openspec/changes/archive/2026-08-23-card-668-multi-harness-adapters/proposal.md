## Why

O processo do [#608](https://github.com/oalansilva/crypto/issues/608) já é uma EFSM portátil (`process-fsm.yaml` + `scripts/process-fsm/`), mas o runtime compilado (Guard, paging Moore, skills, always-on) existe só como pele Cursor. Abrir o mesmo repo no Grok Build hoje é modo cooperativo: o Guard emite `permission` e o Grok honra `decision`; o matcher Cursor não cobre `search_replace`/`write`/`run_terminal_command`; `SessionStart` ignora stdout. Se a lei for copiada para `.grok/`, os harnesses divergem — o mesmo anti-padrão do [#584](https://github.com/oalansilva/crypto/issues/584). Card [#668](https://github.com/oalansilva/crypto/issues/668).

## What Changes

- Declarar três camadas: **núcleo** (yaml + `scripts/process-fsm/` + skills canônicas + `AGENTS.md` curto) e **adapters** Cursor/Grok (tradução de envelope, matcher, JSON, entrega da página Moore).
- `decide()` permanece canônico. O emit passa a ser dual `{permission, decision, agent_message, reason}` para os dois parsers.
- Normalizar payload Cursor (`tool_name`/`tool_input`) e Grok (`toolName`/`toolInput`) antes de classificar write/shell. Matcher Grok cobre as tools reais de write/edit/shell.
- Pele Grok versionada: `.grok/hooks/` chama os **mesmos** scripts; stubs `.grok/skills/<nome>/SKILL.md` (~5 linhas) apontam para `.cursor/skills/<nome>/SKILL.md` (ponte, não cópia da lei).
- Paging Grok: a substância continua só `context_file[q]`; a entrega é arquivo gerado em `.grok/rules/` (stdout de `SessionStart` é ignorado). Cursor continua `sessionStart` → `additional_context`.
- Always-on unificado no stub `AGENTS.md` (já lido pelos dois clientes). `harness.mdc` fica fino: identidade Cursor (hooks + inherit), sem repetir δ.
- Spec `cursor-harness` deixa de declarar Cursor como único harness versionado; passa a ser o adapter Cursor sobre o núcleo.
- Golden de adapter no CI: o mesmo `decide()` produz JSON Cursor e JSON Grok. Ensaio humano lote 1 nos dois clientes: Write de produto com `q_git=develop` → deny. Enquanto o ensaio Grok não passar, o segundo cliente permanece cooperativo, não Auto.
- Sem mudança de código de produto (`backend/` / `frontend/src/`). Fora de escopo: artigo [#614](https://github.com/oalansilva/crypto/issues/614), OpenCode, skills Codex home.

## Capabilities

### New Capabilities

- `process-harness`: contrato multi-cliente — núcleo = verdade do processo; adapter = tradução. SSOT por tipo de regra (coluna/I1–I9 no yaml; runbook nas skills Cursor; always-on no `AGENTS.md`; matcher/JSON nos adapters). Proíbe dual-write de lei em `.cursor/rules` e `.grok/rules`. Stub Grok de skill é ponte, não cópia.

### Modified Capabilities

- `cursor-harness`: Cursor deixa de ser o único harness versionado; always-on δ vive no `AGENTS.md`; `harness.mdc` só identifica o cliente Cursor; skills canônicas continuam em `.cursor/skills/` e são o alvo dos stubs Grok.
- `process-fsm-guard`: envelope Grok entra no mesmo `decide()`; emit dual; matcher/tools Grok de write/shell; Status-edit e sidecar continuam deny nos dois clientes.
- `process-fsm-paging`: Cursor permanece `additional_context`; Grok entrega a mesma página Moore via arquivo gerado em `.grok/rules/` (não stdout de SessionStart).

## Impact

- Altera `scripts/process-fsm/` (normalize + emit; testes golden), `.cursor/hooks.json` / `process-fsm-guard.sh` / `process-fsm-session-start.sh` (pele Cursor mais fina), `AGENTS.md`, `.cursor/rules/harness.mdc`, specs acima.
- Cria `.grok/hooks/`, stubs `.grok/skills/`, e o gerador da página Moore em `.grok/rules/`.
- Não toca `backend/` de produto, `frontend/src/`, `process_event` como via de Status, T0–T17, I1–I9, deploy PROD nem o artigo #614.
- `UI impact: none`. Prototype N/A. Impeccable N/A.
- Origem: issue #668 (kaizen P2). Relacionado: #608, #562, #584 (Cancelado). Homologação: sessão Cursor **e** Grok Build no mesmo worktree, mesmo Write ilegal.
