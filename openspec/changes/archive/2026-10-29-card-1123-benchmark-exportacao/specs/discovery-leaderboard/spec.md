## ADDED Requirements

### Requirement: Export the Decidir ranking as a spreadsheet

The Decidir header SHALL offer "Exportar planilha", which downloads from the server every candidate of the selected sweep that matches the current filters (class, symbol, timeframe, direction), across all pages, in the current sort order, with the global rank preserved. Each row SHALL carry today's leaderboard columns (rank global, candidate, template, timeframe, direction, Sharpe, Trades, Win%, Return, Max DD, Calmar, CAGR anualizado, B&H CAGR, Δ vs B&H, Profit Factor, GO/NO-GO, eligibility and reason) and all 22 shared context fields of `result-context-export`, with the same names and order. Período pedido SHALL be the sweep period, "CAGR da estratégia no período comum" SHALL be the persisted annualized CAGR, Fora do período comum SHALL be "nada", Situação da comparação SHALL be "Válida" and Comparação gravada em SHALL be the sweep completion time. Referência SHALL be "Próprio ativo (buy-and-hold, long-only)", Período comum SHALL be the persisted evidence window, and Versão da amostra SHALL be the persisted candle version and `snapshot_id`. A candidate whose evidence window is shorter than the minimum common period (30 calendar days) SHALL carry "Histórico insuficiente: Período comum de N dias: o mínimo é 30." in Situação da comparação and empty return, CAGR and difference context cells, while today's leaderboard columns keep their persisted values. The export SHALL NOT recompute any metric; returns derived for the context fields SHALL come only from the persisted CAGR and window. When an extra reference column is active and complete for the sweep, each row SHALL also carry, after the 22 context fields, the 13 extra columns of the recorded extra comparison: Referência (extra), Tipo de retorno da referência (extra), Período comum (extra), Fora do período comum (extra), Retorno da estratégia no período comum (extra), CAGR da estratégia no período comum (extra), Retorno da referência (extra), CAGR da referência (extra), Diferença de CAGR (p.p.) (extra), Situação da comparação (extra), Aviso de moeda (extra), Versão da amostra da referência (extra) and Comparação gravada em (extra), and the "Legenda" sheet SHALL explain "(extra)". The button SHALL be at least 44 px high, announce the download in a polite live region and stay disabled while the leaderboard loads or has no rows.

#### Scenario: Export a filtered multiclass ranking

- **WHEN** the operator filters Classe = Ação on a sweep with crypto, ação and ETF and clicks "Exportar planilha"
- **THEN** the workbook has one row per ação candidate of every page, ordered as the leaderboard with the global ranks
- **AND** the currency of each row is USD and Referência is the own asset

#### Scenario: Empty recorte

- **WHEN** the current filters leave no candidate
- **THEN** "Exportar planilha" is disabled

#### Scenario: Export with SPY as extra reference

- **WHEN** the sweep has the extra column "Contra SPY" recorded and Alan exports
- **THEN** each row keeps "Próprio ativo (buy-and-hold, long-only)" in Referência and carries "SPY · ETF · USD" in Referência (extra)
- **AND** a BTC/USDT row carries "USDT tratado como USD, sem conversão. A comparação é só em percentual." in Aviso de moeda (extra)
- **AND** a candidate with a 14-day common period carries "Histórico insuficiente: Período comum de 14 dias: o mínimo é 30." in Situação da comparação (extra) and empty extra return, CAGR and difference cells

#### Scenario: Candidate window below the minimum

- **WHEN** a PENGU/USDT candidate has an evidence window of 14 days and Alan exports
- **THEN** its Situação da comparação is "Histórico insuficiente: Período comum de 14 dias: o mínimo é 30." and its context return and CAGR cells are empty

### Requirement: Discovery ranking keeps the own-asset reference

The Decidir ranking, its sort options (Calmar and CAGR vs B&H), its global ranks, its B&H CAGR and Δ values and its eligibility SHALL keep using only the buy-and-hold of the candidate's own asset over the persisted evidence window. Neither a reference chosen on a result or favorite nor the Decidir extra reference column SHALL affect any of them, and the extra column SHALL NOT become a sort option or a filter. The Decidir header SHALL state "Referência do ranking: o próprio ativo (buy-and-hold, long-only)" and that the order, the global rank and the eligibility do not change with the extra column.

#### Scenario: Reference chosen elsewhere does not move the ranking

- **WHEN** a favorite promoted from this sweep has its reference switched to SPY
- **THEN** the leaderboard order, ranks, B&H CAGR and Δ of the sweep stay unchanged

#### Scenario: Extra column does not move the ranking

