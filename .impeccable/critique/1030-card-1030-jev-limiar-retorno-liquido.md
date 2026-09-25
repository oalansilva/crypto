# Relatório do autor — Design do card #1030

**Change:** `openspec/changes/card-1030-jev-limiar-retorno-liquido/`
**Worktree/branch:** `card-1030-jev-limiar-retorno-liquido` @ `/srv/apps/dev/criptofarol/crypto-worktrees/card-1030-jev-limiar-retorno-liquido` (a partir de `develop` @ `6a10529e`)
**Status:** Design (T3 → Design). Sem-tela.
**Tokens do gate (linha própria parseável):**

UI impact: none
live_route: N/A régua read-only e limiar de confiança no backend/harness do scalp Jev; não há tela de produto
surface: new

Prototype **N/A** (sem superfície visual a clonar; backend/harness). Impeccable **N/A** (sem UI/copy a polir). **Nota:** este relatório é do autor; **não** declara veredito de crítica e não inclui `## Design Critique` (essa seção é do pai, depois do crítico).

## 1. O que li (fontes de verdade)

- `.cursor/skills/openspec-new-change/SKILL.md` e `.cursor/skills/openspec-ff-change/SKILL.md` (bloco «Bound grilled issue»: o issue grelhado é o briefing; `proposal.md` copia Problema/História/Entra/Não entra verbatim; sem `grill-card`).
- `.cursor/skills/design-critic/SKILL.md` (bloco **D4** e tokens do gate do autor; teto sem-tela 1+1+1).
- `.cursor/skills/covenant-flow/SKILL.md` (runbook: gates de coluna, Gist superset do issue, sem `## Design Critique` no `design.md` do autor).
- `AGENTS.md` (always-on: não inventar aresta; `Todo` não é código; Design antes de `Pronto para Dev`).
- Body do issue **#1030** só por REST (`gh api repos/oalansilva/crypto/issues/1030 --jq .body`); **não** usei `gh issue view`. Também li o body do **#1029** por REST, para declarar a dependência sem inventar (não toquei no escopo dele).
- Código e artefactos no worktree: `scalp_engine.py`, `scalp_window.py`, `scalp_service.py`, `scalp_jev_log.py`, `scalp_jev_payload.py`, `scripts/scalp_jev_eval.py`, `openspec/changes/card-1025-jev-destravar-entradas/*`, `openspec/changes/card-1028-jev-veredictos-origem/*`, `ops/systemd/criptofarol-dev-runtime-worker.service`, testes unitários do scalp.

## 2. Dependências conferidas no worktree (não assumidas)

- **#1028 Done e integrado em `develop` @ `6a10529e`** — o registo de veredictos existe: `scalp_engine.py:49-57` (`GATE_ORDER`), `:178-190` (`GateVerdicts`), `:192-212` (`CycleIntent.gate_verdicts`), `:217-243` (`reply_gate_verdicts`); `scalp_service.py:807-840` (`_gate_verdict_fields` / `_write_cycle_record`); `scalp_jev_log.py:392-490` (`_cycle_suffix` / `log_cycle_refusal` / `log_cycle_sent`). O registo de retorno traz a **versão que respondeu** (`model=`), a **origem da confiança** (`confidence_origin=`) e o **rótulo de toxicidade** (`noul_label=`) — `scalp_jev_log.py:325-378`.
- **#1029 em Design, não implementado** — `expected_move_bp` continua interpolado da escala; a leitura por faixa ainda não existe. O design **não** a implementa nem a antecipa: a população elegível reflecte a leitura em vigor e a recalibração depois do #1029 fica **declarada** (decisão 7 do `design.md`).

## 3. Decisões e alternativas rejeitadas (resumo do `design.md`)

