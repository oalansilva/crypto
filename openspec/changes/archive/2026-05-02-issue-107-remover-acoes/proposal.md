## Why

O MVP atual será focado apenas em cripto. Manter opções de ações no fluxo principal cria expectativa de suporte que não será trabalhada agora e pode levar usuários para caminhos sem valor de produto.

## What Changes

- **BREAKING**: remover a seleção de mercado de ações dos fluxos principais de configuração, favoritos e monitor.
- **BREAKING**: bloquear endpoints operacionais de universo/candles para ações no MVP.
- Filtrar favoritos e oportunidades para exibir apenas pares cripto.
- Atualizar testes afetados para validar comportamento crypto-only.

## Capabilities

### New Capabilities

- `crypto-only-mvp`: comportamento MVP que limita fluxos operacionais a ativos cripto.

### Modified Capabilities

- `us-stocks-universe-nasdaq100`: o universo NASDAQ-100 deixa de ser exposto no MVP.
- `favorites-asset-type-filter`: o filtro por tipo de ativo deixa de oferecer ações.
- `monitor`: o monitor deixa de oferecer filtro/exibição de ações.

## Impact

- Frontend: `ComboConfigurePage`, `FavoritesDashboard`, componentes Monitor e testes E2E relacionados.
- Backend: endpoints de mercado em `backend/app/api.py` e validações de candles.
- Testes: ajustar cobertura para crypto-only e remoção de NASDAQ/stocks.
