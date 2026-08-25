## Why

O backend assina e valida JWT HS256 com fallback versionado no repositório. Quem conhece esse `default conhecido` forja `access`/`refresh` para qualquer `sub` e passa em `get_current_user` / `get_current_admin`. P0 da varredura 2026-08-25 (DEV/PROD): o runtime precisa recusar secret ausente, igual ao default ou fraco, e rotacionar o valor em env para invalidar tokens já emitidos com o default.

## What Changes

- **BREAKING** (operacional): o processo de runtime DEV/PROD que assina ou valida JWT deixa de subir se `JWT_SECRET` estiver ausente, vazio/whitespace, igual ao `default conhecido`, ou com comprimento menor que 32.
- Um único critério de resolução de `JWT_SECRET` para `app.routes.auth`, `app.middleware.authMiddleware` e `app.services.oos_promotion_proof` (sem `os.getenv` com fallback do repo espalhado).
- Pytest é a única exceção: secret de teste explícito no `conftest`/monkeypatch; testes nunca usam o default do repo; cobertura do fail-closed e rejeição de token assinado com o default conhecido.
- Exemplo de env do backend documenta `JWT_SECRET` com placeholder, sem valor real.
- Rotação neste card: valor novo e forte no `.env` de DEV no Done/restart; PROD no release. Tokens HS256 antigos deixam de validar; usuários relogam. O valor não vai para git, `Environment=` do systemd, chat, issue ou evidência.
- Scripts one-off `scripts/card_262_*` e `scripts/card_277_*` deixam de carregar o fallback do default. Não são runtime.

Não entra: RS256, 2FA, cookie HttpOnly / revogar ao trocar senha (#694), cifrar `api_secret` Binance (#692), rate limit (#690), `.env.binance` (#687), rotas públicas P0 (#685/#686), UI/frontend, `Environment=` no systemd, log/journal do valor, checagem de entropia além do limiar de 32 + denylist.

## Capabilities

### New Capabilities

- `jwt-secret-fail-closed`: resolução fail-closed de `JWT_SECRET` no runtime que assina/valida JWT; rejeição de token assinado com o default conhecido; documentação de placeholder; secret de teste explícito; recorte dos scripts one-off.

### Modified Capabilities

- (nenhuma) — `login-password-mandatory` e demais specs de auth não mudam o contrato de login/password; este card adiciona o requisito do segredo de assinatura.

## Impact

- Runtime: `app.routes.auth`, `app.middleware.authMiddleware`, `app.services.oos_promotion_proof` (import-time `os.getenv` hoje).
- Testes: `backend/tests/conftest.py`, `backend/tests/unit/test_database_and_auth.py`, `backend/tests/unit/test_oos_promotion_proof_digest.py`.
- Docs/ops: exemplo de env do backend; `.env` DEV no Done; `.env` PROD no release. Units systemd continuam com `source` do `.env` e `Environment=` vazio para este segredo.
- Scripts: `scripts/card_262_*`, `scripts/card_277_*`.
- API HTTP de login/refresh não muda o JSON; sessão existente cai após a rotação (efeito colateral, `UI impact: none`).
- Workers que importarem o módulo de JWT herdam o fail-closed; workers que não usam JWT não precisam da variável.
