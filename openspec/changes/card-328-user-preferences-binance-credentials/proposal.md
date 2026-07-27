## Why

Credenciais Binance (API Key/Secret read-only) hoje só são configuradas na tela de Carteira. O usuário precisa de um lugar dedicado de preferências para salvar essa chave vinculada à conta logada, usada pela Home e pela Carteira, sem misturar configuração sensível com a visualização de saldos.

## What Changes

- Criar tela de **preferências do usuário** (rota autenticada) com o bloco **Credenciais Binance** (status, API Key, API Secret, salvar/remover).
- Reutilizar o contrato existente `GET/PUT/DELETE /api/user/binance-credentials`.
- Mover o formulário completo para fora da Carteira; na Carteira permanecer status compacto + atalho para preferências.
- Incluir entrada de navegação para preferências do usuário (distinta de Preferências do sistema admin).
- Cobrir com testes E2E/visual o novo fluxo.

## Capabilities

### New Capabilities
- `user-preferences-binance-credentials`: tela de preferências do usuário para salvar/gerenciar API Key/Secret Binance read-only vinculada ao usuário logado.

### Modified Capabilities
- `external-balances`: a Carteira deixa de ser o único/lugar principal do formulário completo de credenciais; passa a exibir status + link para preferências, mantendo o consumo da chave do usuário.

## Impact

- Frontend: nova página/rota de preferências, nav, componente reutilizável de credenciais, ajuste em `ExternalBalancesPage`, testes E2E/visual.
- Backend: sem mudança de contrato esperada (endpoints já existem); apenas regressão dos testes de credentials.
- Segurança: secret continua mascarado/não retornado em claro; UI reforça chave read-only + IP whitelist.
