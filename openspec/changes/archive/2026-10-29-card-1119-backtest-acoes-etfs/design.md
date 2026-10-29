UI impact: affected
live_route: /combo/results
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1119](https://github.com/oalansilva/crypto/issues/1119), terceira história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado (fronteira fechada), com as 5 decisões de Alan de 23/10/2026 dentro de Entra, mais as 7 decisões de Alan no Design (comentário «Decisões de Alan no Design (23/10/2026)» no issue, depois da crítica A/B), aplicadas neste rework r1. Não houve reentrevista. O *como* abaixo foi conferido em `develop` @ 5fe666fe (pós-#1118).

Estado atual, conferido no código:

- **Quem é o "backtest individual" na tela.** O Combo (`/combo/configure`) com 1 ativo chama `POST /api/combos/optimize` ("1 ativo: otimiza o primeiro"), recebe os melhores parâmetros e o backtest com eles, e então salva direto em favoritos e abre `/favorites`; com walk-forward abre `/combo/results` com "Salvar nos Favoritos". `POST /api/combos/backtest` (parâmetros fixos) existe na API, mas nenhuma tela o chama. A tela Otimização (`/combo/optimize`, só admin) também chama `POST /api/combos/optimize` com 1 ativo e o lote (`/backtest/batch`) com N, sempre com `start_date: "2024-01-01"` e `end_date: "2024-01-31"` fixos no código (`ComboOptimizePage.tsx`, "TODO: Date picker") e sem mostrar o período na tela; não manda `deep_backtest`, então vale o padrão `true` do schema. A lista de tempos dela tem 1m, 5m, 15m, 30m, 1h, 4h e 1d. O resultado aparece ao lado ("Optimization Complete": retorno, acerto, Sharpe, trades, parâmetros e estágios), sem dizer ativo, janela nem precisão.
- **Recusa por classe.** `combo_routes.py:53-74`: `_refuse_assets` (#1117, `asset_class_not_supported`) e `_ensure_crypto_data_source`, que só aceita CCXT. `asset_analysis_guard.refusal_for_symbols` recusa ação/ETF em todos os caminhos.
- **Stop no preço exato.** `combo_optimizer.py:217-239` (legado) e `:296-315` (rápido) testam `low ≤ stop` (long) ou `high ≥ stop` (short) e saem em `exact_stop_price`, mesmo quando o candle abre além dele. `deep_backtest.py:146` e `:316` fazem o mesmo no 15m. Vale hoje para cripto.
- **Queda silenciosa de precisão.** `combo_optimizer.py:376-475` (`extract_trades_with_mode`) cai para `fast_1d` sem 15m, com cobertura curta ou com erro, e só registra no log; `execution_mode` volta na resposta, mas `ComboResultsPage.tsx` não o mostra. `combo_optimizer.py:2225` desliga o intrabar para qualquer fonte que não seja CCXT.
- **Custos e anos.** `backtest_execution_costs.py`: taxa 0,075% por lado e slippage 0,02% (1d/4h), 0,03% (1h), 0,05% (15m). `combo_optimizer.py:2902` conta os anos pelo calendário ÷ 365; `risk_adjusted.py` usa `periods_per_year = 365`. `POST /api/combos/backtest` hoje não passa slippage. `backtest_service.py:341` (custo padrão 0,001) é o motor do otimizador sequencial, não do Combo.
- **Moeda e hora.** A lista de operações (`StrategyTradesTable.tsx`) escreve "USDT" fixo no preço e "USD" fixo em valor, lucro, máximos e acumulado; a captura viva de NVDA mostra "199.10 USDT". A coluna "Data e hora" mostra só a data (formatador UTC do incumbente).
- **Texto da recusa por classe.** `EQUITY_REASON` (`assetSelection.ts:119`) e `blockedNotice` no front; `EQUITY_UNSUPPORTED_MESSAGE` (`asset_catalog_service.py:66`), `catalog_symbol_reason`, `DISCOVERY_EQUITY_REASON` (`asset_analysis_guard.py:152`) e `discovery_service.py:477` no servidor: todos dizem "análise ainda não disponível para ações e ETFs".
- **Favoritos.** `routes/favorites.py` (`POST /`) não olha a classe; o refresh diário (`favorite_backtest_refresh_service.py`) prepara candles e 15m pelo provedor e roda `ComboOptimizer.run_optimization`.
- **Histórico (#1118).** `services/market_history/`: série por ativo, fonte, sessão, ajuste e timeframe; ação/ETF com 1d e 5m nativos, 15m montado do 5m (`nyse_calendar.derive_15m`), só pregão regular, calendário XNYS com horário de verão; `HistoryService.ensure` coleta sob demanda com lock e limite; amostra congelada por execução (`ExecutionSample`, `data_provenance`), hoje só para cripto (`_begin_sample` exige `ccxt` e `/` no símbolo). `equity_provider.DEFERRED_TIMEFRAMES = {"1h", "4h"}` espera este card.

**Audience:** Alan, que roda uma estratégia num ativo e precisa confiar no número antes de escolher.
**Outcome:** backtest de 1 ação ou ETF com sessão, gap, precisão, custo, moeda e anualização corretos e declarados; cripto com o mesmo gap e a precisão visível.
**Direction:** clone+delta Operate da página viva de resultado, do Combo e da Otimização. Tokens do produto, sem mundo visual novo.
**Scope:** backtest de 1 ativo (Combo com 1 ativo, Otimização com 1 ativo e `POST /api/combos/backtest`), a página de resultado e o resultado ao lado da Otimização; Combo e Otimização só no que muda para ação/ETF; texto da recusa no lote e na Descoberta. Fora: lote com vários ativos, Descoberta com ação/ETF, favoritos de ação/ETF, exportação, ordens.

Regiões clonadas da página viva, só estas (capturadas em `https://dev.criptofarol.com.br` com a API simulada, a 1440 e a 390 px, marcadas com `COPIED:start`/`COPIED:end`):

- `index.html` (canônico, `/combo/results`, NVDA 1d long): fundo; AppNav desktop; AppNav móvel; conteúdo vivo (Voltar, resumo com chips, título, descrição e métricas, Regras da estratégia, gráfico — canvas trocado pela captura PNG da própria página, desktop e móvel —, Detalhes técnicos, aviso educacional).
- `etf-short.html` (extra, `/combo/results`, SPY 1h short) e `cripto.html` (extra, `/combo/results`, BTC/USDT 4h, regressão cripto): as mesmas regiões.
- `configure.html` (extra, `/combo/configure`, NVDA selecionado, busca AAPL): fundo; AppNav desktop e móvel; conteúdo vivo (Template Information, Configuration com o seletor do #1117/#1118, Timeframe, Período, Direction, Deep Backtest, walk-forward, dica de período, Parameter Optimization Ranges, Otimizar).
- `optimize.html` (extra, `/combo/optimize`, NVDA selecionado, 1d): fundo; AppNav desktop e móvel; conteúdo vivo (Configuration com template, seletor, Timeframe, Parameter Ranges, Run Optimization) e o painel de resultado vivo da mesma página, capturado depois de rodar ("Optimization Complete", parâmetros, estágios). O painel vivo foi capturado com BTC/USDT porque a página de hoje recusa NVDA; ele não nomeia o ativo, então nada nele muda de classe.
- `live.css`: o CSS vivo inteiro (`index-N9hYlmCr.css` do DEV), sem poda.

O delta fica só nos blocos `DELTA:start`/`DELTA:end`: chip de classe, favoritar recusado, bloco "Dados e execução" (no resultado e ao lado da Otimização), lista de operações (moeda da classe, hora de Nova York no intradiário de ação/ETF e saída com gap), as frases e opções do Combo e da Otimização, e o painel "Demonstração" no fim de cada página.

## Goals / Non-Goals

**Goals:**

- Backtest de 1 ação ou ETF da Binance, com a cripto como hoje.
- Gap no stop em todas as classes e caminhos, com custo e slippage, explicado no resultado.
- Precisão efetiva sempre visível, com o trecho sem intradiário.
- 15m, 1h, 4h e 1d de ação/ETF no pregão regular.
- Custo, calendário, anualização, moeda, fração e short coerentes por classe e escritos no resultado.
- Identidade da execução (classe, sessão, ajuste, moeda, janela, amostra) até a tela.
- Recusa visível de favoritar ação/ETF.
- Demonstração e regressão cripto: a tela mostra só o número novo; o antes/depois fica na evidência da demonstração.

**Non-Goals:**

- Stop real na corretora, ordens, capacidade da conta (fração, venda descoberta) (#1124).
- Lote com mais de 1 ativo (Combo e Otimização) e Descoberta com ação/ETF (#1120, #1121): continuam recusando, agora com o texto novo da decisão 3 (decisão de Alan no Design, que substitui o «motivo de hoje» do Não entra).
- Seletor de período na Otimização: ela continua com as datas fixas de jan. 2024, agora visíveis (decisão 2).
- Favoritos, refresh e alertas de ação/ETF (#1122); benchmark e exportação (#1123).
- Pré e pós-mercado; 1m e 5m de ação/ETF como tempo gráfico.
- Mudar o otimizador sequencial (`backtest_service.py`) ou o seu custo de 0,001.

## Decisions

1. **Página primária = `/combo/results`; extras `/combo/configure`, `/combo/optimize`, ETF short e cripto.** Quase todo o delta visível (identidade, precisão, convenções, gap, moeda, favorito recusado) mora no resultado, que está no catálogo do gate (`.combo-page`, "Lista de operações", "Análise da estratégia"). O Combo e a Otimização têm delta próprio (aceite de 1 ação, tempos, fonte, textos; na Otimização também o período fixo visível e o bloco "Dados e execução" ao lado) e ganham clone extra. `/combo/optimize` não está no catálogo do gate: é extra, sem gate próprio. SPY short e BTC/USDT são a mesma rota com outro estado; ficam em arquivos próprios porque o gap short, o 1h montado e a regressão cripto não cabem num único resultado verdadeiro. Nenhum arquivo é painel de estados. Alternativa rejeitada: `/combo/select` (lista de templates, sem delta).

2. **Backtest de 1 ativo = Combo com 1 ativo, Otimização com 1 ativo e `POST /api/combos/backtest`** (decisão 1 de Alan no Design, 23/10/2026). Combo e Otimização mandam `run_scope: "single"` no `POST /api/combos/optimize` quando sobra exatamente 1 ativo para rodar; o servidor aceita ação/ETF só com `run_scope == "single"` e exatamente um símbolo, ou em `POST /api/combos/backtest`. `/backtest/batch` (lote com N ativos, em qualquer tela) e a Descoberta continuam recusando ação/ETF (#1120, #1121). Ativo marcado pela Binance segue a recusa do #1117.
   - **Otimização, o que muda na tela.** Com 1 ação/ETF ela roda e mostra o resultado ao lado, como já faz com 1 par cripto, sem salvar em favoritos (o caminho de 1 ativo dela nunca salvou). Nota de classe nova; texto sob demanda "coletado ao rodar o backtest de 1 ativo"; 1m, 5m e 30m ficam "(só cripto)" e indisponíveis com ação/ETF (voltam na seleção mista, onde só a cripto roda); dica de tempo gráfico de ação; texto antes de rodar "1 ação (NVDA): otimiza em 1d, de 1 a 31 jan. 2024, e mostra o resultado ao lado."; linha de coleta ao rodar; e o bloco "Dados e execução" (decisão 16) entre "Optimization Complete" e "Optimization Stages", com o mesmo comportamento recolhido no celular (decisão 19). Os rótulos vivos em inglês ("Run Optimization", "Optimization Complete") ficam como estão.
   - **Datas fixas de jan. 2024.** Ficam como hoje para todas as classes (seletor de período é escopo do #1120), mas passam a aparecer na tela, abaixo do Timeframe: "Período: 1 a 31 jan. 2024, fixo nesta tela." Vale também para cripto, porque é o que já roda. Para ação/ETF o 1d cobre jan. 2024 (NVDA 1d desde 2014); 15m, 1h e 4h dependem do 5m da Binance, que no #1118 começa em mai. 2026. Por isso, quando a cobertura do catálogo (#1118) mostra que o 5m não cobre jan. 2024, a tela avisa **antes** de rodar ("Nada será executado: o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela. Use 1d aqui ou o Combo, que tem período.") e "Run Optimization" não roda (aviso `role=status`). Ativo sob demanda, sem cobertura conhecida, roda a coleta e, se nada cobrir a janela, recebe o 422 `history_unavailable` da decisão 4 como alerta. A Otimização pede intrabar (padrão do schema), então em jan. 2024 a ação roda em precisão diária com o trecho, sempre declarado.
   - Alternativa rejeitada: trocar a janela fixa só para ação/ETF (por exemplo "últimos 30 dias"), porque a mesma tela rodaria períodos diferentes por classe sem o usuário escolher.

3. **Recusa com texto novo** (decisão 3 de Alan no Design, 23/10/2026; substitui o «com o motivo de hoje» do Não entra). Lote do Combo, lote e seleção mista da Otimização e Descoberta continuam recusando ação/ETF com o mesmo código `asset_class_not_supported`, mas o porquê passa a ser "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois". O texto troca nas fontes listadas no Context (`EQUITY_REASON`, `blockedNotice`, `EQUITY_UNSUPPORTED_MESSAGE`, `catalog_symbol_reason`, `DISCOVERY_EQUITY_REASON`, `discovery_service`). Exemplos: seleção mista "Roda 1 par cripto (BTC/USDT): … Fora: NVDA (Ação) — ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois."; só ações/ETFs "Nada será executado nem salvo: NVDA, SPY — ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois." (na Otimização, sem "nem salvo"); alerta ao rodar com o título "Ação e ETF rodam só com 1 ativo por enquanto". Na Descoberta só o texto muda: aviso, lugar e comportamento ficam os do #1117, por isso não há clone dela. O #1120 e o #1121 continuam fora.

4. **Quem dispara a coleta sob demanda.** A partir deste card, o backtest de 1 ativo de ação/ETF (Combo, Otimização ou API) chama `HistoryService.ensure` (decisão 5 do #1118) para: a série do tempo gráfico (1d nativo, ou o 5m quando o tempo é 15m/1h/4h) e, com intrabar ligado, o 5m que monta o 15m, só na janela pedida. A chamada é síncrona dentro do pedido. Coleta em andamento da mesma série (lock do #1118): espera até 30 s e segue com o que já está gravado. Falha com parte gravada: roda no trecho coberto e o resultado diz isso (nota "Janela coberta menor que a pedida" da decisão 16). Ao rodar, Combo e Otimização mostram uma linha `role=status` de coleta enquanto esperam. Falha sem nada gravado: 422 `history_unavailable` com o motivo ("Histórico de NVDA indisponível agora: limite de requisições da Binance. Tente de novo em alguns minutos."), sem resultado vazio. Seletor, filtro, busca, "Todos do filtro" e análises recusadas continuam sem coletar. Custo: NVDA 1d completo = 3 páginas (≈1,5 s); 1 ano de 5m = 20 páginas (≈10 s), medidas do #1118.

5. **Tempos de ação/ETF: 1d nativo; 15m, 1h e 4h montados do 5m.** Generaliza `derive_15m` para `derive_blocks(minutes)`: blocos de 3 (15m), 12 (1h) e 48 (4h) candles de 5m, ancorados às 09:30 de Nova York, cortados no fechamento (16:00; 13:00 em meio-pregão). Assim o último 1h é 15:30–16:00 e o 4h é 09:30–13:30 e 13:30–16:00 (09:30–13:00 em meio-pregão). Âncora em horário de Nova York e gravação em UTC: a virada do horário de verão não cria buraco nem candle a mais. Bloco com 5m faltando não vira candle e aparece como lacuna herdada do 5m (regra do #1118); bloco curto do fechamento não é incompleto. 1h e 4h não são gravados como série nativa; a versão é (versão do 5m, versão da regra); a cobertura lista "montado do 5m". 1m e 5m ficam fora para ação/ETF (o 5m é a matéria-prima, não tempo de estratégia). Alternativa rejeitada: o 1H/4H nativo da Binance, porque a sessão observada é `ETH` (com pré/pós) e a âncora das 09:30 não foi comprovada; duas fontes para o mesmo tempo misturariam séries.

6. **Gap no stop, uma regra só.** Na rotina compartilhada de saída (`_legacy_extract…`, `_fast_extract…`, `_legacy/_fast/_compiled_simulate_execution_with_15m`), por candle checado: long — se `open ≤ stop`, sai em `open`; senão, se `low ≤ stop`, sai em `stop`. Short — se `open ≥ stop`, sai em `open`; senão, se `high ≥ stop`, sai em `stop`. O preço de saída passa por `long/short_trade_profit_frac` com a mesma taxa e o mesmo slippage de qualquer saída. "Retomada" = primeiro candle depois de mercado fechado (noite, fim de semana, feriado), de parada de negociação ou de falta de dados: a regra vale nesse candle, cuja abertura é o preço disponível. No candle de entrada o stop não é checado (a entrada é na abertura, como hoje). O trade com gap ganha `exit_reason = "stop_loss_gap"`, `signal_type = "Stop com gap"`, `stop_price` e `gap_pct`. Sem gap o código percorre o mesmo caminho e devolve o mesmo número, bit a bit. Como a rotina é compartilhada, Descoberta, lote, otimização e refresh dos favoritos de cripto mudam junto (decisão de Alan: números podem piorar onde houve gap). Interruptor `STOP_GAP_EXIT` (padrão ligado) só para rollback.

7. **Precisão efetiva, sem queda silenciosa.** `extract_trades_with_mode` devolve, além do modo, `execution = {precision_requested, precision_effective, intraday_missing: [{from, to}], intraday_reason, gap_stops}`. Regra de cobertura: o 15m cobre a janela quando começa no primeiro pregão (ou dia, em cripto) e termina no último, sem pregão inteiro sem 15m. Senão a execução inteira roda na precisão do candle do tempo gráfico, como diz o card ("precisão diária"). A tela chama de "Precisão diária" só no 1d e de "Precisão do candle de 4h" (ou 1h, 15m) nos outros, no título da faixa e no fato "Precisão" ("Diária" / "Candle de 4h"), para não dizer "diária" num backtest de 4h; "trecho" = os intervalos de pregões da janela sem 15m, juntados. Erro ao ler o intradiário entra como `intraday_reason = "read_error"`. Intrabar desligado = `precision_requested = "daily"`, sem aviso. Vale para cripto também: o aviso sai do log e vai para a tela. Alternativa rejeitada: precisão mista (intrabar onde houver, diária no resto), porque o card pede precisão diária com aviso e trecho e um número só com duas precisões é mais difícil de ler.

8. **Intrabar fora da CCXT.** `combo_optimizer.py:2225` deixa de desligar o intrabar por fonte: com o caminho unificado do #1118, ação/ETF leem o 15m montado do 5m pelo `HistoryService`. `_begin_sample`/`_freeze_intraday` passam a congelar também séries `binance_equity` (hoje exigem `ccxt` e `/`), para que toda tentativa leia a mesma amostra.

9. **Custos por classe.** Tabela por classe em `backtest_execution_costs`: cripto 0,075% por lado (como hoje); ação/ETF com a taxa da Binance Ações confirmada no Apply (documentação oficial de Stocks Trading ou `commission` da conta de teste, sem ordem real). Sem confirmação: 0,075% por lado com `fee_confirmed = false` e a palavra "assumida" no resultado. Slippage por tempo gráfico igual para todas as classes (spec `backtest-slippage-by-timeframe`). `POST /api/combos/backtest` passa a usar a mesma tabela (hoje não passa slippage).

10. **Anualização.** Anos = dias corridos ÷ 365 para todas as classes, porque CAGR e Calmar medem tempo real, que é o mesmo em qualquer mercado. Risco por período (Sortino e afins): `periods_per_year` = 365 × candles por dia em cripto; 252 × candles por pregão em ação/ETF (1d = 1, 4h = 2, 1h = 7, 15m = 26). Alternativa rejeitada: 252 também nos anos, que encurtaria a janela de ação e inflaria o retorno anual.

11. **Sessão, horário de verão e split.** Vêm do #1118 (calendário XNYS, pregão regular, série ajustada por padrão). Posição carregada de um dia para outro é checada no primeiro candle do pregão seguinte, com a regra do gap. Entrada, saída e stop usam a série ajustada; o resultado avisa que o preço pode diferir do negociado na época. O rótulo diz o ajuste verificado no #1118 ("ajustado por split" ou "ajustado por split e dividendo").

12. **Identidade até o resultado.** `ComboBacktestResponse` e `ComboOptimizationResponse` ganham `asset = {symbol, asset_id, asset_class, name, currency}`, `data_provenance` (já existe para cripto; passa a valer para ação/ETF), `execution` (decisão 7) e `conventions = {fee, fee_confirmed, slippage, periods_per_year, calendar, fraction, short}`. O Combo passa esses campos no `state` de `/combo/results`. Resultado antigo sem `execution` (favorito ainda não atualizado) não mostra o bloco; depois do próximo refresh diário o favorito de cripto passa a ter os campos.

13. **Moeda** (decisão 5 de Alan no Design). `asset.currency`: USD para ação/ETF (Binance Ações cota em dólar), a moeda de cotação para cripto (USDT). `StrategyTradesTable` recebe `currency` e o usa em todas as colunas de dinheiro (preço, valor da posição, lucro/prejuízo, máximos favorável e adverso, acumulado), na tabela e no cartão: a lista de cripto passa a dizer USDT em valor e lucro (hoje diz USD), a de ação/ETF diz USD em tudo. Sem conversão USD↔USDT.

14. **Fração e short.** A conta da simulação não muda (capital inteiro por operação, como em cripto). O resultado de ação/ETF avisa a fração; qualquer short avisa que é só simulação. Nada consulta a conta (#1124).

15. **Favoritar ação/ETF recusado.** `POST /api/favorites/` resolve a classe pelo catálogo (`check_assets`) e responde 422 `asset_class_not_favoritable` com a mensagem do spec `favorites`. No Combo, 1 ação/ETF sem walk-forward abre `/combo/results` com `isOptimization: true` em vez de salvar; a checagem `/favorites/exists` não roda para ação/ETF. A Otimização com 1 ativo mostra o resultado ao lado e não salva, como hoje. `/favorites` não ganha aviso novo sobre a mudança dos números de cripto com a regra do gap (decisão 2 de Alan no Design): o resultado explica a regra e o número anterior fica no histórico de runs. No resultado, "Salvar nos Favoritos" fica visível com `aria-disabled="true"` (continua focável), `aria-describedby` no motivo, motivo escrito ao lado e anunciado num `role=status` ao ativar; o modal não abre. Favoritos de cripto, inclusive refresh, não mudam.

16. **Texto visível (contrato).**
   - Bloco "Dados e execução", depois do resumo (no resultado) ou entre "Optimization Complete" e "Optimization Stages" (na Otimização): linha de proveniência ("Binance Ações · pregão regular de Nova York · ajustado por split · USD"; cripto "Binance Spot · 24/7 · ajuste não se aplica · USDT"); faixa de precisão (âmbar se caiu por falta/erro; azul se intrabar ou escolhida; título pela regra da decisão 7); fatos Ativo, Fonte e sessão, Ajuste e moeda, Tempo gráfico, Janela pedida, Janela coberta, Amostra ("Versão N · guardada até …"; ação/ETF "vale o prazo de 30 dias"; cripto "Ao favoritar, Favoritos guarda a amostra do último refresh"), Precisão; "Convenções desta execução": Gap no stop (com a contagem e o exemplo da execução), Custos, Posição com fração (ação/ETF), Short simulado (short), Calendário, Anualização, Preços ajustados (ação **e** ETF). No celular o bloco fica recolhido (decisão 19).
   - Fato "Tempo gráfico" de ação/ETF: 1d "1d nativo · 1 candle por pregão"; 1h "1h montado do 5m · 09:30, 10:30 … 15:30–16:00; nenhum candle atravessa o fechamento"; 4h "4h montado do 5m · 09:30–13:30 e 13:30–16:00 (meio-pregão: 09:30–13:00); nenhum candle atravessa o fechamento"; 15m "15m montado do 5m · 09:30, 09:45 … 15:45–16:00; nenhum candle atravessa o fechamento". Custos e Anualização acompanham (slippage 0,03% / 0,02% / 0,05%; 252 × 7 / × 2 / × 26).
   - Precisão por falta: "O intradiário de 15m faltou de DD mmm. AAAA a DD mmm. AAAA. Você pediu precisão intrabar; como ele não cobre a janela, o stop foi simulado no candle diário (ou: no candle de 4h) em toda a janela."; na Otimização, "A Otimização pede precisão intrabar; …".
   - Coleta que parou com parte gravada (decisão 4): segunda nota âmbar `role=note`, logo abaixo da faixa de precisão, "Janela coberta menor que a pedida" / "A coleta do 1d de NVDA parou depois de guardar até 2 out. 2026 (limite de requisições da Binance). O backtest rodou no trecho guardado, de 11 nov. 2014 a 2 out. 2026; de 5 a 22 out. 2026 ficou fora. Rode de novo mais tarde para completar."; o fato Janela coberta diz o corte e os Avisos do celular ganham "janela coberta menor que a pedida".
   - Chip de classe ao lado do ativo ("Ação", "ETF", "Cripto").
   - Lista de operações: saída com gap como "Stop com gap" e "stop X · abriu Y"; no cartão móvel, "Stop com gap · stop X, abriu Y"; dinheiro na moeda da classe (decisão 13); hora de Nova York no intradiário de ação/ETF (decisão 18).
   - Combo com 1 ação/ETF: fonte "Binance Ações · pregão regular de Nova York · ajustado por split", na cor `--text-tertiary` (5,6:1 sobre a caixa; o `text-zinc-600` herdado dava 2,16:1); nota de classe "Ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização) e abrem o resultado. Com mais de 1 ativo, ficam fora com aviso; o lote vem depois."; sob demanda "Histórico sob demanda · coletado ao rodar o backtest de 1 ativo" (no Combo e na Otimização; a Descoberta mantém o texto do #1118); 1m e 5m com "(só cripto)", indisponíveis com 1 ação/ETF e disponíveis de novo na seleção mista (lá só a cripto roda); dica "Ação e ETF: 15m, 1h, 4h ou 1d, montados no pregão regular de Nova York, sem candle que atravesse o fechamento."; dica do Deep Backtest; texto antes de rodar "1 ação (NVDA): otimiza e abre o resultado, sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados."; ao rodar, linha `role=status` "Coletando histórico de NVDA para a janela pedida (1h e o 5m do intrabar) antes de otimizar… Na primeira execução de um ativo isso pode levar alguns segundos."; falha de coleta sem nada gravado → alerta "Histórico de NVDA indisponível agora".
   - 5m (ou 1m) com ação, caminho real: o tempo foi escolhido com a cripto na seleção (mista) e a cripto saiu, ficando só a ação. O valor fica em 5m (sem troca silenciosa) e a tela avisa **antes** de rodar: texto antes de rodar em âmbar "Nada será executado: NVDA (Ação) não roda em 5m. Escolha 15m, 1h, 4h ou 1d." e aviso `role=status` "Escolha 15m, 1h, 4h ou 1d"; "Otimizar" não roda; escolher 15m, 1h, 4h ou 1d limpa o aviso.
   - Otimização com 1 ação/ETF: os textos da decisão 2 (nota de classe "… e mostram o resultado ao lado …", período fixo visível, dica de tempo, 1m/5m/30m "(só cripto)", texto antes de rodar, aviso de 5m que não cobre jan. 2024, linha de coleta "Coletando histórico de NVDA (1d de 1 a 31 jan. 2024) antes de otimizar…").
   - Recusa do lote, da seleção mista e da Descoberta: o texto da decisão 3.

17. **Demonstração e regressão.** Testes de unidade da rotina de saída: gap long (stop 95, abre 90 → 90 com custo), gap short (espelho), toque sem gap (igual a hoje), retomada depois do fim de semana, gap no 15m. Calendário: 1h/4h em pregão cheio, meio-pregão (27 nov. 2026, sexta depois de Ação de Graças) e virada do horário de verão (8 mar. e 1 nov. 2026). Split: NVDA 7–10 jun. 2024 sem salto nem stop falso. Sessão fechada: nenhum candle em fim de semana e feriado. Falta de intradiário: NVDA "todo o histórico" com o trecho. Regressão cripto: BTC/USDT 1d e 4h numa amostra fixa, rotina antiga contra nova; trades sem gap idênticos, toda diferença é trade com gap. Por decisão 6 de Alan no Design, a tela mostra só o número novo (com a regra explicada em "Gap no stop"); a tabela antes/depois fica na evidência da demonstração no card (tarefas 2.4 e 8.2), nunca na UI. E2E Playwright das telas com a API simulada, seguindo o protótipo.

18. **Hora de Nova York no intradiário de ação/ETF** (decisão 4 de Alan no Design). Em 15m, 1h e 4h de ação/ETF, a lista de operações mostra data e hora no horário de Nova York, com o fuso indicado: cabeçalho "Data e hora (Nova York)" e, em cada célula, a data do formatador vivo com a hora embaixo ("Aug 27, 2026" / "09:30 EDT"; EST fora do horário de verão); no cartão móvel, "Aug 26, 2026, 10:30 → Aug 27, 2026, 09:30" e "Horário de Nova York (EDT)". Em 1d, só a data, como hoje. Cripto não muda (fora do pedido).

19. **"Dados e execução" recolhido no celular** (decisão 7 de Alan no Design). Abaixo de 768 px: ficam visíveis o título, a proveniência, a faixa de precisão, a nota de coleta parcial (quando houver) e uma linha "Avisos: 1 saída com gap · taxa assumida · posição com fração" (os avisos da execução); os 8 fatos e as convenções abrem com um toque num `<button aria-expanded aria-controls>` "Fatos e convenções desta execução · 8 fatos · 6 convenções" (alvo ≥ 44 px, anel de foco, foco fica no botão, estado anunciado pelo `aria-expanded`; Enter e Espaço alternam). De 768 px para cima tudo fica aberto, sem botão e sem a linha de Avisos. Começa recolhido a cada abertura do resultado (sem memória).

## Risks / Trade-offs

- [O 5m da Binance pode ter pouco passado (o #1118 viu NVDA 5m desde mai. 2026 na amostra)] → 1h, 4h e 15m de ação/ETF ficam curtos e o intrabar quase sempre cai para diário em janelas longas; o resultado mostra janela coberta e trecho. O Apply mede a profundidade do 5m de NVDA e SPY (tarefa 1.2); abaixo de 1 ano, avisa Alan antes de seguir.
- [Taxa da Binance Ações desconhecida] → verificação no Apply; até lá "assumida" na tela.
- [Números de cripto mudam no próximo refresh dos favoritos, sem aviso em `/favorites`] → aceito pelo card e pela decisão 2 de Alan no Design (sem aviso novo); o número anterior fica no histórico de runs; o resultado explica o gap.
- [Servidor aceita ação/ETF em `/optimize` com `run_scope`] → só com 1 símbolo; teste de contrato garante que `/backtest/batch` (lote de Combo e Otimização) e a Descoberta continuam recusando, e que a Otimização com 1 ação roda.
- [Otimização com período fixo de jan. 2024] → para ação/ETF só o 1d tem dados nesse mês (o 5m da Binance começa em mai. 2026 no #1118); 15m, 1h e 4h são recusados antes de rodar com o motivo e o caminho (1d ou Combo). Seletor de período fica para o #1120.
- [Preço ajustado difere do negociado] → aviso no resultado; nenhuma ordem usa esse preço.
- [Rota BAPI sem contrato] → herdado do #1118 (validação, circuito, falha visível).
- [Servidor de protótipos só enxerga worktree novo depois de reiniciado] → `scripts/dev_prototype_server.py` calcula as raízes só na partida (`public_roots` em `main`). Neste card o serviço `criptofarol-dev-prototypes.service` foi reiniciado em 23/10/2026 e a URL pública responde 200 (todos os arquivos, inclusive o `optimize.html` novo, que está na mesma pasta). Fica como risco de processo para os próximos cards: worktree criado depois da partida do serviço dá 404 até o restart (ou até a correção para recalcular as raízes por pedido).
- [Cores do delta] → o rework r1 trocou as 6 cores inventadas do a1 (`rgba(147,197,253,.32/.45)`, `rgba(251,191,36,.42/.08)`, `#474d57` ×2) por tokens: `--ap-info-border`, `--ap-warn-border`, `color-mix(in srgb, var(--accent-warning) 8%, transparent)` (o `rgba(245,158,11,.08)` da Descoberta viva) e `--border-default`; e as herdadas `#fbbf24`/`#93c5fd` por `var(--ap-warn-text)`/`var(--ap-info-text)` do `AssetPicker.css` vivo. Sobra um literal herdado, `#b7bdc6` (11× no `delta.css`), o texto secundário da descrição viva de `ComboResultsPage.tsx`, que não tem token no `DESIGN.md`: o hook o sinaliza, ele não é cor inventada (P3 abaixo). Nenhum achado foi silenciado.

### P3 aceitos (detalhe de Apply)

Da crítica A/B do a1 (23/10/2026), resolvidos no Apply e não reabertos como P0/P1:

- Cores herdadas como literal: no Apply, `#fbbf24`/`#93c5fd` viram `var(--ap-warn-text)`/`var(--ap-info-text)` (como no protótipo r1); `#b7bdc6` não é token do `DESIGN.md` — documentar ou trocar por `--text-tertiary` é decisão fora do card (B-P3-2).
- O detector CLI para em `frontend/package.json` e não aplica o `DESIGN.md` abaixo de `frontend/`; a validação cita o modo hook, rodado da raiz (B-P3-3).
- Reset `* { margin: 0; padding: 0 }` sem `@layer` em `index.css:649` zera utilitários do Tailwind; o Apply escreve "Dados e execução" em CSS próprio (como `AssetPicker.css`) ou confere os pixels no E2E; mexer no reset fica fora do card (A-P3, B-P3-4).
- `favicon.ico` 404 na raiz do DEV, uma vez por browser; é ambiente, não o protótipo (B-P3-6).
- Achados do detector no incumbente clonado (cinza sobre cor e roxo/gradiente do botão Otimizar, AppNav 10/11 px, `live.css`), todos em COPIED (B-P3-9).
- Formato de número misto ("181.74" na lista viva × "181,74" no texto; "94.829,00" × "93,610.00") e datas em inglês da lista viva (A-P3, B-P3-10).
- Rótulos vivos em inglês no Combo e na Otimização ("1 minute (só cripto)", "Run Optimization", "Optimization Complete") ao lado do delta em português (A-P3).
- Amostra do protótipo: números, datas, versões, trades, gráfico como captura PNG, "Otimizar" na seleção mista sem efeito além do aviso, e os botões de tempo gráfico do SPY trocando só textos (A-P3, B-P3-10).
- "Otimizando…" sem dizer que coleta na primeira execução (A-P3): **resolvido no protótipo r1** com a linha de coleta no Combo e na Otimização; o texto exato e o tempo de exibição ficam para o Apply.

## Migration Plan

1. Sem migração de esquema: histórico, amostra e catálogo são do #1118/#1117. Os campos novos vão na resposta e em `favorite.metrics` (JSON).
2. Ligar a regra do gap com `STOP_GAP_EXIT=1` (padrão) junto com o deploy; rodar a regressão cripto antes/depois em DEV.
3. Liberar a classe no backtest de 1 ativo (decisão 2: Combo, Otimização e API) no mesmo deploy, junto com o texto novo da recusa (decisão 3); lote e Descoberta seguem recusando.
4. O refresh diário dos favoritos de cripto recalcula com a nova regra no próximo ciclo; nenhum recálculo em massa.

Rollback: `STOP_GAP_EXIT=0` volta à saída no preço do stop; remover `run_scope` do Combo e da Otimização volta a recusar ação/ETF. Nada se perde: os favoritos guardam o histórico de runs.

## Open Questions

Nenhuma aberta. As duas perguntas do a1 foram fechadas por Alan em 23/10/2026 (comentário «Decisões de Alan no Design (23/10/2026)» no issue):

1. ~~O que é o "backtest individual" na tela.~~ **Fechada (23/10/2026):** Combo com 1 ativo **e** a tela Otimização com 1 ativo, mais o backtest com parâmetros fixos pela API; o lote com vários ativos continua no #1120. Aplicada na decisão 2 (com as datas fixas de jan. 2024 visíveis) e no clone `optimize.html`.
2. ~~Aviso em Favoritos sobre a mudança do gap na cripto.~~ **Fechada (23/10/2026):** sem aviso novo em `/favorites`; o resultado explica a regra. Aplicada nas decisões 6 e 15 e em Risks.

As outras cinco decisões de Alan no Design (recusa com texto novo, hora de Nova York no intradiário, USDT na lista de cripto, regressão só com o número novo na tela e "Dados e execução" recolhido no celular) estão nas decisões 3, 18, 13, 17 e 19.

## Apply contract

O Apply lê este `design.md` e os HTML em `frontend/public/prototypes/card-1119-backtest-acoes-etfs/` como spec de layout.

**Contrato visível (não P3):**

- Bloco "Dados e execução" em `/combo/results` e no resultado da Otimização com proveniência, faixa de precisão (estados: intrabar, por falta com trecho, por erro, escolhida; título "diária" só no 1d), nota de coleta parcial, os 8 fatos e as convenções da decisão 16; 4 colunas a 1440 px, 2 até 1100 px e 1 a 390 px; sem rolagem horizontal; abaixo de 768 px recolhido com resumo e botão acessível (decisão 19).
- Chip de classe; lista de operações com todo o dinheiro na moeda da classe (cripto USDT, ação/ETF USD); hora de Nova York com fuso no intradiário de ação/ETF; "Stop com gap" com stop e abertura na tabela e no cartão móvel.
- Favoritar ação/ETF: botão visível, `aria-disabled`, focável, motivo escrito e anunciado, sem modal; cripto como hoje; nenhum aviso novo em `/favorites`.
- Combo: os textos e estados da decisão 16; 1 ação/ETF abre o resultado sem salvar; seleção mista roda só a cripto, com 1m/5m de volta, e diz o porquê novo (decisão 3); 5m com ação avisa antes de rodar e não roda; linha de coleta ao rodar; falha de coleta sem dados vira alerta; texto da caixa Market Data com contraste AA.
- Otimização: 1 ação/ETF roda e mostra o resultado ao lado com "Dados e execução"; período fixo visível; 1m/5m/30m indisponíveis com ação; 15m/1h/4h sem 5m na janela avisam antes de rodar; recusa do lote e da seleção mista com o texto da decisão 3.
- Descoberta: só o texto da recusa muda (decisão 3).
- Regressão cripto: a tela mostra só o número novo; antes/depois só na evidência.
- Comportamentos dos specs: aceite e recusas por escopo, coleta só do que a execução usa, tempos montados no pregão, gap em todos os caminhos, precisão nunca silenciosa, custos e anualização por classe, recusa de favorito na API.

**P3 aceito (Apply):** nomes de campos (`run_scope`, `execution`, `conventions`, `history_unavailable`), forma do interruptor `STOP_GAP_EXIT`, limite de espera da coleta (30 s do #1118), formato de número e data (o formatador vivo da página; o protótipo mistura o "172.10" vivo da tabela com "172,10" do texto), ordem dos fatos, ícones, textos do painel Demonstração (não vão para o produto), números, datas, versões e trades do protótipo (amostra), a captura PNG do gráfico no lugar do canvas, o texto exato da linha de coleta e quanto tempo ela fica, e os P3 de Risks.

## Prototype

- Canônico: `frontend/public/prototypes/card-1119-backtest-acoes-etfs/index.html`, clone de `/combo/results` com o resultado de NVDA 1d long, "todo o histórico": chip "Ação"; "Salvar nos Favoritos" recusado com o motivo; "Dados e execução" com precisão diária e o trecho "11 nov. 2014 a 18 mai. 2026", recolhido no celular; lista em USD, só com data (1d), com "Stop com gap" (26 fev. 2026: stop 181.74, abriu 172.10). Demonstração: "Falha ao ler o intradiário", "Intrabar desligado" e "Coleta parou no meio" (nota âmbar de janela coberta menor).
- Extra `etf-short.html`: SPY 1h short, 1h montado do 5m, intrabar 15m cobrindo a janela, "Short simulado", "Preços ajustados", gap de alta na abertura do pregão (27 ago. 2026, 09:30 EDT: stop 672.04, abriu 676.10), lista com data e hora de Nova York, favorito recusado. Demonstração: tempo gráfico 1h / 4h / 15m (textos do fato, custo e anualização).
- Extra `cripto.html`: BTC/USDT 4h long, regressão cripto (só o número novo): proveniência Binance Spot, lista toda em USDT, sem aviso de fração, "Salvar nos Favoritos" vivo, gap explicado; Demonstração "15m não cobre a janela" mostra "Precisão do candle de 4h" com o trecho.
- Extra `configure.html`: clone de `/combo/configure` com NVDA selecionado, busca AAPL (sob demanda com o texto novo), 1h, fonte Binance Ações (AA), nota de classe nova, 1m/5m indisponíveis, dicas, texto antes de rodar; "Otimizar" mostra a linha de coleta e abre `index.html`. Demonstração: "NVDA + BTC/USDT" (1m/5m voltam; escolher 5m e remover BTC/USDT dá o aviso de 5m antes de rodar), "NVDA + SPY", "Coleta de NVDA falhou".
- Extra `optimize.html`: clone de `/combo/optimize` com NVDA selecionado em 1d e o resultado ao lado: nota de classe nova, sob demanda com o texto novo (AAPL, QQQ), 1m/5m/30m indisponíveis, "Período: 1 a 31 jan. 2024, fixo nesta tela.", dica de tempo, texto antes de rodar, "Dados e execução" com precisão diária e o trecho de jan. 2024; "Run Optimization" mostra a linha de coleta; Timeframe 15m/1h/4h avisa antes de rodar que o 5m não cobre jan. 2024. Demonstração: "NVDA + BTC/USDT" e "NVDA + SPY" com o texto novo da recusa.
- Apoio: `live.css` (CSS vivo inteiro), `delta.css`, `delta.js`, capturas `*-chart-desk.png` e `*-chart-mob.png`.
- Nenhuma página é painel ANTES/DEPOIS nem "N estados"; o painel Demonstração fica no fim, no fluxo, sem `position:fixed`.

## Prototype Validation

Evidência do autor, rework r1 (23/10/2026), depois das 7 decisões de Alan no Design e dos achados mecânicos da crítica A/B. Substitui a evidência do a1. Toda alteração posterior nos arquivos abaixo invalida esta validação.

| Arquivo | Bytes | sha256 | COPIED | DELTA |
|---|---|---|---|---|
| `index.html` (canônico) | 47.602 | `b002bea343432388961a20c8356a24570bdca67a199b9b93d3f3b435809076f1` | 8/8 pares, 24.741 B | 5/5, 21.224 B |
| `etf-short.html` | 45.962 | `017fd1e41ec5e5eba3cde0083799d56916641f8fc65cc73e9fa4fa0dbfef4908` | 8/8 pares, 24.932 B | 5/5, 19.392 B |
| `cripto.html` | 42.000 | `71dcb0b818d7cab4fc72d048b70989c0ab64c386a25dfc1b25e52beca16fbd75` | 7/7 pares, 25.568 B | 4/4, 14.898 B |
| `configure.html` | 33.971 | `463d3c1e32e95ceb065c5c5c02bfbcf9f6cbabd5622f0a898e55f33ddaa25755` | 11/11 pares, 29.361 B | 8/8, 2.652 B |
| `optimize.html` (novo) | 38.693 | `575019cd14c590676bcc2f0c9a9a44995df34d3f73750fee5ea8af672989544d` | 12/12 pares, 30.564 B | 8/8, 6.072 B |
| `live.css` | 222.723 | `7fb6d878705b10256f16443101d7502ca2e7193ced5be9950946020e7e058944` | clone inteiro | — |
| `delta.css` | 8.843 | `8e2e6fe19e77af9ac3f6728a9ac7343b86ab89e911965be524028c4b4d7f1714` | — | delta |
| `delta.js` | 15.175 | `94188bc053c13788f4b8a7564fc212aacada904a769e847e14c27670bc8fc492` | — | delta |
| `nvda-chart-desk.png` | 73.788 | `2e0e6224f99ab6f1dc8f5931784aa5f2bc807da22062dd60e71bafa410d07f25` | captura viva | — |
| `nvda-chart-mob.png` | 47.500 | `edc567e07b989296f94737cfcb0d5d902a81510ddbae7fcbd594c4362d663121` | captura viva | — |
| `spy-chart-desk.png` | 73.846 | `5374dca27c891542434ceb493b43525f69f3227e8e5657fffd4da196b728d711` | captura viva | — |
| `spy-chart-mob.png` | 47.205 | `d0600dbb933c58f1b15896d06ad08a61d08ebebed8e887ff76dc11e57055749e` | captura viva | — |
| `btc-chart-desk.png` | 73.049 | `1c1909eb591693eb65c6802a69d3adbb99cb7c2821d3ec5b375f49ecc84b5379` | captura viva | — |
| `btc-chart-mob.png` | 54.750 | `8943d7e8cbd66f1a208436cb0d512724106377ec7a1f915557b203e526a03621` | captura viva | — |

Nos três resultados, o maior bloco DELTA é a lista de operações viva remarcada (moeda, hora de Nova York no SPY e saída com gap). As capturas vivas são as do a1 (`develop` @ 5fe666fe, bundle `index-C-bdjWHT.js`, API simulada); a de `/combo/optimize` é nova, com o mesmo método, em dois estados da mesma página (NVDA selecionado; painel de resultado depois de rodar), sem `pageerror`. Os HTML saem de um build determinístico (o build do a1 reproduz os sha256 do a1 byte a byte).

- **Gate do clone** (`scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD): `design_token_gap` = None; `UI impact: affected` / `live_route: /combo/results` / `surface: existing` em L1–L3; `evaluate_clone_gate` = True; `clone_gate_ok` = True; `canonical_proto_html` = `index.html`; `classify(index.html, /combo/results)` = PASS; landmarks de `/combo/results` também em `etf-short.html` e `cripto.html`. `/combo/configure` e `/combo/optimize` não estão no catálogo: extras sem gate próprio.
- **Browser gate na URL pública** (`gate2.py https://dev.criptofarol.com.br`, Playwright Python 1.62 + Chromium headless shell 1243, `pt-BR`, tema escuro, contexto novo por página × viewport), em `https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/` (+ `etf-short.html`, `cripto.html`, `configure.html`, `optimize.html`). **277/277 asserts PASS**:

  | Página | 1440×900 | 390×844 |
  |---|---|---|
  | `index.html` (pasta `/`) | 28/28 | 34/34 |
  | `etf-short.html` | 27/27 | 32/32 |
  | `cripto.html` | 20/20 | 25/25 |
  | `configure.html` | 26/26 | 26/26 |
  | `optimize.html` | 27/27 | 32/32 |

  Cobertura: sha256 do corpo servido == disco; COPIED/DELTA em pares; Demonstração no fluxo; sem rolagem horizontal antes e depois dos estados; sem erro de console, `pageerror` nem resposta ≥ 400; landmarks; os 8 fatos, custos, anualização, fração, 252 pregões, taxa assumida, favoritar recusado (aria-disabled, motivo, anúncio, sem modal) e cripto como hoje. Decisões de Alan: (1) Otimização com NVDA roda, nota nova, 1m/5m/30m indisponíveis, período fixo visível, texto antes de rodar, "Dados e execução" ao lado com precisão de jan. 2024, linha de coleta, 1h avisa antes e não roda, mista com 1m/5m/30m de volta; (3) texto novo na seleção mista e em "só ações/ETFs" do Combo e da Otimização, antes e ao rodar; (4) SPY com "Data e hora (Nova York)" e 10 horas "EDT" na tabela, cartões com hora e "Horário de Nova York (EDT)", NVDA 1d só com data; (5) lista de cripto sem "USD" solto, tudo em USDT; (6) cripto sem antes/depois na tela; (7) no celular resumo visível, `aria-expanded=false`, fatos ocultos, alvo ≥ 44 px, Enter abre com foco e anel no botão, Espaço fecha, toque abre; no desktop tudo aberto, sem botão. Mecânicos: "Preços ajustados" no SPY; cripto 4h "Precisão do candle de 4h" e fato "Candle de 4h", sem "diária"; contraste da caixa Market Data ≥ 4,5:1 (medido no browser); caminho real do 5m (mista → 5m → remover BTC/USDT → aviso `role=status` antes de rodar, 5m mantido, "Otimizar" não roda, 1h limpa); coleta parcial na Demonstração do index (nota âmbar `role=note`, fato e Avisos); textos de 4h e 15m do SPY; linha de coleta no Combo antes do alerta de falha e antes de abrir o resultado. Console: nenhum erro nas 10 cargas. Scripts: `capture_opt.py`, `build2.py`, `gate2.py` e `clonegate2.py` no scratchpad do autor.
- **sha256 servido** (capturado nas respostas do browser): os 14 arquivos da tabela, mais a pasta `/` (== `index.html`), batem com o disco.
- **Detector Impeccable.** CLI (`detect.mjs --json`): `index`, `etf-short`, `cripto`, `delta.css`, `delta.js` = `[]`; `configure` 10 e `optimize` 9, todos em linhas COPIED (cinza sobre cor e roxo do incumbente). Modo hook, a partir da raiz (`hookscan.mjs` do B, `DESIGN.md` da raiz): `delta.js` = `[]`; `delta.css` = 11× `design-system-color` `#b7bdc6`, todos o literal herdado da descrição viva de `/combo/results` (sem token; P3 em Risks); **nenhuma cor inventada** (as 6 do a1 viraram tokens); `optimize.html` 12, todos em linhas COPIED (AppNav 10/11 px, cinza sobre cor, roxo). Nenhum achado silenciado.

Histórico (a1, 23/10/2026): 210/210 asserts PASS no servidor local e depois na URL pública (após o restart do serviço de protótipos); A/B deram PASS sem P0/P1 com os sha256 do a1 (`index.html` `8c0f34c2…`).

## Impeccable

Operate, refinamento clone+delta de `/combo/results`, `/combo/configure` e `/combo/optimize`. Setup com `node .agents/skills/impeccable/scripts/context.mjs --target frontend/src/pages/ComboResultsPage.tsx` (PRODUCT.md + DESIGN.md). As decisões de produto do a1 foram fechadas por Alan em 23/10/2026 e aplicadas no rework r1 (Open Questions). No celular, divulgação progressiva: o que decide "confio neste número?" (precisão, coleta parcial, avisos) fica à vista e o resto abre com um toque. Shape: o delta é um bloco de leitura (fatos + convenções) depois do resumo, uma faixa de precisão com tom só quando a precisão caiu, e marcas pontuais (chip, gap, favorito) onde o olho já está. Tokens do produto, rampa 12/13/14/16 px, raios 6/8 px do `DESIGN.md`, alvos de 44 px no botão recusado, foco visível, `aria-disabled` + `aria-describedby` + `role=status`, `role=note` na faixa de precisão, contraste AA medido (no `delta.css` e no browser), cores do delta por token (sobra só o `#b7bdc6` herdado, ver Risks). A seção de crítica fica para o pai.

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r1) aplicou as decisões de Alan no Design e os achados mecânicos da dupla. Não houve segundo rework.

- Autor: `design-autor 1119 a1` (isolado). Rework: `design-autor 1119 r1` (isolado).
- Assessment A: `assessment-a 1119 a1` (isolado). Assessment B: `assessment-b 1119 a1` (isolado, detector + navegador).
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /combo/results` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/
- Protos extras: https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/etf-short.html, https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/cripto.html, https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/configure.html e https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/optimize.html
- Snapshots: `.impeccable/critique/1119-card-1119-backtest-acoes-etfs-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1**: nenhum.
- **Juízo, decidido por Alan no Design** ([comentário](https://github.com/oalansilva/crypto/issues/1119#issuecomment-6374237456)). Tudo foi aplicado no r1:
  - Open Question 1 do autor: backtest de 1 ativo = Combo com 1 ativo **e** Otimização com 1 ativo, mais a API com parâmetros fixos.
  - Open Question 2 do autor: Favoritos sem aviso novo sobre o gap.
  - P2 de A e de B: a recusa no lote e na Descoberta ganha texto novo ("só com 1 ativo por enquanto").
  - P2 de A: operações intradiárias de ação e ETF com data e hora de Nova York.
  - P2 de B: a lista de cripto passa a mostrar USDT em valor e lucro.
  - P2 de B: a regressão cripto mostra só o número novo na tela; o antes/depois fica na evidência.
  - P2 de A: "Dados e execução" recolhido no celular.
- **P2 mecânicos, corrigidos no r1**:
  - "Preços ajustados" no ETF;
  - precisão do candle de 4h coerente na cripto;
  - contraste AA do texto novo da caixa Market Data;
  - aviso de 5m alcançável pelo caminho real;
  - estado "coleta parou no meio";
  - 6 cores inventadas do delta trocadas por tokens;
  - textos de 15m e 4h no fato "Tempo gráfico";
  - sha256 dos PNG;
  - risco do servidor de protótipos atualizado;
  - linha de coleta ao rodar.
- **P3 aceitos, para o Apply**: os itens da subseção "P3 aceitos" em Risks / Trade-offs:
  - `#b7bdc6` herdado;
  - o detector CLI abaixo de `frontend/`;
  - reset `*` sem `@layer`;
  - favicon 404;
  - incumbente clonado;
  - formato de número e data e rótulos vivos;
  - amostra;
  - texto da linha de coleta.
- **Disposition:** o delta visível fica no resultado (`/combo/results`), no Combo (`/combo/configure`) e na Otimização (`/combo/optimize`). Na Descoberta, só o texto da recusa. Lote com vários ativos fica para o #1120, descoberta para o #1121, favoritos de ação/ETF para o #1122.
- **Risco registrado, sem ser P0:** com as datas fixas de jan. 2024 da Otimização, ação e ETF ali rodam de fato só em 1d. Em 15m, 1h e 4h, a tela recusa antes de rodar e mostra o motivo e a saída.

### Proxies

- `design.md` words: 7321 (antes desta seção)
- HTML generated vs copied (`index.html`): 21224 vs 24741
- Spawns: 4
- `proxy modelo: design-autor → Opus 5.5 (claude-opus-5-5)` (a1 e r1)
- `proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5)`
- `proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5)`

Design Agent verdict: PASS
