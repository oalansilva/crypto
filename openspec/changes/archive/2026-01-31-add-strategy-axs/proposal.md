# Change: Add ESTRATEGIAAXS Strategy

## Why
The user requested the addition of a custom trading strategy based on a Pine Script named "ESTRATEGIAAXS".
This strategy utilizes EMA and SMA crossovers to determine buy and sell signals.

## What Changes
- Add `ESTRATEGIAAXS` to the list of available strategies.
- Implement the strategy logic in the backend:
    - EMA (Short, default 6)
    - SMA (Long, default 38)
    - SMA (Intermediate, default 21)
    - Buy Logic: (Short > Long) AND (Crossover(Short, Long) OR Crossover(Short, Intermediate))
    - Sell Logic: Crossunder(Short, Intermediate).
    - **Integration**: Ensure compatibility with standard Stop Loss/Take Profit mechanisms and Parameter Optimization (Grid Search).
- **Frontend**: Implement **Dynamic Parameter Loading** where the interface fetches and renders parameters based on the selected strategy's metadata from the backend.
- Ensure **ESTRATEGIAAXS** parameters (EMA Short, SMA Long, SMA Intermediate) are correctly exposed in the metadata and rendered dynamically on:
    - `/optimize/parameters` (Parameter Optimization)
    - `/optimize/risk` (Risk Management Optimization)
- Add visualization for the 3 moving averages.

## Impact
- Affected specs: `strategy-enablement`
- Affected code:
    - Backend: Strategy factory/registry, new Strategy class.
    - Frontend: Strategy selection, parameter form.
