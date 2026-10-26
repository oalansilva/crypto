## Why

Quinta história do épico #1116. Com o catálogo (#1117), o histórico Binance (#1118), o backtest de ação e ETF (#1119) e o lote multiclasse (#1120) em `develop`, só a Descoberta ainda deixa ação e ETF de fora. Ela recusa os dois no Preflight, congela a amostra pelo caminho CCXT e roda o otimizador com `data_source="ccxt"` fixo. O ranking não mostra classe nem moeda, e a promoção grava o favorito sem a identidade do ativo.

## Problema

Alan não consegue explorar estratégias de ações/ETFs porque aquisição e execução da descoberta ainda fixam o caminho cripto.

## História

Como pesquisador, quero descobrir estratégias em cripto, ações e ETFs para avaliar candidatos de forma justa e reproduzível.

## Entra

- [ ] **Três classes na Descoberta:** cripto, ação e ETF entram na mesma varredura pelo catálogo unificado, e ação e ETF deixam de ficar fora por classe. Cada ativo é coletado e avaliado com a sua classe, fonte, sessão, ajuste e moeda, sem usar dados de outro mercado.
- [ ] **Mesma amostra, sem vazamento:** treino, tentativas e avaliação final usam a mesma amostra congelada, com separação temporal entre treino e avaliação.
- [ ] **Precisão diária visível:** ação ou ETF sem intradiário que cubra a janela gera resultado válido, com marca visível de precisão diária e do trecho sem intradiário; a precisão nunca cai em silêncio, como no backtest e no lote (decisão de Alan, 26/10/2026). Ativo sem candles suficientes para a análise aparece com estado explícito, nunca como resultado.
- [ ] **Teto de 1.000 combinações:** o teto continua valendo com ação e ETF. Acima de 1.000 combinações válidas, a tela recusa antes de começar e pede para estreitar a seleção (decisão de Alan, 26/10/2026).
- [ ] **Orçamento, progresso, cancelamento e retomada** operam também com ações/ETFs; falha não vira estratégia aprovada nem amostra suficiente.
- [ ] **Ranking numa lista só:** os candidatos aparecem numa única lista ordenável, com classe, moeda (USD ou USDT) e convenções em cada linha, e filtro por classe; USD e USDT nunca se confundem (decisão de Alan, 26/10/2026).
- [ ] **Candidato vira favorito:** candidato de ação ou ETF pode ser promovido a favorito como no lote, preservando convenções, janela, versão da amostra e direção; por isso o aceite depende do #1122 (decisão de Alan, 26/10/2026). Cripto mantém o comportamento de hoje.
- [ ] **Viés de sobrevivência explícito:** varredura num período passado avisa que usa só os ativos do catálogo de hoje.
- [ ] **Verificação:** uma varredura com BTC/USDT, NVDA e um ETF chega ao ranking e a favorito, com período efetivo, precisão e limitações visíveis; NVDA em todo o histórico mostra a marca de precisão diária; uma seleção acima de 1.000 combinações é recusada com o pedido para estreitar. A regressão de cripto mostra a Descoberta de cripto funcionando como hoje.

## Não entra

- Executar ordens automaticamente ao descobrir/favoritar uma estratégia.
- Criar novas famílias de estratégia além das existentes.

