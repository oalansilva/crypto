# Proposta: seleção sem rolagem na Discovery

## Why

O configurador de `/combo/discovery` precisa acomodar 30 templates e 126 símbolos. A seleção atual expõe listas paginadas em sequência dentro do formulário, transformando a montagem do escopo em uma procura longa e fazendo o restante da configuração perder contexto. Alan pediu uma alternativa em que o usuário não precise rolar o catálogo para alcançar uma opção.

## What Changes

- Substituir as listas abertas de templates e símbolos por dois resumos compactos no rascunho.
- Abrir um workbench transacional único, com abas de Templates e Símbolos, busca instantânea, filtro por categoria, resultados limitados por página e seleção por adição.
- Permitir selecionar o catálogo inteiro e tratar remoções como exceções explícitas, evitando 126 ações individuais.
- Manter contagens, seleção atual e preflight sincronizados, com `Aplicar` e `Cancelar` inequívocos.
- Preservar shell, histórico, preflight lateral, sweep ativo e leaderboard da Discovery.
- Garantir uso por teclado, focus trap, live regions, alvos de 44 × 44 px e composição sem rolagem interna em desktop e mobile.

## Capabilities

### New Capabilities

- `discovery-catalog-selection`: seleção compacta e pesquisável de catálogos extensos sem percorrer uma lista longa.

### Modified Capabilities

- Nenhuma regra de sweep, preflight, ranking, histórico ou promoção muda; somente a interação que produz os arrays de templates e símbolos do rascunho é redesenhada.

## Impact

- UI afetada: configurador da rota `/combo/discovery`.
- Contrato de dados esperado: os mesmos identificadores de template e pares de símbolo já aceitos pelo preflight.
- Sem mudança proposta em backend, persistência, lifecycle, ranking ou autorização.
- A implementação futura deve medir escala real e preservar a proteção existente de limite máximo do preflight.
