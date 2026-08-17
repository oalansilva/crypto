## 1. Alerta de idade no guard

- [x] 1.1 Adicionar bloco `card_age_inventory` ao `scripts/release-guard` no modo `audit`
- [x] 1.2 Listar cards por coluna com idade em dias (fonte: GraphQL `updatedAt` do item via `gh api graphql`, já que `gh project item-list` não expõe timestamp)
- [x] 1.3 Emitir warn para cards com >30 dias sem atualização por coluna (máx. por coluna para evitar ruído)
- [x] 1.4 Tratar falha de obtenção de data como warn informativo, sem interromper inventário
- [x] 1.5 Validar saída do `release-guard audit` com cards reais do board (sem regressão em pre/post)

## 2. Triagem do #195

- [x] 2.1 Triar o #195 (avançar para `Todo` com prioridade, cancelar ou transferir) com comentário de decisão no card
- [x] 2.2 Registrar decisão no `docs/kaizen-log.md`

## 3. Testes e validação

- [x] 3.1 Executar `release-guard audit` e confirmar warn de idade + ausência de regressão
- [x] 3.2 Validação OpenSpec da change
