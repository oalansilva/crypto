# Kaizen Log — Melhoria Contínua de Processo

> **Princípio:** quanto mais o processo é usado, melhor ele fica. Cada execução gera
> evidência; o Kaizen audita; correções aprovadas viram regras/skills/scripts; o próximo
> ciclo valida se a fricção foi eliminada (métricas de recorrência caem).
>
> **Regra de recorrência:** um mesmo padrão de fricção registrado em 2+ auditorias
> tem sua severidade elevada em um nível e vira candidato a promoção de regra
> (`AGENTS.md`/`rules.md`) ou skill. Proposta de exceção ao limite de 3 cards/release
> para padrões recorrentes: pendente de aprovação de Alan (Kaizen propõe, Alan aprova).
>
> **Segurança:** trechos de sessões (máx. 2-3 linhas) são permitidos SOMENTE neste
> arquivo local. Issues públicas levam métricas agregadas e IDs.
>
> **Materialização (#661):** cada entrada `## YYYY-MM-DD — Kaizen release` exige tabela
> `### Cards kaizen criados…` com 1–3 `#N` novos, ou `(não criado) … coberto por #N`
> (cobertura em fluxo), ou o marcador `Sem achados acionáveis` sem linhas de dados.
> O `release-guard post` bloqueia sem essa evidência.

---


## 2026-08-27 — Kaizen release

- **Release/card**: 2026-08-27 — Homologado → Pronto após deploy PROD `255b8652` (pacote `#747`).
- **Fontes consultadas**: board Project 1 (item Homologado `#747`), git/worktrees + `release-guard pre` PASS, CI PRs #748/#750/#751, OpenSpec archive, transcript Cursor desta sessão (homologação Telegram + wipe `.env` PROD). Sem `opencode.db`.
- **Sessões analisadas**: Apply/QA/T14 `#747`; homologação DEV (vínculo + DM teste); pedido explícito de release + copiar secrets Telegram para PROD.
- **Custo/eficácia**: 1 Homologado; comentário Homologado postado no closeout (bloqueio inicial do `pre`); outage PROD ~minutos por overwrite de `.env`.

### Métricas
- **Board**: 1 Homologado (`#747`). Fora: `#749` P0 Em Refinamento (UI reload); kaizen `#658`/`#659`/`#660`; worktrees in-flight `#472`/`#600`/`#604`/`#606`/`#614`/`#728`.
- **Git**: `origin/main` `255b8652` (PR #750); archive via `release-2026-08-27` `6d11c7a8`; sync PR #751 `56f957d4`. Stash 0.
- **CI**: PR #748 `qa-gate` pass na `develop`. PR #750 checks verdes; `qa-gate` skip (base `main`).
- **OpenSpec**: 1 change arquivada com sync (`monitor-telegram-alerts`, `user-telegram-alerts`); `validate --all` 158/158.
- **PROD**: source `255b8652`; health 200 `ok` após restore do `.env`; webhook 403 sem secret.

### Achados
- F-1 [major] Overwrite do `.env` PROD (`grep` Permission denied + `mv` de tmp só com Telegram) derrubou o backend (`DATABASE_URL` / depois `JWT_SECRET`). Restore de bak 09/08 + JWT do DEV. Esforço S | P0 | Card novo: #752.
- F-2 [minor] Comentário Homologado canônico ausente até o `pre` do lote. Recidiva #658. Esforço S | P1 | coberto por #658.
- F-3 [minor] Um bot Telegram = um webhook: apontar para PROD tira o DEV do `setWebhook`. Sem card novo (doc operacional).
- F-4 [info] Guard `fail_closed` em `q_git=develop`/`main` unbound bloqueou escrita do `.env` pelo Agent; operador colou no shell. Alinhado ao harness.
- F-5 [info] JWT_SECRET de PROD restaurado a partir do DEV (bak 09/08 não tinha). Dívida: rotacionar JWT PROD. Sem card extra neste lote (cap 3; F-1 priorizado).

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | #658
- Secrets/env operacionais sem helper fail-closed | **novo** | #752

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #752 — bootstrap `.env` append-only | P0 | F-1 | Em Refinamento |

---
## 2026-08-26 — Kaizen release

- **Release/card**: 2026-08-26 — Homologado → Pronto após deploy PROD `ef053514` (pacote `#686` + `#687`).
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees + `release-guard audit`, CI PRs #735/#737/#738/#739, OpenSpec validate, transcript Cursor do Apply #687 + closeout. Sem `opencode.db`.
- **Sessões analisadas**: Design→Apply→Done `#687` (T6 sem rotação); closeout no mesmo chat com overlay T16; `#686` já Homologado no pacote.
- **Custo/eficácia**: 2 Homologados; comentários Homologado canônicos só no closeout (bloqueio do `pre`); PROD `BINANCE_*` já no `.env` raiz (sem rotação).

### Métricas
- **Board**: 2 Homologado (`#686` `#687`, Codex/P0). Fora: kaizen `#658`/`#659`/`#660` Em Refinamento; Aprovação de Design `#600`/`#614`/`#728`; worktrees in-flight `#472`/`#600`/`#604`/`#606`/`#614`/`#686`/`#687`/`#728`.
- **Git**: `origin/main` `ef053514` (PR #738); archive via `release-2026-08-26` `95be91bd`; sync PR #739. Stash 0. Tip `main` limpo de `.env.binance`.
- **CI**: PRs #735/#737 `qa-gate` pass na `develop`. PR #738 checks verdes; `qa-gate`/`deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 2 changes arquivadas com sync de specs (`log-viewer`/`logging`, `env-binance-git-hygiene`); sem `--skip-specs` neste lote.
- **PROD**: source `ef053514`; health 200 `ok`; `BINANCE_API_KEY`/`BINANCE_API_SECRET` presentes no `.env` raiz (sem rotação, T6).

### Achados
- F-1 [major] Comentários Homologado canônicos ausentes em `#686`/`#687` até o closeout (`release-guard pre` bloqueou; helper postado no mesmo turno do release). Recidiva #658. Esforço S | P1 | Card existente: #658.
- F-2 [info] `openspec archive -y` sincronizou main specs sem `--skip-specs` (#659 não recidivou neste lote).
- F-3 [minor] Sync `main→develop` (#739) pode deixar change ativa ao lado do archive no worktree até limpeza. WARN #428. Sem card novo.
- F-4 [minor] Título board `#687` ainda “rotacionar as chaves” vs issue “sem rotação” pós-T6. Sem card novo.
- F-5 [info] Pedido `suba a releas` em sessão do card `#687` unbound na página; overlay T16 carregado. Alinhado ao #613.
- F-6 [info] Guard `fail_closed` em `q_git=release-*` unbound atrapalhou o 1º commit do archive; contornado com `git add -A`. Sem card novo.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 10+ auditorias | #658
- Archive `--skip-specs` | **não** neste lote | #659

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #658 |

---
## 2026-08-25 — Kaizen release (lote 729)

- **Release/card**: 2026-08-25 (3º pacote do dia) — Homologado → Pronto após deploy PROD `2b7e1768` via closeout T16.
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees, CI PR #730 (`qa-gate` pass) e PR #731, overlay/runbook, transcript Grok Build desta sessão Apply/QA/T14/release. Sem `opencode.db`.
- **Sessões analisadas**: `#729` Design→Apply→QA→Done; pedido `suba a release` com card já Homologado no board.
- **Custo/eficácia**: um Homologado; comentário Homologado postado no mesmo turno do closeout (arraste de Alan foi antes do helper).

### Métricas
- **Board**: 1 Homologado (`#729`). Fora: kaizen `#658`/`#659`/`#660` Em Refinamento; worktrees in-flight `#600`/`#614`/`#604`/`#728`/`#472`/`#606`.
- **Git**: `origin/develop` HEAD `f55c3b57` (PR #730). Archive via `release-2026-08-25-729`. Stash 0.
- **CI**: PR #730 `qa-gate` pass na `develop`. PR #731 merge `2b7e1768`.
- **OpenSpec**: 1 change arquivada; main specs `llm-flow-emission` / `cursor-harness` / `grill-card` + `--skip-specs` (#659).
- **PROD**: source `2b7e1768`; alembic já head; bundle `index-Dtfnr-Df.js` / `index-DzSLxG6d.css`; health 200 após warmup.

### Achados
- F-1 [major] Comentário Homologado canônico ausente até o closeout (arraste no board sem helper no mesmo turno do T15). Recidiva #658. Esforço S | P1 | Card existente: #658.
- F-2 [minor] Archive `--skip-specs` após sync do main spec. Recidiva #659. Esforço S | P1 | Card existente: #659.
- F-3 [info] Terceiro pacote no mesmo dia; mesma doc canônica `docs/release-2026-08-25.md`.
- F-4 [info] Pedido `suba a release` com sessão Grok unbound na página; overlay T16 carregado. Alinhado ao #613.
- F-5 [info] Closing review achou P1 (filho autor ainda podia T5); corrigido em `9d1c494f` antes do QA.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | #658
- Archive `--skip-specs` | #659

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #658 |
| (não criado) archive --skip-specs headers | — | F-2 | coberto por #659 |

## 2026-08-25 — Kaizen release (lote 685)

- **Release/card**: 2026-08-25 (2º pacote do dia) — Homologado → Pronto após deploy PROD `3482c763` via closeout T16.
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees, CI PR #725 (`qa-gate` pass), overlay/runbook, transcript Cursor desta sessão Apply/QA/T14. Sem `opencode.db`.
- **Sessões analisadas**: `#685` Apply→QA→Done técnico; pedido `suba a release` com card já Homologado no board.
- **Custo/eficácia**: um Homologado; comentário Homologado postado no mesmo turno do closeout (arraste de Alan foi antes do helper).

### Métricas
- **Board**: 1 Homologado (`#685`). Fora: kaizen `#658`/`#659`/`#660` Em Refinamento; worktrees in-flight `#600`/`#614`/`#604`/`#472`/`#606`.
- **Git**: `origin/develop` HEAD `da77e93e` (PR #725). Archive via `release-2026-08-25-685`. Stash 0.
- **CI**: PR #725 `qa-gate` pass na `develop`. PR #726 merge `3482c763`.
- **OpenSpec**: 1 change arquivada; main spec `workflow-projects-lockdown` + `--skip-specs` (#659).
- **PROD**: source `3482c763`; alembic já head; bundle `index-Dtfnr-Df.js` / `index-DzSLxG6d.css`; health 200; GET `/api/workflow/projects` 401 sem connection string.

### Achados
- F-1 [major] Comentário Homologado canônico ausente até o closeout (arraste no board sem helper no mesmo turno do T15). Recidiva #658. Esforço S | P1 | Card existente: #658.
- F-2 [minor] Archive `--skip-specs` após sync do main spec. Recidiva #659. Esforço S | P1 | Card existente: #659.
- F-3 [info] Pedido `suba a release` com sessão Cursor ainda unbound na página; overlay T16 carregado. Alinhado ao #613.
- F-4 [info] Pytest local de isolation no Postgres compartilhado falhou em 2 testes de changes/tasks; CI integration passou. Sem card novo (infra de teste local, não o lockdown).
- F-5 [info] Segundo pacote no mesmo dia; mesma doc canônica `docs/release-2026-08-25.md`.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | #658
- Archive `--skip-specs` | #659

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #658 |
| (não criado) archive --skip-specs headers | — | F-2 | coberto por #659 |

## 2026-08-25 — Kaizen release (lote 684)

- **Release/card**: 2026-08-25 — Homologado → Pronto após deploy PROD `7af54584` via T16 live.
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees + `release-guard pre` PASS, CI PR #721, PROD health pós-deploy, overlay/runbook. Transcript Cursor deste host não indexado nesta sessão (Grok Build). Sem `opencode.db`.
- **Sessões analisadas**: closeout `suba a release` neste chat (Grok Build, sessão unbound; pedido explícito carregou overlay/T16).
- **Custo/eficácia**: um Homologado no pacote; comentário Homologado e `Responsável` ausentes até o closeout (preenchidos neste turno).

### Métricas
- **Board**: 1 Homologado (`#684`). Fora: `#600`/`#614` Aprovação de Design; `#604` Pronto para Dev; `#658`/`#659`/`#660` Em Refinamento.
- **Git**: `origin/develop` só com o pacote (`3ce00bd7`); archive via `release-2026-08-25` `bcd0c400`; merge `7af54584`. Stash 0. Worktrees classificadas via `PRESERVED_BRANCHES`.
- **CI**: PR #721 verde; `e2e-playwright` pass; `qa-gate`/`deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 1 change arquivada; sync da spec `jwt-secret-fail-closed` + `--skip-specs` (#659).
- **PROD**: source `7af54584`; alembic já head; bundle `index-Dtfnr-Df.js` / `index-DzSLxG6d.css`; health 200 após warmup; `JWT_SECRET` rotacionado no `.env` (presença/len, sem valor).

### Achados
- F-1 [major] Comentário Homologado canônico ausente em `#684` até o closeout. Recidiva #579/#658. Esforço S | P1 | Card existente: #658.
- F-2 [minor] `openspec archive` falhou na primeira tentativa (headers ADDED já no main spec após sync); `--skip-specs` operacional. Recidiva #659. Esforço S | P1 | Card existente: #659.
- F-3 [minor] `#684` Homologado sem `Responsável`; o `post` teria bloqueado. Preenchido no closeout (Codex). Sem card novo (o gate de campos já existe).
- F-4 [info] Pedido `suba a release` em sessão unbound: página Moore pede para não carregar playbook; overlay T16 carregado. Alinhado ao decision-log #613.
- F-5 [info] Task 4.1 (`JWT_SECRET` DEV) permaneceu `[ ]` no archive; rotação DEV/PROD foi operacional fora do git. Sem card novo.
- F-6 [info] Health PROD 502 no primeiro segundo após restart; 200 na tentativa seguinte. Padrão já visto no lote 2026-08-23. Sem card novo.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 9+ auditorias | #658
- Archive `--skip-specs` quando o apply/sync já materializou o main spec | #659

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #658 |
| (não criado) archive --skip-specs headers | — | F-2 | coberto por #659 |

## 2026-08-23 — Kaizen release (lote 673)

- **Release/card**: 2026-08-23 (2º pacote do dia) — Homologado → Pronto após deploy PROD `36534ae1` via T16 live.
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees + `release-guard pre` PASS, CI PR #680, PROD health pós-deploy, overlay/runbook. Transcript Cursor deste host não indexado nesta sessão (Grok Build). Sem `opencode.db`.
- **Sessões analisadas**: closeout `suba a release` neste chat (Grok Build, sessão unbound; pedido explícito carregou overlay/T16).
- **Custo/eficácia**: um Homologado no pacote; comentário Homologado e `Responsável` ausentes até o closeout (preenchidos neste turno).

### Métricas
- **Board**: 1 Homologado (`#673`). Fora: `#600`/`#614` Aprovação de Design; `#658`/`#659`/`#660` Em Refinamento.
- **Git**: `origin/develop` só com o pacote (`9a59dddd`); archive via `release-2026-08-23` `dadd739d`; merge `36534ae1`. Stash 0. Worktrees classificadas via `PRESERVED_BRANCHES`.
- **CI**: PR #680 verde; `qa-gate`/`deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 1 change arquivada; `--skip-specs` (#659).
- **PROD**: source `36534ae1`; alembic já head; bundle `index-Dtfnr-Df.js` / `index-DzSLxG6d.css`; health 200.

### Achados
- F-1 [major] Comentário Homologado canônico ausente em `#673` até o closeout. Recidiva #579/#658. Esforço S | P1 | Card existente: #658.
- F-2 [minor] `openspec archive` falhou por header ADDED já no main spec; `--skip-specs` operacional. Recidiva #659. Esforço S | P1 | Card existente: #659.
- F-3 [minor] `#673` Homologado sem `Responsável`; o `post` teria bloqueado. Preenchido no closeout (Clara). Sem card novo (o gate de campos já existe).
- F-4 [info] Pedido `suba a release` em sessão unbound: página Moore pede para não carregar playbook; overlay T16 carregado. Alinhado ao decision-log #613.
- F-5 [info] Ensaio deny Grok Auto (#668 task 4.5) permanece pendente; Grok continua cooperativo. Sem card novo.
- F-6 [info] Segundo pacote no mesmo dia; mesma doc canônica (#580). Sem card novo.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 8+ auditorias | #658
- Archive `--skip-specs` quando o apply já sincronizou o main spec | #659

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #658 |
| (não criado) archive --skip-specs headers | — | F-2 | coberto por #659 |

## 2026-08-23 — Kaizen release (lote 661/663/664/667/668)

- **Release/card**: 2026-08-23 — Homologado → Pronto após deploy PROD `aa36deb1` via T16 live.
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees + `release-guard pre` PASS, CI PR #671, PROD health pós-deploy, overlay/runbook. Transcript Cursor deste host não indexado nesta sessão (Grok Build). Sem `opencode.db`.
- **Sessões analisadas**: closeout `suba a release` neste chat (Grok Build, sessão unbound; pedido explícito carregou overlay/T16).
- **Custo/eficácia**: cinco Homologados no pacote; comentários Homologado ausentes até o closeout (postados antes do `pre`). `#667` chegou Homologado sem Prioridade/Responsável (preenchido neste turno).

### Métricas
- **Board**: 5 Homologado (`#661` `#663` `#664` `#667` `#668`). Fora: `#600`/`#614` Aprovação de Design; `#658`/`#659`/`#660` Em Refinamento.
- **Git**: `origin/develop` só com o pacote (`c88ba0a3`); archive via `release-2026-08-23` `b3373491`; merge `aa36deb1`. Stash 0. Worktrees classificadas via `PRESERVED_BRANCHES`.
- **CI**: PR #671 verde; `qa-gate`/`deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 5 changes arquivadas; `--skip-specs` em #661/#663/#664/#668; sync em #667 (`grill-card`).
- **PROD**: source `aa36deb1`; migration `20260823_0001`; bundle `index-Dtfnr-Df.js` / `index-DzSLxG6d.css`; health 200.

### Achados
- F-1 [major] Comentários Homologado canônicos ausentes nos 5 cards até o closeout. Recidiva #579/#658. Esforço S | P1 | Card existente: #658.
- F-2 [minor] `openspec archive` falhou em #661/#663/#664/#668 por headers ADDED já no main spec / MODIFIED divergente; `--skip-specs` operacional. Recidiva #659. Esforço S | P1 | Card existente: #659.
- F-3 [minor] `#667` Homologado sem Prioridade/Responsável; o `post` teria bloqueado. Preenchido no closeout (Clara/P2). Sem card novo (o gate de campos já existe).
- F-4 [info] Pedido `suba a release` em sessão unbound: página Moore pede para não carregar playbook; overlay T16 carregado. Alinhado ao decision-log #613.
- F-5 [info] Ensaio deny Grok Auto (#668 task 4.5) permanece pendente; Grok continua cooperativo. Sem card novo.
- F-6 [major] `release-guard post` falhou com `python3: Argument list too long` ao exportar `BOARD_JSON` (~245 cards com body) para o checker do #661. Corrigido no closeout: tempfile `--board-json-file` (PR #675, `478f0398`). Sem card novo neste lote (hotfix no pacote).

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 7+ auditorias | #658
- Archive `--skip-specs` quando o apply já sincronizou o main spec | #659

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #658 |
| (não criado) archive --skip-specs headers | — | F-2 | coberto por #659 |

## 2026-08-21 — Kaizen release (lote card 652)

- **Release/card**: 2026-08-21 (3º pacote do dia) — Homologado → Pronto após deploy PROD `0cb8aaf4` via T16 live.
- **Fontes consultadas**: board Project 1, `release-guard pre` PASS, CI PR #654/#655, PROD health, transcript desta sessão. Sem `opencode.db`.
- **Sessões analisadas**: apply #652 + closeout `suba a release` no mesmo chat.
- **Custo/eficácia**: `#652` Homologado quando Alan pediu release; comentário Homologado postado neste turno.

### Métricas
- **Board**: 1 Homologado (`#652`). In-flight `#472`/`#604`/`#606`/`#614`.
- **Git**: develop `49590820`; archive via `release-2026-08-21` `a59cf185`; sync #655.
- **CI**: PR #654 verde; `qa-gate` skip (`base_ref != develop`).
- **OpenSpec**: 1 change arquivada com sync de specs.
- **PROD**: source `0cb8aaf4`; alembic já head; bundle `index-CbEIETTN.js` / `index-q-WncaRa.css`; health 200.

### Achados
- F-1 [info] Primeiro closeout usando T16 live (`process_event fechar_release`) após post PASS — valida #652. Sem card novo.
- F-2 [info] Terceiro pacote no mesmo dia; mesma doc canônica (#580). Sem card novo.
- F-3 [minor] Comentário Homologado ainda ausente até o closeout. Recidiva #579.

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-3 | coberto por #579 |

## 2026-08-21 — Kaizen release (lote 617/618/625/631/632/637)

- **Release/card**: 2026-08-21 (2º pacote do dia) — Homologado → Pronto após deploy PROD `33df201a`.
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees + `release-guard pre` PASS, CI PR #648/#649, transcript Cursor desta sessão, PROD health pós-deploy. Sem consulta a `opencode.db`.
- **Sessões analisadas**: apply dos cards Pronto para Dev e closeout `suba a release` no mesmo chat.
- **Custo/eficácia por card**: seis Homologados no pacote; comentários Homologado canônicos ausentes até o closeout (postados antes do `pre`).

### Métricas
- **Board**: 6 Homologado no lote (`#617` `#618` `#625` `#631` `#632` `#637`). Fora: `#604` Aprovação de Design; `#608` Em Refinamento; in-flight `#472`/`#606`/`#614`.
- **Git**: `origin/develop` só com o pacote (`05691619`); archive via `release-2026-08-21` `6a71b015`; sync `main→develop` #649. Stash 0. Worktrees classificadas via `PRESERVED_BRANCHES`.
- **CI**: PR #648 verde; `qa-gate`/`deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 6 changes arquivadas; `--skip-specs` em #632/#637; specs sync nos demais.
- **PROD**: source `33df201a`; migration `20260821_0001`; bundle `index-CbEIETTN.js` / `index-q-WncaRa.css`; health 200.

### Achados
- F-1 [major] Comentários Homologado canônicos ausentes nos 6 cards até o closeout. Recidiva #579. Esforço S | P1 | Card existente: #579.
- F-2 [minor] `openspec archive` falhou em #632/#637 por headers `MODIFIED` divergentes; `--skip-specs` operacional. Esforço S | P2 | Sem card novo neste lote.
- F-3 [info] Segundo pacote no mesmo dia reutilizou o nome `release-2026-08-21` e atualizou a mesma doc canônica (contrato #580). Sem card novo.
- F-4 [info] Path archive-via-`release-*` + sync #649 usado conforme #617; `pre` com skip de develop local conforme #618.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 6+ auditorias | #579
- Archive via `release-*` quando `develop` exige `qa-gate` | pacote que fecha #617

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #579 |
| (não criado) archive MODIFIED diverge | — | F-2 | coberto por #659 |

## 2026-08-21 — Kaizen release (lote card 613)

- **Release/card**: 2026-08-21 — card 613 (Homologado → Pronto após deploy PROD `7df18d54`).
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees/stash + `release-guard pre` PASS, CI PR #638, ensaio e-to-e desta sessão Cursor (#608/#613), `openspec validate` 149 no CI. Transcripts em `agent-transcripts/` ausentes neste host (limitação declarada). Sem consulta a `opencode.db`.
- **Sessões analisadas**: teste ponta a ponta do epic #608 pedido por Alan; closeout `suba a release` no mesmo chat. Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: `#613` já Homologado no board quando Alan pediu `suba a release`. Comentário Homologado canônico ausente até este turno.

### Métricas
- **Board**: 1 Homologado no lote (`#613`, Clara / P2 / Operacao). Fora: `#614` Aprovação de Design; `#608` Em Refinamento; in-flight `#472`/`#606`.
- **Git**: `origin/develop` só com o pacote (`771784ab`); archive via `release-2026-08-21` `6e58e4e4`. Stash 0. Worktrees in-flight classificadas via `PRESERVED_BRANCHES`.
- **CI**: PR #638 verde; `qa-gate` e `deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 1 change arquivada; spec nova `process-fsm-paging`.
- **PROD**: source `7df18d54`; alembic já head; bundle `index-A5R04R0w.js` / `index-Cyx126Ee.css`; health 200 após warmup.

### Achados
- F-1 [major] Comentário canônico Homologado ausente no #613 até o closeout. Recidiva do contrato #579. Esforço S | P1 | Card existente: #579.
- F-2 [major] Guard `beforeShellExecution` deny por substring (`item-edit` de Status, `>` / paths de produto) em comandos de ensaio e deploy. Recidiva. Esforço S | P1 | Cards existentes: #625, #631.
- F-3 [minor] Archive foi a `main` via `release-*`; `develop` ficou com a change ativa até o sync. Recidiva. Esforço S | P1 | Card existente: #617.
- F-4 [info] Health público 502 imediatamente após restart PROD; 200 em ~8s. Sem card novo.
- F-5 [info] Página unbound pede para não carregar playbook de release; pedido explícito `suba a release` carrega o overlay. Comportamento alinhado a δ (T16) vs Moore. Sem card novo.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 5+ auditorias | #579
- Guard Shell falso positivo / substring | 3+ no dia 20–21 | #625 / #631
- `develop` protegido vs archive no SHA da release | 4ª ocorrência | #617

### Trechos de sessão (evidência local)
- `bound_card=⊥. Write produto deny. Não carregue playbook de release.`
- `process-fsm-guard deny reason=status_item_edit. Use process_event.`
- `process-fsm-guard deny reason=fail_closed q=None q_git=develop bound_card=⊥`

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (não criado) Homologado sem comentário | — | F-1 | coberto por #579 |
| (não criado) Guard Shell / sidecar | — | F-2 | coberto por #625 / #631 |
| (não criado) archive via `release-*` | — | F-3 | coberto por #617 |

## 2026-08-20 — Kaizen release (lote card 612)

- **Release/card**: 2026-08-20 (2º lote do dia) — card 612 (Homologado → Pronto após deploy PROD `5110b9b0`).
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees/stash + `release-guard pre` PASS, CI PRs #629/#630, transcript Cursor da sessão #612, `openspec validate` 148 no CI. Sem consulta a `opencode.db`.
- **Sessões analisadas**: closeout do #612 (Design → apply → QA → homologação em chat → release). Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: `#612` já Homologado no board quando Alan pediu `esta homologado suba a release`. Comentário Homologado canônico já existia neste turno.

### Métricas
- **Board**: 1 Homologado no lote (`#612`, Clara / P1 / Operacao). Fora: `#614` Aprovação de Design; `#608`/`#613`/`#617`/`#625` Em Refinamento; in-flight `#472`/`#606`.
- **Git**: `origin/develop` só com o pacote (`f6388539`); archive via `release-2026-08-20-612` `7c99a894`. Stash 0. Worktrees in-flight classificadas via `PRESERVED_BRANCHES`. Extra `develop-lote3` em `main` (warn).
- **CI**: PR #629 `qa-gate` pass; PR #630 verde com `qa-gate` skip (`base_ref != develop`).
- **OpenSpec**: 1 change arquivada (`--skip-specs` após sync); spec nova `process-fsm-event`.
- **PROD**: source `5110b9b0`; alembic já head; bundle `index-A5R04R0w.js` / `index-Cyx126Ee.css`; health 200 após restart backend/frontend.

### Achados
- F-1 [major] Guard deny por substring do sidecar de digest em qualquer Shell (git add do archive, commit com o token na mensagem). Esforço S | P1 | Card: #631.
- F-2 [major] T14 live nunca preenche `checks_green`; Agent não fecha Done (yaml diz Agent; CLI reject). Esforço M | P1 | Card: #632.
- F-3 [minor] Archive foi a `main` via `release-*`; `develop` ficou com a change ativa. 3ª ocorrência. Esforço S | P1 | Card existente: #617.
- F-4 [minor] HEREDOC/`fail_closed` em branch `release-*`. Recidiva. Card existente: #625.
- F-5 [info] `Responsável` do #612 estava vazio até o closeout (preenchido Clara). Sem card novo.
- F-6 [info] Comentário Homologado canônico existia neste lote (não é recidiva do #579).

### Padrões recorrentes
- `develop` protegido vs archive no SHA da release | 3ª ocorrência | #617
- Guard Shell falso positivo (`>` / fail_closed) | 2ª ocorrência no dia | #625
- Deny por substring do sidecar | 1ª ocorrência como BLOCKER de archive | #631
- T14 live inútil | 1ª ocorrência | #632

### Trechos de sessão (evidência local)
- `process-fsm-guard deny reason=sidecar`
- `process-fsm-guard deny reason=fail_closed q=None q_git=release-2026-08-20-612 bound_card=⊥`
- `A coluna do board continua Done. O próprio card impede o Agent de fazer T15`

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #631 — Guard: substring do sidecar não pode deny git add/commit | P1 | F-1 | Em Refinamento |
| #632 — T14 live: integrar_develop deve poder Done após CI verde | P1 | F-2 | Em Refinamento |
| (não criado) archive via `release-*` | — | F-3 | coberto por #617 |
| (não criado) HEREDOC `>` / fail_closed | — | F-4 | coberto por #625 |

## 2026-08-20 — Kaizen release (lote cards 605/610/611)

- **Release/card**: 2026-08-20 — cards 605, 610, 611 (Homologado → Pronto após deploy PROD `ad8158fd`).
- **Fontes consultadas**: board Project 1 (`item-list`), git/worktrees/stash + `release-guard pre` PASS, `openspec validate --all` 147/147, PR #624, transcript Cursor desta sessão, CI `gh pr checks --watch` exit 0.
- **Sessões analisadas**: homologação do lote 1 (ensaio Write-na-develop) e closeout da release. Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: os 3 já estavam Homologado no board na abertura (exceto o marcador canônico do #605, postado neste turno). Alan pediu `suba a release` e recusou esperar #612/#613.

### Métricas
- **Board**: 3 Homologado no lote; fora: `#608`/`#612`/`#613` Em Refinamento, `#614` Aprovação de Design.
- **Git**: `origin/develop` só com o pacote Homologado (`e78d358c`); archive local via `release-2026-08-20` `06836f77`. Stash 0. Worktrees in-flight classificadas via `PRESERVED_BRANCHES` (#472/#606/#614/#584 e leftovers #605/#610/#611). Extra `develop-lote3` em `main` (warn).
- **CI**: PR #624 verde; `qa-gate` e `deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 3 changes arquivadas (`--skip-specs` após sync agent-driven); specs novas `process-fsm-resolver` e `process-fsm-guard`.
- **PROD**: source `ad8158fd`; alembic `20260818_0001`; bundle `index-A5R04R0w.js` / `index-Cyx126Ee.css`; health 200 após restart.

### Achados
- F-1 [major] `beforeShellExecution` trata `2>/dev/null` (caractere `>`) como mutação; comando de inventário/deploy que também cita path de produto recebe deny. Bloqueou o closeout até encapsular em `/tmp`. Esforço S | P1 | Card: #625.
- F-2 [major] Comentário canônico Homologado ausente no #605 até o closeout. Recidiva do contrato #579. Esforço S | P1 | Card existente: #579 (não duplicar).
- F-3 [minor] Push/archive em `develop` de novo recusado pelo caminho `qa-gate`; lote saiu por `release-*`. Já coberto por #617. Extra worktree `develop-lote3` em `main` não limpa.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 4+ auditorias (#579 publicado; recidiva neste lote no #605)
- `develop` protegido vs archive no SHA da release | 2ª ocorrência | card #617
- Guard Shell falso positivo com redirect nulo | 1ª ocorrência como BLOCKER de operação

### Trechos de sessão (evidência local)
- `process-fsm-guard deny reason=fail_closed q=None q_git=develop bound_card=⊥. Write produto blocked.` (ensaio humano PASS)
- `error: cannot open '.git/FETCH_HEAD': Permission denied` no source PROD até `sudo`
- deny do hook em comando de inventário com `2>/dev/null` + path de produto

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #625 — Guard beforeShellExecution trata redirect nulo como write de produto | P1 | F-1 | Em Refinamento |
| (não criado) recidiva Homologado sem comentário | — | F-2 | coberto por #579 |
| (não criado) archive via `release-*` / worktree leftover | — | F-3 | coberto por #617 |

## 2026-08-19 — Kaizen release (lote cards 549/582/599/609)

- **Release/card**: 2026-08-19 — cards 549, 582, 599, 609 (Homologado → Pronto após deploy PROD `c6762a27`).
- **Fontes consultadas**: board Project 1 (`item-list` 230/230), git/worktrees/stash + `release-guard pre` PASS, `openspec validate --all` 145/145, PR #616, transcript Cursor desta sessão (`610c1ba2`), CI `gh pr checks --watch` WATCH_EXIT=0.
- **Sessões analisadas**: closeout da release; implementação prévia do #609 na sessão anterior. Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: os 4 já estavam Homologado no board na abertura; Alan pediu `suba a release`. `#609` tinha comentário Homologado; `#549`/`#582`/`#599` só receberam o helper neste turno.

### Métricas
- **Board**: 4 Homologado no lote; fora: `#605` QA, `#610`/`#614` Aprovação de Design, `#611` Todo, `#608`/`#612`/`#613` Em Refinamento.
- **Git**: `origin/develop` só com o pacote Homologado (`ff85eb71`); archive local não pôde ir para `develop` (proteção qa-gate). `release-2026-08-19` = develop + archive `0ec5dd77`. Stash 0. Worktrees in-flight classificadas via `PRESERVED_BRANCHES` (#605/#610/#614/#472/#606 e leftovers #549/#582).
- **CI**: PR #616 verde; `qa-gate` e `deploy-staging` skip (`base_ref != develop`).
- **OpenSpec**: 4 changes arquivadas (`--skip-specs` após sync agent-driven); specs novas `process-fsm` e `palestra-upstream-deploy`.
- **PROD**: source `c6762a27`; alembic `20260818_0001`; bundle `index-A5R04R0w.js` / `index-Cyx126Ee.css`; health 200.

### Achados
- F-1 [major] Push em `develop` recusado (`Required status check qa-gate is expected`) para o commit de archive; o lote saiu por `release-*` → `main` mesmo com `develop` só Homologado. Esforço S | P1 | Card: #617.
- F-2 [major] Comentário canônico Homologado ausente em 3/4 cards até o closeout (`#549`/`#582`/`#599`). Recidiva do F-1 lote 2 / contrato #579. Esforço S | P1 | Card existente: #579 (não duplicar).
- F-3 [minor] `pre` em `release-*` bloqueou a ref local `develop` com o archive ainda não publicado. Workaround: `git branch -f develop origin/develop`. Esforço S | P2 | Card: #618.

### Padrões recorrentes
- Homologado sem comentário canônico no turno do arraste | 3+ auditorias (#579 publicado; recidiva neste lote)
- `develop` protegido vs archive no SHA da release | 1ª ocorrência como BLOCKER de push | promoção: runbook `release-*`

### Trechos de sessão (evidência local)
- `remote: error: GH006: Protected branch update failed for refs/heads/develop. Required status check "qa-gate" is expected.`
- `BLOCKER: local branch not merged into origin/develop or origin/main: develop`

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #617 — closeout quando develop exige qa-gate / archive via `release-*` | P1 | F-1 | Em Refinamento |
| #618 — `pre` em `release-*` não bloquear local `develop` | P2 | F-3 | Em Refinamento |
| (não criado) recidiva Homologado sem comentário | — | F-2 | coberto por #579 |

## 2026-08-17 — Card #569 (pivot: reviewers locais inherit/readonly)

- **Release/card**: #569 kaizen (não é closeout de lote).
- **Fontes consultadas**: chat Alan (recusa Bugbot por custo), docs Cursor, `AGENTS.md`, crítica isolada 3 (`35f2d0ba`).
- **Resultado**: design Bugbot-obrigatório obsoleto → pivot para `diff-reviewer` + `code-reviewer` (`inherit`/readonly) vs `develop`; card devolvido a Aprovação de Design.
- **Card**: [#569](https://github.com/oalansilva/crypto/issues/569). Change `card-569-code-review-bugbot`.
- **Status**: Design PASS (pivot); aguardando arraste de Alan para `Pronto para Dev`.

### Achados
- F-2 [major] Produto Bugbot recusado por custo após apply do plano obrigatório. Correção: reviewers locais versionados; Bugbot Off de propósito. Esforço S | P1 | Card: #569.

## 2026-08-17 — Card #569 (Code Review nativo /review-bugbot)

- **Release/card**: #569 kaizen (não é closeout de lote).
- **Fontes consultadas**: docs oficiais Cursor (Bugbot, Agent Review, Security Agents, Subagents), `AGENTS.md`, skill `/review-bugbot`.
- **Resultado**: proposta em Em Refinamento → Design PASS → `Pronto para Dev` (arraste Alan) → apply do contrato `/review-bugbot` vs `develop`, `BUGBOT.md` e revisor de processo.
- **Card**: [#569](https://github.com/oalansilva/crypto/issues/569). Change `card-569-code-review-bugbot`.
- **Status**: implementação na branch `card-569-code-review-bugbot`.

### Achados
- F-1 [major] Code Review usava `Task` genérico; Bugbot só sob pedido. Correção: `/review-bugbot` obrigatório; prompts fiéis à skill. Esforço S | P1 | Card: #569.

## 2026-08-09 — Auditoria inicial (card #420)

- **Escopo**: implementação da v1 do Agente Kaizen (card #420, `Status=Todo`).
- **Fonte**: board Project 1, sessões opencode (escopo release ainda não definido).
- **Resultado**: criação da infraestrutura do Kaizen (agent, command, este log,
  label `kaizen`, regras AGENTS/rules).
- **Cards criados**: (a preencher após auditoria de teste da release 2026-08-08).

---

## Template de entrada de auditoria

```markdown
## YYYY-MM-DD — <Escopo> (</kaizen card <id> | /kaizen release <nome> | /kaizen>)

- **Release/card**: <nome ou id>
- **Fontes consultadas**: <board | git | openspec | ci | sessoes | tech-debt>
- **Sessões analisadas**: <n> sessões | <custo/tokens agregados> | <erros por tipo>
- **Custo/eficácia por card**: <card> → <custo> → <status final no board>

### Achados
- F-<n> [severity: blocker|major|minor|info] <título>
  - Evidência: <IDs de sessão/mensagem/tool, PR, commit, item do board>
  - Causa raiz: <...>
  - Correção proposta: <...> (tipo: regra|script|doc|skill|tech-debt)
  - Esforço: <S|M|L> | Prioridade: <P0|P1|P2>
  - Status: <proposto | aprovado | recusado | implementado | verificado>
  - Card: #<issue>

### Trechos de sessão (evidência local)
- <2-3 linhas, sem payload privado/tokens/raciocínio íntegro>

### Padrões recorrentes (2+ ocorrências → severidade +1 e promoção de regra)
- <padrão> | <ocorrências> | <promoção sugerida>
```

## Histórico de mudanças de processo (regras/skills/scripts)

| Data | Mudança | Origem | Evidência |
| --- | --- | --- | --- |
| 2026-08-09 | Criação do Agente Kaizen (agent, command, log, label, regras) | card #420 | issues #420, kaizen-log |
| 2026-08-14 | Fechamento de release como gate: `RELEASE_DATE` canônica, doc única sem placeholder exigida no `pre`/`post`, entrada de `/kaizen release` em `kaizen-log.md` pré-condição do `post`, `RELEASE_BRANCHES` obrigatório com ausência local+remota, `main` local sincronizada como blocker, ordem canônica no AGENTS.md e spawn vazio de subagent como erro explícito de handoff | card #518 (relacionado a F-3/F-6/F-7 da auditoria 2026-08-14) | issues #518, change `card-518-kaizen-release-gate`, `scripts/release-guard` |
| 2026-08-17 | Code Review local: `diff-reviewer` + `code-reviewer` (`inherit`/readonly) vs `develop`; Bugbot Off de propósito (custo); Autofix não commita na branch existente | card #569 | issues #569, change `card-569-code-review-bugbot` |

## 2026-08-09 — Auditoria de teste: release 2026-08-08 (`/kaizen release`)

- **Release/card**: 2026-08-08 — cards 361, 384, 395, 399 (todos `Pronto`).
- **Fontes consultadas**: board Project 1 (167 itens), issues + comentários, git/refs/worktrees/stash + `release-guard audit`, `openspec validate --all`, PRs #386/#391-394/#396/#398/#400-406/#409/#411-412, opencode DB (37 sessões, 1686 msgs, 6848 parts, 29 todos — read-only), npm audit frontend.
- **Sessões analisadas**: 3 no escopo da release (validação #395+#399: $0.385 / 4.1M tokens; 2 subagentes vision gpt-5.6-luna $0.006). Cards 361/384 executados no Codex — sessões indisponíveis no DB (limitação).
- **Custo/eficácia por card**: 361/384 (Codex, sem sessão) → `Pronto`; 395/399 → `Pronto` com sessões no DB.

### Métricas
- **Board**: Pronto 150, Cancelado 10, Homologado 3 (#385/#413/#416), Em desenvolvimento 2, Todo 2. Divergência `Status` vs `Fluxo` em 100/167 itens (campo legado); #416 `Homologado` com `Fluxo=Backlog`.
- **Git**: 14 warnings / 0 blockers no release-guard; 6 worktrees extras (2 dirty), refs órfãs de releases anteriores (runtime-card-362-develop, rollback-card-362-369, runtime-develop-card369, release-post-20260802, sync-main-into-develop-20260803, release-20260803-cards-366-374); sem stashes.
- **OpenSpec**: `validate --all` 149/149 PASS; 4 changes arquivadas (2026-08-08); 47 changes ativas com idade variada (higiene pendente).
- **Sessões**: erros de tool 0; `step-finish unknown` 2 (card #385, fora do pacote); todos pendentes 4 (sessão #399); drift de roteamento 49 msgs gpt-5.6-luna em sessão deepseek (card #385, $0.58).

### Achados
- F-1 [major] Card #384: `Design Agent verdict: BLOCKED` às 18:38Z seguido de implementação sem aprovação registrada às 19:30Z (mesmo dia). Correção: exigir comentário/arraste de aprovação de Alan + resolução de BLOCKED registrada no design.md. Esforço S | P0.
- F-2 [major] Card #395: zero evidência de gate de Design/Aprovação (criação 00:51 → Done 01:15). Correção: checklist de gates no PR/commits de integração (design.md/verdict mesmo para tooling). Esforço S | P1.
- F-3 [minor] OpenSpec republicado em múltiplos Gists por change (#361: 3 gists; #399: 3 gists) — spam de comentários. Correção: helper atualizar gist-id existente. Esforço S | P2.
- F-4 [minor] Fragmentação de PRs por card (5 em #384, 4 em #399) + commit vazio de retrigger. Correção: agrupar ajustes pós-review; retrigger via `workflow_dispatch`. Esforço M | P2.
- F-5 [minor] Refs/worktrees de releases anteriores não classificados; preserve/change-413-wallet-zebra-20260808 dirty com WIP após `Homologado`. Correção: estender `release-guard post` (inventário runtime-*/rollback-*/preserve). Esforço M | P1.
- F-6 [minor] Todos do opencode nunca fechados na sessão de validação do #399. Correção: `/opsx:verify`/Done exige todos `completed` ou remoção justificada. Esforço S | P2.
- F-7 [info] Release inicialmente fechada `Pronto` sem deploy PROD — corrigida no mesmo dia (regra + skill). Correção (validação): `release-guard pre` checa evidência de deploy PROD. Esforço S | P1.
- F-8 [info] Tech debt: sheetJS/xlsx 5 high + 3 moderate sem fix upstream. Esforço M | P2.
- F-9 [info] vision-router gravou 49 msgs gpt-5.6-luna na sessão principal deepseek (card #385, $0.58) — auditar transform para garantir vision só em sessão filha; #416 endereça troca de modelo. Esforço M | P2.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #421 — Exigir evidência de aprovação de Design antes de aplicar código | P0 | F-1, F-2 | Todo |
| #422 — release-guard: exigir deploy PROD antes de Pronto e inventariar refs órfãs | P1 | F-5, F-7 | Todo |
| #423 — publish-openspec-card-artifacts: atualizar gist existente + retrigger CI sem commit vazio | P2 | F-3, F-4 | Todo |

### Backlog kaizen (para releases seguintes — 2+ ocorrências elevam severidade)
- F-6: sincronizar todos do opencode no fechamento de card (P2).
- F-8 + F-9: avaliar substituição de sheetJS/xlsx e auditar custo/modelID do vision-router (P2).

### Trechos de sessão (evidência local)
- `ses_0212ac001ffe` — todo `in_progress`: "Teste unitário do plugin vision-router (data URL -> persistir -> placeholder -> …)" + 3 pendentes com card #399 já Done.
- `ses_020c4438effey9rj5N` — 49 msgs assistant modelID=gpt-5.6-luna em sessão deepseek, custo total $0.5789.
- `ses_020e33491ffe` — subagent vision gpt-5.6-luna sem erros; roteamento visual esperado (exceção do #399).

### Limitações
- Cards 361/384 executados no Codex — sessões ausentes do opencode DB.
- Timestamps de itens do board não expostos via `gh project item-list`.
- `npm audit` com snapshot local (sem rede completa).

## 2026-08-09 — Auditoria pós-release: release 2026-08-09 (`/kaizen release`)

- **Release/card**: 2026-08-09 — card 420 (Agente Kaizen). Pacote único `Homologado`.
- **Fontes consultadas**: board (170 itens), issues #385/#413/#416/#420, git/refs/worktrees/stash + release-guard audit, OpenSpec (validate 151/151, archive, specs), CI PRs #424/#425/#426, opencode DB (14 sessões no window, read-only).
- **Sessões analisadas**: 14 no window (08-08→09) — custo total $0.2526, 1.69M tokens in, 0 todos incompletos, 0 drift, 0 `step-finish unknown`, 2 erros de tool (1 `task` "Unknown agent type: kaizen" no bootstrap; 1 edit miss). Sessão principal #420 `ses_01c171a3` $0.1153 → Done.

### Métricas
- **Board**: Pronto 150, Done 3 (#385/#413/#416), Homologado 1 (#420 — movido a Pronto após esta auditoria), Todo 4 (#195 + kaizen #421/#422/#423). Divergências Status vs Fluxo legadas (#416, #395, #361, #384, #353, #355).
- **Git**: release-guard audit PASS (15 warnings/0 blockers); refs órfãs antigas persistem (F-6 da auditoria 08-08, card #422 ainda Todo); refs da própria release pendentes de limpeza.
- **OpenSpec**: validate 151/151; **F-1: change card-420 duplicada em develop (ativa + arquivada)** — corrigida no mesmo turno via PR #427.
- **Sessões**: custo baixo, sem alucinação significativa; 2 spawns vision gpt-5.6-luna pós-merge #419 (troca qwen3.7-plus não propaga para sessões em voo).

### Achados
- F-1 [major] Archive OpenSpec não propagou para develop — change card-420 duplicada (ativa + arquivada). Causa: sync back `main -> develop` adicionou o archive sem remover a pasta ativa. **Corrigido imediatamente** (PR #427, `972d620a`). Proposta: `release-guard post` detecta duplicação change ativa+arquivada. Esforço S | P1.
- F-2 [major] Regressão de status `Homologado -> Done` em #385/#413/#416 sem evidência de autorização. Causa: rework/closure iniciado sem classificar regressão; regra "só avança" não prevê retorno. Proposta: regra/checklist — rework pós-Homologado exige comentário de Alan autorizando regressão. Esforço S | P1.
- F-3 [minor] Divergência de título #416: board "MiMo-V2.5" vs issue "Qwen3.7 Plus" vs implementação qwen3.7-plus. Proposta: regra de sync título board/issue no fechamento. Esforço S | P2.
- F-4 [minor] Troca de modelo do vision não propaga para sessões/spawns em voo (2 spawns gpt-5.6-luna pós-merge). Proposta: troca de modelo de agente exige sessão nova. Esforço S | P2.
- F-5 [info] Erro `task` "Unknown agent type: kaizen" durante bootstrap do próprio agente. Proposta: não invocar subagent recém-criado no mesmo turno. Esforço S | P2.
- F-6 [info] Refs da release pendentes de limpeza pós-Pronto; refs antigas persistem (depende de #422). Esforço M | P2.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #428 — release-guard post detecta change OpenSpec duplicada ativa+arquivada | P1 | F-1 | Todo |
| #429 — rework pós-Homologado exige comentário de autorização e classificação no card | P1 | F-2 | Todo |
| #430 — sync título board/issue + sessão nova após troca de modelo de subagent | P2 | F-3, F-4 | Todo |

### Backlog kaizen (releases seguintes)
- F-5: checklist de fechamento — não invocar subagent recém-criado no mesmo turno (P2).
- F-6: limpeza de refs órfãs antigas (já em #422) + refs da release após Pronto (P2).

### Trechos de sessão (evidência local)
- `ses_01c171a3` — 1× task error "Unknown agent type: kaizen" (bootstrap do próprio agente; recuperado; 5/5 todos completed, $0.1153).
- `ses_01c807cb` (tree) — spawns vision `ses_01c08305`/`ses_01c05d64` pós-merge #419 ainda com gpt-5.6-luna; título de sessão "trocar GPT Luna por MiMo-V2.5" divergente do issue.

### Limitações
- Timestamps de itens do board não expostos via `gh project item-list`.
- Evidência de arraste de aprovação não visível via API (só comentários).
- Validação de deploy/URL PROD pertence ao fechamento da sessão principal (executada: source e2c89d4d, services ativos, endpoints ok).

---

## Auditoria pós-release 2026-08-09 — cards #385, #413, #416 (release develop->main #437)

- **Escopo**: release 2026-08-09 (cards #385 Monitor Spot Binance, #413 carteira leitura, #416 roteamento visual qwen3.7-plus). Deploy PROD `27f9e1bf` validado antes da auditoria (regra 14).
- **Board**: 173 itens — Pronto 151, Cancelado 10, Todo 7, Homologado 3 (#385/#413/#416), Em desenvolvimento 2. Prioridade P0=30, P1=77, P2=11, vazia=55; sem Responsável: 21 (inclui #413/#416).
- **Git**: worktree único, 0 stashes; origin/develop ancestral de origin/main com trees idênticas; branches/worktrees do pacote limpas; guard post PASS.
- **OpenSpec**: validate 150/150 pré-archive; 3 changes do pacote arquivadas + 4 delta specs sincronizadas (`monitor-direct-spot-trading` nova, `user-preferences-binance-credentials`, `external-balances`, `visual-analysis-routing`); 148/148 pós-archive.
- **CI**: PR #437 MERGED (27f9e1bf); 20 checks pass + 6 skipping condicionais esperados (qa-gate base develop, deploy-staging var inativa).
- **Sessões**: 41 no window, custo $2.01; #385 ≈ $1.23, #413 ≈ $0.10, #416 ≈ $0.06; nenhuma sessão cara sem Done.

### Achados
- F-1 [minor P1] Evidência documental do deploy PROD ficou só no worktree (doc do pacote com placeholders em develop/main); dois docs de release da mesma data em paralelo. Proposta: antes de `Pronto`, commitar doc preenchida (com seção kaizen); uma doc canônica por release. Esforço S.
- F-2 [minor P2] Campos do board incompletos em cards da release (#413 Responsável/Prioridade/Tipo vazios; #416 Responsável vazio; título board vs issue divergente). Proposta: `release-guard post` valida campos do pacote e título board/issue. Esforço S.
- F-3 [minor P2] Caminhos inventados na delegação visual do #413 (4× File not found + respawns) e 3× webfetch 404. Proposta: path-check antes de delegar ao vision; sem respawn por arquivo inexistente. Esforço S.
- F-4 [minor P2] Títulos de sessão não informativos em sessões caras ("Casual greeting" 4.1M tokens $0.38). Proposta: título descritivo obrigatório em sessões de trabalho. Esforço S.
- F-5 [minor P1] Reincidência (2ª auditoria): todos do opencode nunca concluídos (card-399) e comentário OpenSpec duplicado no card. Proposta: `/opsx:verify`/Done exige todos completed; helper atualiza gist/comentário existente; elevar #423 para P1. Esforço S.
- F-6 [info] 2× `step-finish unknown` e spawns vision gpt-5.6-luna pós-merge #419 — já conhecidos, cobertos por #430. Sem ação nova.

### Cards kaizen (máx 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #43X — release-guard post valida evidência documental e campos do board antes de Pronto | P1 | F-1, F-2 | Todo |
| #43X — path-check antes de delegar análise visual; zero respawn por arquivo inexistente | P2 | F-3 | Todo |
| #43X — fechamento exige todos completed + título de sessão informativo; elevar #423 a P1 | P2 | F-4, F-5 | Todo |

### Backlog kaizen (releases seguintes)
- F-6: troca de modelo não propaga para sessões em voo (já em #430).

### Trechos de sessão (evidência local)
- `ses_01d6…` — 4× `File not found: /tmp/opencode/bl413/{old,new}-{desktop-table,mobile-cards}.png` após delegação vision da sessão principal do #413.
- `ses_01db…` — 3× `webfetch 404` em `docs.github.com/en/rest/attachments/...`, `.../issues/issue-comments`, `github.com/git/git/actions/runs/1`.
- `ses_0212ac…` — todo `in_progress` nunca atualizado ("Teste unitário do plugin vision-router ...") + 3 pendentes; título "Casual greeting", 4.1M tokens, $0.38.
- `ses_01c807→ses_01c083/ses_01c05d` — spawns vision gpt-5.6-luna 2 min após merge #419 (sessão em source sem pull; worktree do card já usava qwen3.7-plus).

### Limitações
- Timestamps do board não expostos via `gh project item-list`.
- Evidência de arraste `Aprovação de Design -> Pronto para Dev` não verificável via API (só comentários).
- Cards 361/384 executados no Codex — fora do opencode DB.

---

## 2026-08-09 — Auditoria pós-release: release kaizen 421-440 (`/kaizen release`)

- **Release/card**: 2026-08-09 — pacote kaizen #421/#422/#423/#428/#430/#438/#439/#440 (PR #451 merge `4e7c125f`; docs #452/#453; limpeza dívida #454/#455 `c25e662f`).
- **Fontes consultadas**: board (176 itens), issues/comentários 421-440, PRs 443-455 + checks, git/refs/worktrees/stash + release-guard audit, OpenSpec validate 144/144 + status (8 changes do pacote), docs/release-2026-08-09.md, opencode DB (45 sessões, mode=ro).
- **Sessões analisadas**: 45 no window — custo total $2.505; pacote ≈ $0.05/card; todos 10/10 completed na sessão de implementação (`ses_0198` $0.417); erros pré-fix #439 (5 file_not_found, 3 webfetch 404) e pré-fix #440/#423 (ses_0212 "Casual greeting" $0.385/4.1M tokens, 4 todos incompletos) sem reincidência pós-fix.

### Métricas
- **Board**: Pronto 154, Homologado 8 (pacote), Cancelado 11, Em desenvolvimento 2 (#197/#259), Todo 1 (#195). Pacote 8/8 com campos (Resp/Prio/Tipo) e título board==issue sincronizados (fix #430/#438 funcionando).
- **Git**: 1 worktree limpa, 0 stashes; refs órfãs runtime-*/preserve/*: 0; guard audit PASS (2 warnings, 0 blockers). Branches da release em origin aguardando closeout pós-Pronto.
- **OpenSpec**: validate 144/144; 8 changes do pacote ativas e completas (archive pendente no fechamento); ~33 changes antigas de cards terminais ainda ativas (F-3).
- **CI**: PRs 443-450 qa-gate verde; PRs 451-455 verdes (qa-gate skipping condicional em PR→main, padrão já documentado).
- **Sessões**: pacote limpo — 0 loops, 0 todos eternos, 0 título genérico em sessão cara (pós-fix).

### Achados
- F-1 [minor→major por recorrência, P1] Comentários de evidência de Done duplicados em 8/8 cards do pacote (postado 2×, formato diferente). Causa: post em lote sem dedupe. Proposta: helper verifica commit ref existente antes de postar; regra 1 evidência por transição. Esforço S.
- F-2 [minor, P1] Guard post não inventaria branches `change-*/card-*/release-*` (só runtime-*/preserve/*): dívida de releases antigas (08-03, mai-jul) sem enforcement. Proposta: estender inventário + checklist de deleção no closeout. Esforço M.
- F-3 [minor, P2] ~33 changes OpenSpec de cards Pronto/Cancelado nunca arquivadas. Proposta: rodada `/opsx:bulk-archive` + check no guard. Esforço M.
- F-4 [minor, P2] Cards presos há 2 auditorias: #197/#259 em Em desenvolvimento, #195 em Todo. Proposta: triagem no próximo turno. Esforço S.
- F-5 [info, P2] Homologado sem comentário padrão "Homologado por Alan" nos 8 cards (arraste/chat não verificável via API). Proposta: warn no guard (extensão #438). Esforço S.
- F-6 [info] "Modelo antigo pós-merge" — 2 spawns vision gpt-5.6-luna 2-5 min pós-merge #419; nenhum além desse par; regra #430 validada.
- F-7 [info] ses_0212 (pré-fix) permanece no DB como recorrência que motivou #440/#423; sem ação nova.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #456 — dedupe de comentários de evidência no fechamento (1 por transição) | P1 | F-1 | Todo |
| #457 — release-guard post inventaria change-*/card-*/release-* + deleção no closeout | P1 | F-2 | Todo |
| #458 — bulk-archive de changes de cards terminais + check no guard | P2 | F-3 | Todo |

### Backlog kaizen (releases seguintes)
- F-4: triagem dos cards presos #197/#259/#195.
- F-5: check de comentário de homologação no guard post (extensão #438).
- F-6/F-7: observabilidade (sem ação nova).

### Trechos de sessão (evidência local)
- `ses_0198` — 10/10 todos completed; 3× edit oldString; 1× PermissionDenied ao editar skill global (helper) antes da versão do repo — sem impacto.
- `ses_0212` — 1 todo in_progress + 3 pending nunca atualizados (card-399); título "Casual greeting", $0.38 (pré-fix #440/#423).

### Limitações
- Timestamps do board não expostos via `gh project item-list`.
- Evidência de arraste/homologação não verificável via API (só comentários).

---

## 2026-08-11 — Auditoria release 2026-08-11 (cards 463, 464, 456, 457, 458) (/kaizen release)

- **Escopo**: release 2026-08-11 — cards 463, 464, 456, 457, 458 (merge main `412ed9ad`/`5619c22a`, deploy PROD validado).
- **Fonte**: board Project 1 (184 itens), PRs 465-479 + checks, `scripts/release-guard audit`, `openspec validate --all` (131/131), 35 sessões opencode na janela 08-09..08-12 (`~/.local/share/opencode/opencode.db`, mode=ro), curl PROD.
- **Métricas**: pacote 5/5 com 1 comentário Done cada; **zero duplicação** (dedupe #456 funcionou — cards 456/457/458 postados pós-merge do helper, 463/464 pré-merge, sem duplicatas); CI 15/15 runs success; 0 branches órfãs/worktrees/stashes pós-closeout; 4 changes ativas = pacote (archive pendente no closeout); custo de sessão do pacote ≈ $0.70 (vs $2.50 da release anterior, ~20× menor).

### Achados
- F-1 [recorrência, P1] Card #195 "Backup de ambiente" preso em Em Refinamento desde 05-12 (3ª auditoria reportando o mesmo card — estava em Todo na 08-09, agora Em Refinamento). Proposta: triagem + aviso de idade por coluna no guard audit. Esforço S.
- F-2 [recorrência, P1] 5/5 cards do pacote em Homologado sem o comentário padrão "Homologado por Alan na develop." (mesma lacuna F-5 da auditoria 08-09; transição por arraste/chat não passa pelo helper). Proposta: guard post com RELEASE_CARDS exige comentário de homologação (warn audit / blocker post) + post retroativo em dry-run. Esforço S.
- **Saneamento F-2 (card #480, 2026-08-13):** dry-run validado e comentário canônico postado exatamente uma vez nos cards [#456](https://github.com/oalansilva/crypto/issues/456#issuecomment-5287148541), [#457](https://github.com/oalansilva/crypto/issues/457#issuecomment-5287148517), [#458](https://github.com/oalansilva/crypto/issues/458#issuecomment-5287148509), [#463](https://github.com/oalansilva/crypto/issues/463#issuecomment-5287148552) e [#464](https://github.com/oalansilva/crypto/issues/464#issuecomment-5287148514), usando a evidência da release/merge `412ed9ad`; consulta posterior contou `1` ocorrência por card. O `release-guard` passou a validar o pacote informado em `RELEASE_CARDS`: warning em `audit`, blocker em `post`, com consulta fail-closed e dedupe numérico dos IDs.
- F-3 [minor, P2] Título board divergente da issue no #463 (rename pós-Done; Title não editável via API Projects v2; nota postada sem aprovação explícita). Proposta: regra de nota de divergência + warn no guard. Esforço S.
- F-4 [info, P2] Branches do pacote deletadas antes do movimento para Pronto (closeout técnico precede etapa kaizen→Pronto). Proposta: documentar ordem canônica no AGENTS.md. Esforço S.
- F-5 [info, P2] `main` local desatualizado pós-release (comparação oficial por origin correta). Proposta: passo de atualização de main local no closeout. Esforço S.
- F-6 [info, P2] Sessão paralela swing trade fora do pacote (kimi-k3, $2.44) — validar se foi escolha de Alan; herança interna consistente. Esforço S.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (a criar) — guard exige evidência de homologação no closeout + post retroativo | P1 | F-2 | Em Refinamento |
| (a criar) — triagem de cards presos por coluna + alerta de idade no guard | P1 | F-1 | Em Refinamento |
| (a criar) — divergência board/issue em rename pós-Done exige nota + warn | P2 | F-3 | Em Refinamento |

### Backlog kaizen (releases seguintes)
- F-4: ordem canônica de deleção de branches (doc AGENTS.md).
- F-5: atualização de `main` local no closeout (guard post warn).
- F-6: validar modelo padrão de sessão (kimi-k3 vs deepseek-v4-flash).

### Trechos de sessão (evidência local)
- `ses_013f` — 1 erro isolado de tool (JSON parse em heredoc), sem repetição; demais sessões do pacote 6/6, 7/7, 7/7 todos completed.
- Dedupe #456: cards 456/457/458 com comentário único "Implementação concluída" formato "Commit/merge: PR N (sha)" pós-merge do helper; 463/464 pré-merge sem duplicata.

### Limitações
- Timestamps por coluna não expostos via `gh project item-list` (usado updatedAt global via GraphQL).
- Evidência de arraste/homologação não verificável via API (só comentários) — motiva F-2.

## 2026-08-12 — Triagem do card #195 (card #481 kaizen)

- **Ação**: triagem do #195 "Backup de ambiente" concluída — decisão **Cancelado** (estado já aplicado no board em 11/08; nota formal registrada no card em 12/08: https://github.com/oalansilva/crypto/issues/195#issuecomment-5272103735).
- **Motivo**: escopo de backup de ambiente (openclaw, skills, apps, banco) coberto por operação do ambiente Oracle (snapshots/backups de infra DEV/PROD); card sem dono operacional ativo e preso há 3 auditorias kaizen.
- **Implementado (card #481)**: `release-guard audit` ganhou bloco `card_age_inventory` — inventário de cards por coluna com idade em dias (GraphQL `updatedAt` do item), warn informativo para >30 dias (default, configurável via `CARD_AGE_THRESHOLD_DAYS`), limite por coluna (`CARD_AGE_MAX_PER_COLUMN`, default 5), paginação até 20 páginas, falha de obtenção como warn sem interromper. Somente em `audit`; pre/post inalterados.

## 2026-08-17 — Cards #530/#531 (kaizen UI do #469)

- **Ação**: regras de apply/verify após o #469 ter marcado tasks de UI `[x]` sem código e ter implementado a Discovery pelo contrato de API em vez do protótipo aprovado.
- **#530**: `/opsx:apply` com `UI impact: affected` carrega o protótipo aprovado como spec de layout; API não é spec de UI.
- **#531**: `/opsx:verify` e Code Review exigem evidência por task de UI contra o protótipo; Playwright `[ ]` bloqueia Done. Skill `openspec-verify-change` e `opsx-verify.md` passam a tratar `[x]` sem implementação como CRITICAL.
- **Evidência base**: PR #528 / card #469 — tasks 6.2–6.10 `[x]` sem implementação; 7.8/7.9 `[ ]` em Done.

## 2026-08-17 — Kaizen release (release 2026-08-17, cards 469/502/503/504/516/517/518/562)

- **Release/card**: 2026-08-17 — cards 469, 502, 503, 504, 516, 517, 518, 562 (Homologado → Pronto após deploy PROD).
- **Fontes consultadas**: board Project 1, git/worktrees/stash + `release-guard pre` PASS, `openspec validate --all` 148/148, PR #564, transcripts Cursor desta sessão, CI push/PR no SHA `f4b89208`.
- **Sessões analisadas**: sessão Cursor do lote (cutover #562, cancelamento #550/#559, isolamento #549, deploy PROD). Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: pacote já Homologado na abertura do lote; closeout nesta sessão até PROD `91f5620e`.

### Métricas
- **Board**: pacote 8 Homologado; 2 Cancelados no mesmo dia (#550/#559) por conflito com #562; #549 em Em Refinamento isolado.
- **Git**: worktrees extras e WIP do #469/OpenSpec do #549 bloqueariam o `pre`; isolados em `card-549-unify-strategy-title-description` e `card-469-idempotency-normalization-wip`.
- **CI**: e2e da *push* em `develop` falhou (timeout em `walkforward-prototype-check` contra URL viva DEV); e2e do PR #564 verde; rerun da push passou depois do protótipo 200 em DEV. `qa-gate` skip no PR para `main` é regra do workflow (`base_ref == develop`).
- **OpenSpec**: archive do pacote + leftovers Pronto/Cancelado; skip-specs em deltas incompatíveis; spec `cursor-harness` promovida no closeout.

### Achados
- F-1 [major] E2E funcional `walkforward-prototype-check.spec.mjs` navega `https://dev.criptofarol.com.br/prototypes/...` (não o preview do CI). Push harness-only (#562) falhou 30s no seletor enquanto DEV reconstruía. Correção: apontar o spec ao servidor Playwright local/`preview` do job, não à URL DEV. Esforço S | P0.
- F-2 [major] 8 cards Homologados sem comentário canônico até o closeout (helper postou retroativo). Correção: o arraste para Homologado deve disparar o helper no mesmo turno. Esforço S | P1.
- F-3 [minor] `gh project item-list` ainda estoura GraphQL no meio do lote (remaining 89). Correção: listagens de closeout sem `content.body`. Esforço S | P1.

### Padrões recorrentes
- E2E acoplado a DEV vivo | 1 ocorrência nesta release (candidato a regra se repetir) | promoção: spec Playwright local
- Homologado sem comentário canônico | recorrência vs #480/#518 | helper existe, falta o turno do arraste

### Cards kaizen propostos (máx. 3; não criados neste closeout — Alan aprova)
- P0: desacoplar e2e de protótipo da URL DEV (F-1)
- P1: comentário de homologação no mesmo turno do arraste (F-2)
- P1: item-list do board sem body no closeout (F-3)

## 2026-08-17 — Kaizen release (lote 2, cards 529/530/531/553/554/566/567/568)

- **Release/card**: 2026-08-17 lote 2 — cards 529, 530, 531, 553, 554, 566, 567, 568 (Homologado → Pronto após deploy PROD).
- **Fontes consultadas**: board Project 1, git/worktrees/stash + `release-guard pre` PASS / `audit` PASS, `openspec validate --all` 143/143 (código) e 142/142 (archive), PR #578, transcripts Cursor (`0c0d840f` implementação; `0b02d24f` closeout), CI do PR #578.
- **Sessões analisadas**: sessão de implementação dos 8 cards (worktrees) e sessão de closeout desta release. Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: pacote já Homologado na abertura do lote; closeout até PROD `2261ad56`. F-1 do lote 1 (e2e DEV vivo) entrou neste pacote como #568 e foi publicado.

### Métricas
- **Board**: 8 Homologado no lote; fora: #569 Aprovação de Design, 2 Em Refinamento (#549 e gerador de templates).
- **Git**: 9 worktrees extras bloqueavam `pre`; 8 mergeadas removidas; WIP do #569 commitado em `059f6f38` e ref local apagada. Stash 0.
- **CI**: PR #578 verde (e2e 4m49s); `qa-gate` skip no PR para `main`.
- **OpenSpec**: 8 changes arquivadas; 7 specs novas; skip `02-agent-chat-favorites.md` (já Hermes).
- **PROD**: installer Discovery + dispatcher/Celery active; health 200; bundle `index-DbfcRxXg.js`.

### Achados
- F-1 [major] Homologado sem comentário canônico nos 8 cards até o closeout (helper retroativo). Recidiva do F-2 do lote 1 no mesmo dia. Esforço S | P1.
- F-2 [major] `pre` trata doc canônica do dia como PR documental e exige `PROD_DEPLOY_EVIDENCE`; o segundo pacote reusou a evidência `91f5620e` do lote 1 para abrir o PR de código #578. Esforço M | P1.
- F-3 [minor] Extra worktree e branch local in-flight (#569) falham o `pre` sem `PRESERVED_BRANCHES` (só vale em post/audit). Esforço S | P2.

### Padrões recorrentes
- Homologado sem comentário canônico | 2 ocorrências no mesmo dia (lotes 1 e 2) | promoção: helper no turno do arraste
- E2E acoplado a DEV vivo | corrigido neste lote (#568)

### Trechos de sessão (evidência local)
- `0c0d840f` — implementação sequencial 568→554→553→566→529→530→531→567 em worktrees.
- `0b02d24f` — closeout: `git branch -D card-569-code-review-bugbot` após push `059f6f38` para o `pre` passar.

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #579 — comentário Homologado no mesmo turno do arraste | P1 | F-1 (recidiva lote 1 F-2) | Em Refinamento |
| #580 — segundo pacote no mesmo dia vs doc canônica no pre | P1 | F-2 | Em Refinamento |
| #581 — worktree extra / branch in-flight no pre | P2 | F-3 | Em Refinamento |

## 2026-08-17 — Kaizen release (lote 3, cards 585/569/581/579/580)

- **Release/card**: 2026-08-17 lote 3 — cards 585, 569, 581, 579, 580 (Homologado → Pronto após deploy PROD `20820d05`).
- **Fontes consultadas**: board Project 1 (GraphQL pontual; `gh project item-list` falhou com `unknown owner type`), git/worktrees/stash + `release-guard pre` PASS, `openspec validate --all` 143/143, PRs #590/#591/#592, transcripts Cursor desta sessão, CI REST `check-runs` (watcher `gh pr checks --watch` 503).
- **Sessões analisadas**: sessão de implementação 585→569→581→579→580 e sessão de closeout. Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: os 5 foram Done técnico no turno anterior; Alan homologou em lote no chat e pediu a release.

### Métricas
- **Board**: 5 Homologado no lote; `#584` WIP preservado fora do pacote.
- **Git**: worktrees extras dos 5 cards removidas no `pre`; `#584` dirty classificado via `PRESERVED_BRANCHES`. Stash 0.
- **CI**: PR #592 verde; `qa-gate` skip no PR para `main`. Watcher GraphQL 503; evidência via REST check-runs.
- **OpenSpec**: 5 changes arquivadas (`--skip-specs`); 143/143.
- **PROD**: source `20820d05`; health 200; bundle inalterado (`index-DbfcRxXg.js`).

### Achados
- F-1 [major] `gh project item-list` e `gh pr checks --watch` falharam com HTTP 503 / `unknown owner type` no closeout; o fluxo só avançou com REST (`gh api` pulls/check-runs). Recidiva de fricção GraphQL (lote 1 F-3 / #509). Esforço S | P1.
- F-2 [minor] helper `post-card-evidence-comment.sh --transition homologado` deu DEDUPE falso em #579 porque o comentário de Done citava o marcador na prosa do card. O `pre` passou (o marcador estava no issue). Esforço S | P2.
- F-3 [minor] worktrees locais das branches squashadas #569/#581 não foram detectadas como mergeadas no `pre` (`git cherry`); 579/580/585 sim. Remoção das worktrees desbloqueou. Esforço S | P2.

### Padrões recorrentes
- Homologado sem comentário canônico | corrigido neste lote (#579); helper no turno do arraste/chat
- Segundo pacote no mesmo dia herda evidência | corrigido neste lote (#580); `pre` PASS sem reuso de `2261ad56`
- GraphQL 503 / item-list no closeout | 2+ ocorrências no dia | promoção: closeout REST-first

### Trechos de sessão (evidência local)
- Closeout: `unknown owner type` em `gh project item-list 1 --owner oalansilva`.
- Helper #579: `DEDUPE: card #579 already has a homologado evidence comment with commit ref 35be2c00` no comentário de Done.

### Cards kaizen propostos (máx. 3; não criados neste closeout — Alan aprova)
- P1: closeout do board/CI via REST quando GraphQL 503 (F-1)
- P2: DEDUPE do helper Homologado só no início do body (F-2)
- P2: `pre` tratar squash-equivalent de worktree extra como mergeada (F-3)

## 2026-08-14 — Kaizen release (release 2026-08-14, cards 470/480/481/482/489/491/509)

- **Ação**: auditoria kaizen pós-release concluída (read-only). F-1 a F-8 registrados abaixo.
- **F-1 (P0)**: rate limit GraphQL como evento central do closeout — guard legado consumia ~4.900 pontos/execução (`gh project item-list --limit 500` paginado); reset de ~1h; nasceu o bug #509. Medição pós-fix: **204 pontos** por execução (item-list 500 + pr list 100), delta ~24x menor. Change `card-509-release-guard-graphql-budget` concluída (tasks 5.1–5.4) e **arquivada** em 2026-08-14 com sync de spec `release-worktree-hygiene`; `openspec validate --all` 137/137.
- **F-2 (P1)**: check de changes OpenSpec terminais do guard cego para nomes sem id de card e in-progress em card terminal → card kaizen proposto.
- **F-3 (P1)**: doc de release fragmentada em 6 PRs + PR de DAG #515; ordem canônica proposta (deploy → doc única sem placeholder → 1 PR).
- **F-4 (P2)**: 8 warns de título board/issue sem nota (#469/#472 batch do #470); notas postadas apenas em #470/#491.
- **F-5 (P2)**: frontier como sessão principal na transição do #491 (~$4.5, pré-regra formal); títulos genéricos em sessões caras.
- **F-6 (P1)**: `/kaizen release` executado após `Pronto` com spawn vazio (0 messages) — kaizen-log sem entrada até esta edição; ordem canônica como gate proposto.
- **F-7 (P2)**: 17 branches da release pendentes de deleção; `main` local stale (recorrência da auditoria 08-11).
- **F-8 (P2)**: 3 todos abertos em sessão do #491; erros isolados de tool (webfetch 404, read not found) sem loop.
- **Cards kaizen criados**: 3 (P0 bug #509 follow-up; P1 bug check changes terminais; P1 story ordem canônica de fechamento), todos em `Status=Em Refinamento`.
- **Trechos de sessão (evidência local)**: `ses_00240169` — "Rate limit GraphQL zerou (0/5000, reset em ~57min) — o guard post consome ~4900 pontos por execução"; guard post com RELEASE_CARDS classificou branches como "preserved (card in flight; not deleted)" e o post passou (caso fail-open residual). `ses_000d79ef` — spawn kaizen com 0 messages/0 parts.
