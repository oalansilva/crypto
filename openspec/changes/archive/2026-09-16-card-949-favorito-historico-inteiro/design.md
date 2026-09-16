## Context

Card **#949**, Status=Design. Briefing = issue grelhado (DoD completo; Q1/Q2/Q3 aceites 2026-09-15). Não reentrevista.

Hoje, promover da Descoberta ou salvar no Combo **depois** de 70/30 copia as datas de **treino** para o favorito (testemunho BTC 1d 17/08/2017 → 24/12/2023) mesmo com período «todo». A lista, o resumo, o gráfico e a atualização leem esse pedaço. A grelha Decidir continua a ter de persistir o treino (ranking/Calmar/GO/NO-GO). Este card muda o **favorito novo**, não a grelha.

**Impeccable recorte (Operate):** audience = operador que promove/salva depois de 70/30 e lê Favoritos; outcome = período escolhido completo na lista/resumo/gráfico/atualização; direction = clone da página viva + delta das datas/números, sem redesign; scope = `/favorites` canónico, extras `/combo/discovery` e `/combo/results`.

UI impact: affected
live_route: /favorites
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações») no **index.html**. Extra 1: `/combo/discovery` em `descoberta.html` («Descoberta de estratégias swing», «Preflight», «Rascunho de varredura») — grelha Decidir 70/30. Extra 2: `/combo/results` em `analise.html` (`.combo-page`, «Lista de operações», «Análise da estratégia») — resumo/gráfico do favorito novo «todo». Extra 3: `/combo/results` em `combo.html` — Combo 2 anos + 70/30 + «Salvar nos Favoritos». Rota viva do save Combo = `/combo/results`, não `/combo/select` (catálogo de templates; sem copy deste card). Sem `/monitor`. `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Promover da Descoberta (período «todo») depois de 70/30: o favorito nasce primeira vela → agora. O testemunho 17/08/2017 → 24/12/2023 deixa de ser o período do favorito **novo**.
- Salvar no Combo depois de 70/30: o favorito cobre o período escolhido na tela, **completo**. 2 anos / 6 meses = esses meses/anos todos, não o treino, **não** «todo o histórico».
- Lista, resumo, gráfico e atualização do favorito novo mostram os números **desse** período completo (Q1). O treino não é o número da lista.
- Grelha Decidir permanece 70/30 (Calmar, cobertura, GO/NO-GO). Retrato da busca continua na Descoberta e não se legenda como desempenho do período completo.
- Só daqui pra frente (Q2): linha já salva com janela de treino **não** muda até um novo save.

**Non-Goals:**

- Preview do período completo no modal de promover.
- Migrar favoritos já salvos; recalcular varreduras antigas.
- Ranking 100%; acabar com o 70/30; treino e completo lado a lado na lista.
- Ampliar Combo 6 meses / 2 anos para «todo o histórico».
- Combo **sem** 70/30; #948 «Já existe»; #917 setas do gráfico; Monitor; Telegram.

## Decisions

1. **Janela operacional do favorito novo ≠ janela de treino da busca.**
   A grelha e o resultado persistido continuam no treino. O favorito novo grava o período escolhido completo. Alternativa «lista continua no treino» recusada (Q1-B). Alternativa «os dois lado a lado» recusada (Q1-C).

2. **«Todo» = primeira vela → agora; 6 meses / 2 anos não viram «todo».**
   Combo com 2 anos + 70/30 cobre esses 2 anos todos. Alternativa «Combo só entra em todo» recusada (Q3-A, era a recomendada). Alternativa «sempre primeira vela → agora mesmo em 2 anos» recusada (Q3-C).

3. **Só daqui pra frente.**
   Sem backfill. Quem já está na lista com 2017→2023 permanece até alguém salvar de novo. Alternativa migrar / só ao abrir recusadas (Q2-B/C).

4. **Mecanismo (P3 de Apply):** datas abertas, segundo backtest no promover, ou refresh imediato — desde que o operador veja o período completo e nunca o treino no lugar dele. O retrato da Descoberta (`metrics_snapshot`, Calmar, veredito) não ganha da lista nos favoritos novos.

5. **Combo save vive em `/combo/results`.** `/combo/select` só lista templates (`Available Templates`). Toggle 70/30 em `/combo/configure`; Combo sem 70/30 fora. Sem chave nova no catálogo: extras usam `/combo/discovery` e `/combo/results` já no yaml.

## Risks / Trade-offs

- [Risco] Apply copia só o rótulo «Todo» e deixa 17/08/2017 → 24/12/2023 → Mitigação: aceite = datas/números do período completo; o testemunho deixa de ser o período do favorito novo.
- [Risco] Lista nova herda Calmar/Return do treino → Mitigação: Q1 — números visíveis são do período completo; retrato fica na Descoberta.
- [Risco] Combo 2 anos vira histórico inteiro → Mitigação: linha ETH 2 anos no proto; spec Q3.
- [Risco] Backfill silencioso das linhas antigas → Mitigação: linha legado no proto (Q2) com 17/08/2017 → 24/12/2023 intacta.
- [Risco] Preview no modal entra por «clareza» → Mitigação: fora; modal igual ao vivo.

## Migration Plan

Sem migração de schema obrigatória para o operador. Rollback = o promover/salvar voltam a copiar o treino. Nenhum backfill: linhas já salvas ficam.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-949-favorito-historico-inteiro/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- Grade `/favorites` favorito **novo** Descoberta «todo»: Período **17/08/2017 → 15/09/2026** (primeira vela → agora). **Não** 17/08/2017 → 24/12/2023. Métricas = período completo (não as da grelha 70/30).
- Mesma grade, linha **já** salva (Q2): continua 17/08/2017 → 24/12/2023 até um novo save.
- Mesma grade, Combo **novo** 2 anos + 70/30: Período **15/09/2024 → 15/09/2026**. Não o treino (~até 02/2026). Não 17/08/2017.
- `/combo/discovery`: grelha Decidir ainda 70/30; Calmar/cobertura/NO-GO do treino; janela de busca 17/08/2017 → 24/12/2023 no retrato. Promover existe; modal **sem** preview do completo.
- `/combo/results` do favorito novo «todo»: resumo e gráfico no período completo, **não** «Resumo · janela de treino da Descoberta · 17/08/2017 → 24/12/2023».
- `/combo/results` Combo 2 anos + 70/30: «Salvar nos Favoritos» grava/mostra 15/09/2024 → 15/09/2026.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Segundo backtest no promover vs datas abertas + refresh vs gravar `period_type=all` com `end_date` nulo — desde que a tela mostre o completo.
- Nomes internos (`start_date`, `metrics_snapshot`, `promotion_metrics`).
- Combo `/combo/configure` copy do toggle; sem extra de clone (sem copy nova obrigatória).
- Detector `side-tab` nos cards mobile de tier (incumbente do clone).
- Truncagem do nome na coluna Estratégia (table-layout fixed vivo).
- Alvos 32px nos ícones da linha.
- Mock sem loading/vazio/erro.
- #917 setas; 32 vs 33 negócios.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/` → `frontend/public/prototypes/card-949-favorito-historico-inteiro/index.html`. Clone da página viva `/favorites` + delta (linha BTC nova no histórico inteiro; linha legado 2017→2023; linha Combo 2 anos completa). Landmarks: `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações».
- Extra Descoberta: `https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/descoberta.html` — grelha 70/30 + retrato de treino; Promover sem preview.
- Extra análise: `https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/analise.html` — resumo/gráfico do BTC novo no período completo.
- Extra Combo: `https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/combo.html` — 2 anos completos + Salvar nos Favoritos após 70/30.
- `cp`/clone = copied; delta de período/números = generated.
- Sem painel ANTES/DEPOIS como URL canónica.

## Prototype Validation

Playwright real (Chromium) em 2026-09-16, URL pública `https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/` + extras. Desktop 1440×900 e mobile 390×844. 8/8 PASS. curl 200 não substitui.

- **index (estado padrão + delta):** landmarks `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»). Desktop = mobile: BTC novo **17/08/2017 → 15/09/2026** (+210,40% / 71 / Sharpe 0,38); legado SOL **17/08/2017 → 24/12/2023**; Combo ETH **15/09/2024 → 15/09/2026** (+35,00% / 22). Sem 17/08/2017 → 24/12/2023 na linha nova «todo».
- **descoberta:** Decidir visível; retrato 70/30 treino 17/08/2017 → 24/12/2023; Calmar/GO-NO-GO da grelha; Promover sem preview do completo. Landmarks «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- **analise:** resumo/gráfico BTC **histórico inteiro 17/08/2017 → 15/09/2026**; **não** «Resumo · janela de treino da Descoberta · 17/08/2017 → 24/12/2023». `.combo-page` + «Lista de operações» + «Análise da estratégia».
- **combo:** 2 anos completos 15/09/2024 → 15/09/2026; chip 70/30 na busca; «Salvar nos Favoritos» grava esse período (não treino, não 2017).

