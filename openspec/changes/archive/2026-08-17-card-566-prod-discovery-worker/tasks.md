## 1. Templates e installer

- [x] 1.1 Adicionar templates systemd PROD de dispatcher e Celery discovery
- [x] 1.2 Fazer o installer aceitar os dois roots canônicos (DEV e PROD) e recusar qualquer outro path
- [x] 1.3 Ligar `RUN_DISCOVERY_OUTBOX_DISPATCHER=1` no runtime-worker PROD sem desligar favorite refresh

## 2. Documentação

- [x] 2.1 Atualizar `docs/runtime-architecture.md` com units/flags/logs PROD de discovery

## 3. Rollout PROD (após Pronto para Dev)

- [x] 3.1 Instalar, enable e confirmar `active` dos workers afetados
- [x] 3.2 Smoke em PROD: sweep sai de pending/queued e processa na tela `/discovery` + `/api/health` 200 (consume da fila sozinho não fecha o card)
- [x] 3.3 Não redesenhar/reiniciar backend, frontend ou leads salvo necessidade operacional registrada

## 4. QA

- [x] 4.1 Teste do installer (path DEV, path PROD, path inválido)
- [x] 4.2 QA visual obrigatória (baseline inalterada)
