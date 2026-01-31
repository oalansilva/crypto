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

### Requirement: Parallelize Optimization Loop
The system MUST execute backtests for parameter variations in parallel processes to utilize available CPU cores. Workers distribute parameter values; on unpicklable or worker errors the system MUST catch, mark that value failed, continue other tests, and log clearly.

### Requirement: Stage-Based Parameter Locking (Sequential Optimization)
The system MUST execute optimization in sequential stages: each stage optimizes ONE parameter or group; previous results are LOCKED for subsequent stages; best result from each stage becomes baseline for next. Stages may include timeframe, then fast/slow/signal, then stop_loss, then stop_gain.

### Requirement: Full History Backtesting (Sequential)
The system MUST use complete available historical data for ALL tests in ALL stages. No date range selection; auto-detect earliest/latest; entire dataset per backtest.

