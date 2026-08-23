---
name: alan-workflow
description: "Use this skill for Alan's default operating process in any repo or workspace: cards/issues, GitHub Projects or Kanban, OpenSpec, implementation, validation, releases/publication, repo hygiene, AGENTS.md/rules cleanup, evidence reporting, and separating general workflow rules from project-specific rules."
---

# Alan Workflow

Contrato operacional **deste repo** (`oalansilva/crypto`). Canônico: `.cursor/skills/alan-workflow/` no GitHub. Não tratar `~/.codex/skills/` nem `/srv/knowledge/hermes-second-brain/skills/` como fonte.

Prioridade (δ e Guard > overlay > skill > wording):

1. **δ e Guard** (`.cursor/process-fsm.yaml`, `process_event`, hook Write).
2. **Overlay** (`docs/crypto-overlay.md` / stub `AGENTS.md`) — só quando a tarefa precisar de portas, Drive, PostgreSQL ou release.
3. **Esta skill** (runbook).
4. **Wording** do chat (`implemente`, `autorizo`, `gostaria sempre`).

Cliente: **Cursor Agent**. Task/subagent usa `inherit` salvo pedido explícito no chat. Review = diff **exato** (não “Codex review”).

Drive/Docs: `Read docs/crypto-overlay.md` on-demand neste repo. No cripto, Drive da Clara sincroniza com `docs/*.md`; não aplicar a regra global antiga “não sincronizar Drive”.

## Comunicação

PT-BR curto. Não diga `concluído` / `Pronto` / `publicado` até a evidência do estado ser verdadeira. `Done` = Done técnico.

## Colunas (Project 1)

Caminho obrigatório:

`Em Refinamento → Todo → Design → Aprovação de Design → Pronto para Dev → Em desenvolvimento → Code Review → QA → Done → Homologado → Pronto`

`Cancelado` é terminal a qualquer momento, inclusive Em Refinamento.

Gates humanos (agente não cruza): (0) Em Refinamento→Todo; (1) Aprovação de Design→Pronto para Dev (só Alan); (2) Done→Homologado. Homologado→Pronto é T16: `process_event fechar_release` após `release-guard post` PASS.

| Status | Significado |
| --- | --- |
| `Em Refinamento` | Entrada **e** grelha da história (`grill-card` no issue). Alan escolhe, prioriza ou cancela. T1 só Alan |
| `Todo` | Backlog (história já afiada). **Não é código.** Próxima etapa: Design |
| `Design` | OpenSpec sintetiza o issue grelhado + crítica; Gist no card; protótipo se UI. Não reentrevistar |
| `Aprovação de Design` | Aguardando Alan |
| `Pronto para Dev` | Design aprovado; único status que libera `/opsx:apply` |
| `Em desenvolvimento` | Implementando |
| `Code Review` | Diff pronto; review antes do commit |
| `QA` | SHA revisado em checks |
| `Done` | Done técnico em `develop` |
| `Homologado` | Alan aprovou em `develop` |
| `Pronto` | Publicado em `main` **e** deploy PROD validado |
| `Cancelado` | Não será feito |

**Anti-bypass:** pedido `implemente` / `implemente todos` **não** autoriza código nem `/opsx:apply` enquanto `Status=Todo`. `UI impact: none` não pula colunas.

## Preflight

Antes de editar:

- `git status -sb`; não misturar outra change.
- Overlay on-demand: `docs/crypto-overlay.md` só se portas/Drive/PG/release; lei: `rules.md`.
- Consultar `Status` no board (`github-project-board`).
- Release/deploy/PROD: carregar também `alan-workflow-ambientes`.

## Grill-card (Em Refinamento)

Skill de entrada: `.cursor/skills/grill-card/` (adapter). Primitivo vendorado: `.cursor/skills/grilling/`. **Não** usar `grill-with-docs` nem `to-spec`.

Disparar quando Alan pede para grelhar/afiar **ou** o card bound está em Em Refinamento **e** o body não tem as 6 seções do DoD. Não em todo T0 (cards nítidos podem T1 direto). Não em Todo/Design.

