## Why

A tela de seleção de combos (`/combo/select`, endpoint `GET /api/combos/templates`) lista 16 templates de teste com nome iniciando em `Quant` (`quant_btc_1d_*`), gerados pelos scripts de descoberta de estratégia (cards 261/262/277). Alan solicitou (2026-08-13) **excluir fisicamente** esses templates — não apenas ocultá-los — e também os 10 favoritos do Monitor que os referenciam (limpeza completa da descoberta de teste).

## What Changes

- Exclusão física dos 16 templates `quant_*` da tabela `combo_templates`.
- Exclusão física dos 10 favoritos (`favorite_strategies`) que referenciam templates `quant_*`.
- Nenhuma mudança de comportamento em otimizador, batch, Monitor ou frontend (a tela apenas deixa de ter os templates; os favoritos órfãos deixam de existir).

## Capabilities

### Modified Capabilities
- `combo-template-catalog`: templates de teste `quant_*` são removidos do catálogo (exclusão física).
- `favorites`: favoritos que referenciam templates `quant_*` são removidos (sem órfãos).

## Impact

- **Backend**: script/rotina de exclusão (uma vez) — sem mudança de código de runtime.
- **API**: `GET /api/combos/templates` — resposta sem templates `quant_*` (porque não existem mais).
- **Dados**: deleção de 16 linhas em `combo_templates` e 10 linhas em `favorite_strategies` (com registro/backup antes).
- **Frontend**: nenhuma mudança.
