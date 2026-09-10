## Context

O Monitor (`/monitor`) mistura nomes de estado HOLD/EXIT. Vivo hoje (`MonitorStatusTab.tsx` + `signalResolution.ts`): KPI `Em posição` + tag `Compra` / `Em saída` + tag `Venda`; h3 `Em posição` / `Saída / cobertura`; badge `Estado {cfg.title}` → `Estado Compra` / `Estado Venda`; coluna Status e card mobile usam `resolved.visual.badgeText` = `Compra` / `Venda`; busca mostra `<span className="kbd">⌘K</span>` sem listener neste ecrã. A Ajuda (`HelpPage.tsx:42`) e o `ScreenHelpPanel` (`MonitorPage.tsx:9`) ensinam Compra/Venda como estados do Monitor.

Compra no HOLD é posição já confirmada, não «compre agora». O residual r1 (só chrome KPI + hint; pill e Ajuda ficam Compra/Venda) não entrega um só vocabulário. Project 1 Status do #788 = Cancelado: esperar #788 deixa a mentira permanente. T6 (Alan devolveu Design) alarga o residual visível ao nome canónico nas superfícies que já mostram HOLD/EXIT — incluindo Status da linha/mobile e a copy de Ajuda — sem criar terceiro estado.

Q1/Q2 do grill estão fechadas e não reabrem: Q1 = remover o hint, sem foco ⌘K/Ctrl+K; Q2 = não criar vocabulário de entrada potencial.

UI impact: affected
live_route: /monitor
surface: existing
surface_detail: topbar-search, kpis, filterbar, sections-hold-exit, table-signals-status, mobile-card-status, screen-help-panel

## Goals / Non-Goals

**Goals:**

- KPI e título da seção com o mesmo nome, sem tag Compra/Venda.
- KPI de saída = `Saída / cobertura` (não `Em saída`).
- Remover badge `Estado Compra` / `Estado Venda` (e qualquer `Estado hold/exit`).
- Remover hint `⌘K` da busca, sem atalho neste card.
- Coluna Status de `table.signals` e o rótulo de estado visível no card mobile = mesmo nome canónico da seção (`Em posição` / `Saída / cobertura`).
- Copy visível da Ajuda `/help` e do `ScreenHelpPanel` no `/monitor` que ensinam Compra/Venda como estados do Monitor passam a esses nomes (troca estrita).

**Non-Goals:**

- Foco por teclado (⌘K/Ctrl+K).
- Mudar a regra de sinal HOLD/EXIT (`resolvedSections`, cálculo, ordem).
- Terceiro estado / vocabulário de entrada potencial (este card não cria a seção de entrada).
- Bot, copy-trade, ordem automática, redesign do Monitor.
- Renomear Compra/Venda no gráfico (`markerLabel`) ou no lado de ordem Spot (BUY/SELL).
- Dual-write `CONTEXT.md` / `docs/adr/`.

## Decisions

- **D1 — Um nome canónico por estado da board.** KPI, h3 da seção, coluna Status e pill/rótulo do card mobile exibem exactamente `Em posição` (HOLD) e `Saída / cobertura` (EXIT). Sem `<span className="tag">` nos KPIs. Sem `<span className="status-section-label">`. Alternativa r1 (só KPI + hint) — rejeitada pelo T6: a pill a dizer Compra no HOLD continua a mentira.
- **D2 — Board vs lado de ordem.** Estado da board ≠ lado de transação. `Compra` / `Venda` permanecem `markerLabel` e copy de ordem Spot (BUY/SELL). Apply não pode «renomear Compra em todo o frontend». O campo interno `badgeText` hoje serve a board; o Apply remapeia o rótulo visível da board sem alterar `markerLabel` nem a legenda de marcadores do gráfico.
- **D3 — Hint = apagar o span.** Remover `<span className="kbd">⌘K</span>` (`MonitorStatusTab.tsx:1011`). Sem listener, sem mudar placeholder. Classe `.kbd` pode ficar órfã (P3 Apply).
- **D4 — Ajuda = troca estrita.** `HelpPage.tsx:42` e `MonitorPage.tsx:9` substituem Compra/Venda-como-estado pelos nomes canónicos. Não reescrever o guia. Não inventar «entrada potencial». Copy de Spot na Ajuda (`comprar / stop / vender`) e títulos de botão Operar ficam — são lado de ordem, não estado da board. #788 cancelado não autoriza criar a seção de entrada aqui.
- **D5 — Regra HOLD/EXIT intocada.** Só labels/copy/hint. Sem mudança em `resolvedSections`, `SECTION_ORDER` ou cálculo de `totalKpi`.
- **P3 aceites (detalhe de Apply, resolvidos no Apply, não reabrir como P0/P1):** CSS órfão `.kbd` / `.kpi-label .tag`; se o remap da board é novo campo vs `badgeText` só na renderização da board; sample data do protótipo (contagens/preços/riscos ilustrativos); filterbar do proto sem o seg admin `Em portfólio`/`Todos`.

