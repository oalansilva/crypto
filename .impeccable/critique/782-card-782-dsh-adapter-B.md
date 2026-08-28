# Snapshot — card #782 `card-782-dsh-adapter` (Assessment B, ROUND 2)

- Card: #782
- Change: `card-782-dsh-adapter`
- Critic: isolated Design Critic B (detector posture; no transcript inherit; no Assessment A)
- UTC: 2026-08-28T19:20:50Z
- Tuple: hooks `q=None` `bound_card=⊥` `q_git=develop` (sessão unbound). Board Project 1 Status=**Design**. Write produto deny. Esta onda só `.impeccable/critique/**`.
- UI impact: none (harness/hooks/docs; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A confirmed (sem HTML, sem `frontend/public/prototypes/` desta change; Playwright visual **não** correu)
- Detector/browser desta coluna: N/A justificado — sem superfície visual. Detector **de pele** (dsh → `hook.mjs`) criticado contra `mapAfterPayload` OpenCode live e o contrato D16.
- `design.md` sha256: `8ff88e5f642be7a4b76053a680532f0764f20027e0e32c3b4536bcf8d671f7b6` (bate com o prompt do polish; 2945 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + seis spec deltas)
- `openspec validate card-782-dsh-adapter --type change --strict`: **valid**
- Probe HTTP: `http://127.0.0.1:3080` → **401**. Residual launcher/auth, não UI de produto.
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).
- `.dsh/` ausente no disco: esperado em Design.

---

## Brief

Kaizen P1: quarto adapter DeepSeek Harness (`dsh`) sobre o mesmo `decide()` / `page()` / `hook.mjs`. Round 1 B = **BLOCKED** em três P1s de ouro. Este round re-sonda código vivo **e** o contrato polido. PASS só se os três P1s não colapsam mais e não há P0/P1 novo.

---

## Probes (live, este worktree, pré-Apply)

`decide()` / `extract_paths()` / `normalize()` em envelopes nativos, com overlay fixture e `status` inject. `str_replace_editor` **não** está em `WRITE_TOOLS` nem `OPENCODE_WRITE_TOOLS`. `PATH_KEYS` já tem `path` e `file_path`. `normalize()` copia `args.command` (verbo do editor) para `_command()`.

### Guard envelopes → paths / permission

| Envelope | `extract_paths` | permission | reason (live) |
| --- | --- | --- | --- |
| D1 `write` + `file_path` produto, develop | `[backend/app/tasks/discovery_tasks.py]` | **deny** | `I1` |
| D2 `edit` + `file_path` frontend, develop | `[frontend/src/x.tsx]` | **deny** | `I1` |
| D3 `write` `file_path=""` | `[]` | **deny** | `empty_path` |
| D4 `edit` `file_path=""` | `[]` | **deny** | `empty_path` |
| D5 `bash` `tee` produto | `[backend/app/main.py]` | **deny** | `I1` |
| D6 `bash` Status field | `[]` | **deny** | `status_item_edit` |
| D7 `edit` `openspec/.../design.md` Design+`card-782-*` | `[openspec/changes/card-782-dsh-adapter/design.md]` | **allow** | — |
| D8 `grep` | `[]` | **allow** | #611 |
| `read` + `file_path` produto | `[]` | **allow** | não está em `WRITE_TOOLS` |
| D10 `str_replace_editor` `str_replace` produto | `[]` | **allow** | fail-open; `cmd='str_replace'` |
| D10b `insert` produto | `[]` | **allow** | fail-open; `cmd='insert'` |
| `create` produto (path preenchido) | `[]` | **allow** | fail-open; `cmd='create'` |
| D10c `str_replace` OpenSpec Design+card | `[]` | **allow** | **sem** extract; coincidência, não D7 |
| D11 `view` produto | `[]` | **allow** | (também não extrai `path`) |
| D12 `create`/`str_replace`/`insert` `path=""` | `[]` | **allow** | **não** `empty_path` |
| `view` `path=""` | `[]` | **allow** | — |
| D13 `cordis_define` | `[]` | **allow** | restrict é pele |
| D14 `workflow` | `[]` | **allow** | #611 |

Live já fecha `write`/`edit`/`bash`+`file_path`. O buraco restante no `decide()` é `str_replace_editor` (e o plugin ainda não existe). Isso é esperado em Design; o ouro do contrato é que deve falhar até Apply.

### Detector OpenCode `mapAfterPayload` (live)

`scripts/process-fsm/opencode_plugin_lib.js` lê só `args.filePath` → `args.path` → `patchText`. **Não lê `file_path`.** `WRITEISH` live = `{write, edit, apply_patch, bash}`.

