# Snapshot — Design critic (sem-tela, 1 crítico, NÃO A/B) · card #927 `card-927-caso-a-release-sem-stall`

- Card: #927 — kaizen: Caso A de release fecha sem stall (post main⊆develop, preflight+e2e fail-fast, T16 no git certo)
- Change: `card-927-caso-a-release-sem-stall`
- Critic: 1 isolado (NOT A/B); inherit de modelo; sem transcript do pai; sem nested agent
- Modelo: inherit (mesmo do chat orquestrador)
- UTC: 2026-09-13T01:20:21Z
- Round: crítico 1/1 (teto D4 sem-tela = 1 autor + 1 crítico + 1 rework; segundo rework só com P0 novo de produto)
- Tuple (este isolado): Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não `move_agent_to_root`. Não editar `design.md` / proposal / tasks / specs / HTML / produto.
- Board / issue: REST `GET /repos/oalansilva/crypto/issues/927` (não `gh issue view`). OPEN; labels `priority:P0` `front:operacao` `type:operacao` `kaizen`. Prompt do pai: Status Project 1 = Design. UI impact: none (sem ecrã). Sem Assessment A/B.
- Digest `design.md` **medido**: sha256 `6867aa1b454842ea496741b4588fb78862181da58a2c8a03721711e708f9b4a9` · **1330** palavras (`wc -w`) · 8919 bytes · 88 linhas.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto; pai cola depois).
- UI impact: **none** (processo / `release-guard` / CI / T16; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*927*`; proto dir **ausente**. Justificativa no `design.md` ## Prototype não vazia. Impeccable / Playwright visual / `DESIGN.md` = N/A. Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- Gate tokens parseáveis (linhas próprias no `design.md`):
  - `UI impact: none`
  - `live_route: N/A`
  - `surface: new`
- Clone gate isento via `UI impact: none` + `live_route: N/A` justificado (frase seguinte: processo/release-guard/CI, sem rota autenticada nem landing) + `surface: new` (padrão aceite em #821/#854/#859/#893 — **não** é tela Cripto nova). **Nenhuma** rota de catálogo emprestada (`/monitor` `/favorites` `/combo/*` `landing`).
- Bloco D4 teto: **presente** no `design.md` (texto exacto da skill).
- Method: issue #927 REST (Entra / Não entra / critérios 1–4 / Q1–Q3); proposal / design Decisions 1–7 + Apply contract / Risks / `tasks.md` 1–7; deltas `release-worktree-hygiene` + `release-archive-via-release-branch` + `ci-testing-hardening` + `process-fsm-event`; live `scripts/release-guard` alinhamento antigo; live `.github/workflows/ci.yml` `e2e-playwright` `needs: [qa-policy]` + `if: always()`; live `test_fechar_release_unbound_non_lote_git_rejected` (`q_git=main` → `reason=unbound`); overlay passo 5b «árvores idênticas».

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| Issue #927 body (REST) | lido — Problema / História / Entra / Não entra / Vocabulário / critérios 1–4 / Q1 `fecho-aviso` Q2 `os-dois` Q3 `para-e-diz` |
| `openspec/changes/card-927-caso-a-release-sem-stall/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-927-caso-a-release-sem-stall/specs/{process-fsm-event,ci-testing-hardening,release-archive-via-release-branch,release-worktree-hygiene}/spec.md` | lido |
| Specs vivas `openspec/specs/{release-worktree-hygiene,release-archive-via-release-branch,process-fsm-event,ci-testing-hardening}` | lidas (regressão do predicado antigo) |
| Overlay `docs/crypto-overlay.md` passo canónico 5b (pré-Apply) | lido — ainda «árvores idênticas»; alvo do task 4.1 |
| Live `scripts/release-guard` alinhamento `post` | lido — mesmo commit **ou** develop ancestral de main **e** árvores iguais |
| Live `.github/workflows/ci.yml` job `e2e-playwright` | lido — `needs: [qa-policy]`; `timeout-minutes: 30`; `if: always() && … qa-policy` |
| Live `scripts/process-fsm/test_process_event.py` T16 unbound | lido — `q_git=main` espera `reason=unbound` (pré-Apply) |
| `frontend/src/**`, `backend/` de app, proto HTML 927 | **none** / ausente |
| Catálogo `/monitor` `/favorites` `/combo/*` `landing` | **não emprestado** |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

Este crítico **não** editou `design.md` / proposal / tasks / specs / produto.

---

## Brief (só neste snapshot)

Quem sofre é o operador de release: o lote Caso A sobe a produção com health ok, mas o fecho T16 stall — cards ficam Homologado. Causa composta (grelha aceite, Q1–Q3 fechadas): (1) `post` exige develop=produção ou develop ancestral de main com árvores idênticas, e o Caso A deixa develop à frente com árvore diferente; (2) pacote incompleto (ex. #916 sem o ficheiro do #897) empurra e o e2e ocupa ~30 min sobre build quebrado; (3) fecho no git de produção/`docs-*`/`sync-*` recusa com a palavra seca `unbound`, sem próxima acção.

Direction do autor: inverter o predicado `post` para «`origin/main` ancestral de `origin/develop`» (extra na develop = aviso); overlay 5b = 1 PR merge normal `main → develop` (ensaio #924; recusa #926 e a dança #913+#914+#915); `pre` em `release-*` fail-closed com compile frontend local sem write tracked de `dist`; `e2e-playwright` só arranca se `frontend-build` success; T16 no git errado reject com mensagem de mudar para develop/`release-*` e repetir, sem auto-switch.

Q1 `fecho-aviso`, Q2 `os-dois`, Q3 `para-e-diz` não reabertas. Não entra (fecho #916/#917 neste card, #658, #910, Caso B #617, watcher 35 min, write unbound, proibir Caso A, auto-switch, só um dos dois cortes) permanece Non-Goal.

---

## Critique (rubrica UI none)

### 1. Escopo vs issue DoD (critérios 1–4)

**Critério 1 — fecho PASS neste turno se produção contida na develop + commit por card; extra = aviso; continua a falhar se develop não contém produção; não exige árvores iguais nem develop ancestral de produção.**

Mapeado: Decision 1 + 6; spec `release-worktree-hygiene` MODIFIED (PASS se mesmo commit **ou** `origin/main` ancestral de `origin/develop`; extra = warn; FAIL se main não é ancestral; cenário «árvores iguais sem containment ainda falha»); spec ADDED «commit em produção por card» via `#<id>` alcançável em `origin/main`; tasks 1.1–1.2 e 2.1–2.2. Sequência «neste turno» = 5b (1 PR) depois deploy, depois `post` — Decision 2 e spec `release-archive-via-release-branch` (primeiro `post` falha antes do sync e o runbook manda completar o merge). Cherry-pick Caso A cria SHAs novos em main que **não** são ancestrais de develop até o merge `main → develop`; o pacote trata isso como o 1 PR obrigatório, não como buraco de aceite. MUST NOT fechar #916/#917: spec + task 2.2.

**Critério 2 — 1 PR merge normal produção → develop; recusa substituir develop / merge que descarta o outro lado / restore; #924 sozinho passa; #926 recusado; dança 3 PRs deixa de ser necessária.**

Mapeado: Decision 2; spec `release-archive-via-release-branch` MODIFIED (árvores idênticas MUST NOT; sync MUST ser um PR merge normal; recusa #926 e #913+#914+#915); tasks 4.1–4.2. Overlay live ainda diz «árvores idênticas» — esperado pré-Apply.

**Critério 3 — pacote incompleto para localmente sem abrir o PR; se o build do ecrã falhou o teste longo não arranca.**

Mapeado: Decisions 3+4 (Q2 `os-dois`); spec `release-worktree-hygiene` ADDED preflight; spec `ci-testing-hardening` ADDED `needs` `frontend-build`; tasks 3.1–3.2 e 5.1. Watcher 35 min MUST NOT: task 5.1 + spec. `timeout-minutes: 30` do job permanece.

**Critério 4 — git de produção/`docs-*`/`sync-*`: para e diz a próxima acção; não muda sozinho; recusa não é palavra seca.**

Mapeado: Decision 5; spec `process-fsm-event` MODIFIED + cenários `main` e `docs-*`/`sync-*`; tasks 6.1–6.2. Paging unbound em develop/`release-*` continua a não ser deny (spec viva + task 6.2). Live `test_fechar_release_unbound_non_lote_git_rejected` ainda espera `reason=unbound` em `q_git=main` — drift pré-Apply, não furo de contrato.

Entra do issue está coberto. Não falta aceite de operador no pacote OpenSpec.

### 2. Entra / não entra — não reaberto

**Não entra (não reaberto):**

- Fechar o lote #916/#917 neste card
- Homologado sem comentário (#658)
- Campos Project vazios (#910)
- Caminho Caso B (#617) — o predicado novo aplica-se ao `post` de qualquer closeout, mas o *caminho* Caso B (archive bloqueado pela protecção) não é redesenhado
- Watcher nativo de 35 min do CI
- Write de produto com chat unbound
- Proibir Caso A (Q1 recusou)
- Exigir develop e produção iguais / dança de 3 PRs (Q1 recusou)
- Mudar o git sozinho e continuar o fecho (Q3 recusou)
- Só um dos dois cortes (Q2 pediu os dois)

Q1/Q2/Q3 não reentrevistadas. `## Open Questions` = nenhuma. P3 do autor são detalhe de Apply, não perguntas de operador.

O «Como (Design)» do issue (archive+stub no primeiro PR vs PR documental depois; helper MAY) não vira aceite novo: overlay passo 4 permanece; helper `scripts/release-casoa-closeout.sh` é MAY (Decision 7, task 7.2).

### 3. Superfície visual + tokens parseáveis

- `UI impact: none` em linha própria; justificativa: processo/release-guard/CI, sem HTML.
- `live_route: N/A` em linha própria; frase seguinte declara ausência (nunca emprestar catálogo).
- `surface: new` em linha própria = isenção clone-gate com `live_route: N/A`, **não** tela nova de produto. Parágrafo seguinte: sem rota autenticada nem landing.
- `## Prototype` N/A com justificativa não vazia. `## Impeccable` N/A.
- Apply contract MUST NOT `backend/` `frontend/src/` proto HTML.
- Zero ficheiros `frontend/public/prototypes/*927*`.
- Nenhuma superfície visual nova/alterada sem classificação.

Tokens parseáveis **ok**. Nenhuma rodada extra para o parser.

### 4. Regressão de produto / contrato operacional

- Predicado antigo (`develop` ancestral de `main` + árvores iguais) **deixa de PASS** sem o merge `main → develop`. Intencional Q1; spec nova tem cenário que falha árvores iguais sem containment. Overlay 5b + runbook fecham o caminho.
- Extra Done na develop (#897/#899/#904 no facto do dia) **não** vai para produção pelo 1 PR `main → develop`; o lote continua a sair por Caso A (cherry-picks). Trade-off no design.md está correcto.
- Caso B: depois do merge em main, o `post` novo também exige containment (main ancestral de develop). Não redesenha #617; o mesmo 1 PR 5b serve. Não é alargamento de Não entra.
- T16: unbound em develop/`release-*` com pacote continua permitido (spec viva + cenário delta). Outros eventos unbound intactos.
- CI: `qa-gate` já `needs` `frontend-build` e `e2e-playwright`; o stall de 30 min é o job e2e a arrancar sem esperar o build. Contrato: e2e MUST NOT start se frontend-build ≠ success. `timeout-minutes: 30` e watcher 35 min intocados.
- Guard `post` continua read-only quanto a refs (compile MUST NOT gravar `frontend/dist` tracked; MUST NOT auto-switch git). Alinhado à spec viva de higiene.
- `AGENTS.md` always-on MUST NOT crescer; skill `covenant-flow` só recorte 5b/1 PR se o pin duplicar o passo.

### 5. Riscos operacionais (não bloqueantes)

- [R-ops] `if: always()` actual em `e2e-playwright` faria o job **arrancar mesmo com `needs: frontend-build` a falhar**, se Apply só acrescentar a dependência. O aceite visível («teste longo nem arranca») está no spec; o *como* YAML (`needs` + `if:` a exigir `frontend-build.result == success`, sem destruir o gate `qa-policy` em PR) é detalhe de Apply — já listado pelo autor (Decision 4 P3).
- [R-ops] Compile local como detector de pacote incompleto cobre o incidente #916/#897 (módulo importado em falta). Ficheiro nascido noutro card mas fora do grafo de compile pode passar. Residual aceite: o DoD de operador é o fail-closed visível no compile, não um inventário de todos os paths do outro card.
- [R-ops] Mapa card→commit por `#N` em squash pode falhar se a mensagem omitir o id. Fail-closed; convenção já usada; regex/word-boundary = P3 Apply.
- [R-ops] Merge `main → develop` pode conflitar com extra Done na ponta. Merge normal (não `ours`) é o aceite; o operador resolve no PR. Não é dança de 3 PRs.
- [R-ops] Helper MAY: se overlay + guard cobrirem env do `post` e a recusa de git errado, não criar o script.

### 6. Apply contract executável

Paths fechados: `scripts/release-guard` (`post` containment + warn extra + `#N` por `RELEASE_CARDS`; `pre` compile em `release-*` código); `docs/crypto-overlay.md` passo 5b + runbook Caso A; recorte skill `covenant-flow` só se pin duplicar; `.github/workflows/ci.yml` `e2e-playwright`; `scripts/process-fsm/process_event.py` + testes injectados (`test_process_event.py` / vizinhos). Deltas OpenSpec dos quatro capabilities. MUST NOT produto UI/backend, fechar #916/#917, Caso B playbook, watcher 35 min, auto-switch, dual-write, `CONTEXT.md`/`docs/adr/`, HTML de protótipo, crescer `AGENTS.md`.

Pré-Apply (correcto nesta coluna): predicado antigo ainda no guard; overlay 5b ainda «árvores idênticas»; e2e ainda só `needs: qa-policy`; T16 em `main` ainda `reason=unbound`.

---

## Audit

| Item da rubrica | Resultado |
| --- | --- |
| Escopo vs issue DoD (4 critérios) | PASS — mapeado a Decisions 1–6, specs, tasks |
| Entra / não entra não reaberto | PASS — Non-Goals = Não entra; Q1–Q3 fechadas |
| Regressão de produto | PASS — inversão do predicado é o aceite Q1; Caso B path não reaberto |
| Riscos operacionais nomeados | PASS — `always()` YAML, compile heurístico, `#N` squash, conflitos de merge; mitigados ou P3 Apply |
| Nenhuma superfície visual nova/alterada sem classificação | PASS — UI none; proto ausente; catálogo não emprestado |
| Tokens parseáveis `UI impact` / `live_route` / `surface` | PASS — três linhas próprias; justificativa na frase seguinte; `surface: new` = isenção clone-gate, não ecrã |
| Prototype N/A justificado | PASS — secção `## Prototype` não vazia; sem HTML 927 |
| Bloco D4 exacto | PASS |
| Classificação P0/P1 vs P3 | PASS — zero furo de produto/escopo/contrato visível; YAML/`reason`/regex/compile script = P3 |
| Snapshot não vazio | este ficheiro |

Finding determinístico sem classificação: **nenhum**.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: Expressão `if:` de `e2e-playwright` — o live usa `always()` + `needs: [qa-policy]`; só acrescentar `frontend-build` a `needs` **não** impede o arranque se o build falhar. Disposition: **aceite** (detalhe de Apply; Decision 4 e spec «MUST NOT start» já fecham o contrato visível).
- P3: Script exacto do compile local (`tsc --noEmit` / temp dir; MUST NOT write tracked `frontend/dist`). Disposition: **aceite**.
- P3: Token exacto de `reason` T16 (live `q_git=main` espera `unbound`; aceite = MUST NOT ser só `unbound` + `message` de próxima acção). Disposition: **aceite**.
- P3: Regex/word-boundary `#N` no mapa card→commit em `origin/main`. Disposition: **aceite**.
- P3: Wording exacto do passo 5b no overlay + recorte pin `covenant-flow` se duplicar. Disposition: **aceite**.
- P3: Helper `scripts/release-casoa-closeout.sh` MAY. Disposition: **aceite**.

Dual-write yaml/`AGENTS.md` / reabrir Q1–Q3 / fechar #916/#917 / HTML / superfície visual sem classificar / rota de catálogo / auto-switch: **false**.

---

## Disposition

Zero P0/P1 aberto. Residuais P3 são detalhe de Apply já antecipados pelo autor (YAML `if:`, compile, `reason` T16, regex `#N`, overlay 5b, helper MAY) — aceitos, não reabertos como P0/P1. Tokens parseáveis presentes; Prototype N/A justificado; Entra/não entra do issue não reaberto. Sem rework.

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; processo/release-guard/CI/T16; nenhuma tela CriptoFarol; justificativa não vazia em `## Prototype`.

Tokens: **ok** (`UI impact: none` / `live_route: N/A` / `surface: new` em linha própria). Missing: nenhum.

`design.md` **não** editado por este crítico.

Path: `.impeccable/critique/927-card-927-caso-a-release-sem-stall-2026-09-13T012021Z.md`
