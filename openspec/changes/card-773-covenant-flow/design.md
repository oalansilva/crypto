## Context

Card [#773](https://github.com/oalansilva/crypto/issues/773). Relacionado: [#608](https://github.com/oalansilva/crypto/issues/608) (epic EFSM), [#720](https://github.com/oalansilva/crypto/issues/720) (terceiro adapter), [#584](https://github.com/oalansilva/crypto/issues/584)/[#668](https://github.com/oalansilva/crypto/issues/668) (anti dual-write). Briefing = body grelhado (DoD completo). Fronteira de decisão vazia.

Hoje a lei (`.cursor/process-fsm.yaml` + `scripts/process-fsm/` + skills canónicas + três peles) vive só no git `oalansilva/crypto`. Outra máquina, Clara, Hermes ou greenfield não instala o processo; copiar skills/hooks à mão diverge. Skills operacionais chamam-se `alan-workflow` / `alan-workflow-ambientes`. Overlay humano é `docs/crypto-overlay.md` (Cripto). Code Review lê `.cursor/BUGBOT.md`. O host vivo desta máquina usa `alan-workflow*`.

O produto **Covenant Flow** (`oalansilva/covenant-flow`) extrai essa lei para um repo versionado. Consumidores implantam por pin. Primeiro consumidor: Cripto, no worktree deste card. Nomes do host vivo só depois de #773 = Pronto.

**UI impact: none.** Harness/productização de processo. Nenhuma rota, shell, componente ou copy de produto. Prototype N/A. Pipeline Impeccable *desta* coluna Design (shape/protótipo/crítica de tela) = N/A. Sem HTML.

Evidência host no body da issue (backup `94f8ed41`, pasta `/home/ubuntu/covenant-flow-trial`) é **host-only**: Design/Apply podem ler; **não** vira requisito do repo GitHub do produto. O trial é scratch descartável — não é probe, commit, nem artefacto OpenSpec.

## Goals / Non-Goals

**Goals:**

- Repo GitHub privado `oalansilva/covenant-flow` (Covenant Flow) com nucleus + 20 skills + 3 adapters + `implantar` + `install.sh --pin` + template `AGENTS.md` + overlay schema + helpers genéricos.
- Uma lei, três peles. Dual-write de T0–T17 / I1–I9 continua proibido. Lock machine continua morto. Sem `opencode.json` como contrato. Sem quarto harness. Sem Bugbot. Sem `BUGBOT.md`.
- Canal v1: copiar peles; consumidor **commita** `.cursor/` `.grok/` `.opencode/`; overlay guarda `pin` semver; bump = re-implantar + commit do diff.
- Overlay máquina `.covenant-flow/overlay.yaml`; humano `overlay_doc` por projeto (Cripto: `docs/crypto-overlay.md`). Fail-closed sem overlay válido. Quebra de schema = major.
- Nomes de skill/produto sem `alan`: `covenant-flow`, `covenant-flow-environments`, `implantar`.
- Apply (#773 em Pronto para Dev): cria o repo, primeira tag pinável, pina o Cripto **neste worktree**. Não troca o host vivo.
- Troca viva do host só com #773 = Pronto (T16 / lote publicado), depois de snapshot fresco (preferir `develop`).

**Non-Goals:**

- Copiar T0–T17 / I1–I9 para `.grok/rules` ou `.opencode/`.
- Lock machine (`design-planner`, lease, packet, attestation, `opencode.db`).
- `opencode.json` como contrato de modelo/MCP/permission.
- Quarto harness (Codex home / Hermes Second Brain) como fonte da lei; dual-write Hermes / `~/.codex/skills/`.
- Bugbot do Cursor e ficheiro `BUGBOT.md` (nome ou conteúdo).
- Funil Cripto; conteúdo de `PRODUCT.md` / `DESIGN.md` / token sheet (contrato de lookup entra; marca não).
- PostgreSQL obrigatório como always-on do **produto** (fica no overlay do consumidor).
- Submodule / marketplace nativo / template-clone como canal v1; peles só-ponteiro ou gitignore.
- OpenClaw; upgrade OpenCode além de 1.18.18.
- Código de produto Cripto (`backend/`, `frontend/src/`); UI / protótipo HTML.
- Apagar as peles atuais do Cripto **antes** do pin no git do consumidor.
- Troca dos nomes do **host vivo** em Pronto para Dev, no Apply, ou em qualquer Status anterior a Pronto.
- Pasta `/home/ubuntu/covenant-flow-trial` como artefacto do produto.
- Usar o backup `94f8ed41` / `fix-kaizen-heading-2` como restore canónico da troca viva.

## Decisions

1. **Nome do produto e das skills: Covenant Flow / `covenant-flow`, zero `alan`.**  
   Repo `oalansilva/covenant-flow`. Skill operacional = `covenant-flow` (ex-`alan-workflow`). Skill de ambientes = `covenant-flow-environments` (ex-`alan-workflow-ambientes`). Skill nova = `implantar`. Covenant = o grafo é o programa; Flow = caminho XOR das 12 colunas / `Status` (não o campo legado `Fluxo`).  
   **Rejeitado:** manter `alan-workflow*` no produto (amarra a marca pessoal; o issue fecha `_Avoid: skills ou pastas alan-*`). **Rejeitado:** `alan-process` como nome de repo (título legado do item no Project 1; não é o produto).

2. **Canal v1 = materialize-and-commit, não submodule.**  
   `implantar` + `install.sh --pin` **copia** as peles para o consumidor. O consumidor **commita** `.cursor/` `.grok/` `.opencode/` no próprio git. Overlay regista `pin: vMAJOR.MINOR.PATCH`. Bump = re-implantar + commit do diff.  
   **Rejeitado:** git submodule (canal v1). Peles só-ponteiro ou gitignore deixam o consumidor sem harness no clone. **Rejeitado:** marketplace nativo Cursor/OpenCode (fora de v1). **Rejeitado:** template-clone como primário (não atualiza por pin). **Rejeitado:** consumidor que só aponta para o repo do produto sem copiar.

3. **Overlay máquina = `.covenant-flow/overlay.yaml`; humano = `overlay_doc` por projeto.**  
   Path do yaml de máquina é do produto e é fixo. O Markdown humano **não** viaja com um nome único: Cripto continua `docs/crypto-overlay.md`; Clara/Hermes/greenfield escolhem o seu. `AGENTS.md` gerado aponta para o valor de `overlay_doc`.  
   **Rejeitado:** `docs/crypto-overlay.md` como path canónico do produto (é Cripto, não portátil). **Rejeitado:** fundir máquina e humano num único Markdown (parse frágil; fail-closed precisa de yaml). **Rejeitado:** overlay só em home do utilizador (não viaja com o clone do consumidor).

4. **Lei no yaml; parâmetros no overlay. Globs/board ids/units saem do pacote.**  
   `process-fsm.yaml` continua a ser a lei (T0–T17, I1–I9, nomes das 12 colunas, eventos, `enabled_tools`, Moore stubs genéricos). **MUST NOT** declarar `product_globs`/`design_globs` como lei. Overlay carrega: `board.*` (ids Project v2; **nomes** das colunas = lei via join), `repo`, `product_globs`, `design_globs`, `integration_branch`, `production_branch`, `pin`, `environments.dev|prod` (`source`, `url`, `db`, `services[]`), `canonical_paths`, `forbidden_worktrees`, `release.{restart,migrate,build,health_url}`, `overlay_doc`, `clients`, paths Impeccable, `runtime.playwright`, `runtime.database` opcional. Guard/`decide()` lêem globs e board ids do overlay: **product writes fail-closed** se overlay faltar ou for inválido. `page()`/`sessionStart` **permanecem fail-open** (página unbound) e MUST NOT despejar o corpo do overlay. Projeto sem PROD omite `environments.prod`; skill ambientes assume DEV e recusa produção; T16 recusa deploy se hooks de release vazios.  
   **Rejeitado:** empacotar `product_globs` / units systemd / URLs do Cripto no yaml do produto (o pacote deixaria de ser portátil). **Rejeitado:** segunda cópia da tabela δ no overlay (dual-write). **Rejeitado:** paging fail-closed (abortar o turno) por overlay em falta.

5. **Árvore do produto = forma de consumidor + `install.sh` + template de overlay.**  
   O repo `covenant-flow` versiona a mesma geometria que o consumidor precisa. `install.sh` / `implantar --pin` copia: **nucleus** (`process-fsm.yaml` + `scripts/process-fsm/`), **três adapters** (`.cursor/` `.grok/` `.opencode/plugin/`), **`.agents/skills/`** (impeccable, design-critic, playwright-cli), **helpers** (`publish-openspec-card-artifacts.sh`, release-guard genérico), **template `AGENTS.md`**. Skills canónicas nas 20 pastas nomeadas; stubs Grok/OpenCode ≤8 linhas. No Cripto (já tem `scripts/process-fsm/`), o pin **atualiza** esses scripts para o Guard que lê overlay.  
   **Rejeitado:** árvore “neutra” `adapters/cursor|grok|opencode` que re-deriva peles no implantar (risco de dual-write da lei). **Rejeitado:** copiar só as três peles e deixar nucleus/helpers de fora. **Rejeitado:** skills só em `~/.cursor/skills` do host.

6. **`implantar --init` não chuta; `--pin` exige overlay **já válido**.**  
   `--init` num repo alvo cria `.covenant-flow/overlay.yaml` a partir do template e lista as chaves obrigatórias **vazias**. `--pin v1.2.3` exige overlay preenchido e válido, copia nucleus+adapters+`.agents/skills/`+helpers+template `AGENTS.md`, escreve `pin: v1.2.3`. Não sobrescreve o Markdown `overlay_doc`. Merge de bump preserva chaves de projeto e só atualiza peles/nucleus/helpers + `pin`. Overlay vazio **não** é caminho feliz de `--pin` nem de Guard fail-closed.  
   **Rejeitado:** `--init` que preenche board/globs “por defeito Cripto”. **Rejeitado:** ligar Guard fail-closed sobre overlay vazio. **Rejeitado:** pin só num ficheiro solto fora do overlay.

7. **Semver `v1.2.3`; quebra do schema do overlay = major (`v2.0.0`).**  
   Tags no repo do produto. Consumidor pinado numa tag. Schema break = remover/renomear chave obrigatória, mudar tipo, ou mudar o significado de uma chave de lei (ex.: nomes das 12 colunas no overlay a contradizer o yaml).  
   **Rejeitado:** CalVer. **Rejeitado:** pin = SHA solto sem tag. **Rejeitado:** minor para quebra de schema.

8. **Apply: produto fora de banda → overlay Cripto preenchido → pin+Guard no mesmo commit. Não troca o host vivo.**  
   Com `Status=Pronto para Dev`, XOR:
   a) Construir a árvore do produto **fora de banda** (dir irmão / extract). **Não** meio-mutar o Guard deste worktree enquanto o overlay ainda está vazio.  
   b) Preencher `.covenant-flow/overlay.yaml` do Cripto (board/globs/environments/`overlay_doc`/`pin`) **enquanto** este worktree ainda usa o Guard atual (globs no yaml). `--init` no Cripto é imediatamente seguido de preencher as chaves; overlay vazio a meio **não** é sucesso.  
   c) Só então `implantar --pin` (nucleus+peles+helpers+`AGENTS.md`) **e** troca Guard/`page()` para ler overlay — **no mesmo commit de pin**.  
   d) Esse commit do git consumidor inclui `.cursor/` `.grok/` `.opencode/` + overlay + `scripts/process-fsm/` (Guard overlay-reading) + `.agents/skills/` (impeccable/design-critic/playwright-cli) + `AGENTS.md` gerado.  
   e) Host vivo continua `alan-workflow*` até Pronto. `alan-workflow*` no git → stubs/aliases até pin único, depois só nomes novos. `BUGBOT.md` e homónimos de harness (raiz e nested `backend/.cursor/` / `frontend/.cursor/`) **saem** (não alias) — é cleanup de harness, não lógica de produto `backend/`.  
   **Rejeitado:** ligar fail-closed overlay-Guard neste worktree **antes** do overlay Cripto válido. **Rejeitado:** troca viva em Pronto para Dev / no Apply / em Design. **Rejeitado:** criar o repo GitHub do produto antes de Pronto para Dev. A janela “git do Cripto já tem nomes novos, host ainda `alan-workflow`” é residual aceite até T16.

