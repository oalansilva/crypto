# logging Specification

## Purpose
TBD - created by syncing delta from change hybrid-grid-optimization. Detailed progress logging for Combo Optimizer.
## Requirements
### Requirement: Detailed Progress Logging
The Combo Optimizer SHALL provide detailed, real-time logging of optimization progress.

#### Scenario: Stage Transition Logging
When the optimizer transitions between stages, it SHALL log: stage number and name, optimization mode (Sequential vs Grid Search), total number of tests, locked parameters from previous stages.

#### Scenario: Individual Test Logging
When each combination is tested in a Grid Search stage, it SHALL log test number/total, parameter combination, key metrics (Sharpe, Return, Trades), and "NEW BEST" when a better result is found.

#### Scenario: Completion Summary
When an optimization job completes, it SHALL log final best parameters, total tests, total time, and key metrics.

### Requirement: Forgot-password não loga e-mail, token ou link em INFO
O handler de forgot-password SHALL NOT gravar o e-mail do usuário, o token de reset nem o URL/link de reset em logs de nível INFO.

#### Scenario: Pedido de reset
- **WHEN** um cliente chama forgot-password para um e-mail existente
- **THEN** qualquer log INFO emitido por esse fluxo SHALL NOT conter o endereço de e-mail
- **AND** SHALL NOT conter o token de reset
- **AND** SHALL NOT conter o reset link

