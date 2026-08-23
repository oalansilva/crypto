## Context

Card [#668](https://github.com/oalansilva/crypto/issues/668) (kaizen P2), filho de processo do epic [#608](https://github.com/oalansilva/crypto/issues/608) (Pronto). Relacionado: [#562](https://github.com/oalansilva/crypto/issues/562) (cutover Cursor), [#584](https://github.com/oalansilva/crypto/issues/584) (Cancelado: dual-write Codex). Fora: artigo [#614](https://github.com/oalansilva/crypto/issues/614).

A EFSM já é portátil: `.cursor/process-fsm.yaml` + `scripts/process-fsm/` (`decide()`, `page()`, `process_event`). O runtime compilado só existe como pele Cursor (`.cursor/hooks.json`, `harness.mdc`, `.cursor/skills/`). Abrir o repo no Grok Build hoje é cooperativo:

- Guard emite `{"permission":"deny"}`; Grok honra `{"decision":"deny"}` e é fail-open se o JSON não bater.
- Matcher Cursor `Write|StrReplace|Delete|EditNotebook` vs tools Grok (`write`, `search_replace`, `run_terminal_command`).
- Payload `tool_name`/`tool_input` vs `toolName`/`toolInput`.
- `sessionStart` injeta `additional_context`; Grok `SessionStart` ignora stdout.
- Skills canônicas em `.cursor/skills/`; Grok indexa `.grok/skills/` com prioridade maior e, com compat Cursor, também `.cursor/skills/` — um stub de mesmo `name` **substitui** o canônico no dedup.
- `harness.mdc` duplica o always-on que os dois clientes já podem ler via `AGENTS.md`.
- Spec `cursor-harness` declara Cursor como único harness versionado.

**UI impact: none.** Harness/hooks/docs de processo. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Núcleo único. Adapter = tradução. Uma mudança de glob/coluna/texto Moore no yaml altera o comportamento compilado dos dois clientes.
- `decide()` canônico; emit dual `{permission, decision, agent_message, reason}`.
- Envelope Grok entra no mesmo pipeline glob-first / I1 / sidecar / Status-edit.
- Pele Grok versionada (hooks + stubs + paging por arquivo) sem copiar a lei.
- Always-on δ no `AGENTS.md`; `harness.mdc` fino (identidade Cursor).
- Golden de adapter no CI + ensaio humano deny na `develop` nos dois clientes.
- Enquanto o ensaio Grok não PASS, Grok permanece cooperativo, não Auto.

**Non-Goals:**

- Código de produto (`backend/` / `frontend/src/`).
- Mover `process-fsm.yaml` para `process/` (path atual permanece SSOT).
- Mudar T0–T17, I1–I9, `process_event` como via de Status, ou o artigo #614.
- OpenCode, skills Codex home, symlink Hermes.
- Parser de AST / Python ofuscado (residual P2 já aceito no #611).
- Ligar Grok Auto sem ensaio humano.
- Desligar compat Cursor no `~/.grok/config.toml` (não é arquivo do repo).
- Impeccable no Grok (fora de `product_globs` / não é aceite).

## Decisions

1. **Três camadas, yaml fica onde está.**  
   Núcleo = `.cursor/process-fsm.yaml` + `scripts/process-fsm/` + `.cursor/skills/*/SKILL.md` + `AGENTS.md`. Adapter Cursor = `.cursor/hooks.json` + hooks + `harness.mdc` + commands. Adapter Grok = `.grok/hooks/` + stubs + regra Moore gerada. Alternativa: mover yaml para `process/` — toca `YAML_PATH`, docs e specs sem ganho de compilação. Rejeitada neste card.

2. **`normalize()` + `emit()` ao lado de `decide()`, não um segundo Guard.**  
   Alternativa: fork `guard.py` para Grok. Isso reabre dual-write da política. Módulos novos (ou funções no mesmo `guard.py`): `normalize(payload) → canonical {tool, input, command, cwd}` e `emit(permission, message) → dual JSON`. `decide()` passa a devolver o dual emit. Testes golden: o **mesmo** `decide()` com envelope Cursor e envelope Grok.

3. **Família write/shell canônica inclui tools e aliases reais.**  
   Write: `Write`, `StrReplace`, `Delete`, `EditNotebook`, `write`, `search_replace`, `Edit`, `MultiEdit`. Shell: `Shell`, `Bash`, `run_terminal_command`, `run_terminal_cmd`, mais `command` no envelope Cursor `beforeShellExecution`. Path aliases: `path`, `file_path`, `file`, `target_file`, `target_notebook`. `cwd` cai para `workspaceRoot` se ausente. Sem a família Grok, o furo atual é P0: `extract_path` vê `search_replace` ∉ `WRITE_TOOLS` → allow. Matcher Grok PreToolUse MUST repetir esses nomes (alias Claude `Write`/`Edit`/`Bash` disparam o hook; o envelope ainda precisa de `normalize`).

4. **Emit dual em Python e no fallback bash; fallback parseia Grok.**  
   Cursor `failClosed: true` na família Write continua. Grok não tem `failClosed`; crash/malformed = fail-open (limite do produto — aceite residual). O fallback bash MUST (a) imprimir `permission` **e** `decision` deny em path de produto, (b) ler `toolName`/`toolInput` além de `tool_name`/`tool_input`. Envelope Grok + Python down + só chaves Cursor = path vazio = allow — o mesmo furo P0. Golden: Grok `write` + `file_path=backend/...` pelo fallback → dual deny.

5. **Pele Grok chama os mesmos scripts; SessionStart Grok é outro adapter.**  
   `.grok/hooks/*.json` nativo, formato aninhado (`hooks: [{type, command}]`): `PreToolUse` matcher `Write|StrReplace|Delete|EditNotebook|write|search_replace|Edit|MultiEdit` e matcher `Bash|Shell|run_terminal_command|run_terminal_cmd`, `timeout` ≥ 30s. Guard: o mesmo `guard.py`. Paging Cursor permanece `additional_context`. Paging Grok: SessionStart grava `.grok/rules/process-fsm-page.md`. Compat Cursor pode continuar; double-fire é idempotente depois de `normalize`. Sem `normalize`, o hook Cursor-compat no envelope Grok **allow** — por isso a pele nativa não é opcional.

6. **Stubs de skill gerados, não copiados.**  
   `.grok/skills/<name>/SKILL.md` para cada skill de processo em `.cursor/skills/`. Mesmo `name` (Grok dedup: `.grok/` vence). Frontmatter `description` gerada do canônico (descoberta, não lei). Corpo ≤8 linhas: MUST Read o `SKILL.md` canônico e segui-lo. CI: gerador/check falha se stub stale. Alternativa: symlink intra-repo — Grok carregaria o runbook Cursor inteiro sem ponte, mas o card pede stub de ~5 linhas e o spec canônico já proíbe symlink nas skills Cursor. Alternativa: não criar stubs e confiar na compat Cursor — quebra se `compat.cursor.skills=false`. Rejeitada.

7. **Always-on δ sobe para `AGENTS.md`; `harness.mdc` fica identidade Cursor.**  
   Os dois clientes já injetam `AGENTS.md` (Grok também lê `.cursor/rules/` por compat). Orçamento: stub ≤40 linhas com δ, Alan-only T1/T7/T15, `Em Refinamento` como entrada, **Cursor Auto permitido; Grok cooperativo até ensaio PASS**. Header do stub deixa de dizer “não always-on”. `harness.mdc` 4–12 linhas: hooks Cursor, Task inherit, “δ está no AGENTS.md”; MUST NOT repetir T1/T7/T15 nem “Auto permitido” de forma que o Grok herde Auto. Spec `Pronto closeout` é MODIFIED: Alan-only vive no `AGENTS.md`, não no mdc. Pytest `test_harness_mdc_body_budget` / `test_agents_md_is_stub` retarget. Alternativa: copiar mdc para `.grok/rules/` — dual-write. Proibida.

8. **Moore Grok = arquivo gerado gitignored; ingestão é Read obrigatório, não auto-rule.**  
   Grok **pula** ficheiros gitignored na discovery de rules. Por isso `process-fsm-page.md` gitignored **nunca** entra como always-on auto-inject (nem neste turno nem no próximo). Entrega: SessionStart grava o arquivo; `.grok/rules/00-harness.md` committed MUST Read esse path quando existir e tratá-lo como página Moore. Homologação de paging = o agente segue essa instrução, não “o produto injetou a rule”. Guard live-resolve continua; página ausente **não** é allow. Placeholder unbound commitado rejeitado.

9. **Trust de hooks é homologação, não apply.**  
   Hooks de projeto Grok exigem `/hooks-trust` (ou `--trust`). O apply versiona os arquivos; o ensaio humano (D12) inclui trust no folder do worktree. Sem trust, o Guard Grok não roda — o cliente permanece cooperativo (D12).

10. **Spec nova `process-harness`; `cursor-harness` vira adapter.**  
    Não criar `process-harness` **no lugar** de `cursor-harness` (archive perderia história). Delta em `cursor-harness` corrige as frases agora falsas (“único harness”, always-on = mdc+sessionStart, orçamento 8–15 do mdc, e **Pronto closeout** exigindo T1/T7/T15 no mdc). Guard/paging ganham ADDED; o núcleo `process-fsm` (T0–T17) não muda.

11. **Golden no `pytest scripts/process-fsm`, não um segundo job.**  
    Fixtures: envelope Cursor `Write` develop deny; envelope Grok `write`/`search_replace` develop deny; Grok `run_terminal_command` tee deny; Grok OpenSpec Design+card-* allow; dual keys em allow e deny; fallback bash com `decision`; `page()` → arquivo Grok com stub Todo; stub generator stale fails. Sem GitHub nos unitários (igual #611/#613).

12. **Ensaio humano é o gate de Auto, não o gate de merge do adapter.**  
    Apply entrega o adapter compilado + testes golden. Homologação: mesmo worktree, `q_git=develop`, Write/search_replace em `backend/` ou `frontend/src/` → deny nos dois clientes; paging Cursor mostra Moore; Grok mostra a mesma substância no arquivo/regra. Até esse ensaio PASS, texto always-on MUST NOT reivindicar Grok Auto.

## Risks / Trade-offs

- [Grok fail-open se o hook crashar] → residual de produto; fallback bash dual-emite deny de produto; ensaio humano prova o caminho feliz. Não dá para ligar failClosed no Grok.
- [Stub de mesmo nome esconde o skill canônico no dedup] → D6: stub manda Read do canônico; description gerada; CI contra stale.
- [Compat Cursor dispara o hook duas vezes] → `decide()` puro/idempotente; primeiro deny ganha; não desligar compat no home do Alan.
- [Página Moore Grok gitignored não auto-load] → D8: `00-harness.md` MUST Read; Guard live; homologação não reivindica auto-inject.
- [Matcher estreito / `run_terminal_cmd`] → D3/D5 lista canônica + timeout ≥ 30s.
- [Fallback bash só Cursor keys] → D4 parse `toolName`/`toolInput` + golden.
- [Grok herda “Auto permitido” via `.cursor/rules`] → D7: Auto só Cursor; Grok cooperativo até ensaio.
- [Folder untrusted] → Guard Grok não corre; D9 + D12: cooperativo até trust+ensaio.
- [Grok adicionar tool nova de write] → lista canônica versionada; golden quebra se o matcher não cobrir o envelope de teste; tool desconhecida sem path → allow (igual #611 “other”).
- [AGENTS.md passar de 40 linhas] → teste de orçamento no process-fsm ou spec check; bullets curtos.
- [Agente Grok não Read o skill canônico] → stub normativo (“MUST Read”); ensaio de Design/apply em Grok na homologação (D12) observa se o runbook é seguido. P2 se só falhar invocação automática — Alan ainda pode `/alan-workflow`.

## Migration Plan

Aditivo. Ordem de apply: (1) `normalize`/`emit` + testes golden no núcleo; (2) fallback bash dual-emit; (3) `.grok/hooks` + session-start writer + gitignore; (4) gerador de stubs + `00-harness.md`; (5) `AGENTS.md` + `harness.mdc` fino; (6) specs main via apply. Rollback = reverter o diff; Cursor #611/#613 permanece. Sem migration de banco. Sem rebuild de frontend. Homologação = D12 nos dois clientes, não um `./restart`.

## Open Questions

Nenhuma bloqueante. Trust de hooks e Grok Auto ficam no ensaio humano (D9/D12), não no apply.

## UI impact

**none** — harness/hooks/docs. Nenhuma superfície de produto nova ou alterada.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; o aceite visível é deny de ferramenta e página Moore de texto.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit (read-only, duas avaliações em paralelo + recrítica). Fontes: `proposal.md`, `design.md` (D1–D12), `tasks.md`, `specs/process-harness/spec.md`, `specs/cursor-harness/spec.md`, `specs/process-fsm-guard/spec.md`, `specs/process-fsm-paging/spec.md`, `scripts/process-fsm/guard.py`, `.cursor/hooks/process-fsm-guard.sh`, `AGENTS.md`, `harness.mdc`. Card #668, change `card-668-multi-harness-adapters`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

**Assessment A (BLOCKED):** P1 paging gitignored nunca auto-load; P1 Pronto closeout ainda exigia T1/T7/T15 no `harness.mdc`; P1 fallback bash sem `toolName`/`toolInput`; P1 matcher sem aliases `run_terminal_cmd`/`Edit`/`Write`.

**Assessment B (PASS com P1 de apply):** os mesmos furos + pytest `test_harness_mdc_body_budget` 8–15 + leak “Auto permitido” via `.cursor/rules`.

Correções (ainda em Design): D3/D4/D5/D7/D8/D10; MODIFIED Pronto closeout; spec Guard fallback Grok + matcher canônico + timeout ≥ 30s; paging = MUST Read, não auto-inject; tasks 1.3/2.1/2.3/3.1–3.3/4.1–4.5.

**Recrítica 2 (inherit, não editar):** P1 da rodada 1 fechados. P2 aceitos: título OpenSpec `8-15 body lines` vs corpo 4–12; fail-open Grok se hook crashar; agente pode não Read a página gitignored (Guard live); tool de write futura → allow (classe #611 “other”).

- **Escopo:** uma lei, dois adapters; yaml + `decide()` SSOT; sem dual-write T0–T17; sem produto.
- **Processo:** `process_event` intacto; Auto Grok gated no ensaio; Alan-only no `AGENTS.md`.
- **Operação:** normalize+emit dual; stubs MUST Read; trust de hooks = homologação.

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica 2). Prototype N/A. Impeccable N/A.
