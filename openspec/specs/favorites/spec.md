# favorites Specification

## Purpose
TBD - created by syncing delta from change save-combo-favorites. Save combo strategy from results to favorites.

## Requirements

### Requirement: Salvar Estratégia dos Resultados do Combo
O sistema DEVE fornecer um mecanismo para salvar uma configuração específica de estratégia (incluindo parâmetros e métricas) da página de Resultados do Backtest de Combo para a lista de Favoritos. Botão "Salvar nos Favoritos", modal com nome e notas; evitar duplicatas (aviso sobrescrever ou salvar como novo).

### Requirement: Campo de Notas
O modal de salvamento DEVE incluir campo opcional "Notas", persistido no banco junto com a estratégia.

### Requirement: Armazenar Métricas Compostas
O sistema DEVE armazenar `total_return` como Retorno Composto ao salvar nos Favoritos. Painel de Favoritos exibe o mesmo retorno composto, não soma simples.
