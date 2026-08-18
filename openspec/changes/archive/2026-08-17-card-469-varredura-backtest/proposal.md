# Change: Varredura sistemática de estratégias swing

## Why

O fluxo atual otimiza um template por vez e, no batch, amplia apenas o conjunto de símbolos. Para descobrir estratégias swing de forma comparável, o administrador ainda precisa repetir manualmente combinações de template, símbolo, timeframe e direção, depois consolidar métricas fora do produto. Isso torna a descoberta lenta, sujeita a duplicatas e sem trilha confiável entre o run exploratório e um favorito promovido.

## What Changes

- Adiciona uma varredura administrativa configurável sobre o produto cartesiano `templates × símbolos × timeframes × direções`, limitada aos timeframes swing `4h` e `1d`, precedida por preflight server-side que devolve snapshot versionado, combinações válidas e exclusões explicadas.
- Reutiliza o motor de otimização e o ciclo de jobs batch existente para execução em background, com claim/lease recuperável, enqueue transacional via outbox, progresso reconciliável, pausa e cancelamento concorrentes.
- Persiste a definição imutável do escopo e cada resultado da varredura para permitir retomada, auditoria e recomposição do leaderboard.
- Consolida os resultados elegíveis em leaderboard ordenável, com ranking padrão por Calmar e alternativa por CAGR versus Buy & Hold.
- Exibe CAGR, Buy & Hold, delta para Buy & Hold, Calmar, drawdown máximo, Sharpe, Profit Factor, win rate e número de trades para cada candidato.
- Separa identidade de estratégia de evidência: `strategy_identity_key` cobre estrutura, parâmetros, símbolo, timeframe e direção (sem janela); `evidence_fingerprint` registra janela, candles, custos e métricas apenas como proveniência. A identidade estável detecta equivalência contra templates/favoritos e bloqueia promoção de duplicatas sem permitir que outra janela contorne a regra.
- Permite promoção manual de um candidato não duplicado **exclusivamente a favorito tier 3**, sem seletor ou override de tier, registrando a origem na varredura e impedindo promoção concorrente ou repetida.
- Deriva o ator do principal autenticado em criação e promoção; autorização negada usa `403`, enquanto conflitos idempotentes/equivalentes usam `409` e, quando houver promoção equivalente vencedora, devolvem sua referência.
- Introduz uma superfície administrativa dentro do shell autenticado de Combo, com configurador, acompanhamento do job, filtros e leaderboard responsivo.

## Capabilities

### New Capabilities

- `discovery-sweep`: configuração, criação, execução e controle de uma varredura sistemática.
- `discovery-leaderboard`: consolidação, ranking e filtragem dos resultados da varredura.
- `discovery-deduplication`: normalização e detecção de equivalência de candidatos.
- `discovery-promotion`: promoção manual, idempotente e auditável de candidato a favorito.

### Modified Capabilities

- O batch backtest passa a ser reutilizado por um orquestrador de descoberta, sem alterar o contrato do batch atual para seus consumidores existentes.
- Favoritos passam a aceitar metadados de origem de descoberta, preservando compatibilidade com favoritos criados por outros fluxos.

## Impact

- **UI impact: affected** — nova superfície administrativa de configuração e leaderboard no shell existente de Combo, com estados de progresso, pausa, cancelamento, deduplicação e promoção.
- Backend: novos contratos e persistência de varredura/resultados; composição sobre `combo_optimizer`, `batch_backtest_service`, `batch_backtest_queue` e `batch_backtest_store`.
- Frontend: nova rota administrativa sob `/combo`, reutilizando shell, tokens e padrões do batch atual.
- Dados: resultados e origem da promoção precisam sobreviver a reinício do processo e ser consultáveis por `sweep_id`.
- Documentação: `docs/strategy-transparency-matrix.md` só será alterado se a implementação adicionar templates ao catálogo; a varredura, isoladamente, não cria templates inéditos.

## Out of Scope

- Gerar automaticamente estruturas de templates inéditas.
- Promover candidatos automaticamente por score.
- Incluir timeframes intraday diferentes de `4h` e `1d`.
- Alterar fórmulas internas do otimizador ou prometer desempenho futuro.
- Tornar a superfície disponível para usuários não administradores.

## Success Criteria

- Um administrador dispara uma única varredura multi-dimensional e acompanha seu estado sem manter a página aberta.
- O total planejado vem de um preflight server-side executável, corresponde às combinações válidas do snapshot e é revalidado atomicamente na criação.
- O leaderboard pode ser recomposto dos resultados persistidos e ordenado sem recalcular backtests.
- Candidatos equivalentes são explicados e nunca promovidos.
- Uma promoção válida cria exatamente um favorito **tier 3** — nenhum outro tier é aceito por este contrato — com referência ao `sweep_id` e ao resultado de origem.
- Toda transição terminal reconcilia cada combinação em `succeeded`, `failed` ou `skipped`, preservando `processed = succeeded + failed + skipped = total`, inclusive em falha operacional de setup/reconciliação.
