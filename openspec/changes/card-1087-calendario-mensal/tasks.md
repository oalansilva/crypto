## 1. Contrato de calendário

- [x] 1.1 Materializar nos testes a matriz de `sweep-calendar-parity`, incluindo os exemplos do issue, todas as cinco opções, dia comum, fim de mês, ano bissexto e virada de ano; usar a mesma referência UTC e os mesmos resultados esperados nas duas linguagens.
- [x] 1.2 Ampliar `frontend/tests/sweep-period.test.mjs` e os testes de `resolve_optimizer_date_range` em `backend/tests/unit/test_discovery_celery_tasks.py` para conferir início/final, fallback sem datas e precedência das datas explícitas; demonstrar a regressão do frontend antes da correção.

## 2. Correção e consumo da janela

- [x] 2.1 Corrigir a subtração mensal/anual em `frontend/src/lib/sweepPeriod.ts` com deslocamento direto e limite ao último dia do mês de destino, preservando UTC, assinaturas e comportamento dos demais modos.
- [x] 2.2 Verificar com relógio controlado que o hint/payload do Combo e os payloads de preflight/criação da Descoberta mantêm a janela corrigida até o consumidor; cobrir 2026-03-31 com `1m` e um caso anual bissexto sem alterar a execução do backtest.
- [x] 2.3 Cobrir regressões de `15d`, personalizado (incluindo vazios/impedimentos), todo o histórico, opções/defaults e data final, mantendo o comportamento anterior para as mesmas entradas.

## 3. Validação

- [x] 3.1 Executar os testes direcionados frontend/backend e a verificação TypeScript/build pertinente; registrar comandos e resultados com a matriz de paridade verde.
- [x] 3.2 Validar a change OpenSpec e conferir o diff para assegurar escopo restrito ao cálculo/testes, sem alterações de ranking, opções, execução ou apresentação.