1. **Acurácia + retorno líquido por faixa, com amostra, por regime.** A `_stats` da régua ganha acurácia ao lado da expectancy. Rejeitado: escolher o limiar pela acurácia (proibido pelo Entra) e manter só a expectancy (não mostra cobertura).
2. **Limiar por retorno líquido esperado = ganho esperado × cobertura**, com a taxa real por perna; `argmax` entre candidatos com amostra suficiente. Rejeitado: a regra do #1025 (menor faixa positiva) — ignora a cobertura e não é por regime.
3. **Um limiar por regime de mercado (σ da janela) com fronteira única partilhada.** Rejeitado: o predicado do gate de regime do #1025 (o lado calmo já é fechado por esse gate → limiar vazio; e lê `expected_move_bp`, que é o que o #1029 muda); mediana da amostra (não reproduzível na decisão).
4. **Política por regime: numérico | desligado | fechado.** Rejeitado: limiar único global; token `regime` reaproveitado para o fecho.
5. **Fecho por amostra insuficiente é estado explícito e o valor em uso é preservado.** Rejeitado: depender de o valor em uso (0,7) ser inalcançável (é o acidente que o card corrige).
6. **Separação por retorno líquido; não separa → limiar desligado.** Rejeitado: monotonicidade da acurácia; quarto estado «fecha por não dar lucro» (reabriria a decisão «não separa → desliga»).
7. **População elegível pelos veredictos registados + homogeneidade (versão/origem) declarada.** Rejeitado: medir sobre todas as respostas (inflaciona a cobertura com ciclos recusados por custo/regime); medir origem/versão só em agregado.
8. **Custo = taxa real por perna da conta, registada com a origem.** Rejeitado: a régua ir à conta (deixaria de ser read-only/offline); default conservador como número neutro.
9. **Configuração explícita e reversível, com falha fechada.** Rejeitado: default numérico aberto; aceitar `nan`/`inf`/fora de [0,1].

## 4. Factos com ficheiro:linha (conferidos no worktree)

- `backend/app/services/scalp_engine.py:14` — `CONFIDENCE_MIN = Decimal("0.7")`; `:382` — gate `low_confidence`; `:391` — `hurdle`; `:401-410` — `regime` (custo + folga); `:412` — `toxic_book`. A confiança decide **antes** dos outros.
- `backend/app/services/scalp_engine.py:49-57` — `GATE_ORDER`; `:217-243` — `reply_gate_verdicts` (o `low_confidence` é `not_applicable` quando `confidence_min is None`); `:178-190` — `GateVerdicts`.
- `backend/app/services/scalp_service.py:96-120` — `_confidence_min()` (`SCALP_CONFIDENCE_MIN`; `none|off|disabled` → `None`; não finitos/fora de [0,1] → default; falha fechada em `:111-119`); `:807-840` — `_gate_verdict_fields`/`_write_cycle_record`; `:1189` — `confidence_min=_confidence_min()` na chamada pós-resposta.
- `backend/app/services/scalp_window.py:118-123` — `entry_hurdle_bp = 2 × fee_bp + spread` e `passes_entry_hurdle`; `:127` — `REGIME_SLACK = 1.5`; `:130-142` — `entry_hurdle_bp_with_slack`/`passes_regime_gate`.
- `backend/app/services/scalp_window.py:28-36` — `WindowMetrics.vol_bp`; `:72-113` — `window_metrics`; `backend/app/services/scalp_jev_payload.py:65-69` (`build_window`) e `:132` (`state.window.vol_bp`).
- `backend/app/services/scalp_jev_log.py:313-322` — `log_call_entry` (grava o `state`, incluindo `window.vol_bp`); `:325-378` — `log_call_return` (model/confidence_origin/noul_label/window_*); `:392-490` — `_cycle_suffix`/`log_cycle_refusal`/`log_cycle_sent`.
- `scripts/scalp_jev_eval.py:66` — `DEFAULT_FEE_BP = 10`; `:68` — `REGIME_SLACK`; `:70` — `MIN_NON_OVERLAPPING_WINDOWS = 30`; `:71` — `MIN_BUCKET_TRADES = 20`; `:72` — `CONFIDENCE_BUCKET_WIDTH = 0.1`; `:90-94` — `EntryRe`/`ReturnRe`/`RefusalRe`/`KVRe`/`TimestampRe`; `:462-485` — `_stats` (sem acurácia); `:511-519` — `confidence_bucket`; `:615+` — `build_report`; `:690-733` — segmentação σ (mediana) e predicado do gate; `:740-757` — proposta do menor bucket positivo; `:856-866` — declaração de insuficiência; `:912` — `--fee-bp`.
- `backend/tests/unit/test_scalp_jev_eval_ruler.py` — contrato actual da régua (incluindo `test_the_instrument_is_read_only` e `test_sufficient_sample_proposes_the_lowest_positive_bucket`, a mudar/estender no Apply); `backend/tests/unit/test_scalp_confidence_gate.py` — contrato actual do gate por env e da remoção.
- `ops/systemd/criptofarol-dev-runtime-worker.service` — `RUN_SCALP_LOOP=1` (DEV); o unit PROD não tem a flag (`scalp_jev_log.py:93-108` arma o log pelo mesmo flag).

