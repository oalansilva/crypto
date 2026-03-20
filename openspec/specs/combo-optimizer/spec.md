# combo-optimizer Specification

## Purpose
Support grid-based optimization for correlated parameters with iterative refinement compatibility.

## Requirements

### Requirement: Grid-Based Optimization for Correlated Parameters
The Combo Optimizer SHALL support joint optimization of correlated parameters using Grid Search. When correlated parameters (e.g., media_curta, media_inter, media_longa) are detected, it SHALL create a single joint stage testing all combinations (cartesian product). Fallback to sequential for uncorrelated parameters.

#### Scenario: Joint optimization of correlated MA parameters
- **GIVEN** correlated parameters media_curta, media_inter, media_longa are defined
- **WHEN** grid optimization is triggered
- **THEN** a single joint stage tests all Cartesian combinations
- **AND** uncorrelated parameters fallback to sequential optimization

### Requirement: Iterative Refinement Compatibility
Grid Search SHALL disable Iterative Refinement (max_rounds = 1 when Grid is active) to avoid redundant testing. Independent parameters (e.g., stop_loss) SHALL be optimized sequentially after Grid.

#### Scenario: Grid disables iterative refinement
- **GIVEN** Grid Search mode is active
- **WHEN** optimization runs
- **THEN** max_rounds is set to 1
- **AND** independent parameters are optimized sequentially after Grid
