## Why

A base do PostHog já cobre o app React e a landing v4, mas a landing estática legada ainda precisa emitir os mesmos eventos mínimos do funil para evitar lacuna de análise caso algum canal ou link antigo continue apontando para ela.

## What Changes

- Adicionar configuração runtime de PostHog na landing legada sem chave hardcoded.
- Capturar eventos mínimos: pageview, submit started, submit accepted e submit failed.
- Reutilizar atribuição first-touch sanitizada já existente na landing.
- Garantir no-op seguro quando a configuração não existir.
- Criar teste Node para validar eventos sem PII.

## Impact

- Frontend estático em `frontend/public/prototypes/cripto-farol-landing/`.
- Sem alteração de backend, banco ou produção.
- DEV continua sendo o único ambiente afetado até homologação/release explícita.
