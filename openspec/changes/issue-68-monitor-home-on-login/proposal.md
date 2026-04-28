# Proposal: Definir Monitor como página inicial operacional após login

## Why

Com o redirecionamento atual, o fluxo de autenticação leva o usuário novamente para `/`
após login/criação de conta. Isso mantém uma tela menos operacional e não reflete a
posição atual do produto, onde o Monitor é a home funcional principal.

## What

Esta change ajusta o fluxo de pós-login para abrir `/monitor` e mantém o acesso autenticado
à raiz (`/`) também apontado para o Monitor, reduzindo fricção e deixando a navegação
alinhada com o uso real.

Inclui também preservação de retorno (`returnTo`) para acesso a rotas protegidas profundas,
além de alinhar o acesso principal do app para não expor “Playground” como rota de entrada.

## Scope

- Frontend:
  - `frontend/src/pages/LoginPage.tsx`
  - `frontend/src/App.tsx`
- OpenSpec (evidência da alteração):
  - `openspec/changes/issue-68-monitor-home-on-login/`

## Out of Scope

- Mudanças de backend de autenticação.
- Redesenho de navegação lateral/labels.

## Impact

- Experiência pós-login passa a entrar direto no Monitor.
- A rota pública raiz autenticada (`/`) passa a delegar para a home operacional.
