# Tasks — card-949-favorito-historico-inteiro

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Promover da Descoberta após 70/30

- [x] 1.1 — Promover candidato validado em 70/30 com período «todo» persiste o favorito em primeira vela → agora (ex. BTC 17/08/2017 → 15/09/2026), não no fim do treino (testemunho 17/08/2017 → 24/12/2023).
- [x] 1.2 — A grelha Decidir da mesma varredura continua 70/30: ranking, cobertura, Calmar e GO/NO-GO intocados; o retrato da busca permanece na Descoberta.
- [x] 1.3 — Modal de promover **não** ganha preview do período completo neste card.

## 2. Salvar no Combo após 70/30

- [x] 2.1 — Save em `/combo/results` depois de 70/30 grava o período escolhido na tela, **completo**. 2 anos → 15/09/2024 → 15/09/2026 (não o treino, não 17/08/2017).
- [x] 2.2 — 6 meses / 2 anos **não** viram «todo o histórico» (Q3). Combo sem 70/30 permanece fora.

## 3. Lista, resumo, gráfico e atualização (Q1)

- [x] 3.1 — `/favorites`: linha nova «todo» mostra 17/08/2017 → 15/09/2026 e métricas do período completo (não Calmar/Return do treino da grelha).
- [x] 3.2 — Resumo e gráfico dessa linha (via `/combo/results`) usam o período completo; **não** o título «Resumo · janela de treino da Descoberta · 17/08/2017 → 24/12/2023».
- [x] 3.3 — Refresh automático/manual da linha nova corre no período completo (aberto até hoje no «todo»).

## 4. Só daqui pra frente (Q2)

- [x] 4.1 — Favorito já na lista com 17/08/2017 → 24/12/2023 **não** é migrado; muda só se alguém salvar de novo.
- [x] 4.2 — Sem backfill de varreduras antigas; `walk-forward-oos-gate` intocado.

## 5. UI, testes e evidência

- [x] 5.1 — Grade `/favorites` alinhada ao proto `index.html` (desktop = mobile): BTC novo, legado, Combo 2 anos; landmarks intactos.
- [x] 5.2 — Extra Descoberta (`descoberta.html`): grelha 70/30 + Promover sem preview.
- [x] 5.3 — Extra análise (`analise.html`) e Combo (`combo.html`): período completo vs 2 anos + «Salvar nos Favoritos».
- [x] 5.4 — Testes do promover/save/refresh e Playwright desktop+mobile contra o proto. Fora: #948, #917, Monitor.
- [x] 5.5 — `openspec verify` desta change.
