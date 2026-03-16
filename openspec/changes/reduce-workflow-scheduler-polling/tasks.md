# Tasks — reduce-workflow-scheduler-polling

## 1. Scheduler behavior
- [x] 1.1 Definir regra de supressão para turnos repetidos sem mudança material.
  - Implementado em `backend/app/services/workflow_polling_suppressor.py`
  - `WorkflowStateSnapshot` captura estado do workflow
  - `SuppressionState` gerencia contagem de supressões e timeouts
  - `should_run()` decide se scheduler deve rodar baseado em mudanças materiais
- [x] 1.2 Reduzir polling/rechecks quando o item ativo não mudou de estado.
  - Supressor detecta mudanças de estado via `detect_material_changes()`
  - Hash de estado para comparação eficiente
  - Contador de turnos suprimidos consecutivamente
- [x] 1.3 Ajustar wake/cadência para privilegiar evento real em vez de inspeção frequente.
  - API endpoint `/api/workflow/scheduler/should-run` retorna decisão
  - Force-run disponível via `/api/workflow/scheduler/force-run`
  - Timeout configurável (padrão 60 min) força execução

## 2. Workflow orchestration efficiency
- [x] 2.1 Evitar shell-heavy reconciliation automática quando não houver novo milestone ou blocker.
  - Supressor quebra apenas em "material changes" (approvals, handoffs, blockers)
  - Logs jelas indicam quando turno foi suprimido
- [x] 2.2 Garantir que o scheduler não reenvie status ambíguo/repetido ao Alan.
  - Supressão impede reenvio quando estado não mudou
  - only runs on actual state changes or timeout
- [x] 2.3 Registrar claramente quando um turno foi suprimido por ausência de mudança material.
  - Logs em nível INFO indicam decisão SUPPRESS vs RUN
  - Metadata inclui suppressed_count e suppressed_since

## 3. Validation
- [x] 3.1 Cobrir o cenário de vários turnos consecutivos sem mudança.
  - max_suppressed_turns (padrão 5) limita supressão consecutive
  - After max, força execução
- [x] 3.2 Cobrir o cenário em que um evento real deve romper a supressão e avançar o fluxo.
  - `should_run()` retorna True imediatamente quando material_change=True
  - Aprovals, handoffs, work item state changes rompen supressão
- [x] 3.3 Validar redução de rechecks redundantes no fluxo ativo.
  - API de status disponível em `/api/workflow/scheduler/status`
  - Tracking de suppressed_count e last_hash

## Implementation Details

### API Endpoints Added
- `GET /api/workflow/scheduler/should-run` - Decide se scheduler deve rodar
- `GET /api/workflow/scheduler/status` - Ver status atual da supressão
- `POST /api/workflow/scheduler/force-run` - Forçar próximo turno
- `POST /api/workflow/scheduler/configure` - Configurar parâmetros

### Configuration Options
- `suppression_enabled`: Enable/disable suppression (default: true)
- `max_suppressed_turns`: Max consecutive suppressed turns before force (default: 5)
- `suppression_timeout_minutes`: Timeout before forcing run (default: 60)

### Material Changes Detected
- approval_created/updated
- handoff_created
- workitem_state_changed/created/blocked
- change_status_changed/activated
- comment_added (threshold > 5 comments)
