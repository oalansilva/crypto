# combo-optimizer Specification

## Purpose
TBD - created by syncing delta from change hybrid-grid-optimization. Grid-based optimization for correlated parameters.

## Requirements

### Requirement: Grid-Based Optimization for Correlated Parameters
The Combo Optimizer SHALL support joint optimization of correlated parameters using Grid Search. When correlated parameters (e.g., media_curta, media_inter, media_longa) are detected, it SHALL create a single joint stage testing all combinations (cartesian product). Fallback to sequential for uncorrelated parameters.

### Requirement: Iterative Refinement Compatibility
Grid Search SHALL disable Iterative Refinement (max_rounds = 1 when Grid is active) to avoid redundant testing. Independent parameters (e.g., stop_loss) SHALL be optimized sequentially after Grid.
