## Why

Ao salvar dados em "Meu Perfil", o usuario nao recebe uma confirmacao visivel de que a atualizacao foi concluida. O fluxo ja dispara uma notificacao, mas o sistema global de toast nao renderiza as mensagens dentro do viewport fixo, deixando o feedback imperceptivel.

## What Changes

- Corrigir o componente global de toast para renderizar notificacoes visiveis em uma area fixa da tela.
- Preservar o toast de sucesso existente no fluxo de atualizacao de perfil.
- Adicionar cobertura E2E para confirmar que salvar o perfil exibe feedback visivel.

## Capabilities

### New Capabilities

### Modified Capabilities
- `frontend-ux`: feedback de sucesso/erro acionado por formularios deve aparecer de forma visivel para o usuario.

## Impact

- Frontend: `frontend/src/components/ui/toast.tsx`, `frontend/src/components/ui/toaster.tsx`.
- Testes: novo teste Playwright para `/profile`.
- APIs: sem mudanca de contrato; o teste usa mocks para `GET/PUT /api/users/me`.
