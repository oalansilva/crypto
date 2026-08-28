## 1. Produto fora de banda (não mutar Guard deste worktree)

- [x] 1.1 Materializar a árvore `covenant-flow` **fora de banda** (dir irmão / extract): `.cursor/` yaml+hooks+rules+commands+agents, `.grok/`, `.opencode/plugin/`, `.agents/skills/` impeccable/design-critic/playwright-cli, `scripts/process-fsm/`, helpers — sem `alan` em nomes; **sem** meio-mutar o Guard deste worktree Cripto
- [x] 1.2 Renomear skills canónicas `alan-workflow` → `covenant-flow` e `alan-workflow-ambientes` → `covenant-flow-environments`; adicionar `implantar`; as 20 skills são: `covenant-flow`, `covenant-flow-environments`, `grill-card`, `grilling`, `openspec-new-change`, `openspec-ff-change`, `openspec-apply-change`, `openspec-verify-change`, `openspec-archive-change`, `openspec-bulk-archive-change`, `openspec-continue-change`, `openspec-explore`, `openspec-onboard`, `openspec-sync-specs`, `github-project-board`, `kaizen`, `design-critic`, `impeccable`, `playwright-cli`, `implantar`
- [x] 1.3 Gerar stubs Grok/OpenCode ≤8 linhas para os nomes novos; nenhuma tabela T0–T17 / I1–I9 em `.grok/` ou `.opencode/`
- [x] 1.4 Yaml empacotado MUST NOT declarar `product_globs`/`design_globs`; lei permanece T0–T17, I1–I9, nomes das 12 colunas, eventos, `enabled_tools`
- [x] 1.5 Não editar `backend/` nem `frontend/src/` de **produto**; não criar HTML de protótipo

## 2. Overlay schema, join status_options, fail-closed (no produto)

- [x] 2.1 Overlay template + validação de schema (chaves do `design.md`); `--init` deixa valores vazios e não chuta Cripto
- [x] 2.2 Join `board.status_options`: nomes = 12 colunas do yaml; ids = Project v2; fail-closed se nome ≠ yaml ou id em falta; overlay MUST NOT copiar T0–T17 / I1–I9
- [x] 2.3 Guard/`decide()` lêem globs e board ids do overlay; `board_status.py` (Guard **e** mover `process_event`) MUST NOT hardcode `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`; overlay ausente/inválido → deny de **product writes**; `page()`/`sessionStart` fail-open (unbound, sem dump do overlay)
- [x] 2.4 Projeto sem `environments.prod` / `release.*` vazios: skill `covenant-flow-environments` assume DEV; T16 recusa deploy; `fechar_release` ¬M_lote menciona `covenant-flow-environments` + `release-guard`
- [x] 2.5 Quebra de schema = bump major (`v2.0.0`); paging fallback MUST NOT despejar corpo de `overlay_doc`

## 3. implantar + install.sh --pin

- [x] 3.1 `install.sh --init` / `--pin <tag>` e skill `implantar`: copia nucleus (yaml + `scripts/process-fsm/`) + três adapters + `.agents/skills/` (impeccable/design-critic/playwright-cli) + helpers (publish-openspec, release-guard genérico) + template `AGENTS.md`; grava `pin`; não sobrescreve `overlay_doc`; recusa overlay vazio/inválido
- [x] 3.2 Bump de pin: re-copia nucleus/peles/helpers, preserva chaves de projeto, consumidor commita o diff
- [x] 3.3 Recusar submodule / gitignore / marketplace / template-clone como canal v1

## 4. Template AGENTS.md, two-path, helpers

- [x] 4.1 Template `AGENTS.md` (tuple, chat≠δ, board URL gerada, ≤40 linhas, overlay on-demand via `overlay_doc`)
- [x] 4.2 Two-path genérico via overlay `canonical_paths` / `forbidden_worktrees` (sem paths `/srv/apps/dev/criptofarol/...` no pacote)
- [x] 4.3 `release-guard` genérico: checklist T16 + hooks overlay `restart`/`migrate`/`build`/`health_url`
- [x] 4.4 Incluir `publish-openspec-card-artifacts.sh` no produto

