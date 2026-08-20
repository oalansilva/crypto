## Context

Card [#611](https://github.com/oalansilva/crypto/issues/611), filho 3/5 do epic [#608](https://github.com/oalansilva/crypto/issues/608). Lote 1: yaml (#609, Pronto) → resolver (#610, em `develop` `d9dd3706`) → Guard Write. Absorve o hook do [#606](https://github.com/oalansilva/crypto/issues/606) **Cancelado**: o Guard **compila** `.cursor/process-fsm.yaml` + `evaluate()`; não é um `if` de coluna.

Hoje `Write`/`StrReplace` de produto passam sempre. Replay: sessão `b6a71170` escreveu `backend/` com `q_git=develop`. Prompt/harness.mdc não bastam para o Auto.

**UI impact: none.** Harness/hooks. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Deny `write_produto` antes do side-effect via `preToolUse` (e `beforeShellExecution` só para o mesmo deny em writes via shell).
- Compilar yaml + resolver: path → glob-first → `(q, bound_card, q_git)` → `evaluate(write_produto)` **só** se `product_globs`.
- I3: `Pronto para Dev` ⇒ deny produto até Status já ser Em desenvolvimento.
- Fail-closed assimétrico (campo do yaml): deny produto se `q` ilegível; allow `design_globs` se `q_git` já é `card-<id>-*`.
- Fixtures stdin JSON sem GitHub; job `process-fsm` existente fica verde.
- Preservar `.cursor/hooks/impeccable.sh`.

**Non-Goals:**

- `process_event` / mover board / `git commit` / `./restart` (#612).
- Paging `sessionStart` / encolher `AGENTS.md` (#613).
- Código de produto; novas colunas; reabrir #606 isolado.
- Parser geral de shell (só mutation tokens + path de produto).

## Decisions

1. **Um módulo `scripts/process-fsm/guard.py` + adapter `.cursor/hooks/process-fsm-guard.sh`.**  
   Alternativa: só bash, ou hook inline no JSON. Python reusa `load_fsm` / `evaluate` / `resolve` já em `develop`. O adapter lê stdin e chama o Python do repo (`backend/.venv/bin/python` se existir, senão `python3`) em `scripts/process-fsm/guard.py`. Imprime JSON Cursor (`permission`, `agent_message`). Se o interpreter/PyYAML falhar: fallback bash **assimétrico** (Decision 12) — não derruba Design.

2. **Pipeline: glob primeiro; `evaluate(write_produto)` só para `product_globs`.**  
   Alternativa: mandar todo Write a `evaluate(write_produto)`. Isso **nega OpenSpec/protótipo em Design** (`i1_write_allowed` é falso fora de Em desenvolvimento/Code Review) e mata o fluxo que o fail-closed tenta preservar. `evaluate()` é cego a globs e **não lê** `fail_closed_asymmetric`. Ordem obrigatória:
   1. parse envelope Cursor → path (ou mutation+path no shell);
   2. `resolve(cwd, path)` → `q_git`, `bound_card`;
   3. classificar glob;
   4. se **não** é `product_globs`: `allow` (design_globs em Design, harness, docs, `.cursor/`); no fail-closed (`q` ilegível) o allow de design ainda exige `q_git=card-<id>-*`;
   5. se **é** `product_globs`: montar `EvalContext(event=write_produto)` e **só então** `evaluate()`.  
   `if status not in (...)` avulso continua proibido (#606). I1/I3/illegal_edges continuam na tabela, aplicadas **somente** a path de produto.

3. **Path do tool, não cwd da sessão.**  
   `Write`/`StrReplace`/`Delete`: `tool_input.path` (aliases `file_path`, `file`). `EditNotebook`: `target_notebook`. Relativo ao `cwd` do payload. Em seguida `resolve(cwd, path, issue_id=bound from path, status=injected_or_live)`.

4. **Globs = prefixo dos yaml `product_globs` / `design_globs`.**  
   `backend/**` ⇒ `backend/`; `frontend/src/**` ⇒ `frontend/src/`; design ⇒ `openspec/changes/` e `frontend/public/prototypes/`. Path fora dos dois conjuntos ⇒ `allow` (não é P0; harness/`docs/`/`.cursor/` continuam editáveis). Testes de produto sob `backend/` entram no deny.

5. **`q` nos unitários é injetado** (`status` no JSON), como o resolver. Sem `gh`.  
   Live: se `status` não vier no stdin, um `status_provider` pontual (GraphQL issue→campo Status do Project 1, timeout curto, **sem** `item-list` paginado). Falha/timeout/`bound_card=⊥` ⇒ `q` ilegível ⇒ Decision 6. O provider é injetável; pytest nunca o chama.

6. **Fail-closed assimétrico (não é o `failClosed` do Cursor).**  
   `q` ilegível + `product_globs` ⇒ deny. `q` ilegível + `design_globs` + `q_git` casa `card-<id>-*` ⇒ allow (Design não morre com `gh` down). `q` ilegível + resto ⇒ allow.

7. **Cursor `failClosed: true` só no `preToolUse` da família Write.**  
   Alternativa: `failClosed` também em `beforeShellExecution`. Há bug conhecido de spawn (`MainThreadShellExec`) que trava o Shell se fail-closed. Residual: se o hook de shell não nascer, write via `cat > backend/` pode passar — aceito P2; P0 é o tool `Write` da sessão `b6a71170`.

8. **`beforeShellExecution` classifica mutation, não todo comando.**  
   Mutation tokens: `>`, `>>`, `tee `, `sed -i`, `perl -i`, `cp `/`mv `/`install ` com destino em `product_globs`. Sem token ⇒ allow (`pytest backend/`, `ruff`, `git status`). `git commit` / `push` / `./restart` **não** são write de arquivo neste card.

9. **Composição no `hooks.json`:** acrescentar entradas; não editar `impeccable.sh`. Matcher `preToolUse`: `Write|StrReplace|Delete|EditNotebook`.

10. **Mensagem de deny** cita invariante/aresta e a coluna/`q_git`. `evaluate()` em Pronto para Dev devolve `reason=I1` (não há `illegal_edge` I3 no yaml #609, de propósito). O Guard **mapeia** `reason=I1` + `state=Pronto para Dev` → `agent_message` cita **I3**, sem alterar o yaml.

11. **Testes em `scripts/process-fsm/test_guard.py`.** Fixtures = **envelope Cursor**, não dict interno:
    - `preToolUse`: `tool_name` + `tool_input.path|file_path|file|target_notebook` + `cwd` (+ `status` injetado);
    - `beforeShellExecution`: `command` + `cwd` (+ `status` injetado).  
    Casos mínimos: cada coluna deny de **produto** + `develop`/`main`/unbound; allow Em desenvolvimento e Code Review com binding; **Write `openspec/changes/...` em Design ⇒ allow**; replay `b6a71170`; fail-closed produto vs design; pytest allow vs redirect deny. CI já roda `pytest scripts/process-fsm`.

12. **Fallback do adapter se Python/PyYAML quebrar.** Prefix-match bash: path `backend/` ou `frontend/src/` ⇒ deny; path `openspec/changes/` ou `frontend/public/prototypes/` + branch `card-<id>-*` ⇒ allow; resto ⇒ allow. Evita que `failClosed: true` no `preToolUse` mate Design quando o venv não tem PyYAML (CI instala pyyaml à parte do python3 do host).

## Risks / Trade-offs

- [Hook crash no `preToolUse`] → `failClosed: true` deny a ferramenta se o adapter **não** devolver JSON. Adapter + fallback bash (Decision 12) devem sempre imprimir JSON válido (deny produto / allow design).
- [Shell failClosed trava sessão] → Decision 7: failClosed só na família Write.
- [Python ofuscado grava backend] → residual P2; lote 1 não é parser de AST.
- [Status live precisa de `gh`] → unitário injetado; live timeout ⇒ deny produto (I1), não allow silencioso.
- [Auto em `develop` edita `scripts/` ou `AGENTS.md`] → fora de `product_globs`; não é aceite deste card.
- [Cwd≠path] → resolver #610 já devolve `bound_card=⊥` ⇒ deny.

## Migration Plan

Aditivo. Rollback = reverter `hooks.json` + `guard.py` + adapter (Impeccable permanece). Sem migration de banco.

## Open Questions

Nenhuma bloqueante. Live GraphQL é detalhe do `status_provider`; contrato = injetável e ausente nos testes.

## UI impact

**none** — harness/hooks. Nenhuma tela de produto nova ou alterada.

## Prototype

N/A — `UI impact: none`. Guard é policy de ferramenta, não superfície visual.

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

Recrítica isolada (read-only) após P0/P1. Fontes: `proposal.md`, `design.md` (Decision 2 glob-first, 11 envelope Cursor, 12 fallback), `tasks.md`, `specs/process-fsm-guard/spec.md`, `specs/cursor-harness/spec.md`. Card #611, change `card-611-process-fsm-guard`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Primeira crítica (inherit, não editar): P0 (Write de OpenSpec passaria por `evaluate(write_produto)` em Design) + P1 (stdin sem envelope Cursor; `beforeShellExecution` MAY vs SHALL; interpreter/`failClosed` matando Design) → **BLOCKED**.

Correções no escopo: glob-first + cenário Design OpenSpec allow; fixtures = envelope Cursor; shell SHALL nos dois specs; fallback bash assimétrico se Python/PyYAML falhar.

Recrítica isolada inherit: P0/P1 fechados. P2 aceitos: I3 só na `agent_message`; `failClosed` ausente no shell; ofuscação `python -c`; Em Refinamento coberto pelo catch-all I1.

- **Escopo:** Guard Write compila yaml #609 + resolver #610; `process_event` (#612), paging (#613) e produto fora. Sem superfície visual nova/alterada.
- **Produto / processo:** deny produto nas colunas do aceite + `develop`/`main`/unbound; allow Em desenvolvimento/Code Review com binding; replay `b6a71170`; I3 duas fases; Design não morre com `gh` down nem com PyYAML ausente.
- **Operação:** `failClosed: true` só na família Write; shell sem failClosed (bug de spawn, P2); unitários sem GitHub.

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica após P0/P1). Prototype N/A. Impeccable N/A.
