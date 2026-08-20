# Proposal: card-582-palestra-upstream-deploy

## Why

O card #582 pede a palestra **Do upstream ao deploy: como automatizar o downstream sem remover os gates humanos** (caso Cripto Farol) para o **Agile Brazil 2026** ([site](https://www.agilebrazil.com/2026/)) — conferência da comunidade ágil em Foz do Iguaçu, 12–13 de novembro de 2026. O roteiro e o bloco de skills já existem; faltam o deck completo dos 7 blocos, evidências do board/card real, a enquete e um pacote copiável para projetor. Não é pitch de produto: é relato de experiência replicável para ~agilistas, produto e engenharia.

## What Changes

- Completar artefatos versionados da palestra em `docs/` (deck Markdown com blocos `--- SLIDE ---`, enquete, walkthrough de card real, mapa das 12 colunas), com slide de abertura no Agile Brazil 2026 (Foz, 12–13 nov).
- Preservar o bloco de skills já publicado; não reescrever o fluxo em vocabulário antigo (`Todo → In Progress`).
- Tom de **relato de experiência** para plateia de conferência (não demo comercial do Cripto Farol).
- Tese explícita de **human-in-the-loop**: automatizar evidência; humanos só nas decisões de julgamento/irreversíveis (os 4 gates). Não listar os gates sem o *porquê*.
- **Não** criar Google Slides automaticamente se `gog`/OAuth estiver indisponível: o Markdown copiável é o entregável canônico no GitHub; Drive/Slides fica pendência classificada.
- Ensaio cronometrado permanece entregável humano. Submissão Even3/CFP **não** entra neste card: o site oficial declara submissões encerradas em 26 de julho de 2026.

## UI impact

`none` — conteúdo de apresentação e docs. Sem alteração de superfície visual do produto. **Não** autoriza pular `Design` / `Aprovação de Design` / `Pronto para Dev`.

## Capabilities

### New Capabilities

- `palestra-upstream-deploy`: contrato dos artefatos da palestra (deck, enquete, evidência de board/card, fidelidade ao fluxo de 12 colunas e 4 gates humanos).

### Modified Capabilities

- Nenhuma. Specs de produto, harness e release-guard não mudam.

## Impact

- Arquivos em `docs/` (deck + evidências). Issue #582 como índice.
- Sem backend, frontend de produto, migrations, services ou `DESIGN.md`.
- Source DEV com WIP legado de `#584` permanece intocada; trabalho nesta change/worktree. Canônico de skills: `#585` (`.cursor/skills/` no GitHub).
