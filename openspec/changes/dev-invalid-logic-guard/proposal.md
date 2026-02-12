# Change Proposal: Guard de Lógica Inválida (Dev)

## Why

Hoje o run pode falhar **antes** do auto-ajuste quando o Dev gera `entry_logic/exit_logic` em texto livre. O motor de lógica rejeita a expressão e a execução cai com `personas_error`, impedindo o ciclo de correção automática e deixando o Trader sem resposta útil.

## What Changes

- Adicionar **preflight determinístico de lógica** antes do backtest.
- Quando a lógica estiver inválida, o Dev **corrige automaticamente** (re-escreve em booleano válido) e **re-tenta** antes de rodar o backtest.
- Persistir no trace os motivos da correção e o número de tentativas.

## Success Criteria

- Se a lógica for inválida, o sistema corrige e **não encerra** o run com erro.
- O backtest roda com lógica válida (sem “unknown columns/functions”).
- O Trader recebe apenas a versão corrigida/avaliada.