O agente reescreve o **body do issue** e, com fronteira vazia, comenta o handoff T1. Não arrasta Status. Não grava `CONTEXT.md` / `docs/adr/`. Não chama `/opsx:*`.

## Card primeiro, OpenSpec mais completo

1. O card nasce primeiro (pode estar incompleto). Em Refinamento: `grill-card` afia o issue; T1 continua só Alan.
2. Design refina em OpenSpec + Gist secreto `crypto openspec <change>`, **sintetizando** o issue grelhado (não reentrevista).
3. O Gist SHALL ser **superset** do issue. `/opsx:apply` lê Gist + `openspec/changes/`, não o body do GitHub como spec paralela.
4. Sem Gist/comentário no card, Design está incompleto. Republicar: `--gist-id` + `--comment-id`.
5. HTML de protótipo **não** vai no Gist. URL HTTP em bloco separado. No DEV Cripto, `/prototypes*` é servido por `criptofarol-dev-prototypes` (worktree + public/dist), sem fallback SPA.
6. Se o body em Design **não** tiver o DoD: não `/opsx:ff`; comentar as seções em falta; permanecer em Design. `/opsx:explore` só para furo técnico (código/specs), nunca para reescrever a história.

Helper (path relativo a esta skill no repo):

```bash
.cursor/skills/alan-workflow/scripts/publish-openspec-card-artifacts.sh \
  --repo oalansilva/crypto --issue <n> --change <change>
```

## OpenSpec

Usar skills `.cursor/skills/openspec-*` e CLI `openspec`. Não inventar artefatos fora de `openspec instructions`.

Ordem: `/opsx:new` → `/opsx:ff` → publicar Gist → Design → (Alan) Pronto para Dev → `/opsx:apply` → `/opsx:verify`. Archive só no fechamento de lote/release. Se o issue bound já tiver o DoD do `grill-card`, o briefing **é** o issue; não perguntar de novo o que construir; não invocar `grill-card` para gerar `proposal.md`. Sem schema `grill-driven`.

## Implementação

Só com `Status=Pronto para Dev`. Mover para `Em desenvolvimento` antes de editar código de produto/`scripts/` de produto. Branch `card-<id>-<slug>` ou `change-<id>-<slug>` a partir de `develop`.

Antes do commit: `Status=Code Review`, `diff-reviewer` + `code-reviewer` no diff não commitado vs HEAD. Depois do commit, ainda na branch e antes de `Status=QA`: `diff-reviewer` em `origin/develop...HEAD`. Então push e `Status=QA`. `/review-bugbot` só se Alan pedir.

Homologado: no **mesmo turno** do arraste/confirmação, `scripts/post-card-evidence-comment.sh --transition homologado` (mesmo sem lote).

## Release

Pedido explícito de Alan (`subir lote`, `fechar release`, …). Overlay de ambiente em `alan-workflow-ambientes`. Detalhe canônico: `docs/crypto-overlay.md` (Release em lote). No cripto: `scripts/release-guard pre` / `post`; `RELEASE_CARDS` nos exemplos de `pre` de lote; `PRESERVED_BRANCHES` no `pre` quando houver worktree in-flight. Homologação não autoriza `main`. Antes do `post`: `/kaizen release` no log **e** materialização Kaizen (1–3 cards em Em Refinamento, dedupe `coberto por #N` em fluxo, ou `Sem achados acionáveis`) — skill `kaizen` é read-only; o orquestrador cria os cards (#661).

Quando o push do archive em `develop` for recusado por proteção (`qa-gate`), mesmo com pacote só Homologado: use `release-*` = `origin/develop` + archive → PR `release-* → main`; `pre` em `release-*` **não** exige archive em `origin/develop`. Após merge + deploy PROD, sync `main → develop` é obrigatório antes do `post` final (reexecutar `post` se as árvores ainda divergirem). Não dual-write o playbook completo neste `SKILL.md` nem no stub `AGENTS.md`.

## Higiene

Worktree por change. Stash só temporário, classificado. Não dual-write esta skill para hermes/`~/.codex`.
