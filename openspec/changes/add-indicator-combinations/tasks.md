# Implementation Tasks

## Phase 1: Backend - Core Combo Strategy System (ISOLATED)
- [ ] Create new isolated directory: `backend/app/strategies/combos/`
- [ ] Create `ComboStrategy` base class in `backend/app/strategies/combos/combo_strategy.py`
  - [ ] Support multiple indicator configurations
  - [ ] Implement flexible entry/exit logic evaluation
  - [ ] Handle AND/OR condition combinations
  - [ ] **NO CHANGES to existing DynamicStrategy**
- [ ] Create pre-built combo strategy templates in `combos/` directory
  - [ ] `MultiMaCrossoverCombo` - Multi-MA Crossover (like CRUZAMENTOMEDIAS)
  - [ ] `EmaRsiCombo` - Trend + Momentum
  - [ ] `EmaMacdVolumeCombo` - Trend + Momentum + Confirmation
  - [ ] `EmaPullbackCombo` - Pullback in Trend (EMA + RSI + Fibonacci)
  - [ ] `BreakoutCombo` - Breakout (Volume + ATR)
  - [ ] `BollingerRsiAdxCombo` - Statistical Combo
- [ ] Create `backend/app/schemas/combo_params.py` (NEW FILE)
  - [ ] Define parameter schemas for each combo template
  - [ ] Include optimization ranges for all parameters
  - [ ] **NO CHANGES to existing indicator_params.py**
- [ ] Create `backend/app/services/combo_service.py` (NEW FILE)
  - [ ] Isolated service for combo backtests
  - [ ] Reuses SequentialOptimizer for optimization
  - [ ] **NO CHANGES to existing BacktestService**
- [ ] Create 4 example custom templates (pre-saved)
  - [ ] "Example: CRUZAMENTOMEDIAS" - EMA(3) + SMA(37) + SMA(32) - existing strategy as combo
  - [ ] "Example: Scalping EMA 5/13" - EMA(5) + EMA(13) for scalping
  - [ ] "Example: Swing RSI Divergence" - RSI(14) + Price divergence logic
  - [ ] "Example: Breakout with Volume" - Price breakout + Volume confirmation
  - [ ] Store in database/config as user-created templates
- [ ] Create database migration for combo_templates table
  - [ ] Add `combo_templates` table to SQLite schema
  - [ ] Columns: id, name, description, is_example, is_prebuilt, template_data (JSON), created_at, updated_at
  - [ ] Seed pre-built and example templates

## Phase 2: Backend - API Integration (NEW ISOLATED ENDPOINTS)
- [ ] Create `backend/app/routes/combo_routes.py` (NEW FILE)
  - [ ] `GET /api/combos/templates` - List available combo templates
  - [ ] `GET /api/combos/meta/:template` - Get template parameter schema
  - [ ] `POST /api/combos/backtest` - Execute combo backtest
  - [ ] `POST /api/combos/optimize` - Run sequential optimization for combos
  - [ ] **NO CHANGES to existing routes (backtest.py, sequential_optimization.py)**
- [ ] Register new routes in main app
- [ ] Update chart data generation to support multiple indicators
  - [ ] Extend existing chart logic (backward compatible)

## Phase 3: Frontend - UI Components (NEW ISOLATED PAGES)
- [ ] Create new frontend routes (ISOLATED from existing pages)
  - [ ] `/combo/select` - Combo template selection page
  - [ ] `/combo/configure` - Combo parameter configuration page
  - [ ] `/combo/optimize` - Sequential optimization page for combos
  - [ ] `/combo/results` - Results page with multiple indicators
  - [ ] **NO CHANGES to existing pages (/optimize/parameters, /backtest)**
- [ ] Create combo-specific components
  - [ ] `ComboTemplateSelector.jsx` - Template selection UI
  - [ ] `ComboParameterForm.jsx` - Parameter configuration with Min/Max/Step inputs
  - [ ] `ComboOptimizationView.jsx` - Sequential optimization progress
  - [ ] `ComboResultsChart.jsx` - Chart with multiple indicator lines
  - [ ] `CustomComboBuilder.jsx` - Visual builder for creating custom combos
    - [ ] Indicator selection dropdown
    - [ ] Alias assignment input
    - [ ] Parameter configuration
    - [ ] Entry/Exit logic builder (simple text or visual)
    - [ ] Save template functionality
- [ ] Add navigation link to combo pages
  - [ ] Add "Combo Strategies" menu item
  - [ ] Add "Create Custom Combo" menu item

## Phase 4: Testing & Validation
- [ ] Create unit tests for `ComboStrategy` class
- [ ] Test each pre-built combo template
- [ ] Verify parameter optimization works for combos
- [ ] Test chart visualization with multiple indicators
- [ ] Performance testing (ensure no significant slowdown)
- [ ] End-to-end testing of complete workflow

## Phase 5: Documentation
- [ ] Update user documentation with combo strategy examples
- [ ] Document each pre-built combo template
- [ ] Add examples of custom combo creation
- [ ] Update API documentation
