# Snapshot — Design critic (sem-tela, 1 crítico, NÃO A/B) · card #884 `card-884-apply-por-coluna-review-onda`

- Card: #884 — kaizen: um Apply por coluna e review em onda — sem pingue-pongue
- Change: `card-884-apply-por-coluna-review-onda`
- Critic: 1 isolado (NOT A/B); inherit de modelo; sem transcript do pai; sem nested agent
- Modelo: inherit (mesmo do chat orquestrador)
- UTC: 2026-09-10T02:05:33Z
- Round: crítico 1/1 (teto D4 sem-tela = 1 autor + 1 crítico + 1 rework; segundo rework só com P0 novo de produto)
- Tuple (este isolado): Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`. Não `move_agent_to_root`.
- Board / issue: REST `GET /repos/oalansilva/crypto/issues/884` (não `gh issue view`). Issue OPEN; labels `kaizen` + `priority:P1` + `type:operacao`. `comments: 1`. Fronteira vazia no body («Nenhuma decisão de operador em aberto»).
- Digest `design.md` **medido**: sha256 `61ab7414dedb79608560c6d0c1249c9b90cf92b4625dba1257d2edabaea6a40b` · **1223** palavras (`wc -w`) · 8295 bytes · 82 linhas.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto; pai cola depois)
- UI impact: **none** (harness Cursor: orquestração Apply + Code Review; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*884*`; proto dir **ausente**; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Justificativa no `design.md` ## Prototype não vazia. Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- Gate tokens parseáveis (linhas próprias no `design.md`):
  - `UI impact: none`
  - `live_route: N/A harness-only; orquestração do pai Cursor (Apply + Code Review); no product route`
  - `surface: new`
