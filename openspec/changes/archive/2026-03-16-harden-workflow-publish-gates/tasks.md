# Tasks — harden-workflow-publish-gates

## 1. Workflow rules / Runtime
- [ ] 1.1 Definir o estado/semântica quando QA funcional passa mas publish/reconcile ainda não fechou.
- [ ] 1.2 Ajustar a lógica de promoção para evitar bloqueio ambíguo por upstream guard.
- [x] 1.3 Garantir que runtime stage, publish status e QA functional result fiquem explicitamente distinguíveis.

## 2. Handoff policy
- [ ] 2.1 Formalizar o checklist mínimo de DEV → QA para changes que afetam runtime/API/UI.
- [ ] 2.2 Formalizar a regra para só anunciar “pronto para homologação” após consistência completa.
- [ ] 2.3 Garantir comentário/handoff curto e claro quando faltar apenas publish/reconcile.

## 3. Validation / Tests
- [ ] 3.1 Cobrir o cenário “QA funcional green, stage blocked by guard”.
- [ ] 3.2 Cobrir o cenário de runtime stale versus código local correto.
- [ ] 3.3 Validar o fluxo final sem mensagens ambíguas para Alan.

## 4. Documentation
- [ ] 4.1 Atualizar a documentação operacional do workflow.
- [ ] 4.2 Registrar a nova regra de handoff e promoção entre DEV, QA e Homologation.
