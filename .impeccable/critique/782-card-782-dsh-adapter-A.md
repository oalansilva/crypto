# Snapshot — Assessment A · ROUND 2 · card #782 `card-782-dsh-adapter`

- Card: #782 kaizen P1 — Harness: quarto adapter DeepSeek dsh — uma lei, quatro clientes
- Change: `card-782-dsh-adapter`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested critic)
- Modelo: inherit
- UTC: 2026-08-28T19:20:00Z
- Round: **2** (round 1 PASS com P2/P3; B BLOCKED com 3 P1; autor patchou o contrato)
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Prompt do pai: tratar worktree como `q=Design` `bound_card=782` `q_git=card-782-dsh-adapter`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `8ff88e5f642be7a4b76053a680532f0764f20027e0e32c3b4536bcf8d671f7b6` · **2945** palavras (`wc -w`) · 23043 bytes — bate com o reivindicado
- Round 1 digest (obsoleto): `ed496aeef464041c584dc0e55b209483780298b6f8fdb4415ba3ffc5442abb34` (2516 palavras)
- UI impact: **none** (harness/hooks/docs/specs/testes de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** — `UI impact: none`; sem HTML em `frontend/public/prototypes/` desta change; aceite visível = deny Cordis `{ kind: 'deny' }`, inject Moore, `hook.mjs` fail-open. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright.
- `openspec validate card-782-dsh-adapter --type change --strict`: **verde**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois de A/B)
- Method: issue #782 body + 3 comments; `proposal.md` / `design.md` (D1–D20 + D10b/D10c/D19b) / `tasks.md` 1–8; deltas `process-harness` `covenant-flow` `process-fsm-guard` `process-fsm-paging` `developer-tooling` `cursor-harness`; live `guard.py` `overlay.py`; `.opencode/plugin/*.js` + `opencode_plugin_lib.js` `mapAfterPayload`; source `/tmp/deepseek-harness` (web-app disable, `dsh-base` row, preset web `minimal`, bundle `sdk-minimal`); probe `decide()`/`extract_paths()`/`validate_overlay()` neste worktree.

---

## Brief

Quarto adapter `dsh` = tradução sobre o mesmo `decide()` / `page()` / `hook.mjs`. Fonte em `oalansilva/covenant-flow` tag **`v1.1.0`**; Cripto copia no pin. Sem dual-write da lei. Sem Auto dsh. Sem Claude-bridge como Guard. `CLIENT_KEYS` três; `SCHEMA_MAJOR=1`; `clients.dsh` extra opcional. `UI impact: none`.

Round 2: re-verificar os três P1 do B contra o contrato patchado. Não relitigar Apply-ainda-não-implementado como P0/P1.

---

## 1. Escopo vs DoD grelhado (issue #782)

Body live: fronteira vazia; Q1=A; Q2=A. Três comments (T0 / recorte produto-consumidor / grill). Design não reentrevista.

| Entra do issue | Onde no pacote (pós-patch) |
| --- | --- |
| Quarto adapter; dsh **não** é yaml | D1; spec `process-harness` Fourth harness is not the law |
| Pele em `oalansilva/covenant-flow`; pin `v1.1.0` | D1; Apply contract (1)(2); tasks 5.x / 6.x |
| `CLIENT_KEYS` três; extra opcional; `SCHEMA_MAJOR=1`; `--init`/`--pin` não emitem/injetam | D1; D19+**D19b**; spec `covenant-flow` ADDED; task 3.3 |
| Overlay Cripto **escreve** `clients.dsh.auto: false` | Apply contract; task 6.1; D19b testemunha o write |
| `render_agents()` sempre quatro nomes; sem Auto dsh; ≤40 | D2; D17; spec Always-on |
| Plugin Cordis nativo; **não** Claude `hooks.json` | D5–D7; D20; task 2.5 |
| `pre-execute` `{ kind: 'deny' }`; write-like sem JSON = fail-closed | D7; D20; tasks 2.1–2.2 |
| Moore `page()` ≤20 via inject | D8; D15; spec paging |
| Detector `post-execute` + `turn-stopping` → `hook.mjs`; fail-open | D10; **D16 `file_path` first**; tasks 2.1 / 4.1 |
| Dialeto `{ tool, args }` `write`/`edit` `file_path`; `bash` `command` | D3–D4; D1–D9; tasks 1.1–1.3 |
| Empty `file_path` write/edit **não** allow | D3/D4; spec Empty |
| Inventário `str_replace_editor` / workflow / MCP / `cordis_*` | D4; D10–D14; D10b/D10c |
| Tool que desmonta Guard = restrict na pele | D11; D13; task 2.2 |
| Ensaio deny = Auto, **não** merge | D13; task 8.1 |
| Sem produto `backend/` / `frontend/src/`; UI none | UI impact / Prototype N/A; task 1.4 / 7.4 |

