## ADDED Requirements

### Requirement: One ranking with class, currency and conventions per row
The Decidir leaderboard and the Acompanhar partials SHALL list crypto, ação and ETF candidates in one list. Each row SHALL show a compact block in two logical lines: (1) asset, timeframe and direction, the class chip with the currency ("Cripto USDT", "Ação USD", "ETF USD") and the precision ("Precisão intrabar (15m)" or the amber "Precisão diária (<ano início>–<ano fim>)"); (2) the short conventions ("Binance Spot · 24/7 · 365 dias/ano" or "Binance Ações · NY · split · 252/ano") and the effective period "<início> – <fim>". The exact daily-precision stretch ("Precisão diária · sem 15m de <início> a <fim>") and the label "Período efetivo" SHALL be available on hover and to assistive technology, and the exact stretch SHALL appear in full in the promotion dialog, in "Por ativo" and in Favorites. Each group SHALL NOT break inside, and no line SHALL start or end with a separator or leave the currency alone. A row MUST NOT show two currencies. The ranking SHALL NOT sum or convert values between USD and USDT.

#### Scenario: Mixed sweep in Decidir
- **WHEN** the sweep with BTC/USDT, NVDA and SPY in 1d completes
- **THEN** the BTC/USDT row SHALL show "BTC/USDT · 1d · Long", "Cripto USDT" and "Precisão intrabar (15m)"
- **AND** the NVDA row SHALL show "Ação USD", the amber "Precisão diária (2003–2025)" with the exact stretch "sem 15m de 2 jan. 2003 a 31 dez. 2025" for assistive technology, "Binance Ações · NY · split · 252/ano" and "2 jan. 2003 – 23 out. 2026"

### Requirement: Ordering is common to every class
The existing ordering SHALL apply to all classes together: every GO above every NO-GO, then Calmar or CAGR vs Buy & Hold, then trades and id. The global rank SHALL be computed over all eligible results before filters. Filters MUST NOT renumber positions. Metrics are percentages or ratios with no currency.

#### Scenario: GO equity above NO-GO crypto
- **WHEN** NVDA is GO with Calmar 1.6 and a crypto pair is NO-GO with Calmar 2.0
- **THEN** NVDA SHALL rank above the crypto pair

### Requirement: Class filter in Decidir
The Decidir filters SHALL include **Classe**, before Símbolo, with "Todas (N)", "Cripto (N)", "Ações (N)" and "ETFs (N)", counted over the results of the sweep. An option with count 0 SHALL be disabled. If the chosen class has no candidate, the table SHALL show "Nenhum candidato de <classe> nesta varredura." with "Limpar filtros". The Classe select SHALL be at least 44 px tall below 768 px. Choosing a class SHALL keep the global ranks. "Limpar filtros" SHALL reset Classe with the others. The leaderboard API SHALL accept `asset_class` and return `class_counts`.

#### Scenario: Filter Ações
- **WHEN** the operator chooses "Ações (1)" in the mixed sweep
- **THEN** only NVDA SHALL remain, with its global rank 2, and "1 de 3 candidatos" SHALL be announced

#### Scenario: Class without candidates
- **WHEN** SPY failed and the sweep has no ETF result
- **THEN** the option "ETFs (0)" SHALL be disabled
- **AND** a class left with no candidate SHALL show "Nenhum candidato de ETF nesta varredura." with "Limpar filtros", never an empty table without a message

### Requirement: Costs and window per class in the header
The leaderboard header SHALL show the fee per class when the sweep has more than one class ("taxa por lado: cripto 0,075% · ação e ETF 0,10%"). The header SHALL show the real state of the sweep ("em execução", "pausada", "concluída", "cancelada", "falha parcial") and MUST NOT read "em execução" after the sweep ends. The window, candles and sample SHALL be shown per row instead of being taken from the first row. The costs recorded on each result (`fees_slippage`) SHALL use the fee of its class.

#### Scenario: Mixed header
- **WHEN** the Decidir shows the mixed sweep
- **THEN** the header SHALL read "taxa por lado: cripto 0,075% · ação e ETF 0,10% · slippage do timeframe"

### Requirement: Promotion shows the identity of the execution
The promotion dialog SHALL show, besides today's identity and risk summary, the class and currency, conventions, precision, effective window, sample version (short `snapshot_id`, kept while the favorite exists) and direction of the candidate. For ação and ETF the title SHALL be "Promover a favorito". The destination SHALL be "Favoritos · sem nível de estrela", with "Monitor, Telegram e Revalidar: ainda não para ações e ETFs." For crypto the dialog SHALL stay "Promover a favorito tier 3" with "Tier 3 · observação".

#### Scenario: Promote NVDA
- **WHEN** the operator opens Promover on the NVDA row
- **THEN** the dialog SHALL show "Ação · USD", the conventions, the daily-precision mark, the effective window, "Amostra <id8>" and "Long", and the destination "Favoritos · sem nível de estrela"
- **AND** after confirming, the row SHALL show "Favorito · sem estrela" and a link to Favoritos

### Requirement: Promoted favorite keeps the identity of the execution
A favorite promoted from the Discovery SHALL store `parameters.data_source` and `parameters.direction`, the effective window, `snapshot_id` (pinned), and in `metrics` the keys `analysis_asset`, `analysis_execution`, `analysis_conventions` and `data_provenance`, besides the discovery provenance of today. Favorites SHALL then show class, currency, precision, conventions, effective period and limitations with the rendering of #1120, with no Discovery-specific change. Uniqueness SHALL use `lock_and_find_duplicate` with `data_source` and `asset` (contract with #1122).

#### Scenario: NVDA in Favorites
- **WHEN** NVDA is promoted from the mixed sweep
- **THEN** Favorites SHALL list NVDA with "Ação · USD", the daily-precision mark, "Binance Ações · NY · split · 252/ano", the effective period and "Limitações e origem"
