## 1. Banco e contrato

- [ ] 1.1 Alembic: tabela `benchmark_comparisons` (id uuid, user_id, favorite_id, owner_kind `result | favorite | discovery_result`, result_id, column_id, created_at, status, payload JSON), tabela `discovery_reference_columns` (id, sweep_id, actor, reference, reference_snapshot_id, status `collecting | computing | done | failed`, done, total, error, active, created_at, completed_at; única ativa por sweep e actor) e coluna `benchmark_comparison_id` (FK nula) em `favorite_strategies`, sem backfill
- [ ] 1.2 Modelo SQLAlchemy e schemas Pydantic do contrato `BenchmarkComparison` (design, decisão 4), com `reason.code` em `no_history | no_overlap | short_overlap` e `currency_note`
- [ ] 1.3 Amostra da referência: papel `benchmark` (série 1d do período comum) em `market_history/snapshots.py`/`sample.py`, com fixação pelo favorito e liberação ao trocar

## 2. Cálculo da comparação (backend)

- [ ] 2.1 `services/benchmark_comparison.py`: série 1d da referência (split ajustado em ação/ETF), período comum encaixado no calendário da referência, retorno da referência, composto dos trades fechados de dentro, trades e datas de fora, CAGR 365,25 dos dois lados, diferença em p.p., long-only
- [ ] 2.2 Estados insuficientes sem zero: sem candle, sem interseção, período comum < 30 dias; o caminho novo não usa o 0,0 de `calculate_buy_and_hold` (Descoberta e holdout intocados)
- [ ] 2.3 Aviso de moeda por moeda do par/classe (USDT x USD) e `return_kind` de ação/ETF = preço sem dividendos
- [ ] 2.4 Coleta na escolha: `prepare_equity_history(..., "1d", intrabar=False)` para ação/ETF e `HistoryService` para cripto, com teto de tempo; falha sem nada guardado não grava
- [ ] 2.5 Testes unitários: BTC/USDT x SPY (01/01/2019 fora, 0 trades), BTC x SOL (3 trades fora), NVDA x SPY, SPY x próprio ativo, CRCL sem interseção, período curto, short long-only, igualdade com o "Retorno total" quando o período comum é a janela inteira

## 3. Rotas e gravação (backend)

- [ ] 3.1 `optimize` e `backtest` gravam a comparação padrão (`trigger=run`) e devolvem `benchmark_comparison`
- [ ] 3.2 `POST /api/benchmark-comparisons` (owner `result` com contexto e trades; owner `favorite` com `favorite_id`) e `GET /api/benchmark-comparisons/{id}`; leitura nunca chama o cálculo
- [ ] 3.3 `POST /api/favorites` aceita `benchmark_comparison_id` (herança ao salvar) e fixa a amostra; `GET /api/favorites` devolve a comparação resumida
- [ ] 3.4 `favorite_backtest_refresh_service`: depois do refresh com sucesso, refaz a comparação com a referência escolhida (ou o próprio ativo) com `trigger=favorite_refresh`
- [ ] 3.5 Testes de rota: dono, admin, troca no favorito solta a fixação anterior, reabrir/exportar com histórico novo devolve os mesmos números, refresh refaz e muda a data

## 4. Planilhas com contexto (backend)

- [ ] 4.1 `services/export_context.py`: colunas de contexto na ordem do spec, estados `registrado | deduzido | não registrado`, dedução de classe/moeda pelo símbolo, aba "Legenda" (com "Comparação refeita" nas planilhas de favorito e "Tela × planilha" na de Favoritos); "Tipo de retorno da referência" = "Retorno de preço, sem dividendos" (ação/ETF) ou "Retorno de preço" (cripto)
- [ ] 4.2 `GET /api/favorites/export?ids=…`: colunas de hoje + contexto, na ordem dos ids, admin
- [ ] 4.3 `POST /api/combos/export-trades`: recebe `context` e `benchmark_comparison_id`; abas Trades (+ Moeda), Contexto e Legenda; com `favorite_id` lê o contexto do favorito
- [ ] 4.4 `GET /api/combos/discovery/sweeps/{id}/leaderboard/export`: recorte filtrado completo na ordem e rank global do leaderboard, colunas de hoje + os 22 campos de contexto com os nomes e a ordem do spec (Período pedido da varredura, retornos derivados do CAGR e da janela; janela abaixo de 30 dias = "Histórico insuficiente" com células vazias), referência própria, sem recálculo; com coluna extra ativa e `done`, + as 13 colunas "(extra)" lidas das comparações gravadas e "(extra)" na Legenda
- [ ] 4.5 Testes com openpyxl: cabeçalhos iguais nas três planilhas, favorito antigo de cripto com "(deduzido)" e "não registrado", insuficiente com células vazias (nunca 0), aviso de moeda, Descoberta com todas as páginas

