## Context

Card [#613](https://github.com/oalansilva/crypto/issues/613), filho E / 5/5 do epic [#608](https://github.com/oalansilva/crypto/issues/608). Lote 3 P2. Yaml (#609), resolver (#610), Guard Write (#611) e `process_event` (#612) já estão `Pronto`. O Auto ainda afoga: `AGENTS.md` (~670 linhas) entra always-on (Cursor auto-injeta o arquivo da raiz), `harness.mdc` carrega Gist/review/OpenSpec, e a skill `alan-workflow` prioriza **chat > overlay > skill**. Lost in the Middle + sycophancy: `implemente` em Todo vira atalho; sessão em Todo vê playbook de release.

**UI impact: none.** Harness/contexto. Prototype N/A. Impeccable N/A.

Dependência: #610 (resolver). Lote 1 já `Pronto` — paging não substitui o Guard.

## Goals / Non-Goals

**Goals:**

- `sessionStart` injeta só a página Moore: `(q, bound_card, q_git)` + `context_file[q]` do yaml (stubs #609).
- `harness.mdc` = 8–15 linhas de corpo (sempreApply). Always-on ≤ esse playbook + a página.
- Skill: prioridade **δ e Guard > overlay > skill > wording**.
- `AGENTS.md` da raiz deixa de ser o muro de 670 linhas always-on; overlay (portas, Drive, release) on-demand.
- Pytest: `q=Todo` ⇒ `additional_context` **não** contém o playbook de release. Sem GitHub nos unitários.

**Non-Goals:**

- Reabrir Guard Write, `process_event`, yaml T0–T17, `enabled_tools` enforcement no paging.
- Autômato de release / deploy PROD / `release-guard` real.
- Código de produto; `git commit` / `./restart` como hook.
- Impedir Cursor Cloud de injetar o que o produto Cursor injeta além deste repo (residual: `sessionStart` é fire-and-forget e **deferred** em cloud agents — docs Cursor).
- Expandir allowlist do `release-guard`.

## Decisions

1. **Módulo `scripts/process-fsm/paging.py` + adapter bash.**  
   Alternativa: prompt-hook, ou só enxugar `harness.mdc`. Compile-Then-Page: o SOP já está no yaml; o hook **pagina o frame**. Função `page(...)` injetável (`resolve_fn`, `status_provider`, `fsm`). CLI/adapter lê stdin JSON `sessionStart` e stdout `{ "additional_context": "..." }`. Sem `failClosed` no `sessionStart` (docs: fire-and-forget; sessão não bloqueia).

2. **Página = tupla + stub yaml + uma linha de `enabled_events(q)`.**  
   Formato pinado (≤20 linhas, epic §4):

   ```text
   process-fsm page
   q=<Status|None> bound_card=<id|⊥> q_git=<branch|⊥>
   enabled_events: <csv do yaml ou (unbound)>
   ---
   <context_file[q] verbatim, ou UNBOUND_PAGE>
   ---
   Resolva (q, bound_card, q_git). Não invente aresta. Chat é wording; NLU ≠ δ. Overlay on-demand (portas, Drive, release).
   ```

   `UNBOUND_PAGE` (q ilegível ou `bound_card=⊥`): `bound_card=⊥. Write produto deny. Não carregue playbook de release.`  
   **Proibido** na página: corpo de `AGENTS.md`/`docs/crypto-overlay.md`, `release-guard pre|post`, “subir lote”, deploy PROD, tabela T0–T17.  
   Teto da página: **≤20 linhas** (epic §4 Moore). O envelope (tupla + `enabled_events` + stub + rodapé) é a página; não é um segundo always-on.  
   `status_provider` default = `github_status_provider` (#611, query pontual issue→Status). Pytest injeta o provider (não um kwarg `q=` que desvie do resolver). Timeout/None ⇒ `UNBOUND_PAGE` + tupla, não Homologado.

3. **`q` vem do Status do card bound, não do chat.**  
   `resolve(cwd, cwd)` → `bound_card` / `q_git`. Se bound, `status_provider(bound_card)` → `q`. Sem `item-list` paginado. Sessão em `card-613-*` com Status Todo ⇒ stub Todo. Sessão em `main`/`develop` ⇒ unbound (não adivinha o card do chat).

4. **`hooks.json` ganha `sessionStart` sem mexer no Guard.**  
   Entrada distinta de `preToolUse`/`beforeShellExecution`/Impeccable. Comando: `.cursor/hooks/process-fsm-session-start.sh` (mesmo padrão do Guard: shebang, JSON sempre, fallback se Python falhar = página mínima unbound, **nunca** o overlay). Sem matcher. Sem `failClosed`.

5. **`harness.mdc`: 8–15 linhas de corpo após o frontmatter.**  
   Contagem: linhas não vazias do corpo (`# Harness` inclusive), excluindo o bloco YAML `---`. Apply MUST deixar 8–15. Conteúdo (não copiar Gist/review/OpenSpec detalhado, `diff-reviewer` nem `release-guard` — isso é skill on-demand). O corpo MUST incluir o SHALL da spec MODIFIED (`Em Refinamento` é a entrada; não pular Design / Aprovação de Design; Todo ≠ código):

   - Resolva `(q, bound_card, q_git)`; não invente aresta.
   - Chat é wording, não autorização; NLU ≠ δ; `implemente` ∉ δ.
   - `Em Refinamento` é a entrada. Não pular Design / Aprovação de Design.
   - `Todo` não é código; próxima = `iniciar_design` via `process_event`.
   - Código / `/opsx:apply` só após `Status=Pronto para Dev` (T8).
   - Alan único em T1/T7/T15/T16.
   - Overlay on-demand; runbook = skill `alan-workflow`; lei = `rules.md`.
   - Skills deste repo; Task `inherit`; cliente Cursor Agent; Auto permitido no dia a dia.

6. **Cursor auto-injeta `AGENTS.md` da raiz → stub + overlay em `docs/`.**  
   Alternativa A: manter 670 linhas e “pedir para ignorar” — falha Lost in the Middle.  
   Alternativa B: `.cursor/overlay-crypto.md` — sai do allowlist documental do `release-guard` (`docs/**` ∪ `AGENTS.md` ∪ …). Fora: não expandir o guard neste card.  
   **Escolha:** `git mv`-equivalente do corpo atual para `docs/crypto-overlay.md` (já allowlist). Raiz `AGENTS.md` vira stub ≤40 linhas: o que é, **quando** `Read docs/crypto-overlay.md` (portas/URLs, Drive, PostgreSQL, release-guard/lote/PROD), URL do board `github.com/users/oalansilva/projects/1` (detecção da skill `github-project-board`), “não é o playbook de 12 colunas”. O always-on que o Cursor injeta passa a ser o stub, não o closeout de release.

7. **Prioridade da skill invertida (bloco no topo do `SKILL.md`).**  
   Substituir a lista atual (`1. chat  2. overlay  3. skill`) por:

   1. **δ e Guard** (`.cursor/process-fsm.yaml`, `process_event`, hook Write).
   2. **Overlay** (`docs/crypto-overlay.md` / stub `AGENTS.md`) — só quando a tarefa precisar de portas, Drive, PG, release.
   3. **Esta skill** (runbook).
   4. **Wording** do chat (`implemente`, `autorizo`, `gostaria sempre`).

   `rules.md` permanece lei humana, não injetada sozinha. Não dual-write hermes/`~/.codex`.

8. **Testes em `scripts/process-fsm/test_paging.py`, job `process-fsm` existente.**  
   Fixtures (provider injetado, sem `gh`):
   - `status_provider` retorna `Todo` ⇒ contexto contém o stub Todo do yaml; **não** contém `release-guard`, `subir lote`, `deploy PROD`.
   - `status_provider` retorna `Homologado` ⇒ stub Homologado (lote / T16); ainda assim **não** `release-guard pre`/`post` nem deploy PROD.
   - unbound / `status_provider`→`None` ⇒ `UNBOUND_PAGE`; não Homologado/release.
   - `additional_context` ≤20 linhas; inclui a tupla.
   - `harness.mdc` corpo 8–15 linhas (teste lê o arquivo versionado); corpo menciona `Em Refinamento` e não menciona `diff-reviewer` / `release-guard`.
   - Stub `AGENTS.md` contém `github.com/users/oalansilva/projects/1`.
   - `SKILL.md` declara a ordem δ/Guard > overlay > skill > wording (assert de âncora, não o runbook inteiro).

9. **Não copiar T0–T17 nem o closeout de release para a página.**  
   Yaml `context_file` já é stub (D6 do #609). Paging **lê** o yaml; não reescreve stubs neste card salvo bug de whitespace. `enabled_tools` continua documentação Moore; paging não enforce tools (Guard já o faz para Write).

10. **Cloud / sessionStart deferred = residual P2.**  
    Docs Cursor: `sessionStart` deferred em cloud agents. Mitigação deste card = stub `AGENTS.md` + harness curto, que o produto Cursor ainda injeta. Homologação humana: sessão **local** em worktree `card-<id>` com Status Todo.

## Risks / Trade-offs

- [Cursor continua injetando o stub `AGENTS.md`] → aceito; o stub não é o playbook de release. Sem o stub a raiz perde o ponteiro on-demand.
- [Cloud agent sem `sessionStart`] → residual P2; harness + stub ainda enxutos.
- [Mover overlay para `docs/crypto-overlay.md` quebra links “veja AGENTS.md”] → stub redireciona; apply atualiza a frase da skill (D7) e o próprio overlay (self-ref). Não varrer o histórico de `docs/decision-log.md`.
- [Página Homologado cita T16/`M_lote`] → o stub yaml já o faz; teste proíbe o **playbook** (`release-guard pre`, deploy PROD), não a palavra “lote”.
- [Agent ignora a página e lê o overlay] → Guard + `process_event` (lotes 1–2) continuam a autoridade; paging não substitui deny.
- [Contagem 8–15 inclui frontmatter] → D5 pinada: só corpo.
- [Skill `alan-workflow` auto-anexa o bloco Release numa sessão Todo] → residual P2: o card inverte prioridade, não encolhe a skill; Guard + `process_event` continuam a autoridade; homologação humana escopa harness + stub + payload do hook.

## Migration Plan

Aditivo. Rollback = reverter hook/`paging.py`/`harness.mdc`/skill + restaurar `AGENTS.md` a partir de `docs/crypto-overlay.md`. Sem banco. Cards em voo: próxima sessão já pagina; sessão aberta não retroage o contexto já injetado.

## Open Questions

Nenhuma bloqueante. Homologação: sessão em Todo não carrega playbook de release (assert do `sessionStart` + ensaio humano).

## UI impact

**none** — harness/contexto. Nenhuma tela, rota ou componente de produto.

## Prototype

N/A — `UI impact: none`. Sem superfície visual nova ou alterada.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none` (paging de contexto / harness; sem superfície visual).

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Agent verdict

PASS — crítica isolada inherit (2 rodadas). Prototype N/A. Impeccable N/A.

## Design Critique

Crítica isolada inherit (read-only, duas rodadas). Fontes: `proposal.md`, `design.md` (D1–D10), `tasks.md`, `specs/process-fsm-paging/spec.md`, `specs/cursor-harness/spec.md`, yaml `context_file`. Card #613, change `card-613-process-fsm-paging`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Round 1 Task id `733a59ad-ed57-49c8-a091-d0da438cfc60` (BLOCKED, P1 D5). Round 2 Task id `f65228a0-5a96-411d-9cbc-d55f1a80064b` (PASS após correção).

### Dimensões

- **Escopo:** lote 3 paging `sessionStart` + harness 8–15 + stub `AGENTS.md` + prioridade invertida; Guard/`process_event`/produto fora. Sem regressão de superfície visual.
- **Produto / processo:** página Moore = tupla + `context_file[q]`; Todo não carrega playbook de release; overlay on-demand em `docs/crypto-overlay.md` (allowlist `docs/**`).
- **Operação:** `sessionStart` fail-open; cloud deferred = residual P2 (stub + harness ainda enxutos); Guard `failClosed` intocado.
- **UI / a11y / responsivo / estados visuais:** N/A — harness.

### P1 round 1 (fechado)

D5/`tasks.md` 2.1 omitiam `Em Refinamento` como entrada e o “não pular Design / Aprovação de Design” da spec MODIFIED. Corrigido: D5 lista os SHALL no orçamento 8–15; task 2.1 cita D5 **e** a spec.

### Achados desta rodada (round 2)

- **P0 / P1:** nenhum.
- **P2 (aceitos, não bloqueiam):** spec ADDED de harness não repete o nome `Em Refinamento` (vive no MODIFIED + D5 + 2.1/3.2); proposal one-liner mais curto que D5; skill `alan-workflow` continua auto-anexável (card inverte prioridade, não encolhe a skill); `sessionStart` deferred em cloud.

### Pendências não bloqueantes

Apply segue D5 + tasks; homologação humana: sessão local em worktree `card-<id>` com Status Todo. Aprovação humana (`Aprovação de Design -> Pronto para Dev`) permanece de Alan.

Design Agent verdict: PASS
