# Design: Dev PythonREPL para Correção de Lógica

## Overview
Adicionar a PythonREPLTool ao Dev para que ele consiga validar/corrigir lógica com execução real em Python e normalizar expressões antes do backtest.

## Flow
1. Dev recebe lógica inválida.
2. Dev usa PythonREPLTool para validar/corrigir a expressão.
3. Se corrigido, o fluxo segue com a lógica ajustada.
4. Se não corrigir, registrar falha e somente então aplicar fallback (ou retornar erro).

## Logging
- Registrar no trace: erro detectado, correção aplicada, lógica final.
- Persistir motivo/resultado em logs do run.
