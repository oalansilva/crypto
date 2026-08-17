# Cripto Farol — Funil Social → Site → Lead

Use esta referência quando implementar ou revisar atribuição, analytics, captação de leads, PostHog/Metabase ou landings do Cripto Farol.

## Princípio operacional

- Ambiente padrão para funil/analytics: DEV em `/srv/apps/dev/criptofarol/source`.
- PROD só entra com pedido explícito de release/publicação.
- O funil precisa ligar: post social com UTM → landing/site → lead salvo → análise por canal.

## Atribuição UTM

Preferência técnica consolidada:

- Usar **first-touch attribution**: a primeira origem que trouxe o usuário deve ser preservada e não sobrescrita por visitas posteriores.
- Persistir a atribuição no navegador, normalmente em `localStorage`, antes do usuário submeter o lead.
- Enviar a atribuição junto do payload de `/api/leads` ou endpoint equivalente.
- Campos esperados: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `referrer`, `landing_path`, `first_seen_at`.

## Privacidade e sanitização

Ao gravar marketing metadata:

- Sanitizar `referrer` removendo query string e hash.
- Sanitizar `landing_path` mantendo somente parâmetros UTM permitidos.
- Descartar tokens, e-mails, IDs sensíveis e quaisquer parâmetros não permitidos.
- Não expor stdout/DB/log bruto em comentários públicos de card.

## Backend robusto

- Evitar validação de schema estreita demais para URLs/campanhas reais de marketing.
- Permitir campos longos no DTO/entrada quando seguro, e aplicar truncamento/sanitização na camada de serviço antes da persistência.
- Não deixar UTM longa causar erro 422 em criação de lead.

## PostHog / analytics de funil

Quando implementar PostHog ou analytics equivalente no Cripto Farol:

- Começar em DEV e manter PROD fora do escopo até pedido explícito de release/publicação.
- Usar configuração por ambiente, sem chave hardcoded: por exemplo `VITE_POSTHOG_KEY` / `VITE_POSTHOG_HOST` no app Vite e arquivo runtime vazio para landing estática.
- Sem chave configurada, o tracking deve ser no-op seguro: não quebrar build, app, landing ou captura de lead.
- Eventos mínimos úteis: pageview/landing view, submit started, submit accepted e submit failed.
- Eventos de funil não devem enviar PII: nome, e-mail, WhatsApp, perfil, texto livre de dor, tokens, IDs internos sensíveis ou URL completa.
- Não enviar `referrer` bruto para analytics, mesmo sanitizado sem query/hash: paths de referrer podem conter e-mail, invite/reset token ou ID sensível. Para análise de canal, reduzir para `referrer_domain`/domínio only; manter `referrer` completo/sanitizado apenas no payload de lead/backend quando necessário.
- Motivos de falha enviados ao analytics devem ser allowlisted/bounded (ex.: `submit_failed`, `network_or_runtime_error`), nunca `error.message` arbitrário, porque mensagens de runtime/fetch podem carregar URL, token ou payload sensível.
- Além de sanitizar payload explícito, tratar propriedades automáticas do SDK. No PostHog JS, use `before_send` para remover ao menos `$current_url`, `$initial_current_url`, `$referrer`, `$initial_referrer`, `$referring_domain`, `$initial_referring_domain`, `$search_engine`, `$search_keyword`, `$initial_search_engine` e `$initial_search_keyword` quando houver risco de query/referrer conter PII.
- Em landing estática sem bundler, não inventar stub parcial do PostHog. O loader `array.js` espera a fila de init em `window.posthog._i`; o snippet precisa criar `_i`, métodos de fila (`capture`, `identify`, `people.set`, etc.) e empilhar `[token, config, name]` antes de carregar o script. Stub que só faz `window.posthog.push(["init", ...])` pode não inicializar.
- Se o host PostHog for configurável, derive também o asset host do mesmo host quando possível; não deixar asset US fixo se o projeto puder usar EU/proxy/CSP.

## Validação mínima antes de Done técnico

Além de testes/build normais:

1. Validar script de captura na landing servida em DEV com URL contendo UTMs.
2. Fazer POST real de lead em DEV com payload de atribuição.
3. Verificar no banco/audit log que `metadata_json` ou campo equivalente gravou a UTM correta.
4. Confirmar que `referrer` e `landing_path` foram sanitizados.
5. Para PostHog/analytics, confirmar que o build passa sem chave configurada e que o SDK fica no-op seguro.
6. Revisar o diff procurando vazamento de PII explícito e propriedades automáticas de URL/referrer/search.
7. Em landing estática, revisar a compatibilidade do snippet com o loader real (`window.posthog._i` no PostHog `array.js`).
8. Validar health/service público DEV após restart dos serviços afetados.

## Evidência boa para reportar

- Endpoint DEV testado.
- Resultado do POST real (`accepted`, `created`, etc.).
- Campo de persistência verificado, sem colar dado sensível.
- Serviços reiniciados e ativos.
- Card em `Done técnico`, não `Pronto`, até homologação/release.