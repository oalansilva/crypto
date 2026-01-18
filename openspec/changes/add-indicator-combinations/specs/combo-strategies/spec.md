# combo-strategies Specification

## Purpose
Enable users to create and backtest trading strategies that combine multiple indicators (including multiple instances of the same indicator) with flexible logic, supporting professional trading patterns like multi-MA crossovers, trend following with momentum confirmation, pullback entries, and breakout validation.

## ADDED Requirements

### Requirement: Select Combo Strategy Template
The strategy selection UI SHALL display a "Combo Strategies" section with pre-built templates.
The system MUST provide at least 6 combo templates: Multi-MA Crossover, EMA+RSI, EMA+MACD+Volume, EMA+RSI+Fibonacci, Volume+ATR, and Bollinger+RSI+ADX.
Each template MUST show a description of its purpose and component indicators.

#### Scenario: User Selects EMA+RSI Combo
- GIVEN the user is on the Custom Backtest page
- WHEN the user clicks on "EMA + RSI (Trend + Momentum)" combo template
- THEN the strategy is selected
- AND parameter fields for EMA Fast, EMA Slow, RSI Period, RSI Min, and RSI Max are displayed
- AND default values are shown (EMA Fast=9, EMA Slow=21, RSI Period=14, RSI Min=30, RSI Max=50)

### Requirement: Configure Combo Strategy Parameters
The parameter form SHALL group parameters by indicator.
Each parameter group MUST have a clear label indicating which indicator it belongs to.
All parameters MUST support optimization ranges for grid search.

#### Scenario: Configure EMA+RSI Parameters
- GIVEN the user has selected the EMA+RSI combo template
- WHEN the user views the parameter form
- THEN parameters are grouped under "EMA Settings" and "RSI Settings" headers
- AND each parameter shows its default value and optimization range
- AND the user can modify any parameter value
- AND the user can enable/disable optimization for each parameter

### Requirement: Support Multi-Instance Indicators with Aliases
The combo strategy system SHALL support multiple instances of the same indicator type.
Each indicator instance MUST have a unique alias for identification in logic expressions.
The system MUST resolve aliases to actual column names during signal generation.

#### Scenario: Configure Multi-MA Crossover Strategy
- GIVEN the user selects the "Multi-MA Crossover" combo template
- WHEN the user views the parameter form
- THEN three moving average parameters are displayed: "Fast EMA", "Long SMA", and "Intermediate SMA"
- AND each has its own length parameter (default: 3, 37, 32)
- AND the entry logic uses aliases: "(fast > long) AND (crossover(fast, long) OR crossover(fast, inter))"
- AND the system resolves "fast" to the EMA_3 column, "long" to SMA_37, "inter" to SMA_32

### Requirement: Create Custom Combo via Visual Builder
The system SHALL provide a visual interface for creating custom combo strategies.
Users MUST be able to select indicators from a list without writing code.
Users MUST be able to configure parameters for each indicator.
Users MUST be able to assign aliases to each indicator instance.
Users MUST be able to save custom combos with a name and description.
Saved custom combos SHALL appear alongside pre-built templates.

#### Scenario: Create and Save Custom EMA + RSI Combo
- GIVEN the user is on the "Create Custom Combo" page
- WHEN the user clicks "Add Indicator" and selects "EMA"
- AND assigns alias "fast" and sets period to 9
- AND clicks "Add Indicator" again and selects "EMA"
- AND assigns alias "slow" and sets period to 21
- AND clicks "Add Indicator" and selects "RSI"
- AND sets RSI period to 14
- AND configures entry logic: "(close > fast) AND (close > slow) AND (RSI_14 > 30 AND RSI_14 < 50)"
- AND configures exit logic: "(RSI_14 > 70) OR (close < fast)"
- AND clicks "Save Template" with name "My EMA RSI Strategy"
- THEN the custom combo is saved to user's template library
- AND appears in the template selection list
- AND can be selected and used like pre-built templates

### Requirement: Provide Example Custom Templates
The system SHALL include at least 4 example custom templates created via the visual builder.
These example templates SHALL demonstrate different combinations and logic patterns.
Example templates SHALL be clearly marked as "Examples" in the template list.
Users SHALL be able to clone example templates to create their own variations.