**Não entra — não reaberto:** vendorar DeepSeek; overlay/board/URLs no produto; #608/#720/#773; T0–T17 em `.dsh/` ou Claude hooks; Auto sem ensaio; Clara/Hermes; `clients.dsh` obrigatório; pin `v2.0.0`; porta 3080 em services; UI/HTML; dsh = lei.

Vocabulário do issue intacto. Proposal «New Capabilities: (nenhuma)» correcto.

---

## 2. Dual-write da lei

Contrato fechado:

- Núcleo = yaml + `scripts/process-fsm/` + skills canónicas + stub `AGENTS.md`.
- Adapter = tradução (plugin Cordis, stubs ≤8 MUST Read, patch ids). D18: `.dsh/` sem T0–T17; sem hooks.json Claude.
- Paging = `page()` compilador; inject `section({ name: 'covenant-flow:moore', text: fn })`; **não** hop Grok gitignored.
- Spec Dual-write forbidden alarga a `.dsh/`. Stubs: `dsh_stubs.py` espelho; não duplicar `.agents/skills/`.
- Dual-write Hermes / `~/.codex/`: Non-Goals.

**false** como furo.

---

## 3. Fail-closed vs Claude-bridge

Live `/tmp/deepseek-harness`: deny `{ kind: 'deny' }` **sem** `next()`; throw no listener → `isError` (não policy deny); Claude bridge parse fail → nenhum hook (fail-open); detector **nunca** `steer` / **nunca** `{ kind: 'block' }`.

Design D7/D20: `{ kind: 'deny', reason }`. Alternativa rejeitada: throw. Alternativa rejeitada: Claude como Guard. Dois módulos Guard ≠ detector. **Correcto. Não reabrir.**

Decision 7 agora inclui `str_replace_editor` mutante e `cordis_*` lifecycle no conjunto write-like fail-closed (fecha o P2 do B sobre WRITEISH só `{write,edit,bash}`). O cenário da spec do plugin ainda exemplifica só `write`/`edit` — residual P3, não buraco: o SHALL é «Write-like tools» e D7 nomeia o conjunto.

---

## 4. Pin `v1.1.0` vs major + fecho D19b (P1 do B #3)

Live: `SCHEMA_MAJOR = 1`; `CLIENT_KEYS = ("cursor", "grok", "opencode")`; falta da tupla = `OverlayInvalid`; extra em `clients` **não** é enumerado (passa). Overlay Cripto live **omite** `clients.dsh` (`pin: v1.0.1`). `--init` template **não** emite `dsh`.

Probe neste worktree:

| Caso | Resultado live |
| --- | --- |
| overlay sem `clients.dsh` (D19) | `validate_overlay` PASS |
| overlay **com** `clients.dsh.auto: false` (D19b) | PASS (já hoje) |
| extra lixo `clients.junk` | PASS |
| `dump_template()` tem `dsh:` | **False** |

O P1 do B era: D19 omit já-verde não prende Apply que passe a rejeitar extras sob `SCHEMA_MAJOR=1`. **Fechado:**

- Decision 1: Apply MUST NOT rejeitar `clients.*` desconhecidas.
- D19 **omit permanece**; **D19b** extra `auto: false` valida (testemunha o write Cripto).
- Spec ADDED cenário «Overlay with extra clients.dsh auto false validates» + SHALL «Apply MUST NOT start rejecting unknown `clients.*` keys».
- Task 3.3 / 7.1 citam D19 **e** D19b.
- D19+D19b juntos: meter `dsh` em `CLIENT_KEYS` quebra D19 (Clara omit); rejeitar extras quebra D19b.

