Apply só com `Status=Pronto para Dev`. MUST NOT `backend/**` produto nem `frontend/src/**`. MUST NOT `./restart` DEV. MUST NOT HTML / `frontend/public/prototypes/`. MUST NOT rollback de disco. `AGENTS.md` always-on MUST NOT crescer.

## 1. Overlay inventário PROD

- [x] 1.1 Em `.covenant-flow/overlay.yaml` `environments.prod.services`, acrescentar `criptofarol-prod-discovery-worker.service` junto dos demais de longa duração
- [x] 1.2 Declarar `environments.prod.oneshot_services` com `criptofarol-prod-candle-writer.service` e `criptofarol-prod-telegram-alert-scan.service` (subconjunto de `services`)
- [x] 1.3 P3: validar o subconjunto em `scripts/process-fsm/overlay.py` só se o parser já rejeitar chaves extra; senão o guard lê a chave e o overlay doc basta

## 2. Runbook overlay on-demand

- [x] 2.1 Em `docs/crypto-overlay.md`, a janela do publish PROD reinicia `services` − `oneshot_services` (não «services afetados» memorizados); oneshot ficam fora da janela; a nota `docs/release-<data>.md` lista a partir do inventário
- [x] 2.2 Recortar `covenant-flow-environments` só se o pin ainda mandar reiniciar `services[]` sem subtrair oneshot; `AGENTS.md` MUST NOT crescer; `./restart` DEV MUST NOT mudar

## 3. Guard: evidência completa da janela

- [x] 3.1 Em `scripts/release-guard` `post` (e `pre` quando já exige evidência), recusar se `services=` omitir qualquer unit da janela overlay; normalizar com/sem `.service`; oneshot extra = warn
- [x] 3.2 Evidência no estilo 16/09 (backend, frontend, leads, runtime-worker sem discovery-worker) MUST falhar

## 4. Guard: código velho vs processo parado

- [x] 4.1 Recusar se um unit da janela **activo** tiver arranque anterior à janela deste deploy (`ExecMainStartTimestamp` ou equivalente; P3 campo e âncora)
- [x] 4.2 Q2 B: unit da janela inactive/failed + `release.health_url` ok → não bloquear; `services=` continua a ter de listar esse unit; MUST NOT desfazer disco

## 5. Testes do guard

- [x] 5.1 Cobrir em `backend/tests/integration/test_release_guard.py` (ou equivalente): janela incompleta falha; janela completa passa; oneshot extra = aviso; activo em código velho falha; parado + health ok passa
- [x] 5.2 P3: fixtures sintéticas `services=app` — ou passam a declarar janela mínima, ou usam overlay de teste; MUST NOT exigir cronómetro da Descoberta

## 6. Verificação

- [x] 6.1 `openspec validate --change "card-968-prod-restart-long-running"` verde; UI impact none; Prototype N/A
- [x] 6.2 Diff sem `backend/` produto, sem `frontend/src/**`, sem `./restart`, sem HTML de protótipo; próximo publish é que usa a janela — não reescrever `docs/release-2026-09-16.md` como entrega
