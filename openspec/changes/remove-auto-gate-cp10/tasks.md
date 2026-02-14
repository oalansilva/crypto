> Nota: use skills de `.codex/skills` quando aplicável (ex.: `openspec-apply-change`, `integration-test-planner`, `debugging-checklist`, `accessibility-basic-check`).

## 1. Remover gate CP10 do fluxo

- [ ] 1.1 Identificar no backend todos os pontos onde o CP10 atua como selection gate de decisão automática.
- [ ] 1.2 Remover branch/condição que aprova ou rejeita run automaticamente via CP10.
- [ ] 1.3 Garantir transição direta do pós-implementação para validação do Trader.

## 2. Consolidar decisão no Trader

- [ ] 2.1 Ajustar lógica para considerar somente veredito do Trader como decisão final.
- [ ] 2.2 Ignorar/remover flags legadas de auto-gate CP10 usadas para finalizar run.
- [ ] 2.3 Validar caminhos de estado para `approved`, `rejected` e `needs_adjustment` baseados no Trader.

## 3. Atualizar contrato de estado (API/UI)

- [ ] 3.1 Revisar payloads/serialização de run para não expor decisão automática de CP10.
- [ ] 3.2 Atualizar frontend para refletir que aprovação depende apenas do Trader.
- [ ] 3.3 Garantir consistência de labels/copy com a persona **Trader**.

## 4. Testes e validação

- [ ] 4.1 Criar/ajustar testes unitários para transições sem CP10.
- [ ] 4.2 Criar/ajustar testes de integração cobrindo o fluxo completo Trader-driven.
- [ ] 4.3 Executar checks do projeto e validar ausência de regressão no fluxo do Lab.

## 5. Rollout

- [ ] 5.1 Documentar mudança funcional (remoção CP10 e autoridade do Trader).
- [ ] 5.2 Preparar checklist de validação pós-deploy para runs novos.
