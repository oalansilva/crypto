# Design: Descartar resultado de Discovery

Card [#663](https://github.com/oalansilva/crypto/issues/663). Change `card-663-discovery-discard`.

## UI impact

**affected** — coluna Ação do leaderboard de Discovery + modal de exclusão. Tela existente `/combo` Discovery.

## Problem / user / hypothesis

Administrador revisa o leaderboard após a varredura. Sem descarte, candidatos ruins ficam para sempre; promoção bloqueada parece “não ter opção de promover”. Hipótese: manter Promover visível (com motivo) e adicionar Excluir com confirmação resolve o destino do candidato.

## Decision

- Estado persistido `discarded` no resultado (não DELETE físico da evidência, para auditoria).
- GET leaderboard default: `status != discarded`.
- POST `.../results/{result_id}/discard` (admin, 403 senão).
- UI: botões Promover + Excluir empilhados na célula; Excluir estilo `cancel-button` (não CTA amarelo).
- Modal de exclusão espelha o de promoção (identidade + sweep/result) com Confirmar exclusão. Título: **Excluir resultado**.
- Linha já promovida: sem Excluir neste card.

## Prototype

- URL HTTP: `https://dev.criptofarol.com.br/prototypes/card-663-discovery-discard/`
- Path: `frontend/public/prototypes/card-663-discovery-discard/index.html`
- Base: protótipo `card-469-varredura-backtest` / tela Discovery atual (shell 224px, tokens, nav Combo).
- Delta: ações Promover+Excluir; modal exclusão; linha some após confirmar; fixture `RS-1100` já promovida.
- Desktop e mobile.

## Risks

- Rank global após omitir descartados precisa recomputar entre restantes (protótipo chama `recomputeRanks`; apply precisa no GET).
- Não confundir com cancelar a varredura inteira (copy do modal).

## Impeccable Brief

- Job: admin decide promover ou descartar cada candidato.
- Outcome: coluna Ação sempre mostra o par de destinos quando permitido; descarte some do ranking.
- Direction: Operate, refinement do produto atual, não layout paralelo.
- Scope: só leaderboard + modal; rascunho/preflight/progresso intactos.
- States: ranking; baixa amostra (promover disabled); duplicata; promovido sem Excluir; modal exclusão; pós-exclusão; cancelar modal.
- Interaction: 44px; confirmação; Escape/backdrop/foco no close.
- Constraints: DESIGN.md tokens; PT-BR; sem lixeira.

## Impeccable Critique

### Assessment A (Task isolada, inherit)

P0: Excluir em promovido; `data-result=unknown`; a11y modal. P1: ranks/contagem; copy “descoberta”; toast. Corrigido no HTML (fixture RS-1100, ids do `data-id`, Escape/backdrop, `recomputeRanks`, toast, título “Excluir resultado”).

### Assessment B (Task isolada, inherit)

P0: foco/Escape; result_id inválido; promovido+Excluir; rank. Mesmas correções. P1 toast/403 no apply (protótipo: toast sucesso; 403 fica no backend).

Disposição: P0/P1 de protótipo **resolvidos**. Residual P2: chip `delta #663` de review; drift ghost vs fill do Promover herdado do 469 — aceito no Design, apply usa `DiscoveryPage` real.

## Impeccable Audit

- a11y: dialog `aria-modal`, `aria-labelledby`/`describedby`, close SVG, Escape, backdrop, `aria-label` em Excluir com `result_id`.
- responsive: stack 44px; cards ≤720px (CSS 469).
- theming: tokens existentes; confirm não usa fill `--accent`.
- perf: HTML estático, sem dependências novas.

## Impeccable Trace

- Target: `frontend/public/prototypes/card-663-discovery-discard/index.html`
- SHA-256: `9161746a3d11b43ba689ec9923faccee7a9510a9a47e22530ea84cc2587e8b74` (revalidar se o arquivo mudar)
- Critics: Assessment A `aef9e46a-e455-4c1a-9a25-25d241d91ccc`; Assessment B `8f1c79d3-813c-44c0-87aa-11e2c4bd813c`; modelo `inherit`.
- Browser: `node /tmp/card663-browser.js` via Playwright `chromium` de `source/frontend/node_modules`.
- Detector: N/A nesta sessão (sem hook Impeccable no HTML estático).

## Prototype Validation

- URL servida: `https://dev.criptofarol.com.br/prototypes/card-663-discovery-discard/` (HTTP 200 após restart de `criptofarol-dev-prototypes`).
- Viewports: 1440×900 e 390×844.
- Asserts: `promote>=1`; `tr[data-id=RS-1100] button.discard` count=0; `RS-1099` tem Promover; modal `#discard-result` = `RS-1048`; após confirm, `RS-1048` count=0; cancel em `RS-1049` mantém a linha; `pageerror`/`console.error` = [].
- Resultado JSON: `{"promote":7,"discard":7,"promotedNoDiscard":0,"lowSamplePromote":1,"resultId":"RS-1048","gone":0,"still":1,"errors":[]}`.
- Screenshots: `/tmp/card663-desktop.png`, `/tmp/card663-mobile.png`.

## Design Critique

Fidelidade: shell/nav/tokens do 469. Delta óbvio na coluna Ação. Achados A/B corrigidos no protótipo. Residual: 403/loading no apply; chip de review.

**Design Agent verdict: PASS**
