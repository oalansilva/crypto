## ADDED Requirements

### Requirement: New post-70/30 favorites show the complete chosen period on the catalog

The Favorites list, the compact refresh status, and the analysis opened from a row SHALL, for favorites **created after this card** by promote or Combo save following 70/30, render the complete chosen period and the metrics of that period. Favorites already stored with a training window SHALL keep their current period and numbers until a later save. The screen SHALL NOT place training and full-period numbers side by side on the list.

#### Scenario: New Discovery todo row on the list

- **WHEN** a newly promoted «todo» favorite after 70/30 is listed on `/favorites`
- **THEN** the Período cell is first candle → now
- **AND** RETURN / Sharpe / trades / win / Max DD are the full-period values
- **AND** that row SHALL NOT display 17/08/2017 → 24/12/2023

#### Scenario: Legacy training row stays

- **WHEN** an older favorite whose stored window is 17/08/2017 → 24/12/2023 is listed
- **THEN** Período remains 17/08/2017 → 24/12/2023
- **AND** its metrics remain the stored ones until someone saves again

#### Scenario: New Combo 2-year row is not all-history

- **WHEN** a Combo favorite saved after 70/30 with period 2 years is listed
- **THEN** Período is those 2 years complete
- **AND** it SHALL NOT show the asset's first candle as start
