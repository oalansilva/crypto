## 1. Resiliência do endpoint de oportunidades

- [x] 1.1 Adicionar timeout de agregação no `OpportunityService.get_opportunities` para não bloquear indefinidamente na coleta paralela.
- [x] 1.2 Tornar o build de jobs de coleta tolerante a erro por configuração da estratégia/fonte, registrando como skip.
- [x] 1.3 Atualizar rota e logs para continuar retornando `200` com oportunidades válidas mesmo com falhas parciais.

## 2. Estabilidade do endpoint de candles

- [x] 2.1 Ajustar validação de timeframe para permitir `stock + 4h` sem erro estrutural.
- [x] 2.2 Encaminhar `stock + 4h` para caminho com fonte compatível e retorno agregado.

## 3. Testes e evidência

- [x] 3.1 Atualizar cobertura de `/api/market/candles` para validar `1d` e `4h` com stooq/yahoo conforme ativo.
- [x] 3.2 Atualizar cobertura de `OpportunityService` para garantir timeout e isolamento de falhas por estratégia.
- [x] 3.3 Validar no fluxo local que o card #71 atende `/api/opportunities` sem bloqueio em cenário com falha parcial.

*Nota:* para implementação e validação, use os skills do `.codex/skills` disponíveis (e.g. testes, debug, playwright) quando aplicável.
