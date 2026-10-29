## Why

Sétima história do épico #1116. O catálogo (#1117), o histórico Binance (#1118), o backtest de ação/ETF (#1119), o lote (#1120), a Descoberta (#1121) e os favoritos com alertas (#1122) já estão em `develop`. Hoje a única referência é o buy-and-hold do próprio ativo, e ela só aparece na Descoberta: a tela do resultado não mostra referência nenhuma. As três planilhas não dizem de que classe, moeda, fonte, sessão, ajuste, período e amostra vieram os números. Com cripto, ação e ETF lado a lado, Alan não consegue saber se uma estratégia vale a pena contra uma alternativa simples (segurar SPY, QQQ ou o próprio ativo), nem reproduzir o contexto de um número exportado.

## Problema

Alan não consegue interpretar comparações entre classes ou reproduzir o contexto de um resultado exportado.

## História

Como pesquisador, quero escolher uma referência e exportar resultados com contexto completo para avaliar o valor da estratégia e compartilhar a análise.

## Entra

- [ ] **Referência à escolha:** a referência padrão é o buy-and-hold do próprio ativo. Alan pode trocá-la pelo buy-and-hold de qualquer cripto, ação ou ETF do catálogo (por exemplo SPY ou QQQ); a referência escolhida é coletada quando é escolhida, se ainda não tiver histórico (decisão de Alan, 27/10/2026).
- [ ] **Escolha depois de rodar:** a troca acontece na tela do resultado (backtest/combo) ou do favorito, e a escolha fica gravada nesse resultado ou favorito e vai para a planilha. O ranking da Descoberta e do lote continua comparando com o próprio ativo (decisão de Alan, 27/10/2026).
- [ ] **Janela comum:** estratégia e referência são comparadas só no período que as duas cobrem, com calendário e ajuste coerentes; a tela e a planilha mostram esse período comum e o que ficou de fora. Referência sem histórico suficiente aparece com motivo claro, nunca como comparação válida nem como zero.
- [ ] **Moedas diferentes:** quando estratégia e referência têm moedas diferentes (USDT na cripto, USD em ação e ETF), a comparação é feita em percentual e a tela e a planilha avisam que USDT foi tratado como USD, sem conversão. Nunca em silêncio (decisão de Alan, 27/10/2026).
- [ ] **Retorno de preço:** referência de ação ou ETF (p.ex. SPY/QQQ) é informada como retorno de preço, sem dividendos.
- [ ] **Planilhas com contexto completo:** a planilha da lista de favoritos, a planilha de trades do resultado de combo/backtest e uma exportação nova do ranking da Descoberta trazem, além das métricas de hoje: classe, moeda, fonte, sessão, ajuste, período pedido e efetivo, modo de execução, referência escolhida com o seu resultado e período comum, e versão da amostra (decisão de Alan, 27/10/2026).
- [ ] **Sem recálculo escondido:** comparação e planilha correspondem ao resultado gravado e à amostra da referência gravada junto com a escolha; abrir ou exportar de novo não recalcula com dados atualizados.
- [ ] **Favoritos antigos:** favorito sem contexto registrado continua exportando. Classe e moeda saem do símbolo e aparecem marcadas como "deduzido"; o que não foi gravado (fonte, sessão, ajuste, versão da amostra) aparece como "não registrado" (decisão de Alan, 27/10/2026).
- [ ] **Verificação:** NVDA comparado com SPY; um ETF comparado com o próprio ativo; BTC/USDT comparado com o próprio ativo e com SPY (aviso de USDT tratado como USD e período comum visíveis); referência com histórico insuficiente mostra o motivo; troca de referência num favorito fica gravada e sai na planilha; as três planilhas trazem o contexto completo; um favorito antigo de cripto exporta com "deduzido" e "não registrado"; o ranking da Descoberta e do lote segue comparando com o próprio ativo.

## Não entra

- Fonte externa nova para a referência ou para conversão de moeda: a referência vem só do catálogo e do histórico Binance que já existem, e USDT x USD não é convertido.
- Escolher a referência antes de rodar, ou ordenar o ranking da Descoberta e do lote por outra referência que não o próprio ativo.
- Retorno com dividendos (retorno total) nas referências de ação e ETF.
- Otimização de alocação de carteira ou relatório fiscal.

