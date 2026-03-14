# Design — alterar-dados-dos-cards

## Overview

Esta é uma mudança de UX pequena, centrada no detalhe do card já existente no Kanban.

## Design goals
- evitar fricção para corrigir dados básicos do card
- não introduzir telas pesadas para uma ação simples
- deixar o cancelamento claro e seguro
- manter consistência com o fluxo atual do drawer/detalhe do Kanban

## Proposed interaction

### 1. Edit card metadata
No detalhe do card, o usuário deve poder entrar em modo de edição para:
- alterar `title`
- alterar `description`
- salvar e ver a mudança refletida imediatamente no card/board

### 2. Cancel card
No mesmo contexto do detalhe do card, deve existir uma ação secundária/destrutiva de **Cancelar card**.

Comportamento esperado:
- pedir confirmação explícita
- não apagar o card do banco
- retirar o item do fluxo ativo / tratá-lo como cancelado no runtime
- deixar o histórico consultável

## UX notes
- priorizar reaproveitamento do drawer atual do Kanban
- evitar navegação para página separada nesta primeira entrega
- o estado cancelado deve ser visualmente inequívoco quando consultado
- feedback de sucesso/erro deve ser imediato e acionável

## Open questions for implementation
- exibir cards cancelados em coluna própria, ocultá-los do board padrão, ou mantê-los apenas no detalhe/filtros
- melhor mapeamento runtime para cancelamento no nível da change sem quebrar guard rails do board

## Design recommendation
Para esta fase, seguir a solução mais enxuta possível:
- editar no drawer
- confirmar cancelamento
- manter rastreabilidade completa
