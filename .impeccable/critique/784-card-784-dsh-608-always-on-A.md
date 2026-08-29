# Snapshot — Assessment A · ROUND 2 · card #784 `card-784-dsh-608-always-on`

- Card: #784 — Harness: dsh deve entregar always-on do #608 (AGENTS.md + skills), não só Guard
- Change: `card-784-dsh-608-always-on`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested critic)
- Modelo: inherit
- UTC: 2026-08-29T01:46:34Z
- Round: **2** (round 1 BLOCKED P1 thin SkillProvider; autor reivindica fecho em D4 + A4/A5/A10 + specs/tasks)
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Prompt do pai: worktree `card-784-dsh-608-always-on`; Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `a9c0c702048645d430d2e58ad5ef7ca736d4bed4a7f28a2d884eae81002cef0f` · **2399** palavras (`wc -w`) · 18761 bytes
- Round 1 digest (obsoleto): `657b0426c355af465fbd4f08dc2cd154357e8b1ea0ff56b09cbac0574ed2dc83` (1873 palavras)
- UI impact: **none** (harness/hooks/docs/specs de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*784*`; aceite visível = inject do stub + `<available_skills>` na sessão dsh + boot exit no DEV inválido. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright.
- `openspec validate card-784-dsh-608-always-on --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois de A/B)
- Method: issue #784 body (Q1–Q6 = A); `proposal.md` / `design.md` D1–D8 + A1–A10 (texto actual, não o digest r1); `tasks.md` 1–8; deltas `process-harness` `process-fsm-paging` `developer-tooling` `covenant-flow`; live worktree plugin/lib/boot/goldens #782; source `/tmp/deepseek-harness` (`waitWithAbort` / `validateCandidate` / `validateDefinition` / `listLayerCandidates` / `dsh-tool-skill` catalog; host `id: skill` vs `skill-filesystem` `disabled: true`).

---

## Brief (só neste snapshot)

