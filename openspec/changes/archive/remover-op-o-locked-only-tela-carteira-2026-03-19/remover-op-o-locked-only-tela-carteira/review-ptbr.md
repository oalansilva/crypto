# Revisão: Remover "Locked Only" da tela da carteira

## O que muda

- **Remover toggle "Locked only"** do filtro da página Wallet (`/external/balances`)
- **Remover coluna "Locked"** da tabela de saldos
- O campo `locked` continuaexistindo na resposta da API (sem mudança no backend)

## Impacto

- **Frontend**: alterações apenas em `ExternalBalancesPage.tsx` e testes E2E em `external-balances.spec.ts`
- **Spec**: requisito removido do `external-balances/spec.md`

## Arquivos gerados

| Artefato | Arquivo |
|---|---|
| Proposal | `proposal.md` |
| Specs (delta) | `specs/external-balances/spec.md` |
| Design | `design.md` |
| Tasks | `tasks.md` |

📋 Aguardando seu ok para avançar para DESIGN.