#### Scenario: View and Clone Example Templates
- GIVEN the user is on the template selection page
- WHEN the user views the template list
- THEN at least 4 example templates are displayed with "Example" badge
- AND example templates include:
  - "Example: CRUZAMENTOMEDIAS" - EMA 3 + SMA 37 + SMA 32 (existing strategy as combo)
  - "Example: Scalping EMA 5/13" - Fast EMAs for scalping
  - "Example: Swing RSI Divergence" - RSI with divergence detection
  - "Example: Breakout with Volume" - Price breakout confirmed by volume
- AND user can click "Clone" on any example template
- AND the cloned template opens in the custom builder for editing
- AND user can modify and save as their own template

### Requirement: Persist Custom Templates
Custom templates SHALL be stored in the SQLite database.
The system SHALL use a dedicated `combo_templates` table.
Template data SHALL be stored in JSON format.
The system SHALL support CRUD operations (Create, Read, Update, Delete) for custom templates.
Pre-built and example templates SHALL be marked with appropriate flags.

#### Scenario: Save and Retrieve Custom Template
- GIVEN the user has created a custom combo "My EMA RSI Strategy"
- WHEN the user clicks "Save Template"
- THEN the template is saved to the `combo_templates` table
- AND the template_data column contains JSON with indicators, logic, and parameters
- AND the template appears in the user's template list
- WHEN the user refreshes the page
- THEN the saved template is still available
- AND can be loaded and used for backtesting

### Requirement: Validate Entry/Exit Logic Syntax
The system SHALL validate entry/exit logic syntax before saving templates.
The system SHALL check that all aliases referenced in logic exist in the indicator list.
The system SHALL provide clear error messages for invalid syntax.
Users SHALL be able to test logic with sample data before saving.

#### Scenario: Validate Logic Before Saving
- GIVEN the user is creating a custom combo with aliases "fast" and "slow"
- WHEN the user enters entry logic: "(close > fast) ANDD (RSI > 30)"
- AND clicks "Save Template"
- THEN the system displays error: "Invalid syntax: 'ANDD' is not recognized. Did you mean 'AND'?"
- AND the template is not saved
- WHEN the user corrects to: "(close > fast) AND (RSI > 30)"
- AND clicks "Save Template"
- THEN the system validates successfully and saves the template

### Requirement: Enforce Unique Indicator Aliases
Each indicator alias SHALL be unique within a combo strategy.
The system SHALL prevent saving templates with duplicate aliases.
The system SHALL suggest unique aliases automatically when adding indicators.
The system SHALL display an error if user attempts to use a duplicate alias.

#### Scenario: Prevent Duplicate Aliases
- GIVEN the user has added an EMA indicator with alias "fast"
- WHEN the user adds another EMA indicator and tries to use alias "fast"
- THEN the system displays error: "Alias 'fast' is already in use. Please choose a unique alias."
- AND suggests alternatives: "fast2", "medium", "slow"
- AND prevents saving until alias is changed

### Requirement: Limit Indicators Per Combo
Each combo strategy SHALL support a minimum of 2 indicators.
Each combo strategy SHALL support a maximum of 6 indicators.
The system SHALL display an error if user tries to add more than 6 indicators.
The system SHALL explain the performance impact of too many indicators.

#### Scenario: Enforce Maximum Indicators
- GIVEN the user has added 6 indicators to a custom combo
- WHEN the user clicks "Add Indicator"
- THEN the system displays error: "Maximum of 6 indicators reached. Too many indicators may impact performance."
- AND the "Add Indicator" button is disabled
- WHEN the user removes one indicator
- THEN the "Add Indicator" button is enabled again

### Requirement: Handle Runtime Errors in Logic Evaluation
The system SHALL catch errors during entry/exit logic evaluation.
The system SHALL display clear error messages when logic fails during backtest.
The system SHALL suggest potential fixes for common errors.
Failed backtests SHALL not crash the application.