## 5. Riscos

- Amostra DEV insuficiente por regime → bot fica fechado (resultado válido e decidido no card; declarado, nunca concluído).
- Amostra com origens de confiança/versões misturadas → confundir faixa com artefacto (homogeneidade declarada; sem homogeneidade não propõe limiar).
- #1029 mudar a população elegível (hurdle/regime passam a ler a faixa) → relatório antigo inválido em silêncio (declarar a leitura/modelo em vigor; recalibração pós-#1029 é requisito).
- Fronteira de regime mal configurada/ausente → aplicar o limiar à população errada ou não operar (fronteira única partilhada; ausente → ambos fechados).
- `argmax` escolher cobertura minúscula → mínimos de amostra (30 população / 20 faixa) e cobertura visível ao lado do ganho.
- Token de recusa novo quebrar a régua do #1025 → é um **valor** novo de `skip_reason`, não um prefixo; `RefusalRe`/`KVRe` toleram (`:92-94`), a régua não é alterada.
- Régua deixar de ser read-only → recebe valores por argumento; o teste de read-only existente cobre o ficheiro.

## 6. O que deixei em aberto (não decidido no Design)

- **Valores concretos** (limiar por regime e fronteira de σ): dependem do relatório da régua; não fixados aqui — é o mesmo critério do #1025 («nenhum limiar sem o relatório»).
- **Dependência #1029**: a população elegível reflecte a leitura da previsão em vigor; a recalibração depois do #1029 é requisito declarado, não comportamento assumido.
- **P3 (detalhe de Apply):** nomes exactos das configurações e do token de fecho; largura/fronteira exactas; conjunto de limiares candidatos; forma da tabela da curva do limiar; como o serviço calcula o regime na decisão (mesma σ do payload); como os testes injectam população/fronteira/políticas.
- **Não apurado:** a lista completa de faixas com amostra suficiente no log DEV actual (a régua do #1025 declarou amostra insuficiente; a régua estendida ainda não existe para medir) — é resultado do Apply, não do Design.

## 7. Ficheiros do pacote

- `openspec/changes/card-1030-jev-limiar-retorno-liquido/proposal.md` (Problema/História/Entra/Não entra/Evidência **verbatim** do issue, conferido por comparação programática).
- `openspec/changes/card-1030-jev-limiar-retorno-liquido/design.md`.
- `openspec/changes/card-1030-jev-limiar-retorno-liquido/tasks.md` (todas as caixas `- [ ]`).
- `openspec/changes/card-1030-jev-limiar-retorno-liquido/specs/scalp-jev-net-return-ruler/spec.md`.
- `openspec/changes/card-1030-jev-limiar-retorno-liquido/specs/scalp-confidence-threshold-per-regime/spec.md`.
- Este relatório. `openspec validate card-1030-jev-limiar-retorno-liquido --strict` verde (4/4 artefactos).

`proxy modelo: design-autor → deepseek-flash (deepseek-flash)`
