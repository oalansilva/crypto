# Design: card-585-process-skills-github

Este arquivo é o **refinamento do card #585**. O issue veio primeiro; o Dev implementa **a partir daqui** (Gist). Tudo que o card exige para codar está abaixo (superset).

## UI impact

`none` — harness, skills e docs. Sem superfície visual do produto. **Não** autoriza pular `Design` / `Aprovação de Design` / `Pronto para Dev`.

## Prototype

**N/A** — sem UI.

## Impeccable

**N/A** — `UI impact: none`.

## Origem

- Issue: [#585](https://github.com/oalansilva/crypto/issues/585)
- Incorpora [#584](https://github.com/oalansilva/crypto/issues/584) (Cancelado 2026-08-17, substituído por este card)
- Fontes Cursor: [Rules](https://cursor.com/docs/rules.md), [Skills](https://cursor.com/docs/skills.md), [Customizing agents](https://cursor.com/learn/customizing-agents)
- Change: `card-585-process-skills-github`
- Gist: republicar o mesmo (`crypto openspec card-585-process-skills-github`); sem Gist sprawl

## Card primeiro, OpenSpec mais completo (regra para todos os cards)

1. O **card** nasce primeiro (Em Refinamento → Todo): problema, objetivo, aceite, UI impact. Pode estar incompleto.
2. **Design** refina o card em OpenSpec (`proposal`, `design`, `specs`, `tasks`) + Gist no issue.
3. O OpenSpec/Gist SHALL ser **superset** do card: tudo que o Dev precisa para codar está no Gist, **incluindo** o que o issue já tinha.
4. Dev/`/opsx:apply` lê **Gist + `openspec/changes/<change>/`**, não o body do GitHub como spec paralela.
5. O issue continua origem e índice (objetivo + link do Gist). Se o chat acrescentar detalhe no card, **promover** para `design.md`/`specs` e republicar o **mesmo** Gist (`--gist-id` + `--comment-id`).
6. **Falha:** Gist mais pobre que o card. **Antes de Aprovação de Design:** copiar o que faltar para o OpenSpec; sem Gist/comentário, permanecer em `Design`.

## Problema (do card + crítica)

1. Skills globais fora do checkout GitHub (Codex / disco hermes).
2. Opção B (symlink `/srv/knowledge/hermes-second-brain/...`) **revogada** — quebra clone/CI.
3. Contrato obsoleto: `In Progress`, Codex, Design como exceção, board sem `Em Refinamento`, paths OpenClaw.
4. Always-on demais: `AGENTS.md` + harness + cópia da lei; o agente ignora o muro.
5. Drive contraditório (skill global vs `AGENTS.md` do cripto).
6. Design sem Gist no card (#585 na primeira passagem) — gap de evidência.

Cursor ainda **descobre** `~/.codex/skills/` por compatibilidade. O projeto **não** trata isso como canônico.

## Decisão de canônico (Alan 2026-08-17)

**GitHub do cripto manda.** As três skills são arquivos reais em `.cursor/skills/` no repo `oalansilva/crypto` (não symlink).

WIP `card-584-migrate-codex-skills-cursor` e `openspec/changes/card-584-migrate-codex-skills-cursor/` = insumo. **Não** mergear Opção B. **Não** commitar symlinks untracked em `/srv/apps/dev/criptofarol/source`.

### Ownership (crítica B1)

- Única fonte para Cursor **neste repo:** `.cursor/skills/<name>/`.
- Hermes e `~/.codex/skills/`: **freeze** neste card; sem dual-write; sem apagar globais sem Alan.
- Clara e outros repos: **fora de escopo**.

### Natureza da skill (B2)

Cópia **crypto-scoped** neste repo. Caminho primário:

`Em Refinamento → Todo → Design → Aprovação de Design → Pronto para Dev → Em desenvolvimento → Code Review → QA → Done → Homologado → Pronto`

(`Cancelado` terminal a qualquer momento, inclusive Em Refinamento.)

Cliente: Cursor Agent; Task/`inherit`; review do **diff exato** (não “Codex review”). Não é skill global multi-board com Design opcional.

### Inventário GitHub (B3)

| Incluir | Excluir |
| --- | --- |
| `SKILL.md`, `scripts/`, `references/` | `agents/openai.yaml` |
| `publish-openspec-card-artifacts.sh` com path **relativo** à skill no repo | `/root/.codex/...`, `/root/.openclaw/...` |

Aceite: `git ls-files`; modo de arquivo **≠** `120000` (não symlink).

`alan-workflow-ambientes` (mapa DEV/PROD) já está atual no conteúdo; ainda precisa **viver no GitHub** e perder `openai.yaml`/paths Codex.

### Orçamento de contexto (B4) — mapa do card, detalhado

Padrão Cursor: duas camadas (Rules estáticas vs Skills on-demand). `AGENTS.md` é alternativa a rules, não terceiro manual. `rules.md` na raiz **não** é injetado sozinho.

**Por que anti-bypass é Always Apply:** a skill pode não carregar em `implemente todos em Todo`.

```text
always-on (curto)   harness.mdc  →  Status; Em Refinamento; Todo ≠ código; Gist antes de Aprovação de Design; OpenSpec ≥ card
                    AGENTS.md    →  ponteiros (board, ports, Drive, skills)

on-demand           alan-workflow / alan-workflow-ambientes / github-project-board
                    openspec-* / kaizen / design-critic

lei humana          rules.md     →  o que nunca pular (harness aponta, não copia o runbook)
```

| Arquivo | Papel Cursor | Deve conter | Não deve conter |
| --- | --- | --- | --- |
| `.cursor/rules/harness.mdc` | Always Apply (única rule always-on) | Cliente Cursor; preflight `Status`; **Em Refinamento** é entrada; Todo→Design (não código); **Gist OpenSpec no card**; **OpenSpec superset do issue**; código só após Pronto para Dev; preferir `.cursor/skills/` do repo; “carregue `alan-workflow` em card/release” | 12 colunas detalhadas, OpenSpec CLI, mapa DEV/PROD, TL;DR longo |
| `AGENTS.md` | Ponteiros de projeto | Project 1, `rules.md`, skills em `.cursor/skills/`, ports/URLs curtos, Drive, PostgreSQL, release-guard, `./restart` | Contrato global duplicado; ~600 linhas de processo |
| `rules.md` | Lei humana | Anti-bypass + 12 colunas em 1 bloco; evidência de aprovação Alan | Comandos `gh`, tutorial |
| `.cursor/skills/alan-workflow/` | Skill processo | 12 colunas, 4 gates humanos, OpenSpec, review, QA, release; inherit; Drive = “siga AGENTS.md do repo” | Codex `fork_turns`; `~/.codex` canônico; helper `/root/.codex/...` |
| `.cursor/skills/alan-workflow-ambientes/` | Skill ambiente | Mapa DEV/PROD (Hermes, services, URLs) | Kanban |
| `.cursor/skills/github-project-board/` | Skill board | `gh project` + Status das 12 colunas; exemplo `/srv/apps/dev/criptofarol/source` → Project 1 | `/root/.openclaw/workspace/...` |
| `.cursor/skills/openspec-*` | Já no repo | `/opsx-*` | — |
| `.agents/skills/design-critic/` | Path oficial Cursor | Gate Design | Duplicar no harness |
| `docs/decision-log.md` | História | Canônico GitHub; anti-bypass; card vs Gist | Operar o dia a dia |

Gates humanos (agente não cruza): (0) Em Refinamento→Todo; (1) Aprovação de Design→Pronto para Dev; (2) Done→Homologado; (3) Homologado→Pronto.

Enforcement mecânico Status/Gist no CI: **fora de escopo**. Residual: o modelo ainda pode ignorar o gate.

## DoD de Design (todo card, incluso este)

Sem isto o card **não** vai para Aprovação de Design:

1. `design.md` + crítica isolada + veredito (Prototype/Impeccable N/A se UI none).
2. OpenSpec **superset** do issue (regra acima).
3. Gist secreto `crypto openspec <change>` com proposal/design/tasks/specs.
4. Comentário no card com o link (`publish-openspec-card-artifacts.sh`). Republicação: `--gist-id` + `--comment-id`.
5. Se UI: **Protótipo navegável** HTTP; HTML **não** no Gist.

## Implementação (somente `Status=Pronto para Dev`)

1. Copiar arquivos reais (inventário B3) de hermes/`~/.codex` → `.cursor/skills/` (não symlink).
2. Reescrever os 3 `SKILL.md` (12 colunas, Cursor, anti-bypass, helper relativo, Drive via AGENTS.md).
3. Enxugar `harness.mdc` (preflight: Status, Todo≠código, Gist, OpenSpec≥card) e `AGENTS.md` (ponteiros).
4. `rules.md` permanece lei; harness aponta.
5. Spec main `cursor-harness`; `decision-log`; palestra #582 (path `.cursor/skills/`).
6. PR `develop`; evidência `git ls-files .cursor/skills/alan-workflow/SKILL.md` (e irmãs); não modo symlink.
7. Não mergear `card-584-*` Opção B.

Fora de escopo: #581, #579, #580, #549, #472, #582.

## Critérios de aceite (do card, para o Dev)

- Checkout GitHub carrega as 3 skills sem hermes e sem depender de `~/.codex/skills/`.
- `alan-workflow` descreve `Em Refinamento → … → Pronto` (não `In Progress` como default).
- Always-on = harness curto; runbook = skills; lei = `rules.md`; `AGENTS.md` só aponta.
- `implemente` em Todo não autoriza código.
- Design sem Gist ou Gist mais pobre que o card = Design incompleto.
- Nada operacional só no VPS.

## Design Critique

Crítica isolada (Task read-only): BLOCKED inicial (B1–B4). Resolvido neste artefato (ownership, crypto-scoped, inventário, orçamento).

Pós-Alan: Gist obrigatório no Design; card primeiro / OpenSpec superset — incluídos aqui para o apply não perder.

## Design Agent verdict

**PASS** — UI N/A; blockers fechados; este `design.md` é superset do issue #585. Aguarda Alan em Aprovação de Design.