- **WHEN** Alan chooses SPY as extra reference on a sweep sorted by CAGR vs B&H whose "Contra SPY" values are not in rank order
- **THEN** the candidates keep the same order and global ranks as before the choice
- **AND** "Ordenar por" still offers only Calmar and CAGR vs B&H

### Requirement: Extra reference column in the Decidir

After a sweep is completed, the Decidir SHALL offer "Comparar com outra referência", which opens the same single-choice reference selector as the result screen (search, class filter with 44 px buttons on touch, "Próprio ativo · Padrão" first, marked catalog assets disabled with the catalog state and reason linked by `aria-describedby`, focus trap, Esc closing and returning focus to the trigger). The default SHALL be "Próprio ativo" with no extra column. Before the choice, an option SHALL say, from stored catalog history and the candidates' windows and without collecting, "Sem período comum com nenhum candidato desta varredura" when no candidate overlaps it and how many candidates would have a short common period. Choosing an asset SHALL show a column "Contra <asset>" on every candidate of the sweep, before "Ação", whose cell shows, for the candidate's common period, the CAGR difference in percentage points, the reference CAGR and the common period, computed with the same rules as the result's "Comparação com referência" (common period snapped to the reference calendar, compound of the closed trades inside it, both CAGRs with calendar days ÷ 365.25, long-only). A cell whose strategy and reference currencies differ SHALL show "USDT tratado como USD" as visible text with an icon. A cell with no common period, a common period below the minimum, or an expired candidate sample SHALL show "Sem comparação" and the reason, never a number or zero. The strip SHALL show the reference, "Retorno de preço, sem dividendos" for an ação or ETF reference, a count of candidates with and without comparison, the currency warning when any row has it, and the recording line. On narrow screens the cell SHALL appear in each candidate card with the "Contra <asset>" label. Choosing "Próprio ativo" SHALL remove the column.

#### Scenario: SPY column on a multiclass sweep

- **WHEN** Alan chooses SPY on a sweep with BTC/USDT, NVDA, SOL/USDT, SPY and PENGU/USDT (14-day window)
- **THEN** all five candidates show a "Contra SPY" cell
- **AND** BTC/USDT shows "+66,8 p.p.", "SPY +15,25% a.a.", "2 jan. 2019 – 31 dez. 2024" and "USDT tratado como USD", in the pt-BR format of the rest of the Decidir
- **AND** the column header hint says "Δ CAGR · período comum · não ordena"
- **AND** NVDA shows its difference without a currency warning
- **AND** PENGU/USDT shows "Sem comparação" and "Período comum de 14 dias: o mínimo é 30." without any percentage

#### Scenario: Reference with no common period with the sweep

- **WHEN** the sweep ends on 31/12/2024 and Alan chooses CRCL, whose history starts on 05/06/2025
- **THEN** the selector warned "Sem período comum com nenhum candidato desta varredura" before the choice
- **AND** every cell shows "Sem comparação" and "Sem período comum com CRCL." without numbers
- **AND** the strip says that no candidate has a common period with CRCL and why

#### Scenario: Back to the own asset

- **WHEN** Alan chooses "Próprio ativo" in the selector
- **THEN** the "Contra" column disappears and the spreadsheet has no "(extra)" columns

### Requirement: Extra column recorded once per sweep and user

The server SHALL compute the extra column once per choice, for all candidates of the sweep (not only the visible page), in a background job of the batch queue, regenerating each candidate's trades only from its frozen sample (or, for a crypto candidate that never saved a sample, by the old path from the local candle cache, accepted only when the redone metrics match the ones the sweep recorded) and using a frozen daily sample of the reference; no new candidate data SHALL be fetched. The choice SHALL be recorded per sweep and per user, with the reference sample version and the recording time; each cell SHALL be a recorded comparison. Opening, reloading or exporting SHALL read the recorded column and SHALL NOT collect or recompute. Choosing again a reference already recorded for the sweep SHALL reactivate the recorded column without recomputing. While the reference is collected or the column computed, the strip SHALL show the progress in a polite live region and the cells SHALL show "Calculando…" without numbers. When the reference has no stored daily history, it SHALL be collected first ("Coletando histórico de <asset> na Binance…"); if the collection fails with nothing stored, nothing SHALL be recorded, the previous column (or none) SHALL stay, and an alert SHALL give the reason with a "Tentar de novo" button of at least 44 px. A candidate without metrics (`insufficient_sample`) SHALL show "Sem amostra" and SHALL NOT be computed.

#### Scenario: Reload keeps the recorded column

- **WHEN** Alan chose SPY on a sweep and reloads the Decidir
- **THEN** the "Contra SPY" column shows the same recorded values without a computing state
- **AND** the strip says when it was recorded and that opening, reloading or exporting again does not recompute

