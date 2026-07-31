## 1. OpenSpec e card

- [x] 1.1 Publicar artifacts OpenSpec no issue #337 (Gist + comentário)
- [x] 1.2 Confirmar Status=In Progress e branch `change-337-monitor-spot-stop-limit`

## 2. Backend

- [x] 2.1 Estender cliente Spot assinado (POST/DELETE) + helpers de filtros/arredondamento
- [x] 2.2 Service place/cancel/status de `STOP_LOSS_LIMIT` com qty 100% free e `cfstop_`
- [x] 2.3 Rotas autenticadas GET/POST/DELETE `/api/monitor/spot-stop-order`
- [x] 2.4 Testes unit/integration com mocks Binance (place, cancel, disabled/erros)

## 3. Frontend

- [x] 3.1 Bloco Proteção Spot no `ChartModal` (status + Proteger/Remover + confirmação)
- [x] 3.2 Atualizar copy da chave Binance em Meu Perfil (Spot trading opcional)
- [x] 3.3 E2E/visual proporcionais do bloco no chart

## 4. Fechamento

- [ ] 4.1 Code Review + commit/push + PR develop
- [ ] 4.2 QA gate verde + merge + `./restart` + Done técnico