Pin minor correcto. Q1=A intacta.

---

## 5. Empty-path + `str_replace_editor` (P1 do B #1)

Live (pré-Apply, esperado):

| Envelope | `extract_paths` | `decide()` |
| --- | --- | --- |
| D1 `write` + `file_path` produto | `[backend/…]` | deny `todo-write` |
| D2 `edit` + `file_path` frontend | `[frontend/src/…]` | deny `todo-write` |
| D3/D4 empty `file_path` | `[]` | deny `empty_path` (mensagem ainda «OpenCode…») |
| D5 `bash` tee produto | `[backend/app/main.py]` | deny `todo-write` |
| D7 `edit` OpenSpec Design | path design | **allow** |
| D8 `grep` | `[]` | allow #611 |
| D10/D10b mutate/insert produto | **`[]`** | **allow** (fail-open; `_command()` rouba `args.command='str_replace'`) |
| D10c mutate OpenSpec | `[]` | allow **pela razão errada** (missing-path, não glob design) |
| D11 `view` | `[]` | allow |
| D12 empty create/insert/str_replace | `[]` | **allow** (não está em `OPENCODE_WRITE_TOOLS`) |
| `create` nonempty produto | `[]` | allow |
| `cordis_define` | `[]` | allow (restrict é pele D13) |
| D14 `workflow` | `[]` | allow #611 |

`PATH_KEYS` já tem `path` e `file_path`. `WRITE_TOOLS` já tem `write`/`edit`. `normalize()` copia `args.command` → campo shell (`'str_replace'`). MUTATION_RE não casa esses verbos.

**Contrato pós-patch (fecha o colapso G4/G5):**

- D10: deny **`write_produto`** **e** `extract_paths()==["backend/app/main.py"]` (não empty_path).
- D10b: `insert` mutate deny **e** `extract_paths()==[produto]`.
- D10c: mutate OpenSpec Design+`card-782-*` **allow** **e** `extract_paths()==[design.md]` (impede deny-all-mutate).
- D12: empty_path **e** `extract_paths()==[]` (create + o mesmo vazio para str_replace/insert). Spec: cenários create empty **e** insert empty.
- D11: `view` allow; `evaluate(write_produto)` não corre.
- Decision 4 + spec SHALL: mutate via **`extract_paths(args.path)`**; MUST NOT promover `args.command` a shell; MUST NOT despejar a tool inteira em `WRITE_TOOLS` (view de `backend/` viraria write_produto via `bool(command)`).
- Editor: **sdk-minimal** (não default web). Live confirma: `web-app` `tool-str-replace-editor: disabled: true`; row existe em `dsh-base`; bundle `sdk-minimal` monta a tool; **também** o preset de sessão web `minimal` (`packages/preset/agent-presets/presets/minimal/`) — inventário um pouco mais largo que o texto D4 (P3).
- Mensagem empty_path MUST NOT citar só “OpenCode”. Task 1.1/1.2.

Naive dump-em-`WRITE_TOOLS` falha D11. Dump-só-em-`OPENCODE_WRITE_TOOLS` falha D10 (`extract_paths` vazio). Empty-path-deny sem parse falha D10. Deny-all-mutate falha D10c. **O colapso do P1 está fechado no ouro.** `.dsh/` código ainda não existe — Design, não Apply.

---

## 6. Detector mapper (P1 do B #2)

Live `opencode_plugin_lib.js` `mapAfterPayload`:

1. `args.filePath`
2. senão `args.path`
3. senão `patchText`

Probe ESM neste worktree:

| Fixture | stdin `file_path` |
| --- | --- |
| `{ tool: write, args: { file_path: frontend/src/x.tsx } }` **sem** `filePath` | **`""`** (no-op) |
| `{ args: { filePath: … } }` | preenchido |
| `{ args: { path: … } }` (str_replace) | preenchido (OpenCode lê `path` no 2º ramo) |

Envelope default `dsh web` = `write`/`edit` + **`file_path` frozen**. Copy do mapper OpenCode deixa `hook.mjs` vazio em toda edição UI do preset standard.

**Contrato pós-patch:**

