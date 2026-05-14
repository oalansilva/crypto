# Cripto Farol Leads

Servico operacional de captura de leads do beta fechado do Cripto Farol.

## Objetivo

- Receber `POST /api/leads` da landing publica.
- Criar acesso beta via backend FastAPI do repo `crypto`.
- Registrar lead na planilha local `.xlsx` e sincronizar Google Drive quando configurado.
- Notificar Telegram/Gmail quando configurado.

## Arquivos

- `server.js`: servidor HTTP de captura de leads.
- `package.json`: dependencias do servico.
- `.env.leads`: credenciais e tokens de runtime, nao versionado.
- `data/`: planilhas de leads, nao versionado.

Landing visual e assets ficam no frontend do repo:

- `frontend/public/prototypes/cripto-farol-landing-v4/`

## Validacao local

```bash
npm test
npm start
```

Depois validar `http://127.0.0.1:5174/health`.

## Guardrail

Nao versionar `.env.leads`, tokens, planilhas reais ou dados pessoais de leads.
