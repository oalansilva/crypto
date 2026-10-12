## 1. Timeframes da Descoberta

- [x] 1.1 Expandir `DISCOVERY_SWING_TIMEFRAMES` para `15m`, `1h`, `4h`, `1d`; preflight rejeita 1m/5m/30m no eixo da Descoberta.
- [x] 1.2 Em `DiscoveryPage.tsx`: quatro checkboxes (15 minutos, 1 hora, 4 horas, 1 dia), default `1d`, heading «Compare templates em 4h, 1h, 15m e 1d.», impedimento com os quatro valores, filtro do leaderboard com 1h e 15m. Sem checkbox 1m/5m/30m. Sem filtro 1D. Sem campo de slippage.
- [x] 1.3 Playwright `/combo/discovery` contra o proto: landmarks, quatro timeframes, heading, custo só de leitura.

## 2. Slippage no backtest

- [x] 2.1 Helper único da tabela (1d/4h 0,02%; 1h 0,03%; 15m 0,05%) por lado, somado à taxa 0,075%; compra `preço × (1+slip)`, venda `preço × (1−slip)`.
- [x] 2.2 Ligar o helper em Combo, Descoberta, lote e revalidação de favoritos para os timeframes da tabela. 1m/5m/30m no Combo não herdam a tabela.
- [x] 2.3 Worker da Descoberta persiste `fees_slippage` reais; rótulo `taxa 0,075%` + slippage do timeframe (não 0,1%/0,1%).
- [x] 2.4 Teste: mesma estratégia/período em 1h rende menos por operação na diferença do 0,03% por lado; 15m usa 0,05%; 1d/4h usam 0,02%.

## 3. Templates e VWAP

- [x] 3.1 Criar pelo editor existente (sem `lab_`) os 3 templates: Canal Donchian + volume; Squeeze de Bollinger; Pullback média longa + RSI + ADX. Aparecem no catálogo da Descoberta. Não fixam timeframe.
- [x] 3.2 Expor VWAP do dia (reset 00h UTC) e VWAP móvel de N candles (N otimizável) no editor; ambos usáveis em entrada/saída.
- [x] 3.3 Backtest sem erro: cada template novo em 4h, 1h e 15m (ex. BTC/USDT); um template já oferecido em 1h e 15m; VWAP do dia em 15m/1h/4h; VWAP móvel também em 1d.

## 4. Favoritos e fecho

- [x] 4.1 Revalidação normal de favoritos passa a usar a tabela; não disparar recálculo imediato de todos.
- [x] 4.2 Selo `evaluate_discovery_go_nogo`, elegibilidade 30/90% e Promover à mão intactos. Sem veto Combo. Sem promoção automática.
- [x] 4.3 Skills do projeto (`.cursor/skills`, `.agents/skills`) quando couber. Gate de UI: Design → Aprovação de Design → Pronto para Dev (não aplicar antes).
