# Revisão PO — `corrigir-divida-tecnica-openspec`

## Resumo
Dívida técnica média: documentação, monitoramento e cron jobs.

## O que muda

1. **OpenSpec specs** — 14 specs com erros de validação serão corrigidos (adicionar SHALL/MUST e cenários faltantes).
2. **Health monitoring** — Novo cron que verifica backend e frontend e notifica Alan no Telegram se algo cair.
3. **Cron jobs** — crypto-news-daily e monitor diario (4 erros consecutivos) serão consertados com backoff ou desabilitados com trigger manual.
4. **docs/coordination/** — Arquivos de changes arquivadas/completadas serão removidos.

## Critérios de aceite
- `openspec validate --specs` mostra 0 erros
- Cron de health notifica Alan no Telegram se serviço cair
- Cron jobs rodam sem erros consecutivos
- docs/coordination/ limpo

## Sem novo UI/UX
Esta change é manutenção — health monitoring é cron/script, sem novo UI/UX.