## Risks / Trade-offs

- [Risco] Operador habituado a ler Compra/Venda na pill → Mitigação: T6; o nome da seção já era `Em posição` / `Saída / cobertura`; a pill alinhada elimina a tradução.
- [Risco] Apply alargar o rename a `markerLabel` / Spot → Mitigação: D2 no contrato Apply; spec observa só board + Ajuda de estado.
- [Risco] Utilizador Mac continuar a tentar ⌘K → Mitigação: Q1; foco fora deste card.
- [Risco] CSS órfão `.kbd` / `.kpi-label .tag` → P3 Apply, aceite aqui.

## Apply contract

- Ficheiros: `MonitorStatusTab.tsx` (hint, KPI tags/nome de saída, badge de seção, Status da linha); `OpportunityCard.tsx` (pill/rótulo mobile de estado); `HelpPage.tsx:42`; `MonitorPage.tsx` `ScreenHelpPanel`. Opcional no mesmo diff: remap de `badgeText` só para board em `signalResolution.ts` **sem** tocar `markerLabel`.
- Observável: busca sem ⌘K; KPIs `Em posição`, `Saída / cobertura`, `Total`, `Em carteira` sem tag; h3 iguais; 0 `Estado Compra/Venda`; Status da tabela e card mobile com os mesmos nomes; Ajuda/painel sem ensinar Compra/Venda como estado do Monitor.
- Proibido: listener ⌘K; terceiro estado; rename global de Compra; dual-write ADR.

## Open Questions

- Nenhuma. Q1/Q2 fechadas no grill; T6 decidido pelo operador na devolução de Design.

## Prototype

- Path canónico: `frontend/public/prototypes/card-718-monitor-naming-atalho/index.html`.
- URL canónica: `https://dev.criptofarol.com.br/prototypes/card-718-monitor-naming-atalho/`
- Path extra (Ajuda `/help`): `frontend/public/prototypes/card-718-monitor-naming-atalho/ajuda.html`.
- URL extra: `https://dev.criptofarol.com.br/prototypes/card-718-monitor-naming-atalho/ajuda.html`
- Tipo: COM-TELA — o index clona a página viva `/monitor` (chrome `MonitorStatusTab` + `ScreenHelpPanel` de `MonitorPage`) com tokens de `frontend/src/index.css` (`.monitor-theme` + painel de ajuda) e aplica SÓ o delta T6. Landmarks do catálogo HEAD: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. Pares `COPIED:start`/`COPIED:end`. O extra clona `/help` (irmão, nunca painel das N no index). T5 mede só o index (`live_route: /monitor`).
- Proibido: painel ANTES/DEPOIS / «6 estados» como URL canónica; Gist HTML; reescrever DESIGN.md.
- Digest index sha256: `9fb0e14144333144c1b80249099e388579a187de27715eefd457cf612f199660` (24121 bytes). Extra ajuda: `c42327c826f5d8b68614181a779f6d3745866c6af95f7138cda7ab80af1c5972`.

## Design Critique

- Onda T6: autor + dupla A/B (teto com-tela; sem segundo rework — 0 P0/P1 novo). A=APROVAR-COM-P3; B=APROVAR-COM-P3.
- P0: nenhum.
- P1: nenhum.
- P3 aceites (detalhe de Apply, resolvidos no Apply): CSS órfão `.kbd` / `.kpi-label .tag`; remap `badgeText` só na board (incl. `Sinal ·` se visível) sem `markerLabel`/Spot; sample data; filterbar sem seg admin; clone thinning (AppNav / `MonitorDisclaimer` / spark fora de `surface_detail`); uppercase CSS incumbente da pill/h3 (`EM POSIÇÃO` visual, `textContent` canónico).
- Gate: `UI impact: affected`, `live_route: /monitor`, `surface: existing` (`surface_detail: topbar-search, kpis, filterbar, sections-hold-exit, table-signals-status, mobile-card-status, screen-help-panel`) — verificado pela dupla.
- Snapshots: `.impeccable/critique/718-card-718-monitor-naming-atalho-T6-A.md` e `…-T6-B.md`. Gist OpenSpec não é a crítica.
- Design Agent verdict: PASS

## Prototype Validation

- URL canónica: `https://dev.criptofarol.com.br/prototypes/card-718-monitor-naming-atalho/` — HTTPS pode 404 até restart do unit de protótipos; A/B validaram HTTP local no worktree (index sha256 `9fb0e141…` = disco). Extra: `…/ajuda.html`.
- A (`.impeccable/critique/718-card-718-monitor-naming-atalho-T6-A.md`): PASS; 0 P0/P1; desktop+mobile; `/login` não tratado como `/monitor`.
- B (`.impeccable/critique/718-card-718-monitor-naming-atalho-T6-B.md`): PASS 73/73; 0 P0/P1; catálogo `/monitor` + copied 12533; extra `/help` irmão.
- Veredito: PASS. Nenhum P0/P1 aberto.
