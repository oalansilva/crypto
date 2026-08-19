## Context

Card [#609](https://github.com/oalansilva/crypto/issues/609), filho 1/5 do epic [#608](https://github.com/oalansilva/crypto/issues/608). Lote 1: yaml → resolver (#610) → Guard (#611).

Hoje a δ do processo (T0–T17, I1–I9, `request_implement` ∉ δ) vive no body do #608. Nenhum runtime lê isso. Este card transforma a tabela em `.cursor/process-fsm.yaml` + validador + pytest, **sem** ligar hook Cursor.

**UI impact: none.** Harness/processo. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Uma fonte compilável da EFSM do #608 (estados, transições, tools, eventos, globs, invariantes).
- Validação determinística sem GitHub e sem hook.
- Contrato estável para #610/#611 consumirem o mesmo arquivo.

**Non-Goals:**

- `preToolUse` / `beforeShellExecution` (#611).
- Resolver de worktree/`bound_card` (#610) — este card só declara os campos; não resolve git.
- `process_event` (#612), paging `sessionStart` (#613).
- Código de produto, novas colunas, reabrir #606.
- Enumerar o produto `Q_board × Q_git × Q_spec`.

## Decisions

1. **Um yaml versionado em `.cursor/process-fsm.yaml`**  
   Alternativa: JSON Schema solto ou Python dict. Yaml é o artefato que o Guard vai *compilar* (#611); humanos do board já leem Markdown. Schema do validador rejeita yaml incompleto.

2. **Validador em `scripts/process-fsm/` + pytest, sem I/O de rede**  
   Alternativa: testes só no backend pytest misturados a produto. Isolar evita acoplar harness a FastAPI/PostgreSQL. Fixtures = stdin-like dicts (de, evento, ator, guarda, esperado allow/deny ou next state).

3. **`request_implement` ∈ `illegal_events`, nunca em `transitions[]`.**  
   `write_produto` **não** é irmão disso. É ação Moore (`enabled_tools` / I1): allow só se `q ∈ {Em desenvolvimento, Code Review}` ∧ `q_git=card-<id>` ∧ `bound_card=id` ∧ path desse worktree. Fora disso, `illegal_edges` (ex.: Todo+Write, Done+Write, develop+Write, unbound+Write) ⇒ `reject`. Meter `write_produto` em `illegal_events` global quebraria I1 e o #611.

4. **Duas chaves no yaml, nomes fixos:** `illegal_events` (Σ fora de δ: `request_implement`, `pular_coluna`, `Agent.aprovar_design`) e `illegal_edges` (tuplas `(state, event[, actor])` que reject).

5. **Encoding da tabela**
   - T0: `from: null` (criação).
   - T2: `from: Vivo`; o validador **expande** para todos os estados não terminais.
   - T17: **duas** rows (Pronto para Dev → Design; Em desenvolvimento → Design), mesmo evento `invalidar_aprovacao`.
   - T16: guarda inclui `M_lote`; detalhe do lote fora deste card.

6. **`context_file` neste card são stubs** (≤20 linhas inline ou paths placeholder). Paging real = #613.

7. **Globs pinados (epic #608 §3.3):** `product_globs`: `backend/**`, `frontend/src/**` (+ testes de produto sob esses trees). `design_globs`: `openspec/changes/**`, `frontend/public/prototypes/**`.

8. **Não copiar T0–T17 para `AGENTS.md`.** Yaml é a fonte compilável; #608 permanece spec humana.

9. **Fail-closed deste card = pytest.** Não instala hook (crítica #606). Campo `fail_closed_asymmetric: true` no yaml documenta para o #611: deny produto se Status ilegível; allow `design_globs` se a branch do path já é `card-<id>-*`.

10. **Testes em `scripts/process-fsm/`** (`test_*.py`). Apply MUST deixar `pytest scripts/process-fsm -q` verde; ligar esse comando no job de testes do CI (sem GitHub). Sem path de teste, o aceite “PR não mergeia se divergir” é falso.

**Matriz T0–T17 (from, event, actor, to)** — pin semântico; o yaml MUST copiar isto, não inventar Σ:

| # | from | event | actor | to |
| --- | --- | --- | --- | --- |
| T0 | null | criar_card | Agent\|Alan | Em Refinamento |
| T1 | Em Refinamento | priorizar | Alan | Todo |
| T2 | Vivo | cancelar | Alan | Cancelado |
| T3 | Todo | iniciar_design | Agent | Design |
| T4 | Design | recriticar | Agent | Design |
| T5 | Design | submeter_design | Agent | Aprovação de Design |
| T6 | Aprovação de Design | devolver_design | Alan | Design |
| T7 | Aprovação de Design | aprovar_design | Alan | Pronto para Dev |
| T8 | Pronto para Dev | iniciar_apply | Agent | Em desenvolvimento |
| T9 | Em desenvolvimento | pedir_review | Agent | Code Review |
| T10 | Code Review | achar_bloqueante | Agent | Em desenvolvimento |
| T11 | Code Review | aceitar_sha | Agent | QA |
| T12 | QA | rerun_infra | Agent | QA |
| T13 | QA | falha_codigo | CI\|Agent | Em desenvolvimento |
| T14 | QA | integrar_develop | Agent | Done |
| T15 | Done | homologar | Alan | Homologado |
| T16 | Homologado | fechar_release | Alan | Pronto |
| T17a | Pronto para Dev | invalidar_aprovacao | Guard | Design |
| T17b | Em desenvolvimento | invalidar_aprovacao | Guard | Design |

Σ legal = eventos desta matriz. Determinismo: T4/T5 (`G_design`), T10/T11 (¬T10), T12/T13/T14 (T13 ≻ T12; T14 só verde). I2: T1, T7, T15, T16.ator ⊇ Alan (não só T7).

## Risks / Trade-offs

- [Yaml e #608 divergem] → matriz neste design + validador I2 + `pytest scripts/process-fsm -q` no CI.
- [Schema cedo demais para #610/#611] → campos `enabled_tools`/`product_globs` já no yaml, mesmo sem o Guard os usar.
- [T16/`M_lote` incompleto] → T16 com guarda `M_lote`; detalhe do lote fora (#612).
- [Write legal negado] → `write_produto` nunca em `illegal_events`; só `illegal_edges` + I1.

## Migration Plan

- Aditivo. Nada para rollback além de reverter o yaml/scripts.
- #610 MUST ler este yaml de `develop` após o #609 estar integrado.

## Open Questions

Nenhuma bloqueante. Ator T1/T7/T15/T16 = Alan; Agent+T7 é aresta ilegal (fixture).

## UI impact

**none** — sem tela, rota ou componente. Prototype N/A. Impeccable N/A (justificativa: harness yaml/pytest).

## Prototype

N/A — `UI impact: none`.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none` (harness yaml/pytest; sem superfície visual).

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Recrítica isolada (read-only) após correção dos P1s. Fontes: `proposal.md`, `design.md`, `tasks.md`, `specs/process-fsm/spec.md`. Card #609, change `card-609-process-fsm-yaml`, `Status=Design`. Prototype: N/A. Impeccable: N/A (UI impact none).

### Dimensões

- **Escopo:** lote 1 yaml + validador + pytest; hook/resolver/`process_event`/paging e produto fora. Sem regressão de superfície visual.
- **Produto / processo:** δ T0–T17 pinada; `write_produto` é Moore/I1, não evento global ilegal; `request_implement` ∈ `illegal_events`.
- **Operação:** fail-closed deste card = pytest; CI `pytest scripts/process-fsm -q`; sem GitHub nos unitários.
- **UI / a11y / responsivo / estados visuais:** N/A — harness.

### P1s anteriores (fechados)

1. `write_produto` gated by I1, ausente de `illegal_events`; `illegal_edges` Todo/Done/develop/unbound — D3–D4, tasks 1.2–1.3, spec I1.
2. Matriz T0–T17 (T17a/T17b) em `design.md` + Σ legal no spec (18 eventos).
3. Validador I2: T1, T7, T15, T16.ator ⊇ Alan — task 2.2 + cenários do spec.
4. Fixtures `scripts/process-fsm/test_*.py` e task 3.3 no CI.

### Achados desta rodada

- **P0 / P1:** nenhum.
- **P2 (aceitos, não bloqueiam):** I3–I9 por id (#608 §5); `illegal_edges` mistura Q e X (`develop`/`unbound`); Gherkin sem cenário nomeado Done/develop+Write (cobertos no SHALL/3.2); allow I1 pytest só Em desenvolvimento; T4/T5 e T12–T14 são eventos distintos (determinismo = exclusividade de guarda).

### Pendências não bloqueantes

Apply copia I3–I9 e globs do Decision 7; `enabled_tools`/`context_file` stubs. Aprovação humana (`Aprovação de Design -> Pronto para Dev`) permanece de Alan.

Design Agent verdict: PASS

## Design Agent verdict

PASS — crítica isolada inherit (recrítica após P1). Prototype N/A. Impeccable N/A.
