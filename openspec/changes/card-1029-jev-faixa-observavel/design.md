# Design — card-1029-jev-faixa-observavel

## Context

Card **#1029**, Status=Design. Briefing = issue grelhado (Problema, História, Entra/Critérios, Não entra, Evidência e as **5 decisões fechadas** de 23/09), copiado verbatim em `proposal.md`. Sem reentrevista. **Depende de #1028** (Done técnico, já em `develop` no commit `6a10529e`): o registo de veredictos/versão/origem já existe — este card **assenta** nele, não o reabre. Relacionado com **#1025** (Done técnico, homologado: custo maker, regime, cadência). **SEM-TELA** (backend/registo do scalp Jev; sem painel/Monitor). #1001/#1006/#1008/#1015 não se reabrem.

UI impact: none
live_route: N/A backend/registo do scalp Jev, sem tela
surface: new

Sem rota autenticada, sem landing, sem HTML, sem protótipo. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`. Prototype **N/A**. Impeccable **N/A** (não há superfície visual).

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

### Factos do código actual (lidos no worktree, sem alterar nada)

- **A escala são dez níveis e a interpolação é linear.** `backend/app/services/scalp_jev.py:52` define `_EXPECTED_MOVE_BP_LEVELS_BP: tuple[int, ...] = (0, 5, 10, 15, 20, 25, 30, 35, 50, 80)`; `scalp_jev.py:65-81` (`_bp_from_score`) interpola **linearmente** entre os níveis (`lo_bp + frac * (hi_bp - lo_bp)`); `scalp_jev.py:284-299` (`_expected_move_bp`) usa esse valor interpolado para o `JevSignal` — é exactamente o artefacto que este card remove. Exemplo: `score=3.07` → `15 + 0,07 × 5 = 15,35`; `score=2.86` → `14,30`; `score=0.92` → `4,60` (o artefacto quantizado citado na Evidência do issue; correcção P3 mecanico f-1029-1).
- **A pergunta é `type: score` com os dez níveis como critérios.** `scalp_jev.py:199-206` (`_systemone_payload`) monta `expected_move_bp` com `"type": "score"` e `"criteria": _expected_move_bp_criteria()`; `scalp_jev.py:55-62` devolve `[f"{bp} bp" for bp in _EXPECTED_MOVE_BP_LEVELS_BP]` — números nus, sem qualquer referência ao custo. O construtor do payload (`_systemone_payload`, `scalp_jev.py:182-211`) **não recebe** `fee_bp`/`spread_bp`.
- **A decisão consome `expected_move_bp` em pontos-base.** `backend/app/services/scalp_engine.py:164` (`JevSignal.expected_move_bp`); `scalp_engine.py:241-242` (`reply_gate_verdicts` chama `passes_entry_hurdle`/`passes_regime_gate` com `jev.expected_move_bp`) e `scalp_engine.py:390-410` (os gates de custo devolvem `skip_reason="hurdle"` e `skip_reason="regime"`). O `score` cru é lido à parte por `scalp_jev.py:325-334` (`_move_score`) e registado em `scalp_jev.py:459` (`score=…`).
- **As comparações de custo já existem em `scalp_window.py`, sem limiar novo.** `scalp_window.py:118-119` `entry_hurdle_bp(fee_bp, spread_bp) = 2 × fee_bp + spread_bp`; `scalp_window.py:122-123` `passes_entry_hurdle` compara **estrito** `>`; `scalp_window.py:127` `REGIME_SLACK = Decimal("1.5")`; `scalp_window.py:130-132` `entry_hurdle_bp_with_slack` (× 1,5); `scalp_window.py:135-142` `passes_regime_gate` compara `>=`.
- **Custo real no DEV (facto citado, não medido aqui).** `openspec/changes/card-1025-jev-destravar-entradas/evidence/apply-evidence.md:110,114-116`: `fee_bp = 10 bp por perna` (`commissionRates.maker = 0,00100000`, `spotBNBBurn = true`) ⇒ round-trip **~20 bp**; `hurdle(spread=0,1) = 20,10 bp` e o gate de regime exige **≥ 30,15 bp**. É a fonte destes números; usados só como facto.
- **O registo do ciclo e do retorno já existe e é aditivo (#1015/#1028).** `backend/app/services/scalp_jev_log.py:327-378` (`log_call_return`, com `expected_move_bp=`, `score=`, `model=`, `confidence_origin=`, `noul_label=`); `scalp_jev_log.py:390-421` (`_cycle_suffix`, campos `k=v` depois de `user=`/`skip_reason=`); `scalp_jev_log.py:424-482` (`log_cycle_refusal`/`log_cycle_sent`); `backend/app/services/scalp_service.py:806-841` (`_gate_verdict_fields`/`_write_cycle_record`).
- **A régua read-only do #1025 lê o ficheiro por regex e tolera campos extra.** `scripts/scalp_jev_eval.py:92` `RefusalRe = r"\sscalp cycle refused user=(\S+) skip_reason=(\S+)"` e `:93` `KVRe` sobre `k=v`; campos aditivos na mesma linha **não** a quebram, mas a adjacência `user= … skip_reason=` tem de ser mantida. A régua **não** é alterada (Não entra).
- **A versão do modelo já é fixa e já é gravada (#1028).** `scalp_jev.py:44-49,104-111` (`_DEFAULT_JEV_MODEL = "jev-1.13.0"`, `jev_model()` nunca devolve o apelido); `scalp_engine.py:161-174` (`JevSignal.model`). O A/B deste card **herda** o pin, não o reabre.
- **O gate de confiança é anterior aos de custo e é removível por configuração.** `scalp_engine.py:270` (`confidence_min: Optional[Decimal] = CONFIDENCE_MIN`, `None` remove o gate); `scalp_engine.py:382-388` (`low_confidence`) fecha **antes** de `hurdle` (`:390`) e `regime` (`:401`). O valor do limiar é de outro card (Não entra).
- **DEV-only.** O handler do diagnóstico só é instalado quando `diagnostic_enabled()` (`scalp_jev_log.py:93-99`); o loop DEV corre com `RUN_SCALP_LOOP=1` e o unit PROD não tem a flag. O loop é sequencial por utilizador (`backend/app/services/scalp_loop.py:87-98`).
- **Testes que fixam o contrato a mudar:** `backend/tests/unit/test_scalp_direcional_jev.py:490-492` (`_bp_from_score(5.0) == 25`, `_bp_from_score(4.5) == 22.5`, `_expected_move_bp({... score 5.0}) == 25`) e `backend/tests/unit/test_scalp_jev_consult_cadence.py:243-244` (`criteria == [f"{bp} bp" …]` e `_EXPECTED_MOVE_BP_LEVELS_BP == (0, 5, 10, …, 80)`).

## Vocabulário

- **Posição na escala:** a opção que o modelo escolheu, lida como índice ordenado (0–9) — a resposta continua a ser uma posição, não uma magnitude.
- **Nível já alcançado (nível creditado):** o nível inteiro da escala em que a posição cai, arredondando **para baixo** (`floor`); o seu bp **exacto** (um valor da escada) é o único bp que a comparação de custo usa.
- **Faixa do ciclo:** uma de três — `below_cost` (abaixo do custo), `covers_cost` (cobre o custo, sem a folga), `covers_with_slack` (cobre com folga) — classificada pelo **nível creditado** contra o **custo real daquele ciclo**.
- **Custo real do ciclo:** o `hurdle` do #1025 (`2 × fee_bp + spread_bp`, taxa maker real por perna) e o custo com folga (`hurdle × 1,5`).
- **Rótulo do modelo:** o texto de cada uma das dez opções da pergunta; passa a nomear a **faixa daquele ciclo** em vez de um número nu.
- **A/B:** a leitura read-only que compara a **confiança média** obtida com a janela de estado actual e com uma janela maior, na mesma versão fixa de modelo.
- **Não-regressão declarada:** os gates que não são de custo mantêm a decisão; a decisão de custo **muda por desenho** (nível creditado em vez de valor interpolado) e isso é contrato visível.

## Goals / Non-Goals

**Goals:**

- A decisão de entrada passa a comparar a **faixa do nível já alcançado** com o **custo real do ciclo**, sem converter a posição num bp interpolado.
- As fronteiras das faixas acompanham a taxa real do ciclo (sem faixas fixas na escala) e **sem limiar novo** (reuso dos predicados existentes).
- A interpolação linear sai do caminho de decisão; o registo mostra **faixa + posição** e nunca um bp interpolado; o artefacto 15,0 / 15,35 / 14,30 deixa de ser produzido.
- O modelo continua a responder **uma posição** (dez opções), com o **rótulo em faixas**.
- Um **A/B** mede a confiança média com a janela actual e a janela maior, mesma versão fixa, amostra declarada, mínimo de **30 janelas de 900 s não sobrepostas**; abaixo disso, **amostra insuficiente**.

**Non-Goals:**

- Mudar o valor do limiar de confiança, a ordem dos gates de confiança/atraso/hold/toxicidade ou o primeiro `skip_reason` desses gates.
- Mudar a geometria de alvo/stop, o tempo de espera ou o escape de saída.
- Mudar o corte de toxicidade.
- Reabrir #1028 (veredicto dos gates, origem da confiança, versão pinada, faixa de toxicidade, tempo limite).
- Expor no painel/Monitor/`/api/scalp/status`; base de dados nova, dashboard, exportação/Drive, backtest; alterar a régua read-only do #1025.
- PROD nesta entrega (T16, no lote).

## Decisions

1. **As faixas relativas ao custo são materializadas pelo nível creditado contra o hurdle e o slack reais, reusando `passes_entry_hurdle` / `passes_regime_gate` — sem limiar novo.** Seja `L` o bp exacto do nível creditado e `H = entry_hurdle_bp(fee_bp, spread_bp)`, `S = entry_hurdle_bp_with_slack(fee_bp, spread_bp)`. A faixa é `covers_with_slack` se `passes_regime_gate(L, fee_bp, spread_bp)`; senão `covers_cost` se `passes_entry_hurdle(L, fee_bp, spread_bp)`; senão `below_cost`. A comparação continua a viver **onde já vive** (`scalp_window.py`) e é chamada com `L`; nenhuma fronteira é acrescentada à escala e nenhuma constante nova nasce. A semântica estrita `>` do hurdle e `>=` do regime permanece exactamente a do #1025.
   *Alternativa rejeitada —* **faixas fixas na escala** (p.ex. «abaixo de 20 bp»): viola a decisão do dono («as fronteiras acompanham a taxa real do ciclo; não há faixas fixas na escala») e volta a medir uma magnitude que a escala não tem.
   *Alternativa rejeitada —* **recalcular a comparação no caminho do registo** (nova função de bandas no `scalp_jev_log`/`scalp_service`): duplicaria o limiar e a proxy divergiria do que a decisão consumiu — o inverso do que o #1028 fixou («valor e origem na mesma função»).

2. **A interpolação linear sai do caminho de decisão; a posição passa a ser lida como nível creditado (arredonda para baixo).** `_bp_from_score` deixa de ser chamada; passa a existir a leitura do **nível já alcançado**: `score` recortado a `[0, len(levels)-1]` e arredondado para baixo por `floor`, e o bp devolvido é `_EXPECTED_MOVE_BP_LEVELS_BP[índice]` — um valor **exacto** da escada. A escada (dez níveis) **não muda** (Não entra: «mudar a escada de níveis»). O `JevSignal` leva a posição/índice além do bp do nível creditado, para o registo.
   *Alternativa rejeitada —* **manter a interpolação e só mudar o rótulo**: o artefacto 15,35 / 14,30 / 9,60 continuaria a ser produzido e comparado — é exactamente o que o card remove.
   *Alternativa rejeitada —* **comparar o `score` cru como número** (p.ex. 4,5 contra 20,10): misturaria unidades (índice de escala vs pontos-base) e quebraria os predicados de custo, que são contas em bp.
   *Alternativa rejeitada —* **arredondar para o nível mais próximo**: a decisão do dono é creditar o **nível já alcançado** («só passa quem atinge o nível inteiro que cobre o custo»), ou seja, para baixo.

3. **`expected_move_bp` muda de significado — declarado como contrato visível.** Antes: valor **interpolado** entre níveis (`score 3.07` → `15,35` bp). Depois: o bp **exacto do nível já alcançado** (`score 3.07` → `15` bp). O campo continua a ser a única entrada dos predicados de custo e dos veredictos (`scalp_engine.py:241-242,390-410`), que **não** mudam de fórmula; o que muda é o valor que recebem. Não é um efeito lateral: é o núcleo do card.
   *Alternativa rejeitada —* **renomear o campo** (p.ex. `credited_move_bp`): a régua read-only do #1025 lê `expected_move_bp=` por `KVRe` (`scripts/scalp_jev_eval.py:93`) e renomear obrigaria a mexer na régua (Não entra). O campo fica com o nome e o valor passa a ser sempre um valor da escada.
   *Alternativa rejeitada —* **manter os dois valores** (interpolado para decidir, creditado para registar): seria decidir por uma conversão que o fornecedor diz para não fazer e manter o artefacto.

4. **O registo mostra a faixa escolhida e a posição na escala, e nunca um bp interpolado.** Os registos (`log_call_return` e o registo do ciclo) ganham, de forma **aditiva**, a faixa (`move_band`) e a posição (`move_position`), mantendo `score=` (o `score` cru, já registado, é a posição) e `expected_move_bp=` com o **bp exacto do nível creditado**. Depois do card, nenhum campo do registo pode carregar um bp que não seja um nível da escada; o artefacto 15,0/15,35/14,30/9,60 deixa de aparecer.
   *Alternativa rejeitada —* **só `expected_move_bp` com o valor creditado**: cumpriria «nunca bp interpolado», mas não cumpriria «o registro mostra sempre **a faixa escolhida e a posição na escala**» (critério observável). Os campos novos são o mínimo para ler as duas coisas.
   *Alternativa rejeitada —* **um segundo registo só para a faixa/posição**: violaria o «no mesmo registro» e inflaria o ficheiro sem necessidade (o registo do ciclo já existe desde o #1028).

5. **O rótulo que o modelo vê são as faixas daquele ciclo, com as dez opções preservadas.** `_expected_move_bp_criteria()` passa a ser **cost-aware**: para os dez níveis ordenados, o rótulo de cada opção é a faixa daquele nível face ao custo do ciclo (`below_cost` / `covers_cost` / `covers_with_slack`), calculada **pelos mesmos predicados** da decisão. O `type` continua `score`, as **dez opções continuam a existir** e a resposta continua a ser uma **posição** (índice). Assim, a faixa que o modelo escolheu e a faixa que a decisão deriva do nível creditado **coincidem** por construção.
   *Alternativa rejeitada —* **manter `"{bp} bp"`**: é o «número nu» que o dono mandou substituir (critério observável).
   *Alternativa rejeitada —* **colapsar a pergunta a três opções** (uma por faixa): deixaria o modelo de responder «uma posição na escala» (decisão do dono) e apagaria a leitura do nível já alcançado / do arredondamento para baixo.
   *Alternativa rejeitada —* **faixas fixas no rótulo** (p.ex. «cobre 20 bp»): viola «não há faixas fixas na escala».

6. **Recusa por custo = token de custo que já existe, com um motivo só; a faixa mais baixa não ganha motivo próprio.** `below_cost` fecha como `skip_reason="hurdle"`; `covers_cost` fecha como `skip_reason="regime"`; `covers_with_slack` passa a regra de custo. Nenhum token novo é criado e a faixa mais baixa não ganha razão própria. O gate de confiança e a sua ordem **não** são tocados: com o gate **removido** (`confidence_min=None`, o modo a que a calibração aponta e onde a decisão é previsão × custo × regime), uma posição abaixo do custo fecha **por custo**, nunca por confiança; com o gate **ligado** e a falhar, o ciclo fecha em `low_confidence` como hoje (o limiar/ordem da confiança é outro card — Não entra).
   *Alternativa rejeitada —* **novo `skip_reason` para a faixa mais baixa** (p.ex. `below_cost`): viola a decisão do dono («com um motivo só no registro … a faixa mais baixa não ganha motivo próprio»).
   *Alternativa rejeitada —* **reordenar o custo antes da confiança**: mudaria a decisão de ciclos cuja confiança também falha, fora do que este card autoriza (o limiar/o gate de confiança é o card do limiar) e contra a não-regressão do #1028. Declarado: a ordem vigente é preservada.

7. **O A/B mede a confiança média nos dois braços, com a versão fixa do #1028, e só conclui com ≥30 janelas de 900 s não sobrepostas.** O A/B é uma leitura **read-only** sobre os registos de diagnóstico: cada registo passa a declarar o **braço** (janela actual / janela maior) e a confiança; a amostra é agrupada em **janelas de 900 s não sobrepostas**; a comparação exige a **mesma versão fixa de modelo** (a do #1028) e **declara o tamanho da amostra**; conclui com a **confiança média** de cada braço; com menos de **30 janelas de 900 s não sobrepostas** **não conclui** e escreve **`amostra insuficiente`**.
   *Alternativa rejeitada —* **concluir com menos janelas**: é a decisão do dono («mínimo de 30 janelas de 900 s não sobrepostas») e a lição do #1025 («amostra insuficiente tem de ser declarada, não concluída»).
   *Alternativa rejeitada —* **correr dois modelos** (um por braço): violaria «com a mesma versão de modelo fixa» e confundiria o efeito da janela com o efeito da versão.
   *Alternativa rejeitada —* **levar o A/B ao painel/Monitor**: Não entra.

8. **Fronteira de ambiente: só DEV, só log, sem PROD.** Destino é o ficheiro de diagnóstico do #1015 (ficheiro único, tecto e truncagem de cauda inalterados), instalado só quando `diagnostic_enabled()`; sem `frontend/**`, sem rota/HTML, sem painel/Monitor/`/api/scalp/status`, sem base de dados, sem dashboard/exportação/Drive/backtest. PROD é T16, no lote.
   *Alternativa rejeitada —* **expor as faixas/posição no Monitor**: Não entra (decisão do #1015).

9. **Não-regressão declarada separando o que fica do que muda por desenho.** Ficam idênticos: confiança, `hold`, `jev_late`, `toxic_book`, os gates de dimensionamento, a cadência, o payload de estado. Muda **por desenho**: o valor de custo comparado (nível creditado em vez de interpolado) e, como consequência, a decisão de custo de algumas posições entre níveis — o que o card quer e o que a decisão do dono 4 fixa. Os testes que fixam a interpolação (`test_scalp_direcional_jev.py:490-492`) e a lista de critérios nus (`test_scalp_jev_consult_cadence.py:243-244`) passam a afirmar o contrato novo.
   *Alternativa rejeitada —* **prometer não-regressão total da decisão**: seria falso — o card existe exactamente para mudar a leitura de custo das posições entre níveis (arredonda para baixo).

## Risks / Trade-offs

- [Risco] Reusar `expected_move_bp` para o bp do nível creditado muda o significado do campo para outros leitores (régua `scalp_jev_eval.py`, testes). Mitigação: decisões 3 e 4 — declarado como contrato visível; o campo continua a ser um bp de um nível da escada; a faixa e a posição viajam em campos aditivos e a régua **não** é alterada (Não entra).
- [Risco] O rótulo em faixas mudar a distribuição das respostas do modelo e invalidar a comparação com a calibração histórica por bucket de `score`. Mitigação: o `score` cru continua a ser registado (`score=`) e a escala (dez níveis) não muda; o A/B é o instrumento para medir o efeito da janela com a versão fixa. Trade-off declarado.
- [Risco] O construtor do payload não recebe o custo (`_systemone_payload`, `scalp_jev.py:182-211`): o rótulo por faixa exige passar `fee_bp`/`spread_bp` (ou o `hurdle`/`slack`) até à pergunta, e o orçamento de entrada do #1025 (≤ ~500 tokens) tem de continuar a caber. Mitigação: a faixa substitui o token de bp (mesma ordem de bytes); a verificação do orçamento e a forma de passagem são P3 (Apply).
- [Risco] Várias das dez opções partilharem a mesma faixa (quando o custo corta a escada), o modelo responder «a faixa» e perder-se a posição. Mitigação: a pergunta mantém dez opções **ordenadas** e a resposta é o índice (`score`); o registo mostra a faixa **e** a posição; o texto exacto do rótulo é P3.
- [Risco] `passes_entry_hurdle` é estrito (`>`): um nível creditado exactamente igual ao hurdle cai em `below_cost` e é recusado. Mitigação: reuso sem limiar novo (decisão 1); o nível creditado é um valor da escada e a igualdade é caso-limite; declarado nos cenários (a semântica do #1025 não muda).
- [Risco] O A/B precisa de amostra real de ambas as janelas e o loop é sequencial por utilizador (`scalp_loop.py:87-98`, cadência 30 s do #1025). Mitigação: o A/B é read-only sobre o log e a coleta dos dois braços (tamanho/conteúdo da janela maior, alternância) é P3; o piso de 30 janelas não sobrepostas protege contra conclusão prematura.
- [Risco] Concluir o A/B com amostra insuficiente. Mitigação: decisão 7 + cenário de spec (`amostra insuficiente`).
- [Trade-off] O arredondamento para baixo torna a entrada mais conservadora (posições entre níveis perdem). Aceite e pretendido: «só passa quem atinge o nível inteiro que cobre o custo».
- [Trade-off] O registo fica com mais chaves (faixa, posição, braço). Aceite: o tecto de 200 MB e a truncagem de cauda do #1015 já limitam o ficheiro; o dado é o que o card pede.
- [Trade-off] O `hurdle`/`regime` passam a ser a leitura de custo que «decide», e a posição na escala deixa de prometer magnitude exacta. Aceite: é o que o fornecedor documenta e o que a Evidência do #1025 homologou.

## Apply contract

**Contrato visível (não P3):**

- **Faixas relativas ao custo do ciclo:** três faixas — **abaixo do custo**, **cobre o custo**, **cobre com folga** — cujas fronteiras são o `hurdle` real do ciclo (`2 × fee_bp + spread_bp`) e o custo com folga (`hurdle × 1,5`); **não há faixas fixas na escala** e **nenhum limiar novo** é introduzido (reuso de `passes_entry_hurdle` estrito `>` e `passes_regime_gate` `>=`).
- **Decisão:** posição abaixo do custo ⇒ **recusa por custo** (`skip_reason="hurdle"`), **um motivo só**, sem token próprio para a faixa mais baixa; cobre o custo sem folga ⇒ `skip_reason="regime"`; cobre com folga ⇒ **passa a regra de custo**. O **nível já alcançado** é creditado com **arredondamento para baixo** (posição entre níveis ≠ crédito do nível de cima).
- **Sem interpolação:** o valor derivado por interpolação linear entre níveis **sai do caminho de decisão**; nenhum bp interpolado é usado para decidir nem escrito no registo.
- **Registo:** todo registo que carrega a resposta mostra sempre a **faixa escolhida** e a **posição na escala**; o bp, quando aparece, é o **bp exacto de um nível da escada** (o do nível creditado); o artefacto 15,0 / 15,35 / 14,30 / 9,60 **deixa de ser produzido**.
- **Pergunta:** as **dez opções continuam a existir** e a resposta continua a ser uma **posição**; o rótulo que o modelo vê são as **faixas daquele ciclo**, não números nus.
- **`expected_move_bp` muda de significado** (de valor interpolado para bp do nível já alcançado do ciclo) — declarado como contrato visível; os predicados de custo e os tokens `hurdle`/`regime` **não** mudam de fórmula nem de nome.
- **Confiança intocada:** o valor do limiar de confiança e a ordem dos gates (confiança antes do custo) **não** mudam; com o gate removido, abaixo-do-custo fecha por custo.
- **A/B:** registra a **confiança média com a janela actual e com a janela maior**, com a **mesma versão fixa de modelo** (pin do #1028) e o **tamanho da amostra** declarado; conclui **apenas** com **≥30 janelas de 900 s não sobrepostas**; abaixo disso **não conclui** e o registo escreve **`amostra insuficiente`**; é read-only e **não** altera a decisão.
- **Só log / só DEV:** destino é o ficheiro de diagnóstico do #1015 (ficheiro único, tecto e truncagem inalterados); sem painel/Monitor/`/api/scalp/status`, sem rota/HTML, sem base de dados, sem dashboard/exportação/Drive/backtest; PROD fora (T16).
- **Sem alterar a régua read-only do #1025** (`scripts/scalp_jev_eval.py`) nem o prefixo `scalp cycle refused` / a adjacência `user= … skip_reason=`.

**P3 — detalhe de Apply (aceito aqui, resolvido no Apply — não reabrir como P0/P1):**

- Nomes exactos das chaves novas do registo (`move_band`, `move_position`, `move_level_bp`, braço do A/B), ordem e separador; se `expected_move_bp=` mantém o nome; se o `score=` cru permanece como posição.
- Texto exacto do rótulo que o modelo vê (separador, ordinal, se o bp do nível aparece junto à faixa) e **como** o `fee_bp`/`spread_bp` (ou o hurdle/slack) chegam a `_systemone_payload`/`_expected_move_bp_criteria`; reverificação do orçamento de entrada do #1025.
- Nome da função do **nível creditado** e se `_bp_from_score` é apagada ou fica sem uso; tratamento dos fallbacks `number`/`value` (mantêm a leitura literal de hoje, declarados fora do contrato de faixa, ou passam a `unknown`).
- Interface A/B: nome/path do script read-only (estender a régua do #1025 vs ficheiro novo), **tamanho e conteúdo da janela maior**, **como** os dois braços são coletados (env que alterna a janela de estado / replay), algoritmo de agrupamento em janelas de 900 s não sobrepostas e formato de saída.
- Forma como os testes injectam resposta/`urlopen` falsos e verificam os campos novos; actualização das asserções de contrato (`test_scalp_direcional_jev.py:490-492` e `test_scalp_jev_consult_cadence.py:243-244`).
- Se a faixa/posição entram também no registo de **entrada** (`log_call_entry`, escrito antes da resposta) ou ficam circunscritas ao retorno/ao ciclo.

## Open Questions

Nenhuma. A fronteira veio grelhada (5 decisões fechadas) e os *como* fecham nas decisões 1–9. O que falta (tamanho/conteúdo da janela maior, texto exacto do rótulo) é detalhe de Apply (P3) e resolve-se no Apply, não com o dono.

## Design Critique

Publicada pelo pai após a onda de crítica (excepção prevista no runbook). Sem-tela: o crítico é **um**; sem onda A/B, sem protótipo, sem clone de página viva e sem Snapshot Impeccable.

**Onda (teto 1+1+1, sem-tela):** 1 autor → 1 crítico → **sem rework**. `rework: nao`, `p0_p1_count: 0`. A coluna segue para `Aprovação de Design`.

**Crítico, ronda única:** rubrica 7/7 `ok` (tokens do gate, briefing verbatim, escopo, decisões com alternativa rejeitada, contrato visível vs P3, cobertura dos critérios observáveis, tasks). Um único achado, classificado pelo crítico como **P3 mecanico**, `bloqueia_merge: nao` — gravidade e classe copiadas do dump, sem reclassificação:

| id | gravidade | classe | bloqueia_merge | achado | fecho |
| --- | --- | --- | --- | --- | --- |
| f-1029-1 | **P3** | mecanico | nao | Exemplo numérico falso: `design.md` afirma `score=0.92 → 9,60` e o cenário «The quantization artifact is no longer produced» da spec `scalp-jev-scale-record` lista `(15 / 10 / 5)` para `(3.07, 2.86, 0.92)`. O real é `_bp_from_score(0.92) = 4,60` (floor ⇒ `0`); `9,60` vem de `score=1,92`. | **Aceito como P3** (detalhe de Apply): o contrato — nível creditado (floor) → bp **exacto** da escada — **não** muda. O Apply corrige os números ilustrativos ao reescrever as asserções, e o cenário passa a afirmar o contrato novo. |

**P3 aceitos** (detalhe de Apply; registados como aceites e resolvidos no Apply, nunca reabertos como P0/P1):

- Chaves/ordem/separador das novas entradas do registo e se `expected_move_bp=`/`score=` mantêm o nome.
- Texto exacto do rótulo em faixas e **como** o `fee_bp`/`spread_bp` (ou hurdle/slack) chegam a `_systemone_payload`/`_expected_move_bp_criteria`; reverificação do orçamento ≤ ~500 tokens do #1025.
- Nome da função do nível creditado, destino de `_bp_from_score` (apagada/sem uso) e tratamento dos fallbacks `number`/`value`.
- Interface do A/B: path do script read-only, tamanho/conteúdo da janela maior, coleta dos dois braços, agrupamento em janelas de 900 s não sobrepostas, formato de saída.
- Injeção de resposta/`urlopen` falsos nos testes e actualização das asserções de contrato.
- Se a faixa/posição entram também no registo de entrada (`log_call_entry`).

**Sem achados de produto/escopo:** confirmado — nada do «Não entra» entrou (limiar/ordem da confiança, geometria alvo/stop, corte de toxicidade, painel/Monitor, PROD, DB/dashboard/backtest); as **5 decisões fechadas do dono** foram tratadas como lei e não reabertas; briefing verbatim em `proposal.md`; 3 capabilities / 9 requisitos / 27 cenários dão cobertura aos critérios observáveis do issue.

**Factos verificados pelo crítico** (o que bate certo): escada e `_bp_from_score` (`scalp_jev.py:52,65-81`, `:284-299`); `_systemone_payload` sem custo (`:182-211`); predicados de custo (`scalp_window.py:118-123,127,130-142`); ordem da confiança antes do custo (`scalp_engine.py:382-388` vs `:390`,`:402`); registo aditivo (`scalp_jev_log.py:327-378,390-421`); régua tolerante a campos aditivos (`scalp_jev_eval.py:92-93`); testes de contrato (`test_scalp_direcional_jev.py:490-492`, `test_scalp_jev_consult_cadence.py:243-244`); `validate --strict` verde; custo DEV da evidência do #1025 (`apply-evidence.md:110,114-116`: `fee_bp=10`, `hurdle(spread=0,1)=20,10`, regime `30,15`). Drift menor de números de linha citados (`GATE_ORDER` l.47-54 vs 49-55; regime `:401` vs `:402`) — P3 de Apply, sem efeito no contrato.

**Proxies do handoff:** spawns = **2** (autor, crítico; sem rework). `design.md` final: ver contagem em baixo. HTML generated vs copied = **N/A vs N/A** (sem protótipo). Prototype **N/A**. Impeccable **N/A**. Cliente Cursor: os dois filhos de juízo correram com o slug `juizo` do `.cursor/model-map.yaml`.

### Re-submissão (T17 · I4) — 23/09

Depois do T7 e do Apply (22/22 tasks, sem P0), o filho Apply resolveu o P3 `f-1029-1` **no próprio `design.md`** (corrigiu `score=0.92 → 9,60` para `4,60`). Como o digest do Design é o hash do `design.md`, isso invalidou o congelamento do T7: `pedir_review` devolveu `I4` e a FSM aplicou o **T17b** (`Em desenvolvimento → Design`), com a razão visível `digest_changed`. O dono escolheu **aceitar o T17** em vez de restaurar um número que o crítico provou ser falso.

Esta re-submissão (T5) **não** introduz nenhuma decisão nova: leva apenas o número corrigido (P3 `f-1029-1`) e o registo deste evento. As **9 decisões**, as 3 capabilities e o Apply contract ficam **inalterados**. O trabalho de código do Apply (22/22 tasks, sem P0) permanece **não commitado** no worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-1029-jev-faixa-observavel` e é **re-verificado** na nova entrada em `Em desenvolvimento`, após o novo T7.
