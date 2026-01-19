# Tasks: Database-Driven Strategy Configuration

## Phase 1: Database Schema Enhancement ✅
- [ ] Add `optimization_schema` JSON column to `combo_templates` table
- [ ] Create migration script `add_optimization_schema.py`
- [ ] Test migration on clean database
- [ ] Test migration on database with existing templates

## Phase 2: Convert Pre-built Strategies to JSON
- [ ] Convert `MultiMaCrossoverCombo` to JSON seed data
- [ ] Convert `EmaRsiCombo` to JSON seed data
- [ ] Convert `EmaMacdVolumeCombo` to JSON seed data
- [ ] Convert `BollingerRsiAdxCombo` to JSON seed data
- [ ] Convert `VolumeAtrBreakoutCombo` to JSON seed data
- [ ] Convert `EmaRsiFibonacciCombo` to JSON seed data
- [ ] Create seed script `seed_prebuilt_strategies.py`
- [ ] Verify all 6 strategies inserted correctly

## Phase 3: Update Service Layer
- [ ] Modify `ComboService.list_templates()` to query DB only
- [ ] Remove `PREBUILT_TEMPLATES` dictionary from `ComboService`
- [ ] Update `ComboService.get_template_metadata()` to read from DB
- [ ] Update `ComboService.get_strategy_instance()` to use DB data
- [ ] Modify `ComboOptimizer.generate_stages()` to read schema from DB
- [ ] Remove `get_optimization_schema()` method calls
- [ ] Update error handling for missing templates

## Phase 4: Remove Hard-coded Classes
- [ ] Delete `backend/app/strategies/combos/multi_ma_crossover.py`
- [ ] Delete `backend/app/strategies/combos/ema_rsi_combo.py`
- [ ] Delete `backend/app/strategies/combos/ema_macd_volume_combo.py`
- [ ] Delete `backend/app/strategies/combos/bollinger_rsi_adx_combo.py`
- [ ] Delete `backend/app/strategies/combos/volume_atr_breakout_combo.py`
- [ ] Delete `backend/app/strategies/combos/ema_rsi_fibonacci_combo.py`
- [ ] Update `backend/app/strategies/combos/__init__.py`
- [ ] Remove unused imports from `combo_service.py`

## Phase 5: Testing & Validation
- [ ] Run unit tests for `ComboService`
- [ ] Run integration tests for backtest flow
- [ ] Test optimization with DB schemas
- [ ] Verify all 6 pre-built strategies work
- [ ] Test custom template creation
- [ ] Test template deletion
- [ ] Performance test (ensure no slowdown)

## Phase 6: Documentation
- [ ] Update `COMBO_STRATEGIES_USER_GUIDE.md`
- [ ] Update `COMBO_TEMPLATES_REFERENCE.md`
- [ ] Update `COMBO_API_DOCUMENTATION.md`
- [ ] Add migration guide for existing deployments
- [ ] Update README with new architecture

## Summary
**Total Tasks**: 41
**Estimated Time**: 9 hours
**Risk Level**: Medium (requires careful migration)

## Dependencies
- Requires `add-indicator-combinations` to be complete
- Database backup recommended before migration

## Success Criteria
- All tests passing
- No Python strategy classes remain
- All 6 pre-built strategies work from database
- Documentation updated