- Decision 5: `dsh_plugin_lib.js` irmão, **não** copy-paste; alternativa rejeitada: reexportar `mapAfterPayload` OpenCode.
- Decision 10: `mapAfterPayload` MUST ler **`file_path` primeiro**, depois `path`, só então fallbacks. MUST NOT reutilizar o OpenCode.
- D16: fixture `arguments.file_path` de UI **sem** `filePath` → stdin preenchido; nunca block/steer; exit 0.
- Spec `process-harness` + `developer-tooling`: cenário dsh post-execute com `file_path` e AND «MUST NOT be the OpenCode mapper».
- Tasks 2.1 / 4.1 / 7.2.

**Fechado.** Residual P3: D16 não exige pytest negativo `import { mapAfterPayload } from opencode_plugin_lib` — o fixture snake_case já falha o mapper OpenCode (provado neste turno).

---

## 7. Restrict Cordis / produto vs consumidor

Sete tools live (`cordis_define` / `run` / `stop` / `undefine` / `inspect_*`). D11 prefixo `cordis_` excepto inspect, **antes** de `decide()` glob. D13 golden do **plugin**. Host runner sem tool modelo ≠ deny. Residual web bundle sem `dsh-tool-cordis`.

| Onde | O quê |
| --- | --- |
| Produto tag `v1.1.0` | `.dsh/` + lib/goldens + `install.sh` copia `.dsh/` sempre + `render_agents` quatro nomes |
| Cripto no pin | cópia `.dsh/`; `pin: v1.1.0`; **edit** `clients.dsh.auto: false` |
| Não sobe | overlay Cripto, board, systemd, overlay_doc, monorepo DeepSeek, `:3080` |
| Não entra no Cripto Apply | `backend/` / `frontend/src/` de app |

Ordem Apply (1) produto (2) pin = canal v1. `dsh plugin add` → `$DSH_HOME` rejeitado. Helper `--patch` com `name` absoluto.

---

## 8. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy | **none** — fora |
| `backend/` de app | **none** |
| Protótipo HTML / Playwright / `DESIGN.md` | **N/A** — sem pasta `prototypes/*782*` |
| Rubrica Impeccable visual | **N/A** |
| Detector `hook.mjs` em sessões dsh | pele de harness; fail-open; **entra** |
| UI dsh `:3080` | **vendor** — Non-Goal; 401 launcher |

`UI impact: none` + Prototype N/A justificados.

---

## 9. Goldens D1–D20 vs live vs contrato

| Golden | Live hoje | Contrato pinta o delta? |
| --- | --- | --- |
| D1–D9 write/edit/bash/`file_path`/empty/Design/grep/quatro dialetos | D1–D8 já verdes; D9 falta ouro `file_path` vs G11 `filePath` | sim (regressão, não fecho de comportamento) |
| D10 write_produto + `extract_paths` | allow, paths=[] | **sim — fecha P1 colapso** |
| D10b insert + `extract_paths` | allow, paths=[] | **sim** |
| D10c Design allow + `extract_paths` | allow pela razão errada | **sim** |
| D11 view allow | allow | sim; D11 falha dump em `WRITE_TOOLS` |
| D12 empty mutate empty_path + paths=[] | allow | sim |
| D13 restrict plugin | decide() allow | sim (pele) |
| D14 workflow #611 | allow | sim |
| D15 page() ≤20 sem release-guard | reuso OpenCode | sim |
| D16 mapper `file_path` sem `filePath` | OpenCode mapper devolve `""` | **sim — fecha P1 detector** |
| D17 AGENTS.md quatro nomes | live 3 nomes / 14 linhas | sim |
| D18 `.dsh/` sem T0–T17 | `.dsh/` ainda não existe | sim |
| D19 omit `clients.dsh` | já verde | permanece |
| D19b extra `auto: false` | já verde | **sim — fecha P1 schema** |
| D20 fail-closed `{ kind: 'deny' }` | plugin dsh N/A | sim; D7 inclui mutate/cordis |

Tasks 7.1–7.3 mapeiam D1–D20 incluindo D10/D10b/D10c `extract_paths`, D16 snake_case, D19b.

---

## Achados

