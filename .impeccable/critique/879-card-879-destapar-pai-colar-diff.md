# Snapshot — Design critic (sem-tela, 1 crítico) · card #879 `card-879-destapar-pai-colar-diff`

- Card: #879 — kaizen: destapar o pai (grelha, Apply, review, QA); no review, colar o diff
- Change: `card-879-destapar-pai-colar-diff`
- Critic: 1 isolado (NOT A/B); inherit de modelo; sem transcript do pai; sem nested agent
- Modelo: inherit
- UTC: 2026-09-09T20:58:51Z
- Round: crítico pós-rework 1/1 (teto D4 sem-tela = 1 autor + 1 crítico + 1 rework; segundo rework só com P0 novo de produto)
- Tuple (este isolado): hook `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Board: Status observado **Design** (prompt do pai + comment REST `5608620649`). Issue OPEN `kaizen` + `priority:P1` + `type:operacao`. REST `GET /repos/oalansilva/crypto/issues/879` (não `gh issue view`). `comments: 2` (grill-card fronteira vazia; rework Design no mesmo card).
- Digest `design.md` **medido**: sha256 `07096b7216feed26b61c5f85a0efebdf49e4501cbf2ac13ed27b34ab94b1e231` · **1511** palavras (`str.split` / `wc -w`) · 10914 bytes · 79 linhas.
- `openspec validate card-879-destapar-pai-colar-diff --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto; pai cola depois)
- UI impact: **none** (harness Cursor: destape `subagentStop` + cola do diff de review; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*879*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Justificativa no `design.md` ## Prototype não vazia. Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- Overlay live: `pin: v1.1.14`; `clients.*.auto: false` (cursor/grok/opencode/dsh). `integration_branch: develop`.
- Gate tokens parseáveis (linhas próprias no `design.md`):
  - `UI impact: none`
  - `live_route: N/A harness-only; Cursor session orchestration (destape + review diff paste); no product route`
  - `surface: new`
- Clone gate isento via `UI impact: none` + `live_route: N/A` justificado. **Nenhuma** rota de catálogo emprestada (`/monitor` `/favorites` `/combo/*` `landing`).
- Bloco D4 teto: **presente** no `design.md` (texto exacto da skill).
- Method: issue #879 REST; comments `5604681804` (grill) e `5608620649` (rework 1/1); proposal / design D1–D12 + Apply contract / Risks / `tasks.md` 1–4; deltas `cursor-code-review` + `cursor-harness` + `llm-flow-emission`; live `.cursor/hooks.json` (sem `subagentStop` — pré-Apply); `.cursor/agents/{diff,code}-reviewer.md` (readonly/inherit; **ainda** sem MUST NOT git — drift); `.cursor/hooks/process-fsm-session-start.sh` (padrão locator + venv); `.gitignore` `.cursor/*` sem allowlist de `tmp/`; `AGENTS.md` 20 linhas; overlay pin/auto.

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| Issue #879 body + 2 comments (REST) | lido |
| `openspec/changes/card-879-destapar-pai-colar-diff/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-879-destapar-pai-colar-diff/specs/{cursor-harness,cursor-code-review,llm-flow-emission}/spec.md` | lido |
| `.cursor/hooks.json` live | lido — `sessionStart` / Guard / Impeccable; **sem** `subagentStop` (pré-Apply) |
| `.cursor/hooks/process-fsm-session-start.sh` | lido — locator cwd + venv/`python3` (padrão D6) |
| `.cursor/agents/diff-reviewer.md` + `code-reviewer.md` | lido — `readonly: true` / `model: inherit`; corpo ainda pede intervalo sem recusar git/transcripts (drift S1) |
| `.cursor/skills/covenant-flow/SKILL.md` (coluna Code Review) | lido — «diff **exato**»; ainda não cola path (pré-Apply) |
| `.covenant-flow/overlay.yaml` | lido — pin `v1.1.14`; `clients.*.auto: false`; `integration_branch: develop` |
| `AGENTS.md` | lido — 20 linhas; não deve crescer |
| `.gitignore` `.cursor/*` | lido — `tmp/` fora da allowlist (D2 correcto) |
| `openspec/specs/cursor-code-review/spec.md` viva | lido — spawn já pede diff no prompt; filho ainda deriva git (drift) |
| `frontend/src/**`, `backend/` de app, proto HTML 879 | **none** / ausente |
| Catálogo `/monitor` `/favorites` `/combo/*` `landing` | **não emprestado** |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

Este crítico **não** editou `design.md` / proposal / tasks / specs / produto.

---

## Brief (só neste snapshot)

Quem sofre é o Alan / a sessão Cursor: o pai fica mudo depois do filho já ter acabado, ou o Code Review improvisa sem o intervalo na mão (Ask mode bloqueia git; o filho lista transcripts). Incidente #876 / PR #878: ~49 min. Q1=automático, Q2=falha visível e pára, Q3 revogada (quatro etapas Cursor), destape = ordem — fechadas.

Rework 1/1 (comment `5608620649`, mesmo card): destape S2 também para Design-autor / crítico / Assessment A/B quando `status=completed` e sidecar bate. Incidente desta sessão: autor `4bc9a67b` completed OK; crítico `dfbef63a` 20:18:50–20:44:52 UTC `aborted` pelo `concluiu?` — **não** entra no destape.

Direction: S1 (só Code Review) pai materializa o intervalo em `.cursor/tmp/review-diff.patch` + `review_diff_path:`; filho só `Read`; sem intervalo → `ERROR: review-diff missing` e pára. S2 hook `subagentStop` (nunca `subagentStart`) + sidecar + classificador quatro etapas **e** filhos de Design; poke = ordem exacta; `aborted`/`error`/ainda a trabalhar/`is_parallel_worker` → `{}`.

---

## Rubrica (UI none + D4 teto)

### 1. Escopo vs Entra / não entra do issue #879 + rework 1/1

**Entra — mapeado:**

| Entra | Onde no pacote |
| --- | --- |
| S1 só Code Review: intervalo já materializado; filho sem git/transcripts | D1–D4; proposal What; spec `cursor-code-review` ADDED + MODIFIED; `llm-flow-emission`; tasks 1.1–1.2 |
| Sem intervalo: falha visível e pára | D3 string exacta `ERROR: review-diff missing`; spec Missing review interval; task 1.1 / 3.3 |
| S2 quatro etapas Cursor: filho `completed` + pai mudo → avança a etapa; poke = ordem | D5–D9; spec `cursor-harness` payloads grelha/Apply/review/QA; tasks 2.1–2.4 |
| Rework: Design-autor / crítico / A/B só se `completed` + sidecar | D7–D9; Goals; spec scenarios Design-autor + Design critic; tasks 2.1 / 2.4 / 3.1 |
| `aborted`/`error`/filho a trabalhar → `{}`; `dfbef63a` não destapa | D7; Non-Goals; Risk; spec «Non-completed stop is silent» (inclui aborto 27 min); task 2.1 MUST NOT destapar `aborted` |
| Poke nunca pergunta `concluiu?` / `já acabou?` | D9 textos exactos; spec MUST NOT dessas substrings |
| Grelha/Apply por prevenção | Goals; aceite do body |
| Clique no card continua workaround | D7/Risks; Non-Goals não o removem |
| S2 não substitui S1; S1 não se estende a grelha/Apply/QA | D4 «Grelha, Apply, and QA MUST NOT receive this diff-paste»; Non-Goals |

**Não entra — não reaberto:**

- Produto Descoberta / #876 / cobertura 67%
- T1/T7/T15/T18; aresta nova em `process-fsm.yaml` (poke QA cita `integrar_develop` **existente** em Σ, não inventa)
- QA dsh / `continue` (#858)
- Destapar filho ainda a trabalhar; destapar `error`/`aborted` (incluindo `dfbef63a`)
- Poke perguntar estado; Bugbot; reviewer Write; filhos background; curar hang do host
- Terceira solução; destape só por clique/`proceed`
- Clientes Grok/OpenCode/dsh; dual-write T0–T17; pin novo (`v1.1.14` intacto); crescer `AGENTS.md`; overlay `clients.*.auto`
- Q1/Q2/S1 reabertos

Recorte do rework está no proposal + design + spec + tasks; MUST NOT golden «Design-autor → {}» (task 3.1). Coerente.

### 2. Superfície visual + tokens

- `UI impact: none` com justificativa não vazia (harness-only).
- `live_route: N/A` + harness; **não** é rota de catálogo.
- `surface: new` = isenção do clone-gate (task 4.2), o mesmo padrão aceite em #821/#854/#859 — **não** é tela Cripto nova. Parágrafo abaixo dos tokens declara zero rota/shell/copy/HTML.
- `## Prototype` N/A justificado. Impeccable/Playwright N/A.
- Apply contract MUST NOT `backend/` `frontend/src/` proto HTML `DESIGN.md`.
- Nenhuma superfície visual nova/alterada sem classificação.

### 3. Contrato visível S1 (Code Review)

- Pai gera o intervalo (pré-commit `git diff HEAD` + untracked; fecho `origin/develop...HEAD`). Filho não.
- Ficheiro obrigatório em path gitignored; bytes no prompt opcionais — fecha o *como* da grelha sem furar o aceite «prompt **ou** ficheiro».
- String de erro na mesma classe visível que `ERROR: subagent spawn failed/empty` (spec viva).
- Agentes permanecem `readonly: true` / `model: inherit`. Live ainda **não** recusa git — esperado pré-Apply.
- Matcher continua `generalPurpose` com corpo versionado (não `subagent_type` code-reviewer), alinhado à spec viva.

### 4. Contrato visível S2 (destape)

- Só `subagentStop`; `failClosed` MUST NOT; `loop_limit: 32` justificado (Design+grelha+Apply+2 reviewers+QA no mesmo `#id`).
- Guardas AND: `completed` + `loop_count=0` + sidecar fingerprint + classificador. Palavra nua `Design` não casa. Design-autor antes de crítico/A/B.
- Seis payloads de ordem; zero `concluiu?`. Design-autor → spawn crítico/dupla (não salta a T5). Crítico/A/B → Critique + Gist + `submeter_design` (pai, não o filho).
- Sidecar cooperativo: falha segura se o pai esquecer. Hook apaga após poke.
- Parallel/background → `{}` (não cura o facto staff). Crash fail-open.
- Padrão de script = sessionStart (cwd-independente + venv). Goldens pytest no adapter Cursor.

### 5. Regressão operacional

- Σ / yaml FSM intocados.
- Guard failClosed Write-family + Impeccable `afterFileEdit`/`stop` permanecem (task 2.3 / spec scenario hooks.json).
- Pin `v1.1.14` live = design. Stubs Grok/dsh/OpenCode ponte. `clients.*.auto: false`.
- `AGENTS.md` 20 linhas; Non-Goal não crescer.
- `integrar_develop` no poke QA = evento já legal; closeout verde já exigido ao pai no mesmo turno (spec `cursor-harness` viva). Não é aresta nova.

### 6. Apply contract executável

Paths fechados: `hooks.json`, `process-fsm-subagent-stop.sh`, `subagent_stop.py`, dois `agents/*.md`, `covenant-flow/SKILL.md`, `scripts/process-fsm/test_*.py`. Filho Apply sem `process_event`. Pré-Apply: `subagent_stop.py` ausente; hooks.json sem `subagentStop` — correcto nesta coluna.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: Sequência de **dois** filhos na mesma etapa (pré-commit `diff-reviewer` → `code-reviewer`; Assessment A → B). Um sidecar + poke do primeiro pode ordenar a etapa seguinte cedo demais. Disposition: **accepted-residual** — detalhe Apply. Runbook: sidecar **por** Task; tratar o resultado e regravar o sidecar do seguinte; não tratar o poke do primeiro reviewer como skip do `code-reviewer`; não tratar o poke do primeiro Assessment como `submeter_design` antes de B. A/B em paralelo com `is_parallel_worker: true` → `{}` por D7 (alinhado a «primeiro plano» da grelha); spawn sequencial foreground `generalPurpose` se o destape A/B for o aceite.
- P3: Needles do classificador (`design-autor`, `design-critic`, `grill-card`, `apply-coluna`, `qa-gate`, Assessment A/B) têm de ir na `description` do Task. Disposition: **accepted-residual** — o design já proíbe casar a palavra nua `Design`; Apply trava as strings no skill + goldens.
- P3: Schema JSON do sidecar (campos exactos do fingerprint `task`/`description`) não está no `design.md`. Disposition: **accepted-residual** — D8 + goldens 3.1 fecham no Apply.
- P3: Golden «ainda a trabalhar → `{}`» é ausência de `subagentStop` `completed`, não um stdin a inventar. Disposition: **accepted-residual** — não fingir evento; cobrir `error`/`aborted`/sem sidecar como `{}`.
- Dual-write yaml/`AGENTS.md`/pin/auto / reabrir Q1–Q2 / destapar `dfbef63a` / HTML / superfície visual sem classificar / rota de catálogo: **false**.

## Disposition

Zero P0/P1. Rework 1/1 aplicado: S2 Design-autor/crítico/A/B só com `completed` + sidecar; `aborted`/`error`/filho a trabalhar → `{}`; incidente `dfbef63a` fora; S1 só review; poke = ordem. Tokens parseáveis presentes; Prototype N/A justificado; sem rota de catálogo. Residuais P3 são sequência de sidecar, needles do classificador, schema do JSON e golden de não-evento — resolvidos no Apply, não reabertos como P0/P1.

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; harness Cursor (destape + cola de diff); nenhuma tela CriptoFarol.

Tokens: **ok** (`UI impact` / `live_route` / `surface` em linha própria). Missing: nenhum.

`design.md` **não** editado por este crítico.

Path: `.impeccable/critique/879-card-879-destapar-pai-colar-diff.md`
