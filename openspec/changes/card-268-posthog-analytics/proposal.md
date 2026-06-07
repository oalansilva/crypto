## Why

O Cripto Farol precisa medir o funil social -> site -> lead antes de investir em dashboards ou mídia. PostHog Cloud no free tier permite começar com custo esperado zero e com limite de cobrança controlável.

## What Changes

- Adicionar analytics frontend via PostHog configurável por ambiente, sem chave hardcoded.
- Capturar eventos mínimos do funil: pageview, início de sessão do app e submissão/resultado do formulário de lead quando aplicável.
- Reutilizar a atribuição first-touch/UTM já persistida no navegador, enviando apenas metadata não sensível.
- Manter o produto funcional sem PostHog quando as variáveis de ambiente não estiverem configuradas.
- Registrar o guardrail operacional de free tier e billing limit antes de escala relevante.

## Capabilities

### New Capabilities
- `product-analytics`: rastreamento mínimo de eventos de produto/funil com PostHog e controle por configuração de ambiente.

### Modified Capabilities
- `closed-beta-access-control`: o formulário de lead passa a emitir eventos técnicos de funil sem expor PII.

## Impact

- Frontend Vite/React: inicialização de analytics, tracking de pageview e eventos de formulário.
- Configuração de ambiente: novas variáveis `VITE_POSTHOG_KEY` e `VITE_POSTHOG_HOST`.
- Dependência frontend: SDK `posthog-js`.
- Sem impacto de banco ou API obrigatória nesta etapa.
