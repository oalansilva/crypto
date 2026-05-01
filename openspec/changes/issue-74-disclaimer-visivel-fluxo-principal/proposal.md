# Proposal: Inserir disclaimer visível no fluxo principal (Issue #74)

## Why

O fluxo atual ainda permite entrar no produto sem um aviso claro de caráter educativo.
O risco é o usuário interpretar os sinais e métricas como recomendação financeira direta
ou promessa de desempenho, o que contraria o posicionamento do produto.

## What

Esta change adiciona um disclaimer persistente do primeiro acesso da sessão nas áreas centrais:

- Tela de login (fluxo de entrada da aplicação).
- Tela principal de operação (`/monitor`).

O texto deve ser neutro, educativo e sem promessa de lucro:

- reforça que o produto é de apoio à decisão;
- não é recomendação financeira;
- não há garantia de resultados;
- convida à autonomia e prudência.

O aviso será exibido na primeira sessão e pode ser dispensado com interação do usuário para
não poluir retornos subsequentes na mesma sessão.

## Scope

- Frontend:
  - `frontend/src/components/monitor/MonitorDisclaimer.tsx` (novo)
  - `frontend/src/pages/LoginPage.tsx` (inclusão do aviso)
  - `frontend/src/pages/MonitorPage.tsx` (inclusão do aviso)
- OpenSpec:
  - `openspec/changes/issue-74-disclaimer-visivel-fluxo-principal/`

## Out of Scope

- Alteração de contratos de API.
- Tradução internacional da mensagem (PT-BR apenas).

## Impact

- Reforça compliance e expectativa correta de uso desde entrada e operação principal.
- Reduz risco de percepção de produto de recomendação.
