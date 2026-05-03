## Context

A tela Monitor usa um topo global (`AppNav`) e uma área própria de filtros/tabela (`MonitorStatusTab`). O print do card 116 marca elementos nos dois pontos.

## Goals / Non-Goals

**Goals:**
- Remover apenas os elementos destacados no card 116.
- Preservar ações úteis de gráfico e favorito.
- Manter a tabela funcional e com `colSpan` correto quando linhas forem expandidas.

**Non-Goals:**
- Não redesenhar a tela inteira.
- Não alterar lógica de cálculo, carteira, favoritos ou status.
- Não remover o botão `Atualizar` nem o toggle de tema.

## Decisions

- Remover o badge `Binance system` no `AppNav`.
  - Racional: o item é puramente informativo e foi destacado para remoção.
- Remover o grupo de ordenação visível.
  - Racional: a ordenação padrão por tier/distância continua operando, mas os botões destacados deixam de ocupar espaço.
- Remover a coluna final de status e manter a coluna inicial `Status`.
  - Racional: havia duas colunas com o mesmo cabeçalho, e a final duplica o estado já exibido.
- Remover só o botão `...`, mantendo gráfico e favorito.
  - Racional: `...` não executa ação útil hoje; gráfico e favorito seguem sendo comandos diretos.

## Risks / Trade-offs

- [Risk] Remover coluna altera o `colSpan` do detalhe expandido.
  - Mitigation: recalcular `detailColSpan` para as colunas restantes.
- [Risk] Teste existente assumia duas colunas `Status`.
  - Mitigation: atualizar E2E para exigir apenas um `Status`.
