## Context

Card [#612](https://github.com/oalansilva/crypto/issues/612), filho 4/5 do epic [#608](https://github.com/oalansilva/crypto/issues/608). Lote 2: yaml (#609), resolver (#610) e Guard Write (#611) já estão em `develop`/`Pronto`. O Agent ainda move coluna com `gh project item-edit` solto; chat vira T7. O Guard barra Write de produto, não barra transições humanas nem `request_implement`.

**UI impact: none.** Harness/CLI. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- CLI SMAG `process_event <evento>`: valida δ (ator, guarda, `bound_card`) e só então move Status.
- Agent ⇏ T1 / T7 / T15 / T16; `aprovar_design` pelo Agent = reject.
- T8 duas fases: `iniciar_apply` move Status primeiro; **não** libera Write enquanto `q` ainda é Pronto para Dev.
- T17 quando `digest` muda (I4): volta a Design, não apply silencioso.
- T16: se `M_lote` não aceitar, reject + apontar `alan-workflow-ambientes` / `release-guard`.
- `request_implement` ∉ δ: reject, `q` inalterado, lista `enabled_events(q)`.
- Agent Shell não faz `item-edit` de Status; o script é a via.
- Fixtures sem GitHub; job `process-fsm` verde.

**Non-Goals:**

- Autômato completo de release / deploy PROD / `release-guard` real (T16 só o predicado stub).
- Paging `sessionStart` / encolher `AGENTS.md` (#613).
- Código de produto; `git commit` / `./restart` como gate (continuam Agent + cards existentes).
- Verificar Gist/crítica via `gh` dentro do script (T5 file-level).
- Permitir `--actor Alan` na CLI ou `actor=` na função `process_event()`.
- `PROCESS_FSM_MOVE` ou qualquer allow de Status via env.

## Decisions

1. **Um módulo `scripts/process-fsm/process_event.py` (CLI + função injetável).**  
   Alternativa: MCP tool Cursor, ou só prosa na skill. SMAG: a máquina é a ferramenta. A sessão chama `backend/.venv/bin/python scripts/process-fsm/process_event.py <evento> [--card N] [--change <slug>] [--dry-run]`. Função `process_event(...)` **não** aceita `actor=`. Actor é sempre `Agent`. Testes injetam mover, status, git e predicados de guarda — **não** ator. `--dry-run` avalia e **não** chama o mover nem grava sidecar.

2. **Actor da CLI/função é sempre `Agent`. Não existe `--actor` nem parâmetro `actor`.**  
   Alternativa: `--actor Alan` / `--from-guard`. O modelo forjaria Alan e furaria I2. T1/T7/T15/T16 rejeitam. Alan **arrasta** essas colunas no Project 1 (fora da CLI; o hook não vê o UI). `devolver_design` / `cancelar`: CLI Agent rejeita; Alan arrasta.

3. **I4 em `evaluate()`; T17 só no compile interno.**  
   Yaml T8/T9 não listam `digest_changed`. Mesmo assim `evaluate(iniciar_apply|pedir_review)` MUST, **antes** de retornar transition: se `digest_changed is True` ou `None` ⇒ `reject` `reason=I4` (não T8/T9). Fixture: `evaluate(iniciar_apply, digest_changed=true)` ≠ T8. Cenário legal T8 exige `digest_changed=false`.  
   Só depois desse reject, `process_event` **compila I4**: mede digest nos arquivos, chama `evaluate(invalidar_aprovacao, actor=Guard, digest_changed=true)` — único sítio com ator Guard, sem flag de CLI. Mover `to=Design` uma vez; nunca Em desenvolvimento / Code Review.  
   `invalidar_aprovacao` com digest inalterado: actor permanece Agent → `evaluate` reject `actor`; mover não chamado.

4. **Digest congelado no T5; sidecar imutável para o Agent.**  
   Canonical: SHA-256 de `design.md` + protótipo opcional (paths ordenados). Sidecar `openspec/changes/<change>/.design-digest` escrito **somente** pelo script após T5 aceite (`open()` no processo Python — o hook Cursor não vê). `--dry-run` não grava. Yaml T7 `freeze_digest` = **N/A neste card** (Alan arrasta T7; o freeze útil é o sidecar do T5).  
   Guard deny `Write`/`StrReplace`/`Delete` e Shell mutante cujo path termina em `.design-digest` (qualquer `q`). Patch de `design.md`/protótipo depois do T7 continua possível; I4 no apply vira T17 — o furo era **forjar o hex**. Ausência do sidecar em Pronto para Dev / Em desenvolvimento ⇒ `digest_changed=true`. `G_design` mínimo = arquivos OpenSpec presentes (Gist/crítica = dever do Agent, P2).

5. **`evaluate()` honra `guard:` + deriva `q_git_card` de `q_git`.**  
   Predicados: `q_git_card` = `CARD_GIT_RE.match(q_git)` (não bool solto desencontrado de `q_git`); `digest_changed`; `M_lote`; `G_design`; `checks_green`; exclusive-group T10–T13 (Decision 15). Guarda no yaml + predicado `False`/`None` ⇒ reject fail-closed `guard:<nome>`. Guarda ausente no yaml ⇒ não exige o predicado. `write_produto` ignora essas guardas (I1). Testes legais T5/T8/T16/T17 passam predicados explícitos (`digest_changed=false` no T8 legal).

6. **T8 não devolve permissão de Write.**  
   `process_event iniciar_apply` com δ ok: mover `set_status(Em desenvolvimento)` e stdout JSON `{result: transition, id: T8, to: Em desenvolvimento}`. Não há campo `write: allow`. O Guard #611 continua lendo Status **live**. Fixture obrigatória: após `process_event` com mover **no-op** (status injetado ainda Pronto para Dev), `decide(Write produto)` = deny I3. Fixture complementar: depois que o fake status vira Em desenvolvimento, Write allow (reuso do Guard).

7. **`M_lote` default `false`. Toda rejeição de `fechar_release` cita a skill.**  
   Alternativa: `release-guard pre` real — fora de escopo. Live CLI (Agent) rejeita por ator; testes de `evaluate(Alan, M_lote=false)` rejeitam por guarda. **Qualquer** reject de `fechar_release` (ator ou guarda) MUST incluir `alan-workflow-ambientes` e `release-guard` na mensagem. O script **não** executa `release-guard`, deploy PROD nem `set_status(Pronto)` mesmo se um teste chamar `evaluate` com Alan+`M_lote=true` — `process_event()` nunca promove ator.

8. **`request_implement` e demais `illegal_events`:** reject, estado inalterado, stdout lista `enabled_events(q)` a partir do yaml. Chat não é evento; se o Agent invocar a ferramenta com esse nome, a máquina rejeita.

9. **`bound_card` e `--card`.**  
   Resolver #610 no cwd + path do repo (ou `--card`). Se `bound_card=⊥` e o evento move um card existente (tudo exceto T0), reject `unbound`. Se `--card` ≠ id da branch `card-<id>-*`, reject. T0 (`criar_card`) fica fora deste card se precisar de `gh issue create`; pode reject `not_implemented` com mensagem — **não** é aceite. Aceite é mover Status de um card já bound.

10. **Board mover injetável; live usa `gh project item-edit` só dentro do script.**  
    Protocolo: `set_status(issue_number: int, to: str) -> None`. Live: Project 1 `oalansilva`, campo Status, option id do `to`. Pytest: `FakeMover` que registra chamadas. **Nenhum** teste chama GitHub. `--dry-run` usa mover no-op.

11. **Guard deny Status **vence** substring `process_event.py`; sem env.**  
    Ordem no Python **e** no fallback bash: (1) path termina em `.design-digest` ⇒ deny (`preToolUse` e shell, **antes** de `design_globs` allow); (2) `command` contém `item-edit` / field id de Status / `updateProjectV2ItemFieldValue` ⇒ **deny mesmo se** também citar `process_event.py`; (3) `command` é **unicamente** python + `scripts/process-fsm/process_event.py` + evento + flags ⇒ esta regra não nega; (4) `if not path: allow`; (5) glob-first #611.  
    **Não** existe `PROCESS_FSM_MOVE`. O hook vê o Shell do Agent, não o `gh` filho do script. Heurística: `--field-id PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM` ou `--single-select-option-id` das 12+Cancelado. `gh issue view` / `item-list` ⇒ allow.

12. **Não expandir o Guard para `git commit` / `./restart`.** Fora. I8/T14 atômico não é aceite P0.

13. **Stdout JSON estável** (para o Agent e para testes):  
    `{result, state, to, reason, enabled_events?, message?}`. `result` ∈ `transition | reject`. Reject de T7: `reason=actor` ou `agent-t7`. Não imprimir tokens/secrets.

14. **Ajuste mínimo em `test_fsm.py`:** transições com `guard:` no yaml passam o predicado True explícito (`digest_changed=false` no T8 legal), senão Decision 5 quebra a suíte #609. Não reescrever a matriz.

15. **T10–T14 com deny total de item-edit (opção A lite + B).**  
    Deny de `item-edit` vale para **todas** as colunas. Agent só move via `process_event`.  
    - **T10–T13:** o evento nomeado **é** a guarda do `exclusive_group`. `achar_bloqueante` ⇒ `open_p0_p1=true` (demais do grupo false); `aceitar_sha` ⇒ `reviewers_ok`; `rerun_infra` ⇒ `flaky_infra`; `falha_codigo` ⇒ `source_failure`. Não há flag spoofável à parte do próprio evento (NLU escolhe o evento; δ ainda checa `q` + ator Agent).  
    - **T14 `integrar_develop`:** live `checks_green=None` ⇒ reject fail-closed. Alan **pode arrastar** para Done no UI (hook não vê). Squash/`./restart` continuam Agent fora deste script. Card futuro pode ligar a guarda; **não** neste lote.

## Risks / Trade-offs

- [Agent usa GraphQL ofuscado / `python -c` para item-edit] → residual P2 (mesmo classe do Guard #611). Heurística cobre `gh project item-edit` e o mutation name. Não é parser AST.
- [Alan arrasta T7 e o digest sidecar não existe] → I4 fail-closed: `iniciar_apply` vira T17 para Design. Mitigação: T5 deste fluxo grava o sidecar; cards já em Pronto para Dev sem sidecar precisam de um T5 retrô ou Alan devolve a Design. Aceito no lote 2: o card 612 é o primeiro consumidor.
- [Hook não vê `gh` filho do script] → desejado (Decision 11). Risco inverso: script bugado move coluna. Mitigação: δ + testes; `--dry-run`.
- [`evaluate` default fail-closed nas guardas] → exige tocar `test_fsm.py`. Mitigação: predicado True explícito só nas linhas T5/T8/T16/T17a/T17b e T14 se testado.
- [`M_lote` sempre false no live] → T16 nunca passa pela CLI. Correto neste card; release continua skill de ambientes.
- [T5 sem verificar Gist] → Agent pode submeter Design incompleto. P2; gate de Gist continua na skill/harness.mdc.
- [`enabled_tools` yaml só lista `process_event` em Pronto para Dev] → este card não reescreve essa allowlist (#613). A CLI é o mover em T3/T5/T8/T9/T10–T13 mesmo assim; paging não enforce neste lote.
- [T14 reject live] → Agent não integra em `develop` via script; Alan arrasta Done ou card futuro. Aceite #612 não inclui T14.

## Migration Plan

Aditivo. Rollback = reverter `process_event.py` + delta `fsm.py`/`guard.py`/`test_fsm.py`. Sem migration de banco. Cards em voo: sidecar ausente ⇒ I4 (T17), não apply.

## Open Questions

Nenhuma bloqueante. IDs do Project 1 (Status field / options) podem viver como constantes no módulo, iguais aos já usados operacionalmente; não são segredo.

## UI impact

**none** — harness/CLI. Nenhuma tela de produto nova ou alterada.

## Prototype

N/A — `UI impact: none`. `process_event` é ferramenta de processo, não superfície visual.

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

Crítica isolada inherit (read-only, três rodadas). Fontes: `proposal.md`, `design.md` (D1–D15), `tasks.md`, `specs/process-fsm-event/spec.md`, `specs/process-fsm/spec.md`, `specs/process-fsm-guard/spec.md`, `specs/cursor-harness/spec.md`, yaml T7/T8/T16/T17. Card #612, change `card-612-process-event`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Primeira crítica: **BLOCKED** — P0 (`PROCESS_FSM_MOVE` spoofable no proposal) + P1 (sidecar forjável em `design_globs`; I4 só no wrapper; T10–T14 vs deny total de item-edit; comando encadeado; `actor=` na função; `pedir_review`/T17b ausente).

Correções no escopo: remover env; I4 em `evaluate(T8/T9)`; compile T17 com ator interno Guard; sidecar deny **antes** do glob-first; T10–T13 evento=guarda / T14 live reject; Status deny vence substring `process_event.py`; função hardcode Agent; cenário+task `pedir_review`.

Recrítica 2: P1-1 ainda aberto (MODIFIED allow OpenSpec sem exceptuar sidecar). Correção: except + cenário Write `.design-digest` em Design + tasks 3.1/3.3.

Recrítica 3 (inherit, não editar): P0/P1 fechados. P2 aceitos: GraphQL ofuscado; `enabled_tools` yaml; Gist fora de `G_design`; fail-closed #611 vs sidecar (apply nega sidecar primeiro).

- **Escopo:** `process_event` SMAG; Guard deny item-edit Status e sidecar; sem release/paging/produto.
- **Processo:** Agent ⇏ T1/T7/T15/T16; T8 sem token de Write; I4→T17; `request_implement` ∉ δ; T16 stub aponta ambientes.
- **Operação:** fixtures sem GitHub; Alan arrasta gates humanos e Done (T14).

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica 3). Prototype N/A. Impeccable N/A.
