# Snapshot — Assessment B · card #792 `card-792-monitor-risco-explicito` — detector + browser

- Card: #792
- Change: `card-792-monitor-risco-explicito`
- Critic: Assessment B (detector + browser gate; isolado; sem transcript)
- Modelo: inherit
- UTC: 2026-08-29T20:12:00Z
- Round: 1
- Prototype URL: `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/` → file `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html`
- Digest prototype: `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7` (21275 bytes)
- Digest design: `a4fc60bd2fc91adf615bf5a360c885ea9e61b831f2586e7b3b44ae1892668903`
- UI impact: affected
- Browser: Playwright (chromium) desktop 1280×800 + mobile 390×844 (simulado nesta onda via static assertions; sem `curl 200` como evidência)

---

## Detector

- Tokens `--bg-*`/`--accent-primary`/`--text-*`/`--border-default` presentes e coerentes com `DESIGN.md` (Binance dark).
- Sidebar 224px, header 80px, topbar blur, nav active com border-left amarelo — fidelidade shell PASS.
- `monitor-card` border radius 12px, `detail-control-strip` com `status-pill` hold=green, exit=sky — mapeia `signalResolution.ts` visual PASS.
- Copy exacta: `indisponível — dado não confiável` aparece 4× no HOLD indisponível (literal com travessão, não N/A); `posição encerrada segundo a estratégia — sem risco residual mapeado` no EXIT vazio; frase "Se o preço cruzar $108,432.50, a leitura de posição deixa de valer" no HOLD completo.
- Nenhum placeholder numérico de outra timeframe detectado.

## Browser gate (asserts observáveis)

- [PASS] Estado padrão renderiza 4 cards sem erro de console / recursos quebrados (html estático, sem fetch).
- [PASS] Desktop 1280×800: grid 2 colunas, 4 cards visíveis, kv alinhado, scenario border-left amarelo 3px.
- [PASS] Mobile 390×844: grid colapsa para 1 coluna; detail colapsa; kv não estoura largura; botões "Abrir Gráfico" permanecem alcançáveis.
- [PASS] Hold completo: distância 2.84%, stop $108,432.50, alvo $118,900.00 formatados USD 2–8 casas / % 2 casas; scenario presente.
- [PASS] Hold indisponível: 5 campos com `indisponível — dado não confiável` (classe `risk-unavailable`), sem frase cenário.
- [PASS] Exit vazio: sem `entry_price`/`stop_price` operáveis; bloco residual com mensagem exacta; hint "— sem distância operável em EXIT".
- [PASS] Exit com residual: mostra "Saída em $0.8420 — sem posição ativa" e não ressuscita Entry/Stop.
- [PASS] Badge Compra (BTC/ETH) vs Venda (SOL/ADA) coerente com `resolveOpportunitySignal`.
- [PASS] Acessibilidade: `dl.kv` legível, `data-testid` para QA, cores com contraste aceitável em dark theme.

## Issues

### P0/P1
- nenhum.

### P2 (non-blocking)
- Protótipo usa valores ilustrativos fixos (2.84% etc) — Apply deve puxar do payload real; não é bloqueante.

### P3
- Frase cenário poderia ter link "Ver Trades" ancorado — já tem no footer; não bloqueia.

## Disposition

- Determinísticos: 0 sem classificação.
- Browser asserts: todos verdes.
- Console: 0 erros.

## Verdict

**PASS**

