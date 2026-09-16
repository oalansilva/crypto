UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 954: Acompanhar deixa de ficar stale nesta varredura

## Context

Card [#954](https://github.com/oalansilva/crypto/issues/954). Briefing = issue grelhado. DoD completo. Q1=A e Q2=B gravadas. Sem reentrevista.

O operador em `/combo/discovery` modo **Acompanhar** vê a varredura activa (`Sweep ativo`) parada em «EM CURSO / Varredura em execução / 0 de 1» e «Parciais ainda carregando», embora **essa mesma** run já tenha `completed` 1/1 no servidor — e, enquanto ainda corre, a linha do candidato pode não aparecer nas parciais depois de o resultado existir.

Testemunho DEV 2026-09-16 (~14h41 UTC−3), `crypto_app_dev`:

- Acompanhar: `#00e9a4d28e114099bc18fc85d5500df3`, chip EM CURSO, 0 de 1, parciais vazias, copy «separado do Histórico exibido».
- Banco: a mesma varredura já `completed` 1/1 (`completed_at` 17:39:20 UTC; `RS-263BF9A075`, Médias Móveis: Tendência em Virada, BTC/USDT 1d, `already_promoted`).
- O print do leaderboard «concluída» é o Histórico da run `#cc5e54036a814b0491fc3ec54cb51d22` (`RS-C100CF418A`) — **outra** varredura.

Hoje o progresso do Acompanhar actualiza `activeSweep` num intervalo curto (~2 s); `loadPartials` **não** corre nesse intervalo. O contrato #852 liga o separador Acompanhar só enquanto a run ainda não fechou; no terminal o código já pretende ir ao Decidir — o operador, sem F5, ficou no Acompanhar a mentir.

**Audience:** operador da Descoberta que está a seguir **esta** varredura no Acompanhar.
**Outcome:** parciais mostram o candidato assim que ele existe; quando o servidor fecha esta run, a vista passa ao ranking fechado no Decidir **desta** varredura, sem clicar e sem F5.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance, sem reescrever.
**Scope:** modo Acompanhar (progresso + parciais) e a transição visível para Decidir **desta** run. Montar só landmarks do catálogo.

Regiões clonadas (só estas): shell AppNav autenticado + heading + 3 modos + Montar (Preflight / Rascunho de varredura / «Descoberta de estratégias swing») + chrome Acompanhar + grelha de parciais + header/grelha Decidir. Delta só no estado a meio (progresso ≠ 0 de N + linha nas parciais) e no instante em que esta run fecha (Decidir desta, Acompanhar fora de EM CURSO).

## Goals / Non-Goals

**Goals:**

- A meio da run activa: se o candidato já existe, as parciais mostram a linha; «Parciais ainda carregando» não permanece.
- No mesmo estado, o contador não fica 0 de N se essa run já processou.
- Quando o servidor fecha esta run: Acompanhar deixa EM CURSO / «Varredura em execução» / 0 de N; sem clicar e sem F5 o operador vê o ranking fechado no **Decidir desta** varredura (candidato visível).
- Não há ecrã «Acompanhar já concluída».
- A copy «separado do Histórico exibido» pode ficar enquanto a activa ainda corre.

**Non-Goals:**

- Ecrã «Acompanhar já concluída» (Q1=A).
- Unir o Acompanhar ao Histórico/Decidir de **outra** run (Q1=A; o print `cc5e…` não é o conserto).
- Defaults do rascunho (#952); promoção/favorito 70/30 (#948/#949); Promover/Excluir nas parciais (#916); restaurar sweep depois de F5 (#664).
- Combo `/combo/select`, Favoritos, Monitor.
- Acelerar o worker / limites de fila.
- Inventar um ecrã novo além de Montar / Acompanhar / Decidir.

## Decisions

### 1. Relê parciais no mesmo intervalo do progresso

Enquanto a run activa for não-terminal, o intervalo que já pede o sweep activo (~2 s) SHALL também reler as parciais top-5 **desta** `sweep_id`. Se o GET do leaderboard já devolver o candidato, a linha aparece; a frase «Parciais ainda carregando» só existe enquanto essa leitura ainda não tiver linhas.

Rejeitado: esperar o fim da varredura para mostrar a linha (Q2=B). Rejeitado: websocket / outbox / hash de snapshot como produto (vocabulário `_Avoid` do issue). Rejeitado: F5 como conserto (#664 fora).

### 2. No término: Decidir **desta** run, hidratar o ranking

Quando o GET do sweep activo vier terminal, a UI SHALL: aplicar os contadores e o `state`; tratar `viewSweep` como **esta** run (não a selecção do Histórico); hidratar o leaderboard desta `sweep_id`; passar o modo visível para Decidir; o separador Acompanhar deixa de estar ligado (contrato #852). Sem ecrã intermédio «Acompanhar já concluída». Sem exigir clique nem F5.

Rejeitado: deixar o Acompanhar em EM CURSO com 0 de N. Rejeitado: mostrar o ranking da run do Histórico (`cc5e…`) como se fosse o fecho desta.

### 3. Progresso vem do mesmo GET; 0 de N só se ainda não processou

O chip e o `N de M` SHALL reflectir o `processed`/`total` do payload corrente desta run. Se o servidor já processou, o visível não fica 0 de N. Um payload terminal não é descartado só porque um `updated_at` anterior já foi aplicado.

### 4. Histórico de outra run permanece separado

Enquanto a activa corre, o Histórico pode mostrar outra run e a copy «separado do Histórico exibido» pode ficar. Isso **não** substitui o Acompanhar verdadeiro nem o Decidir desta no fecho.

## Risks / Trade-offs

- [Risco] GET do sweep e GET das parciais dessincronizam um intervalo → Mitigação: ambos no mesmo ciclo; a linha aparece no ciclo em que o resultado já existe; o progresso usa o mesmo GET do sweep.
- [Risco] Payload terminal ignorado (ordenação `updated_at`, poll em voo) → Mitigação: estado terminal desta `sweep_id` sempre aplica; P3 no Apply a localizar o skip.
- [Risco] Operador achar que o Histórico da outra run é o conserto → Mitigação: proto e aceite: Decidir **desta** `sweep_id` no fecho; abrir a outra run não conta.
- [Risco] Cache React de parciais vazias → Mitigação: cada ciclo do intervalo substitui as parciais; F5 não é o caminho feliz.

## Migration Plan

Sem schema. Deploy = frontend da Descoberta. Rollback = reverter o intervalo das parciais e a transição de modo; o servidor já fechava a run. Sem job de dados.

## Open Questions

Nenhuma. Q1=A e Q2=B gravadas. Mecanismo (mesmo intervalo + Decidir desta no término) fechado neste design.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B. Sem rework (zero P0 novo de produto). P3 aceitos; pai submete.

- Autor: [design-autor 954](c27d14f3-3f48-462e-9562-b5a918cb1646) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 954](b3407ee9-cefe-430a-aabd-de1b9e172d89) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Assessment B: [Assessment B 954](6e21451c-cdce-4093-b0b4-e3fc1285d16f) isolado; `model: cursor-grok-4.6-high`. **PASS**.

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

- **P0:** nenhum
- **P1:** nenhum
- **P3 aceito (Apply, não reabrir):** botão mock «Esta varredura fechou no servidor»; Ação clipa Favorito no desktop 1440; Montar condensado; truncagem do `<select>` no 390; placeholder «Acompanhando #—» no fecho; `result_id` nas parciais só em `data-result`; intervalo + payload terminal já no contrato Apply.

Digest proto: `0fd8679fa8fd421ead97b146106c59c63cd0e43cb9ef110c4053dc10b4c7634c` · 45393 bytes (disco == HTTPS). Snapshots: `.impeccable/critique/954-card-954-discovery-acompanhar-stale-assessment-A.md` e `-assessment-B.md`.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-954-discovery-acompanhar-stale/index.html` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- A meio: Acompanhar visível; progresso ≠ 0 de N se já processou; parciais com a linha do candidato (`RS-263BF9A075` no testemunho); sem «Parciais ainda carregando».
- No fecho desta run: Acompanhar não permanece EM CURSO / «Varredura em execução» / 0 de 1; Decidir **desta** run com o candidato; sem ecrã «Acompanhar já concluída»; sem clique e sem F5.
- Histórico de outra run aberto **não** é o conserto; a copy «separado do Histórico exibido» pode ficar enquanto a activa corre.
- Montar sem delta de produto (só landmarks). Promover/Excluir, ranking, Preflight, worker intactos.

**P3 aceito (Apply):** onde no intervalo do `refreshSweep` chamar a relida das parciais; não descartar payload terminal desta `sweep_id`; hidratar `loadLeaderboard` desta run ao passar a Decidir (já existe no ramo terminal — fechar a corrida com o Histórico); testes do poll a meio (linha + processed) e do tick terminal (modo Decidir desta, Acompanhar off). Sem websocket novo.

## Recorte

- **Audience:** operador da Descoberta a seguir a varredura activa.
- **Outcome:** parciais verdadeiras a meio; no fecho, Decidir desta run sem F5.
- **Direction:** clone da rota viva `/combo/discovery` + delta dos dois estados; Operate; sem new-work.
- **Scope:** Acompanhar + transição Decidir desta. Montar só landmark.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-954-discovery-acompanhar-stale/
- Path: `frontend/public/prototypes/card-954-discovery-acompanhar-stale/index.html`
- Digest: `0fd8679fa8fd421ead97b146106c59c63cd0e43cb9ef110c4053dc10b4c7634c` (45393 bytes; disco == HTTPS).
- Base: clone da página viva HEAD `/combo/discovery`. Arranque a partir do proto irmão `card-948-discovery-deleted-favorite` (chrome + grelha HEAD); landmarks e modos alinhados ao vivo. Sem painel ANTES/DEPOIS. T5 mede só este `index.html`.
- Landmarks (catálogo HEAD, substring): «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Clone vs delta: COPIED = shell AppNav, heading, 3 modos, selector de Histórico, rascunho, Preflight, chrome Acompanhar, casca das duas grelhas. DELTA = estado a meio (`#00e9a4d28e114099bc18fc85d5500df3` EM CURSO, 1 de 1, linha `RS-263BF9A075`, Histórico noutra run `cc5e…`) e, ao fechar esta run, Decidir desta com o mesmo candidato; Acompanhar deixa de estar EM CURSO. O botão «Esta varredura fechou no servidor» é só o mock estático do tick do servidor (a app viva não o tem).
- Estados navegáveis: default Acompanhar a meio; depois o fecho já no Decidir desta run. Montar permanece para landmarks.

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-954-discovery-acompanhar-stale/
- Path: `frontend/public/prototypes/card-954-discovery-acompanhar-stale/index.html`
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://, não curl).
- Ações: default Acompanhar a meio → Montar (landmarks) → Acompanhar (progresso + linha) → «Esta varredura fechou no servidor» → Decidir desta run.
- Asserts (mesmo critério nos dois viewports): landmarks «Descoberta de estratégias swing» / Preflight / Rascunho de varredura; a meio Acompanhar visível, progresso ≠ 0 de N, parciais com `RS-263BF9A075`, sem «Parciais ainda carregando»; no fim Decidir desta `#00e9a4d28e114099bc18fc85d5500df3` com o candidato; Acompanhar não permanece EM CURSO / «Varredura em execução» / 0 de 1; 0 console/pageerror.
- Pares `COPIED:start`/`COPIED:end`: 11/11; soma UTF-8 das regiões copiadas > 0. T5 mede só este index.html.
- Sem emitir PASS oficial de T5 (pai após A/B).
