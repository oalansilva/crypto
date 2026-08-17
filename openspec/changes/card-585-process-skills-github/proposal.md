# Proposal: card-585-process-skills-github

## Why

O card #585 (origem no board) pediu revisar **onde vive cada regra**, versionar skills no GitHub e alinhar ao Cursor. Sem isso:

- Cursor é o harness ativo, mas `alan-workflow`, `alan-workflow-ambientes` e `github-project-board` ainda dependem de `~/.codex/skills/` ou `/srv/knowledge/hermes-second-brain/skills/`.
- Opção B (#584, **Cancelado**): symlink absoluto hermes — quebra clone e CI.
- `alan-workflow` descreve `Todo → In Progress` e “Codex review”; Design aparece como exceção.
- `github-project-board` sem `Em Refinamento`; exemplos `/root/.openclaw/...`.
- Anti-bypass repetido em quatro always-on; o modelo obedece o chat (`implemente todos em Todo`).
- `AGENTS.md` (~600 linhas) compete com `.cursor/rules` por contexto (doc Cursor: rules mínimas).
- Drive: skill global “não sincronizar” vs overlay do cripto que exige sync.

## What Changes

Incorpora o escopo do #584. Canônico = **arquivos reais** em `.cursor/skills/` no GitHub `oalansilva/crypto`. Padrão Cursor: harness alwaysApply curto; skills on-demand; `AGENTS.md` ponteiros; `rules.md` lei humana. Conteúdo das 3 skills = fluxo de 12 colunas + Cursor/`inherit`. Preflight de Design: Gist no card; OpenSpec **superset** do issue (Dev implementa pelo Gist).

## UI impact

`none`

## Capabilities

- `cursor-harness`
