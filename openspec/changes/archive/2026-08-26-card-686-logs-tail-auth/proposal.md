## Why

`GET /api/logs/tail` é público: devolve conteúdo de `full_execution_log.txt` (até 256 KiB), o path de filesystem e HTTP 200 anônimo em DEV e PROD. O viewer do Combo faz poll sem Bearer. Forgot-password grava e-mail e reset link em INFO, então o tail vaza credenciais de recuperação. Fechar o endpoint e o log agora, antes de mais vazamento.

## What Changes

- **BREAKING:** `GET /api/logs/tail` exige `Depends(get_current_admin)`. Anônimo → 401; autenticado não-admin → 403.
- Resposta do tail **não** inclui path de filesystem (`path` ausente no JSON).
- Forgot-password **não** loga e-mail, token ou link de reset em INFO.
- `BackendLogViewer` envia `Authorization: Bearer` (via `authFetch` ou equivalente). Estados **401** (não logado) e **403** (não admin) são observáveis no banner de erro existente, sem redesenhar o modal.
- Testes cobrindo 401/403/200 admin e ausência de `path`; testes de que o log de reset não contém e-mail/token/link.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `log-viewer`: auth admin no tail; JSON sem path; cliente envia Bearer; 401/403 visíveis.
- `logging`: forgot-password não emite e-mail, token ou link em INFO.

## Impact

- Backend: `backend/app/routes/logs.py`, `backend/app/routes/auth.py` (forgot-password), testes de rota/log.
- Frontend: `frontend/src/components/BackendLogViewer.tsx` (só fetch + mensagem de 401/403). Combo continua o host; layout do viewer intacto.
- Superfícies: modal **Ver logs** em Combo. Sem rotação de arquivo de log.
