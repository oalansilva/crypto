# Revisão (PT-BR) — turn-scheduler-idle-backoff

## Objetivo
Reduzir o custo/ruído do **Turn Scheduler** (job que roda a cada 15 min) quando **não existem changes ativas** — sem perder a responsividade quando existir trabalho.

## Problema atual
Mesmo sem changes ativas, o job continua rodando e gerando execuções “vazias”. Isso consome recursos e pode gerar spam/ruído.

## Proposta
Quando não houver change ativa:
- aumentar o intervalo (backoff) automaticamente; e/ou
- pausar temporariamente o scheduler;
- e retomar automaticamente quando voltar a existir change ativa.

## Critérios de aceite
- Sem changes ativas: não deve ficar rodando a cada 15 min indefinidamente.
- Com change ativa: comportamento continua igual (executa turnos normalmente).
- Não gerar notificações desnecessárias.
- Mudança segura e reversível.

## Próximo passo
Você (Alan) revisa/ajusta o comportamento desejado (backoff vs pausar) e aprova pra eu implementar.
