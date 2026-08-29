# Snapshot — card #784 `card-784-dsh-608-always-on` (Assessment B, ROUND 2)

- Card: #784
- Change: `card-784-dsh-608-always-on`
- Critic: isolated Design Critic B r2 (detector posture; no transcript inherit; no Assessment A; no inherit of B r1 as authority — r1 só como lista de P1 a re-sondar)
- UTC: 2026-08-29T01:50:00Z
- Tuple: hooks `q=None` `bound_card=⊥` `q_git=develop` (sessão unbound). Write produto deny. Esta onda só `.impeccable/critique/**`.
- UI impact: none (harness/hooks/docs de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-784-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Sem superfície visual nova ou alterada. Detector Impeccable da pele dsh permanece o de #782; este card não o altera.
- `design.md` sha256: `a9c0c702048645d430d2e58ad5ef7ca736d4bed4a7f28a2d884eae81002cef0f` (2399 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + quatro spec deltas: `process-harness`, `process-fsm-paging`, `developer-tooling`, `covenant-flow`)
- `openspec validate card-784-dsh-608-always-on --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).

Round 1 B = **BLOCKED** num P1: ouro A4/A5/A10 não pinavam o contrato live `SkillProvider` que o first-request consome (thenable `list`/`get`, `candidate.provider`, `waitWithAbort`+`signal`, `get(candidate, options)`). Este round re-sonda código vivo **e** o contrato polido. PASS só se esse P1 não colapsa mais e não há P0/P1 novo.

---

## Brief

Always-on dsh (#608) após a pele #782: sessão `306d48f7` (cwd=`/home/ubuntu`, preset `standard`) tem Moore + Guard deny e **zero** stub `AGENTS.md` + **zero** `<available_skills>`. Native loader e `skill-filesystem` do preset resolvem projeto a partir do cwd da sessão. Este card: o mesmo plugin Guard compila o ficheiro `AGENTS.md` via `systemPrompt.section` order 40, publica catálogo `REPO_ROOT/.dsh/skills` via `ctx.skills.registerProvider` (scanner thin, não `FileSystemSkillProvider`), boot fail-closed se `canonical_paths.dev` set e não-dir, pin `v1.1.1`. Auto dsh permanece `false`. UI none.

Audience: operador dsh no consumidor pinado. Outcome: first-request com stub + `covenant-flow` no catálogo mesmo cwd≠repo; Guard deny intacto. Direction: um plugin, provider no JS, yaml sem skill paths. Scope: produto `v1.1.1` + pin Cripto; não reabrir #608/#720/#773/#782.

---

## Probes (live, este worktree, pré-Apply)

### Boot engole DEV inválido — **live TRUE; contrato fecha**

`scripts/process-fsm/dsh_boot.sh` linhas 36–40:

```bash
if [[ -n "$DEV_ROOT" && -d "$DEV_ROOT" ]]; then
  LAUNCH_DIR="$DEV_ROOT"
else
  LAUNCH_DIR="$REPO_ROOT"
fi
```

Overlay Cripto live: `canonical_paths.dev: /srv/apps/dev/criptofarol/source` (diretório). Path set e **não**-dir (ficheiro ou inexistente) cai no `else` em silêncio. Q6 / A7 / task 3.1: exit ≠0 + stderr nomeia o path; chave vazia → `REPO_ROOT`; dir válido ainda preferido (A9). Boot **não** seta workspace GUI (residual aceite: plugin é a garantia). Overlay python `except` → `dev = ""` → ramo vazio (fora do A7).

### Plugin / lib — **live ainda v1.1.0; esperado em Design**

- `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt"]` apenas; `tools/pre-execute` fail-closed; uma secção `covenant-flow:moore` order 50; **não** `registerProvider`; **não** secção agents.
- `dsh_plugin_lib.js`: só `node:` builtins (`child_process`, `fs`, `path`, `url`) + `spawnSync`. Sem `readAgentsStub` / sem provider. Sem `import 'yaml'` / `@deepseek-ai/dsh-skill-filesystem`.
- Consumidor **sem** `package.json` na raiz → import extra desses pacotes = plugin não carrega = Guard some. Decision 4 rejeita isso corretamente.
- `.dsh/cordis.patch.yml`: dois inserts (Guard + Impeccable); sem `customSkillDirs`; sem path `.dsh/skills`.
- `.dsh/` sem tabela T0–T17. Stubs: 17 `SKILL.md` (inclui `covenant-flow` e `grill-card`); corpos ponteiros MUST Read canónico.
- `AGENTS.md`: 19 linhas não-vazias; `NLU ≠ δ`; `Todo` não é código; quatro clientes; «Não reivindique modo Auto no Grok, no OpenCode nem no dsh.» Overlay `clients.dsh.auto: false`; `pin: v1.1.0`.

### Catálogo native (`/tmp/deepseek-harness`) — **contrato que o first-request consome**

Confirmado neste turno em `packages/skill/skill/src/index.ts` + `tool-skill` + `skill-filesystem` + preset `standard`:

- Host `web-app` desliga `id: skill-filesystem` e `id: tool-skill`. Registry `id: skill` (`@deepseek-ai/dsh-skill`) **fica** no host. Preset `standard` remonta filesystem **e** `tool-skill` na camada do preset. Comentário do preset: o catálogo mergeado **também** carrega o que o deployment registou globalmente (repository plugins).
- `dsh-tool-skill` first-request: `ctx.skills.snapshot({ cwd: agent.session.header.cwd, signal, scope: agent })`. Sem `snapshot.complete` **ou** zero model-invocable → **não** emite `<available_skills>`. First-request **sempre** passa `signal`.
- `registerProvider(create)` é síncrono; `create(control)` devolve `{ name, list, get }`. `runtime` reservado. Duplicados **na mesma camada** throw. Host plugin → camada **global**; preset filesystem → camada do preset. Nearest layer sombreia o mesmo `name`; rank só desempata **dentro** da camada.
- `waitWithAbort(x, signal)` com `signal` definido faz `x.then(...)`. Array síncrono → TypeError → provider skipped no `try` de `list()` → `snapshot.complete=false` → catálogo omitido (sintoma 306d48f7).
- `validateCandidate` **fora** do `try` de `list()`: exige kebab `name`, `description` string não-vazia, `source` string, `rank` finito, `provider === provider.name`, e se `invocation` existe **ambos** `modelInvocable`/`userInvocable` booleanos. Candidate sem `provider` rebenta `snapshot()`, não só skip.
- `SkillRegistry.get(name)` chama `provider.get(candidate, options)` e `validateDefinition` (`content` string).
- `isModelInvocable` lê `skill.invocation.modelInvocable` (não trata `invocation` ausente).
- `MemoryProvider` (`skill.spec.ts`): `async list` / `async get(candidate)`; cada candidate `provider: 'memory'`. `FileSystemSkillProvider.list` devolve **array** quando completo (`watch: false` → array); `{ candidates, complete: false }` só se o watcher falha. Isolado: `{ includeDefaultRoots: false, customSkillDirs: [root] }`, `CUSTOM_RANK = 300`.
- `parseInvocationPolicy` nativo: default `modelInvocable: true` / `userInvocable: true` quando o frontmatter não traz as chaves. Stubs `.dsh/skills` não trazem essas chaves — o thin MUST carimbar os booleanos no candidate (não depender do parser yaml do pacote).
- Import estático de `.dsh/plugin/*.js` resolve pela URL do ficheiro (árvore do consumidor). `inject: ['skills']` no filesystem package é o mesmo serviço host `ctx.skills`. `ctx.on("tools/pre-execute")` já funciona **sem** `inject: ["tools"]` (ensaio 306d48f7 deny PASS).

### Goldens #782 ainda no disco (pré-Apply)

- `_mock_ctx_prelude` **não** tem `skills.registerProvider`.
- `test_plugin_deny_on_illegal_product_write_without_throw` afirma `ctx.sections[0].name === "covenant-flow:moore"`.
- `test_pin_copies_dsh_without_injecting_clients_dsh` crava `v1.1.0`.
- D13/D16/D20 intactos no código. D20 não chama `apply()`.

Esperado: Apply actualiza A1/A10 + mock + pin-test. Contrato agora nomeia esses patches.

### Dual-write / Auto / UI

`test_agents_md_is_stub` já recusa `| T0`, `T0–T17`, `Auto dsh`. Design: compilar o **ficheiro**; MUST NOT interpolar T0–T17 no JS. Sem HTML desta change. `UI impact: none` correcto.

---

## Critique (contrato vs live)

### Issue ↔ proposal ↔ design ↔ tasks ↔ specs

Issue #784 (Q1–Q6 = A) mapeia o furo 306d48f7. Pacote OpenSpec sintetiza sem reabrir Qs:

| Entra | Onde |
| --- | --- |
| Stub `AGENTS.md` cwd-independente (compilar ficheiro) | D1/D5/D7; spec `process-harness` + `process-fsm-paging`; A1–A3; tasks 1.1 / 2.2 |
| Catálogo `covenant-flow` cwd≠repo via provider JS | D4 (shape live); spec catalog + thenables; A4/A5/A10; tasks 1.2 / 2.3 / 4.3 / 4.6 |
| Sem skill paths no yaml; host `skill-filesystem` disabled intacto | D4; A6; task 2.4 |
| Sem dual-write T0–T17; sem Auto dsh | Non-Goals; spec covenant-flow; tasks 5.2 / 6.1 / 7.2 |
| Boot fail-closed DEV inválido | D6; spec developer-tooling; A7–A9; tasks 3.1–3.2 |
| Pin `v1.1.1` produto-primeiro | D8; spec covenant-flow; tasks 5.x / 6.x |
| Homologação dump first-request; tool `skill` extra | Q2; task 8.1 (não bloqueia apply; bloqueia Auto) |
| Um plugin; native loader fica; `minimal` fora | Q1/Q3/Q5 |

`## Open Questions` = nenhuma bloqueante. `UI impact: none` + Prototype N/A justificados. Sem HTML. Sem rewrite `DESIGN.md`.

### P1 r1 (SkillProvider / waitWithAbort) — **fechado no contrato**

O patch do autor pinou o que o registry live consome, não só a factory isolada:

- D4: `list`/`get` Promise; `waitWithAbort`+`signal` → `.then`; array síncrono = sintoma 306d48f7; cada candidate `provider: "covenant-flow-process"`; `validateCandidate` fora do `try`; skip de frontmatter inválido no `list`; `get(candidate, options)` não `get(name)`; `invocation` ambos booleanos; `source`/`rank`/`locator`/`path`; factory síncrona; MUST NOT `yaml` / FileSystemSkillProvider.
- A4: fake `waitWithAbort`+`validateCandidate` (cópia live, sem importar `dsh-skill`); `list({ cwd: homedir, signal })`; `process.cwd()` ≠ `REPO_ROOT`; thenable (tem `.then`); cada `provider ===`; kebab / description / source / rank / `modelInvocable`; locator sob `REPO_ROOT/.dsh/skills`.
- A5: `waitWithAbort(provider.get(candidate, { signal }), signal)` — **não** `get("covenant-flow")`; `content` string MUST Read; `validateDefinition`.
- A10: o objeto que `apply()` registou sobrevive ao mesmo fake path e lista `covenant-flow`.
- Spec `process-harness` cenário **Provider thenables survive signal and validateCandidate**; spec `developer-tooling` golden com `signal` + campo `provider`.
- Tasks 1.2 / 2.3 / 4.1 / 4.3 / 4.6. Apply contract: A4/A5/A10 passam por fake `waitWithAbort` **com `signal`**, não só `list()` directo; deny-test deixa `sections[0]===moore`; mock `registerProvider`.

P1 r1 **não** reabre. Apply que devolver array síncrono ou candidate sem `provider` falha o ouro escrito.

### O que o card fecha bem

- Compilar `AGENTS.md` (não copiar T0–T17 para `.dsh/` / JS / yaml).
- `REPO_ROOT` do lib (`join(lib, "../..")`), não `process.cwd()` / `session.header.cwd`.
- Recusar `FileSystemSkillProvider` / `customSkillDirs` no yaml / desligar native / segundo plugin — motivo ESM correcto (consumidor sem o pacote).
- `clients.dsh.auto: false`; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; tag patch não major.
- Boot: distinguir vazio vs path mentiroso.
- Fail-open só no texto da secção agents; Guard fail-closed; `registerProvider` **depois** do deny + try/catch.
- Goldens A1 (secções por `name`/`order` + inject `skills`), A2/A3, A6, A7–A9, A10 (provider registado + mock D13).
- Arquitectura live: plugin host → camada global; preset `standard` mergeia repository plugins no catálogo do agente.

---

## Findings

### P0

(nenhum)

### P1

(nenhum aberto)

P1 r1 (thenable / `candidate.provider` / `waitWithAbort`+`signal` / `get(candidate, options)` / provider de `apply()`) — **closed** neste patch.

### P2

- **A4 afirma `invocation.modelInvocable === true` e não `userInvocable`.** Live `validateInvocation`: se `invocation` existe, **ambos** os booleanos. D4 + spec + task 1.2 já exigem os dois. Disposition: A4 SHOULD também afirmar `userInvocable === true`. Pytest incompleto não colapsa se Apply segue D4.
- **`list` fulfilled = array vs observation `{ complete: false }`.** `dsh-tool-skill` omite o bloco se `snapshot.complete === false`. A4 diz «observation inclui `covenant-flow`». `MemoryProvider` (citado em D4) devolve array (= complete true). Sem watch, `{complete:false}` não é o caminho natural. Disposition: A4 SHOULD tratar o fulfilled como array (MUST NOT `{ complete: false }`). Não é o furo r1 (array síncrono).
- Plugin omitido / `--patch` falha = waterfall allow. Homologação 8.1. **accepted-residual** (#782).
- cwd=repo duplica stub + catálogo (Q5 aceite). `$HOME` com `.git` + `.dsh/skills` próprio sombreia nomes sobrepostos (residual design).
- Preset `minimal` / `persona.complete: true` sombreia `systemPrompt.section` (fora de escopo; residual #782).
- `:3080` / dump autenticado replay 306d48f7 = task 8.1, não gate de apply.
- Overlay python no boot `except Exception: dev = ""` ainda trata overlay ilegível como chave vazia → `REPO_ROOT`. Fora do A7.
- `inject: skills` acopla o Guard ao registry host. Web/standard: `id: skill` presente. Composição sem registry = plugin não monta (mesma classe plugin-não-montado #782). Q3 `minimal` fora.

### P3

- Task 4.3 resume «lookup cwd = homedir» e não repete o pin A4 `process.cwd() ≠ REPO_ROOT`. `_node()` default `cwd=REPO`. Se o golden só passar `options.cwd` e o processo Node ficar no git, `list` que use `process.cwd()` passa. A4 tabela já exige o cwd do processo. Apply MUST seguir a tabela A4, não só o resumo 4.3.
- Fake `waitWithAbort`: `await list()` sozinho aceita array (`await` de non-thenable). A4 «tem `.then`» + «cópia live faz `x.then`» fecham se o assert do thenable for **antes** do `await`.
- A3: `readAgentsStub()` sem `root`; «ou read fail» dá escape.
- Sem golden dedicado de frontmatter inválido → skip. Árvore live dos 17 stubs é gerada por `dsh_stubs.py` (name+description). Parser regex `_description_raw` conserva aspas na description — `validateCandidate` ainda passa (string não-vazia). Needle do DoD é o `name`.
- Task 8.1 needle = `covenant-flow`; issue DoD também cita `grill-card`. Scan one-level sem filtro → `grill-card` entra. Design: dump MAY listar `grill-card`.
- Homologação issue também pede caso feliz cwd=repo. Q5 always-inject + native intacto cobrem por construção; task 8.1 foca o replay que falhou.
- `implantar` live ainda exemplifica `--pin v1.1.0`; task 5.2/6.1 sobem a `v1.1.1`. Pin-test live ainda crava `v1.1.0` — Apply MUST.
- Spec `process-harness` no main ainda diz «three client adapters»; delta #782 (não arquivado) já é quatro. Este card ADDED cwd-independente.
- `resourceBase` não é validado no list; tool `skill` tem default. Fora do DoD.
- Inventário se `inject: skills` aparece no plugin inventory (Open Questions residual). Host `--patch` não é o sandbox `cordis-host-runner`.
- D20 não chama `apply()` — A10 já o distingue.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. Browser gate: **N/A (no UI)**.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM yaml: sem task de estado/evento/`enabled_tools`. T1/T7 Alan; T5 parent. I1–I9 / T0–T17 não reabertos no JS/yaml. Dual-write da lei **proibido** no pacote (compilar ficheiro).
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Auto dsh: overlay live `false`; stub e specs MUST NOT reivindicar; pin não injeta a chave.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.

---

## Trace

1. Live plugin: só Moore 50 + Guard; inject sem `skills`; boot else silencioso; `.dsh/` sem tabela T0–T17; 17 stubs process.
2. Native registry: Promise + `candidate.provider` + signal no first-request; filesystem do consumidor não importa; preset `standard` mergeia providers globais.
3. Design D1–D8 + A1–A10 **agora** pinam Promise / `provider` no candidate / `get(candidate)` / `waitWithAbort`+`signal` / provider registado por `apply()` / secções por nome / mock `registerProvider`.
4. Specs ADDED batem com o briefing e com o SHALL do catálogo (thenable + `validateCandidate`).
5. tasks 1.2 / 2.3 / 4.1 / 4.3 / 4.6 = o ouro que o Apply tem de falhar se o scanner for síncrono ou sem `provider`.

---

## Disposition

Zero P0/P1 abertos. P1 r1 fechado: D4 + A4/A5/A10 + spec thenable + tasks 1.2/4.3/4.6 pinam o contrato live `SkillProvider` que o first-request consome. Residuais P2 (userInvocable no A4, observation `complete:false`, `--patch` omit, duplicação cwd=repo, `minimal`, overlay ilegível) não colapsam o DoD se Apply seguir D4/MemoryProvider. Dual-write T0–T17, Auto, import `FileSystemSkillProvider`, e boot silencioso no DEV inválido estão fechados no contrato. Guard deny live intacto; regressão `sections[0]` e ordem `apply()` passaram a ouro A1/A10 (pytest no Apply). Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui.

### Verdict

**PASS**
