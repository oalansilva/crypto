# Snapshot — Assessment A · card #720 `card-720-opencode-three-adapters`

- Card: #720 P0 kaizen — Harness: terceiro adapter OpenCode — uma lei, três clientes
- Change: `card-720-opencode-three-adapters`
- Critic: Assessment A (crítica isolada de Design; sem transcript do pai; sem partilha com B)
- Modelo: inherit
- UTC: 2026-08-27T20:10:03Z
- Tuple: `.grok/rules/process-fsm-page.md` ausente. `scripts/process-fsm/resolve.py` → `bound_card=720` `q_git=card-720-opencode-three-adapters` `q=None` (board não injectado neste isolado). Issue + prompt do pai: `Status=Design`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- UI impact: **none** (justificado: harness/hooks/docs/specs/testes de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A (sem HTML em `frontend/public/prototypes/`; `openspec validate card-720-opencode-three-adapters --type change --strict` = valid)
- Impeccable visual / Playwright / detector-de-tela desta coluna: N/A justificado. Detector automático como **pele de harness** (Grok+OpenCode → `hook.mjs`) entra no card, não nesta crítica de tela.
- Method: body grelhado #720 (fronteira vazia) + 2 comentários live; `proposal.md` / `design.md` (D1–D12, G1–G16) / `tasks.md`; change specs `process-harness` `cursor-harness` `developer-tooling` `process-fsm-guard` `process-fsm-paging`; specs main; archive `2026-08-23-card-668-multi-harness-adapters`; `guard.py` `normalize`/`extract_path`/`decide`; `.grok/hooks/process-fsm.json`; `.cursor/hooks.json` + `impeccable.sh` + `hook.mjs`; `AGENTS.md`; `openspec/config.yaml`; binário live `/home/ubuntu/.opencode/bin/opencode` `--version 1.18.18` (strings)

---

## Brief

**Problema:** o núcleo #668 já é lei com dois adapters. Abrir o repo no OpenCode **1.18.18** não é contrato: `normalize()` não vê `{ tool, args }` (`filePath` / `patchText` / `command`) e write ilegal em `backend/` + `q_git=develop` cai no early-return allow. Detector Impeccable está só no Cursor. Copiar T0–T17 para `.opencode/` reabre #584/#668.

**Outcome:** terceiro adapter = tradução sobre o mesmo `decide()` / `page()`; detector no mesmo `hook.mjs` nos três clientes; sem dual-write da lei; sem lock machine; sem `opencode.json`; sem `/opsx-*`; sem produto.

**Direction:** dialeto nativo no núcleo; plugin auto-load throw-no-deny; paging inject (`experimental.chat.system.transform`); stubs ponte ≤8 linhas; Grok `PostToolUse`+`Stop` + OpenCode `tool.execute.after`+`session.idle`.

**Scope:** `scripts/process-fsm/`, `.opencode/plugin/` + stubs, `.grok/hooks/` só detector, `AGENTS.md`, decision-log, specs, `openspec/config.yaml` no Apply. Fora: upgrade, lock machine, produto, hop Grok no OpenCode, Auto sem ensaio.

---

## Critique

### 1. Fidelidade ao #720 grelhado

Body live (2026-08-27T19:49:50Z; grelha: fronteira vazia; rodada 1 já no body). Comentário canónico exacto: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Design não reentrevista.

| Entra do issue | Onde no Design / spec / tasks |
| --- | --- |
| Alvo fixo 1.18.18; sem upgrade | D1; Non-Goals; lista canónica = golden + ensaio |
| Terceiro dialeto `{ tool, args }` (`filePath` / `patchText` / `command`); tools `write`/`edit`/`apply_patch`/`bash` | D2–D3; spec `process-fsm-guard` ADDED; tasks 1.1–1.2 |
| Path vazio / `patchText` sem path **não** vira allow | D4; G4–G6; spec Empty OpenCode write path |
| Plugin `.opencode/plugin/` singular (#395); auto-load; **sem** `opencode.json`; throw no deny | D5–D6; spec plugin throw; tasks 2.1 / 2.3 |
| Paging `experimental.chat.system.transform`; inject, não hop Grok | D7; spec `process-fsm-paging` ADDED; task 2.2 |
| Pele irmão #668; **sem** `/opsx-*` | D8; spec No opsx; task 2.3 |
| Stubs ≤8 linhas MUST Read; 1.18.18 não descobre `.cursor/skills/`; não duplicar Impeccable/`design-critic` em `.agents/skills/` | D8; spec OpenCode stub is a bridge; task 3.1 |
| Detector nos três; mesmo `hook.mjs`; fail-open | D9; spec Impeccable detector is on all three; tasks 4.1–4.3 |
| Specs dois → três; lock machine / `opencode.db` / lease / attestation / `opencode.json` continuam proibidos | D10; `process-harness` / `cursor-harness` / `developer-tooling` |
| `AGENTS.md` três clientes; sem Auto OpenCode/Grok; ≤40 | D12; G15; task 3.2 |
| Decision log: revoga unicidade #562; **não** a morte do lock machine | D10; task 3.3 |
| Ensaio deny + detector = homologação / Auto, não merge | D11–D12; vocab do issue; task 6.5 |
| `UI impact: none`; sem produto | UI impact / Prototype / pipeline N/A; task 6.4 |

**Vocabulário:** `Núcleo` / `Adapter` / `Dialeto nativo OpenCode` / `Impeccable (skill)` vs `(detector)` / `Lock machine` / `Ensaio deny` — copiados do issue, não inventados. `_Avoid` do issue (dual-write, harness único, copiar runbook, OpenCode antigo, `opencode.json`, Auto sem ensaio, confundir skill com detector) está nos Non-Goals + Apply contract.

**Marcador `Move File` vs `Move to:`:** o Entra resume `*** Add/Update/Delete/Move File:`. Design observa o binário 1.18.18 (`*** Move to:`) e mapeia o shorthand. Independente: no binário live, `*** Move to:` = 3 hits, `*** Move File:` = 0. Spec e G3 usam o marcador live. Não é sinónimo inventado; é correcção empírica documentada (risco: parse extra de `Move File` é barato).

**Não entra — não reaberto:**

- lock machine / lease / packet / `design_artifact_write` / attestation / `opencode.db` / vision Go/Qwen
- segundo Guard / segundo detector / T0–T17 / I1–I9 em `.opencode/` / `permission: { edit: deny }` estático
- `opencode.json` (mínimo ou completo)
- `/opsx-*` no OpenCode; yaml para `process/`; produto; `--auto` sem ensaio; #614; Hermes / `~/.codex/skills/`
- núcleo #668 (yaml, `decide()` dual emit) — este card **acresce** detector Grok que o #668 listou como Non-Goal (`Impeccable no Grok`) *porque o #720 Entra o manda*; não relitiga Guard/paging Grok (task 4.1 + Apply contract)
- upgrade neste card
- arquivo Moore gitignored + MUST Read no OpenCode (inject)

`Open Questions: Nenhuma bloqueante` bate com fronteira vazia. Residuais (#5894, plugin carregou) ficam no ensaio, como o issue.

Drift: nenhum de recorte. Proposal “New Capabilities: (nenhuma)” correcto: pele é o terceiro adapter do `process-harness` já existente.

### 2. Escopo vs recorte pedido (terceiro adapter + detector; sem lock / json / opsx / produto)

| Recorte | Status |
| --- | --- |
| Terceiro adapter OpenCode 1.18.18 sobre `decide()`/`page()` | D2 / spec três adapters / tasks 1–2 |
| Detector Impeccable Grok+OpenCode, mesmo `hook.mjs` | D9 / tasks 4.1–4.3 |
| Sem lock machine | Non-Goals + `cursor-harness` ADDED “OpenCode lock machine stays dead” + decision-log |
| Sem `opencode.json` | D5; G16; task 2.3 |
| Sem `/opsx-*` | D8; spec No opsx; G16 |
| Sem produto | Apply contract; task 1.4 / 6.4 |
| Sem dual-write da lei / T0–T17 em `.opencode/` | spec Dual-write forbidden alarga a `.opencode/`; G16; stubs ≤8 MUST Read |
| Sem upgrade | D1 |

Pele = dois módulos (Guard throw vs detector never-throw) é decisão de isolamento, não segundo detector. Paging no Guard plugin *ou* irmão (task 2.2) não mistura o throw do detector. Implementável.

### 3. Regressão de produto/processo (#668 Cursor/Grok Guard, dual-write, T0–T17)

**#668 Guard Cursor/Grok — não quebra o contrato, acresce dialeto.**

- `normalize()` hoje só `tool_name`/`toolName` + `tool_input`/`toolInput`. Terceiro envelope entra ao lado; `emit()` dual permanece (D6). Spec velha “Guard normalizes Cursor and Grok envelopes” **não** é REMOVE — o ADDED OpenCode estende (SHALL include ≠ only). Matcher Grok `PreToolUse` e Cursor `preToolUse`/`failClosed` **não** são relitigados.
- `WRITE_TOOLS` actual não tem `edit` nem `apply_patch`. `apply_patch`+`patchText` sem parse = path vazio = `decide()` linha 403–404 `_allow()` — o furo P0 que o card fecha (G4–G6 / D4).
- `write` já é tool Grok. Deny de path vazio para o conjunto OpenCode `{write, edit, apply_patch}` **aperta** Grok `write` vazio (hoje allow). Não autoriza write legal; fecha o mesmo furo #611-shaped. Cursor `Write` (maiúscula) permanece no early-return antigo. Aceitável; não reabre o núcleo yaml/`process_event`.
- Fallback bash (`.cursor/hooks/process-fsm-guard.sh`) hoje não lê `tool`/`args`/`filePath`. Task 1.3 / G12 fecham o furo #668-análogo para o *wrapper* Cursor/Grok. A pele OpenCode (task 2.1) chama `guard.py`/`decide()` — wording do próprio issue. Python-down no OpenCode = classe fail-open (igual Grok crash #668), não regressão do Guard Cursor.
- Detector Grok: `PostToolUse`+`Stop` **acrescentados** ao JSON aninhado que já tem `PreToolUse`+`SessionStart`. Apply contract: não relitigar Guard/paging. Risco operacional = JSON malformado no Apply, não o desenho.
- Auto: Cursor Auto permanece; Grok #668 4.5 ainda pendente; OpenCode cooperativo até ensaio próprio. `AGENTS.md` actual (14 linhas não-vazias) já separa “Cursor Agent (Auto permitido)” de “Grok Build (cooperativo…)”. G15 + `test_agents_md_is_stub` retarget. Sem herdar Auto.

**Dual-write da lei:** stubs `.opencode/skills/` = ponte MUST Read, corpo ≤8, sem tabela. Spec “Dual-write of the law is forbidden” passa a inspeccionar `.opencode/`. G16. Sem gerador CI obrigatório (ao contrário de `grok_stubs.py`) — residual de Apply/stale, não segundo runbook desenhado.

**T0–T17 / I1–I9 em `.opencode/`:** Non-Goal + G16 + task 2.3/6.3. Paging OpenCode = `page()` inject, não cópia do yaml. `00-harness.md` Grok intacto (hop só Grok).

**`process_event`:** G8 `bash` + `item-edit` Status → deny. Spec OpenCode Auto / process_event nos três. Sem aresta nova. T1/T7/T15 Alan-only no stub. `openspec/config.yaml` “OpenCode is not an active harness” fica para Apply (task 5.2) — correcto neste turno Design.

**#668 archive:** Non-Goal “OpenCode … MUST NOT be an active contract” e “Impeccable no Grok” são *revogados só na unicidade / detector*, como o issue manda. Lock machine morto no #562 **não** é revogado. Padrão de apply (núcleo → pele → stubs → AGENTS → specs → ensaio Auto) é o irmão, não um segundo processo.

### 4. Riscos operacionais (rubrica)

**Plugin não carregado = write passa.** Residual explícito, classe Grok sem `/hooks-trust`. Homologação 6.5 registra load em `.opencode/plugin/`. Binário 1.18.18: auto-load `*.js`/`*.ts` em `.opencode/plugin/` **ou** `plugins/` sem `opencode.json`; export `Plugin = (input, options?) => Promise<Hooks>` função, não objecto. Design versiona só singular (#395). Guard live-resolve não substitui o load. **accepted-residual.**

**#5894 `tool.execute.before` em subagent `task`.** Issue: verificar no Design no 1.18.18; se persistir, residual. Design: não live-testado em TUI/subagent; residual explícito; ensaio P0 = sessão principal; sem upgrade. Independente no binário 1.18.18: `tool.execute.before` dispara no *spawn* `task` com `{prompt, description, subagent_type, command}`, não nas writes internas do filho — compatível com a anomaly. 6.5 “observado se possível”. **accepted-residual**, não BLOCKED de Design (fronteira vazia; risco aberto no issue).

**Tool desconhecida → allow (#611).** D3 + G10 `grep`. Upgrade de API = card filho. **accepted-residual.**

**Auto claims.** D12 + spec + G15 + task 3.2: MUST NOT reivindicar Auto OpenCode/Grok. Ensaio bloqueia Auto, não o merge. **false** (fechado).

**AGENTS.md budget.** 14 linhas não-vazias hoje; três nomes cabem num bullet; teste ≤40 já existe (`test_agents_md_is_stub`). **false.**

**Throw vs JSON.** D6: 1.18.18 não honra `{permission, decision}`; deny = `throw`; allow = void; `decide()` continua dual JSON para Cursor/Grok *e* para o plugin ler antes do throw. Spec plugin throw vs G1–G12 JSON. Task 6.2: teste de throw, não JSON permission. Binário: `yield* trigger("tool.execute.before", {tool, sessionID, callID}, {args})` antes de `u.exec`. Throw TUI real = ensaio (Open Questions). **false** no desenho; residual de homologação.

**Paging inject vs hop Grok.** D7 fecha inject. Spec: OpenCode `output.system.push` do mesmo texto Cursor `additional_context`; Grok permanece arquivo gitignored + `00-harness.md`. Scenario “does not use the Grok gitignored hop”. Binário: `plugin.trigger("experimental.chat.system.transform", {sessionID, model}, {system})` e concatena partes extra depois do header — alinhado ao risco “push vs merge bloco 0”. **false.**

### 5. Specs / tasks vs design.md (G1–G16 vs task 6.1 G1–G12)

Design G1–G16 são o aceite de teste. Tasks:

| Golden | Task |
| --- | --- |
| G1–G12 (dialeto + empty path + três clientes + fallback) | 6.1 (texto “G1–G12”) |
| G13 paging ≤20; G14 detector adapter; plugin throw | 6.2 |
| G15 AGENTS.md; G16 `.opencode/` | 6.3 |

Não há furo: 6.1 não “esquece” G13–G16; o split espelha #668 4.1 / 4.2 / 4.3. Wording de 6.1 é só o bloco núcleo. **false** como P1; **P3** de clareza.

Títulos OpenSpec MODIFIED conservam o nome canónico (`Process law has one nucleus and two adapters`) com corpo “three” — correcto para apply não deixar a requirement velha “OpenCode MUST NOT” viva ao lado de uma ADD com outro título. Heading stale = P3, não conflito pós-archive.

`cursor-harness` “Column gate is always-on” (main) ainda descreve paging Cursor+Grok só. Delta de paging OpenCode vive em `process-fsm-paging` ADDED. Sem colisão normativa; Apply pode não retocar essa frase. P3.

`developer-tooling` MODIFIED substitui “`.opencode/` MUST NOT permanecer como contrato activo” por plugin auto-load + `opencode.json` proibido. Scenario Cursor deixa de tratar `.opencode/` como tabu absoluto. Coerente.

### 6. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy | **none** — fora (task 1.4 / 6.4) |
| `backend/` de produto | **none** |
| Protótipo HTML / Playwright | **N/A** — sem pasta `prototypes/*720*`; Prototype N/A |
| Rubrica Impeccable (fidelidade/carga/a11y/viewport) | **N/A** — sem UI de produto |
| Detector `hook.mjs` em Grok/OpenCode | pele de harness (alarme pós-edit UI); não é tela; fail-open |
| TUI OpenCode / Grok | **vendor** — Non-Goal |

`UI impact: none` + Prototype N/A + pipeline Impeccable *desta coluna* N/A estão justificados e alinhados ao issue (“Pipeline Impeccable *deste* card (critique A/B de tela nova) = N/A. Detector automático em sessões futuras = **entra**.”). Não falta protótipo.

### 7. Apply contract implementável?

Sim, no mesmo padrão #668, com o binário 1.18.18 a confirmar os nomes.

Ordem D11: (1) `normalize`/`extract_path` + G1–G12 (2) fallback bash `{tool, args}` (3) `.opencode/plugin/process-fsm-guard.js` throw (4) transform paging (5) stubs + zero opsx (6) detector Grok + plugin impeccable (7) `AGENTS.md` + decision-log + `openspec/config.yaml` + specs main.

Pontos de Apply (não BLOCKED):

- Plugin Guard: serializar `{ tool, args }`, `cwd` de `directory`/`worktree`, spawn `guard.py` (ou o wrapper `.cursor/hooks/process-fsm-guard.sh` para herdar G12), ler `permission`/`decision`, **throw** só no deny; crash/parse → não throw (fail-open) *salvo* se Apply optar por fail-closed à Cursor Write — o issue não exige fail-closed no OpenCode.
- Detector: reusar o mapeamento de `impeccable.sh` (`afterFileEdit`→`hook_event_name=PostToolUse`, `stop`→`Stop`; `filePath`→`file_path`). Grok: ficheiro JSON *aditivo* (ou secções novas no `process-fsm.json`) com timeout >30s no Stop. OpenCode: módulo separado, catch-all, nunca throw.
- `PATH_KEYS` += `filePath`; parse `patchText` com os quatro marcadores live; `bash` ∈ shell set (≠ `Bash`).
- Empty-path deny **antes** do early-return, só no conjunto write OpenCode; Status-edit / sidecar continuam primeiro.
- Stubs: um por `.cursor/skills/*` (16 skills); skip `.agents/skills/{impeccable,design-critic,playwright-cli}`. Preferir gerador irmão de `grok_stubs.py` se extraído (Apply contract “se extraído”).
- Não editar yaml T0–T17, `process_event`, Guard/paging Grok, `frontend/src/`, produto `backend/`.
- `openspec validate` da change já verde neste turno.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: `#5894` — `tool.execute.before` no 1.18.18 observa-se no spawn `task` (args = prompt/agent), não nas writes do subagent. Design não fez ensaio TUI; residual explícito + 6.5. Disposition: **accepted-residual**.
- P2: Plugin não carregado / folder untrusted = write passa. Classe Grok sem trust. Homologação registra load. Disposition: **accepted-residual**.
- P2: Task 2.1 chama `guard.py` directo (texto do issue); G12/task 1.3 são o fallback do wrapper Cursor/Grok. Python-down no OpenCode pode fail-open salvo Apply ligar o wrapper. Disposition: **accepted-residual**.
- P2: Tool nova fora da lista canónica → allow (#611 / G10). Upgrade = filho. Disposition: **accepted-residual**.
- P2: Stubs OpenCode sem gerador/CI stale (Grok tem `grok_stubs.py`). Issue não exige gerador; G16 cobre ≤8 / sem T0–T17. Disposition: **accepted-residual**.
- P3: Task 6.1 diz “G1–G12”; G13–G16 estão em 6.2–6.3. Disposition: **false** como furo; nit de wording.
- P3: Requirement title `one nucleus and two adapters` com corpo “three” (nome OpenSpec conservado de propósito). Disposition: **accepted-residual**.
- P3: `cursor-harness` “Column gate is always-on” main continua a citar só paging Cursor+Grok; inject OpenCode está em `process-fsm-paging`. Disposition: **accepted-residual**.
- P3: Sem golden explícito `*** Move to:`; lista canónica + G3 Update File chegam. Disposition: **accepted-residual**.
- Auto claims / AGENTS.md >40 / throw-vs-JSON / inject-vs-hop / dual-write T0–T17 / regressão Guard #668 / superfície visual sem classificar: **false**.

## Disposition

Zero P0/P1 abertos. P2 = residuais do issue (plugin load, #5894, #611, Python-down, stubs sem CI) já nomeados para ensaio/Apply, não recorte. Não editar `design.md` por estes P2.

## Verdict

**PASS** (zero P0/P1 aberto; Prototype N/A justificado; `openspec validate --strict` valid)

## Snapshot

`.impeccable/critique/720-card-720-opencode-three-adapters-20260827T201003Z-A.md`

Visual/Playwright: N/A (`UI impact: none`).
