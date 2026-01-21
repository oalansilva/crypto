# Proposta: Otimizar Busca de Parâmetros Multi MA

## Why
A estratégia "Multi MA Crossover" envolve três médias móveis: Curta (media_curta), Intermediária (media_inter) e Longa (media_longa).
Atualmente, o otimizador gera um produto cartesiano de todos os valores possíveis para cada parâmetro.
Isso resulta em muitas combinações que são logicamente inválidas ou redundantes, especificamente onde `Curta >= Intermediária` ou `Intermediária >= Longa`.
Essas combinações inválidas desperdiçam recursos computacionais significativos durante o backtesting.

## What Changes
Implementar um filtro heurístico no `ComboOptimizer` para podar combinações de parâmetros inválidas antes da execução.
A regra a ser aplicada é: `Período Curto < Período Intermediário < Período Longo`.
Isso será aplicado dinamicamente durante a geração de estágios ou no loop de execução.
**Atenção aos Apelidos:** O filtro deve reconhecer variações como `media_curta`/`ema_short`/`sma_short`, `media_inter`/`sma_medium` e `media_longa`/`sma_long`.

## Benefícios
- **Economia de Recursos:** Redução drástica no número de backtests (aprox. 83% de redução em um grid completo se considerarmos apenas combinações ordenadas).
- **Maior Cobertura:** A economia de tempo permite:
    - Testar intervalos maiores (ex: 2017-2025).
    - Usar passos menores (maior precisão).
    - Adicionar mais indicadores ao teste.


## Riscos
- **Suposição Heurística**: O filtro assume que quaisquer parâmetros chamados `media_curta`, `media_inter` e `media_longa` (ou seus apelidos) DEVEM seguir essa ordem. Embora verdadeiro para a estratégia específica "Multi MA Crossover", isso pode restringir configurações experimentais se os usuários intencionalmente quiserem testar médias invertidas (o que é raro).
- **Complexidade**: Adiciona lógica específica ao otimizador genérico, acoplando-o ligeiramente a essa convenção de nomenclatura.
