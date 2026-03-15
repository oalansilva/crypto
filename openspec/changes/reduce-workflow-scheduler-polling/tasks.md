# Tasks — reduce-workflow-scheduler-polling

## 1. Scheduler behavior
- [ ] 1.1 Definir regra de supressão para turnos repetidos sem mudança material.
- [ ] 1.2 Reduzir polling/rechecks quando o item ativo não mudou de estado.
- [ ] 1.3 Ajustar wake/cadência para privilegiar evento real em vez de inspeção frequente.

## 2. Workflow orchestration efficiency
- [ ] 2.1 Evitar shell-heavy reconciliation automática quando não houver novo milestone ou blocker.
- [ ] 2.2 Garantir que o scheduler não reenvie status ambíguo/repetido ao Alan.
- [ ] 2.3 Registrar claramente quando um turno foi suprimido por ausência de mudança material.

## 3. Validation
- [ ] 3.1 Cobrir o cenário de vários turnos consecutivos sem mudança.
- [ ] 3.2 Cobrir o cenário em que um evento real deve romper a supressão e avançar o fluxo.
- [ ] 3.3 Validar redução de rechecks redundantes no fluxo ativo.
