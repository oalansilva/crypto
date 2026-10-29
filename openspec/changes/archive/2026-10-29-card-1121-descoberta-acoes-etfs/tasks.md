## 1. Aceite por classe no Preflight

- [x] 1.1 `asset_analysis_guard.discovery_symbol_reasons` deixa de devolver ação e ETF negociáveis; marcado e fora do catálogo seguem com o motivo (decisão 2)
- [x] 1.2 `discovery_service.preflight`: remover o ramo de classe ("Inclua ao menos 1 par cripto"), contar ação e ETF no total e no teto, devolver `by_class`, `collection`, `precision_forecast` e `survivorship` (decisões 2, 6, 8, 9, 12)
- [x] 1.3 Recusa do teto com o total, as classes e "Estreite a seleção"; `create_sweep` continua recusando o mesmo snapshot (decisão 8)
- [x] 1.4 Remover `DISCOVERY_EQUITY_REASON` e o texto "… a Descoberta vem depois" do backend e do front

## 2. Aquisição, amostra e execução por classe

- [x] 2.1 `discovery_inputs.prepare` decide a classe pelo catálogo; ação/ETF coletam por `prepare_equity_history` (com `on_progress`) e congelam por `freeze_symbol` (`candles` e `intraday`, vazio sem 15m); manifesto com `provenance` de `binance_equity` (decisão 3)
- [x] 2.2 Supervisor passa a fonte do manifesto a `run_optimization` e transforma o progresso da coleta em evento (decisões 3 e 9)
- [x] 2.3 Amostra única por (varredura, ativo, tempo, janela), gravada sob lock e reaproveitada pelas outras combinações e pelas novas tentativas (decisão 4)
- [x] 2.4 "Sem candles" e "poucas velas" viram `insufficient_sample` com motivo; falha de coleta vira falha operacional dentro das 3 tentativas (decisão 7)
- [x] 2.5 `_expected_candles_for_window` pelo calendário NYSE para ação e ETF; cripto igual (decisão 5)
- [x] 2.6 `run_combination` guarda `asset`, `execution` e `conventions` em `metrics`; `fees_slippage_record` por classe (decisões 6 e 11)

## 3. API de varredura, ranking e promoção

- [x] 3.1 `GET /sweeps/{id}` com `assets[]` (estado, combinações feitas, etapa e página da coleta, motivo) (decisão 7)
- [x] 3.2 `_result_row` e `leaderboard` com `asset`, `execution`, `conventions`, `precision`; filtro `asset_class` e `class_counts` com rank global preservado (decisão 11)
- [x] 3.3 `promote_result`: `tier` 3 para cripto e nulo para ação/ETF; `parameters.data_source`/`direction`; `analysis_asset`, `analysis_execution`, `analysis_conventions`, `data_provenance`; `lock_and_find_duplicate` com `data_source` e `asset`; amostra fixada (decisão 10)

## 4. Frontend `/combo/discovery` (seguir o protótipo)

- [x] 4.1 Seleção: ação e ETF negociáveis rodam na Descoberta; nota da classe e texto sob demanda da Descoberta (decisão 2)
- [x] 4.2 Preflight: "Vão rodar", "Precisam de coleta", "Precisão diária prevista", recusa do teto, viés de sobrevivência e taxa por classe (decisões 2, 6, 8, 9, 12)
- [x] 4.3 Acompanhando: quadro "Por ativo" com estados (desfecho misto com as duas contagens), cabeçalhos de coluna acima de 620 px e cartão abaixo, ativo em curso + falhas + insuficientes no topo, "Mostrar mais 50", linha viva; foco no título do progresso depois de confirmar o cancelamento; parciais com o bloco do candidato (decisões 7 e 11)
- [x] 4.4 Decidir: cabeçalho multiclasse com o estado real, nota "Sem resultado" / "Amostra insuficiente" com "ver Por ativo", aviso de sobrevivência, filtro Classe (opção 0 desabilitada, vazio com "Limpar filtros", 44 px abaixo de 768 px), bloco compacto do candidato, nota de cobertura por calendário (decisões 7, 11 e 12)
- [x] 4.5 Modal de promoção com identidade da execução, título e destino por classe, estado "Favorito · sem estrela" + "Ver em Favoritos" (decisão 10)

## 5. Testes e verificação

- [x] 5.1 Testes de contrato do backend: varredura mista aceita; NVDA congelado de `binance_equity` com o mesmo `snapshot_id` em treino, tentativas e avaliação; NVDA 1d em todo o histórico com precisão diária e trecho; 4h de ação em 2019–2020 como "sem candles"; falha de coleta → "Falha" após 3 tentativas; teto com ação/ETF; cobertura NYSE; promoção de NVDA com `tier` nulo e chaves `analysis_*`
- [x] 5.2 Regressão de cripto: varredura só de cripto com as mesmas combinações, amostra, métricas, elegibilidade e ranking de antes
- [x] 5.3 E2E Playwright de `/combo/discovery` (funcional + visual, 1440 e 390) com a API simulada, seguindo o protótipo: Preflight misto, teto, por ativo, filtro Classe, promoção de NVDA; atualizar `route-coverage-inventory.json`
- [ ] 5.4 Demonstração no card (DEV): varredura BTC/USDT + NVDA + um ETF em 1d e todo o histórico até o ranking e o favorito, com período efetivo, precisão e limitações visíveis em Favoritos; seleção acima de 1.000 recusada; registrar o protótipo seguido e os desvios no handoff <!-- covenant-flow:after-qa -->
