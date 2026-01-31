# Sequential Optimization - Tasks

## Backend Implementation
- [ ] Create `SequentialOptimizer` service class
- [ ] Implement stage execution logic with parameter locking
- [ ] Add stage result persistence (SQLite/JSON)
- [ ] Create API endpoints for sequential optimization
- [ ] Add job tracking for multi-stage optimization

## Frontend Implementation
- [ ] Create `SequentialOptimizationWizard` component
- [ ] Add optimization mode selector to `BacktestForm`
- [ ] Implement stage progress visualization
- [ ] Create `SequentialResults` component with stage breakdown
- [ ] Add "validate with grid search" option

## Testing
- [ ] Unit tests for `SequentialOptimizer`
- [ ] Integration tests for full sequential flow
- [ ] Manual testing with MACD on BTC/USDT
- [ ] Performance comparison vs grid search

## Documentation
- [ ] Update user guide with sequential optimization workflow
- [ ] Add examples for common strategies (MACD, RSI, Bollinger)
