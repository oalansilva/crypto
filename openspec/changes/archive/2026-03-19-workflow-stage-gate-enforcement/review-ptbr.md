# Review PT-BR — workflow-stage-gate-enforcement

## Resumo

Implementar validação no backend para impedir que cards pulem etapas no workflow.

## O que será feito

1. **Validação de Transição de Estágio**:
   - Validar se todas as etapas anteriores foram completadas antes de mover para próxima
   - Bloquear movimento se etapa foi pulada

2. **Rastreamento de Handoff**:
   - Adicionar campo `last_agent_acted` para rastrear qual agente atuou
   - Exigir comentário de handoff ao completar etapa

3. **API de Validação**:
   - Retornar erro 400 se tentar pular etapa
   - Mensagem clara explicando qual etapa foi pulada

## Estágios do Workflow
`pending → po → design → dev → qa → homologation → archived`

## Impacto
- Backend: validação no serviço de transição
- Runtime: work items rastreiam atividade por etapa

## Próximo passo
- Aprovação Alan → DEV (Codex) → QA → Homologação