9. **Troca viva (host) só com #773 = Pronto.**  
   Depois de T16 / lote publicado: snapshot **fresco** do que estiver vivo (preferir `develop`) **antes** de qualquer mutação; depois o host passa a `covenant-flow*`. O backup `94f8ed41` / `fix-kaizen-heading-2` / `/home/ubuntu/backups/covenant-flow-pre-773-*` é evidência histórica, não restore dessa troca.  
   **Rejeitado:** usar `94f8ed41` como restore canónico. **Rejeitado:** tratar `/home/ubuntu/covenant-flow-trial` como canónico ou como artefacto do produto. **Rejeitado:** mutar `~/.cursor/skills/alan-workflow*` no Apply.

10. **20 skills enumeradas; três adapters; OpenCode 1.18.18.**  
    Skills (20): `covenant-flow`, `covenant-flow-environments`, `grill-card`, `grilling`, `openspec-new-change`, `openspec-ff-change`, `openspec-apply-change`, `openspec-verify-change`, `openspec-archive-change`, `openspec-bulk-archive-change`, `openspec-continue-change`, `openspec-explore`, `openspec-onboard`, `openspec-sync-specs`, `github-project-board`, `kaizen`, `design-critic`, `impeccable`, `playwright-cli`, `implantar`. Peles Cursor / Grok / OpenCode 1.18.18 como no DoD. Stubs ≤8 linhas.  
    **Rejeitado:** upgrade OpenCode neste card. **Rejeitado:** apagar `.grok/`/`.opencode/` do Cripto no cutover. **Rejeitado:** quarto harness. **Rejeitado:** copiar a tabela para as peles.

