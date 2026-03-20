# optimization Specification

## Purpose
TBD - created by archiving change optimize-multi-ma-params. Update Purpose after archive.
## Requirements
### Requirement: Geração de Combinação de Parâmetros
O otimizador MUST gerar combinações de parâmetros para estratégias, respeitando os intervalos e passos definidos.

#### Scenario: Filtrando Combinações Multi MA Inválidas
Dada uma estratégia com parâmetros `media_curta` (Curta), `media_inter` (Intermediária) e `media_longa` (Longa)
Quando o otimizador gera combinações
Então ele MUST excluir qualquer combinação onde `media_curta >= media_inter` OU `media_inter >= media_longa`
E ele MUST executar apenas backtests para combinações onde `media_curta < media_inter < media_longa`

### Requirement: Iterative Convergence
The optimization process MUST iterate through parameter stages (Rounds) until the set of best parameters stabilizes or a maximum round limit is reached. When Round N+1 finds identical optimal parameters to Round N, the system MUST stop and return the Converged Best Solution.

#### Scenario: Convergence stops optimization
- **GIVEN** Round N returns optimal parameters P
- **WHEN** Round N+1 finds identical parameters P
- **THEN** the system stops and returns P as the Converged Best Solution
- **AND** no further rounds are executed

### Requirement: Parallelize Optimization Loop
The system MUST execute backtests for parameter variations in parallel processes to utilize available CPU cores. Workers distribute parameter values; on unpicklable or worker errors the system MUST catch, mark that value failed, continue other tests, and log clearly.

#### Scenario: Parallel execution with error handling
- **GIVEN** a grid of parameter variations to test
- **WHEN** optimization runs
- **THEN** backtests execute in parallel processes utilizing available CPU cores
- **AND** worker errors are caught and marked as failed
- **AND** other tests continue to completion
- **AND** failures are logged clearly