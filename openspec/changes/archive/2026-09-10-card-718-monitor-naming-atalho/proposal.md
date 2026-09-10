## Why

O operador do Monitor traduz nomes de estado entre KPI, seção, coluna Status, card mobile e Ajuda, e ainda encontra um hint ⌘K na busca que não foca nada no Mac. Compra no HOLD é posição já confirmada, não «compre agora»; deixar a pill e a Ajuda a dizer Compra/Venda como estado da board continua a mentira. O #788 está Cancelado — não há card vivo para receber o vocabulário da Ajuda.

## What Changes

- KPI e título da seção com o mesmo nome de estado, sem tag Compra/Venda.
- KPI de saída = `Saída / cobertura` (não `Em saída`).
- Remover badge `Estado Compra` / `Estado Venda` (e qualquer `Estado hold/exit`).
- Remover o hint `⌘K` da busca (sem atalho neste card).
- **T6:** coluna Status de `table.signals` e o rótulo de estado visível no card mobile (hoje `badgeText` Compra/Venda) passam a mostrar o mesmo nome canónico da seção: `Em posição` / `Saída / cobertura`.
- **T6:** copy visível da Ajuda `/help` (`HelpPage.tsx:42`) e do `ScreenHelpPanel` no `/monitor` que ensinam Compra/Venda como estados do Monitor passam a esses nomes (troca estrita; não reescrever o guia; não inventar entrada potencial).

## Vocabulário

- `Em posição`: estado de posição ativa em acompanhamento no Monitor (HOLD já confirmado).
- `Saída / cobertura`: estado de saída ou cobertura acionável para nova análise (EXIT).
- `Estado da board`: nome canónico visível em KPI, seção, coluna Status e card mobile.
- `Lado de ordem`: `Compra` / `Venda` = BUY/SELL nos marcadores do gráfico (`markerLabel`) e no Spot — não é estado da board.
- `Hint de atalho falso`: texto de tecla (⌘K) exibido na busca sem focar nada ao ser pressionado.
- `_Avoid:` Compra/Venda como nome de estado da board; `Em saída` vs `Saída / cobertura` misturados; vocabulário de entrada potencial / terceiro estado; `Cmd+K` como sinónimo solto do hint; dual-write `CONTEXT.md` / `docs/adr/`.

## Capabilities

### New Capabilities

- `monitor-naming-atalho`: um só vocabulário de estado da board no Monitor e na copy de Ajuda que ensina esses estados; busca sem hint falso.

### Modified Capabilities

- `monitor`: contrato observável da página `/monitor` (KPI, seção, Status da linha/mobile, ScreenHelpPanel) e do parágrafo Monitor em `/help`; regra HOLD/EXIT inalterada; lado de ordem Compra/Venda intocado.

## Impact

- **Código (Apply, não nesta rodada):** `frontend/src/components/monitor/MonitorStatusTab.tsx` — hint `:1011`; KPIs `:1062-1076`; badge `:1168`; Status da linha `:1294` (`resolved.visual.badgeText`); `OpportunityCard.tsx` pill/rótulo mobile (`badgeText`).
- **Ajuda (T6, troca estrita):** `frontend/src/pages/HelpPage.tsx:42` e `frontend/src/pages/MonitorPage.tsx:9` (`ScreenHelpPanel`).
- **Não mexer:** `markerLabel` / marcadores do gráfico; Spot BUY/SELL; `resolvedSections` / cálculo / ordem; `backend/`; dual-write ADR.
- **Fora de escopo (não entra):** foco por teclado (⌘K/Ctrl+K); terceiro estado / entrada potencial (mesmo com #788 cancelado); bot, copy-trade, ordem automática, redesign do Monitor.

## Decidido

- Q1 (Alan, grill): remover o hint ⌘K — NÃO implementar foco.
- Q2 (Alan, grill): residual mínimo no sentido de NÃO criar vocabulário de entrada potencial / terceiro estado. T6 (Alan, devolução Design) alarga o residual visível ao nome único nas superfícies que JÁ mostram HOLD/EXIT, incluindo pill e Ajuda. Q1/Q2 não reabertas.
- #788 = Cancelado no Project 1 — este card absorve a copy de estado da Ajuda; não cria a seção de entrada.
- PO 2026-08-29: P2. Origem: varredura 2026-08-25. UI impact: affected (`/monitor`). Extra: `/help` (clone irmão).