## 4A. Coluna extra do Decidir (backend)

- [ ] 4A.1 `PUT /api/combos/discovery/sweeps/{id}/reference-column {reference_symbol | null}` (admin, dono): `null` desativa; referência já gravada na varredura reativa sem recalcular (200); nova cria a coluna e enfileira o job (202). `GET …/reference-column` (estado e progresso) e `POST …/reference-column/retry`
- [ ] 4A.2 Job no worker da fila de lotes (#1120): coleta a referência se faltar (decisão 6), congela uma amostra 1d da referência (papel `benchmark`, união das janelas), e, em lotes de 25, regenera os trades de cada candidato a partir do `snapshot_id` dele (mesmo caminho da promoção) e grava `benchmark_comparison.compute` com dono `discovery_result`; progresso gravado; trocar de referência cancela o job anterior
- [ ] 4A.3 Estados sem número: `insufficient_sample` = "Sem amostra" (não calcula), amostra do candidato vencida = "Sem comparação · Amostra do candidato vencida em <data>", `no_overlap`, `short_overlap`, `no_history`; falha na coleta não grava e mantém a coluna anterior
- [ ] 4A.4 `GET …/leaderboard`: `reference_column` (referência, estado, contagens válidas/curtas/sem período comum, aviso de moeda presente, gravada em, versão da amostra) e `reference_comparison` por linha da página (junção, sem cálculo); `metric` continua só `calmar_ratio | delta_cagr_vs_bh`; ordem, rank e elegibilidade iguais com e sem coluna
- [ ] 4A.5 Fixação das amostras (referência e candidatos) enquanto a coluna estiver ativa; GC em 30 dias depois de desativar
- [ ] 4A.6 Testes: BTC/USDT × SPY no Decidir igual ao resultado (02/01/2019, 0 trades fora, aviso de moeda); PENGU/USDT 14 dias = `short_overlap`; CRCL contra varredura até 31/12/2024 = `no_overlap` em todos; ordem e rank idênticos antes e depois; leitura e exportação não chamam o cálculo nem a coleta; reativar referência gravada não recalcula; falha na coleta não grava; outra varredura começa sem coluna; outro usuário não vê a coluna

## 5. Frontend: tela do resultado

- [ ] 5.1 `components/results/BenchmarkComparison.tsx` na `ComboResultsPage`, entre a análise e `DataExecutionBlock`, na moldura `r19-data`, com os estados válido, gravando/coletando, insuficiente (sem período comum e período comum curto, cada um com a sua frase de apoio), falha na coleta e não registrada; sem números no DOM durante gravando/coletando; no favorito, a linha de gravação diz que a comparação é refeita só no refresh do backtest; subtítulo "÷ 365,25" (layout de `index.html` e `favorite.html`)
- [ ] 5.2 Seletor modal de escolha única sobre o catálogo (`AssetPicker` em modo único ou componente irmão): busca, filtro de classe, "Próprio ativo · Padrão", histórico, aviso antes da escolha ("Sem período comum com esta estratégia" / "Só N dias em comum com esta estratégia", sem coletar e sem bloquear), marcados desabilitados com estado e motivo do catálogo (`aria-describedby`), filtros de classe com 44 px no toque, foco preso, Esc, retorno do foco, 44 px, tela cheia no celular
- [ ] 5.3 Troca grava via API e atualiza `history.state` (`replace`), para recarregar manter a escolha; aberta de Favoritos, grava no favorito
- [ ] 5.4 "Salvar nos Favoritos" envia `benchmark_comparison_id`
- [ ] 5.5 "Exportar para Excel" usa `authFetch` e envia contexto e `benchmark_comparison_id`
- [ ] 5.6 Testes de componente (Vitest): estados, texto do aviso com as duas moedas, nenhum "%" nem zero no insuficiente (os dois motivos), aviso antes da escolha, marcado desabilitado, foco do diálogo

## 6. Frontend: Favoritos e Descoberta

- [ ] 6.1 `FavoritesDashboard`: "Ref.: <ativo> · comparação gravada <data>" na linha e no cartão quando não é o próprio ativo (inclusive referência de outra classe, como SPY Trend com BTC/USDT); "Exportar" baixa de `/api/favorites/export` com os ids da lista filtrada; sai o SheetJS dessa tela
- [ ] 6.2 `DiscoveryPage` (Decidir): frase "Referência do ranking…" (ordem, rank e elegibilidade não mudam com a coluna extra) e "Exportar planilha" (44 px, status `polite`, desabilitado sem linhas ou carregando) com os filtros atuais
- [ ] 6.2a Faixa "Coluna extra" (layout de `discovery.html`): padrão "Nenhuma" + "Comparar com outra referência" (44 px); com referência: ativo, classe, moeda, "Retorno de preço, sem dividendos" em ação/ETF, "A coluna não muda a ordem…", resumo de candidatos com e sem comparação, aviso de moeda quando houver, linha de gravação, progresso (`role=status`) e falha (`role=alert`, "Tentar de novo" 44 px); consulta do progresso enquanto `collecting | computing`
- [ ] 6.2b Seletor do resultado reaproveitado (mesmo componente do 5.2) com título "Escolher referência da coluna extra", "Próprio ativo · Padrão · Sem coluna extra" e aviso contado sobre os candidatos ("Sem período comum com nenhum candidato desta varredura" / "N candidato(s) com período comum curto")
- [ ] 6.2c Coluna "Contra <ativo>" antes de "Ação": Δ p.p. com tom, CAGR da referência, período comum, "USDT tratado como USD" na linha, "Sem comparação" + motivo, "Calculando…" sem número, "Sem amostra"; no cartão móvel (< 720 px) a célula ocupa a largura com o rótulo; nenhuma opção nova em "Ordenar por"
- [ ] 6.3 Testes de componente: Ref. só fora do padrão; exportação com filtros; ranking e ordem intocados; coluna extra (estados, sem número em calculando/insuficiente, aviso de moeda só na linha com moedas diferentes, remoção com Próprio ativo)

## 7. Playwright e verificação do card

- [ ] 7.1 E2E com API simulada a 1440 e 390: NVDA x SPY; ETF x próprio ativo; BTC/USDT x próprio ativo e x SPY (aviso e período comum); insuficiente com motivo (sem período comum e período comum curto); aviso antes da escolha e marcado desabilitado no seletor; falha na coleta; troca no favorito gravada e reaberta; seletor (Tab, Shift+Tab, Esc, foco)
- [ ] 7.2 E2E das planilhas: as três baixam com as colunas de contexto; favorito antigo de cripto com "deduzido" e "não registrado"; Descoberta com o próprio ativo
- [ ] 7.3 Regressão: Descoberta e lote seguem ordenando pelo próprio ativo (Δ e rank iguais antes e depois de trocar a referência de um favorito promovido e de escolher a coluna extra)
- [ ] 7.3a E2E Playwright do Decidir com API simulada a 1440 e 390 (toque): abrir o seletor (foco, Tab/Shift+Tab presos, Esc devolve o foco, filtros 44 px, WAVES/USDT desabilitado, avisos antes da escolha); escolher SPY (calculando sem número, coluna nos 5 candidatos, ordem e rank idênticos, aviso de moeda só em cripto, PENGU/USDT período curto com motivo); recarregar mantém a coluna gravada; QQQ com coleta; CRCL sem período comum em todos; falha na coleta e "Tentar de novo"; voltar para Próprio ativo; planilha com as 13 colunas "(extra)" e sem elas no padrão
- [ ] 7.4 Verificação no DEV com dados reais: NVDA x SPY, um ETF x próprio ativo, BTC/USDT x próprio ativo e x SPY, referência sem histórico suficiente, troca num favorito saindo na planilha, favorito antigo de cripto exportando, coluna "Contra SPY" numa varredura real do Decidir (ordem igual, planilha com "(extra)")
