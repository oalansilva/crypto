## 1. OpenSpec e setup

- [x] 1.1 Publicar artefatos OpenSpec no card #268 antes de codar.
- [x] 1.2 Adicionar dependência `posthog-js` ao frontend.

## 2. Implementação frontend

- [x] 2.1 Criar wrapper `frontend/src/lib/analytics.ts` com inicialização condicional por env e no-op seguro.
- [x] 2.2 Integrar captura de pageview inicial com attribution sanitizada.
- [x] 2.3 Integrar eventos não sensíveis no fluxo do formulário de lead.

## 3. Validação

- [x] 3.1 Validar OpenSpec da change.
- [x] 3.2 Executar build frontend sem env PostHog para provar no-op seguro.
- [ ] 3.3 Registrar evidência técnica e próximos passos de configuração da chave PostHog.

Nota: usar as skills/regras do projeto quando aplicável a frontend, testes, debugging e revisão.