11. **Review: postura nos agents; Bugbot/`BUGBOT.md` fora; `/review-security` MAY se Alan pedir.**  
    `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` (`inherit`, readonly) carregam as regras (incluindo paths sensíveis: auth/credencial/wallet/trading/API). `REVIEW.md` MAY existir **sem** menção a Bugbot. Code Review gate = os dois reviewers. `/review-bugbot` e `BUGBOT.md` **não** entram no produto (MUST NOT correr mesmo que alguém peça como path de produto; skill não é shipped). `/review-security` **MAY** correr quando Alan pede explicitamente; não substitui o gate.  
    **Rejeitado:** manter `BUGBOT.md` como alias. **Rejeitado:** Bugbot nativo no fluxo. **Rejeitado:** REVIEW.md obrigatório. **Rejeitado:** remover `/review-security` como MAY-when-Alan-asks.

12. **Helpers genéricos viajam; valores não.**  
    `publish-openspec-card-artifacts.sh` entra no produto. `release-guard` torna-se genérico: checklist T16 + chama `release.{restart,migrate,build,health_url}` do overlay. Two-path = `canonical_paths` / `forbidden_worktrees` no overlay. Template `AGENTS.md`: tuple, chat≠δ, board URL gerada, ≤40 linhas, overlay on-demand via `overlay_doc`. Paging fallback MUST NOT despejar o corpo do overlay (`overlay_doc`; Cripto: `docs/crypto-overlay.md`).  
    **Rejeitado:** empacotar o funil Cripto, `PRODUCT.md`, `DESIGN.md`, token sheet. **Rejeitado:** PostgreSQL como always-on do pacote. **Rejeitado:** release-guard com units systemd do Cripto hardcoded.