> Seções acima copiadas do body do issue [#1121](https://github.com/oalansilva/crypto/issues/1121) (grelhado, fronteira vazia; 4 decisões de Alan de 26/10/2026 dentro de Entra). Não houve reentrevista.

## What Changes

- **Descoberta aceita cripto, ação e ETF na mesma varredura.** O Preflight deixa de tirar ação e ETF por classe. Ativo marcado pela Binance e ativo fora do catálogo continuam fora com o motivo (#1117). Os tempos da Descoberta (15m, 1h, 4h, 1d) servem às três classes (#1119), então nenhum tempo fica de fora por classe.
- **Aquisição pelo caminho do #1118 para toda classe.** Ação e ETF são coletados por `prepare_equity_history`, com a série do tempo gráfico e o 5m do intrabar, e congelados pela fonte `binance_equity`. A cripto segue o caminho unificado, como hoje. O otimizador recebe a fonte do ativo, não `ccxt` fixo. Nenhuma série de outro mercado entra.
- **Mesma amostra congelada, corte 70/30 no tempo.** Coleta e congelamento acontecem uma vez por ativo, tempo e janela da varredura. Treino, tentativas e avaliação final de cada combinação leem só dessa amostra. O corte temporal 70/30, o mínimo de 30 trades e o GO só com walk-forward não mudam.
- **Precisão diária marcada.** Ação ou ETF sem 15m que cubra a janela roda com o candle do tempo gráfico e gera resultado válido, com a marca âmbar "Precisão diária · sem 15m de <início> a <fim>" no Acompanhar, no ranking, na promoção e no favorito. O Preflight avisa antes de começar quais ativos devem cair para precisão diária.
- **Estado explícito por ativo.** O Acompanhar ganha um quadro "Por ativo", com classe, moeda, combinações feitas e o estado de cada ativo: na fila, coletando histórico (série e página), rodando, concluído, concluído com precisão diária, amostra insuficiente (com o motivo, inclusive "sem candles na janela") e falha. Amostra insuficiente e falha nunca viram candidato nem favorito.
- **Teto de 1.000 combinações com ação e ETF.** O teto passa a contar ação e ETF. Acima dele, o Preflight recusa antes de começar e pede para estreitar a seleção, com o total por classe.
- **Orçamento, progresso, cancelamento e retomada** valem também para ação e ETF: a coleta conta como trabalho da combinação e usa o mesmo lease, as mesmas 3 tentativas e o mesmo limite de recursos. Pausar, Retomar e Cancelar continuam como hoje. Uma tentativa refeita reaproveita a amostra já congelada.
- **Ranking numa lista só.** Cada linha do Acompanhar e do Decidir mostra classe e moeda (USDT ou USD), convenções, precisão e período efetivo. O Decidir ganha o filtro **Classe** (Todas, Cripto, Ações, ETFs, com contagem). A ordenação existente (GO acima de NO-GO, Calmar ou CAGR vs B&H) vale para todas as classes juntas, sem soma nem conversão entre USD e USDT. O cabeçalho mostra a taxa por classe.
- **Promoção de ação e ETF como no lote.** O mesmo modal de promoção, com a identidade do ativo à vista. Para ação e ETF, o destino é "Favoritos · sem nível de estrela" até o #1122. O favorito guarda classe, fonte, sessão, ajuste, moeda, convenções, janela efetiva, versão da amostra (`snapshot_id`) e direção, nas mesmas chaves que Favoritos já lê (#1120). A cripto segue "Promover a favorito tier 3", como hoje.
- **Viés de sobrevivência.** O Preflight e o Decidir avisam: "a varredura usa só os ativos do catálogo de hoje; ativos que saíram da Binance antes não entram".
- **Textos que saem da Descoberta:** o motivo "ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois", a nota do seletor "Nesta etapa as análises rodam só com cripto" e o estado "Pronto para iniciar · ações e ETFs fora".

## Capabilities

### New Capabilities

- `multiclass-discovery`: varredura com cripto, ação e ETF. Cobre o aceite por classe no Preflight, a aquisição e o congelamento por classe, a mesma amostra com corte temporal, a precisão diária marcada, o estado por ativo, o teto de 1.000 com ação e ETF, o orçamento, o progresso, o cancelamento e a retomada, e o aviso de viés de sobrevivência.
- `discovery-multiclass-ranking`: ranking único com classe, moeda, convenções, precisão e período efetivo por linha, filtro por classe e promoção de ação e ETF a favorito com a identidade da execução.

### Modified Capabilities

- `crypto-only-mvp`: a Descoberta deixa de recusar ação e ETF (sobre o texto do #1120). O Monitor continua só cripto até o #1122.
- `discovery-promotion`: a promoção continua tier 3 para cripto. Ação e ETF são promovidos sem nível de estrela até o #1122, com a identidade da execução.

## Impact

- Backend:
  - `services/discovery_inputs.py`: aquisição e congelamento por classe e amostra por ativo/tempo na varredura.
  - `services/discovery_supervisor.py`: fonte por ativo no otimizador e progresso da coleta.
  - `services/discovery_service.py`: Preflight multiclasse, teto, previsão de precisão e coleta, filtro `asset_class` no leaderboard, promoção com identidade e tier por classe.
  - `services/asset_analysis_guard.py` e `services/asset_catalog_service.py`: a Descoberta deixa de usar o motivo de classe.
  - `tasks/discovery_tasks.py`: persistência de `asset`, `execution` e `conventions`, cobertura pelo calendário da classe e "sem candles" como amostra insuficiente.
  - `services/discovery_favorite_metrics.py`: chaves `analysis_*` no favorito.
  - `metrics/backtest_execution_costs.py`: taxa por classe no registro de custos.
  - `routes/discovery_routes.py`: filtro `asset_class` e estado por ativo.
- Frontend:
  - `pages/DiscoveryPage.tsx`: Preflight, Acompanhar com o quadro por ativo, Decidir com o filtro Classe, as linhas multiclasse e o modal de promoção.
  - `lib/assetSelection.ts`: a Descoberta conta ação e ETF como roda.
  - `components/AssetPicker.tsx`: textos da classe e da coleta.
- APIs:
  - `POST /api/combos/discovery/sweeps/preflight` ganha `by_class`, `collection`, `precision_forecast` e `survivorship`, e para de devolver ação e ETF em `excluded_assets`.
  - `GET /api/combos/discovery/sweeps/{id}` ganha `assets[]`, o estado por ativo.
  - `GET …/leaderboard` aceita `asset_class` e devolve `asset`, `execution`, `conventions` e `class_counts` por linha.
  - `POST /api/combos/discovery/results/{id}/promote` aceita ação e ETF.
- Dados: sem migração de tabela. `discovery_results` já tem `data_source`, `asset_class`, `session`, `adjustment`, `period_covered` e `snapshot_id`; `execution`, `conventions` e `asset` vão em `metrics` (JSON).
- Dependências: #1117, #1118, #1119 e #1120 em `develop`. **O aceite depende do #1122**, que cuida da identidade, da atualização e dos alertas do favorito de ação e ETF. O contrato com o #1122 está em `design.md`.
