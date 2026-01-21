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

