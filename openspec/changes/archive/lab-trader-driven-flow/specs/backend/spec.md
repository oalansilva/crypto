# Spec: Lab Trader-Driven Flow (Backend)

**Capability:** backend  
**Type:** refactor  
**Change:** lab-trader-driven-flow

---

## MODIFIED Requirements

### Requirement: Rename graph function

**Description:** The system SHALL rename `build_cp7_graph` to `build_trader_dev_graph` to reflect new architecture.

**Files:** `backend/app/services/lab_graph.py`

#### Scenario: Function renamed
- **Given** código usa `build_cp7_graph()`
- **When** refactor aplicado
- **Then** função MUST be renamed to `build_trader_dev_graph()`

---

### Requirement: Create trader validation node

**Description:** The system SHALL create `trader_validation_node` to replace Validator persona.

**Files:** `backend/app/services/lab_graph.py`

#### Scenario: Trader validates result
- **Given** Dev finalizou com `ready_for_trader=true`
- **When** nó executado
- **Then** Trader MUST receive `strategy_draft` + Dev result
- **And** MUST decide approved/needs_adjustment/rejected

---

### Requirement: Update prompts

**Description:** The system SHALL create `TRADER_VALIDATION_PROMPT`, update `DEV_SENIOR_PROMPT`, and simplify `COORDINATOR_PROMPT`.

**Files:** `backend/app/services/lab_graph.py`

#### Scenario: Prompts are correct
- **Given** Trader validando
- **When** prompt enviado
- **Then** MUST instruct to compare with strategy_draft

---

## REMOVED Requirements

### Requirement: Remove Validator persona

**Description:** The system SHALL remove `persona="validator"` block from `implementation_node`.

**Files:** `backend/app/services/lab_graph.py`

#### Scenario: Validator removed
- **Given** código tem bloco validator
- **When** removido
- **Then** `VALIDATOR_PROMPT` MUST be deleted

---

## MODIFIED Requirements

### Requirement: Reconfigure graph edges

**Description:** The system SHALL update graph edges for Trader → Dev → Trader flow.

**Files:** `backend/app/services/lab_graph.py`

#### Scenario: Edges configured
- **Given** upstream aprovado
- **When** próximo nó avaliado
- **Then** MUST go to dev_implementation

---

## ADDED Requirements

### Requirement: Create template from strategy_draft

**Description:** The system SHALL implement function `_create_template_from_strategy_draft` to convert approved draft to custom template.

**Files:** `backend/app/routes/lab.py`

#### Scenario: Draft creates template
- **Given** strategy_draft aprovado
- **When** função chamada
- **Then** template custom MUST be created with name `lab_{run_id[:8]}_draft_{symbol}_{timeframe}`

---

### Requirement: Convert idea to logic

**Description:** The system SHALL provide helper `_convert_idea_to_logic` to translate free text to executable syntax.

**Files:** `backend/app/routes/lab.py`

#### Scenario: Text converted
- **Given** "RSI < 30 E preço > EMA(50)"
- **When** conversão executada
- **Then** MUST return "rsi < 30 AND close > ema"

---

### Requirement: Extract stop-loss

**Description:** The system SHALL provide helper `_extract_stop_loss_from_plan` to extract percentage from risk plan.

**Files:** `backend/app/routes/lab.py`

#### Scenario: Percentage extracted
- **Given** "stop-loss 3%"
- **When** extração executada
- **Then** MUST return 0.03

---

## MODIFIED Requirements

### Requirement: Update seed template selection

**Description:** The system SHALL prioritize strategy_draft in `_choose_seed_template` over alphabetical selection.

**Files:** `backend/app/routes/lab.py`

#### Scenario: Draft prioritized
- **Given** strategy_draft válido
- **When** escolha executada
- **Then** MUST create custom template (not alphabetical)

---

### Requirement: Include draft in context

**Description:** The function `_context_for_backtest` SHALL include strategy_draft in returned context.

**Files:** `backend/app/routes/lab.py`

#### Scenario: Context includes draft
- **Given** run com upstream.strategy_draft
- **When** contexto criado
- **Then** MUST include `strategy_draft`

---

### Requirement: Use new graph

**Description:** The function `_run_lab_autonomous` SHALL use `build_trader_dev_graph` instead of `build_cp7_graph`.

**Files:** `backend/app/routes/lab.py`

#### Scenario: New graph used
- **Given** Lab iniciado
- **When** graph importado
- **Then** MUST use build_trader_dev_graph
