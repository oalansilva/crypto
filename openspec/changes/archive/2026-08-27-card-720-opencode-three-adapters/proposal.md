## Why

O núcleo do [#668](https://github.com/oalansilva/crypto/issues/668) já é uma lei com dois adapters (Cursor, Grok Build). Abrir o mesmo repo no OpenCode **1.18.18** hoje não é contrato: o Guard não vê o dialeto nativo `{ tool, args }` (`filePath` / `patchText` / `command`) e um write ilegal em `backend/` com `q_git=develop` passa. Sem detector no Grok/OpenCode, edição de UI nesses clientes não dispara o alarme que o Cursor já tem. Copiar T0–T17 para `.opencode/` reabre o anti-padrão [#584](https://github.com/oalansilva/crypto/issues/584)/#668. Card [#720](https://github.com/oalansilva/crypto/issues/720) (P0).

## What Changes

- Terceiro adapter OpenCode 1.18.18 sobre o mesmo `decide()` / `page()`. Adapter = tradução. Sem dual-write da lei. Sem upgrade de OpenCode neste card.
- `normalize()` / `extract_path()` / goldens aceitam o **dialeto nativo OpenCode** `{ tool, args }` como terceiro dialeto ao lado de Cursor e Grok. Tools canônicas: `write`, `edit`, `apply_patch`, `bash`. Path vazio / `patchText` sem path extraível **não** vira allow.
- Plugin JS em **`.opencode/plugin/`** (singular, convenção [#395](https://github.com/oalansilva/crypto/issues/395)). Auto-load, **sem** `opencode.json`. Serializa o objeto nativo, chama o mesmo `guard.py`/`decide()`, e **throw** no deny.
- Paging OpenCode: `experimental.chat.system.transform` (nome no binário 1.18.18) injeta o mesmo texto que Cursor `additional_context`. Sem arquivo gitignored + hop MUST Read.
- Pele Guard = irmão #668: plugin Guard + paging + stubs + `AGENTS.md` + specs. **Commands `/opsx-*` fora** no OpenCode (modelo usa tool `skill`).
- Stubs ponte (corpo ≤8 linhas, MUST Read do canônico) só para skills que o OpenCode 1.18.18 **não** descobre (descobre `.opencode/skills/`, `.agents/skills/` — **não** `.cursor/skills/`).
- **Detector Impeccable nos três** (mesmo `hook.mjs`; pele só traduz evento; fail-open, não aborta o turno): Cursor já ligado; este card registra Grok `PostToolUse`+`Stop` e OpenCode `tool.execute.after`+`session.idle`.
- Spec `process-harness`: dois → **três** adapters. `cursor-harness` / `developer-tooling`: adapter OpenCode permitido; detector deixa de ser “só Cursor”; lock machine / `opencode.db` / lease / attestation / `opencode.json` como contrato de modelo/MCP/permission **continuam** proibidos.
- `AGENTS.md`: nomear o terceiro cliente; **não** reivindicar Auto OpenCode (nem Auto Grok enquanto #668 4.5 pendente). ≤40 linhas não-vazias.
- Decision log: revoga unicidade [#562](https://github.com/oalansilva/crypto/issues/562); **não** revoga a morte do lock machine. Registra paridade do detector nos três.
- Sem produto. Sem segundo Guard / segundo detector. Sem tabela T0–T17 em `.opencode/`.

## Capabilities

### New Capabilities

- (nenhuma) — a pele OpenCode é o terceiro adapter do núcleo já descrito em `process-harness`; não é um segundo processo.

### Modified Capabilities

- `process-harness`: dois → três adapters; revoga “OpenCode MUST NOT be an active contract”; detector Impeccable nos três clientes; lock machine permanece morto.
- `cursor-harness`: adapter OpenCode permitido ao lado de Cursor e Grok; `AGENTS.md` nomeia os três clientes; sem Auto OpenCode; lock machine / `opencode.json` / lease / attestation continuam proibidos.
- `developer-tooling`: detector deixa de ser só Cursor; pele OpenCode em `.opencode/plugin/` (sem `opencode.json`); Grok `PostToolUse`/`Stop` no mesmo `hook.mjs`.
- `process-fsm-guard`: terceiro dialeto nativo `{ tool, args }` (`filePath` / `patchText` / `command`); plugin throw no deny; `apply_patch` sem path extraível não é allow.
- `process-fsm-paging`: OpenCode injeta a página Moore via `experimental.chat.system.transform` (mesma substância do yaml); Cursor permanece `additional_context`; Grok permanece arquivo gerado + MUST Read.

## Impact

- Altera `scripts/process-fsm/` (`normalize` / `extract_path` / goldens do dialeto OpenCode), `.grok/hooks/` (detector `PostToolUse`+`Stop`), `AGENTS.md`, `docs/decision-log.md`, specs acima.
- Cria `.opencode/plugin/` (Guard + detector) e stubs `.opencode/skills/` para skills que o 1.18.18 não descobre em `.cursor/skills/`.
- Apply (não este turno Design) também ajusta `openspec/config.yaml` (“OpenCode is not an active harness”).
- Não toca `backend/` de produto, `frontend/src/`, yaml T0–T17, `process_event` como via de Status, lock machine, artigo [#614](https://github.com/oalansilva/crypto/issues/614), nem upgrade do binário.
- `UI impact: none`. Prototype N/A. Pipeline Impeccable *desta* coluna Design (shape/protótipo/crítica de tela) = N/A. Detector automático em sessões futuras = entra.
- Origem: issue #720 (kaizen P0). Relacionado: #668, #608, #562, #611. Homologação: ensaio deny OpenCode 1.18.18 + detector nos três clientes no mesmo worktree.
