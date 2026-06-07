## Context

O frontend já captura first-touch attribution em `frontend/src/lib/attribution.ts` e persiste UTM/referrer em `localStorage`. O próximo passo é medir o funil inicial no PostHog Cloud sem criar custo obrigatório nem expor PII.

## Goals / Non-Goals

**Goals:**
- Inicializar PostHog somente quando `VITE_POSTHOG_KEY` estiver configurada.
- Enviar pageviews e eventos técnicos mínimos do funil com attribution sanitizada.
- Manter o app sem dependência operacional de PostHog em DEV/PROD quando a configuração estiver ausente.
- Evitar email, nome, WhatsApp, dor declarada ou qualquer PII nos eventos.

**Non-Goals:**
- Criar dashboards PostHog ou Metabase nesta etapa.
- Enviar eventos server-side.
- Alterar schema de banco, API de leads ou fluxo de email beta.
- Publicar em PROD sem release explícita.

## Decisions

1. **SDK frontend `posthog-js` controlado por env**
   - Decisão: usar `posthog-js` no Vite e inicializar apenas com `VITE_POSTHOG_KEY`.
   - Racional: é a rota oficial e evita script manual no HTML; sem env, o wrapper vira no-op.
   - Alternativa considerada: snippet direto no `index.html`; rejeitado por dificultar tipagem, testes e controle por ambiente.

2. **Wrapper local de analytics**
   - Decisão: criar `frontend/src/lib/analytics.ts` para centralizar init/capture.
   - Racional: reduz acoplamento com PostHog e facilita desligar/trocar provedor no futuro.

3. **Eventos sem PII**
   - Decisão: eventos de lead usarão status técnico e attribution; não enviarão nome, email, WhatsApp, perfil ou dor.
   - Racional: analytics inicial precisa medir conversão por canal, não dados pessoais.

4. **Pageview manual**
   - Decisão: capturar pageview inicial manualmente após inicialização.
   - Racional: o app ainda não precisa de tracking complexo por rota; o mínimo validável é uma pageview inicial com path e attribution.

## Risks / Trade-offs

- [Risco] Chave ausente em DEV/PROD pode dar falsa impressão de bug de analytics. → Mitigação: wrapper no-op documentado e build validando sem env.
- [Risco] Enviar PII por engano em evento de formulário. → Mitigação: API do wrapper aceita payload explícito e o form só envia status/attribution.
- [Risco] Custo surpresa se o uso crescer. → Mitigação: decisão operacional registrada: free tier agora e billing limit antes de escala relevante.

## Migration Plan

1. Implementar wrapper e eventos em branch `card-268-posthog-analytics` sobre `develop`.
2. Validar build sem variáveis PostHog para garantir no-op seguro.
3. Configurar `VITE_POSTHOG_KEY`/`VITE_POSTHOG_HOST` somente no ambiente alvo quando Alan fornecer a chave do projeto PostHog.
4. Reiniciar apenas frontend DEV após integração/build quando necessário.

## Open Questions

- Chave real do projeto PostHog ainda não foi fornecida; implementação deve permanecer pronta e segura sem ela.
