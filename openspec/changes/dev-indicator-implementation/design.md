# Design: Dev implementa novos indicadores

## Overview
Permitir que o Dev altere o backend para criar novos indicadores no engine, evitando falhas de lógica por colunas inexistentes.

## Scope
- Backend somente (estratégias/serviços).
- **Não alterar frontend/interface**.

## Flow
1. Dev identifica erro (ex.: coluna/indicador ausente, falha de preflight).
2. Dev diagnostica a causa e decide a correção (ex.: adicionar ROC).
3. Dev implementa cálculo no `ComboStrategy` (ou serviço equivalente).
4. Atualiza validações/aliases para expor a coluna esperada.
5. Registra no trace a inclusão do indicador/correção aplicada.
