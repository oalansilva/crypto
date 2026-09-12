# Tasks — card-916-discovery-acompanhar-acoes

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Coluna Ação nas parciais

- [x] 1.1 — Thead das parciais ganha coluna Ação depois de CAGR, reusando `action-cell` / `action-stack` / `promote-action` / `discard-action` do Decidir (Promover amarelo, Excluir outline + lixeira). Sem ícones novos só no Acompanhando. Fidelidade ao proto.
- [x] 1.2 — Cada linha elegível do top-5 mostra Promover e Excluir sempre que as parciais estão visíveis (em curso, pausada, recuperada no F5).
- [x] 1.3 — NO-GO com amostra suficiente: selo visível; Promover enabled. Baixa amostra / duplicata / já promovido: mesmos bloqueios visíveis do Decidir; já promovido não oferece Excluir.

## 2. Diálogos reutilizados

- [x] 2.1 — Clique Promover nas parciais abre o diálogo actual «Promover a favorito tier 3» (sem seletor de tier). Clique Excluir abre «Excluir resultado».
- [x] 2.2 — Voltar / Fechar / overlay: candidato e varredura inalterados; foco volta ao gatilho.

## 3. Pós-ação

- [x] 3.1 — Confirmar promover: linha fica Favorito tier 3, ocupa o lugar no top-5, sweep não para; o mesmo `result_id` no Decidir mostra o estado promovido.
- [x] 3.2 — Confirmar excluir: some nas parciais e no Decidir da mesma varredura; o próximo já processado pode ocupar o lugar; rascunho não reabre; F5 não ressuscita. Refresh do top-5 (P3).
- [x] 3.3 — Se o POST recusar com sweep a correr, erro visível; sem API nova de desconfiança.

## 4. Fora e verificação

- [x] 4.1 — Top-5 não vira lista completa; Montar sem delta; Decidir inalterado (já tem as ações). Sem paginação/filtros no Acompanhando.
- [x] 4.2 — Testes: parciais com Promover/Excluir; NO-GO promove; pós-promover e pós-excluir; sync entre abas; Montar e Decidir sem regressão. Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 4.3 — `openspec verify` desta change.
