# Change Proposal: proactive-log-monitoring

## Why
Hoje, erros de execução (ex.: intervalos inválidos no Binance) só aparecem quando o usuário reclama. Isso atrasa correções e causa fricção no fluxo do Lab. Precisamos que o sistema identifique e reporte automaticamente falhas recorrentes de execução, com o tipo de erro e provável causa.

## What Changes
- Detectar erros críticos de execução nos logs do backend (ex.: intervalo inválido, símbolo inválido, falha de download) e anexar o diagnóstico à execução.
- Expor o diagnóstico na resposta do run (API) para que a UI possa mostrar o motivo.
- Registrar um resumo estruturado para auditoria e troubleshooting.