#### Scenario: Handle Division by Zero Error
- GIVEN the user has created a combo with logic: "(RSI / (ATR - ATR))"
- WHEN the user runs a backtest
- AND the logic causes a division by zero error
- THEN the system catches the error
- AND displays: "Error in entry logic: Division by zero detected. Check your formula."
- AND suggests: "Ensure denominator is never zero. Consider adding a condition."
- AND the backtest stops gracefully without crashing

### Requirement: Provide Helper Functions for Logic
The system SHALL provide helper functions for common trading logic patterns.
The following functions SHALL be available: crossover, crossunder, above, below.
The system SHALL document available functions in the UI.
Functions SHALL be optimized for performance on large datasets.

#### Scenario: Use Crossover Function
- GIVEN the user is creating entry logic for a combo
- WHEN the user enters: "crossover(fast, slow)"
- THEN the system recognizes the crossover function
- AND evaluates it as: "(fast[current] > slow[current]) AND (fast[previous] <= slow[previous])"
- AND the logic works correctly during backtest
- WHEN the user hovers over "crossover" in the UI
- THEN a tooltip displays: "crossover(a, b): Returns true when 'a' crosses above 'b'"

### Requirement: Support Multi-Output Indicators
Indicators that return multiple values SHALL use a consistent naming convention.
Bollinger Bands SHALL use: {alias}_upper, {alias}_middle, {alias}_lower.
MACD SHALL use: {alias}_macd, {alias}_signal, {alias}_histogram.
The system SHALL document the naming convention in the UI.

#### Scenario: Use Bollinger Bands in Logic
- GIVEN the user adds Bollinger Bands indicator with alias "bb"
- WHEN the indicator is calculated
- THEN three columns are created: "bb_upper", "bb_middle", "bb_lower"
- AND the user can reference them in logic: "(close < bb_lower) AND (RSI < 30)"
- AND the system displays available columns in a dropdown/autocomplete

### Requirement: Edit Saved Custom Templates
Users SHALL be able to edit their saved custom templates.
The system SHALL provide an "Edit" button for custom templates.
Editing SHALL load the template into the custom builder with all settings.
Users SHALL be able to save changes (update) or save as new template (clone).

#### Scenario: Edit Existing Template
- GIVEN the user has a saved custom template "My EMA RSI Strategy"
- WHEN the user clicks "Edit" on the template
- THEN the custom builder opens with all template settings loaded
- AND the user can modify indicators, aliases, or logic
- WHEN the user clicks "Save Template"
- THEN the system asks: "Update existing template or save as new?"
- AND allows user to choose update or clone

### Requirement: Delete Custom Templates
Users SHALL be able to delete their custom templates.
The system SHALL provide a "Delete" button for custom templates only.
The system SHALL require confirmation before deleting.
Pre-built and example templates SHALL NOT be deletable.

#### Scenario: Delete Custom Template
- GIVEN the user has a saved custom template "Test Strategy"
- WHEN the user clicks "Delete" on the template
- THEN the system displays confirmation: "Are you sure you want to delete 'Test Strategy'? This cannot be undone."
- WHEN the user confirms
- THEN the template is removed from the database
- AND disappears from the template list
- WHEN the user tries to delete a pre-built template
- THEN the "Delete" button is not visible

### Requirement: Execute Combo Strategy Backtest
The backend SHALL instantiate the correct combo strategy class based on user selection.
The combo strategy MUST calculate all required indicators.
The combo strategy MUST evaluate entry logic combining all indicator conditions.
The combo strategy MUST evaluate exit logic combining all indicator conditions.

#### Scenario: Run EMA+RSI Backtest
- GIVEN the user has configured EMA+RSI combo parameters
- WHEN the user clicks "Run Backtest"
- THEN the backend creates an `EmaRsiCombo` strategy instance
- AND the strategy calculates EMA_9, EMA_21, and RSI_14 indicators
- AND entry signals are generated when: (close > EMA_9) AND (close > EMA_21) AND (RSI > 30 AND RSI < 50)
- AND exit signals are generated when: (RSI > 70) OR (close < EMA_9)
- AND results include all trades, metrics, and indicator data

