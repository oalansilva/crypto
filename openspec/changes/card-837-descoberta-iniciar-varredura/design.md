# Design — Descoberta: Iniciar começa a varredura da seleção atual (card #837)

## Problema

Quem monta uma varredura em Descoberta clica **Iniciar** e recebe **Falha ao iniciar**
(conflito de rascunho) em vez da varredura da seleção da tela — sobretudo depois de
cancelar/terminar uma run e ajustar templates, símbolos, timeframes, direções ou período.
O caminho feliz depende de **Novo rascunho**, que deveria ser atalho, não obrigação.

## Usuário afetado

Administrador que monta e inicia varreduras em Descoberta (`/combo/discovery`).

## Hipótese

Se **Iniciar** tratar a seleção da tela como começo novo após run terminal (nova
varredura, nunca reabrir a morta) e bloquear com orientação quando houver execução em
curso, o operador inicia a seleção atual sem segundo botão, sem reload e sem JSON técnico.

## Resultado esperado

Aceite 1–7 do issue: início da seleção atual com progresso; pós-terminal (igual ou
diferente) gera varredura nova sem 409; execução + outra seleção bloqueia orientando
cancelar; repetição na mesma seleção mostra a existente sem duplicata; reload não prende;
erro em linguagem de operação.

## Recorte

- **Audience:** administrador operador de varreduras.
- **Outcome:** Iniciar = começar a seleção da tela, sempre.
- **Direction:** clone da Descoberta viva + delta só no comportamento de Iniciar/fim de run.
- **Scope:** clique **Iniciar**, estados pós-terminal/em execução/em criação, mensagens.
  Fora: preflight, limite, leaderboard, promoção/descarte, identificador do rascunho, #831,
  Combo/Monitor/Favoritos.

## Gate (clone gate T5, linhas legíveis por máquina)

UI impact: affected
live_route: /combo/discovery
surface: existing

## Apply contract

1. Pós-terminal, **Iniciar** cria varredura nova da seleção enviada (mesmo que igual à
   run morta); nunca reabre a morta; sem 409 no caminho feliz.
2. Com varredura não-terminal, **Iniciar** de outra seleção não cria nem substitui;
   resposta e tela orientam a cancelar antes.
3. Repetição na mesma seleção em criação/execução retorna a existente, sem duplicata.
4. Falha de início fala operação (o que fazer), sem JSON/jargão.
5. Frontend espelha 1–4 em `DiscoveryPage` (botão, bloqueio, mensagens, pós-reload);
   sem mudar preflight/limite/leaderboard/promoção/descarte.
6. Spec canónica `discovery-sweep` recebe o delta antes do apply.

## Prototype

- **URL:** `https://dev.criptofarol.com.br/prototypes/card-837-descoberta-iniciar-varredura/`
  (validada localmente via estático de `frontend/public/`; sem painel ANTES/DEPOIS).
- **Caminho:** `frontend/public/prototypes/card-837-descoberta-iniciar-varredura/index.html`
  (58.394 bytes, sha256 `bf98b9d9…be988020`).
- **Base:** clone da Descoberta viva (`frontend/src/pages/DiscoveryPage.tsx` + shell
  autenticado + tokens `DESIGN.md`; landmarks `Descoberta de estratégias swing`,
  `Rascunho de varredura`, `Preflight`). Trechos clonados delimitados por
  `COPIED:start/end` (shell+heading; rascunho+preflight; comentários inertes, sem
  impacto visual); toolbar do protótipo, leaderboard e script de fixtures são
  delta/chrome, fora do COPIED.
- **Delta:** Iniciar pós-terminal (igual/diferente) abre run nova; execução + outra
  seleção bloqueia com aviso "cancele antes"; duplo clique mostra a existente;
  reload preserva seleção livre; erro operacional sem JSON.
- **Fluxos/estados:** 9 fixtures (live-same, live-other, creating, cancelled-diff,
  cancelled-same, completed-same, reload-cancelled, start-error, pós-cancelar).
- **Exceção justificada:** a linha `Chave do rascunho` permanece visível porque é
  fidelidade ao clone (existe na página viva, `DiscoveryPage.tsx:1592`); escondê-la
  é explicitamente fora de escopo do issue.

## Prototype Validation

- **Viewports:** desktop 1280×800 + mobile 390×844, Chromium real (playwright-core).
- **Gate:** `.impeccable/critique/card-837-gate.mjs` — asserts observáveis por fixture
  (toast/bloqueio/nova run/progresso/reload/erro sem `{`/409/conflito/payload/idempot).
- **Resultado:** TOTAL 52 · PASS 52 · FAIL 0; zero console/page errors. Screenshots
  base/pós-cancelar desktop+mobile em `.impeccable/critique/card-837-gate-*.png`.
- **Revalidação no digest atual** (2026-09-05, após reescrita deste `design.md` sem
  tocar no HTML): rodada integral repetida em Chromium real, desktop+mobile:
  TOTAL 52 · PASS 52 · FAIL 0, zero console/page errors; screenshots regerados.

## Design Critique

- P0: nenhum (A+B). Index é clone+delta com landmarks
  (`Descoberta de estratégias swing`, `Rascunho de varredura`, `Preflight`); sem
  galeria de estados, sem painel ANTES/DEPOIS, sem toggle `aria-pressed` vazio.
- P1: nenhum (A+B). 7 aceites rastreados às 9 fixtures; gate 52/52 replicado por B.
- P2 (A-1, fix no apply): scroll horizontal do leaderboard (`.table-wrap`,
  `min-width 1050px`) inalcançável por teclado — apply adiciona `tabindex=0` +
  `role=region` + label.
- P2 (A-2, fix no apply): ramo `JSON.stringify` em `errorDetail`
  (`DiscoveryPage.tsx:198-205`) pode vazar JSON contra o aceite 7 — apply remove;
  protótipo já correto, sem rework.
- P2 (B, ambiente, sem rework): URL canónica devolvia 404 porque o serviço de
  protótipos subiu antes do worktree — pai reinicia o serviço antes do T7.
- P3 (accept): toast 4,2s sem dispensar (contrapartes persistentes existem); labels
  muted 10–11px no limite do contraste (tokens `DESIGN.md`, fora de escopo);
  `.empty-state` morto aparente; `Iniciar` disabled fora da tab order com
  orientação `role=alert` visível; histórico do protótipo estático (fora de escopo).
- P3 (classify): seleção vazia sem fixture — fora de escopo, sem regressão.
- Riscos/pendências não bloqueantes: copy final do erro operacional pode ganhar
  teste com operador na homologação.
- Protótipo: `https://dev.criptofarol.com.br/prototypes/card-837-descoberta-iniciar-varredura/`
  (`frontend/public/prototypes/card-837-descoberta-iniciar-varredura/index.html`,
  sha256 `bf98b9d9…be988020`, 58.394 bytes = 50.857 generated + 7.537 copied).
- Snapshots: `.impeccable/critique/card-837-descoberta-iniciar-varredura-20260905-202504Z-A.md`
  e `.impeccable/critique/card-837-descoberta-iniciar-varredura-20260905T202813Z-B.md`
  (+ PNGs de B).
- Design Agent verdict: PASS.
