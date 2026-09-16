UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 948: candidato volta a Promover depois de excluir o favorito

## Context

Card [#948](https://github.com/oalansilva/crypto/issues/948). Briefing = issue grelhado. DoD completo. Q1 e Q2 aceites (2026-09-15). Sem reentrevista.

O administrador, em `/combo/discovery` modo Decidir (e Acompanhar se a linha ainda estiver visível), continua a ver **Já existe** / **Equivale ao favorito ativo N** ou **Favorito tier 3** depois de o favorito N ter saído da lista. A promoção recusa «já duplica favorito ativo» para um N que já não existe. Testemunho original: candidato Médias Móveis: Tendência em Virada, `RS-E2FF8F9FEB`, varredura `af8fb5dee323462c98baa5c492f0fbfb`; favorito `9` MISSING. A limpeza operacional pontual em PROD desses snapshots **não** é o conserto.

Hoje o leaderboard devolve o `dedup_state` **já gravado**. A promoção recusa `duplicate_favorite` / devolve `already_promoted` **sem olhar** se o favorito ainda existe. `DELETE /favorites/{id}` apaga a linha e **não** reclassifica candidatos. A spec canónica fala de inativo/arquivado → `historical_duplicate_favorite`; esse estado **não existe no código**. Exclusão real é o produto de hoje. Q1 recusou nota histórica visível.

**Audience:** administrador da Descoberta que acaba de tirar uma estratégia dos favoritos e volta a Decidir (ou Acompanhar) na mesma varredura.
**Outcome:** a grelha e o botão de promover dizem a mesma verdade da lista real: órfão = Promover, sem nota de favorito; favorito vivo = Já existe.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance, sem reescrever.
**Scope:** grelha Decidir + parciais Acompanhar. Montar só landmarks do catálogo.

Regiões clonadas (só estas): shell AppNav autenticado + heading + 3 modos + Montar (Preflight / Rascunho de varredura / «Descoberta de estratégias swing») + chrome Acompanhar + grelha de parciais + header/grelha Decidir. Delta só nas células de acção/nota das linhas órfãs vs vivo.

## Goals / Non-Goals

**Goals:**

- Depois de excluir o favorito, a linha que dizia **Já existe** / **Equivale ao favorito ativo N** volta a **Promover**, sem nota de favorito (Q1).
- A linha **Favorito tier 3** da mesma exclusão também volta a **Promover** (Q2).
- Tentar promover é aceite e cria um favorito novo; grelha e servidor dizem a mesma verdade.
- A linha permanece na varredura; não some só porque o favorito foi excluído.
- Decidir e Acompanhar (quando a mesma linha ainda estiver visível) mostram a mesma verdade.
- Favorito **ainda** na lista: **Já existe** / **Equivale ao favorito ativo N** e o bloqueio permanecem.

**Non-Goals:**

- Clicar **Excluir** na grelha (descartar o candidato desta varredura). Não apaga favorito.
- Nota histórica «já esteve nos favoritos».
- Continuar sem Promover / aposentar a identidade nesta grelha.
- Só corrigir Já existe e deixar Favorito tier 3.
- Inventar arquivar/inativar na lista de favoritos (o produto exclui de verdade).
- Redefinir equivalência, ranking Calmar, Preflight, worker, filtros, selo NO-GO, amostra insuficiente.
- Redesign dos três modos.
- Limpeza operacional pontual em PROD (já feita; não é o conserto).

## Decisions

### 1. Mecanismo: reclassificar o gravado **e** reler na hora

Os dois. Apagar o favorito dispara reclassificação append-only dos resultados que apontam para esse N (`duplicate_favorite` ou `already_promoted` → current `unique`). Leaderboard/parciais e promoção **também** relêem se o `dedup_reference` ainda existe na lista. Assim: (a) a grelha deixa de mentir no próximo GET; (b) um GET/POST que chegue antes da reclassificação persistida, ou um estado residual, não recusa fantasma.

Rejeitado: só persistir (a promoção ainda mente se o GET for stale ou se o hook de delete falhar). Rejeitado: só reler (o estado gravado continua a mentir em qualquer leitor que não passe no mesmo helper; o print do issue era exactamente isso).

### 2. Estado visível = `unique`; sem `historical_duplicate_favorite` na grelha

A classificação **corrente** do resultado passa a `unique` e `dedup_reference` some. A evidência anterior permanece queryable em `discovery_dedup_evidence` (append-only). A grelha **não** mostra nota de que já foi favorito (Q1). O estado canónico `historical_duplicate_favorite` **não** entra no payload da grelha neste card — o frontend hoje só ramifica `duplicate_favorite` / `already_promoted` / resto; inventar um terceiro rótulo visível violaria Q1.

Rejeitado: persistir `historical_duplicate_favorite` como estado corrente (obrigaria copy nova ou um ramo que a grelha não tem). Rejeitado: soft-delete / arquivar o favorito só para satisfazer a spec de inativo.

### 3. Frontend só reflecte o payload verdadeiro

`DiscoveryPage.tsx` continua a mapear `duplicate_favorite` → **Já existe** + **Equivale ao favorito ativo N**, e `already_promoted` → **Favorito tier 3**. Sem copy nova. Sem nota histórica. Apply não precisa de ramo de UI para «órfão» se o backend já enviar `unique`.

### 4. Re-promover cria outro favorito (número novo)

Facto do produto: a linha do favorito some de verdade. Confirmar Promover num órfão cria um favorito **novo**. Não reutilizar o N apagado. Não é opção deste card.

### 5. Outros bloqueios reais permanecem

Baixa amostra, amostra insuficiente, discarded, duplicata de favorito **vivo**, selo NO-GO (alerta, política actual). **Excluir** na grelha continua a recusar se `already_promoted` **ainda** for verdade; depois da exclusão do favorito, a linha órfão volta a poder ser excluída da varredura (comportamento de `unique`).

## Risks / Trade-offs

- [Risco] GET do leaderboard corre antes do commit da reclassificação no DELETE → Mitigação: reler existência do favorito na serialização (`_result_row` / rank) e na promoção; o payload corrente não mente mesmo com estado gravado stale.
- [Risco] Resultado aponta para N por `dedup_reference` **ou** só pela identidade, se o reference estiver podre → Mitigação: o DELETE reclassifica por reference = N; a relida na hora também consulta a lista viva por `strategy_identity_key` (já existe na promoção). Sem redefinir equivalência.
- [Risco] Cache React de uma varredura já aberta → Mitigação: o próximo fetch (abrir Decidir/Acompanhar, F5, troca de run) traz o payload verdadeiro; sem copy de «atualizar». Fora: polling novo.
- [Risco] Spec canónica `historical_duplicate_favorite` vs exclusão real → Mitigação: este card trata exclusão real; não inventa arquivo na lista. Rasto interno não aparece na grelha.
- [Risco] Operador achar que a linha tinha de desaparecer (Q1 ≠ D) → Mitigação: proto mostra a linha no sítio, com Promover.

## Migration Plan

Sem schema novo. Sem soft-delete. Deploy: o hook no DELETE + relida no GET/POST bastam para órfãos já gravados; não precisa de job one-shot em PROD (a limpeza pontual do favorito 9 já aconteceu e **não** substitui o hook). Rollback = reverter o hook e a relida; resultados entretanto reclassificados para `unique` continuam verdadeiros (favorito segue inexistente).

## Open Questions

Nenhuma. Q1/Q2 aceites. Mecanismo (os dois) fechado neste design.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-948-discovery-deleted-favorite/index.html` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- Órfão que era **Já existe** / **Equivale ao favorito ativo N**: botão **Promover**; sem essa nota; linha ainda na grelha.
- Órfão que era **Favorito tier 3**: deixa o rótulo e mostra **Promover**.
- Favorito vivo: **Já existe** + **Equivale ao favorito ativo N** permanecem.
- Confirmar Promover no órfão cria favorito novo; sem recusa fantasma para o N apagado.
- Decidir e Acompanhar (se visível) iguais. Montar sem delta. **Excluir** da grelha inalterado quanto a não apagar favorito.
- Sem nota histórica.

**P3 aceito (Apply):** onde exactamente no `DELETE` dos favoritos chamar a reclassificação; helper partilhado de «favorito ainda existe?» usado por `_result_row`, parciais, `promote_result` e `discard_result`; append em `DiscoveryDedupEvidence` com a classificação corrente `unique` (sem novo enum visível); testes de integração do GET/POST com N MISSING vs N vivo; o frontend só muda se o payload ainda mentir.

## Recorte

- **Audience:** administrador da Descoberta depois de excluir um favorito.
- **Outcome:** órfãos voltam a Promover, sem nota; vivo continua Já existe; promoção e grelha coincidem.
- **Direction:** clone da rota viva `/combo/discovery` + delta das acções órfãs; Operate; sem new-work.
- **Scope:** duas grelhas; Montar só landmark. Sem copy nova.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-948-discovery-deleted-favorite/
- Path: `frontend/public/prototypes/card-948-discovery-deleted-favorite/index.html`
- Digest: `1f8b13c879526506` (sha256 completo `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74`).
- Base: clone da página viva HEAD `/combo/discovery`. Arranque a partir do proto irmão `card-944-discovery-favorites-nomenclature` (já com nomenclatura e acções); landmarks e chrome reforçados contra o catálogo HEAD. Sem painel ANTES/DEPOIS. T5 mede só este `index.html`.
- Landmarks (catálogo HEAD, substring): «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Clone vs delta: COPIED = shell AppNav, heading, 3 modos, rascunho, Preflight, chrome Acompanhar, casca das duas grelhas. DELTA = linhas órfãs com Promover (sem nota Equivale…; sem Favorito tier 3) + linha viva com Já existe / Equivale ao favorito ativo 12. Default = Decidir (testemunho do print).
- Estado default: varredura concluída `af8fb5dee323462c98baa5c492f0fbfb`; rank 1 = `RS-E2FF8F9FEB` (órfão Já existe → Promover, BTC/USDT 1d); rank 2 = `RS-EA2A508DBD` (órfão tier 3 → Promover); rank 3 = favorito vivo 12 (Já existe).

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-948-discovery-deleted-favorite/
- Path: `frontend/public/prototypes/card-948-discovery-deleted-favorite/index.html`
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://, não curl).
- Disco == HTTPS: sha256 `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74`.
- Ações: default Decidir → órfãos e vivo → Acompanhar (mesma verdade) → Montar (landmarks visíveis) → voltar a Decidir.
- Asserts (70/70 nos dois viewports): landmarks «Descoberta de estratégias swing» / Preflight / Rascunho de varredura; default Decidir; órfão `RS-E2FF8F9FEB` **Promover**, sem **Já existe**, sem **Equivale ao favorito ativo N**, linha permanece; órfão `RS-EA2A508DBD` **Promover**, sem **Favorito tier 3**, sem essa nota, linha permanece; vivo **Já existe** + **Equivale ao favorito ativo 12**; Acompanhar igual; 0 console/pageerror.
- Pares `COPIED:start`/`COPIED:end`: 11/11, soma UTF-8 31521 (> 0). T5 mede só este index.html.
- Detector `detect.mjs`: `[]`.
- Resultado do gate do autor: asserts verdes. Sem emitir PASS de T5 (pai após A/B).

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 (aceito, Apply):** Montar condensado vs vivo; Ação clipa (`Prom` / `Já e`) em 1440×900; testemunhas abaixo da dobra em 390×844; leaderboard mock 680/680; `data-label` Win rate / Maximum Drawdown; hook DELETE + relida na hora; nav/CSS vars de shell.
- **Disposition:** P3 no Apply. Sem rework. Q1/Q2 intactas. Dupla A/B PASS.
- Proto: https://dev.criptofarol.com.br/prototypes/card-948-discovery-deleted-favorite/ · digest `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74`
- Snapshot T7: `.impeccable/critique/948-card-948-discovery-deleted-favorite-assessment-A.md` · `.impeccable/critique/948-card-948-discovery-deleted-favorite-assessment-B.md`
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
- Proxies: `design.md` words + HTML generated 37769 vs copied 31389 · spawns 4 (1 autor abortado + restage + A + B)

Design Agent verdict: PASS