| Input | stdin `file_path` |
| --- | --- |
| `{tool:write, args:{file_path:"frontend/src/App.tsx"}}` | `""` |
| `{tool:edit, args:{file_path:"frontend/src/x.tsx"}}` | `""` |
| `{tool:edit, args:{filePath:"frontend/src/x.tsx"}}` | preenchido |
| `{tool:str_replace_editor, args:{path:"backend/app/main.py"}}` | preenchido (`path`) |
| `{tool:write, arguments:{file_path:...}}` (sem `args`) | `""` |

Copy deste mapper no dsh = detector no-op em todo `write`/`edit` nativo.

### Overlay schema (live)

- `SCHEMA_MAJOR=1`; `CLIENT_KEYS=("cursor","grok","opencode")`
- omit `clients.dsh` → `validate_overlay` **PASS**
- extra `clients.dsh.auto: false` → **PASS**
- extra lixo `clients.dsx` → **PASS** (não há rejeição de chave desconhecida)
- `--init` / `empty_template` / `dump_template`: **sem** `dsh`
- overlay Cripto live: `pin: v1.0.1`, sem `clients.dsh`
- `render_agents()`: três nomes (sem dsh)

### Presets `/tmp/deepseek-harness`

- `dsh web` / `web-app`: `tool-fs` e `tool-str-replace-editor` **disabled: true**; preset **standard** remonta `tool-fs` (`write`/`edit` + `file_path`).
- `str_replace_editor` ligado em: bundle **`sdk-minimal`**, agent preset web **`minimal`**, e row `dsh-base` (antes do overlay web desligar).
- Contrato D4 correto: goldens da tool existem porque a família runtime a monta, não porque o web default a exponha.

---

## Prior P1s (round 1) — re-probe do contrato

### P1-1 D10/D12 `str_replace_editor` — **CLOSED**

Round 1: deny-only + empty-path colapsava; `_command()` rouba o verbo; faltava `extract_paths`, allow Design+`card-*`, golden `insert`, preset web vs minimal.

Contrato agora (não só wording):

- Decision 4: mutate via **`extract_paths(args.path)`**; `args.command` MUST NOT virar `_command()` de shell; MUST NOT despejar a tool em `WRITE_TOOLS`; editor no preset **`sdk-minimal`** (web-app default desliga).
- Golden **D10**: deny **e** `extract_paths()==["backend/app/main.py"]` (não empty_path).
- **D10b**: `insert` + `extract_paths()==["backend/app/main.py"]`.
- **D10c**: Design+`card-782-*` allow **e** `extract_paths()==[openspec/changes/card-782-dsh-adapter/design.md]`.
- **D12**: empty_path **e** `extract_paths()==[]` (create/str_replace/insert).
- Spec `process-fsm-guard`: *«Mutating `str_replace_editor` (`command` `create`, `str_replace`, or `insert`) MUST be classified as a product write via `extract_paths(args.path)`»*; cenário mutate **AND** `extract_paths()` equals `["backend/app/main.py"]` **AND** deny is `write_produto`, not empty-path; insert; OpenSpec allow; create/insert empty **AND** `extract_paths()` is empty.
- Tasks **1.1 / 1.2 / 7.1**: D10/D10b/D10c MUST assert `extract_paths()`; D12 `extract_paths()==[]` + empty_path; MUST NOT promover `args.command` a shell; MUST NOT despejar a tool em `WRITE_TOOLS`.

Colapso round 1 (meter a tool em `OPENCODE_WRITE_TOOLS` sem ler `args.path`): D10 falha (`extract_paths` não é o path). Deny-all mutate: D10c falha. Dump da tool inteira em `WRITE_TOOLS`: D11 falha (`view` de `backend/` viraria `write_produto`). Live atual (allow + `extract_paths==[]`) falha D10/D10b/D12. **Não colapsa.**

### P1-2 D16 detector / `file_path` — **CLOSED**

Round 1: copy de `mapAfterPayload` OpenCode deixa `hook.mjs` vazio em `arguments.file_path`.

Contrato agora:

- Decision 5: `dsh_plugin_lib.js` é irmão, **não** copy-paste; alternativa rejeitada: reexportar `mapAfterPayload` OpenCode.
- Decision 10: MUST ler **`file_path` primeiro**, depois `path`; MUST NOT reutilizar o mapper OpenCode.
- Golden **D16**: `arguments.file_path` de UI **sem** `filePath` → stdin `file_path` **preenchido** (não o mapper OpenCode).
- Spec `developer-tooling` / `process-harness`: *«lê `arguments.file_path` primeiro (envelope nativo; sem `filePath`) e depois `path`»* **AND** *«MUST NOT ser o `mapAfterPayload` OpenCode»*.
- Tasks **2.1 / 4.1 / 7.2**: mapper próprio; fixture `file_path` sem `filePath`; MUST NOT copiar o OpenCode.

