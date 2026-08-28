## Why

A lei do processo (EFSM + três harnesses) vive só no Cripto. Outra máquina, Clara, Hermes ou greenfield não instala o mesmo processo; copiar skills/hooks à mão diverge (#584/#668). Sem um produto versionado, o harness do #608/#720 não viaja. O card [#773](https://github.com/oalansilva/crypto/issues/773) fecha isso: um repo/produto `oalansilva/covenant-flow` (Covenant Flow), overlay por projeto, peles commitadas no git do consumidor, pin semver.

## What Changes

- **Novo repo GitHub privado** `oalansilva/covenant-flow` (Covenant Flow). Nucleus: `process-fsm.yaml` + `scripts/process-fsm/` + skills canónicas. Uma lei, três peles. Sem dual-write da tabela δ. Sem lock machine. Sem Bugbot do Cursor. Sem ficheiro `BUGBOT.md`. Nenhum nome de produto ou skill contém `alan`.
- **Canal v1:** skill `implantar` + `install.sh --pin` que **copia** nucleus (yaml + `scripts/process-fsm/`) + três adapters + `.agents/skills/` (impeccable/design-critic/playwright-cli) + helpers + template `AGENTS.md`; o consumidor **commita** isso no próprio git. Overlay guarda o `pin` (tag semver `vMAJOR.MINOR.PATCH`). Atualizar = re-implantar + commit do diff. **BREAKING** vs o estado atual (lei só no Cripto, skills `alan-workflow*`).
- **20 skills no produto:** `covenant-flow`, `covenant-flow-environments`, `grill-card`, `grilling`, `openspec-new-change`, `openspec-ff-change`, `openspec-apply-change`, `openspec-verify-change`, `openspec-archive-change`, `openspec-bulk-archive-change`, `openspec-continue-change`, `openspec-explore`, `openspec-onboard`, `openspec-sync-specs`, `github-project-board`, `kaizen`, `design-critic`, `impeccable`, `playwright-cli`, `implantar`.
- **3 adapters** (Cursor / Grok / OpenCode 1.18.18) em **todos** os consumidores: hooks, stubs ≤8 linhas, plugin. Adapters só traduzem; yaml é a lei.
- Overlay máquina: `.covenant-flow/overlay.yaml`. Markdown humano: `overlay_doc` (Cripto: `docs/crypto-overlay.md` permanece por projeto). Schema com chaves obrigatórias (board, repo, globs, pin, two-path, release hooks, clients, runtime). Quebra de schema = major (`v2.0.0`).
- Template `AGENTS.md` (tuple, chat≠δ, board URL gerada). Two-path genérico (`canonical_paths` / `forbidden_worktrees`). Release-guard **genérico** (checklist T16 + hooks `restart`/`migrate`/`build`/`health_url`). Helper `publish-openspec-card-artifacts.sh` viaja com o produto.
- Postura de review vive em `diff-reviewer.md` + `code-reviewer.md` (`inherit`, readonly). `REVIEW.md` opcional **sem** menção a Bugbot. **Não** entra Bugbot nativo nem `BUGBOT.md`.
- **Apply** (só com `Status=Pronto para Dev`): constrói o produto **fora de banda**; preenche overlay Cripto **enquanto** o Guard deste worktree ainda lê globs do yaml; só então `implantar --pin` **e** troca Guard/`page()` para overlay **no mesmo commit**. Esse commit inclui `.cursor/` `.grok/` `.opencode/` + overlay + `scripts/process-fsm/` + `.agents/skills/` (impeccable/design-critic/playwright-cli) + `AGENTS.md` gerado. Overlay vazio a meio do Apply **não** é caminho feliz. Host vivo intacto.
- **Troca viva (host):** o dia a dia desta máquina (Cursor/Grok/OpenCode a usar `covenant-flow*` em vez de `alan-workflow*`) **só** depois de #773 = `Pronto` (T16 / lote publicado). Não em Pronto para Dev, não no Apply. Até lá: sandbox só; vivo `alan-workflow` intacto. Antes de qualquer mutação no vivo: snapshot fresco (preferir `develop`). O backup `94f8ed41` é evidência histórica, não restore da troca. Evidência host no body da issue é host-only, não requisito do produto. `/home/ubuntu/covenant-flow-trial` é scratch descartável, não artefacto do produto.

**Não muda (honra Não entra):** copiar T0–T17/I1–I9 para `.grok/`/`.opencode/`; lock machine; `opencode.json` como contrato; quarto harness; Funil Cripto; conteúdo de `PRODUCT.md`/`DESIGN.md`/token sheet; PostgreSQL como always-on do **produto**; submodule/marketplace/template-clone como canal v1; OpenClaw; upgrade OpenCode além de 1.18.18; código de produto Cripto; UI/protótipo HTML; apagar peles atuais do Cripto antes do pin; troca viva do host antes de Pronto.

## Capabilities

### New Capabilities

- `covenant-flow`: produto portátil — repo, overlay schema, `implantar` + `install.sh --pin`, nomes das 20 skills, materialize-and-commit das peles no git do consumidor, pin semver, first-consumer Cripto no worktree, live-switch-at-Pronto (não em Pronto para Dev).

### Modified Capabilities

- `process-harness`: uma lei (yaml T0–T17 / I1–I9 / colunas / eventos / `context_file` / `enabled_tools`) + três adapters; **globs e board ids no overlay, não no yaml**; dual-write continua proibido; skills `covenant-flow*`; peles em todos os consumidores após pin; stubs ≤8 linhas; product **writes** fail-closed sem overlay; paging/`sessionStart` fail-open (unbound, sem dump do overlay).
- `cursor-harness`: adapter Cursor usa as skills `covenant-flow*`; overlay on-demand lê `overlay_doc` do overlay (Cripto: `docs/crypto-overlay.md`); `harness.mdc` / commands `/opsx-*` / kaizen viajam; Code Review sem Bugbot (`/review-bugbot` fora do produto); postura de review nos subagents versionados.
- `developer-tooling`: peles `.cursor/` `.grok/` `.opencode/` **commitadas** no git do consumidor (não gitignore, não submodule); `BUGBOT.md` deixa de ser requisito e **não** existe no produto; review stance em `diff-reviewer` + `code-reviewer` (`REVIEW.md` opcional sem Bugbot); skill `implantar` entra no conjunto versionado; skill de ambientes passa a `covenant-flow-environments` (valores no overlay, não no pacote).
- `cursor-code-review`: Bugbot nativo e `BUGBOT.md` saem do produto; gate = `diff-reviewer` + `code-reviewer`; `/review-security` MAY quando Alan pede explicitamente; postura de review nos dois agents (`REVIEW.md` opcional sem Bugbot).
- `process-fsm`: yaml empacotado MUST NOT declarar `product_globs`/`design_globs` como lei; permanece T0–T17, I1–I9, nomes das 12 colunas, eventos, `enabled_tools`. Globs vivem em `.covenant-flow/overlay.yaml`.
- `process-fsm-guard`: `decide()` classifica contra overlay `product_globs`/`design_globs`; Status-edit e o mover de `process_event` usam o módulo partilhado `board_status.py` com overlay `board.status_field_id` / `status_options` ids (MUST NOT hardcode Cripto `PVTSSF_*` em Python empacotado); overlay ausente/inválido = fail-closed em **writes** de produto; dual-write da lei continua proibido.
- `process-fsm-event`: reject `fechar_release` ¬`M_lote` MUST conter `covenant-flow-environments` (não `alan-workflow-ambientes`) e `release-guard`; mover lê overlay via `board_status` (sem `PVTSSF_*` hardcoded).
- `oracle-environment-map`: skill `covenant-flow-environments`; valores de topologia em overlay `environments.*`; skill empacotada MUST NOT hardcode paths/units Cripto/Clara/Hermes como o único mapa; OpenClaw continua fora.
- `process-fsm-paging`: fallback MUST NOT despejar `docs/crypto-overlay.md` hardcoded; usa `overlay_doc` do consumidor / nunca despeja o corpo do overlay.
- `release-archive-via-release-branch`: runbook on-demand = skill `covenant-flow`; overlay humano = `overlay_doc` (Cripto: `docs/crypto-overlay.md`).

## Impact

- **Produto novo** `oalansilva/covenant-flow` (privado, tags semver). Apply cria o repo e a primeira tag pinável.
- **Consumidor Cripto (worktree do card):** overlay preenchido **antes** do Guard fail-closed; pin commit = peles + overlay + `scripts/process-fsm/` + `.agents/skills/` + `AGENTS.md`; remove `BUGBOT.md` (ficheiros de harness, incluindo nested `backend/.cursor/` / `frontend/.cursor/`); skills `alan-workflow*` → stubs/aliases depois nomes novos. Globs/board/units no overlay, não no pacote.
- **Host vivo:** intacto até #773 = Pronto. Apply **não** troca nomes no dia a dia desta máquina.
- **Não toca:** `backend/` de produto, `frontend/src/`, Funil, `PRODUCT.md`/`DESIGN.md`/token sheet, PostgreSQL as always-on do pacote, OpenClaw, upgrade OpenCode, lock machine, `opencode.json`.
- Relacionado: #608 (epic EFSM), #720 (terceiro adapter), #584/#668 (anti dual-write). `UI impact: none`. Prototype N/A.
- Origem: issue #773 (DoD grelhado). Homologação do pin = worktree; troca viva = T16.
