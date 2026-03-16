# Revisão PT-BR — reduce-workflow-scheduler-polling

## Resumo

Esta change reduz o desperdício de tokens do workflow atacando o scheduler: menos polling sem novidade, menos rechecagem do mesmo estado e mais comportamento orientado a evento real.

## O que entra
- suprimir turnos repetidos sem mudança material
- reduzir rechecks de runtime/Kanban quando nada mudou
- deixar o scheduler mais orientado a milestone/bloqueio/gate
- melhorar a cadência para gastar menos token em orquestração ociosa

## O que não entra
- refazer CI
- mudar features do produto
- substituir a lógica inteira de workflow

## Decisão de PO
- o scheduler deve gastar token só quando há valor novo
- inspeção repetida de estado inalterado deve ser exceção, não padrão
- prioridade é cortar custo operacional sem perder controle do fluxo

## Próximo gate
- Alan approval do planning para implementar a redução de polling/cadência