## 5. Review sem Bugbot (harness, não lógica de produto)

- [x] 5.1 Mover postura de review para `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` (`inherit`, readonly); paths sensíveis no diff-reviewer, não em `BUGBOT.md`; `REVIEW.md` só se existir, sem Bugbot
- [x] 5.2 Apagar ficheiros de **harness** `.cursor/BUGBOT.md` e nested `backend/.cursor/BUGBOT.md` / `frontend/.cursor/BUGBOT.md` no pin Cripto (não alias). Isto é cleanup de harness versionado, **não** edição de lógica de produto em `backend/` ou `frontend/src/`
- [x] 5.3 `/review-bugbot` fora do produto (MUST NOT correr; skill não shipped). `/review-security` MAY se Alan pedir explicitamente; gate continua `diff-reviewer` + `code-reviewer`

## 6. Repo GitHub do produto + tag (ainda fora de banda)

- [x] 6.1 Criar repo GitHub **privado** `oalansilva/covenant-flow` (só neste Apply, com `Status=Pronto para Dev`)
- [x] 6.2 Push da árvore do produto e tag semver pinável `vMAJOR.MINOR.PATCH` (primeira tag v1.y.z)
- [x] 6.3 README do produto: clone + `implantar --init`/`--pin`; sem paths host-only, sem trial folder, sem `94f8ed41` como restore

## 7. Overlay Cripto preenchido **antes** de ligar Guard fail-closed

- [x] 7.1 **Neste** worktree, **enquanto o Guard atual ainda classifica globs pelo yaml:** `--init` se preciso e **preencher de imediato** `.covenant-flow/overlay.yaml` (board ids + 12 nomes iguais ao yaml, globs, environments, `overlay_doc: docs/crypto-overlay.md`, `pin`). Overlay vazio a meio **não** é sucesso
- [x] 7.2 Só então `implantar --pin` **e** trocar Guard/`page()` para overlay **no mesmo commit**. O commit inclui `.cursor/` `.grok/` `.opencode/` + overlay + `scripts/process-fsm/` (Guard overlay-reading) + `.agents/skills/` (impeccable/design-critic/playwright-cli) + `AGENTS.md` gerado
- [x] 7.3 `alan-workflow*` → stubs/aliases até o pin único, depois só `covenant-flow*` **no git**; não apagar peles `.grok/`/`.opencode/`
- [x] 7.4 **Não** renomear o host vivo (`~/.cursor/skills/alan-workflow*`, `~/.codex/skills/`, dia a dia Cursor/Grok/OpenCode); troca viva só com #773 = Pronto
- [x] 7.5 **Não** commitar `/home/ubuntu/covenant-flow-trial`; **não** restaurar vivo a partir de `94f8ed41`

## 8. Testes e verificação

- [x] 8.1 Goldens: `--init` chaves vazias; `--pin` recusa overlay vazio; join `status_options` falha se nome≠yaml ou id em falta; após pin, overlay inválido → fail-closed em **writes**; paging unbound fail-open; stubs ≤8 linhas; zero T0–T17/I1–I9 em `.grok/`/`.opencode/`; `board_status.py`, Guard e `process_event` empacotados sem `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`
- [x] 8.2 Ensaio deny Write produto com `q_git` da branch de integração nos três clientes **neste worktree** após pin (não reivindica Auto Grok/OpenCode)
- [x] 8.3 `openspec validate card-773-covenant-flow --type change --strict` verde; zero diff de UI `frontend/src/` / lógica de produto `backend/` (nested `backend/.cursor/BUGBOT.md` é harness)
- [x] 8.4 Confirmar host vivo ainda `alan-workflow*` no fim do Apply; documentar que snapshot fresco (preferir `develop`) é pré-requisito da troca viva em T16
