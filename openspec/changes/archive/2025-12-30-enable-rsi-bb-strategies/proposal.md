# Proposta: Habilitar Estratégias RSI Reversal e Bollinger Bands

## Objetivo
Habilitar as estratégias RSI Reversal e Bollinger Bands no formulário Custom Backtest, permitindo configuração dinâmica de parâmetros e visualização dos indicadores no gráfico de resultados (estilo TradingView).

## Por Quê
Atualmente, apenas a estratégia SMA Cross está funcional. As estratégias RSI Reversal e Bollinger Bands estão implementadas no backend mas desabilitadas no frontend. O usuário precisa poder testar diferentes estratégias e ver os indicadores correspondentes (linha RSI, bandas de Bollinger) no gráfico para análise visual.

## O Que Muda

### Backend
#### [CRIAR] [rsi_reversal.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/src/strategy/rsi_reversal.py)
- Verificar se a estratégia retorna DataFrame com indicador `rsi` (similar ao SMA Cross).
- Se necessário, atualizar para retornar DataFrame completo.

#### [CRIAR] [bb_meanrev.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/src/strategy/bb_meanrev.py)
- Verificar se retorna DataFrame com `bb_upper`, `bb_middle`, `bb_lower`.
- Se necessário, atualizar para retornar DataFrame completo.

#### [MODIFICAR] [backtest_service.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/backend/app/services/backtest_service.py)
- Adicionar mapeamento de cores para indicadores RSI e BB:
  - `rsi` → Roxo (`#8b5cf6`)
  - `bb_upper` → Azul claro (`#60a5fa`)
  - `bb_middle` → Amarelo (`#fbbf24`)
  - `bb_lower` → Azul claro (`#60a5fa`)
- Formatar nomes dos indicadores com parâmetros (ex: "RSI(14)", "BB(20,2)")

### Frontend
#### [MODIFICAR] [CustomBacktestForm.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/CustomBacktestForm.tsx)
- Remover `disabled` das estratégias RSI Reversal e Bollinger Bands.
- Adicionar seções de parâmetros condicionais:
  - **RSI Reversal**: campos para `rsi_period`, `oversold`, `overbought`
  - **Bollinger Bands**: campos para `bb_period`, `bb_std`, `exit_mode` (select)
- Enviar parâmetros customizados no objeto `params` para cada estratégia selecionada.

#### [MODIFICAR] [CandlestickChart.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/CandlestickChart.tsx)
- Adicionar suporte para indicadores em painel separado (RSI deve aparecer abaixo do gráfico principal).
- Usar cores do backend para cada indicador.
- Legenda deve mostrar todos os indicadores ativos.

## Verificação
- **Formulário**: Selecionar RSI Reversal e verificar campos de parâmetros (period, oversold, overbought).
- **Formulário**: Selecionar Bollinger Bands e verificar campos (period, std, exit mode).
- **Execução**: Rodar backtest com RSI (14, 30, 70) e verificar que funciona.
- **Gráfico**: Visualizar linha RSI roxa no painel inferior.
- **Gráfico**: Visualizar 3 bandas de Bollinger (azul/amarelo/azul) no gráfico principal.
- **Legenda**: Confirmar que mostra "RSI(14)", "BB Upper(20,2)", "BB Middle(20,2)", "BB Lower(20,2)".
