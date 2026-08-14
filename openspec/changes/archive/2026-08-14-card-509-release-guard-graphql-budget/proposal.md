## Why

O `scripts/release-guard` esgota a cota GraphQL compartilhada do GitHub. Uma execução de `gh project item-list 1 --owner oalansilva --limit 500 --format json` consumiu cerca de 202 pontos; hoje o guard pode repeti-la em até cinco checks e uma vez por branch em `card_is_terminal()` (13 nomes de branch), além de executar `gh pr list` por branch. Isso pode exceder os 5.000 pontos disponíveis por usuário/hora.

Há também uma falha fail-open: se a consulta ao board falhar, `card_is_terminal()` confunde estado desconhecido com card não terminal, permitindo que `post` preserve a branch como “card in flight” sem evidência autoritativa.

## What Changes

- Obter uma única fotografia completa do Project e uma única lista global de PRs abertos por execução de `post|audit`, carregadas no shell principal e reutilizadas por todos os checks.
- Validar exit code, JSON, completude do Project e estrutura/truncamento da lista de PRs antes de qualquer lookup.
- Resolver cards e PRs localmente com estados explícitos `terminal`, `non-terminal` e `unknown`; PRs são identificados por `(headRepositoryOwner.login, headRefName)`, e desconhecido bloqueia `post` e gera warning em `audit`.
- Tratar qualquer falha de snapshot imediatamente no nível global, mesmo sem consumidores relevantes na execução.
- Normalizar `RELEASE_CARDS` uma vez e validar formato, intervalo e identidade inequívoca por `(repository=oalansilva/crypto, issue number)`, além da presença de Status.
- Consultar o rate limit REST somente para diagnosticar falhas, sem retry ou polling.
- Corrigir o teto do inventário de idade para no máximo 19 requisições GraphQL, contando a página inicial e avisando explicitamente quando o resultado ficar truncado.
- Cobrir orçamento de chamadas e comportamento fail-closed com um fake `gh` e contadores.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `release-worktree-hygiene`: passa a operar com snapshots remotos únicos e completos por execução, orçamento explícito de chamadas e estado desconhecido fail-closed.

## Impact

- `scripts/release-guard`: loaders, lookups locais, validação do pacote, diagnóstico de rate limit e paginação de idade.
- `backend/tests/integration/test_release_guard.py`: fake `gh`, contadores e cenários de falha/ambiguidade.
- GitHub GraphQL: `post` limitado a até uma listagem de Project e uma de PRs; `audit` acrescenta no máximo 19 páginas do inventário de idade.
- UI impact: none. A mudança afeta somente script Bash operacional e testes, sem tela, rota, componente, copy ou interação visual.
