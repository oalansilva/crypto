## 1. Backend tail

- [x] 1.1 Adicionar `Depends(get_current_admin)` em `tail_log` (`logs.py`)
- [x] 1.2 Remover a chave `path` de todos os ramos de resposta do tail
- [x] 1.3 Testes: 401 sem token, 403 não-admin, 200 admin sem `path`

## 2. Forgot-password

- [x] 2.1 Remover e-mail, token e reset link do log INFO em `forgot_password`
- [x] 2.2 Teste de que INFO do fluxo não contém os três campos

## 3. Viewer

- [x] 3.1 Trocar `fetch` cru por `authFetch` (sessão + poll) em `BackendLogViewer`
- [x] 3.2 Mapear HTTP 401 e 403 no banner de erro existente (copy observável, sem redesenho)
- [x] 3.3 Atualizar testes de contrato do viewer para Authorization e 401/403
