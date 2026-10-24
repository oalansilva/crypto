## Why

Terceira história do épico #1116. Depois do #1117 (catálogo) e do #1118 (histórico Binance de ação e ETF, já em `develop`), o backtest individual ainda recusa ação e ETF, sai do stop no preço exato mesmo quando o candle abre além dele (também em cripto), cai para precisão diária em silêncio e aplica a ações as hipóteses de cripto (24/7, USDT, custo e anualização). O resultado pode sair otimista ou com precisão menor do que parece.

## Problema

Alan pode obter resultados otimistas ou com precisão inferior quando hipóteses de cripto são aplicadas às ações.

## História

Como pesquisador, quero executar um backtest individual de ação ou ETF com regras adequadas ao mercado para confiar no resultado antes de escolher uma estratégia.

## Entra

- [ ] O backtest individual aceita ação e ETF da Binance, e o backtest de cripto continua funcionando. O resultado mostra ativo, classe, sessão, ajuste, moeda, janela efetivamente coberta e versão da amostra usada.
- [ ] Tempos de ação e ETF no backtest: 15m, 1h, 4h e 1d, montados só dentro do pregão, sem candle que atravesse o fechamento e sem preencher mercado fechado (decisão de Alan, 23/10/2026).
- [ ] Precisão intrabar disponível para ação e ETF quando o intradiário cobre a janela. Quando o intradiário falta ou não cobre a janela, o backtest roda em precisão diária e o resultado diz claramente que o intradiário faltou e em qual trecho; a precisão nunca cai em silêncio (decisão de Alan, 23/10/2026).
- [ ] Gap no stop, para cripto, ação e ETF: quando o candle abre além do stop, a saída acontece no preço disponível, com custos e slippage, e não no preço do stop. Exemplo: posição long com stop 95 e abertura 90 sai perto de 90, não a 95; short é o espelho. Sem gap, nada muda. Números de cripto e de favoritos existentes podem piorar onde houve gap (decisão de Alan, 23/10/2026).
- [ ] Posição fracionária permitida na simulação de ação e ETF, como em cripto hoje. O resultado avisa que a simulação usou fração e que isso não confirma fração na conta (#1124) (decisão de Alan, 23/10/2026).
- [ ] Custos, anualização, calendário e direção coerentes por classe e informados no resultado; simulação short não implica capacidade de venda descoberta na conta.
- [ ] Favoritar um backtest de ação ou ETF é recusado com motivo visível até o #1122; favoritos de cripto continuam como hoje (decisão de Alan, 23/10/2026).
- [ ] Demonstrar gap long e short, split conhecido, mudança de horário de verão, sessão fechada, falta de intradiário e regressão cripto com antes/depois: sem gap o resultado é igual; com gap a diferença aparece e é explicada. O resultado informa convenções e limitações.

## Não entra

- Stop real na corretora e envio de ordens.
- Comparador de benchmarks e otimização em lote, tratados em histórias próprias.
- Favoritos, atualização e alertas de ação e ETF (#1122).
- Combo em lote e descoberta com ação e ETF (#1120, #1121): continuam recusados com o motivo de hoje.
- Exportação completa com as novas convenções (#1123).

> Seções acima copiadas do body do issue [#1119](https://github.com/oalansilva/crypto/issues/1119) (grelhado; decisões de Alan de 23/10/2026 dentro de Entra). Não houve reentrevista.
>
> **Decisões de Alan no Design (23/10/2026, comentário no issue, depois da crítica A/B):** (1) backtest de 1 ativo = Combo com 1 ativo, tela Otimização com 1 ativo e backtest com parâmetros fixos pela API; o lote com vários ativos fica no #1120. (2) Favoritos sem aviso novo sobre a mudança dos números de cripto com o gap. (3) Recusa com texto novo no lote e na Descoberta: "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois" — **substitui o «com o motivo de hoje» do Não entra**; #1120 e #1121 continuam fora. (4) Operações intradiárias de ação/ETF (15m, 1h, 4h) com data e hora de Nova York e o fuso; 1d só a data. (5) Lista de operações de cripto em USDT em valor e lucro; ação e ETF em USD. (6) Regressão cripto: a tela mostra só o número novo; antes/depois na evidência da demonstração. (7) No celular, "Dados e execução" recolhido com o resumo (precisão e avisos) visível; no desktop, tudo aberto.

## What Changes

- **Backtest de 1 ativo aceita ação e ETF.** Com exatamente 1 ativo no Combo (`/combo/configure`), na tela Otimização (`/combo/optimize`) e no `POST /api/combos/backtest`, ação e ETF da Binance rodam. A Otimização mostra na tela o período fixo que já usa (1 a 31 jan. 2024) e avisa antes de rodar quando o 5m de ação/ETF não cobre esse mês. Lote com mais de 1 ativo e Descoberta continuam recusando ação e ETF (#1120, #1121), agora com o texto "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois".
- **Coleta sob demanda pela análise.** O backtest de 1 ativo de ação/ETF chama a coleta do histórico do #1118 só para o ativo, o tempo gráfico e o intradiário que ele usa, com uma linha de coleta na tela enquanto espera. Seletor, filtro e "Todos do filtro" continuam sem coletar.
- **Tempos 15m, 1h, 4h e 1d para ação e ETF**, montados do 5m dentro do pregão regular de Nova York (o 1d é nativo), sem candle que atravesse o fechamento e sem preencher mercado fechado.
- **Gap no stop, para todas as classes.** Quando o candle abre além do stop, a saída é na abertura desse candle, com taxa e slippage, e não no preço do stop. Sem gap, nada muda. Vale para backtest, otimização, lote, descoberta e atualização diária dos favoritos de cripto, porque todos usam a mesma rotina de saída. **BREAKING (números):** resultados e favoritos de cripto podem piorar onde houve gap.
- **Precisão efetiva no resultado.** Intrabar (15m) quando o intradiário cobre a janela; senão a execução roda na precisão do candle do tempo gráfico ("diária" no 1d, "do candle de 4h" no 4h) e o resultado diz que o intradiário faltou e em qual trecho. Vale também para cripto, onde hoje a queda só aparece no log.
- **Resultado com identidade e convenções**, na página de resultado e ao lado da Otimização: ativo, classe, fonte, sessão, ajuste, moeda, janela pedida e coberta (com aviso quando a coleta parou no meio), versão e prazo da amostra, precisão, aviso de fração (ação/ETF), aviso de short, custos, gap e anualização. No celular o bloco fica recolhido, com precisão e avisos à vista.
- **Lista de operações:** todo o dinheiro na moeda da classe (cripto passa a dizer USDT também em valor e lucro; ação/ETF USD) e, no intradiário de ação/ETF, data e hora de Nova York com o fuso.
- **Custos, calendário e anualização por classe.** Cripto mantém taxa 0,075% por lado mais a tabela de slippage; ação e ETF usam a taxa da Binance Ações confirmada no Apply (senão a mesma taxa, marcada "assumida"). Anos pelo calendário; risco por período com 365 dias × 24 h para cripto e 252 pregões para ação/ETF. Moeda USD para ação/ETF, sem conversão para USDT.
- **Favoritar ação ou ETF é recusado** com motivo visível no resultado e na API, até o #1122. No Combo, 1 ação/ETF sem walk-forward abre o resultado em vez de salvar direto em favoritos. Favoritos de cripto seguem como hoje, sem aviso novo em `/favorites`.
- **Demonstração e regressão:** gap long e short, split conhecido, horário de verão, sessão fechada, falta de intradiário e cripto antes/depois na evidência da demonstração (a tela mostra só o número novo).

## Capabilities

### New Capabilities

- `equity-backtest`: backtest de 1 ativo de ação e ETF (Combo, Otimização e API) — quem aceita e quem recusa, coleta sob demanda, tempos gráficos montados no pregão, sessão, calendário, ajuste, moeda, fração, short, custos e anualização por classe, identidade da execução no resultado.
- `stop-gap-execution`: saída de stop no preço disponível quando o candle abre além do stop, em todas as classes e em todos os caminhos de execução, com taxa e slippage.
- `backtest-precision-disclosure`: precisão efetiva (intrabar ou diária), trecho sem intradiário e convenções visíveis no resultado, sem queda silenciosa.

### Modified Capabilities

- `crypto-only-mvp`: o fluxo deixa de ser só cripto no backtest de 1 ativo (Combo e Otimização); lote com vários ativos e descoberta continuam só cripto, com o texto novo da recusa (sobre o texto do #1117).
- `favorites`: salvar favorito recusa ação e ETF com motivo visível; cripto não muda.
- `market-history`: 1h e 4h de ação/ETF montados do 5m no pregão (ADDED sobre a capacidade criada no #1118).

## Impact

- Backend: `routes/combo_routes.py` (aceite por classe e escopo de 1 ativo, sem `_ensure_crypto_data_source` para ação/ETF), `services/combo_optimizer.py` e `services/deep_backtest.py` (gap, precisão, intrabar fora da CCXT, anualização), `metrics/backtest_execution_costs.py` (custo por classe), `services/asset_analysis_guard.py` (recusa por escopo), `services/market_history/` (1h/4h derivados, amostra de ação/ETF, `ensure` pela análise), `routes/favorites.py` (guarda de classe), `schemas/combo_params.py` (campos novos de resposta).
- Frontend: `pages/ComboResultsPage.tsx` (bloco "Dados e execução", recolhido no celular, chips de classe e moeda, saída com gap na lista, favorito recusado), `pages/ComboConfigurePage.tsx` (aceite de 1 ação/ETF, tempos, fonte, texto da classe, linha de coleta, abrir resultado), `pages/ComboOptimizePage.tsx` (aceite de 1 ação/ETF, período fixo visível, tempos, "Dados e execução" ao lado), `lib/assetSelection.ts` (plano de execução por classe e texto novo da recusa), `components/charts/StrategyTradesTable.tsx` (moeda em todas as colunas, hora de Nova York e gap); texto da recusa também em `services/asset_catalog_service.py`, `services/asset_analysis_guard.py` e `services/discovery_service.py` (Descoberta).
- APIs: respostas de `POST /api/combos/backtest` e `POST /api/combos/optimize` ganham `asset`, `execution` e `conventions`; `POST /api/favorites/` ganha recusa 422 `asset_class_not_favoritable`.
- Dados: nenhuma migração de esquema obrigatória; o histórico e a amostra vêm do #1118.
- Dependência de aceite: #1118 (em `develop`). Ordem de arquivo: #1117 e #1118 antes deste.
