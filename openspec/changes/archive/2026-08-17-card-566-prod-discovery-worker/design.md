## Context

`/discovery` está em PROD sem dispatcher/Celery. O installer DEV recusa qualquer root ≠ `/srv/apps/dev/criptofarol/source`. O runtime-worker PROD já faz refresh de favoritos e não deve perder isso.

## Goals / Non-Goals

**Goals:**
- Templates + installer PROD.
- Dispatcher ligado sem desligar favorite refresh.
- Unit Celery `criptofarol-prod-discovery-worker`.
- Docs + evidência: active + consume + `/api/health` 200.
- Restart só dos workers afetados.

**Non-Goals:**
- Idempotência (#567).
- Redesign da tela.
- Candle-writer.
- Restart de backend/frontend/leads.

## Decisions

1. **Espelhar DEV, não fundir no backend.** Worker dedicado continua fora da API.
2. **Installer with DEV|PROD targets.** Accept only the two canonical roots; refuse anything else. DEV install remains working.
3. **Favorite refresh remains.** Flags PROD: refresh atual + `RUN_DISCOVERY_OUTBOX_DISPATCHER=1`.
4. **PROD só depois de Pronto para Dev.** Este card é a autorização de operação PROD após o arraste do Alan; o pedido genérico `implemente` sozinho não liga workers.
5. **Smoke = tela processando.** Fechar o card exige sweep saindo de pending na `/discovery` PROD, não só `celery inspect`.
6. **Sem drop-in no backend PROD.** Não copiar `criptofarol-dev-backend.service.d/discovery-workers.conf` para o backend PROD.
7. **UI impact: none.**

## UI impact

`none` — infra/systemd. A tela Discovery já existe e não muda.

## Prototype

N/A. Justificativa: sem delta visual; Alan valida units active e um sweep/consume.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Sweep em PROD gasta CPU/API] → Smoke mínimo ou evidência de consume da fila; não disparar varredura enorme.
- [Drop-in do backend DEV não se aplica a PROD] → Templates PROD próprios; não copiar drop-in DEV no backend PROD.
- [Dois runtime-workers] → Preferir ligar dispatcher no unit PROD já existente (refresh) em vez de segundo processo, salvo o unit DEV já ser dedicado e o PROD misturar rotinas — apply confirma o unit real antes de editar.

## Migration Plan

1. OpenSpec + Aprovação de Design.
2. Templates/installer na branch; testes de recusa de path inválido.
3. Após Pronto para Dev: instalar em PROD, enable, evidência.
4. Documentar runbook.

## Open Questions

Confirmar no apply se o `criptofarol-prod-runtime-worker` atual já mistura favorite refresh (provável) para só acrescentar a flag do dispatcher.

## Design Critique

- Escopo: workers PROD de discovery; tela `/discovery` não muda.
- Crítica isolada: P1 (installer só PROD, smoke só fila, drop-in backend) corrigidos — DEV+PROD canônicos, smoke na tela, sem restart de API/UI/leads.
- Superfície visual nova: nenhuma.

## Prototype Validation

N/A — sem protótipo navegável. Validação humana é a tela PROD processando, não um mock.

Design Agent verdict: PASS
