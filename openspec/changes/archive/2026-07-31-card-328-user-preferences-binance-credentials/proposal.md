## Why

Credenciais Binance (API Key/Secret read-only) precisam ficar no lugar natural da conta do usuário. Após feedback de Alan, o melhor lugar é **Meu Perfil** (aberto pela barra/conta), não uma tela separada de Preferências.

## What Changes

- Colocar o bloco **Credenciais Binance** em `/profile` (Meu Perfil), acessível pela barra de conta.
- Remover a entrada de navegação Preferências do usuário e a página dedicada `/preferences` (com redirect para `/profile`).
- Na Carteira, manter status compacto + atalho para **Meu Perfil**.
- Reutilizar `GET/PUT/DELETE /api/user/binance-credentials`.
- Atualizar E2E/visual para o fluxo no perfil.

## Capabilities

### New Capabilities
- `user-preferences-binance-credentials`: gerenciamento de API Key/Secret Binance read-only na tela Meu Perfil do usuário logado.

### Modified Capabilities
- `external-balances`: Carteira mostra status + link para Meu Perfil (não edita a chave no formulário completo).

## Impact

- Frontend: ProfilePage, nav/conta, remoção/redirect de `/preferences`, Carteira compacta, testes E2E/visual.
- Backend: sem mudança de contrato.
- Segurança: secret mascarado; UI reforça chave read-only + IP whitelist.
