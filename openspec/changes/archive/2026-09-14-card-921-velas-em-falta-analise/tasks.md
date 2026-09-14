# Tasks — card-921-velas-em-falta-analise

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Clip de médias

- [x] 1.1 — Em `/combo/results` e no gráfico do Monitor, clipar overlays SMA/EMA (e mix `mergeStrategyTransparencySeries`) ao timestamp da última vela realmente carregada; nunca pintar linha à frente.
- [x] 1.2 — Vale para qualquer par cripto nessas telas, não só BTC.

## 2. Série de mercado ao abrir a análise

- [x] 2.1 — Pedido de `/api/market/candles` (full history do par/intervalo do favorito) não congela o snapshot no timeout curto: continua em background e substitui quando chega.
- [x] 2.2 — Se a série de mercado já está em dia, a última vela do gráfico coincide com a última vela de mercado (BTC 1d: não parar em 15/08 com mercado em 12/09).

## 3. Ingestão universo × intervalos

- [x] 3.1 — Catch-up/writer cobre todos os pares de mercado (não só ecrã; teto 40 não corta o aceite) nos intervalos 15m, 1h, 4h e 1d.
- [x] 3.2 — Prioridade ecrã-primeiro; o resto fecha o aceite 6 na mesma.
- [x] 3.3 — Depois de encher, o incremental mantém a série até o presente (pares parados em maio não voltam a ficar meses atrás).
- [x] 3.4 — Picker/API do Monitor abre 15m, 1h, 4h e 1d; análise usa o intervalo do favorito.

## 4. Contrato e evidência

- [x] 4.1 — 1:1 lista↔setas e zoom inicial ~180 do #917 continuam a passar.
- [x] 4.2 — UI alinhada ao proto `frontend/public/prototypes/card-921-velas-em-falta-analise/` (`index.html` análise + `monitor.html`).
- [x] 4.3 — Playwright desktop+mobile nas duas rotas: última vela = última média; BTC 1d em dia; DOGE 1d (ou equivalente parado) chega ao presente após catch-up.
- [x] 4.4 — `openspec verify` desta change.
