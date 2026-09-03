## Why

O adapter dsh de [#782](https://github.com/oalansilva/crypto/issues/782) já compila Guard + Moore a partir do núcleo #608, mas a sessão de homologação `session-306d48f7-d893-471e-ba4c-8fe7a5153fda` (cwd=`/home/ubuntu`, preset `standard`) mostrou Moore presente, Guard deny PASS, **zero** injeção de `AGENTS.md`, **zero** `<available_skills>` e 0 skill / 52 bash. O native loader de `AGENTS.md` e o `skill-filesystem` do preset resolvem o projeto a partir do cwd da sessão; quando cwd ≠ git do consumidor, o stub always-on e o catálogo de process skills não entram. Card [#784](https://github.com/oalansilva/crypto/issues/784).

## What Changes

- O **mesmo** plugin Guard (`.dsh/plugin/process-fsm-guard.js`) injeta o stub `AGENTS.md` do `REPO_ROOT` via `systemPrompt.section` (compila o ficheiro; sem dual-write T0–T17) **e** publica o catálogo de process skills a partir de `REPO_ROOT/.dsh/skills` mesmo quando o cwd da sessão é `$HOME`.
- `inject` do plugin passa a incluir `skills` além de `systemPrompt`. O provider vive no plugin (`ctx.skills.registerProvider`); **sem** paths de skill no yaml; **sem** tocar a row host `skill-filesystem` `disabled`.
- Native loader de `AGENTS.md` / `skill-filesystem` do preset **permanece**. Duplicação quando cwd=repo é aceite.
- `dsh_boot.sh`: `canonical_paths.dev` preenchido e **não** é diretório → exit ≠0 nomeando o path; chave vazia → `LAUNCH_DIR=REPO_ROOT`. Boot **não** define o workspace GUI; o plugin é a garantia.
- Ensaio humano = dump do first-request contém texto do stub + `<available_skills>` com `covenant-flow`. Chamada da tool `skill` é extra, não DoD. Auto dsh continua `false`. Preset `minimal` fora de escopo.
- Fonte no produto `oalansilva/covenant-flow` tag **`v1.1.1`**; Cripto pin depois. Mesma ordem que #782. Sem vendorar `deepseek-harness`. Sem reabrir #608/#720/#773/#782. Sem copiar T0–T17 para `.dsh/` ou `cordis.yml`. Stubs ≤8 linhas. Sem produto UI. Sem Auto dsh.

## Capabilities

### New Capabilities

- (nenhuma) — always-on dsh é o quarto adapter já descrito em `process-harness` (#782); este card fecha a ingestão cwd-independente, não um quinto cliente nem uma spec de produto.

### Modified Capabilities

- `process-harness`: stub `AGENTS.md` ingested pelo dsh mesmo com session cwd ≠ git do consumidor; catálogo de process skills vem do provider do plugin; cenário quatro-clientes inclui cwd≠repo (replay 306d48f7); Auto dsh permanece gated.
- `process-fsm-paging`: além de `covenant-flow:moore` order 50, o mesmo plugin injeta secção `covenant-flow:agents` (order 40) com o texto do ficheiro `AGENTS.md`; fail-open (texto vazio se o ficheiro faltar), como Moore.
- `developer-tooling`: `dsh_boot.sh` falha se `canonical_paths.dev` está set e não é diretório; catálogo de skills do processo não depende do cwd da sessão; goldens de secção + provider + boot.
- `covenant-flow`: pin **`v1.1.1`** copia o plugin atualizado; `install.sh --pin` continua a copiar `.dsh/` sempre; `SCHEMA_MAJOR` / `CLIENT_KEYS` inalterados.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` (tag `v1.1.1`) — `.dsh/plugin/process-fsm-guard.js` (`inject`, secção agents, `registerProvider`), `scripts/process-fsm/dsh_plugin_lib.js` (ler stub; provider sobre `.dsh/skills`), `dsh_boot.sh` (exit no path DEV inválido), goldens pytest `scripts/process-fsm`. Depois `implantar --pin v1.1.1` no Cripto.
- Não toca `backend/` / `frontend/src/` de produto, yaml T0–T17, `cordis.patch.yml` skill paths, row host `skill-filesystem`, preset `minimal`, Auto dsh, monorepo DeepSeek, Clara/Hermes.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A.
- Origem: issue #784. Homologação: replay 306d48f7 (cwd≠repo, preset standard); não bloqueia o merge do adapter; bloqueia Auto.