#### Scenario: QQQ collected on choice

- **WHEN** Alan chooses QQQ and the catalog has no stored QQQ history
- **THEN** the strip shows "Coletando histórico de QQQ na Binance…" and then the computing progress, with no numbers in the cells
- **AND** the column "Contra QQQ" appears when the column is recorded

#### Scenario: Collection fails

- **WHEN** the QQQ collection fails while the column shows CRCL
- **THEN** nothing is recorded, the column keeps CRCL and an alert offers "Tentar de novo"

#### Scenario: Expired candidate sample

- **WHEN** the frozen sample of a candidate expired before the extra column was chosen
- **THEN** its cell shows "Sem comparação" and "Amostra do candidato vencida em <data>." without any number, and nothing new is fetched
- **AND** the selector warned before the choice how many candidates have an expired sample (and, when all of them, to run the sweep again)
- **AND** the strip summary counts it as "(amostra vencida)"; while the column is active the other candidates show "amostra guardada pela coluna extra"

#### Scenario: Crypto candidate without a saved sample

- **WHEN** a crypto candidate of a sweep run without the durable sample (the old path: no `snapshot_id`) is in the extra column
- **THEN** the job redoes its trades by the old path with the same window (the combination's; else the sweep's; else, for older sweeps that asked for a relative period without recording dates, the smallest window from the first training candle the result recorded whose train/holdout split ends at the last training candle it recorded, so the training segment is the same), parameters, direction, frozen template and `split_train_ratio`, reading the candles and the 15m only from the local cache (no network, nothing written to the cache), whether or not the sweep recorded a candle version and whether or not its SHA-256 still matches
- **AND** it computes the cell normally, with the redone trades, only when the redone metrics match the ones recorded on the result, in the same unit and segment as the sweep (training segment of the split): same number of trades, win rate equal up to float rounding (1e-9), and CAGR within 0.0005 (half of the one decimal of percentage the Descoberta shows)
- **AND** when the metrics do not match, the cell shows "Sem comparação" and "Trades refeitos não batem com a varredura." (reason `sample_unavailable`, detail `metrics_mismatch`; the long text ends with "Rode a varredura de novo para comparar."); when the cache no longer has the candles it shows "Velas do candidato não estão mais guardadas." (`missing`), and when the sweep did not record a window or metrics to check against "Varredura sem dados para refazer os trades." (`unrecorded`); always without any number and never "vencida"; the spreadsheet carries "Sem comparação: <reason>" in "Situação da comparação (extra)"
- **AND** when redoing it fails for any other reason, the cell shows "Sem comparação" and "Trades do candidato não refeitos." (reason `regeneration_failed`), its long text is "Sem comparação: não foi possível refazer os trades do candidato com as velas guardadas no servidor." (never mentioning a sample, which never existed), and the spreadsheet carries "Sem comparação: Trades do candidato não refeitos." (never "Histórico insuficiente")
- **AND** the selector does not count it as an expired sample: a crypto candidate with a determinable window and the cache present is not a warning (the check happens in the job), and one that cannot be redone is counted as "N candidato(s) sem as velas da varredura"; when all candidates cannot be redone it warns "Todos os N candidatos sem as velas da varredura: rode a varredura de novo para comparar", and when every candidate is either expired or cannot be redone (some of each) it warns "Nenhum dos N candidatos tem amostra ou velas da varredura para refazer os trades: rode a varredura de novo para comparar"; the strip summary counts every such cell as "(sem os trades da varredura)"
- **AND** its row keeps "sem amostra guardada" and never says "amostra guardada pela coluna extra"

#### Scenario: Candidate without a recorded CAGR

- **WHEN** a candidate has metrics but no recorded CAGR (for example, a CAGR above the ranking ceiling) and is not `insufficient_sample`
- **THEN** it is not computed and, once the column is recorded, its cell shows "Sem comparação" and "Sem CAGR gravado do candidato." without any number (reason `no_cagr`), never "Calculando…"
- **AND** in the spreadsheet its "Referência (extra)" is the column's asset and "Situação da comparação (extra)" says "Sem comparação: o candidato não tem CAGR gravado."

#### Scenario: Promote with the extra column active

- **WHEN** Alan promotes a candidate whose "Contra SPY" cell is valid
- **THEN** the promotion says "Leva a comparação com SPY gravada" and the new favorite points to that recorded comparison (same reference, same sample, no recomputation)
- **AND** a candidate with "Sem comparação" is promoted with the default reference (own asset)

#### Scenario: Another sweep starts without a column

- **WHEN** Alan opens a different sweep in the Decidir
- **THEN** it shows "Coluna extra: Nenhuma" until he chooses a reference for that sweep
