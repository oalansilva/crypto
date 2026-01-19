# Tasks: Database-Driven Strategy Configuration

## Phase 1: Database Schema Enhancement ✅ COMPLETE
- [x] Add `optimization_schema` JSON column to `combo_templates` table
- [x] Create migration script `add_optimization_schema.py`
- [x] Test migration on clean database
- [x] Test migration on database with existing templates

## Phase 2: Convert Pre-built Strategies to JSON ✅ COMPLETE
- [x] Convert `MultiMaCrossoverCombo` to JSON seed data
- [x] Convert `EmaRsiCombo` to JSON seed data
- [x] Convert `EmaMacdVolumeCombo` to JSON seed data
- [x] Convert `BollingerRsiAdxCombo` to JSON seed data
- [x] Convert `VolumeAtrBreakoutCombo` to JSON seed data
- [x] Convert `EmaRsiFibonacciCombo` to JSON seed data
- [x] Create seed script `seed_prebuilt_strategies.py`
- [x] Verify all 6 strategies inserted correctly

## Phase 3: Update Service Layer ✅ COMPLETE
- [x] Modify `ComboService.list_templates()` to query DB only
- [x] Remove `PREBUILT_TEMPLATES` dictionary from `ComboService`
- [x] Update `ComboService.get_template_metadata()` to read from DB
- [x] Update `ComboService.get_strategy_instance()` to use DB data
- [x] Modify `ComboOptimizer.generate_stages()` to read schema from DB
- [x] Remove `get_optimization_schema()` method calls
- [x] Update error handling for missing templates

## Phase 4: Remove Hard-coded Classes ✅ COMPLETE
- [x] Delete `backend/app/strategies/combos/multi_ma_crossover.py`
- [x] Delete `backend/app/strategies/combos/ema_rsi_combo.py`
- [x] Delete `backend/app/strategies/combos/ema_macd_volume_combo.py`
- [x] Delete `backend/app/strategies/combos/bollinger_rsi_adx_combo.py`
- [x] Delete `backend/app/strategies/combos/volume_atr_breakout_combo.py`
- [x] Delete `backend/app/strategies/combos/ema_rsi_fibonacci_combo.py`
- [x] Update `backend/app/strategies/combos/__init__.py`
- [x] Remove unused imports from `combo_service.py`

## Phase 5: Testing & Validation ✅ COMPLETE
- [x] Run unit tests for `ComboService`
- [x] Run integration tests for backtest flow
- [x] Test optimization with DB schemas
- [x] Verify all 6 pre-built strategies work
- [x] Test custom template creation
- [x] Test template deletion
- [x] Performance test (ensure no slowdown)

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