> Seções acima copiadas do body do issue [#1123](https://github.com/oalansilva/crypto/issues/1123) (grelhado; quatro decisões de Alan de 27/10/2026 dentro de Entra). Não houve reentrevista. O *como* abaixo e em `design.md` foi conferido em `develop` @ 9b83d25e.

## Decisões de Alan no Design

- **Referência também na Descoberta (28/10/2026,** [comentário no #1123](https://github.com/oalansilva/crypto/issues/1123#issuecomment-6462139347)**).** Na Descoberta (Decidir, `/combo/discovery`), Alan escolhe uma referência (por exemplo SPY; qualquer cripto, ação ou ETF do catálogo, como no resultado) e cada candidato do ranking ganha uma **coluna extra** com o resultado contra essa referência. A **ordem do ranking não muda**: continua pela diferença contra o próprio ativo. A elegibilidade também não muda. Substitui, no Entra, "o ranking da Descoberta e do lote continua comparando com o próprio ativo" só no que diz respeito à coluna extra. Continua fora: ordenar o ranking, ou mudar a elegibilidade, por outra referência. O body do issue não foi reescrito; a decisão vive no comentário. Motivo de Alan: "hoje uso mais a tela Descoberta".

## What Changes

- **Comparação com referência na tela do resultado.** A tela do resultado (`/combo/results`) ganha a seção "Comparação com referência", logo abaixo da análise da estratégia. Ela mostra, no período comum, o retorno e o CAGR da estratégia e da referência e a diferença em pontos percentuais. A referência padrão é o buy-and-hold do próprio ativo. Hoje essa tela não mostra referência nenhuma: o buy-and-hold só aparece na Descoberta.
- **Trocar referência depois de rodar.** O botão "Trocar referência" abre um seletor do catálogo (cripto, ação e ETF), com busca e filtro de classe. A referência escolhida é coletada na hora se ainda não tiver histórico. A escolha fica gravada no resultado, ou no favorito quando a tela foi aberta de Favoritos, e vai para a planilha. Ao salvar o resultado nos Favoritos, a escolha vai junto.
- **Comparação gravada, sem recálculo escondido.** O servidor calcula a comparação uma vez, na escolha, congela a amostra diária da referência (mesmo mecanismo de amostra do #1118, fixada enquanto um favorito a usa) e grava os números, o período comum e o que ficou de fora. Abrir a tela ou exportar de novo lê o que foi gravado. Só a atualização do backtest do favorito (evento já visível em Favoritos) refaz a comparação, com a mesma referência, e a tela mostra a data.
- **Janela comum e o que ficou de fora.** A comparação usa só o período que estratégia e referência cobrem, em fechamentos diários, com o calendário de cada lado (24/7 na cripto, pregão de Nova York em ação e ETF). A tela e a planilha mostram o período comum e o que ficou de fora (datas e trades da estratégia fora do período comum).
- **Histórico insuficiente com motivo.** Sem período comum, período comum curto demais ou coleta sem candles: a seção mostra o motivo e "Sem comparação", sem números e nunca zero.
- **Aviso de moeda e retorno de preço.** USDT contra USD: aviso visível "USDT tratado como USD, sem conversão; comparação só em percentual" na tela e na planilha. Referência de ação/ETF: "retorno de preço, sem dividendos".
- **Três planilhas com o mesmo contexto.** A planilha de Favoritos, a de trades do resultado e a nova exportação do ranking da Descoberta (botão "Exportar planilha" no Decidir) passam a ser montadas pelo servidor com um único conjunto de colunas de contexto: classe, moeda, fonte, sessão, ajuste, período pedido e efetivo, modo de execução, referência com o seu resultado e período comum, aviso de moeda, tipo de retorno e versão das amostras. Cada planilha leva uma aba "Legenda" com o significado de "deduzido" e "não registrado".
- **Favoritos antigos.** Favorito sem contexto registrado continua exportando: classe e moeda deduzidas pelo símbolo e marcadas "deduzido"; fonte, sessão, ajuste e versão da amostra como "não registrado"; referência sem comparação gravada como "não registrado".
- **Coluna extra no Decidir (decisão de Alan, 28/10/2026).** O Decidir ganha "Comparar com outra referência": o mesmo seletor do resultado escolhe um ativo do catálogo e cada candidato ganha a coluna "Contra <ativo>" com a diferença de CAGR no período comum, o CAGR da referência e o período comum, o aviso "USDT tratado como USD" na linha em que as moedas diferem e "Sem comparação" com o motivo (período comum curto ou sem período comum), nunca zero. A escolha fica gravada na varredura, para o usuário, e a coluna é calculada uma vez pelo servidor, num lote, sobre a amostra congelada de cada candidato e uma amostra congelada da referência; recarregar, abrir de novo ou exportar lê o que foi gravado. O padrão continua "Próprio ativo", sem coluna extra.
- **Ordem, rank e elegibilidade da Descoberta e do lote intactos.** O ranking segue pela métrica de "Ordenar por" (Calmar ou CAGR vs B&H do próprio ativo); a coluna extra não vira opção de ordenação nem filtro. O lote não ganha coluna. A exportação da Descoberta mantém a referência do próprio ativo nos 22 campos de contexto e, com uma referência extra escolhida, acrescenta as colunas "(extra)"

## Capabilities

### New Capabilities

- `benchmark-reference-choice`:
  - referência padrão (próprio ativo) e troca por qualquer cripto, ação ou ETF do catálogo, depois de rodar, na tela do resultado ou do favorito;
  - coleta da referência na escolha;
  - comparação gravada com a amostra da referência, sem recálculo ao abrir ou exportar; refeita só na atualização do favorito;
  - janela comum em fechamentos diários, calendário de cada lado, o que ficou de fora;
  - histórico insuficiente com motivo, nunca zero;
  - aviso USDT tratado como USD e retorno de preço sem dividendos;
  - escolha herdada ao salvar o resultado nos Favoritos.
- `result-context-export`:
  - colunas de contexto comuns às três planilhas;
  - planilha de Favoritos, de trades do resultado e do ranking da Descoberta montadas pelo servidor;
  - favoritos antigos com "deduzido" e "não registrado";
  - aba "Legenda".

### Modified Capabilities

- `discovery-leaderboard`: o Decidir ganha "Exportar planilha" (ranking com contexto e referência do próprio ativo) e a coluna extra com outra referência (escolhida depois da varredura, gravada na varredura por usuário, calculada uma vez com amostras congeladas, exportada nas colunas "(extra)"); ordem, rank global e elegibilidade continuam só no próprio ativo.

## Impact

- Backend:
  - novo `services/benchmark_comparison.py`: cálculo da janela comum, retorno e CAGR dos dois lados, o que ficou de fora, motivos de histórico insuficiente e gravação;
  - `services/market_history/snapshots.py`, `sample.py`: amostra diária da referência (papel `benchmark`), fixada pelo favorito;
  - `metrics/benchmark.py`: `calculate_buy_and_hold` deixa de devolver zero para histórico insuficiente no caminho novo (o caminho da Descoberta não muda);
  - novas rotas `POST /api/benchmark-comparisons`, `GET /api/benchmark-comparisons/{id}`; `PATCH /api/favorites/{id}` aceita a comparação escolhida; `POST /api/favorites` herda a do resultado;
  - `routes/combo_routes.py`: `optimize`/`backtest` devolvem a comparação padrão gravada; `export-trades` recebe contexto e comparação e monta a aba de contexto;
  - nova `GET /api/favorites/export` e `GET /api/combos/discovery/sweeps/{id}/leaderboard/export`;
  - Descoberta: `PUT`/`GET /api/combos/discovery/sweeps/{id}/reference-column` e `POST …/reference-column/retry`; o leaderboard devolve `reference_column` e, por linha, `reference_comparison`; cálculo no worker da fila de lotes (#1120), regenerando os trades de cada candidato a partir da amostra congelada dele;
  - novo `services/export_context.py` (colunas de contexto e estados "deduzido"/"não registrado");
  - `services/favorite_backtest_refresh_service.py`: refaz a comparação com a referência escolhida na atualização;
  - Alembic: tabela `benchmark_comparisons` (dono `result`, `favorite` ou `discovery_result`), tabela `discovery_reference_columns` e coluna `benchmark_comparison_id` em `favorite_strategies`.
- Frontend:
  - `pages/ComboResultsPage.tsx` e novo `components/results/BenchmarkComparison.tsx` (seção, seletor e estados);
  - `components/AssetPicker.tsx`: modo de escolha única para o seletor de referência;
  - `pages/FavoritesDashboard.tsx`: exportação pelo servidor e "Ref." na linha;
  - `pages/DiscoveryPage.tsx`: botão "Exportar planilha", faixa "Coluna extra", coluna "Contra <ativo>" (cabeçalho e célula; no celular, uma linha a mais no cartão) e o seletor de referência reaproveitado do resultado;
  - `components/charts/StrategyTradesTable.tsx`, `SaveFavoriteModal.tsx`: rótulo e referência no salvar.
- Sem nova dependência: `openpyxl` e `pandas` já montam a planilha de trades; o SheetJS do front deixa de montar a de Favoritos.
- Descoberta, lote e Monitor: sem mudança no cálculo do ranking, na ordenação nem na elegibilidade; a Descoberta só ganha a coluna extra.
