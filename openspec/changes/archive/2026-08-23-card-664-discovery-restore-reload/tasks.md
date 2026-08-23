## 1. Contratos e persistência

- [x] 1.1 Formalizar o contrato admin-only de `GET /combos/discovery/sweeps/active` como `200 {"sweeps":[SweepDetail...]}` (lista completa, `[]` quando vazio), ordenação `created_at DESC, sweep_id DESC` e isolamento por ator.
- [x] 1.2 Estender o detalhe do sweep com o identificador necessário ao retry do mesmo rascunho, sem expor dados de outro ator.
- [x] 1.3 Cobrir no contrato de outbox a invariável de que sweep `running` com combinações pendentes nunca fica apenas com intent `acked`.

## 2. Backend e wake-up

- [x] 2.1 Implementar `GET .../sweeps/active` devolvendo todos os não terminais do ator (não um singleton) e validar ator em active, detalhe e leaderboard.
- [x] 2.2 Implementar `ensure_sweep_wakeup`/rotação transacional com lock do sweep, geração idempotente e preservação do intent quando já `delivered`.
- [x] 2.3 Integrar `resume` à garantia de wake-up sem iniciar trabalho durante `paused` ou `cancelling`.
- [x] 2.4 Fazer o dispatcher reparar sweep `running` com pendências e sem wake-up reclamável; substituir enqueue direto do próximo lote por rotação durável.
- [x] 2.5 Adicionar testes de concorrência, ACK anterior, broker indisponível, redelivery, pausa e corrida com cancelamento usando PostgreSQL de teste.

## 3. Frontend de recuperação

- [x] 3.1 Adicionar estado de recuperação inicial bloqueante e carregar active/history sem executar preflight ou habilitar start prematuramente.
- [x] 3.2 Hidratar controles, snapshot, draft key e congelamento a partir do sweep restaurado, mantendo o configurador editável quando não houver ativo.
- [x] 3.3 Restaurar o leaderboard da run ativa por padrão, preservar a seleção histórica separada e manter polling até estado terminal.
- [x] 3.4 Implementar estados loading, erro com retry, corrida terminal, paused/resume e atualização de histórico com foco, live region e targets acessíveis.
- [x] 3.5 Preservar o comportamento existente de Novo rascunho, preflight, start idempotente e seleção manual de run terminal.

## 4. Testes de produto e browser

- [x] 4.1 Atualizar testes unitários/integração do Discovery para recuperação de cada estado não terminal e ausência de ativo.
- [x] 4.2 Adicionar teste funcional Playwright: iniciar, recarregar, reencontrar o mesmo sweep/progresso e verificar que terminal não reaparece como ativo.
- [x] 4.3 Adicionar teste funcional Playwright: pausar, recarregar, retomar e observar avanço das combinações pending após wake-up.
- [x] 4.4 Validar protótipo e tela implementada em `1440×1000` e `390×844`, incluindo erro, paused, terminal, foco e ausência de overflow.
- [x] 4.5 Executar detector Impeccable, auditoria de acessibilidade e suíte de regressão de Combo/Discovery; evidência no Playwright e detector `[]` (sem reescrever `design.md` — digest I4).

## 5. Verificação e entrega

- [x] 5.1 Validar OpenSpec e marcar apenas tarefas comprovadamente implementadas e testadas.
- [ ] 5.2 Fazer smoke em DEV com PostgreSQL, worker de Discovery e uma varredura pequena; confirmar reload, resume, contadores reconciliados e conclusão.
- [x] 5.3 Atualizar o comentário do card com Gist dos artefatos, URL do protótipo e evidência do design antes de solicitar Aprovação de Design.