Fechar ingestão cwd-independente no adapter dsh já pinado em `v1.1.0` (#782). Mesmo plugin Guard: secção `covenant-flow:agents` order 40 compila `REPO_ROOT/AGENTS.md`; `ctx.skills.registerProvider` publica `.dsh/skills` mesmo com session cwd=`$HOME`. Pin produto `v1.1.1`. Não reabrir #608/#720/#773/#782. Sem dual-write T0–T17. Sem Auto dsh. Sem FileSystemSkillProvider no JS do consumidor. `UI impact: none`.

Round 2: re-verificar o P1 r1 (thenable `list`/`get`, `candidate.provider`, `get(candidate, options)`, goldens via `waitWithAbort`+`validateCandidate`) contra o contrato patchado. Não relitigar «Apply ainda não implementou» como P0/P1.

---

## 1. P1 da ronda 1 — mapeamento do fecho

O P1 r1 era um único furo com cinco arestas. Live (`packages/skill/skill/src/index.ts`):

- `waitWithAbort(x, signal)` com `signal` definido faz `x.then(...)`. Array síncrono → TypeError → `catch` em `listLayerCandidates` → provider skipped + `cacheable=false` → `snapshot.complete=false` → `dsh-tool-skill` **não** emite `<available_skills>`.
- `validateCandidate` corre **depois** do `try` de `list()`: candidate sem `provider === provider.name` rebenta o collect da camada, não só skip.
- Registry `get(name)` chama `provider.get(candidate, options)` e `validateDefinition` (`content` string).
- First-request **sempre** passa `signal` (`tool-skill` `snapshot({ cwd, signal, scope: agent })`).

| Aresta r1 | Onde no pacote actual | Fechado? |
| --- | --- | --- |
| `list`/`get` MUST Promise; MUST NOT array síncrono | D4 shape; task 1.2; spec harness SHALL; cenário «Provider thenables… MUST NOT return a bare array» | **sim** |
| First-request `signal` + `waitWithAbort` → `.then` | D4 (cita `listLayerCandidates` / `waitWithAbort`); A4/A5/A10 fake com `AbortController` não abortado | **sim** |
| Cada candidate `provider === "covenant-flow-process"` (= `provider.name`) | D4; task 1.2; spec harness + tooling; A4/A10 | **sim** |
| `validateCandidate` fora do `try` (lixo rebenta a camada) | D4; skip de frontmatter inválido / kebab / description vazia no `list` (não throw) | **sim** |
| `get(candidate, options)` não `get(name)`; `content` string | D4; task 1.2; A5 `waitWithAbort(provider.get(candidate, { signal }), signal)` | **sim** |
| Goldens não chamar só `list()` directo | A4/A5/A10 + task 4.3/4.6 + spec tooling «fake `waitWithAbort`/`validateCandidate` path»; Apply contract | **sim** |
| `invocation` ambos booleanos; `source` string; `rank` finito; kebab; locator/path | D4 MUST `{ modelInvocable: true, userInvocable: true }`, `source: "custom"`, `rank: 300`, locator opaco; spec SHALL; A4 campos + `validateCandidate` não throw | **sim** |
| Lib só `node:` ; MUST NOT `yaml` / FileSystemSkillProvider | D4; task 1.2; Apply contract | **sim** |
| Provider registado por `apply()` (não só factory isolada) | A10; task 2.3/4.6 | **sim** |

Não reabro o P1: o contrato de produção está pinado em design + spec + tasks, independentemente de o Apply ainda não ter escrito o JS (plugin live continua `inject = ["systemPrompt"]` — esperado, Status=Design).

---

## 2. Escopo vs grill #784 (Q1–Q6 = A)

Body live: fronteira vazia; Q1–Q6 = A. Design não reentrevista.

| Entra do issue | Onde no pacote (pós-patch) |
| --- | --- |
| Mesmo plugin Guard; `REPO_ROOT` ancora stub + catálogo (Q1=A) | D1; spec harness + paging; tasks 2.1–2.3 |
| `inject` inclui `skills`; provider JS; sem paths no yaml; sem tocar host `skill-filesystem` (Q4=A) | D4; A6; spec tooling; task 2.4 |
| Secção **sempre** injeta; native fica; duplicação cwd=repo aceite (Q5=A) | D5; spec paging; Non-Goals |
| Boot: DEV set e não-dir → exit ≠0; vazio → `REPO_ROOT`; boot ≠ workspace GUI (Q6=A) | D6; A7–A9; task 3.x |
| DoD dump first-request stub + `<available_skills>` `covenant-flow`; tool `skill` extra; Auto false (Q2=A) | D2; task 8.1; D4 scan one-level (não filtrar a um único skill; `grill-card` entra; needle do DoD = `covenant-flow`) |
| Preset `minimal` fora (Q3=A) | D3; Non-Goals |
| Pin produto `v1.1.1` depois Cripto; não major | D8; tasks 5–6; spec `covenant-flow` |
| Write ilegal + `q_git=develop` continua deny; Moore não regride | D1/A1/A10; deny-test por `name`/`order` (não `sections[0]`) |
| Stubs ≤8; fail-open stub / fail-closed Guard | D4/D5; A3; A5 |
| Sem `.agents/skills` no catálogo quando cwd=$HOME | Non-Goals + D4 só `.dsh/skills` |
| Sem insert extra filesystem (Q4≠B) | A6; task 2.4 |
| Sem inject condicional (Q5≠B); sem fallback silencioso boot (Q6≠B) | D5; D6/A7 |

**Não entra — não reaberto:** vendorar DeepSeek; dual-write T0–T17; Auto dsh; preset minimal; produto `backend/`/`frontend/src/`; Clara/Hermes; pin major; «abra o canonical DEV na GUI» como fecho do 306d48f7; segundo plugin.

Vocabulário do issue intacto. Proposal «New Capabilities: (nenhuma)» correcto.

---

## 3. Fidelidade live (re-probe; não é Apply)

### Plugin / lib / boot (worktree, pré-Apply — esperado)

- `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt"]`; Moore 50; `tools/pre-execute` fail-closed; sem `ctx.skills`. Delta do contrato = acrescentar `"skills"`, secção 40, `registerProvider` **depois** do deny.
- `dsh_plugin_lib.js`: `REPO_ROOT = join(lib, "../..")` via `import.meta.url` (não `process.cwd()`). Só `node:` + `spawnSync`. Sem `readAgentsStub` / provider ainda.
- `dsh_boot.sh`: `else` ainda engole DEV set e não-dir. A7 é o delta.
- `_mock_ctx_prelude` ainda sem `skills.registerProvider`; deny-test ainda `sections[0]===moore`; pin-test ainda `v1.1.0`. D7/A1/A10/task 4.1/4.6 obrigam o Apply a actualizar — pytest falha visível se o Apply ignorar.

### Registry / first-request (harness)

- Host web-app: `id: skill` (`@deepseek-ai/dsh-skill`) **fica** no host; `skill-filesystem` e `tool-skill` `disabled: true`; preset `standard` remonta filesystem + tool-skill na camada do agente. Comentário live: deployment-level providers (plugin `--patch`) registam na camada **global**; o agente lê global ∪ chain. Rank só desempata **dentro** da camada. D risco 1 agora descreve isto (r1 P3 «design diz rank 100» está corrigido).
- `inject: ["systemPrompt", "skills"]` no Guard host: `skills` é serviço host. Residual: composição sem registry → plugin não monta (mesma classe #782; Q3 `minimal` fora).
- `FileSystemSkillProvider` isolado linhas 835–848: `includeDefaultRoots: false` + `customSkillDirs` — D4 emula este recorte sem importar o pacote (consumidor sem `@deepseek-ai/dsh-skill-filesystem` / `yaml`; import extra = plugin não carrega = Guard some). Correcto.
- `dsh-tool-skill`: `if (!snapshot.complete) return decision`; se `!history.published && skills.length === 0` omite o bloco. 306d48f7 = zero model-invocable (cwd=$HOME, filesystem project root = cwd). Thin global com candidates `modelInvocable: true` é o fecho.

### Goldens A1–A10 vs live (pós-patch)

| Golden | Cobre o furo r1? | Nota |
| --- | --- | --- |
| A1 secções por `name`/`order` + inject | n/a (paging/Guard) | fecha o P2 r1 `sections[0]===moore` |
| A2 stub wording / sem T0 | n/a | |
| A3 `text()===""` | n/a | read-fail chega; fixture-root vs `REPO_ROOT` hardcoded = P3 |
| A4 fake `waitWithAbort`+`validateCandidate` + `signal` + `provider` + thenable | **sim** | raw `list({ cwd: homedir, signal })`; não `$HOME` skills |
| A5 `get(candidate, { signal })` + `validateDefinition` | **sim** | não `get("covenant-flow")` |
| A6 yaml | n/a | |
| A7–A9 boot | n/a | |
| A10 provider **registado** por `apply()` + fake list + D13/D20 + deny por nome + pin `v1.1.1` | **sim** | mock chama `create(control)` |

---

## 4. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy | **none** — fora |
| `backend/` de app | **none** |
| Protótipo HTML / Playwright / `DESIGN.md` | **N/A** — zero `prototypes/*784*` |
| Rubrica Impeccable visual | **N/A** |
| Texto de sistema dsh (agents + Moore) | harness; aceite = dump first-request; **entra** (não é UI Cripto) |
| `<available_skills>` / tool `skill` | catálogo de sessão dsh; **entra** (não é UI Cripto) |
| Detector `hook.mjs` | pele #782; este card não altera; **fora do delta** |
| UI dsh `:3080` | **vendor** — Non-Goal; dump autenticado residual |

`UI impact: none` + Prototype N/A justificados. HTML não gerado / não copiado.

---

## Achados

- P0: (nenhum)
- P1: (nenhum aberto). P1 r1 **closed** — ver tabela §1. D4 + A4/A5/A10 + spec harness cenário thenable + spec tooling golden `signal` + tasks 1.2/4.3/4.6 pinam Promise, `candidate.provider`, `get(candidate, options)`, skip de lixo no `list`, e goldens que passam por fake `waitWithAbort`+`validateCandidate` (cópia das regras live, sem importar `dsh-skill`).
- P2: Homologação task 8.1 continua mais estreita que o issue (AC grelhado pede cwd=repo **e** needle `grill-card`; 8.1 só replay 306d48f7 + `covenant-flow`). D4 agora **proíbe** filtrar o scan a um único skill (`grill-card` entra). Q5 always-inject cobre cwd=repo no texto. Não bloqueia sozinho. Disposition: **accepted-residual**.
- P2: `inject: skills` acopla o Guard ao registry host. Web/`standard` OK (`id: skill` no host). Composição sem registry = plugin não monta (mesma classe #782). Disposition: **accepted-residual**.
- P2: cwd=repo duplica AGENTS.md (secção sistema + user-role nativo) e o catálogo (global thin + preset filesystem; camada do agente sombreia o mesmo `name`). Q5 aceite. Tokens, não lei. Disposition: **accepted-residual**.
- P2: `$HOME` com `.git` e `.dsh/skills` próprio — camada do preset sombreia o global nos nomes sobrepostos. Design risco 1 agora atribui a **camada**, não ao rank 100. Disposition: **accepted-residual**.
- P2: Sem watch/Chokidar no thin. Stubs git; registry re-lista. Disposition: **accepted-residual**.
- P2: Boot não seta GUI workspace — sessão pode continuar cwd=$HOME; plugin é a garantia. Operador ainda precisa `--patch` (#782). Disposition: **accepted-residual**.
- P3: A4 lista `invocation.modelInvocable === true` e não nomeia `userInvocable` na coluna; D4/spec/task 1.2 já exigem os dois booleanos e «cópia das regras live» de `validateInvocation` (undefined `userInvocable` throw). Disposition: **accepted-residual**.
- P3: Fake `waitWithAbort` MUST usar `.then` como o live quando `signal` está definido (não `async (x) => x` / `Promise.resolve` que engolem array). A4 «thenable (tem `.then`)» + spec «MUST NOT return a bare array» + D4 citam o live; risco só se Apply enfraquecer o fake contra o texto. Não relitigar como P1. Disposition: **accepted-residual**.
- P3: A3 «lib apontando fixture» vs `readAgentsStub()` preso a `REPO_ROOT` da lib; ramo read-fail chega. Disposition: **accepted-residual**.
- P3: Parser `dsh_stubs.py` (`^description:\s*(.*)$`) conserva aspas na description; nativo `yaml` stripa. Cosmético no catálogo. Skip inválido já no risco. Disposition: **accepted-residual**.
- P3: `persona.complete: true` no web `minimal` pode sombrear `systemPrompt.section` (#782). Q3 fora. Disposition: **accepted-residual**.
- P3: Dump autenticado `:3080` / inventário `inject: skills` no plugin inventory. Disposition: **accepted-residual**.
- P3: Overlay python `except` no boot trata overlay ilegível como chave vazia → `REPO_ROOT` (fora do A7). Disposition: **accepted-residual**.
- P3: Guard/Moore continuam em `process.cwd()` capturado no `apply`; AGENTS/skills em `REPO_ROOT` do ficheiro. Intencional. Disposition: **accepted-residual**.
- P3: `resourceBase` não é validado no `list`; tool `skill` tem default. Fora do DoD. Disposition: **accepted-residual**.
- P3: Task 2.2 wording `text função = readAgentsStub()` pode ler-se como string no `apply`; D7/A1 exigem função por assemble (igual Moore). Disposition: **accepted-residual**.
- Dual-write T0–T17 / segundo plugin / yaml skill paths / desligar native / tocar host `skill-filesystem` / FileSystemSkillProvider importado do consumidor / Auto dsh / preset minimal / produto UI / superfície visual sem classificar / Design Critique pré-PASS / `complete: true` na secção agents: **false**.

---

## Disposition

P1 r1 **closed** neste patch. Zero P0/P1 abertos. Recorte Q1–Q6 = A mapeado. Regressão Guard/Moore pintada (A1/A10; deny-test por nome; mock `registerProvider`; ordem deny **antes** do provider). Boot vs GUI cwd correcto. UI none classificada. Sem HTML. Residuais P2/P3 não impedem PASS: homologação 8.1 mais estreita que o issue, acoplamento `inject: skills`, duplicação cwd=repo, sombra `$HOME`+git, fake vs live se o Apply enfraquecer a cópia.

Não há re-despacho de autor por P0/P1.

---

## Verdict

**PASS** (zero P0/P1 abertos; Prototype N/A justificado; UI impact none classificado; crítica isolada round 2; snapshot não vazio)

## Snapshot

`.impeccable/critique/784-card-784-dsh-608-always-on-A.md`