13. **Primeiro consumidor = Cripto, um canónico no git/worktree.**  
    Depois do pin neste worktree: um canónico pinado; globs/board/units no overlay; peles `.grok/`/`.opencode/` permanecem; skills `alan-workflow*` são stubs/aliases e depois só os nomes novos. Clara / Hermes / greenfield são consumidores **seguintes**, fora deste card. A skill `covenant-flow-environments` **não** exige Hermes como único mapa; valores vêm do overlay (Cripto preenche o seu). OpenClaw continua fora. Ensaio deny Write produto com `q_git` da branch de integração corre no Cripto pinado (worktree), não no host vivo.  
    **Rejeitado:** cutover simultâneo de Clara/Hermes neste card. **Rejeitado:** dois canónicos (home + repo) depois do pin. **Rejeitado:** skill de ambientes que hardcode paths Cripto/Clara/Hermes como o único mapa.

14. **Join `board.status_options`: ids no overlay, nomes = yaml, sem copiar a lei.**  
    Overlay guarda **ids** Project v2. Os **nomes** em `board.status_options` MUST ser exactamente os 12 nomes de coluna em `process-fsm.yaml`. Validação = join nome→id. Fail-closed se um nome não bater com o yaml ou se faltar um id. Overlay MUST NOT copiar T0–T17 / I1–I9. O módulo partilhado `scripts/process-fsm/board_status.py` (Guard **e** mover de `process_event`) lê `board.status_field_id` e ids de `status_options` do overlay. Python empacotado MUST NOT hardcode `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`.  
    **Rejeitado:** copiar a tabela de transições para o overlay. **Rejeitado:** nomes só-overlay que podem divergir do yaml.

15. **Prioridade da skill: `covenant-flow skill priority is delta and Guard first`.**  
    O requisito Cursor deixa de se chamar `alan-workflow skill priority…`. Corpo: δ e Guard > overlay > skill > wording; overlay on-demand via `overlay_doc`.

## Apply contract