Impeccable Operate: clone + delta. Tokens Binance (`--accent #fcd535`, `--bg-primary #0b0e11`). Detector: `side-tab` nos cards mobile de tier — incumbente, P3. Sem P0/P1 de produto no autor.

Verdict autor: **PASS**.

## Open Questions

Nenhuma. Fronteira veio grelhada; Q1/Q2/Q3 aceites. Preview no modal fora. `/combo/select` confirmado sem copy deste card.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B. Sem rework (zero P0 novo de produto). P3 aceitos; pai submete.

- Autor: [design-autor 949](bacfc60b-d662-472a-8bec-4f8f9f047dbc) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 949](d0bc768e-6fe4-4af8-a58b-62165403e57a) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Assessment B: [Assessment B 949](a76dd586-524f-4415-9183-e403ad85465c) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /favorites` / `surface: existing`.
- Proto: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/
- Extra Descoberta: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/descoberta.html
- Extra análise: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/analise.html
- Extra Combo: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/combo.html
- Snapshot T7: `.impeccable/critique/949-card-949-favorito-historico-inteiro.md`
- Snapshot A: `.impeccable/critique/949-card-949-favorito-historico-inteiro-assessment-A.md`
- Snapshot B: `.impeccable/critique/949-card-949-favorito-historico-inteiro-assessment-B.md`

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3** aceito (Apply, não reabrir): detector `side-tab` nos cards mobile de tier
- **P3** aceito: truncagem do nome na coluna Estratégia (table-layout fixed vivo)
- **P3** aceito: alvos 32px nos ícones da linha / 28px nas estrelas
- **P3** aceito: mock 71 negócios vs recorte da lista (33 tr); #917 fora
- **P3** aceito: clip da Ação «Promover» a 1440 (clone #944)
- **P3** aceito: Preflight 01 jan 2017 vs testemunho 17/08; leaderboard 309/26; thead clip no 390
- **P3** aceito: copy de contraste «não o treino» na análise; SVG vs setas; mock sem loading/vazio/erro
- **P3** aceito: mecanismo (segundo backtest vs datas abertas vs `end_date` nulo)
- **Disposition:** P3 aceites no Apply. Sem rework.

### Proxies

- `design.md` words: 1676
- HTML generated vs copied: 40437 vs 7718
- Spawns: 3
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

Design Agent verdict: PASS
