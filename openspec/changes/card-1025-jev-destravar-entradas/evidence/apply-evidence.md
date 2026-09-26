# Card #1025 — evidência de Apply (A–G)

Change: `card-1025-jev-destravar-entradas` (branch `card-1025-jev-destravar-entradas`)
Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1025-jev-destravar-entradas`
Cliente: dsh (Apply child). Sem commit/push, sem `process_event`, sem reviewers.

## 0. Escopo e ambiente

- DEV-only (`RUN_SCALP_LOOP=1`), backend puro: **sem** `frontend/**`, sem rota/HTML/painel, sem
  migração/base de dados nova, sem dashboard/exportação/Drive, sem backtest, sem PROD, sem segredos.
- Diff: 7 serviços de backend + 2 ficheiros de teste existentes ajustados + 7 ficheiros de teste
  novos + `scripts/scalp_jev_eval.py` + o inventário do portfólio de testes
  (`backend/tests/unit/test_inventory.json` e a contagem em `test_backend_unit_harness.py`) +
  `openspec/changes/card-1025-jev-destravar-entradas/**`.
  `scripts/process-fsm/**`, `AGENTS.md`, `.cursor/**` e `.covenant-flow/**` intocados.

## 1. Card A — régua read-only (`scripts/scalp_jev_eval.py`)

Comando (log real do #1015 no DEV; DB DEV em leitura, `sudo -u root` porque o Postgres usa peer auth):

```
sudo -u root env DATABASE_URL=… PYTHONPATH=<worktree>/backend \
  backend/.venv/bin/python scripts/scalp_jev_eval.py \
  --log /srv/apps/dev/criptofarol/source/backend/scalp_jev_diagnostic.log \
  --json --out <worktree>/openspec/changes/card-1025-jev-destravar-entradas/evidence/card-a-ruler-report.md
```

Relatório completo: `evidence/card-a-ruler-report.md`. Resultado:

| item | valor |
| --- | --- |
| janela do log | 2026-09-23 13:26:57 → 17:39:02 (252,1 min) |
| chamadas com janela / com retorno | 781 / 781 |
| janelas de 900 s | 781 decisões, **3 não sobrepostas** (mínimo de conclusão: 30) |
| confiança máxima observada | **0,39** |
| recusas registadas | `jev_target` 1496, `hold` 374, **`low_confidence` 406**, `no_book` 117, `switch_off` 1, `window_empty` 1 |
| realizado a 900 s | **parcial**: OHLCV `BTC/USDT` 15m com 23 candles até 2026-09-23 15:45; **1** janela com preço (`n_priced`) — cobertura parcial declarada |
| regiões | σ: calmo 0 / activo 3; predicado do gate: calmo 2 / activo 1 — ambos insuficientes |
| buckets | score 0/1/6; confidence [0.0,0.1), [0.2,0.3) e [0.3,0.4) — 1 trade cada, 1 com preço |

**Declaração (tasks 1.4/1.5): amostra insuficiente** — 3 janelas não sobrepostas < 30 **e** só 1
janela com preço (`n_priced`, correção E2). Consequência aplicada:

- `CONFIDENCE_MIN` mantém o default (`0,7`) — nenhum limiar inventado sem régua (task 3.3/3.4);
- `EXIT_TARGET_BP = 35` / `EXIT_STOP_BP = −28` mantidos (task 4.2);
- `HOLD_AFTER_FILL_S = 900 s` mantido (valor de produto, fora da recalibração);
- σ (`vol_bp`) **não** entra no gate de regime: a segmentação da régua não o justificou (task 4.3) →
  o gate decide só pela previsão (task 4.1).

A régua é read-only (só `get_latest_candle_time`/`read_recent_candles`), não exige o loop do scalp e
testa essa propriedade (`test_the_instrument_is_read_only`).

## 2. Decisões P3 tomadas no Apply

| P3 | decisão |
| --- | --- |
| Envs novas | cadência `SCALP_JEV_TARGET_MS` (default 30000 ms); limiar `SCALP_CONFIDENCE_MIN` (default `CONFIDENCE_MIN`); registo cru opt-in `SCALP_JEV_RAW_PAYLOAD` |
| TTL da cache de fee | `FEE_CACHE_TTL_SECONDS = 900 s`, por utilizador; o fallback também fica em cache (sem pedido assinado por ciclo) |
| `fee_bp` / BNB | `fee_bp = commissionRates.maker × 10000` (por perna); `bnb_fee_active = spotBNBBurn`; endpoints `GET /api/v3/account` + `GET /sapi/v1/bnbBurn`; shape `(fee_bp, bnb_fee_active)` intacta; `/api/scalp/status` mostra a taxa em uso (`com taxa 7,5 bp (BNB)`) e mantém `fee_bp`/`hurdle_bp` |
| Injeção dos testes | o `ExchangePort` ganhou `fee_terms()`; sem esse método o serviço usa o fallback conservador `(10, False)` (nenhuma chamada de rede nos testes) |
| Folga de 50% | `entry_hurdle_bp_with_slack()` / `passes_regime_gate()` em `scalp_window.py` (`REGIME_SLACK = 1.5`, comparação `>=`) |
| Escala de tokens | instrumento = heurística bytes/4 (`estimate_input_tokens`) sobre o corpo compacto |
| `N` da janela | `RECENT_TRADES_N = 5`; cada trade `[age_s, price, qty, aggressor]`; agregados de 900 s preservados; decimais arredondados a bp/quantidade útil |
| Registo do escape | `log_aggressive_exit` (WARNING, token `reason=hold_window_end`, `price_cap=none`, lado, tipo, quantidade, status, `executed_qty`, `avg_price`, ids) — nunca o token `stuck` |
| Escala do `criteria` | os 10 níveis passam a `"0 bp"…"80 bp"` (o significado fica nas instruções da pergunta); ladder inalterada |
| Drivers do `book_toxic` | `noul`, `window_ret_bp`, `window_vol_bp`, `window_aggressor_flow`, `window_spread_bp_mean`, `window_trade_count` no registo de retorno; limiar `noul ≥ 0,5` intocado |

## 3. Grupos A–G — o que mudou e onde

| grupo | tasks | ficheiros | nota |
| --- | --- | --- | --- |
| A — régua | 1.1–1.5 | `scripts/scalp_jev_eval.py`, `evidence/card-a-ruler-report.md` | read-only; amostra insuficiente declarada; gate C/D fechado |
| B — fee/hurdle | 2.1–2.4 | `scalp_binance.py`, `scalp_service.py`, `test_scalp_maker_fee_hurdle.py` | maker real por perna + cache TTL + fallback `(10, False)` |
| C — confiança | 3.1–3.4 | `scalp_jev.py`, `scalp_jev_log.py`, `scalp_engine.py`, `scalp_service.py`, `test_scalp_confidence_gate.py` | registo cru opt-in; `CONFIDENCE_MIN` por env injetado; default mantido (régua insuficiente) |
| D — regime | 4.1–4.4 | `scalp_window.py`, `scalp_engine.py`, `test_scalp_regime_gate.py` | token `regime` entre `hurdle` e `toxic_book`; sem switch por env |
| E — escape | 5.1–5.4 | `scalp_engine.py`, `scalp_binance.py`, `scalp_service.py`, `scalp_jev_log.py`, `test_scalp_aggressive_exit.py` | MARKET sem teto; gates reordenados (escape antes de `exit_resting`); cancelar + enviar no mesmo ciclo |
| F — cadência | 6.1–6.4 | `scalp_engine.py`, `scalp_service.py`, `scalp_jev.py`, `scalp_jev_payload.py`, `test_scalp_jev_consult_cadence.py` | 30 s por env; payload ≤ ~500 tokens; `latency_ms` pós-registo |
| G — `book_toxic` | 7.1–7.2 | `scalp_jev.py`, `scalp_jev_log.py`, `test_scalp_book_toxic_observability.py` | drivers no log; sem retune do limiar; painel/status sem campos |

### 3.1 Reordenação do caminho de saída (achado F1)

`decide_exit_cycle` passa a avaliar `seconds_since_fill >= HOLD_AFTER_FILL_S` **antes** do ramo
`resting is not None → skip_reason="exit_resting"`. Ao disparar devolve `send=True`,
`aggressive_exit=True`, `cancel_resting=True`, `price=None`, `order_type="MARKET"`; o serviço cancela
a passiva não preenchida (via `intent.cancel_resting`, antes do envio; e qualquer resto de entrada
não preenchido, no mesmo ramo) e envia a MARKET **no mesmo ciclo**, sem tentativa passiva extra e sem
checagem de livro fresco (o escape sai sempre). O `should_post_exit` perdeu o ramo temporal: dentro da
janela só há saída passiva de alvo/stop.

### 3.2 Evidência DEV do `book_toxic` (task 7.1/7.2)

Tally do log real do #1015 (766 retornos): `book_toxic=True` **412** (53,8%), `False` **354**;
recusas `toxic_book` **0** (o `low_confidence`, que precede o `toxic_book`, fechou 394 ciclos antes de
o gate tóxico ser avaliado); **0** registos com `noul=` (formato pré-#1025).

**Declaração 7.2: a evidência multi-dia que distingue opinião do modelo de mapeamento errado não é
produzível com a amostra actual** (17 min, um regime, e os registos existentes não têm `noul`). Os
drivers passam a ser gravados a partir desta entrega (provado em
`test_return_record_carries_noul_and_the_window_features` e
`test_model_opinion_can_be_told_apart_from_a_wrong_mapping`); a leitura multi-dia fica como
confirmação de Done. Limiar `noul ≥ 0,5` intocado (`test_noul_threshold_is_not_retuned`); nada no
painel/status (`test_drivers_stay_out_of_the_product_surface`).

### 3.3 Fee maker real no DEV (task 2.x, evidência do passo)

Probe read-only no DEV (credencial Spot do utilizador DEV, mesmos endpoints do contrato):

```
users: [('38b88997-612d-45ee-b13c-a5cc81a34585', False)]
user=38b88997-… enabled=False fee_bp=10.00000000 bnb=True hurdle(spread=0.1)=20.10000000 regime_gate=30.150000000
```

Leitura real `GET /api/v3/account` + `GET /sapi/v1/bnbBurn` sem erro: a conta DEV devolve
`commissionRates.maker = 0,00100000` (10 bp por perna) com `spotBNBBurn = true`. Como o contrato fixa
`fee_bp` = taxa maker real devolvida pela API (e o BNB como estado à parte), o hurdle desta conta fica
em ~20,1 bp e o gate de regime exige ≥30,15 bp — a banda 12–16 bp do critério pressupõe uma taxa maker
descontada (VIP/BNB efectivo) que esta conta DEV não apresenta. O fallback `(10, False)` é
indistinguível em número, o que mantém o comportamento conservador.

## 4. Testes e validação

Comando (focado no card; `CRYPTO_SCALP_BTCUSDT_SNAPSHOT_PATH` aponta para um ficheiro nosso porque o
`/tmp/crypto-scalp-btcusdt-snapshot.json` pertence ao runtime-worker DEV a correr como root):

```
CRYPTO_SCALP_BTCUSDT_SNAPSHOT_PATH=/tmp/pytest-scalp-final.json \
  /srv/apps/dev/criptofarol/source/backend/.venv/bin/python -m pytest \
  backend/tests/unit/test_scalp_direcional_jev.py \
  backend/tests/unit/test_scalp_jev_horizonte.py \
  backend/tests/unit/test_scalp_ws_fresh_state.py \
  backend/tests/unit/test_scalp_maker_fee_hurdle.py \
  backend/tests/unit/test_scalp_confidence_gate.py \
  backend/tests/unit/test_scalp_regime_gate.py \
  backend/tests/unit/test_scalp_aggressive_exit.py \
  backend/tests/unit/test_scalp_jev_consult_cadence.py \
  backend/tests/unit/test_scalp_book_toxic_observability.py \
  backend/tests/unit/test_scalp_jev_eval_ruler.py \
  backend/tests/contract/test_backend_unit_harness.py -q
→ 170 passed
```

- `black --check` limpo nos 8 ficheiros alterados (nenhum reformatado na verificação).
- `openspec validate card-1025-jev-destravar-entradas --strict --no-interactive` → **valid**;
  `openspec validate --all --no-interactive` → **181 passed, 0 failed**.
- `scripts/validate_backend_unit_inventory.py` → `valid: true` (sem `missing`, `stale` ou
  `semantic_issues`); 7 ficheiros de teste novos entraram em `backend/tests/unit/test_inventory.json`
  (80 → **87** entradas) e o contrato `test_inventory_matches_all_unit_test_files` foi actualizado
  para 87 — o portfólio tem de bater certo com os ficheiros em disco.
- A suite completa de `backend/tests` não foi corrida (erro de colecção pré-existente e alheio em
  `test_discovery_favorite_metrics.py`, indicado no briefing do card).
- Ajustes em testes existentes, todos por contrato novo (não por conveniência):
  `JEV_TARGET_MS == 30000`; `_buy_signal()` com previsão 35 bp (limpa o gate de regime com a fee
  conservadora e o spread semeado); `JEV_STAND_IN_MOVE_BP=35` no cenário keyless; os dois cenários de
  resting entry mantêm a ordem fresca porque o timeout de entrada (10 s) é menor que a cadência (30 s);
  `should_post_exit` sem `seconds_since_fill`; `FakeExchange` ganhou `place_aggressive_exit`.

### 4.1 Escala de tokens (task 6.2)

Payload real (300 trades na memória, 5 recentes transportados): **321 tokens** (heurística bytes/4) e
`state` com 651 bytes; ladder `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` intacta. Antes: 1.158 tokens.

### 4.2 Cadência (task 6.1)

`JEV_TARGET_MS = 30000` → 120 pedidos/h contra 3.600 a 1 Hz = **30× menos** (critério ≥15×);
`JEV_FLOOR_MS = 400` e o `interval` do loop (0,4 s) inalterados; `JEV_LATE_MS = 1500` inalterado.

## 5. Estado das tasks (31 no ficheiro)

`tasks.md`: **31/31** marcadas. As três de evidência/fecho foram resequenciadas pelo dono
(ok 23/09) e ficam registadas aqui — não como implementação em falta:

- **7.2** — evidência **multi-dia** do `book_toxic`: o log do #1015 é de um só dia e os registos
  anteriores não têm `noul`; a gravação dos drivers começa com esta entrega (provada em §3.2) e a
  leitura multi-dia é recolhida depois da integração em `develop` (T14) e anexada ao card para a
  homologação (T15).
- **8.3** — confirmação no **runtime-worker DEV** com o código novo: o worker DEV corre `develop`,
  não esta branch; a evidência é recolhida depois de integrar + `./restart` DEV (T14) e anexada (T15).
  Aqui ficou a régua sobre o log real do DEV, a leitura real da fee e os testes focados que exercitam
  cada caminho; produzir a evidência no worker a partir da branch exigiria escrever estado de scalp no
  DEV (proibido).
- **8.4** — fecho da coluna (`/opsx:verify`, `qa-gate`, PR `q_git`): **executado pelo pai nesta
  entrada**; este filho não faz commit/push/PR nem `process_event`.

## 6. Residual / P3 que fica para o fecho (Done)

1. **Confirmação no runtime-worker DEV** (task 8.3) — ver §5.
2. **Evidência multi-dia** do `book_toxic` (7.2) e da confiança/geometria (Card A) — ver §5 e §1.
3. **Painel mostra a fee**: `ScalpModule.tsx` imprime `7,5 bp` fixo quando `bnb_fee_active` é `true`,
   ignorando `fee_bp`. O card proíbe `frontend/**`; a taxa real fica visível no payload/`status_text`
   do `/api/scalp/status`. Correcção da cópia de tela fica para card de UI.
4. **`fee_bp` no DEV é 10 bp com `spotBNBBurn=true`**: o status mostra "10 bp (BNB)"; a banda 12–16 bp
   do critério pressupõe uma taxa maker descontada que a conta DEV não apresenta. Se o produto quiser
   mostrar 7,5 bp com BNB ligado, isso é uma decisão explícita nova (aplicar o desconto em vez de ler a
   taxa real) — fora deste card.
5. **Ciclo de import pré-existente** (não introduzido aqui): `import app.services.scalp_jev_payload`
   como primeiro import do processo falha porque `scalp_btcusdt_stream → scalp_engine → scalp_window →
   scalp_btcusdt_stream`; o mesmo acontece em `HEAD` e o caminho de produção entra por
   `scalp_service`. Não foi corrigido (fora do escopo do card); fica registado.

## 7. Correções pós-T18 (`nao_homologar` — entrada `card-1025-correcao-achados`)

Correcções mecânicas e de juízo aplicadas nesta entrada, sem commit/push/PR/`process_event` e com o
`Status` intocado:

| id | correcção | ficheiro(s) |
| --- | --- | --- |
| E1 | Barreiras **espelhadas** por lado: no SELL o alvo fica abaixo e o stop acima da entrada (a coluna SELL estava corrompida). Teste `test_sell_barriers_are_mirrored_by_side`. | `scripts/scalp_jev_eval.py`, `test_scalp_jev_eval_ruler.py` |
| E2 | Insuficiência olha a contagem de janelas **com preço** (`n_priced`), não só a lista de candles; cobertura parcial declara amostra insuficiente. Teste `test_partial_coverage_declares_insufficiency_on_the_priced_windows`. | `scripts/scalp_jev_eval.py`, `test_scalp_jev_eval_ruler.py` |
| E3 | Se o cancelamento da saída passiva **falhar**, a agressiva **não** é enviada nesse ciclo (evita oversell): o escape é adiado com a mesma chave de reconciliação/backoff e o estado resting é mantido. Teste `test_escape_is_deferred_when_the_passive_cancel_fails`. | `scalp_service.py`, `test_scalp_aggressive_exit.py` |
| E4 | Com amostra suficiente a régua volta a **derivar** a geometria alvo/stop (candidatos + expectancy líquida com taxa maker por perna + hit-rate de break-even); sem amostra/candidato positivo, mantém os defaults de produto explicitamente não derivados. Teste `test_sufficient_sample_derives_the_geometry_from_the_barriers`. | `scripts/scalp_jev_eval.py`, `test_scalp_jev_eval_ruler.py` |
| E6 | `evidence/card-a-ruler-report.md` **regenerado** de uma execução real da régua sobre o log do #1015 + OHLCV DEV (§1): 781 chamadas, 3 janelas não sobrepostas, `n_priced` 1, amostra insuficiente declarada. | `evidence/card-a-ruler-report.md` |
| E7 | `apply-evidence.md` §5 passa a **31/31** (as três de evidência/fecho estão resequenciadas para pós-T14/T15, como no próprio `tasks.md`). | `evidence/apply-evidence.md` |
| N1 | `DEFAULT_FEE_BP` documentado e usado **por perna** (10 bp → round-trip 20 bp); todo o custo e o predicado de regime usam `2 × taxa`. Teste `test_the_cost_uses_the_maker_fee_per_leg_everywhere`. | `scripts/scalp_jev_eval.py`, `test_scalp_jev_eval_ruler.py` |
| N2 | `SCALP_CONFIDENCE_MIN` rejeita **não finitos** (`nan`/`inf`) e cai no default conservador (falha fechada); teste alargado com `nan`/`inf`. | `scalp_service.py`, `test_scalp_confidence_gate.py` |
| N3 | Resto abaixo do `MIN_NOTIONAL`/`NOTIONAL` (código de filtro `-1013`) é tratado como **dust**: estado da posição limpo, registo visível, sem re-tentar para sempre. Teste `test_dust_remainder_closes_the_position_instead_of_retrying_forever`. | `scalp_service.py`, `binance_spot_orders.py`, `scalp_binance.py`, `test_scalp_aggressive_exit.py` |
| N4 | Tasks 3.3/3.4 fechadas sem mentir: caminho **explícito** de remoção do gate (`SCALP_CONFIDENCE_MIN=none|off|disabled` → `None`, sem `low_confidence`), com teste; valor calibrado mantido no default porque o Card A declarou amostra insuficiente. | `tasks.md`, `scalp_engine.py`, `scalp_service.py`, `test_scalp_confidence_gate.py` |
| N5 | Barreiras/realizado só com candles **já fechados** dentro de `[start, end]` (sem candle-limite nem `open_time` deslocado). Teste `test_only_closed_candles_inside_the_window_are_read`. | `scripts/scalp_jev_eval.py`, `test_scalp_jev_eval_ruler.py` |
| N6 | Specs reconciliadas: o opt-in cobre **só** o payload cru; o registo de retorno (com os drivers do `book_toxic`, G) é gravado sempre. `openspec validate --strict` verde. | `specs/scalp-confidence-gate/spec.md` |

**Validação desta entrada:** pytest focado **170 passed**; `black --check` limpo (8 ficheiros);
`openspec validate card-1025-jev-destravar-entradas --strict --no-interactive` → **valid**;
`validate_backend_unit_inventory.py` → **87/87**. Sem `process_event`, sem commit/push/PR, sem
reviewers e sem tocar em `frontend/**` ou no painel.
