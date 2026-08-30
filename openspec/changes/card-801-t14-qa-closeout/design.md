## Context

Card [#801](https://github.com/oalansilva/crypto/issues/801). Q1=A, Q2=A, Q3=A congeladas (não reabrir). Não reabre #632 (T14 live + dirty⇒I8) nem #729 (um chat / filhos). Não re-grelhar.

**Factos live (código em `develop` / este worktree):**

- T11: `EVENT_GUARDS["aceitar_sha"]` seta `reviewers_ok=True` só pelo nome; yaml `actions: [diff_vs_develop, push, set_status]`; `test_aceitar_sha_moves_qa` move QA sem PR. Não exige nem cria PR `q_git`→develop.
- `measure_checks_green` é bool: False para sem-PR, sem head, API erro, `qa-gate` ausente, pending, skipped, cancelled ou failure. `evaluate()` recusa com `guard:checks_green` — as causas colapsam.
- `LiveT14Runner` já levanta `T14Error("squash: no PR")` e `T14Error("sync: dirty")` (sem path no texto); `process_event` engole a excepção e devolve só `reason=I8` (sem `message`). `_payload` já aceita `message` se truthy.
- `sync_dev_source` corre só em `environments.dev.source`; porcelain não-vazio ⇒ I8, sem checkout/merge/reset.
- Guard `beforeShellExecution` existe; **não** há deny de `git checkout -b card-*` no canónico.
- Moore `context_file[QA]`: «Não mexer fonte. CI. T13 volta a Em desenvolvimento.»
- Spec viva `process-fsm-event` ainda diz «T14 stays reject live»; o archive #632 já substituiu isso. Drift para este Design.
- dsh plugin já injeta Moore (`covenant-flow:moore` ← `runPage`).

**UI impact: none.** Harness/CLI/hooks/Moore/skills. Nenhuma rota, shell, componente ou copy de produto. Sem HTML, sem `DESIGN.md`, sem Impeccable, sem Playwright visual.

## Goals / Non-Goals

**Goals:**

- T11 sem PR ⇒ reject `no_pr`, Status permanece Code Review, nenhum PR criado.
- `integrar_develop` devolve `reason` estruturado: `no_pr` | `qa-gate pending` | `qa-gate failed` | `sync: dirty`. Dirty inclui `message` com path + porcelain. I8 continua: dirty/falha de runner ⇒ permanece QA, sem checkout/merge/reset.
- Pai (Cursor) ou root/script (dsh) espera `qa-gate pending` e repete T14 no **mesmo turno**. Filho QA não chama `process_event`.
- Guard deny `git checkout -b card-*` / `git switch -c card-*` em `environments.dev.source`.
- Moore + skill: primeiro reject não é fim de turno; dsh não spawna filho QA.

**Non-Goals:**

- Reabrir #632 / #729. Medir `reviewers_ok` de verdade (card irmão, Q3=A).
- T11 criar PR; throwaway / checkout limpo que ignore dirty; `--checks-green`; T7/T15; Agent `item-edit` de Status.
- Poll/retry **dentro** de `process_event` (continua one-shot).
- Código de produto (`backend/`, `frontend/src/`). UI / HTML / `DESIGN.md`.
- Fechar à mão #792/#798. Novo evento FSM, nova coluna, dual-write da lei.

## Decisions

1. **`reason` é o token parseável; `message` é o detalhe humano.**  
   Residual da grelha. Live `_payload` já tem os dois campos; T14 só não os preenche. Operadores/scripts leem `reason`. Tokens fechados: `no_pr` | `qa-gate pending` | `qa-gate failed` | `sync: dirty`. Para `sync: dirty`, `message` MUST conter o path de `environments.dev.source` e o `git status --porcelain` (texto). Outras falhas de runner (restart, comment, squash merge) permanecem `reason=I8` com `message=str(exc)` — deixam de ser I8 mudo, sem inventar token novo. Alternativa rejeitada: só `message` e `reason=I8`/`guard:checks_green` (o pai continuaria a não ramificar). Alternativa rejeitada: `--checks-green`.

2. **Classificador estruturado; bool só para o yaml `checks_green`.**  
   Nova função no módulo `t14` (nome Apply: `classify_qa_gate`) devolve `{ok: bool, reason: str | None}`. Mapa live:
   - sem `q_git`, lista PR vazia, sem `headRefOid` → `ok=False`, `reason=no_pr`
   - `qa-gate` com `status` ≠ `completed` (queued / in_progress) → `qa-gate pending`
   - check ausente, skipped, cancelled, failure, API/JSON/timeout → `qa-gate failed`
   - `completed` + `success` → `ok=True`, `reason=None`
   `measure_checks_green` torna-se wrapper `classify.ok` (fixtures bool antigas continuam). `process_event integrar_develop`: se `checks_green` não foi injetado, chama o classificador, seta o bool, e se `evaluate()` recusar com `guard:checks_green` **substitui** `reason` pelo token classificado. Testes unitários injetam classificador ou bool; MUST NOT chamar GitHub.

3. **T11: probe de PR antes de `evaluate`; `reviewers_ok` intacto (Q3=A).**  
   `aceitar_sha` lista PR `q_git`→develop (mesmo `_pr_list_json`). Vazio ⇒ reject `reason=no_pr`, mover vazio, Status Code Review. Não cria PR. Com PR, `EVENT_GUARDS` continua a setar `reviewers_ok=True` pelo nome. Fixture `test_aceitar_sha_moves_qa` MUST injetar PR presente; fixture #792 (push sem PR) MUST ser `no_pr`. Alternativa rejeitada: T11 cria PR. Alternativa rejeitada: nova guarda yaml `has_pr` (mudaria Σ/yaml).

4. **`T14Error` deixa de ser engolido sem `message`.**  
   `except T14Error as exc`: se o texto/atributo for dirty ⇒ `reason=sync: dirty` + `message` path+porcelain; se `squash: no PR` ⇒ `reason=no_pr` (cinto; o classificador já corta antes do runner); senão `reason=I8` + `message=str(exc)`. `LiveT14Runner.sync_dev_source` MUST pôr path + porcelain no erro. Q2=A: porcelain não-vazio continua sem checkout/merge/reset/restart/move.

5. **Retry de pending é do turno, não do script δ.**  
   `process_event` não faz sleep/poll. Pai Cursor (ou root/script dsh) no mesmo turno espera o check e volta a chamar `integrar_develop`. Helper opcional em `scripts/process-fsm/` que só mede+espera+reinvoca é Apply-ok; não é evento novo. Filho QA MUST NOT `process_event`.

6. **Guard deny `checkout -b card-*` só no canónico.**  
   Em `decide()`, **antes** do early-return sem path (igual `status_item_edit`). Match: `git checkout -b card-*` ou `git switch -c card-*` (e `--track -b`) quando `cwd` ou `git -C` resolve para overlay `environments.dev.source`. Reason: `canonical_card_branch`. Allow: a mesma criação numa worktree `card-<id>-*`; `checkout` de branch existente; `git worktree add`. Fallback bash MUST deny a mesma classe. `guard.py` `decide()` é a lei (Cursor/Grok/OpenCode/dsh via `runGuard`). Sem matcher de spawn QA em `decide()` (não partir Task Cursor).

7. **Moore `context_file[QA]` é o núcleo; skill explica o como.**  
   Stub curto (paging ≤20 linhas): filho QA lê checks sem `process_event`; pai T14 no mesmo turno do verde; pending ⇒ espera e repete; `no_pr`/`sync: dirty` visíveis; T13 volta a Em desenvolvimento. dsh já recebe a página pelo plugin — isso cumpre «plugin/moore, não só skill». Skill `covenant-flow`: ramo Cursor (filho QA + pai T14) e ramo dsh (sem filho QA; PR **antes** de T11; wait qa-gate; T14). `AGENTS.md` não cresce. Stubs thin.

8. **Spec viva «T14 stays reject live» é substituída neste delta, sem reabrir #632.**  
   RENAMED do leftover #612 (igual ao archive #632) + ADDED do closeout estruturado. Yaml T14/I8/Σ intactos. O closeout atómico #632 permanece facto; este card só torna causas visíveis e fecha T11/turno.

## Risks / Trade-offs

- [Pai ignora Moore e para no primeiro reject] → skill + stub QA + fixture de regressão #798 (`sync: dirty` visível, turno não acaba). Sem novo evento.
- [Classificador vs bool injetado nos testes antigos] → bool injetado True/False continua; só o live path e fixtures novas usam o classificador. `guard:checks_green` só se o classificador estiver ausente e o bool for False.
- [Deny `checkout -b` falso positivo em worktree] → match exige path = `environments.dev.source`, não substring `card-` no cwd do worktree.
- [dsh root em source canónico] → o deny impede repetir #792; o closeout dsh corre no worktree `card-<id>-*` + `process_event` (igual Cursor).
- [Drift spec #632] → este archive fecha o leftover; não religa T14 reject permanente.

## Migration Plan

Aditivo em `process_event` / `t14` / `guard` + stub QA + skill. Rollback = reverter o módulo; T11 volta a aceitar sem PR e T14 volta a `guard:checks_green`/`I8` mudo. Sem migration de banco. Sem mudança da linha T14 do yaml.

## Open Questions

Nenhuma bloqueante. Card irmão `reviewers_ok` medido: Alan cria se quiser; este card não o abre.

## UI impact

**none** — closeout de harness (CLI, Guard, Moore, skill). Nenhuma superfície visual de produto nova, alterada ou removida. Não há ecrã, rota, token ou copy para o utilizador final.

## Prototype

N/A — `UI impact: none`. Sem HTML, sem URL navegável, sem digest de protótipo.

## Prototype Validation

N/A — não há protótipo para validar em navegador.

## Impeccable Brief

N/A — `UI impact: none`. Sem shape, folha de tokens ou `DESIGN.md`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Apply contract

Apply (só com `Status=Pronto para Dev`) lê este recorte, não o body do GitHub:

1. **T11 `no_pr`** em `process_event("aceitar_sha")`: sem PR `q_git`→develop ⇒ `reason=no_pr`, Status Code Review, mover vazio. Com PR, `reviewers_ok` continua pelo nome do evento. Atualizar `test_aceitar_sha_moves_qa` (PR presente) + fixture #792.
2. **Classificador** em `t14.py`: tokens `no_pr` | `qa-gate pending` | `qa-gate failed`; `measure_checks_green` = `ok`. `integrar_develop` substitui `guard:checks_green` pelo token. Sem `--checks-green`.
3. **T14Error visível**: dirty ⇒ `reason=sync: dirty` + `message` path+porcelain; sem mutate. Outro runner fail ⇒ `I8` + `message`. Fixture #798.
4. **Guard** `canonical_card_branch`: deny `checkout -b`/`switch -c` `card-*` no source canónico; fallback bash igual. Pytest sem GitHub.
5. **`context_file[QA]`** no yaml (núcleo) + `covenant-flow` (Cursor: filho QA + pai T14 mesmo turno; dsh: sem filho, PR antes de T11, wait, T14). Paging ≤20 linhas. Sem dual-write T0–T17.
6. **Spec viva** `process-fsm-event`: RENAMED leftover #612; não reabrir #632/#729; não medir `reviewers_ok`.
7. **Não editar** `backend/` `frontend/src/` `DESIGN.md` `CONTEXT.md` `docs/adr/` Σ/yaml T11–T14.

**Ficheiros previstos (Apply):**

- `scripts/process-fsm/process_event.py`
- `scripts/process-fsm/t14.py`
- `scripts/process-fsm/guard.py`
- `scripts/process-fsm/test_process_event.py`
- `scripts/process-fsm/test_t14.py`
- `scripts/process-fsm/test_guard.py`
- `scripts/process-fsm/test_paging.py` (needle do stub QA, se o paging o citar)
- `.cursor/process-fsm.yaml` (`context_file[QA]` apenas)
- `.cursor/hooks/process-fsm-guard.sh`
- `.cursor/skills/covenant-flow/SKILL.md`

Helper opcional: `scripts/process-fsm/` wait+reinvoke T14 (não é evento). Stubs `.dsh/skills/*` / `.grok/skills/*` só se o gerador o exigir; corpo thin.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2 accepted-residual:** cenários do Guard só cobrem `cwd` = source; live `git -C <canónico> checkout -b card-*` a partir de worktree → `paths=[]` → allow. Apply MUST golden `git -C`. Aliases `-B`/`--create`. Fallback bash allow sem path. Pai que ignora Moore. MAY vs SHALL do filho QA Cursor. Wrapper JSON não pode falhar `qa-gate` success por linha má.
- **P3 accepted-residual:** runner omitido = I8 sem `message`. `checkout -B` / `switch -C` fora da lista. `RecordingT14Runner("sync_dev_source")` ≠ `sync: dirty`. `_pr_list_json` + `json.loads` sem catch. Paging ≤20. CLI validate. #632/#729 OPEN no GitHub (não `gh issue close`).
- **Prototype:** N/A — `UI impact: none`; aceite = T11 `no_pr` + T14 causas visíveis + deny checkout no canónico; sem HTML.
- **Snapshot Impeccable:** `.impeccable/critique/801-card-801-t14-qa-closeout-A.md` e `…-B.md` (r1). Apply/Code Review não lêem. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS** — zero P0/P1; A e B isolados; sem superfície visual por classificar; browser N/A justificado.