### Requirement: Optimize Combo Strategy Parameters
The sequential optimization SHALL test parameters one at a time in stages.
Each stage MUST use the best parameter values from previous stages.
The optimization MUST start from market standard default values for all parameters.
The user SHALL be able to configure custom optimization ranges for each parameter (Min, Max, Step).
Stop Loss MUST be optimized LAST after all indicator parameters.
Results MUST show the best parameter value for each stage.

#### Scenario: Optimize EMA+RSI Combo with Custom Stop Loss Range
- GIVEN the user has enabled optimization for EMA Fast, EMA Slow, RSI Period, and Stop Loss
- AND starting defaults are: Fast EMA=9, Slow EMA=21, RSI=14, Stop Loss=1.5%
- AND user configures EMA Fast range: Min=9, Max=15, Step=1 → [9, 10, 11, 12, 13, 14, 15]
- AND user configures EMA Slow range: Min=21, Max=30, Step=1 → [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
- AND user configures RSI Period range: Min=12, Max=16, Step=1 → [12, 13, 14, 15, 16]
- AND user configures Stop Loss range: Min=0.5%, Max=2%, Step=0.5% → [0.5%, 1%, 1.5%, 2%]
- WHEN the user runs parameter optimization
- THEN Stage 1 tests EMA Fast [9, 10, 11, 12, 13, 14, 15] with other params at defaults, selects best (e.g., 12)
- AND Stage 2 tests EMA Slow [21, 22, 23, 24, 25, 26, 27, 28, 29, 30] with Fast=12, other params at defaults, selects best (e.g., 26)
- AND Stage 3 tests RSI Period [12, 13, 14, 15, 16] with Fast=12, Slow=26, other params at defaults, selects best (e.g., 14)
- AND Stage 4 tests Stop Loss [0.5%, 1%, 1.5%, 2%] with ALL indicator params optimized, selects best (e.g., 1%)
- AND the system runs only 26 tests total (7 + 10 + 5 + 4) instead of 1400 combinations (7 × 10 × 5 × 4)
- AND results show the best value for each stage with performance metrics
- AND final optimized parameters are: Fast=12, Slow=26, RSI=14, Stop Loss=1%

### Requirement: Visualize Combo Strategy Indicators
The results chart SHALL display all indicators used in the combo strategy.
Each indicator MUST use a distinct color.
The chart legend MUST show all indicator names with their parameters.

#### Scenario: View EMA+RSI Chart
- GIVEN a backtest with EMA+RSI combo has completed
- WHEN the user views the results chart
- THEN the chart displays three indicator lines: EMA_9 (blue), EMA_21 (green), and RSI_14 (purple)
- AND the legend shows "EMA(9)", "EMA(21)", and "RSI(14)" with corresponding colors
- AND buy/sell markers are overlaid on the price chart
- AND all indicators are properly aligned with the price data

### Requirement: Combo Strategy Metadata API
The backend SHALL provide an API endpoint to list available combo strategies.
The endpoint MUST return strategy name, description, component indicators, and parameter schemas.
The parameter schemas MUST include default values and optimization ranges.

#### Scenario: Fetch Combo Strategy Metadata
- GIVEN the frontend needs to display combo strategy options
- WHEN the frontend calls `/api/strategies/meta?type=combo`
- THEN the API returns a list of combo strategies
- AND each strategy includes: name, description, indicators array, and parameters object
- AND parameters include: name, default, min, max, step, and description
- AND the response format matches the existing single-indicator schema format

### Requirement: Combo Strategy Performance
Combo strategy backtests SHALL complete within 150% of single-indicator backtest time.
Indicator calculations SHALL be cached to avoid redundant computation.
Sequential optimization SHALL use the existing SequentialOptimizer service.

#### Scenario: Performance Benchmark
- GIVEN a dataset with 10,000 candles
- WHEN running a single-indicator RSI backtest
- AND running a combo EMA+RSI backtest
- THEN the combo backtest completes in less than 1.5x the time of the single-indicator backtest
- AND memory usage remains within acceptable limits (< 2GB)
- AND sequential optimization completes significantly faster than grid search would
