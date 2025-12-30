# Tarefas: Armazenamento Incremental de Dados

## Phase 1: Foundations (Backend)
- [ ] Add `pyarrow` to requirements (if needed) or verify environment support
- [ ] Create `src/data/incremental_loader.py`
  - [ ] Implement `load_local_data(symbol, timeframe)` -> DataFrame
  - [ ] Implement `save_data(df, symbol, timeframe)` -> Parquet
  - [ ] Implement `fetch_and_update(symbol, timeframe)` logic

## Phase 2: Refactoring
- [ ] Update `BacktestService` to instantiate `IncrementalLoader` instead of `CCXTLoader`
- [ ] Remove legacy `CCXTLoader` (or keep as fallback/deprecated)

## Phase 3: Verification
- [ ] Create unit test for Incremental Loader
  - [ ] Test fresh download
  - [ ] Test incremental update (append)
  - [ ] Test slice retrieval
- [ ] Verify performance (Parquet load speed)