- Clone gate isento via `UI impact: none` + `live_route: N/A` justificado + `surface: new` (padrão #854/#879/#880). **Nenhuma** rota de catálogo emprestada (`/monitor` `/favorites` `/combo/*` `landing`).
- Bloco D4 teto: **presente** no `design.md` (texto exacto da skill).
- Method: issue #884 REST; proposal / design D1–D4 + Apply contract / Risks / `tasks.md` 1–5; deltas `cursor-harness` + `llm-flow-emission` + `cursor-code-review`; live `.cursor/skills/covenant-flow/SKILL.md` (tabela de filhos + Destape S2 linha sequencial); `.cursor/skills/openspec-apply-change/SKILL.md` (Pause entre tasks ainda happy path — pré-Apply); `scripts/process-fsm/subagent_stop.py` `FOLLOWUP_APPLY` / `FOLLOWUP_REVIEW` (wording actual ainda manda review após Apply e commit após *um* reviewer); spec viva `openspec/specs/cursor-code-review` «re-run the affected reviewer» (o delta MODIFIED substitui).

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| Issue #884 body (REST) | lido — Entra / não entra, Q1–Q4 fechadas, aceite 1–8 |
| `openspec/changes/card-884-apply-por-coluna-review-onda/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-884-apply-por-coluna-review-onda/specs/{cursor-harness,llm-flow-emission,cursor-code-review}/spec.md` | lido |
| `.cursor/skills/covenant-flow/SKILL.md` live | lido — tabela já diz 1 Apply + onda; Destape S2 ainda «Após destape de `diff-reviewer`, o pai spawna `code-reviewer`» (alvo D2); sidecar um ficheiro `.cursor/tmp/awaiting-task.json` |
| `.cursor/skills/openspec-apply-change/SKILL.md` live | lido — loop interno já escrito; **Pause if** unclear ainda devolve ao pai (alvo D1) |
| `scripts/process-fsm/subagent_stop.py` `FOLLOWUP_*` | lido — `FOLLOWUP_APPLY` manda review; `FOLLOWUP_REVIEW` manda commit após um reviewer (alvo D4 wording) |
| `openspec/specs/cursor-code-review/spec.md` viva | lido — happy path actual = «primary session SHALL fix … re-run the affected reviewer» (delta MODIFIED) |
| `frontend/src/**`, `backend/` de app, proto HTML 884 | **none** / ausente |
| Catálogo `/monitor` `/favorites` `/combo/*` `landing` | **não emprestado** |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

Este crítico **não** editou `design.md` / proposal / tasks / specs / produto.

---

## Brief (só neste snapshot)

Quem sofre é o Alan / a sessão Cursor: o pai **repete** a barra (Apply → review → Apply → review) em vez de a correr **uma vez por coluna**. Testemunha sessão #879 2026-09-09, pai `25d57e12`: 4 Apply + 5 reviews em série, ~71 min; host não preso em I/O (`durationMs` ~139 s). A lei escrita já descrevia 1 filho Apply e onda; checagens de *texto* teriam passado no dia — o buraco não é lei em falta.

Direction (D1–D4): camada visível sem δ — prompt autocontido + recusa se Apply devolver cedo + tecto 1+1; dois Task no mesmo turno; um ciclo de correção depois bloqueio visível na coluna Code Review; prova = próxima sessão, sem pytest extra. Barra Q4 intocável. Destape máquina (#879), hang (#880), Gmail, aresta FSM e produto fora.

---

## Rubrica (UI none + D4 teto)

### 1. Escopo vs Entra / não entra do issue #884

**Entra — mapeado:**

| Entra | Onde no pacote |
| --- | --- |
| Um filho Apply até tasks feitas ou P0 visível; loop fatiado interno; não um spawn por task | D1; proposal What; spec `cursor-harness` ADDED «One Apply child…»; MODIFIED activity-children; tasks 1.1 / 1.4 / 1.5 |
| Recusa se Apply devolver cedo sem P0: não abre review nem segundo Apply | D1 (b); spec scenario «Early Apply return is a visible block»; `llm-flow-emission` «same class of visible block»; task 1.1 / 2.1 |
| Code Review: dois reviewers no mesmo turno do pai, intervalo já colado; relógio = mais lento; fila do host não falha (Q3) | D2; spec `cursor-harness` «Code Review wave…»; `llm-flow-emission` «two Tasks in one turn»; `cursor-code-review` «Pre-commit reviewers are a same-turn wave»; tasks 1.2 / 1.4 |
| P1/P2 voltam numa lista; no máximo um Apply de correção + uma onda; não spawn por achado; não terceiro ciclo (Q2) | D3; spec «At most one correction Apply then one wave then visible block»; `cursor-code-review` MODIFIED «Principal session…»; tasks 1.3 |
| P3 / detalhe de implementação aceite no Design, resolvido no Apply (teto 1+1+1) | Goals; D4 bloco exacto; Non-Goals; spec `cursor-code-review` «P3 stays classified residual» |
| Fecho pós-commit continua uma onda; não é o pingue-pongue deste card | D3 último parágrafo; spec `cursor-code-review` ADDED; Risk «Fecho vs develop»; task 1.3 |
| Prova de Done = próxima sessão; sem teste automático extra (Q1) | D4; proposal Impact; spec MUST NOT automatic tests as Done; tasks 4.1 / 5 (validate + zero produto, não C1–C8 novos) |
| App/UI não mudam; #879/#880 não reabertos; Gmail/boot fora; barra Q4 intacta | Non-Goals; Apply contract MUST NOT; tasks 2.3 / 5.2 / 5.3 |

**Não entra — não reaberto:**

- Plugin Gmail / MCP no boot
- Custo de cache do host por spawn
- Destape máquina (matcher, sidecar path, `loop_count`, poke ≠ `concluiu?`) — #879; D2/D4 só *wording* da ordem; Rejeitado dois sidecars
- Hang / InstantiationService / Landlock / Desktop+SSH — #880
- Cortar grelha, crítico, intervalo colado, os dois reviewers ou QA (Q4)
- Pytest extra para apanhar o pingue-pongue (Q1)
- Aresta FSM; agente a arrastar T1/T7/T15/T18; `.cursor/process-fsm.yaml`
- Código de produto Cripto; dual-write / pin novo; `AGENTS.md` always-on a crescer
- Terceiro ciclo Apply+review (Q2) = bloqueio visível, não mais trabalho deste card

Q1–Q4 do operador **não** reabertas. *Como* (paths, prompts, wording `FOLLOWUP_*`) fechado no Design. Coerente.

### 2. Superfície visual + tokens (D4 gate)

- `UI impact: none` em linha própria, justificativa não vazia (harness-only).
- `live_route: N/A` + harness Cursor Apply/Code Review; **não** é rota de catálogo.
- `surface: new` = isenção do clone-gate (mesmo padrão #854/#879/#880) — **não** é tela Cripto nova. Parágrafo imediatamente abaixo declara zero rota/HTML/protótipos e «Nunca `/monitor` `/favorites` `/combo/*` `landing`».
- Sem-tela: ausência + justificativa curta **presente**.
- `## Prototype` N/A justificado (orquestração do pai; sem HTML). Impeccable / Playwright / `DESIGN.md` = N/A.
- Apply contract MUST NOT produto / HTML de protótipo / `backend/` / `frontend/src/`.
- Nenhuma superfície visual nova/alterada sem classificação.

### 3. Decisões D1–D4 (stress-test)

**D1 — prompts + recusa + tecto 1+1; Pause deixa de ser happy path.** Honrado. Live `openspec-apply-change` ainda trata Pause/ask-parent entre tasks como happy path — é exactamente o fio 1 do Context; o delta 1.5 fecha-o. P0 visível continua a parar a coluna (não apaga bloqueio real). Recusa é emissão do pai (chat + destape *wording*), não Guard nem aresta — alinhado a Q1 (pytest/Guard rejeitados). Nested spawn Apply→reviewers continua proibido (#729).

**D2 — dois Task na mesma mensagem; sidecar único; apagar a linha sequencial.** Honrado. Live covenant-flow l.195 é o texto a apagar («Após destape de `diff-reviewer`, o pai spawna `code-reviewer`») — é a série da testemunha, residual aceite no #879, agora Entra deste card. Sidecar permanece um ficheiro `#879`; Rejeitado dois sidecars / matcher. Fila do host = aceite Q3. Residual declarado: sidecar único não destapa os dois ao mesmo tempo — não é furo de escopo.

**D3 — 1 correção + onda, resto P1/P2 = bloqueio visível na coluna Code Review; pai não patcha.** Honrado. Specs ADDED + MODIFIED (`Principal session applies reviewer findings` deixa de ser «fix + re-run the affected reviewer»). Sem terceira coluna, sem T18, sem evento novo. Fecho pós-commit fora do tecto de correção pré-commit (Risk explícito).

**D4 — sem pytest extra; só retune de needles se strings se moverem.** Honrado. Tasks 4.1 / 5 não inventam `test_card_884_*`. Wording `FOLLOWUP_APPLY` / `FOLLOWUP_REVIEW` está no contrato; máquina destape intocada. Live actual: `FOLLOWUP_APPLY` já manda review sem ramo «devolver cedo»; `FOLLOWUP_REVIEW` manda commit após *um* reviewer — o Apply troca o texto, não o matcher.

### 4. Contrato visível / risco operacional

- Três camadas (prompt + recusa + tecto) + destape wording: o pai **já** ignorava texto no incidente; Residual explícito; prova = próxima sessão (Q1). Não é P0 — operador fechou a prova.
- `FOLLOWUP_APPLY` estático não inspecciona o payload do filho (máquina #879). D4 mete os dois ramos *no texto* da ordem (done/P0 → onda no mesmo turno; cedo sem P0 → bloqueio, não review). Pai LLM interpreta. Alinhado a «não muda destape máquina».
- Barra Q4: grelha / crítico / intervalo colado / dois reviewers / QA — Non-Goals + task 5.3. Tabela de filhos e S1 cola do diff permanecem.
- Pin / `clients.*.auto` / `AGENTS.md` / yaml FSM: MUST NOT. Sem produto.

### 5. Apply contract executável

Paths fechados: `.cursor/skills/covenant-flow/SKILL.md`, `.cursor/skills/openspec-apply-change/SKILL.md`, `FOLLOWUP_*` em `subagent_stop.py` (só wording), deltas OpenSpec três specs. Needles existentes MAY retune. Filho Apply sem `process_event` / commit / nested reviewers. Pré-Apply: Pause e linha sequencial ainda no disco — correcto nesta coluna.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: Copy exacto de `FOLLOWUP_APPLY` (ramo done/P0 vs devolver cedo) e `FOLLOWUP_REVIEW` (espera o par; lista P1/P2 → um Apply; limpo → commit; nunca nascer o outro reviewer agora). Disposition: **accepted-residual** — detalhe de Apply; D4 já fecha a semântica; needles `test_subagent_stop.py` / `test_card_729_activity_children.py` retunam só se as strings se moverem (não aceite).
- P3: Sidecar único com dois Task no mesmo turno (last-writer; destape do primeiro = espera o par, não commit, não duplica). Disposition: **accepted-residual** — D2 + Risk já declaram; Q3 fila; MUST NOT dois sidecars (#879).
- P3: Templates «Output On Pause» / «Pause on … unclear» em `openspec-apply-change`: o Apply reescreve para Pause ≠ happy path entre tasks, P0 visível ainda pára. Disposition: **accepted-residual** — detalhe de Apply; D1 + task 1.5.
- P3: Classificação de P0 *de reviewer* vs lista P1/P2 (spec: classify blocking; tecto de correção é P1/P2). Disposition: **accepted-residual** — Entra do issue é P1/P2; P0 visível já pára a coluna no Apply; não reabre pingue-pongue.
- Dual-write yaml/`AGENTS.md`/pin/auto / reabrir #879 máquina ou #880 / Gmail / HTML / superfície visual sem classificar / rota de catálogo / pytest extra como Done / terceiro ciclo: **false**.

## Disposition

Zero P0/P1. D1–D4 honram Entra/não entra e Q1–Q4. Tokens parseáveis presentes; Prototype N/A justificado; sem rota de catálogo. Residuais P3 são wording `FOLLOWUP_*`, sidecar na onda, templates Pause, e P0-de-reviewer — resolvidos no Apply, não reabertos como P0/P1.

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; harness Cursor (Apply por coluna + review em onda); nenhuma tela CriptoFarol.

Tokens: **ok** (`UI impact` / `live_route` / `surface` em linha própria). Missing: nenhum. Sem-tela: ausência + justificativa curta presentes. Bloco D4 teto: presente (texto exacto).

`design.md` **não** editado por este crítico.

Path: `.impeccable/critique/884-card-884-apply-por-coluna-review-onda.md`
