UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 916: Promover / Excluir nas parciais do Acompanhando

## Context

Card [#916](https://github.com/oalansilva/crypto/issues/916). Briefing = issue grelhado. Q1–Q7=A. Sem reentrevista.

`/combo/discovery` aba Acompanhando já mostra parciais top-5 (selo GO/NO-GO + seis métricas) sem coluna de ação. Promover e Excluir existem só no Decidir. APIs já agem no candidato, não na varredura.

**Audience:** administrador da Descoberta com varredura longa, decisão já tomada nas parciais.
**Outcome:** promover ou excluir sem mudar de aba; Decidir continua com a lista completa.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance, sem reescrever.
**Scope:** coluna Ação nas parciais + estado pós-ação + os dois diálogos reutilizados.

Regiões clonadas (só estas): shell AppNav + heading + 3 modos + parciais Acompanhando + Decidir + Montar (Preflight / Rascunho / «Descoberta de estratégias swing» para landmarks). Delta = coluna Ação nas parciais (e pós-ação). Decidir já tem Promover/Excluir — clona, não redesenha. Montar sem delta.

## Goals / Non-Goals

**Goals:**

- Promover e Excluir em cada linha elegível das parciais, visíveis com sweep em curso / pausada / recuperada.
- Mesmos diálogos de hoje (tier 3; descarte). Cancelar não mexe.
- NO-GO: selo visível; Promover enabled se elegível.
- Pós-promover: Favorito tier 3 no lugar; sweep segue.
- Pós-excluir: some nas duas abas; próximo processado pode ocupar o lugar; rascunho não reabre.
- Top-5 continua top-5.

**Non-Goals:**

- Lista completa / paginação / filtros no Acompanhando.
- Montar; motor; ranking; selo; Calmar; métricas da grelha (#906); Favoritos (#897).
- Apagar favorito já promovido; reabrir Promover no Decidir (#896); redesign da aba.

## Decisions

### 1. Mesmo `action-stack` do Decidir nas parciais

Reutilizar `action-cell` / `promote-action` / `discard-action` (Promover amarelo, Excluir outline vermelho + ícone lixeira). Não inventar ícones só no Acompanhando. Bloqueios baixa amostra / duplicata / já promovido iguais ao Decidir. Amostra insuficiente continua fora do top-5.

Rejeitado: atalho sem diálogo; só ícone; só Promover.

### 2. Diálogos globais, não por aba

Os diálogos actuais (Promover a favorito tier 3; Excluir resultado) já estão fora do switch de modos. Acompanhar só passa o `result_id` alvo. Cancelar / Voltar / overlay click devolve foco ao gatilho.

Rejeitado: diálogo novo; confirmar inline.

### 3. Pós-ação no top-5, sweep intacto

Promover: a linha permanece, CTA vira «Favorito tier 3», rank não muda, progresso não para. Excluir: some nas parciais e no Decidir da mesma varredura; o 6.º já processado pode entrar; F5 não o ressuscita; «novo rascunho» não dispara. Refresh do top-5 é P3 de Apply (reuso do fetch de parciais).

Rejeitado: parar a varredura; reabrir Montar.

### 4. Largura: 7.ª coluna nas parciais

Desktop: overflow-x já existente; Ação à esquerda como no Decidir. Mobile ≤720px: `action-cell` full-width, botões 100% — o mesmo card-stack.

## Risks / Trade-offs

- [Risco] Coluna Ação aperta as seis métricas → Mitigação: overflow-x desktop; cards mobile.
- [Risco] Backend recusar promote/discard com sweep a correr → Mitigação: produto exige ação no candidato visível; Apply confirma o endpoint; se furar, fecha o contrato sem API nova de desconfiança.
- [Risco] Operador promover um NO-GO que depois cai no ranking → Mitigação: igual ao Decidir — age no candidato visível.

## Migration Plan

Sem schema. Rollback = omitir a coluna nas parciais. Diálogos e APIs já existem.

## Open Questions

Nenhuma. Q1–Q7=A.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-916-discovery-acompanhar-acoes/index.html` como spec de layout. Sem HTML neste arquivo.

**Contrato visível (não P3):**

- Parciais visíveis: coluna Ação com Promover e Excluir em cada linha elegível.
- NO-GO: selo + Promover enabled se elegível.
- Mesmos diálogos; cancelar não mexe.
- Pós-promover: Favorito tier 3; lugar no top-5; sweep segue.
- Pós-excluir: some nas duas abas; próximo pode ocupar; rascunho fechado.
- Top-5 não vira lista completa. Montar sem delta. Decidir inalterado.

**P3 aceito (Apply):** ligar os botões das parciais aos handlers/diálogos já no Decidir; refresh do top-5 após discard; `min-width` da tabela; sync de estado Decidir↔parciais no mesmo `result_id`; se o POST recusar com sweep running, tratar o erro visível sem inventar API.

## Recorte

- **Audience:** administrador a decidir nas parciais de uma varredura longa.
- **Outcome:** Promover/Excluir sem ir ao Decidir.
- **Direction:** clone da rota viva + coluna Ação; Operate; sem new-work.
- **Scope:** parciais Acompanhando; Decidir e Montar só clone/landmarks.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-916-discovery-acompanhar-acoes/
- Path: `frontend/public/prototypes/card-916-discovery-acompanhar-acoes/index.html`
- Digest: `567efe740215a257` (sha256 completo `567efe740215a257cdcf079ebfed208fd3982c47e6fd8e89d6ce8b21842e51c5`, 63795 bytes; HTTPS == disco).
- Base: clone de `/combo/discovery` (HEAD desta branch, pós-#906) + delta da coluna Ação nas parciais. Sem painel ANTES/DEPOIS.
- Landmarks: «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Estado default: Acompanhando, sweep em curso `#3d9bee8b`, parciais top-5 com NO-GO e coluna Ação.

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-916-discovery-acompanhar-acoes/
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://).
- Disco == HTTPS após polish mobile do chip Favorito.
- Ações: default Acompanhar → Promover (cancelar) → Promover (confirmar) → Excluir CFX → Decidir (sync) → Montar (landmarks).
- Asserts (38/38 PASS nos dois viewports): landmarks 3/3; default Acompanhar com coluna Ação; NO-GO + Promover enabled; diálogo tier 3; cancelar não mexe; pós-promover Favorito tier 3 no lugar e sweep 309/697 EM CURSO; pós-excluir some + DOT ocupa; Decidir sync; Montar Preflight/Rascunho sem parciais; 0 Antes/Depois; 0 console/pageerror.
- Detector `detect.mjs`: `[]`.
- Resultado: **PASS** (autor). Dupla A/B e `## Design Critique` ficam no pai.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 (aceito, Apply):** Montar condensado vs vivo; classes `.promote` vs `promote-action`; trap Tab nos handlers vivos; PAUSADA não mockada à parte; duplicata ausente nas parciais; Decidir mock vs copy 309/26; ranks 1,2,4,5,6 pós-excluir; `min-width` da tabela / overflow 390; chrome Acompanhar abaixo da dobra em 390×844; chip NO-GO full-width; diálogo mobile 2-col; erro POST com sweep running (já no contrato Apply).
- **Disposition:** P3 no Apply. Sem rework. Q1–Q7=A intactas.
- **Pendências não bloqueantes:** largura 7 colunas em ecrã estreito (scroll horizontal); Decidir já tem as ações — não redesenhar.
- Proto: https://dev.criptofarol.com.br/prototypes/card-916-discovery-acompanhar-acoes/ · digest `567efe740215a257`
- Snapshot T7: `.impeccable/critique/916-card-916-discovery-acompanhar-acoes.md` (A: `…-assessment-A.md` · B: `…-assessment-B.md`)
- Design Agent verdict: PASS
