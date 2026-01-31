# Salvar Estratégia Combo nos Favoritos

## Por Que
Os usuários realizam backtests extensos e descoberta de parâmetros nas páginas de `/combo/select` e otimização. Quando uma estratégia lucrativa é encontrada (como a recente "Multi MA" com 24k% de retorno), o usuário atualmente não tem uma maneira direta de salvar essa configuração específica em sua lista de "Favoritos" para monitoramento ou implantação futura.

Isso exige copiar manualmente os parâmetros para uma nota separada ou tentar recriá-la na página de Favoritos, o que é propenso a erros.

## O Que Muda
Esta proposta introduz um fluxo de trabalho "Salvar nos Favoritos" diretamente da página de Validação/Resultados do Combo.

### Backend
- Garantir que `ComboBacktestResponse` (métricas e parâmetros) seja mapeado corretamente para o esquema `FavoriteStrategyCreate`.
- **Crítico**: Garantir que a métrica `total_return` salva no banco de dados seja o **Retorno Composto** (Crescimento Real), consistente com a lógica verificada de "71k%", e não a Soma Simples.

### Frontend
- Adicionar um botão "Salvar nos Favoritos" ao componente `ComboResults`.
- Abrir um modal com detalhes pré-preenchidos:
    - **Nome**: Gerado automaticamente (ex: "BTC 1d - NomeEstrategia - 24000% ROI") mas editável.
    - **Notas**: Campo de texto opcional para observações.
    - **Métricas**: Exibição somente leitura das principais métricas (ROI, WinRate, Drawdown).
    - **Parâmetros**: Payload JSON oculto/somente leitura.
- Chamar `POST /api/favorites` na confirmação.
- **Validação**: Verificar se já existe favorito com mesmo nome e alertar usuário.

### Métricas e Campos necessários para Salvar
Os seguintes campos serão preenchidos automaticamente a partir do Resultado do Backtest:
1.  **symbol**: (ex: `ETH/USDT`)
2.  **timeframe**: (ex: `1d`)
3.  **strategy_name**: (ex: `multi_ma_crossover`)
4.  **parameters**: O dicionário JSON exato usado no backtest (ex: `{'ema_short': 8, ...}`)
5.  **metrics**: Um dicionário contendo:
    - `total_return`: **Retorno Composto %** (Deve corresponder à nova lógica do otimizador).
    - `win_rate`: Win Rate %.
    - `total_trades`: Número de trades.
    - `max_drawdown`: Max drawdown %.
    - `sharpe_ratio`: Índice de Sharpe.