Live: OpenCode mapper + `args.file_path` → `file_path=""`. Um copy falha D16. **Não colapsa.**

### P1-3 D19 extra `clients.dsh` — **CLOSED**

Round 1: D19 omit já é verde hoje; não testemunha o write Cripto; rejeitar `clients.*` extra com `SCHEMA_MAJOR=1` quebraria o pin.

Contrato agora:

- Decision 1 / Apply contract: *«Apply MUST NOT passar a rejeitar chaves `clients.*` desconhecidas»*.
- **D19** omit (regressão) **e** **D19b**: overlay **com** `clients.dsh.auto: false` valida.
- Spec `covenant-flow`: cenário *«Overlay with extra clients.dsh auto false validates»* **AND** *«Apply MUST NOT start rejecting unknown `clients.*` keys while `SCHEMA_MAJOR` remains 1»*; cenário *«Cripto records auto false»* + `CLIENT_KEYS` still three.
- Tasks **3.3 / 7.1**: D19 omit + D19b extra presente.

Rejeitar extras quebra D19b. Meter `dsh` em `CLIENT_KEYS` quebra D19 omit. **Não colapsa.**

---

## Remaining findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- Tasks 1.x–4.x ainda apontam paths do worktree consumidor; Apply contract é produto `oalansilva/covenant-flow` tag `v1.1.0` depois pin. Produto live `install.sh` faz `rsync -a --delete` de `.opencode/` e **não** copia `.dsh/`. Consumer-first + pin apaga o núcleo. Contrato salva; tasks podem desviar.
- Plugin não carregado / `--patch` omitido = waterfall default `allow` = write passa. Homologação 8.1. **accepted-residual.**
- OpenCode live `WRITEISH = {write, edit, apply_patch, bash}` sem `str_replace_editor`. Decision 7 inclui mutate no write-like fail-closed; spec D20 cenário só `write`/`edit`. Task 2.2 serializa **todo** `pre-execute` para `decide()` (mitiga). Residual: fail-closed sem JSON no mutate se o plugin copiar o set OpenCode.
- `:3080` 401; inventário autenticado residual 8.1.
- `workflow` / `subagent` / MCP / tool nova → allow (#611). D8/D14.
- Paging `systemPrompt.section` não entra no agent preset `minimal` (`persona.complete: true`); Guard ainda resolve `q`.
- Dois remotes (tag produto, depois pin Cripto). Canal v1 #773.
- Proposal Why («Guard não vê `file_path`») está stale; Context do design está certo. Risco: Apply reescrever `normalize()`.

### P3

- D10/spec dizem deny `write_produto` com `q_git=develop`; live nesse ramo é `reason=I1` (G3 da #720: `extract_paths` + deny + `empty_path` not in reason). Apply MUST espelhar G3, não o token `write_produto` na string.
- Sem golden nomeado para `create` com path preenchido (SHALL + task 1.1 já listam `create`; D12 cobre vazio).
- Agent preset web `minimal` também monta `str_replace_editor`; o contrato nomeia `sdk-minimal` (correto) + dsh-base. Ouro é da tool, não do preset.
- Títulos OpenSpec stale (`two adapters` / `three clients`) com corpo four.
- `empty_path` live ainda diz «OpenCode»; Design MAY alargar.
- `render_agents()` live 14 linhas / três nomes; D17 acresce dsh.
- Task 7.4 `openspec validate` sem `--strict` no texto (este turno: `--strict` verde).
- `guard.py` docstring «Cursor + Grok + OpenCode».
- `PreToolDecision.ask` existe; D20 exige `{ kind: 'deny' }`.
- `pwsh` no preset Windows = #611 no host Linux.

---

## Audit

- A11y / responsive / browser / detector visual: N/A (`UI impact: none`). Prototype N/A confirmed. Playwright visual não correu.
- Dual critic / T7: snapshot desta coluna = este arquivo (round 2 overwrite).
- FSM yaml: sem task de estado/evento/`enabled_tools`. T1/T7 Alan; T5 parent. I1–I9 / T0–T17 não reabertos.
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Dual-write da lei: D17/D18 + spec Dual-write forbidden. Não está no Apply.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados; extra testemunhada por D19b.

---

## Disposition

Zero P0/P1. Os três P1s do round 1 estão fechados em design + specs + tasks com goldens que não colapsam (D10/D10b/D10c `extract_paths`, D16 `file_path` nativo, D19b extra + MUST NOT rejeitar `clients.*`). Live ainda fail-open em `str_replace_editor` e no mapper OpenCode — Apply deve verdear esses goldens, não o contrário. Residuais P2/P3 (plugin load, 401, #611, dois remotes, tasks vs produto-primeiro) não bloqueiam. Detector/browser visual N/A. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

### Verdict

**PASS**
