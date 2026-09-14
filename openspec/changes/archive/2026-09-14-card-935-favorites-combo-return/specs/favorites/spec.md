## ADDED Requirements

### Requirement: Analysis summary uses the same compound the Favorites grid already shows

The Favorites panel already stores and renders `total_return` as compound return. When that RETURN is already visible on a row, opening `/combo/results` from that row SHALL render «Retorno total» with the same canonical large compound. The system MUST NOT treat a compound ratio whose absolute value is greater than 1 as if it were already a percent (that heuristic MAY remain valid for win rate and drawdown, which stay below 1 as ratios). Percentage-point fields (`total_return_pct`) MUST continue to mean points (98591,56 = +98.591,56%), not a second ×100.

#### Scenario: Grid points and analysis ratio resolve to the same large percent

- **WHEN** the grade reads percentage points 98591,56 (or ratio 985,91) for a filled Favorites row
- **THEN** RETURN on `/favorites` is the large compound (~+98.591%)
- **AND** «Retorno total» on the analysis of that same row is the same large compound
- **AND** the analysis MUST NOT show ~985,85%

#### Scenario: Small ratio stays a small percent on both screens

- **WHEN** a favorite metric payload contains compound ratio `total_return=0.35` (or points 35)
- **THEN** the Favorites page renders RETURN as ~+35%
- **AND** the analysis summary of that row also renders ~+35%
