## ADDED Requirements

### Requirement: Default reference is the asset's own buy-and-hold

Every combo/backtest result screen (`/combo/results`) SHALL show a "Comparação com referência" section directly below the strategy analysis. Without a choice, the reference SHALL be the buy-and-hold of the result's own asset over the same window, long-only even for a short strategy (labelled "buy-and-hold long-only" in that case). The server SHALL compute and record this default comparison when it returns an optimization or backtest result, and the result payload SHALL carry the recorded comparison.

#### Scenario: Fresh BTC/USDT result shows its own buy-and-hold

- **WHEN** Alan runs a BTC/USDT 1d combo and the result screen opens
- **THEN** the section shows "BTC/USDT (próprio ativo)" as the reference
- **AND** it shows strategy return, strategy CAGR, reference return, reference CAGR and the CAGR difference in percentage points over the common period
- **AND** no currency warning is shown

#### Scenario: ETF compared with its own asset

- **WHEN** the result is SPY 1d with no reference chosen
- **THEN** the reference is "SPY (próprio ativo)" and is labelled "retorno de preço, sem dividendos"

#### Scenario: Short strategy keeps a long-only reference

- **WHEN** the result is a short strategy
- **THEN** the reference label says "buy-and-hold long-only"

### Requirement: Choose another reference after running

The result screen SHALL offer "Trocar referência", which opens a single-choice selector of the asset catalog (crypto, ação and ETF) with search, class filter and "Próprio ativo" as the first option. Choosing an asset SHALL record a new comparison for that result, or for the favorite when the screen was opened from Favorites, replacing the previous choice. The choice SHALL NOT exist before running: no run form, batch form or Discovery sweep form SHALL gain a reference field (the Decidir extra column is chosen on a completed sweep). Marked or unavailable catalog assets SHALL be shown disabled with the catalog state and reason, linked to the option by `aria-describedby`, and SHALL NOT be selectable. Before the choice, an option whose stored history gives no common period with the strategy window SHALL say "Sem período comum com esta estratégia", and one whose common period would be below the minimum SHALL say "Só N dias em comum com esta estratégia"; the warning SHALL be visible text with an icon, SHALL come from the stored catalog history and the strategy window without collecting, and SHALL NOT block the choice. The class filter buttons SHALL be at least 44 px high on touch. The selector SHALL trap focus, close on Esc and return focus to "Trocar referência".

#### Scenario: Marked asset is disabled with the catalog reason

- **WHEN** the catalog marks WAVES/USDT as removed and Alan opens the selector
- **THEN** WAVES/USDT is listed disabled with "Removido" and the catalog reason
- **AND** clicking it does not change the choice and Tab skips it

#### Scenario: Warning before a choice without comparison

- **WHEN** a BTC/USDT result ends on 31/12/2024 and the selector lists CRCL, whose stored history starts on 05/06/2025
- **THEN** the CRCL option shows "Sem período comum com esta estratégia" before Alan chooses it
- **AND** CRCL can still be chosen

#### Scenario: NVDA compared with SPY

- **WHEN** Alan opens "Trocar referência" on an NVDA result, picks SPY and confirms "Usar referência"
- **THEN** the section shows SPY (ETF, USD) as the reference with its return, CAGR and the difference
- **AND** the section says the choice was recorded on this result, with date and time

#### Scenario: Choice on a favorite is recorded on the favorite

- **WHEN** Alan opens a favorite's analysis from Favorites and switches the reference to SPY
- **THEN** the favorite stores the new comparison and the section says "Gravada no favorito"
- **AND** reopening the analysis shows SPY with the same numbers
- **AND** the Favorites row shows "Ref.: SPY"

#### Scenario: Saving a result carries the choice

- **WHEN** Alan switches a fresh result to SPY and then saves it with "Salvar nos Favoritos"
- **THEN** the new favorite points to the same recorded comparison

#### Scenario: Promoted favorite inherits the Decidir cell

