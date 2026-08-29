## Context

Card [#784](https://github.com/oalansilva/crypto/issues/784). Pele dsh já pinada no Cripto em `v1.1.0` (#782). Q1–Q6 da grelha estão fechadas no issue (todas A); este Design não as reabre. Relacionado e **não** reaberto: #608, #720, #773, #782.

Plugin live `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt"]` apenas. `apply` regista `tools/pre-execute` fail-closed e **uma** secção `covenant-flow:moore` order 50 (`text` função = `page().additional_context`). Não lê `AGENTS.md`. Não chama `ctx.skills`.

`dsh_boot.sh` live: se overlay `canonical_paths.dev` é não-vazio **e** é diretório → `LAUNCH_DIR=DEV_ROOT`; senão (chave vazia **ou** path que não é diretório) → `LAUNCH_DIR=REPO_ROOT` em silêncio. Depois `cd "$LAUNCH_DIR"` e `dsh web --patch`. Boot **não** define o workspace GUI da sessão.

Native dsh (`/tmp/deepseek-harness`, evidência deste turno):

- `dsh-agent-instructions` carrega `AGENTS.md` a partir de `agent.session.header.cwd` → `findProjectRoot(cwd)`. cwd=`/home/ubuntu` sem `.git` de consumidor → stub do Cripto não entra.
- Host `web-app` **desliga** a row `id: skill-filesystem` (`disabled: true`). Preset `standard` remonta `@deepseek-ai/dsh-skill-filesystem` na camada do preset. `list()` usa `findProjectRoot(cwd)` para `<projectRoot>/.dsh/skills` (rank 100) e `.agents/skills` (rank 200). Sem `.git` no ancestral do cwd, o project root **é o próprio cwd**.
- Catálogo modelo: `dsh-tool-skill` emite `<available_skills>` a partir do registry `ctx.skills` (user-role, first-request). Sem candidates model-invocable → bloco ausente.
- `ctx.skills.registerProvider(create)` é síncrono; `create(control)` devolve um `SkillProvider` `{ name, list, get }`. `runtime` é nome reservado. Nomes duplicados **na mesma camada** throw.
- `FileSystemSkillProvider` isolado: `{ providerName, includeDefaultRoots: false, customSkillDirs: [root] }` — teste `skill-filesystem.spec.ts` (só vê o custom root; não reclama bundled/user). `apply()` do pacote também faz `ctx.skills.registerProvider`.
- Cordis `tree.import(name)` resolve o **entry** contra `ctx.baseUrl`. Imports estáticos **dentro** de um ficheiro em `.dsh/plugin/*.js` resolvem a partir do URL desse ficheiro (árvore do consumidor), não do `node_modules` do dsh. O consumidor **não** tem `@deepseek-ai/dsh-skill-filesystem`.

Ensaio 306d48f7: cwd=/home/ubuntu, preset standard, Moore presente, Guard deny PASS, 0 `AGENTS.md`, 0 `<available_skills>`, 0 skill / 52 bash.

**UI impact: none.** Harness/hooks/docs de processo. Nenhuma rota, shell, componente ou copy de produto.

## Goals / Non-Goals

**Goals:**

- Stub `AGENTS.md` do `REPO_ROOT` no first-request dsh mesmo com session cwd ≠ git do consumidor (replay 306d48f7).
- Catálogo process skills (`covenant-flow` no `<available_skills>`) a partir de `REPO_ROOT/.dsh/skills`, mesmo cwd.
- Um plugin (Guard). `inject` inclui `skills`. Provider no JS, não no yaml.
- `dsh_boot.sh` fail-closed no `canonical_paths.dev` set e não-diretório. Chave vazia → `REPO_ROOT`.
- Pin produto `v1.1.1` → Cripto. Goldens: secção + provider + boot. Guard continua fail-closed. Stub section fail-open se o ficheiro faltar (texto vazio), como Moore.

**Non-Goals:**

- Reabrir #608/#720/#773/#782. Dual-write T0–T17 em `.dsh/` / `cordis.yml`. Vendorar `deepseek-harness`.
- Preset `minimal`. Auto dsh (ou herdar Auto Cursor). Tool `skill` como DoD. Desligar native loader / row host `skill-filesystem`.
- Paths de skill no yaml. Definir workspace GUI no boot. Produto `backend/` / `frontend/src/`. UI / HTML. Pin major.

## Decisions

1. **Q1 — mesmo plugin Guard injeta stub + catálogo; boot ainda prefere DEV canónico.**  
   `REPO_ROOT` já é `join(lib, "../..")` na `dsh_plugin_lib.js` (ficheiro do plugin, não `process.cwd()`). A secção lê `join(REPO_ROOT, "AGENTS.md")`. O provider lista `join(REPO_ROOT, ".dsh/skills")`. Boot continua: DEV existe como diretório → lança de lá; a garantia always-on **não** é o cwd do `dsh web`. DoD de homologação = replay 306d48f7, não “abrir o GUI no source”. Alternativa rejeitada: segundo plugin só para inject (Q1=A: um plugin). Alternativa rejeitada: dual-write T0–T17 no patch (lei continua só no yaml + stub ficheiro).

2. **Q2 — ensaio = dump first-request; Auto dsh fica false.**  
   PASS humano: texto do stub (frases always-on já no ficheiro) **e** `<available_skills>` contendo `covenant-flow`. Chamada `skill` é extra. `clients.dsh.auto` permanece `false`. Alternativa rejeitada: exigir tool call no DoD.

3. **Q3 — preset `minimal` fora.**  
   Só `standard` (ensaio). Sem goldens `minimal`. Residual: `persona.complete: true` no web `minimal` pode sombrear `systemPrompt.section` (já residual #782); este card não o trata.

4. **Q4 — `ctx.skills.registerProvider` + scanner thin no lib; não `new FileSystemSkillProvider` no plugin do consumidor.**  
   API live escolhida: `ctx.skills.registerProvider((control) => provider)` (`packages/skill/skill/src/index.ts`; README: registration síncrona; `skill.spec.ts` `MemoryProvider` é `async list` / `async get(candidate)` e carimba `provider: 'memory'`). O provider **emula** o padrão isolado `includeDefaultRoots: false` + `customSkillDirs: [REPO_ROOT/.dsh/skills]` (teste filesystem linhas 835–848) **sem** construir a classe do pacote e **sem** `import '@deepseek-ai/dsh-skill-filesystem'` / `yaml` (consumidor sem os dois pacotes; import extra = plugin não carrega = Guard some). `ctx.loader.internal.import` no `apply` acoplaria a internals do loader. Vendorar o harness é non-goal. Frontmatter: o mesmo recorte regex/`---` que `dsh_stubs.py` (só `node:` builtins).  
   **Shape live que o first-request consome** (`listLayerCandidates` / `validateCandidate` / `waitWithAbort` / `SkillRegistry.get` em `dsh-skill` `src/index.ts`):  
   - `name: "covenant-flow-process"` (não `filesystem`, não `runtime`).  
   - `list(options)` e `get(candidate, options)` MUST devolver **Promise** (função `async` ou thenable). `waitWithAbort(x, signal)` com `signal` definido faz `x.then(...)`. Array síncrono → TypeError → provider skipped no `try` de `list()` → `snapshot.complete=false` → `dsh-tool-skill` **não** emite `<available_skills>` (o furo 306d48f7). First-request **sempre** passa `signal`.  
   - `list` ignora `options.cwd` (e não usa `process.cwd()` para o root): um nível `REPO_ROOT/.dsh/skills/<name>/SKILL.md`. Diretório ausente → Promise de `[]` (não throw). Frontmatter inválido / `name` não kebab / `description` vazia → **skip** essa entrada no `list` (não throw), para `validateCandidate` nunca ver lixo. Não filtrar a um único skill: `grill-card` e o resto dos stubs entram; o needle do DoD é `covenant-flow`.  
   - Cada `SkillCandidate` MUST ter: `name` kebab, `description` string não-vazia, `invocation: { modelInvocable: true, userInvocable: true }`, `source: "custom"`, `rank: 300` (número finito), `provider: "covenant-flow-process"` **igual a `provider.name`**, `locator` opaco (ex. `{ path, directory }`), `path` string do `SKILL.md`. `validateCandidate` corre **fora** do `try` de `list()`: candidate sem `provider === name` rebenta o collect da camada, não só skip.  
   - `get(candidate, options)` — **não** `get(name)`. Relê `candidate.locator` / `candidate.path`. Devolve Promise de `SkillDefinition` com os mesmos `name`/`description`/`invocation`/`source`/`provider` **e** `content` string (body do ficheiro). `validateDefinition` exige `content` string.  
   Sem watch (stubs git; o registry re-lista).  
   `inject = ["systemPrompt", "skills"]`. Sem `customSkillDirs` no `cordis.patch.yml`. **Não** editar `id: skill-filesystem` `disabled: true` no host.  
   **Ordem em `apply(ctx)`:** `tools/pre-execute` + as duas `systemPrompt.section` **antes** de `registerProvider`. `registerProvider` só se `typeof ctx.skills?.registerProvider === "function"`; wrap em try/catch — throw do provider MUST NOT impedir o deny. Alternativa rejeitada: yaml `customSkillDirs`. Alternativa rejeitada: `ctx.skills.register()` runtime por skill.

5. **Q5 — sempre injectar a secção; native loader fica.**  
   `covenant-flow:agents` dispara sempre (cwd=repo ou não). Native `agent-instructions` + preset `skill-filesystem` intactos. Duplicação cwd=repo aceite (secção sistema + user-role baseline; catálogo global + project-dsh rank 100). Não desligar native. Fail-open: ficheiro em falta / unreadable → `text` retorna `""` (Moore já devolve `""` se `page()` falha). Guard **não** herda fail-open.

6. **Q6 — boot: path DEV set e não-dir → exit ≠0; vazio → REPO_ROOT.**  
   Hoje o ramo `else` engole um `canonical_paths.dev` apontando para path inexistente. Apply MUST: `if [[ -n "$DEV_ROOT" && ! -d "$DEV_ROOT" ]]; then echo "dsh_boot: canonical_paths.dev is not a directory: $DEV_ROOT" >&2; exit 1; fi`. `[[ -z "$DEV_ROOT" ]]` → `LAUNCH_DIR="$REPO_ROOT"`. Boot **não** envia workspace/cwd de sessão ao GUI. Plugin permanece a garantia.

7. **Nome e ordem das secções vs Moore.**  
   Persona first-party = order 0; tools bash = 1000; Moore live = `covenant-flow:moore` order **50**. Stub always-on: `covenant-flow:agents` order **40** (antes da página Moore; depois da persona). `text` função por assemble, igual Moore. Não `complete: true`. Não `agent/session-start` como único caminho. Não hop gitignore. Compila o **ficheiro** (≤40 linhas não-vazias no produto); MUST NOT interpolar tabela T0–T17 no JS.  
   **Goldens #782:** `_mock_ctx_prelude` MUST ganhar `skills.registerProvider(create)` que chama `create(control)` (senão D13 e `test_plugin_deny_on_illegal_product_write_without_throw` rebentam ao `apply()`). Esse deny-test live afirma `ctx.sections[0].name === "covenant-flow:moore"`. Apply MUST **actualizar esse golden** (e A1) para localizar secções por `name`/`order` (`covenant-flow:agents` 40 **e** `covenant-flow:moore` 50), **não** `sections[0]===moore`. D20 não chama `apply()` — não precisa do mock. `test_pin_copies_dsh_without_injecting_clients_dsh` ainda crava `v1.1.0`; Apply MUST subir o pin esperado para `v1.1.1` (e preservar `clients.dsh.auto: false` no bump Cripto, task 6.1).

8. **Pin patch `v1.1.1`, mesma ordem que #782.**  
   Produto primeiro, tag **`v1.1.1`**, depois `implantar --pin v1.1.1` no Cripto. Não major. `CLIENT_KEYS` / `SCHEMA_MAJOR` / `clients.dsh.auto: false` inalterados.

### Golden cases (pytest `scripts/process-fsm`, sem GitHub)

| # | Caso | Esperado |
| --- | --- | --- |
| A1 | Plugin `apply` + `ctx.systemPrompt.section` | duas secções localizadas por `name`/`order` (MUST NOT `sections[0]`): `covenant-flow:agents` 40 (`text` função) **e** `covenant-flow:moore` 50; `inject` contém `systemPrompt` e `skills` |
| A2 | `text` de `covenant-flow:agents` com `AGENTS.md` presente em `REPO_ROOT` | contém texto do stub (p.ex. `NLU ≠ δ` / `Todo` não é código); **não** contém `T0` / `release-guard pre`; ≤40 linhas não-vazias no ficheiro |
| A3 | `AGENTS.md` em falta (lib apontando a root de fixture sem o ficheiro, ou read fail) | `text()` === `""` (fail-open); Guard `pre-execute` deny **não** muda |
| A4 | Fake `waitWithAbort` + `validateCandidate` (cópia das regras live, **sem** importar `dsh-skill`): `list({ cwd: homedir, signal })` com `process.cwd()` ≠ `REPO_ROOT` e `AbortController` não abortado | thenable (tem `.then`); não throw; observation inclui `covenant-flow`; **cada** candidate `provider === "covenant-flow-process"`; `name` kebab; `description` não-vazia; `source` string; `rank` finito; `invocation.modelInvocable === true`; `locator`/`path` sob `REPO_ROOT/.dsh/skills`; não lista skills de `$HOME`; `validateCandidate(c, "covenant-flow-process")` não throw |
| A5 | Fake registry `get`: `waitWithAbort(provider.get(candidate, { signal }), signal)` no candidate A4, **não** `get("covenant-flow")` | thenable; `validateDefinition`: `content` string com MUST Read `.cursor/skills/covenant-flow/SKILL.md`; `provider === "covenant-flow-process"`; `name` igual ao candidate; corpo stub ≤8 linhas |
| A6 | `cordis.patch.yml` | sem path `.dsh/skills`; sem `customSkillDirs`; ids de insert inalterados; host row `skill-filesystem` não aparece |
| A7 | `canonical_paths.dev` = path existente que **não** é diretório (ficheiro) **ou** path inexistente | `dsh_boot.sh` exit ≠0; stderr contém o path |
| A8 | overlay sem `canonical_paths.dev` / chave vazia; `dsh` fake no PATH que imprime cwd e sai 0 | boot exit 0; launch cwd = `REPO_ROOT` (não um path inventado) |
| A9 | `canonical_paths.dev` é diretório | `LAUNCH_DIR` = esse diretório (comportamento #782 preservado) |
| A10 | `apply(ctx)` com `_mock_ctx_prelude` que inclui `skills.registerProvider` | factory síncrona; `provider.name === "covenant-flow-process"`; o **mesmo** objeto registado sobrevive a fake `waitWithAbort(list, signal)` + `validateCandidate` e lista `covenant-flow` (não só a factory isolada); D13/D20 passam; deny-test #782 localiza moore **por nome** (não `sections[0]`) |

## Apply contract

- Ordem: (1) commit no produto `oalansilva/covenant-flow` tag **`v1.1.1`**; (2) `implantar --pin v1.1.1` no Cripto. Zero produto UI.
- Produto: `dsh_plugin_lib.js` (`readAgentsStub()`, `createRepoDshSkillProvider(root)` com `async list`/`get`, candidates `provider: "covenant-flow-process"`, só `node:` builtins), `.dsh/plugin/process-fsm-guard.js` (`inject` + secções + `registerProvider` **depois** do deny listener), `dsh_boot.sh` (exit no DEV inválido), goldens A1–A10. **Não** alterar `.dsh/cordis.patch.yml` para skills. **Não** vendorar harness. **Não** `import 'yaml'` / FileSystemSkillProvider. **Não** desligar native loader.
- Cripto no pin: `.dsh/` + `scripts/process-fsm/` atualizados; overlay `pin: v1.1.1`; `clients.dsh.auto: false` permanece; `AGENTS.md` gerado inalterado em substância (≤40).
- Plugin: `inject = ["systemPrompt", "skills"]`. Secções 40 + 50. `registerProvider` só se `ctx.skills.registerProvider` existe; try/catch. Deny path #782 intacto.
- Pytest: A1–A10; A4/A5/A10 passam por fake `waitWithAbort`+`validateCandidate` **com `signal`**, não só `list()` directo; `_mock_ctx_prelude` tem `skills.registerProvider`; deny-test #782 deixa de usar `sections[0]===moore`; pin-test `v1.1.1`. D13/D16/D20 não regridem. Sem GitHub nos unitários.
- Homologação (não bloqueia apply; bloqueia Auto): replay 306d48f7 — cwd≠repo, preset standard, dump first-request com stub + `<available_skills>` `covenant-flow`; Guard deny continua.

## Risks / Trade-offs

- [Provider global vs preset `filesystem`] → merge live: camada mais próxima sombreia o mesmo `name`; rank só desempata **dentro** da camada (não é o rank 100 que “vence” o 300 entre camadas). cwd=repo: preset project-dsh sombreia o thin global (mesmo ficheiro; Q5 aceite). cwd=$HOME: preset não vê o repo → thin global lista `REPO_ROOT`. Residual: `$HOME` com `.git` e `.dsh/skills` próprio sombreia nomes sobrepostos.
- [inject `skills` se o registry host faltar] → Cordis não chama `apply` até o serviço existir; web/standard montam `dsh-skill` (host `id: skill`). Residual: composição sem registry = Guard também não carrega (mesmo classe plugin-não-montado #782). `minimal` fora (Q3).
- [`registerProvider` throw se nome duplicado na camada host] → `covenant-flow-process` não é `filesystem` nem `runtime`. `apply` regista deny **antes**; try/catch no provider.
- [Thin scanner vs FileSystemSkillProvider] → sem watch/Chokidar; stubs git. Frontmatter inválido = skip no `list`. Root ausente → `[]`. A4/A5/A10 pinam Promise + `candidate.provider` + `get(candidate)` via fake `waitWithAbort` (P1). Sem `import 'yaml'`.
- [Boot exit no DEV inválido] → operador vê o path; já não cai calado em `REPO_ROOT` com overlay mentiroso. Overlay Cripto live aponta para `/srv/apps/dev/criptofarol/source` (diretório). Overlay python `except` no boot ainda trata overlay ilegível como chave vazia → `REPO_ROOT` (fora do A7).
- [Boot não seta GUI workspace] → sessão pode continuar cwd=$HOME; plugin é a garantia. Residual: operador tem de `--patch` (#782). Worktree com overlay DEV a apontar para o source canónico → `LAUNCH_DIR=source` e plugin absoluto do worktree (já #782).
- [Ensaio Auto dsh] → este card não herda Auto. DoD humano ≠ tool `skill`. Task 8.1 needle = `covenant-flow`; dump MAY também listar `grill-card` (scan one-level, sem filtro). Ensaio feliz cwd=repo não é o DoD humano (Q5 always-inject).
- [Goldens `apply()`] → `_mock_ctx_prelude` MUST ter `skills.registerProvider`; deny-test MUST abandonar `sections[0]===moore` e localizar por `name`/`order` (D7). Sem isso pytest falha visível no Apply — não é buraco live se A1/A10 forem seguidos.
- [cwd=repo duplica AGENTS.md e o catálogo] → aceite (Q5). Tokens, não lei. Guard/Moore continuam em `process.cwd()` do `apply`; AGENTS/skills em `REPO_ROOT` do ficheiro (intencional).

## Migration Plan

Aditivo sobre `v1.1.0`. Ordem Apply: (1) lib `readAgentsStub` + provider **Promise** + shape `validateCandidate` + goldens A2–A5; (2) plugin inject/secções **depois** deny listener + `registerProvider` + A1/A10 e regressão D13/D20 + mock `skills` + deny-test por nome; (3) `dsh_boot.sh` A7–A9; (4) A6 yaml intacto; (5) tag `v1.1.1`; (6) pin Cripto. Rollback = pin `v1.1.0`. Sem migration de banco. Sem rebuild frontend. Homologação = dump 306d48f7, não `./restart`.

## Open Questions

Nenhuma bloqueante (Q1–Q6 = A). P1 do shape `SkillProvider`/`waitWithAbort` fechado neste patch (D4 + A4/A5/A10). Residual para ensaio: dump autenticado `:3080` no replay cwd≠repo; inventário se `inject: skills` aparecer no plugin inventory.

## UI impact

**none** — harness/hooks/docs de processo. Nenhuma rota, shell, componente ou copy de produto. Nenhuma superfície visual nova ou alterada. O aceite visível é texto de sistema/catálogo na sessão dsh, não uma tela Cripto.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; o aceite é inject do stub + `<available_skills>` na sessão dsh e boot exit no path DEV inválido. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Detector Impeccable da pele dsh permanece o de #782; este card não o altera.

## Design Critique

- **P0:** nenhum.
- **P1 r1 (closed):** provider thin vs registry live (`waitWithAbort` + `validateCandidate`): `list`/`get` thenable, `candidate.provider === "covenant-flow-process"`, `get(candidate, options)`, goldens A4/A5/A10 pelo fake registry com `signal`. Disposition: **closed** no patch do autor (D4 + tasks 1.2).
- **P2 (accepted-residual):** `inject: skills` acopla Guard ao registry host; cwd=repo duplica stub/catálogo (Q5); `$HOME` com `.git` próprio pode sombrear; plugin omitido = allow (#782); task 8.1 mais estreita que o needle `grill-card` do issue (scan one-level cobre se Apply não filtrar).
- **P3 (accepted-residual):** dump autenticado `:3080`; preset `minimal` / `persona.complete`; pin-test live ainda `v1.1.0` até Apply; A3 fixture vs `REPO_ROOT`.
- Prototype: N/A — harness, sem superfície visual.
- Snapshot: `.impeccable/critique/784-card-784-dsh-608-always-on-A.md` e `…-B.md` (r2 PASS). Apply e Code Review não lêem essa pasta.
- **Design Agent verdict: PASS**
