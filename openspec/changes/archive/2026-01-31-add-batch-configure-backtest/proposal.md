# Change: Batch backtests from Configure Backtest screen

## Why
Today, running backtests for multiple assets requires the user to manually:
- selecionar um símbolo na tela `Configure Backtest`
- rodar a otimização / backtest
- salvar o melhor resultado nos favoritos

Para testar rapidamente todos os ativos relevantes de uma estratégia (por exemplo, todos os pares BTC/USDT, ETH/USDT, etc. para `multi_ma_crossover`), o fluxo manual é lento, repetitivo e propenso a erros.  
Um fluxo em lote, disparado a partir da própria tela de configuração, permite gerar automaticamente uma “primeira triagem” de candidatos e salvá‑los em `Favorites` com uma anotação clara de que foram **“gerados em lote”**.

## What Changes
- Adicionar um fluxo de **Batch Backtest** na tela `Configure Backtest` que:
  - usa a configuração atual (template, parâmetros, ranges, timeframe, flags como `Deep Backtest`)
  - permite ao usuário escolher o **escopo dos símbolos** a rodar: um único símbolo atual, um subconjunto multi‑selecionado (x, y, z) ou **todos** os símbolos disponíveis/filtrados
  - ao finalizar cada ativo, **cria sempre uma nova estratégia favorita** em `favorite_strategies` (não sobrescreve existentes), com:
    - um comentário específico indicando que foi **gerado em lote** (por exemplo `\"gerado em lote\"` + timestamp ou id do batch)
    - `tier = 3` para todas as estratégias geradas em lote
- Garantir que o batch:
  - rode de forma segura (fila de jobs, sem travar a UI)
  - registre progresso e erros (por ativo) para feedback ao usuário

## Impact
- **Affected specs**
  - `specs/backtest-config/spec.md` – comportamento da tela Configure Backtest e fluxo de execução.
- **Affected code (provável)**
  - Frontend:
    - `frontend/src/pages/ComboOptimizePage.tsx` ou componente equivalente da tela Configure Backtest
    - Componentes de UI de botão/estado de execução (novo botão “Run Batch” / “Run All Symbols”)
  - Backend:
    - Serviço de backtest/otimização (ex.: `AutoBacktestService`, `ComboOptimizer`, ou serviço dedicado para batch a partir de uma única configuração)
    - Rotas para disparar jobs em lote (nova rota ou extensão de `/api/combos/backtest` / `/api/auto_backtest`)
  - Persistência:
    - `FavoriteStrategy` (já existente) – uso automatizado para salvar favoritos marcados com `notes = "gerado em lote"` (ou concatenado às notas existentes)