- **WHEN** a candidate with a valid "Contra SPY" cell is promoted from the Decidir
- **THEN** the favorite starts with that recorded comparison and its analysis shows SPY without computing on open

#### Scenario: Back to the own asset

- **WHEN** Alan picks "Próprio ativo" in the selector
- **THEN** the recorded choice returns to the own asset's buy-and-hold

#### Scenario: Nothing before running

- **WHEN** Alan opens the Combo run form, the batch form or the Discovery sweep form
- **THEN** none of them offers a reference choice

### Requirement: Collect the reference when it is chosen

When the chosen reference has no daily history stored, the server SHALL collect it from the existing Binance history (#1118) at the moment of the choice, before computing the comparison. The section SHALL show "Coletando histórico de <ativo> na Binance…" in a polite live region while it runs. No external source other than the existing catalog and Binance history SHALL be used.

#### Scenario: QQQ without stored history

- **WHEN** Alan picks QQQ and the catalog shows its history as on demand
- **THEN** the section shows the collecting state and then the comparison with QQQ

#### Scenario: Collection fails

- **WHEN** the collection of the chosen reference fails with nothing stored
- **THEN** nothing is recorded and the section keeps showing the previous recorded comparison
- **AND** an alert says the collection of that asset failed, with the reason, that nothing was recorded and which reference stays, with a "Tentar de novo" button of at least 44 px

### Requirement: Compare only over the common period

The comparison SHALL use only the period covered by both the strategy's effective window and the reference's daily history: start is the later of the two starts and end is the earlier of the two ends, snapped to dates with a reference daily close (UTC days for crypto, New York regular sessions for ação/ETF). The reference return SHALL be the last daily close in the common period divided by the first one, minus one, on split-adjusted prices for ação/ETF and the stored series for crypto. The strategy return SHALL be the compound return of the closed trades whose entry and exit both fall inside the common period. Both CAGRs SHALL use the same calendar-day count of the common period divided by 365.25. When the common period equals the strategy window, the strategy return SHALL equal the result's "Retorno total". The section and the spreadsheet SHALL show the common period and what was left out: the strategy dates outside it and the number of closed trades left out.

#### Scenario: BTC/USDT against SPY over a period starting on a New York holiday

- **WHEN** a BTC/USDT result covers 01/01/2019 to 31/12/2024 and Alan switches to SPY
- **THEN** the common period is 02/01/2019 to 31/12/2024
- **AND** the section says that 01/01/2019 (no session in New York) was left out with 0 trades

#### Scenario: Reference with shorter history

- **WHEN** the same result is compared with SOL/USDT, whose history starts on 11/08/2020
- **THEN** the common period starts on 11/08/2020
- **AND** the section lists 01/01/2019 to 10/08/2020 of the strategy and the closed trades of that range as left out
- **AND** the strategy return shown is the compound of the trades inside the common period, not the full "Retorno total"

### Requirement: Insufficient reference history shows the reason, never a number

When there is no daily history after collection, no common period, or a common period shorter than the minimum, the section SHALL show "Sem comparação" with the reason in plain text and SHALL NOT show return, CAGR or difference for either side, nor zero. The spreadsheet SHALL carry the same state and reason. The minimum common period SHALL be 30 calendar days. Each reason SHALL have its own supporting sentence: no common period asks for a reference with history in the strategy period; a common period below the minimum says that few days distort the annualized CAGR and asks for a reference with more history inside the strategy period.

#### Scenario: Reference that starts after the strategy ends

- **WHEN** a result ending on 31/12/2024 is compared with CRCL, whose history starts on 05/06/2025
- **THEN** the section shows "Sem comparação" and "CRCL tem histórico desde 05/06/2025, depois do fim da estratégia (31/12/2024). Não há período comum."
- **AND** no percentage and no "0,00%" appear in the section

#### Scenario: Common period too short

- **WHEN** the common period has fewer than 30 calendar days
- **THEN** the section shows "Sem comparação" and "Período comum de N dias: o mínimo é 30."
- **AND** the supporting sentence differs from the no-common-period one
- **AND** no percentage and no "0,00%" appear in the section

### Requirement: Different currencies are compared in percent with a visible warning

When the strategy currency and the reference currency differ (USDT for crypto, USD for ação and ETF), the comparison SHALL be in percent only and the section and the spreadsheet SHALL show "USDT tratado como USD, sem conversão. A comparação é só em percentual." The warning SHALL be visible text with an icon, not a tooltip, and SHALL NOT appear when the currencies match.

#### Scenario: BTC/USDT against SPY

- **WHEN** the reference of a BTC/USDT result is SPY
- **THEN** the warning is visible next to the comparison
- **AND** the spreadsheet column "Aviso de moeda" carries the same sentence

#### Scenario: NVDA against SPY

- **WHEN** the reference of an NVDA result is SPY
- **THEN** no currency warning appears

### Requirement: Ação and ETF references are price return

A reference of class ação or ETF SHALL be labelled "retorno de preço, sem dividendos" in the section and in the spreadsheet. No dividend or total-return series SHALL be used.

#### Scenario: SPY label

- **WHEN** SPY is the reference
- **THEN** the section shows "Retorno de preço, sem dividendos"

### Requirement: Recorded comparison, no hidden recalculation

Each comparison SHALL be recorded once, with the reference identity, the frozen daily sample of the reference (snapshot manifest with version label and content hash, pinned while a favorite points to it), the strategy window, the common period, what was left out, the numbers, the currency warning, the state and reason, and the recording time. Opening the screen again or exporting SHALL read the recorded comparison and SHALL NOT collect or recompute. A favorite's comparison SHALL be recomputed only when that favorite's backtest is refreshed, with the same chosen reference, and the new recording time SHALL be shown. On a favorite, the recording line SHALL say "Refeita só quando o backtest do favorito é atualizado, com a mesma referência." While a comparison is being recorded or collected, the section SHALL NOT render numbers of the new reference. A favorite with no recorded comparison SHALL show "Comparação não registrada" with "Comparar com o próprio ativo" and "Trocar referência", and SHALL NOT compute on open.

#### Scenario: Reopen after the reference history changed

- **WHEN** SPY receives new candles after the choice and Alan reopens the favorite analysis or exports again
- **THEN** the section and the spreadsheet show the same numbers, common period and sample version as recorded

#### Scenario: Favorite refresh recomputes with the same reference

- **WHEN** the favorite with reference SPY is refreshed by the daily backtest update
- **THEN** the comparison is recomputed with SPY over the new window and the section shows the new recording time
- **AND** the favorite's recording line already said it is redone only when the favorite's backtest is refreshed, with the same reference

#### Scenario: Old favorite without a recorded comparison

- **WHEN** Alan opens the analysis of a favorite saved before this change
- **THEN** the section shows "Comparação não registrada" and computes nothing until Alan acts

### Requirement: Discovery and batch ranking keep the own asset

The Discovery leaderboard and the batch ranking SHALL keep ranking by the difference against the own asset's buy-and-hold. A reference chosen on a favorite promoted from Discovery or created by a batch, or chosen for the Decidir extra column, SHALL NOT change any ranking, rank or eligibility. The Decidir extra column SHALL use the same comparison rules as this capability (common period, closed trades inside it, CAGR with calendar days ÷ 365.25, insufficient history without numbers, currency warning, price return) and is specified in `discovery-leaderboard`.

#### Scenario: Promoted favorite with SPY reference

- **WHEN** a Discovery-promoted favorite has its reference switched to SPY
- **THEN** the Discovery leaderboard still shows "B&H" and "Δ" against the own asset for that result

#### Scenario: Extra column uses the result rules

- **WHEN** a BTC/USDT candidate covering 01/01/2019 to 31/12/2024 gets the Decidir extra column against SPY
- **THEN** its common period is 02/01/2019 to 31/12/2024, as on the result screen, and the cell shows "USDT tratado como USD"
- **AND** its rank and its B&H and Δ against the own asset stay unchanged
