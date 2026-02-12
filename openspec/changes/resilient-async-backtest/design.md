# Design: Resilient Async Backtest

## Overview
Mover a execução do backtest para jobs assíncronos no Dev. O loop Dev acompanha status e erros, e reitera sem bloquear o fluxo principal.

## Components
- **JobManager**: criação/consulta de jobs de backtest.
- **Run State**: persistência de `backtest_job` + `diagnostic`.
- **Dev Loop**: re-tentativas quando job falha.

## Flow
1. Dev cria template.
2. Dev dispara job assíncrono e atualiza `backtest_job`.
3. Job completa ou falha; erro é capturado como `diagnostic`.
4. Dev ajusta template/motor e re-dispara novo job.

## Open Questions
- Tempo máximo de espera antes de considerar falha?
- Número máximo de re-tentativas (usar `max_iterations` do run?).
