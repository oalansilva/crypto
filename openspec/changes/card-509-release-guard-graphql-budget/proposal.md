## Why

O `release-guard post|audit` repete consultas completas ao GitHub Project por branch e por seção, esgotando a cota GraphQL compartilhada e tornando o fechamento de release indisponível. Quando a consulta falha, parte do inventário ainda confunde estado remoto desconhecido com card em andamento, o que enfraquece o comportamento fail-closed do guard.

## What Changes

- Carregar e validar uma única fotografia completa do Project por execução do guard, sem cache entre processos.
- Reutilizar a fotografia nos checks de títulos, changes terminais, branches, campos obrigatórios e homologação.
- Resolver o status de cards por lookup local tri-state (`terminal`, `non-terminal`, `unknown`) e bloquear modos estritos quando a informação remota for desconhecida.
- Carregar a lista de pull requests abertos uma única vez e indexá-la por branch, preservando `unknown` quando a consulta falhar.
- Validar presença e unicidade dos IDs de `RELEASE_CARDS` antes de aceitar campos e status.
- Tornar falhas por rate limit explícitas e corrigir o limite total da paginação do inventário de idade.
- Adicionar testes que provem a quantidade máxima de consultas e a semântica fail-closed.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `release-worktree-hygiene`: o guard passa a usar snapshots remotos únicos por execução e a tratar indisponibilidade/ambiguidade como estado desconhecido bloqueante em modos estritos.

## Impact

- `scripts/release-guard`: carregamento, validação e reutilização dos snapshots de Project e PRs; inventário de branches; validação do pacote; diagnóstico de rate limit.
- `backend/tests/integration/test_release_guard.py`: fake do GitHub CLI, contadores de chamadas e cenários de falha/ambiguidade.
- GitHub GraphQL: redução esperada de milhares para algumas centenas de pontos por execução, sem alterar dados do board.
- UI impact: none. Não há tela, componente, rota frontend ou interação visual afetada.
