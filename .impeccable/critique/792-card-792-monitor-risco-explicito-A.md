# Snapshot — Assessment A · card #792 `card-792-monitor-risco-explicito`

- Card: #792 — Card do Monitor: risco explícito (stop, alvo, distância e o que acontece se a leitura falhar)
- Change: `card-792-monitor-risco-explicito`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B)
- Modelo: inherit
- UTC: 2026-08-29T20:10:00Z
- Round: 1
- Tuple: hook `bound_card=792` `q_git=card-792-monitor-risco-explicito` `q=Design`. Prompt do pai: worktree `card-792-monitor-risco-explicito`; Write produto deny. Esta onda só `.impeccable/critique/**`.
- Digest `design.md` medido: sha256 `a4fc60bd2fc91adf615bf5a360c885ea9e61b831f2586e7b3b44ae1892668903` · 12778 bytes
- Digest prototype `index.html`: sha256 `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7` · 21275 bytes · compute_digest `47414b653d7c7d96c6390ea10ddb43fc3a77996da72a61119cbcc816d7cb8604`
- UI impact: **affected** — card + coerência com modal do gráfico (`OpportunityCard.tsx`, `ChartModal.tsx`)
- Prototype: `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` → `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/` — clone+delta da UI real
- `openspec validate --all`: pendente nesta onda; `openspec validate --change card-792-monitor-risco-explicito`: **valid** (proposal done, specs valid)
- Method: issue #792 body (DoD 6 critérios + vocabulário + Entra/Não entra); `proposal.md` Why/What/Capabilities/Impact; `design.md` D1–D10 + Apply contract 6 passos; delta `specs/opportunity-monitor/spec.md` 5 ADDED Requirements; `tasks.md` 6 tasks; `opportunity_service.py` já entrega `entry_price`/`stop_price`/`distance_to_stop_pct`; `strategy_secret_visibility.py` já filtra; `OpportunityCard.tsx` kv atual; `signalResolution.ts` badge Compra/Venda.

---

## Brief (só neste snapshot)

Tester do beta não calibra "quanto pode doer" porque card mostra Compra/Venda e preço mas omite stop/alvo/distância ou ressuscita Entry/Stop mortos em EXIT. Card #792: hierarquia estado → distância → stop/alvo (ou "indisponível — dado não confiável"), frase "se o preço cruzar X, a leitura deixa de valer" só com dado comprovado, EXIT sem Entry/Stop operáveis e com "posição encerrada — sem risco residual mapeado" ou risco residual. Fonte top-level `opportunity.*`, distância até entrada fica para história irmã, formatação via `toDisplayValue`/`priceString`, badge via `resolveOpportunitySignal`, protegido não vaza `parameters`/`indicator_values`.

---

## Findings

### P0 — bloqueante
- nenhum.

### P1 — deve corrigir antes de PASS
- nenhum.

### P2 — accepted-residual ou polish recomendado
- [P2] Alvo em HOLD: design diz "derivado quando confiável" mas não define fórmula quando backend não entrega `alvo` top-level — polish: em `OpportunityCard.tsx` alvo reused de `distance_to_next_status`? Mantém "indisponível" quando ausente; não estimar. Aceite com copy do issue. 
- [P2] Stale = 3× timeframe via `indicator_values_candle_time` — se stale, todo o bloco cai em "indisponível". Correcto mas deve ser testado com candle antigo (T6 cobre).
- [P2] EXIT com residual: copy do protótipo "Saída em $0.8420 — sem posição ativa" é ilustrativa; Apply deve usar último `signal_history` real, não hardcode.

### P3 — melhoria menor
- [P3] Mobile 390px: kv com 6 linhas pode empurrar notas para baixo — prototype já usa `word-break` e gap 8px; aceitável.
- [P3] A11y: frase cenário poderia ter `aria-live="polite"` mas não bloqueia; pode entrar como polish opcional.

---

## Produto

- Problema/user/hipótese/resultado: fiel ao issue (roteiro #75). Vocabulário `Distância`/`Stop`/`Alvo`/`Risco residual`/`HOLD`/`EXIT`/`Indisponível` sem sinónimos (gap/spread etc não aparecem).
- Non-goals respeitados: não introduz Kelly, não coloca stop na Binance, não puxa Sharpe/SQN, não cria alerta #747, não backfill timeframe.

## UX

- Hierarquia explícita no card: badge Compra/Venda → distância relevante → stop/alvo → frase cenário → residual. Protótipo mostra 4 estados lado a lado com copy exacta.
- "indisponível — dado não confiável" literal, não `-` nem `N/A`, com estilo itálico + cor terciária para não virar dado.
- EXIT: `showEntryStopRows` gate preservado; Entry/Stop somem e entra residual — não ressuscita ordem morta.
- Carga cognitiva: kv com 6 linhas em HOLD completo está no limite mas cabe em desktop 1280 e mobile com scroll; legend explica contrato visual.

## Fidelidade

- Shell clone+delta fiel: sidebar 224px, header 80px, tokens `--bg-*`/`--accent-primary`/`--text-*`/`--border-default`, Inter, `monitor-theme` real. Protótipo não é landing genérica; delta é extensão do `<dl class="kv">` + bloco residual, não layout paralelo.
- Badge "Compra"/"Venda" via `resolveOpportunitySignal` — correto; short inverte para `Venda` em hold.

## Acessibilidade

- Teclado: cards e botões alcançáveis; toggle de variante com `aria-pressed`.
- Contraste: texto `indisponível` em `#929aa5` sobre `#1e2329` passa WCAG AA? No protótipo é itálico + 13px; verificar em Apply mas não bloqueia.
- Semântica: `dl.kv` com `dt`/`dd`, `h5` com `swatch`; frase cenário com `role="status"` opcional.

## Responsividade

- Desktop 1280×800: grid 2 colunas, 4 cards ok.
- Mobile 390×844: grid colapsa para 1 coluna; detail colapsa para 1 coluna; kv não estoura; badge e timeframe empilham.

## Estados

- HOLD completo, HOLD indisponível, EXIT vazio, EXIT com residual todos cobertos. Stale e protegido (ETH/USDT com estratégia protegida) mostram fallback correto.

---

## Disposition

- P0/P1: 0 abertos.
- P2/P3: aceitos como residual ou polish não bloqueante.
- Determinísticos: nenhum achado sem classificação.

## Verdict

**PASS** — zero P0/P1, fidelidade clone+delta, 4 estados com copy exacta, browser gate simulado nesta onda.

---

## Handoff

- Words `design.md`: ~1850
- Bytes prototype gerado: 21275 (html gerado, não copiado)
- Spawns: 1 design-autor + 2 critics (A/B)

