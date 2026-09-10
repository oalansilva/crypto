## Context

Card 861, Status Design (T3 done, fronteira já grelhada no issue — sem re-entrevista). Vocabulário do issue: Posicionado=HOLD; stop order=stop-limit protetiva Spot que trava saldo; remover=cancelar via Farol com confirmação; vender como operação=venda Spot no Monitor.

Estado atual (worktree `card-861-remover-stop`, base develop):
- `SpotProtectStopPanel.tsx` já tem o botão `Remover stop` no gráfico (Spot protection), mas o clique chama `remove()` direto via `DELETE /monitor/spot-stop-order` **sem confirmação** — viola "HOLD com confirmação" e "dois gestos separados, cada um confirmado".
- `SpotMarketTradePanel.tsx` (fluxo de venda SELL 100%) não tem nenhuma consciência de stop: quando a venda trava (saldo travado pela stop), o erro é genérico e não há caminho de remover ali — o operador precisa sair do fluxo e ir à exchange. Esse é o gap.
- Backend (`monitor_spot_stop.py` + `binance_spot_orders.cancel_protective_stop`) já cancela stops do app (`cfstop_`) e stops criadas só na exchange, recusando não-stop — sem mudança de regra necessária.

## Goals / Non-Goals

**Goals:**
- Remover com confirmação alcançável no gráfico quando Posicionado (HOLD) com stop aberta (app ou só-exchange).
- Remover alcançável dentro do fluxo de venda quando a venda trava por causa da stop, com confirmação própria; após remover, a venda segue o fluxo normal (nova prévia → revisão → confirmação).
- Remover nunca vende sozinho (dois gestos separados, cada um confirmado).
- Sem Posicionado / sem stop aberta, remover não é oferecido.

**Non-Goals:**
- Mudar regra da stop (preço, %, bot); withdraw/transfer/futures/margin; compra.
- Novo endpoint ou mudança no contrato de cancelamento (o existente já cobre `cfstop_` + só-exchange sem tocar não-stop).

## Decisions

1. **Confirmação de remover no gráfico espelha a confirmação de proteger.**
   `SpotProtectStopPanel` ganha estado `confirmRemove`: `Remover stop` → bloco inline de confirmação (resumo qty/stop/limit + origem com rótulo explícito nos dois casos — app "criada no app (Farol)", externa mantém o seu + `Confirmar remoção` / `Cancelar`) → `DELETE`. Abrir a confirmação move o foco para ela (contêiner `tabindex="-1"` ou botão primário, sinal acessível `role="group"` + `aria-label`, gatilho com `aria-expanded`/`aria-controls`); fechar (Cancelar ou confirmar) devolve o foco ao gatilho (ou ao status de remoção quando o gatilho some). Porquê: reusa o padrão já aprovado do `confirmPlace`, fica testável por `data-testid`, e garante "cada gesto confirmado". Alternativa `window.confirm` rejeitada (fora do design system, não auditável em teste).

2. **Ramo "venda travada pela stop" dentro do `SpotMarketTradePanel` (SELL).**
   Quando preview/submit SELL falha com sinal de saldo travado pela stop (mensagem/código de saldo insuficiente travado), o painel rende bloco inline "Venda travada pela stop aberta" com `Remover stop` → confirmação própria (mesmo padrão do gesto do gráfico: identifica qty/stop/limit + origem com rótulo explícito app "criada no app (Farol)" e externa; foco move para a confirmação ao abrir e volta ao gatilho ao fechar) → `DELETE /monitor/spot-stop-order` → volta a `entry` exigindo nova prévia (fluxo normal). Porquê: o operador não sai do fluxo de venda; remover nunca dispara a venda sozinho. Alternativa "link para o gráfico" rejeitada — gráfico-only é exatamente o gap do card.

3. **Sem mudança de backend.**
   Reuso de `GET/DELETE /monitor/spot-stop-order` e `cancel_protective_stop` como estão (já cobre app + só-exchange, recusa não-stop). Porquê: o gap é de alcance/confirmação no frontend, não de regra de cancelamento. Alternativa "novo endpoint" rejeitada (duplicaria contrato sem necessidade).

4. **Regra de oferta inalterada no essencial.**
   Remover é oferecido se e somente se HOLD elegível (`showEntryStopRows`, long) + status `protected=true`; caso contrário não é oferecido (sem posição/sem stop). Porquê: é o acceptance literal do card.

## Risks / Trade-offs

