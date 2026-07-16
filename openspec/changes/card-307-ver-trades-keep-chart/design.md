## Context

`ChartModal` no Monitor com `viewMode=trades` renderiza `StrategyChartSurface` com gráfico + `belowContent` (tabela de trades). O gráfico usa `xl:h-full` dentro de um filho `flex-1`. Quando a tabela de trades carrega e cresce, o espaço flex do gráfico colapsa e o canvas some visualmente.

## Goals / Non-Goals

**Goals:**

- Gráfico permanece com altura mínima estável em Ver Trades (desktop/mobile).
- Trades rolam em área própria sem roubar a altura do gráfico.
- Abrir Gráfico sem regressão.

**Non-Goals:**

- Mudar API de trades ou conteúdo da tabela.
- Redesign visual completo do modal.

## Decisions

1. **Gráfico `shrink-0` com altura fixa/min em trades view**  
   Evitar `xl:h-full` quando há `belowContent`/trades, para o flex não zerar a altura.

2. **Área de trades `flex-1 min-h-0 overflow-auto`**  
   A lista cresce e rola; o gráfico fica no topo.

3. **Ajuste em `StrategyChartSurface` + props do `ChartModal`**  
   Detectar presença de `belowContent` (ou flag explícita) para aplicar classes de layout.

## Risks / Trade-offs

- [Altura fixa em telas baixas] → Mitigar com `min-h` + scroll do modal/trades.
- [Regressão Abrir Gráfico] → Manter layout atual quando `belowContent` ausente.