Apply corre só com `Status=Pronto para Dev`, no worktree `card-773-covenant-flow`. **Não** é este turno Design. **Não** muta o host vivo. **Não** liga Guard fail-closed sobre overlay vazio neste worktree.

Ordem XOR:

1. Extrair/renomear nucleus + 20 skills + 3 peles + helpers para a árvore do produto **fora de banda** (dir irmão / extract; sem `alan`; sem `BUGBOT.md`; sem T0–T17 em `.grok/`/`.opencode/`; yaml sem `product_globs`/`design_globs` — esses vão ao overlay). `install.sh --init` / `--pin`; skill `implantar`; overlay template + validação (join `status_options` nome→id); template `AGENTS.md`; release-guard genérico; helper `publish-openspec-card-artifacts.sh`. Criar repo GitHub **privado** `oalansilva/covenant-flow`, push, tag `v1.y.z`.
2. Neste worktree Cripto, **ainda com o Guard atual (globs no yaml):** `--init` se preciso e **preencher de imediato** `.covenant-flow/overlay.yaml` (board ids + nomes das 12 colunas iguais ao yaml, globs, environments, `overlay_doc: docs/crypto-overlay.md`, `pin`). Overlay vazio a meio **não** é sucesso.
3. Só então `implantar --pin` **e** troca Guard/`page()` para overlay **no mesmo commit**. O commit inclui `.cursor/` `.grok/` `.opencode/` + overlay + `scripts/process-fsm/` (Guard overlay-reading) + `.agents/skills/` (impeccable/design-critic/playwright-cli) + `AGENTS.md` gerado. `docs/crypto-overlay.md` permanece o humano Cripto.
4. `alan-workflow*` → stubs/aliases até o pin único, depois só `covenant-flow*`. Remover `.cursor/BUGBOT.md` e homónimos **de harness** `backend/.cursor/BUGBOT.md` / `frontend/.cursor/BUGBOT.md` (não é lógica de produto backend/frontend; não alias). Postura de review nos agents; `/review-security` MAY se Alan pedir; Bugbot fora.
5. Goldens: overlay inválido/ausente → deny de **product writes** depois do pin commit (`sessionStart` continua fail-open); join `status_options` falha se nome≠yaml ou id em falta; `--init` deixa chaves vazias; `--pin` recusa overlay vazio; nenhuma tabela T0–T17/I1–I9 nas peles Grok/OpenCode; `board_status.py` / Guard / `process_event` sem `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM` empacotado; `openspec validate` da change.
6. Ensaio deny Write produto com `q_git` da branch de integração nos três clientes **neste worktree** após pin (não reivindica Auto Grok/OpenCode).
7. Zero `frontend/src/` e zero `backend/` de **produto**. Nested `backend/.cursor/BUGBOT.md` é ficheiro de harness. Zero troca de `~/.cursor/skills/alan-workflow*` / `~/.codex/skills/`. Zero commit da pasta trial. Zero restore a partir de `94f8ed41`.
8. Troca viva do host **não** é task de Apply; fica para #773 = Pronto (T16), com snapshot fresco prévio.

## Risks / Trade-offs

- [Guard fail-closed antes do overlay preenchido] → mitigado pela ordem XOR (D8): overlay válido **antes** de trocar o Guard; `--pin` recusa overlay vazio. Empty overlay mid-Apply não é sucesso.
- [Janela git-novo / host-antigo até Pronto] → aceite. Apply documenta; T16 faz a troca viva. Não acelerar a troca para “alinhar nomes”.
- [Diffs de bump de pin ruidosos] → residual do canal copy+commit. Mitigação: copiar só peles; não reformatar overlay de projeto. Kaizen posterior se o ruído doer.
- [Plugin OpenCode 1.18.18 pode não carregar] → residual #720; `session.idle` já é fail-open. Ensaio no worktree pinado; sem upgrade.
- [Título do item no Project 1 ainda diz `alan-process`] → cosmético do board; produto é `covenant-flow`. Não é requisito de rename do Project neste card.
- [Guard passa a depender do overlay] → **product writes** fail-closed se overlay em falta/inválido. Paging/`sessionStart` fail-open (unbound, sem dump). `--init` não chuta valores. Testes de schema no produto.
- [Cripto `process-fsm.yaml` hoje tem globs Cripto] → Apply **move** globs/ids para o overlay; yaml do produto fica lei. Risco de omitir uma chave → ensaio deny no worktree.
- [Stubs `alan-workflow*` durante a transição] → necessários para o host antigo enquanto o git já tem nomes novos. Depois do pin único no git, só nomes novos **no git**; host continua antigo até Pronto.
- [Sandbox trial confundido com produto] → OpenSpec e Apply **não** referem a pasta como artefacto; README do produto não a cita como canónico.
- [Dois restores] → `94f8ed41` histórico; snapshot fresco obrigatório antes da troca viva. Design/Apply não restauram o vivo a partir do backup antigo.

