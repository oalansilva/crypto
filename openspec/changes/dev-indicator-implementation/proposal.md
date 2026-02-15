# Change Proposal: Dev implementa novos indicadores

## Why

Hoje o Dev pode ajustar lógica, mas não consegue **adicionar indicadores** ausentes no engine (ex.: ROC). Isso causa colunas inexistentes, falhas no preflight e degeneração (0 trades).

## What Changes

- Permitir que o Dev **crie/edite indicadores** no backend (ex.: `ComboStrategy`).
- Habilitar o Dev a **alterar arquivos do projeto** necessários para adicionar indicadores (exceto frontend/interface).
- Ao ocorrer erro (ex.: coluna ausente), o Dev **diagnostica e corrige** automaticamente no backend.
- Registrar no trace quando um indicador novo foi adicionado ou quando uma correção foi aplicada.

## Success Criteria

- Dev consegue adicionar indicador novo (ex.: ROC) sem tocar no frontend.
- Preflight deixa de falhar por coluna ausente.
- Erros são diagnosticados e corrigidos automaticamente pelo Dev.
- Logs indicam que o indicador foi implementado e a correção aplicada.