- P0: (nenhum)
- P1: (nenhum) — os três do B estão no contrato (verificados, não confiados na lista do autor)
- P2: Plugin não carregado / `--patch` omitido / `name` relativo / copy `export default` OpenCode em vez de `export function apply(ctx)` = waterfall default `allow`. Homologação 8.1 registra load. Disposition: **accepted-residual**.
- P2: Inventário autenticado `:3080` 401; source `/tmp/deepseek-harness` cobre web/base/minimal/sdk-minimal. Disposition: **accepted-residual**.
- P2: `workflow` / `subagent` / MCP `mcp__*` / tool nova → allow (#611) se não passarem no `pre-execute` do `ctx` raiz. D8/D14. Disposition: **accepted-residual**.
- P2: Tasks 1.x–4.x ainda soam a paths do worktree consumidor; Apply contract é produto `v1.1.0` depois pin; `install.sh` live `rsync -a --delete` de `scripts/process-fsm/` ainda não copia `.dsh/`. Consumer-first + pin apagaria o núcleo. Contrato de ordem salva; tasks podem desviar. Disposition: **accepted-residual**.
- P2: Proposal Why («o Guard não vê `{ tool, args }` com `file_path`») stale; Context do design e o live contradizem para `write`/`edit`/`bash`. Risco: Apply reescrever `normalize()`. Disposition: **accepted-residual**.
- P2: Processo actual em `/tmp/deepseek-harness` até relançar no canonical DEV. Disposition: **accepted-residual**.
- P3: Preset de sessão web **`minimal`** também monta `str_replace_editor`; D4/task 1.1 nomeiam sobretudo **`sdk-minimal`**. Envelope continua pinado por D10–D12. Disposition: **accepted-residual**.
- P3: Sem golden dedicado `create` nonempty (SHALL + task 1.1 nomeiam `create`; D10/D10b cobrem a classe; D12 cobre create vazio). Disposition: **accepted-residual**.
- P3: Títulos OpenSpec stale (`two adapters` / `all three clients` / `Three adapters ship`) com corpo four. Disposition: **accepted-residual**.
- P3: Mensagem `empty_path` live ainda diz «OpenCode»; Design MUST alargar (D3 Decision). Disposition: **accepted-residual** (contrato fecha; código é Apply).
- P3: Cenário spec fail-closed do plugin exemplifica só `write`/`edit`; Decision 7 inclui mutate/cordis. Disposition: **accepted-residual**.
- P3: D16 não exige import negativo do mapper OpenCode; fixture snake_case basta. Disposition: **accepted-residual**.
- P3: Paging `persona.complete: true` no preset web `minimal` pode sombrear `systemPrompt.section`; Guard ainda resolve `q`. Disposition: **accepted-residual**.
- P3: `PreToolDecision.ask` + approval host pode executar; D20/`kind: 'deny'` já exclui. Disposition: **accepted-residual**.
- Dual-write T0–T17 / Claude-bridge como Guard / pin major / `clients.dsh` obrigatório / Auto dsh / superfície visual sem classificar / Design Critique pré-PASS / produto UI / ouro D10 colapsável / mapper OpenCode como D16 / D19-omit-only: **false**.

## Disposition

Zero P0/P1 abertos. Recorte = DoD grelhado (Q1=A Q2=A). Os três P1 do Assessment B estão no `design.md` sha256 medido, nas specs e nas tasks — não só na lista reivindicada. Fail-closed nativo vs Claude fail-open permanece. Pin minor + D19/D19b prendem o anti-pattern de fechar extras sem major. Live já nega `write`/`edit`/`bash`+`file_path`; o delta restante (`str_replace_editor` via `extract_paths`, pele Cordis, mapper `file_path`, pin) é Apply após Pronto para Dev. P2/P3 residuais não bloqueiam. Não editar `design.md` por estes P2/P3.

## Verdict

**PASS** (zero P0/P1 aberto; Prototype N/A justificado; UI impact none classificado; round-2 P1s do B fechados no contrato)

## Snapshot

`.impeccable/critique/782-card-782-dsh-adapter-A.md`

Prototype: N/A — `UI impact: none`; harness/hooks/docs de processo; nenhuma tela de produto a prototipar; aceite = deny Cordis + Moore + detector fail-open no quarto cliente.