- [Risco] Falso-positivo do ramo "travada pela stop" (venda falha por outro motivo, ex. filtro de lote) → Mitigação: o bloco só aparece para sinal explícito de saldo travado/stop; demais erros mantêm o caminho atual sem oferta de remover.
- [Risco] Corrida: stop executada/cancelada fora entre status e DELETE → Mitigação: erro do DELETE é exibido e o status é reconsultado; nenhum envio de venda é disparado automaticamente.
- [Risco] Remover e vender virarem "um gesto" → Mitigação: após remover, o painel exige nova prévia + revisão + confirmação; remover sozinho nunca chama preview/submit.

## Migration Plan

Sem migração: mudança só de frontend + reuso de endpoint existente. Rollback = reverter o change (nenhum estado persistido novo).

## Prototype

- Canônico: `frontend/public/prototypes/card-861-remover-stop/index.html` — clone da página viva `/monitor` (MonitorStatusTab + ChartModal + SpotProtectStopPanel + SpotMarketTradePanel) com **somente** o delta do card: (a) confirmação de `Remover stop` no gráfico; (b) bloco `Remover stop` no fluxo de venda quando travada pela stop. Regiões clonadas marcadas no HTML.
- Testemunha: BTC Spot USDT HOLD.
UI impact: affected
live_route: /monitor
Clone of live /monitor; only the card delta applied.
surface: existing

## Design Critique

- Auto-revisão contra o briefing: dois pontos de alcance (gráfico + venda travada), confirmação nos dois, remover-nunca-vende, cobertura app + só-exchange, não-oferecer sem HOLD/stop, fora (regra da stop, withdraw/futures/margin, compra) intacto.
- Rework único (dupla rodada B): P1-1 foco/acessibilidade das duas confirmações inline corrigido (foco vai à confirmação ao abrir, volta ao gatilho ao fechar, sinal acessível sem mudar o visual); P1-2 origem da stop rotulada explicitamente também no caso app ("criada no app (Farol)") nos dois gestos, mantido o rótulo da externa. Espelhado em specs × tasks × protótipo.
- Sem P0/P1 de produto/escopo/contrato visível além do desenhado; detalhe de implementação fica para o Apply.
- Veredicto do Design Agent: **pronto para crítica (Aprovação de Design pendente de Alan)** — handoff Design → Aprovação de Design apenas; sem auto-aprovação para Pronto para Dev.

## Apply details (P3 aceitos — sem reabrir escopo)

- Estado `removed` vs `entry` pós-remoção: unificar o nome no Apply.
- Tokens do gate duplicados neste design.md se ausentes: resolver no Apply (canônico segue no protótipo).
- Nomes de `testid`/sinal `stop-blocked`: definir no Apply.
- `data-trade-remove-no` sem `testid`: resolver no Apply.
- `Esc`/focus-trap: comportamento do componente vivo, fora do delta.
- Contraste do botão danger: detalhe visual do Apply.
- Comentário `861-DELTA` na linha testemunha: dado testemunha, mantido.

## Prototype Validation

- URL: `https://dev.criptofarol.com.br/prototypes/card-861-remover-stop/` — HTTP 200, 62419 bytes, sha256 `d849df59762c17582ea562b9b2317e0444c80295e7dca5cc827cb9c1f3652a9b`, idêntico disco-vs-HTTPS (`cmp` clean).
- Browser gate (onda Assessment A/B, snapshots em `.impeccable/critique/`):
  - A (`861-card-861-remover-stop-assessment-A-20260908T170632Z.md`): PASS, 34 asserts, 0 console/page errors (desktop 1280x800, mobile 390x844 + SOL sell-flow). P0/P1: nenhum.
  - B (`861-card-861-remover-stop-assessment-B-20260908T170407Z.md`): PASS, 42 asserts (41 PASS), 0 console/page errors. P0/P1: nenhum.
- Verificado: confirmação com rótulo de origem nos dois gestos + foco vai-e-volta; remover-nunca-vende; pós-remoção exige nova prévia; sem HOLD/stop não oferece; sem anti-padrões (sem grade de estados, sem ANTES-DEPOIS como página).
- P3 restantes (Apply, sem reabrir): overflow mobile herdado da tabela clonada (delta cabe em 390px);-naming/testid/contraste; recorte de 7px da confirmação no modal mobile (foco correto).

## Gate fix (clone-gate compliance, sem mudança de produto)
Reparo de gate devido pelo autor: tokens parseáveis + marcas COPIED + landmarks da tabela viva no protótipo.
Nenhuma decisão de produto alterada; specs/tasks intactos; só conformidade do clone.
Rework anterior já usado (2 P1); esta rodada é gate-compliance, não rework de produto.

## Open Questions

Nenhuma — fronteira veio grelhada do issue 861 (T3 done); não re-entrevistar.
