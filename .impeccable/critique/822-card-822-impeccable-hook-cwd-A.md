# Snapshot — Assessment A · card #822 `card-822-impeccable-hook-cwd`

- Card: #822 — kaizen: detector Impeccable falha no Grok após cada tool; Cursor e dsh dependem da pasta de trabalho
- Change: `card-822-impeccable-hook-cwd`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem nested critic)
- Modelo: inherit
- UTC: 2026-09-03T18:35:53Z
- Round: 1
- Tuple (este isolado): Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `d5a1fe2718d61c8888848021e0b93d6eef394ee90f25de29684864b8935692a7` · **1858** palavras (`wc -w`) · 13488 bytes · 128 linhas
- UI impact: **none** (harness/hooks; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*822*`; aceite = locator cwd-independente nas peles. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright. Sem browser gate.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois de A/B)
- Method: issue #822 body + comentário [5530106068](https://github.com/oalansilva/crypto/issues/822#issuecomment-5530106068); `proposal.md` / `design.md` D1–D6 + Apply contract / `tasks.md` 1–7; deltas `process-harness` `developer-tooling` `cursor-harness` `process-fsm-guard`; HEAD `9f2bfe97` worktree; rascunho canónico `develop` 7×`M` (leitura only).

---

## Brief (só neste snapshot)

Alan quer o detector Impeccable (e, no Grok, também o Guard e o SessionStart) a encontrar o script da pele quando o cwd da sessão não é a pasta do JSON/plugin. Live: 128×127 `./impeccable.sh: not found` no PostToolUse Grok; fail-open da tool; detector mudo. Grelha Q1–Q3 fechada no comentário: Grok detector+Guard+SessionStart; OpenCode entra por paridade; rascunho local = ponto de partida do Apply após Pronto para Dev. `UI impact: none`.

---

## Rubrica (UI none)

### 1. Escopo vs grill #822 (Q1–Q3 no comentário 5530106068)

Body live ainda mostra Qs abertas; Design **não** as reabre — sintetiza do comentário. Letras D1–D5 batem com o Entra pós-grelha.

| Q congelada | Onde no pacote |
| --- | --- |
| Q1 = detector **e** bloqueio de escrita **e** arranque de sessão no Grok | D1; proposal What; spec `process-harness` (quatro eventos) + `process-fsm-guard` (PreToolUse + SessionStart); tasks 2.1–2.2; C1–C4 |
| Q2 = OpenCode **entra** (paridade dos quatro; não “só Grok, Cursor e dsh”) | D4; proposal What/Impact; spec harness + tooling C9; tasks 5.1–5.3 |
| Q3 = rascunho local = ponto de partida Apply após Pronto para Dev | D5; Apply contract; tasks 1.1–1.2; Non-Goal: commit na `develop` durante Design |

Entra do body (núcleo) mapeado: Grok três cwd (raiz / `.grok/hooks/` / `frontend/`); Cursor `afterFileEdit`/`stop` três cwd (raiz / `.cursor/` / `.cursor/hooks/`); dsh `resolveRepoCwd` vs `process.cwd() \|\| REPO_ROOT`; fail-open; sem segundo detector.

**Não entra — não reaberto:** produto `backend/`/`frontend/src/`; dual-write T0–T17; Auto qualquer cliente; #668 / #720 / #782 / #784 / #821 como trabalho; T16/release/PROD; trocar `hook.mjs`; Guard Cursor; Guard dsh; `guard.py` `decide()`; pin `covenant-flow`.

Proposal «New Capabilities: (nenhuma)» correcto.

### 2. Paridade dos quatro (OpenCode in)

| Cliente | Recorte | Contrato |
| --- | --- | --- |
| Grok | detector PostToolUse/Stop **e** Guard PreToolUse **e** SessionStart | cadeia `test -f` repo-relative → sibling `./` → git toplevel; C1–C4 |
| Cursor | só `afterFileEdit` / `stop` | mesma classe para `.cursor/hooks/impeccable.sh`; Guard/`sessionStart` HEAD; C5–C7 |
| dsh | plugin Impeccable | `resolveRepoCwd(process.cwd())`; Guard dsh fora; C8 |
| OpenCode | plugin Impeccable | espelho em `opencode_plugin_lib.js` (MUST NOT import dsh); `$HOME` não vira cwd de `runHookMjs`; Guard OpenCode fora (Q2 = miss detector, não write-block); C9 |

HEAD medido: OpenCode já faz `input.directory \|\| input.worktree \|\| REPO_ROOT` e `runHookMjs` abre `hook.mjs` via `REPO_ROOT` do ficheiro — o furo real é directory truthy = `$HOME` a virar cwd do spawn. D4 nomeia esse furo (não o 127 Grok). Não omite o quarto cliente.

### 3. Grok detector + Guard + SessionStart

HEAD `.grok/hooks/process-fsm.json`: `./impeccable.sh PostToolUse` / `Stop`; `./process-fsm-*.sh`. Reprodução: cwd raiz → 127; `.grok/hooks/` → 0; `frontend/` → 127. Wrappers já resolvem `ROOT` por `dirname` depois do `exec`. Locator no JSON é o recorte certo.

Guard wrapper `.grok/hooks/process-fsm-guard.sh` `exec` o Cursor Guard; o processo sai 0 mesmo em deny (JSON fail-closed). C3 `exit 0` é locator encontrado, não allow de produto. SessionStart wrapper `exit 0`; `--write-grok-page` grava dest âncora no ficheiro da lib (não cwd). C4 exercita o locator sem mudar `decide()`.

### 4. Cursor afterFileEdit / stop

HEAD: `.cursor/hooks/impeccable.sh afterFileEdit` (parte se cwd = `.cursor/` ou `.cursor/hooks/`). D2 + spec cursor-harness: locator na mesma classe; `preToolUse` failClosed / `beforeShellExecution` / `sessionStart` inalterados. Goldens via `sh -c` (C5–C6). Rascunho canónico já tem a cadeia.

### 5. dsh Impeccable cwd

HEAD plugin: `const cwd = process.cwd() \|\| REPO_ROOT` (cwd `$HOME` truthy nunca cai). D3: `resolveRepoCwd` = `git -C start rev-parse --show-toplevel` senão `REPO_ROOT`. Rascunho canónico já exporta o helper e troca o plugin. Guard dsh continua `process.cwd() \|\| REPO_ROOT` — fora (#784).

### 6. Fail-open

Dois 127 distintos, ambos nomeados:

- Locator (pele em falta) = badge Grok actual; aceite = exit 0 nos três cwd; último `exit 127` só se o ficheiro não existir em lado nenhum.
- Detector `hook.mjs` crash/timeout = wrappers `exit 0` / `next()` / sem throw; C11; spec harness «Detector remains fail-open»; dsh MUST NOT `{ kind: 'block' }` / `steer`.

Não se troca fail-open do detector por fail-closed. Guard produto permanece fail-closed via JSON/`decide()`, não via exit do locator.

### 7. Dual-write T0–T17

C12 + spec harness cenário Dual-write + tasks 2.2 / 6.5 / 7.3. JSON/plugins só locators/cwd. Sem tabela T0–T17, I1–I9, 12 colunas em `.grok/` / `.dsh/` / `.opencode/`. `hook.mjs` continua o único detector. `process-fsm.yaml` / `AGENTS.md` / `guard.py` fora.

### 8. Sem produto UI

`UI impact: none` com justificativa. Prototype / Prototype Validation / pipeline Impeccable desta coluna = N/A. Apply contract: zero `backend/` / `frontend/src/`. Task 7.2. Nenhuma superfície visual nova/alterada sem classificação. Clone/browser gate isento (harness-only; `live_route: N/A`).

### 9. Apply contract vs rascunho na `develop`

Medido: `/srv/apps/dev/criptofarol/source` HEAD `9f2bfe97`, 7×`M` exactos (`.grok/hooks/process-fsm.json`, `.cursor/hooks.json`, `.dsh/plugin/impeccable-hook.js`, `scripts/process-fsm/dsh_plugin_lib.js`, `test_guard.py`, `test_paging.py`, `test_dsh_adapter.py`). Worktree do card: `card-822-impeccable-hook-cwd` @ `9f2bfe97`, só untracked OpenSpec da change. Rascunho **não** tem OpenCode — D4/D5/tasks 5.x. Design MUST NOT commit na canónica. Apply copia o delta para **esta** worktree após Pronto para Dev; não limpa a canónica (operador).

Rascunho `sh -c` cobre C1 (Grok PostToolUse) e C5 (Cursor afterFileEdit). Tabela C1–C12 + task 6.1 exigem também C2–C4 e C6. Apply que copiar os testes do rascunho sem os alargar falha o aceite da tabela — já no espírito do risco «Apply que ignore OpenCode falha C9».

### 10. Riscos operacionais (aceites no design.md)

- Grok recarrega JSON só em sessão nova (128×127 na sessão viva).
- Locator `exit 127` se git falhar e cwd sem o ficheiro.
- Cursor Guard / OpenCode Guard / pin `covenant-flow` v1.1.6 sem locator (próximo `--pin`).
- Espelho `resolveRepoCwd` em duas libs (MUST NOT cruzar).
- `resolveRepoCwd($HOME)` se `$HOME` for git alheio devolve esse toplevel, não `REPO_ROOT` (neste host `$HOME` não é git; C8 assume isso).
- Canónica `develop` fica suja até o operador limpar.

Rollback nomeado: reverter JSON/plugins para `./` e `process.cwd() \|\| REPO_ROOT`. Sem migration / rebuild.

---

## Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| Rotas Cripto / shell autenticado / componentes / copy | não tocadas |
| HTML protótipo | N/A (`UI impact: none`) |
| Badge `[hooks: 1 failed]` | aceite operacional Grok, não tela de produto |
| `DESIGN.md` / Playwright desta coluna | N/A |

---

## Achados

### P0

(nenhum)

### P1

(nenhum) — design.md não omite OpenCode nem Guard/SessionStart Grok; grelha Q1–Q3 reflectida em D1/D4/D5 + specs + tasks.

### P2

- **Rascunho de testes subcobre C2–C4/C6** (só PostToolUse + afterFileEdit via `sh -c`). Tabela + task 6.1 já obrigam os seis. Disposition: **accepted** (risco de Apply, contrato escrito).
- **`resolveRepoCwd` = qualquer git toplevel do cwd.** `$HOME` que seja git alheio viola o THEN «git do consumidor / `REPO_ROOT`». C8 no rascunho assume `$HOME` sem git. Disposition: **accepted** (residual; host de crítica `$HOME` não é git).

### P3

- OpenCode Guard continua `input.directory` cru. Disposition: **accepted** (Q2 = detector).
- Cursor Guard/`sessionStart` ainda dependem de cwd = raiz. Disposition: **accepted** (recorte).
- Próximo `implantar --pin` pode repor `./impeccable.sh` se o produto pinado não tiver o locator. Disposition: **accepted** (grelha não pediu tag).
- Espelho `resolveRepoCwd` dsh↔OpenCode pode divergir. Disposition: **accepted**.
- Canónica `develop` suja até o operador. Disposition: **accepted**.
- C4 SessionStart no pytest pode (re)escrever `.grok/rules/process-fsm-page.md` (padrão já unlink em `test_write_grok_page_cli_uses_repo_root`). Disposition: **accepted**.
- Goldens Cursor via `sh -c`; se o runner nativo não for shell, a cadeia `test -f && exec` parte. Issue prescreveu essa cadeia; Grok vivo já é `sh:`. Disposition: **accepted**.
- Plugin OpenCode MUST permanecer só `default` export (golden 1.18.18). Disposition: **accepted** (já pinado fora deste card).

---

## Verdict

**PASS** — zero P0/P1 abertos. Prototype N/A justificado. Snapshot visual Impeccable N/A justificado (`UI impact: none`). Este ficheiro é o relatório da crítica de processo, não o browser gate.
