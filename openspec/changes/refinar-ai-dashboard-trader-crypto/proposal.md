## Why

O `AI Dashboard` já unifica sinais, mas ainda não filtra bem o universo de ativos nem oferece contexto operacional suficiente para um trader agir com confiança. Isso reduz credibilidade do produto porque mistura ativos pouco relevantes, stablecoins e sinais sem prazo, validade ou transparência clara sobre frescor e conflito entre fontes.

## What Changes

- Curar o universo padrão do `AI Dashboard` para priorizar ativos tradáveis e relevantes, ocultando por padrão pares estáveis e cobertura de baixa prioridade.
- Introduzir contexto operacional no sinal unificado, incluindo horizonte, validade, entrada, invalidação, alvo e risco quando esses dados existirem.
- Expor metadados de confiança por fonte e por sinal consolidado, incluindo atualização, staleness, convergência e motivo resumido da decisão final.
- Ajustar a interface para separar oportunidades principais de cobertura adicional, sem perder acesso aos ativos ocultados pelo filtro padrão.

## Capabilities

### New Capabilities
- `ai-dashboard-asset-curation`: Curadoria, priorização e segmentação do universo de ativos exibido no dashboard.
- `ai-dashboard-signal-actionability`: Enriquecimento do sinal unificado com contexto operacional consumível por trader.
- `ai-dashboard-source-trust`: Transparência de frescor, convergência e confiabilidade por fonte e no sinal final.

### Modified Capabilities
- Nenhuma.

## Impact

- Backend: extensão do agregador em `backend/app/routes/ai_dashboard.py` e possíveis utilitários de priorização/classificação.
- Frontend: ajustes em `frontend/src/pages/AIDashboardPage.tsx` e componentes de `frontend/src/components/ai-dashboard/`.
- API: payload de `/api/ai/dashboard` precisará incluir blocos opcionais de curadoria, actionability e trust sem quebrar compatibilidade.
- Dados: necessidade de usar volume/liquidez, timestamps e metadados de origem já disponíveis nas três fontes.
- QA: novos cenários E2E e de integração para filtros padrão, sinais acionáveis e metadados de confiança.
