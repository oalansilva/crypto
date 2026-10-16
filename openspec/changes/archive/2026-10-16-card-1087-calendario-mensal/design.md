## Context

O #1087 corrige o calendário do #1078. `subtractFixedWindow` em `frontend/src/lib/sweepPeriod.ts` usa setters UTC que transbordam dias inexistentes. `resolve_optimizer_date_range` em `backend/app/tasks/discovery_tasks.py` usa `relativedelta`, que limita ao último dia válido.

O Combo usa `resolvePeriodDates` na janela do backtest e `comboPeriodHint` na apresentação. A Descoberta envia datas explícitas por `periodPayloadForApi` no preflight e na criação; o backend prioriza essas datas e calcula o período apenas quando faltam. Corrigir somente o backend não corrige os payloads da tela.

UI impact: none
live_route: N/A correção de aritmética de calendário; sem alteração de apresentação
surface: none

A mudança corrige valores de data já apresentados, sem alterar layout, copy, controles, estados ou navegação.

## Goals / Non-Goals

**Goals:** preservar o dia quando existe no mês de destino; limitar ao último dia quando não existe; produzir datas iguais com a mesma referência UTC e opção; preservar data final e demais modos.

**Non-Goals:** mudar ranking, execução, opções ou defaults do #1078; recalcular histórico; reabrir #1078; modificar APIs, validação de entradas ou relógios dos fluxos.

## Decisions

1. Tratar `1m`, `3m`, `6m`, `1y` e `2y` como deslocamentos de 1, 3, 6, 12 e 24 meses da referência original. Determinar ano/mês de destino e escolher `min(dia original, último dia do destino)`, em UTC. Calcular diretamente evita transbordamento e encurtamento cumulativo de subtrair um mês repetidamente. Dias fixos não representam meses de calendário.
2. Concentrar a correção em `sweepPeriod.ts`, preservando assinaturas e consumidores. Manter `relativedelta` no backend. Compartilhar contrato e vetores de teste entre linguagens dispensa endpoint ou dependência nova.
3. Preservar precedência de datas explícitas no backend. Verificar snapshots sem datas (fallback) e snapshots com datas resolvidas pelo frontend. Datas apresentadas/enviadas devem corresponder à janela consumida; snapshots existentes não serão reinterpretados.
4. Congelar referência UTC nos testes. Cobrir as cinco opções com dia comum, fim de mês, fevereiro bissexto e virada do ano, usando os mesmos vetores esperados nas duas linguagens. Conferir também payload/preflight e apresentação existentes com relógio controlado.

## Risks / Trade-offs

- Divergência futura entre linguagens → matriz de paridade executada em ambos os testes; formato/local da fixture é detalhe de Apply.
- Perda do dia original ao iterar meses → deslocamento total direto; incluir 2026-03-31 menos três meses = 2025-12-31.
- Relógios diferentes na virada UTC → igualdade exige a mesma referência; sincronização de relógios fica fora do card.
- Regressão nos demais modos → preservar `15d`, `custom`, `all`, nulos e datas explícitas; conferir data final em todos os vetores.

## Migration Plan

Correção localizada, sem migração ou reprocessamento. Implementação após T7/T8; reversão pode restaurar o helper anterior. Publicação segue o fluxo normal do card.

## Prototype

N/A — cálculo de datas com apresentação existente; HTML gerado/copied: N/A.

## Impeccable

N/A — sem decisão visual, copy nova, interação ou superfície alterada. Design e aprovação humana continuam obrigatórios.

## Open Questions

Nenhuma decisão de produto pendente. Crítica independente e publicação ficam com o orquestrador.

## Design Critique

- P0–P2: nenhum. Disposition: critérios do card, tokens sem-tela, UTC/clamp, demais modos e precedência de datas explícitas cobertos.
- P3: formato/local da matriz de paridade. Disposition: aceito como detalhe de Apply, já previsto no design.
- Verdict: PASS; sem rework necessário.
