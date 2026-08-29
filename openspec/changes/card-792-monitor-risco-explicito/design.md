# Design: Card do Monitor — risco explícito (card #792)

## Context

Card [#792](https://github.com/oalansilva/crypto/issues/792) — P0, frente Risco, `UI impact: affected`. Grelha fechada em 2026-08-29: fonte = top-level `opportunity.*`; distância até entrada permanece interna; copy EXIT vazio = "posição encerrada — sem risco residual mapeado"; formatação via `toDisplayValue`/`priceString`.

Problema: tester do beta vê Compra/Venda e preço no card mas não vê stop/alvo/distância ou vê Entry/Stop ressuscitados em EXIT sem explicar risco residual — o Farol vira sinal, não farol. Relacionado: spec `opportunity-monitor` (EXIT esconde Entry/Stop), #75 roteiro ponta-a-ponta, #463/#637 execução vs leitura, `SpotProtectStopPanel` já existe para colocar stop na Binance (fora deste card).

Usuário afetado: investidor do beta que precisa calibrar tamanho de posição e decidir se abre o gráfico sem achar que o Farol executa ordem.

Hipótese: mostrar hierarquia explícita no card (estado → distância → stop/alvo → frase de cenário) usando dados já derivados no backend (`opportunity.entry_price`/`stop_price`/`distance_to_stop_pct`/`signal_history`/`is_holding`) elimina a pergunta "quanto pode doer?" sem operador.

Resultado esperado: tester percorre só o card e aponta onde dói se a leitura falhar (critério #4), sem inventar placeholder nem vazar segredo de estratégia protegida.

**UI impact: affected** — card + coerência com modal do gráfico. Tela já existe: rota `/monitor` (`MonitorStatusTab.tsx` tabela admin + `OpportunityCard.tsx` no expand + `signalResolution.ts`). Protótipo MUST clonar a **página** `/monitor` (KPIs, filterbar, `table.signals`, status-row HOLD/EXIT, mobile-cards) e redesenhar só o delta no card expandido / kv. Remoção em EXIT mostra shell atual sem Entry/Stop operáveis. Proibido layout paralelo (galeria 2×2 de cards).

Vocabulário congelado do issue (não usar sinônimos):
- `Distância` = % até próximo gatilho relevante para o estado atual (HOLD = até saída; EXIT = sem distância operável)._Avoid gap/delta/spread_
- `Stop` = preço de invalidação (`opportunity.stop_price` top-level)._Avoid stop loss executado/ordem na corretora_
- `Alvo` = preço de referência de saída por objetivo da estratégia (derivado quando confiável)._Avoid take profit garantido_
- `Risco residual` = exposição que ainda importa após EXIT (ou "posição encerrada" quando não há)._Avoid risco futuro/pré-entrada_
- `HOLD` = Compra com entrada ativa confirmada (`is_holding=true` + `signal_history` sem EXIT posterior)._Avoid comprado/segurar_
- `EXIT` = Venda/exit com posição encerrada segundo estratégia._Avoid vendido/zerado na corretora_
- `Indisponível` = dado ausente/não confiável — UI explicita, não oculta._Avoid N/A silencioso/traço sem legenda_

## Goals / Non-Goals

**Goals (Entra):**
- Hierarquia no card: estado (Compra/Venda via `resolveOpportunitySignal`) → distância relevante → stop/alvo (ou "indisponível — dado não confiável").
- Quando `is_holding=true` + `stop_price`/`entry_price`/`distance_to_stop_pct` top-level: distância + stop + alvo visíveis sem abrir gráfico.
- Quando dado ausente/não confiável (null/undefined/stale): "indisponível — dado não confiável" — nunca omite nem inventa placeholder/número de outra timeframe.
- Frase de cenário de erro ("se o preço cruzar X, a leitura de posição deixa de valer") só quando houver dado comprovado (`stop_price` ou invalidação de `signal_history`).
- EXIT: não mostrar Entry/Stop como operáveis; "posição encerrada segundo a estratégia — sem risco residual mapeado" quando `signal_history` vazio, ou risco residual quando houver.
- Badge `Compra/Venda` via `resolveOpportunitySignal`; antecipa roteiro #75; coerência card ↔ modal do gráfico.

**Non-Goals (Não entra):**
- Dimensionamento automático/Kelly/"aposte 2%".
- Colocar stop na Binance por este card (`SpotProtectStopPanel` já existe).
- Métricas completas de backtest no card (Sharpe/SQN vivem em Favoritos).
- Alertas Telegram (#747) ou automação TP/SL/trailing tipo 3Commas.
- Backfill de stop/alvo com placeholder ou número de outra timeframe.

## Decisions

1. **Fonte = top-level `opportunity.*` (decisão 2026-08-29).** `entry_price`/`stop_price`/`distance_to_stop_pct` já derivados em `opportunity_service.py` (com `direction` short invertido) e expostos no payload público. Alternativa rejeitada: recalcular no frontend a partir de `parameters`/`indicator_values` — vazaria segredo quando `is_strategy_protected=true` e divergiria do gráfico.
2. **Distância relevante = `distance_to_next_status` para rótulo + `distance_to_stop_pct` para risco.** Em HOLD a distância até saída já vem em `distance_to_next_status`/`exit_details`; a distância até stop é `distance_to_stop_pct`. Em EXIT não há distância operável — UI mostra risco residual, não distância até entrada (essa métrica fica para história irmã; não duplicar neste card).
3. **"Indisponível — dado não confiável" como string literal.** Copy congelada do issue. Alternativa rejeitada: `-`, `N/A`, traço sem legenda — teste beta já provou que omissão vira "sinal".
4. **Frase de cenário condicionada a dado comprovado.** Só renderiza quando `stop_price` existe ou quando `signal_history[].explanation.summary` traz invalidação. Evita alucinar nível de invalidação. Reuso de `latestTradeExplanation` existente para explicação, mas frase de risco usa `stop_price` como âncora numérica.
5. **EXIT: esconder `showEntryStopRows` + mensagem explícita.** Reuso de `showEntryStopRows = section !== 'exit' && !hasExitedOpportunity(opportunity)` — em EXIT o bloco "Compra/Stop" some e entra o bloco "Risco residual / posição encerrada". Copy vazia = `posição encerrada segundo a estratégia — sem risco residual mapeado` (decisão 2026-08-29).
6. **Segredo: `strategy_secret_visibility.py` já resolve.** `is_strategy_protected=true` mantém `parameters={}` e `indicator_values` filtrado por `execution_columns` — risco usa só top-level, então não precisa branch de visibilidade novo. Checagem: `redact_opportunity_payload` preserva `entry_price`/`stop_price`/`distance_to_stop_pct` mesmo quando protegido.
7. **Formatação: reuso `toDisplayValue`/`priceString`.** USD com `minimumFractionDigits:2 maximumFractionDigits:8`, % com 2 casas. Mantém paridade com "preço atual" já mostrado.
8. **Layout: estender o `<dl class="kv">` existente, não criar nova seção desconectada.** Ordem no card: badge Compra/Venda → `distância relevante` → `stop` → `alvo/distância objetivo` → frase cenário (quando houver) → risco residual/posição encerrada (em EXIT). `alvo` é derivado de payload quando confiável; se ausente, cai em "indisponível". Não mover controles de portfólio, notas ou ações do footer.
9. **Coerência com modal:** `ChartModal` já consome `opportunity` + `resolvedSignal`; mesma hierarquia e mesmas strings, sem duplicar lógica de cálculo.
10. **A11y/copy:** badge `Compra/Venda` via `resolveOpportunitySignal.visual.badgeText`; Frase de cenário em `aria-live="polite"` opcional; "indisponível — dado não confiável" com `title` explicando que dado não confiável ≠ erro de rede.

## Apply contract

Frontend-only (backend já entrega top-level):

1. `frontend/src/components/monitor/OpportunityCard.tsx` — estender bloco `<dl class="kv">` atual (linha 380-407):
   - Manter `showEntryStopRows` para HOLD; em HOLD renderizar na ordem: `distância relevante` (`distance_to_stop_pct` → distância até stop + `distance_to_next_status` → distância objetivo), `stop` (`stop_price`), `alvo` (derivado quando confiável senão "indisponível — dado não confiável"), frase cenário ("se o preço cruzar $X, a leitura de posição deixa de valer") condicionada a `stop_price` ou `signal_history` invalidation comprovada. Formatar via `toDisplayValue`/`priceString`.
   - Em EXIT: não renderizar `entry_price`/`stop_price` como operáveis; renderizar bloco "Risco residual" com mensagem `posição encerrada segundo a estratégia — sem risco residual mapeado` quando `signal_history` vazio/len 0, senão último risco residual de `signal_history`. Usar copy exata do issue.
   - Quando campo for null/undefined/stale: literal `indisponível — dado não confiável` (sem `-`, sem `N/A`).
   - Manter `is_strategy_protected` intacto: risco só lê top-level; não tocar `opportunity.parameters`/`indicator_values`.
   - Manter `data-testid` existentes; adicionar `data-testid={`monitor-risk-block-${symbolTestKey}`}` e `monitor-risk-fallback` para QA.
2. `frontend/src/components/monitor/types.ts` — `Opportunity.alvo` é derivado; não adicionar campo obrigatório novo no tipo; documentar que `entry_price`/`stop_price`/`distance_to_stop_pct` são top-level públicos (já existem).
3. `frontend/src/components/monitor/signalResolution.ts` — sem mudança de lógica de seção; badge já resolve `Compra/Venda`; garantir que `hasExitedOpportunity` continue sendo o gate de EXIT.
4. `ChartModal.tsx` — espelhar mesma hierarquia e copy do card para o payload aberto; não reintroduzir Entry/Stop em EXIT.
5. Validar no modal que "indisponível — dado não confiável" também aparece quando campo ausente.
6. Testes: `frontend/tests` / Playwright cobrindo HOLD com dados, HOLD sem dados, EXIT vazio, EXIT com residual, protected=true não vaza `parameters`.

Rollback: reverter `OpportunityCard.tsx` ao `<dl>` anterior (só preço atual/distância stop/distância objetivo + Entry/Stop em HOLD). Sem migration. Sem mudança de API.

## Risks / Trade-offs

- [Alvo derivado quando confiável — cálculo no frontend vs backend] → aceitar derivado no payload quando existir; quando ausente, "indisponível" — não estimar alvo no card para não virar recomendação de TP.
- [Stale = `indicator_values_candle_time` + 3× timeframe] → se stale, todo o bloco de risco cai em "indisponível" — melhor ser pessimista que inventar.
- [História irmã "distância até entrada" não existe ainda] → este card não mostra distância até entrada em EXIT; EXIT mostra risco residual ou "posição encerrada". Não duplicar métrica.
- [Copy longa em PT-BR pode quebrar layout do card em mobile] → `kv` com `word-break` e `line-clamp` já no shell; testar em 360px.

## Open Questions

Nenhuma bloqueante. Fronteira 2026-08-29 fechada.

## UI impact

**affected** — card + coerência com modal do gráfico. Não há rota nova; `MonitorPage` permanece em `/monitor`.

## Prototype

- URL: `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/`
- Caminho versionado: `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html`
- Digest: `1a1ff265162784ca5708a76de22e6565ae85fb2832b90daec73cc40ac12f90c3` (sha256 do HTML, 95314 bytes)
- Copied vs generated: copied 82460 bytes (tokens + `.monitor-theme` de `index.css` + shell AppNav + markup KPIs/filterbar/`table.signals`/status-row/OpportunityCard chrome); generated 12854 bytes (review-bar, kv #792, frase cenário, residual EXIT, copy `indisponível`, JS Antes/Depois + expand)
- Viewports: desktop 1280×800, mobile 390×844
- Base: clone da **página** `/monitor` (vista admin `showTechnicalColumns=true`) — sidebar 224px, nav autenticada com Monitor active, header workspace, tokens `--bg-*`/`--accent-primary`/`--text-*`/`--border-default` e `--bg-1`/`--t-1` do `monitor-theme`. CSS copiado de `frontend/src/index.css` (~3007–4269). Markup alinhado a `MonitorStatusTab.tsx` (thead, pair-cell, risk-bar, row-actions) + `OpportunityCard.tsx` no expand. Topologia de tabela: `card-637` só como referência; delta USDC não copiado. `DESIGN.md` não reescrito.
- Fluxos/estados: 4 **linhas** na mesma tabela — SOL HOLD completo (expandida no Depois) · ETH HOLD indisponível · ADA EXIT vazio · LINK EXIT com residual. SOL é HOLD Compra ($105.39 / 13.38% / 35.21% stop), nunca EXIT.
- Delta: só o kv do card expandido + frase "Se o preço cruzar $X…" + bloco "Risco residual" em EXIT + literal `indisponível — dado não confiável`. Toggle Antes/Depois troca o kv no mesmo sítio (Antes = kv atual do produto). Sem galeria 2×2.

## Prototype Validation

- URL: `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/` (servido também em `http://127.0.0.1/prototypes/card-792-monitor-risco-explicito/`)
- Viewports: 1280×800 e 390×844 em navegador real (Playwright / Chromium + xvfb)
- Ações/asserts (obrigatórios):
  - (a) thead visível no desktop contém `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags` — PASS
  - (b) `table.signals` e botão `Operar` — PASS
  - (c) linha SOL mostra Compra, `$105.39`, `35.21%`, `Médias Móveis` — PASS
  - (d) Depois: ETH com `indisponível — dado não confiável`; ADA EXIT com `posição encerrada segundo a estratégia — sem risco residual mapeado`; SOL com "cruzar" — PASS
  - (e) clicar Antes altera o kv (labels `compra`/`distância stop` vs `distância até saída`/`distância até stop`); `aria-pressed` coerente — PASS
  - (f) mobile 390: `.table-wrap` escondido, `.mobile-cards` visíveis, delta de risco legível — PASS
  - (g) 0 erros de console com impacto — PASS
- Resultado: asserts a–g verdes. Evidência: `output/playwright/card-792-desktop-1280.png`, `card-792-mobile-390.png`. Crítica A/B e `## Design Critique` ficam com o pai.

## Impeccable pipeline (esta coluna Design)

- `node .agents/skills/impeccable/scripts/context.mjs --target frontend/src/components/monitor/OpportunityCard.tsx` → PRODUCT.md/DESIGN.md como autoridade (não reescritos).
- Shape mental: audience/outcome/direction/scope (recorte abaixo); brief integral não neste arquivo.
- Prototype (rewrite da topologia inválida) → polish por patch (overflow da tabela / `Operar` visível a 1280) → browser gate desktop+mobile + asserts a–g.

## Audience / Outcome / Direction / Scope (recorte do brief)

- **Audience:** investidor do beta (e Alan em T7) que já usa a tabela `/monitor` e precisa reconhecer a mesma tela no protótipo.
- **Outcome:** calibrar tamanho de posição no card expandido e decidir se abre o gráfico sem achar que o Farol executa ordem; apontar risco sem operador (roteiro #75).
- **Direction:** clone da página `/monitor` (não galeria de cards). Binance dark, tokens da folha + `monitor-theme`, tabela admin com Distância/7d/Tags. Delta só no kv do OpportunityCard.
- **Scope:** 4 linhas (SOL HOLD completo, ETH HOLD indisponível, ADA EXIT vazio, LINK EXIT residual); badge Compra/Venda; Antes/Depois no mesmo sítio. Fora: Kelly, stop na Binance, backtest no card, Telegram, backfill.

## Apply contract (resumo para o Gist)

Ordem frontend-only (6 tarefas em `tasks.md`): 1) `OpportunityCard.tsx` kv HOLD + frase cenário condicionada, 2) EXIT sem Entry/Stop + mensagem residual, 3) coerência `ChartModal.tsx`, 4) segredo protegido só top-level, 5) Playwright 5 cenários. Sem backend, sem migration.

## Design Critique

- **P0:** nenhum. Topologia r1 (galeria 2×2) fechada: `table.signals`, thead Status/Preço/Distância/7d/Risco até stop/Tags, ações incluindo Operar, linha SOL HOLD (Compra, $105.39, 13.38%, 35.21% stop, Médias Móveis). Toggle Antes/Depois altera o kv.
- **P1:** nenhum.
- **P2 (accepted-residual):** 4 linhas expandem no load; dt `entrada` no Depois vs `compra` no vivo (Apply usa labels do produto); cenário acrescenta “segundo a estratégia (stop)”; ChartModal fora do HTML estático; fixtures ETH/LINK ilustrativos.
- **P3 (accepted-residual):** 7d = `-`; última `th` “ações” (produto deixa vazia); testids duplicados mobile+tabela; mobile 390 começa nos KPIs.
- Prototype: `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/` — `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` (95314 bytes, sha256 `1a1ff265…`; copied 82460 / generated 12854).
- Snapshot: `.impeccable/critique/792-card-792-monitor-risco-explicito-r2-A.md` e `…-r2-B.md` (r2 PASS). Apply e Code Review não lêem essa pasta. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS**

