## Context

Card [#632](https://github.com/oalansilva/crypto/issues/632) (kaizen P1, Origem: lote #612 F-2). O yaml T14 já é `QA --integrar_develop, Agent, checks_green--> Done` com ações `squash`, `restart`, `comment_done`, `set_status` e invariante I8. O #612 compilou T10–T13 e deixou T14 live reject (`checks_green` unset). O Agent não fecha Done; o `./restart` canônico em DEV vira passo de skill. Alan pediu (2026-08-21) o restart automático do processo antigo para os cards novos.

**UI impact: none.** Harness/CLI. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Live `process_event integrar_develop` mede `checks_green` (CI, sem flag spoofável).
- Com guarda verdadeira, executa squash → atualiza source DEV → `./restart` canônico → comentário Done → Status=Done.
- Falha de squash/restart/health ⇒ I8, Status permanece QA, mover não é chamado.
- Homologar / fechar_release continuam reject Agent. pytest cobre verde e falha.

**Non-Goals:**

- T16 / deploy PROD / `release-guard` real / warmup 502 de `criptofarol.com.br`.
- Restart no meio do card (unit isolado continua skill de ambientes).
- Expandir o Guard para `git commit` / `./restart`.
- `--actor Alan`, `--checks-green` na CLI, `PROCESS_FSM_MOVE`.
- Código de produto (`backend/`, `frontend/src/`).
- Alterar a linha T14 do yaml (já está correta).

## Decisions

1. **Medir `checks_green` no live; testes injetam o predicado.**  
   Alternativa: flag `--checks-green` (Agent forja, mesma classe do env #612). `main()` **não** aceita essa flag. Se o caller da função não passou `checks_green`, `process_event` chama `measure_checks_green(bound_card, q_git)` **antes** de `evaluate()`. True **somente** quando existe PR `q_git` → `develop` cujo check GitHub de nome `qa-gate` está `success` no SHA de head. Pending, skipped, cancelled, failure, ausência do check ou erro de API ⇒ False (fail-closed). Outros checks no SHA **não** entram no predicado (`qa-gate` já agrega os `needs` do workflow). Pytest injeta `checks_green=` ou um measurer fake; **não** chama GitHub.

2. **Ações T14 são Mealy injetáveis, ordem fixa, I8; runner ausente nunca move.**  
   Protocolo (`T14Runner`): `squash` → `sync_dev_source` → `restart` → `comment_done`. Só então o mover `set_status(Done)`. Qualquer exceção/returncode ≠ 0 aborta: reason `I8`, mover vazio, Status permanece QA. Se o runner (ou o measurer, no live) for `None`, `process_event` MUST `reject` e MUST NOT chamar `_safe_move` — não há fall-through para “só arrastar Done”. `main()` injeta measurer+runner reais no mesmo padrão do `GhBoardMover`. `--dry-run` avalia δ (inclui medição read-only) e **não** chama o runner nem o mover. Testes usam fakes; fixture obrigatória: measurer True + runner omitido ⇒ mover vazio.

3. **Restart é o path absoluto canônico, nunca o worktree.**  
   `/srv/apps/dev/criptofarol/source/restart`. O script recusa `ROOT_DIR` em worktree (`/srv/apps/dev/criptofarol/*` que não seja o source) e o path PROD não é este. Alternativa: `./restart` no cwd do Agent — cairia no recusar ou, pior, no fallback legado. T14 MUST `exec` o path canônico (sudo -n já está no próprio script). Sem fallback `stop`/`start`.

4. **`sync_dev_source` probeia dirty **antes** de mutar o checkout.**  
   Merge no GitHub não atualiza `/srv/apps/dev/criptofarol/source`. Ordem obrigatória nesse path: (1) `git status --porcelain` — se não vazio (tracked **ou** untracked) ⇒ `reject` `I8`, **sem** `checkout`/`merge`/`reset --hard`/`restart`/`set_status`; (2) só então `git fetch origin` + `checkout develop` + `merge --ff-only origin/develop`; non-FF ⇒ I8, sem hard reset. `ff-only` sozinho **não** detecta dirty.

5. **Squash = `gh pr merge --squash` do PR da branch; idempotente se já merged.**  
   Depois que `evaluate()` aceitou (`checks_green` True), falha de qualquer passo do runner — inclusive squash sem PR/SHA — ⇒ `reason=I8` (yaml: falha squash/restart ⇒ permanece QA). Measurer False **antes** de `evaluate()` continua `guard:checks_green`, runner não roda. Já merged ⇒ pula `gh pr merge`, segue sync+restart. Não squash local na worktree para `develop`.

6. **Health: o `restart` canônico já espera 8004+5175 (30s).** Exit ≠ 0 ⇒ I8. Depois do exit 0, T14 ainda faz retry curto em `https://dev.criptofarol.com.br/api/health` (502 de warmup ≠ falha imediata; esgotar retries ⇒ I8). Não valida PROD.

7. **`comment_done` = `scripts/post-card-evidence-comment.sh --transition done`.**  
   `--card`, `--commit` (SHA de `origin/develop` após squash), `--branch develop`, `--review` gerado pelo script T14 (`qa-gate` verde + restart canônico + health). Falha do comentário ⇒ I8 (Done sem evidência não fecha). Dedup do helper permanece.

8. **T10–T13, T15, T16, Guard item-edit: inalterados.**  
   Evento nomeado continua ligando as guardas T10–T13. Agent `homologar`/`fechar_release` reject. O Shell do Agent para T14 é **somente** `python scripts/process-fsm/process_event.py integrar_develop [--card] [--change] [--dry-run]`; squash/restart são filhos do processo (o hook não vê, igual ao `item-edit` interno). Não expandir deny/allow de `./restart`.

9. **Spec #612 “T14 stays reject live” é substituída, não convive.**  
    Delta OpenSpec: RENAMED dessa requirement (fica só T10–T13) + ADDED da T14 live atômica. Fixture atual `test_integrar_develop_rejects_without_checks_green` permanece (unset + measurer que devolve None/False). Fixtures novas: measurer True + runner ok → Done; `restart` falha → I8; runner omitido → mover vazio; porcelain não vazio → I8 sem mutar o source.

## Risks / Trade-offs

- [DEV source sujo no closeout] → porcelain não vazio ⇒ I8 **antes** de checkout/merge; T14 não destrói o checkout (`reset --hard` proibido).
- [Hook não vê `gh pr merge` / `restart` filhos] → desejado (mesmo padrão #612). Risco: script bugado mergeia. Mitigação: δ + `--dry-run` + testes I8; squash só do PR da `q_git` bound.
- [Medição GitHub falha (rede)] → fail-closed False, reject. Correto.
- [Harness-only ainda roda `./restart` completo] → custo de build DEV. Aceito: é o closeout canônico; evita o buraco dos cards novos.
- [T14 live chama GitHub] → unitários continuam sem GitHub (measurer/runner injetados). Um teste de contrato do measurer pode mockar subprocess, não a API real.
- [502 público após health interno ok] → retries no URL DEV; esgotar = I8. Não trata Caddy/PROD.
- [Alan arrasta Done no UI] → hook não vê; residual igual #612. Este card não fecha esse furo.

## Migration Plan

Aditivo em `process_event.py`. Cards em QA passam a poder `integrar_develop` de verdade. Rollback = reverter o módulo; T14 volta ao reject live. Sem migration de banco. Sem mudança de yaml.

## Open Questions

Nenhuma bloqueante. Dispensa Playwright visual continua regra de overlay/Alan, agregada no `qa-gate` quando o job e2e é `needs` — T14 não tem segunda lista.

## UI impact

**none** — CLI de processo. Nenhuma tela de produto nova ou alterada.

## Prototype

N/A — `UI impact: none`. T14 não tem superfície visual.

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

Crítica isolada inherit (read-only, duas rodadas). Fontes: `proposal.md`, `design.md` (D1–D9), `tasks.md`, `specs/process-fsm-event/spec.md`, `specs/process-fsm/spec.md`, `specs/cursor-harness/spec.md`, yaml T14/I8, `process_event.py` baseline #612, `restart` canônico. Card #632, change `card-632-t14-live-done`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Primeira crítica: **BLOCKED** — P0-1 (`ff-only` não detecta dirty) + P1 (runner `None` fall-through; D1 vs D2; spec sem dirty/path/`comment_done`; reason squash ≠ I8).

Correções no escopo: porcelain **antes** de mutar; runner/measurer `None` ⇒ reject sem mover; predicado só `qa-gate`; spec+tasks com dirty, path absoluto, `comment_done` I8; falha de runner após guarda True ⇒ `reason=I8`.

Recrítica 2 (inherit, não editar): P0/P1 da rodada 1 fechados. P2 aceitos: spoof via parâmetro da função; retry após squash; health público DEV; sem lock no source; `checkout develop` só no D4 (spec/tasks dizem fetch+ff); fixture squash falho não listada em 2.7 (corpo da spec cobre).

- **Escopo:** T14 live atômico; T16/PROD fora; yaml T14 intacto.
- **Processo:** Agent ⇏ T1/T7/T15/T16; Done = `process_event integrar_develop`, não `item-edit` nem `./restart` no worktree.
- **Operação:** I8 com porcelain + runner obrigatório; restart só `/srv/apps/dev/criptofarol/source/restart`.

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica 2). Prototype N/A. Impeccable N/A.

