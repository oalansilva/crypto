# Change Proposal: Dev PythonREPL para Correção de Lógica

## Why

Hoje, quando a lógica de entrada/saída está inválida, o fluxo aplica fallback automático ou encerra com erro. Isso impede o Dev de **corrigir de fato** a lógica e reduz a transparência do ajuste.

## What Changes

- Habilitar **PythonREPLTool** no agente Dev (LangGraph) para correções de lógica/código.
- Ao detectar erro de lógica, **tentar correção via Dev** antes de qualquer fallback.
- Registrar no trace/log quando uma correção foi aplicada (entrada, saída e motivo).

## Success Criteria

- Erros de lógica disparam correção do Dev com PythonREPLTool.
- O fallback automático deixa de ser o caminho padrão nesse caso.
- Logs mostram claramente quando houve correção e o resultado.
