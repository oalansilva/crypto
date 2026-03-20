# Revisão: Corrigir Specs de Validação

## O que muda

- **14 specs com erro** de validação vão ser corrigidos (Purpose + Scenarios)
- **Health monitoring** adicionado: cron que verifica backend/frontend e te notifica no Telegram se algo cair
- **Crons problemáticos** (crypto-news-daily, monitor diario) serão corrigidos com backoff ou desabilitados
- **docs/coordination** limpa — remove arquivos de changes arquivadas

## Impacto

- OpenSpec validation: limpa
- Ops: visibilidade de saúde do sistema
- Cron: operação confiável

## Tasks

1. Corrigir 11 specs (adicionar Purpose + Scenarios)
2. Criar health check script + cron
3. Corrigir/desabilitar crons com erro
4. Limpar docs/coordination