## Migration Plan

Três fases, XOR:

1. **Design (agora):** só OpenSpec neste worktree. Sem repo GitHub do produto. Sem pin. Sem mutação do host. Sem HTML.
2. **Apply (Pronto para Dev):** (a) produto fora de banda + repo GitHub; (b) overlay Cripto preenchido com Guard yaml-globs ainda vivo; (c) pin+Guard overlay no mesmo commit. Host vivo intacto. Rollback = reverter o commit do consumidor e apagar/arquivar o repo do produto se ainda sem outros consumidores. Sem migration de banco. Sem rebuild de frontend.
3. **Troca viva (Pronto / T16):** snapshot fresco (preferir `develop`) → host passa a `covenant-flow*`. Rollback do host = restore **desse** snapshot, não `94f8ed41`.

Rollback intermédio (entre Apply e Pronto): worktree/git do Cripto pode reverter o commit de pin; o repo do produto pode permanecer (é o pacote). O vivo não precisa de rollback porque não foi mutado.

## Open Questions

Nenhuma bloqueante (grelha vazia, rodada 2 fechada). Residuais operacionais (plugin OpenCode, diffs de bump, janela de nomes, título `alan-process` no Project) não são forks de produto.

## UI impact

**none** — productização do harness/processo (repo, overlay, skills, peles, pin). Nenhuma superfície visual do Cripto Farol (rota, shell, componente, copy, token, protótipo HTML). Nenhuma tela nova ou alterada. O aceite visível é clone+implantar+pin no git do consumidor e deny de Write ilegal após pin — não um ecrã.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar nem HTML a servir. Pipeline Impeccable desta coluna (shape / prototype / screen critique / browser gate) = N/A: o card não desenha UI; `DESIGN.md` e a folha de tokens não são autoridade deste trabalho. Snapshot Impeccable = N/A justificado. O filho autor não escreve `## Design Critique`.

## Prototype Validation

N/A — sem protótipo HTML, sem URL DEV `/prototypes/*`, sem Playwright de tela neste card. Validação de Apply = goldens de overlay/pin/dual-write + ensaio deny no worktree, não browser de produto.

## Design Critique

- P0: nenhum (A, B, A2, B2, A3, B3).
- P1 onda 1 (A+B, aberto → patch → fechado): deltas irmãos (`process-fsm`, Guard, event, `oracle-environment-map`, leftover stubs, paging, release-archive); join `board.status_options` nome→id sem copiar T0–T17; Apply XOR (overlay preenchido antes do Guard fail-closed; pin commit com `scripts/process-fsm/` + `AGENTS.md`); `implantar` copia nucleus+adapters+helpers. Disposition: **closed**.
- P1 onda 2 (A, aberto → patch → fechado): `process-harness` «Process law has one nucleus…» ainda mandava glob no yaml. MODIFIED: globs/board ids no overlay; colunas/invariantes/`context_file` no yaml. Disposition: **closed**.
- P2 (accepted-residual): janela git-novo / host-`alan-workflow` até Pronto; plugin OpenCode 1.18.18 fail-open; diffs de bump; título do item Project `alan-process`; live-switch na spec Apply-scoped (tasks 7.4/8.4 = deny+documentar); nomes em `status_options` = join D14, não segunda tabela.
- P3 (accepted-residual): título MODIFIED `alan-workflow skill priority` + bloco RENAMED; «two adapters» vs três; título `cursor-code-review` MAY vs corpo Bugbot MUST NOT; schema `clients`/paths Impeccable sem forma YAML; `palestra-upstream-deploy` fora de recorte.

Prototype: N/A — harness/productização de processo; nenhuma tela de produto.

Snapshot Impeccable (visual): N/A justificado (`UI impact: none`). Evidência A/B isolada (git-tracked; Gist não envia):
- `.impeccable/critique/773-card-773-covenant-flow-20260828T025700Z-A.md` (A3 PASS)
- `.impeccable/critique/773-card-773-covenant-flow-B-r3.md` (B3 PASS)

Design Agent verdict: PASS
