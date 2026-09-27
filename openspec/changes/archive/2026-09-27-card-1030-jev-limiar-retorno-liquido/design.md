## Context

Card **#1030**, Status=Design, cliente Cursor Agent. Briefing = issue grelhado (`## Problema`, `## História`, `## Entra` com critérios observáveis, `## Não entra`, `## Evidência`), copiado **verbatim** em `proposal.md`; sem reentrevista. **SEM-TELA** (backend/harness): régua de avaliação e limiar de confiança do scalp Jev. Sem rota, sem protótipo, sem painel/Monitor, sem base de dados nova.

**Dependências (confirmadas no worktree, sem assumir):**

- **#1028 está Done e integrado em `develop` @ `6a10529e`** — o registo de veredictos dos gates já existe no worktree: `backend/app/services/scalp_engine.py:49-57` (`GATE_ORDER`), `:178-190` (`GateVerdicts`), `:192-212` (`CycleIntent.gate_verdicts`), `:217-243` (`reply_gate_verdicts`); `backend/app/services/scalp_service.py:807-840` (`_gate_verdict_fields` / `_write_cycle_record`); `backend/app/services/scalp_jev_log.py:392-490` (`_cycle_suffix` / `log_cycle_refusal` / `log_cycle_sent`). O registo de retorno passou a trazer a **versão do modelo que respondeu** (`model=`), a **origem da confiança** (`confidence_origin=`) e o **rótulo de toxicidade** (`noul_label=`) — `scalp_jev_log.py:325-378`.
- **#1029 está em Design e não implementado** — a "previsão como faixa observável" ainda **não existe**: `expected_move_bp` continua a vir da interpolação da escala (`scalp_jev.py::_bp_from_score`) e é o que alimenta os gates `hurdle` e `regime`. Este design **não** implementa nem antecipa a leitura por faixa: a régua consome o realizado e o registo, e **declara** que a população elegível (que passa custo/regime) reflecte a leitura em vigor e a versão do modelo dessa amostra; a recalibração depois do #1029 fica **declarada como dependência**, não assumida como comportamento futuro.

Factos do código actual (lidos no worktree, sem alterar nada):

- **O limiar de confiança é hoje um número único configurável:** `backend/app/services/scalp_engine.py:14` (`CONFIDENCE_MIN = Decimal("0.7")`); `backend/app/services/scalp_service.py:96-120` (`_confidence_min()` lê `SCALP_CONFIDENCE_MIN`, aceita `none|off|disabled` → `None` = remoção explícita, e cai no default em valores não finitos/fora de [0,1]); aplicado em `decide_cycle` no gate `low_confidence` (`scalp_engine.py:382`), **antes** de `hurdle` (`:391`), `regime` (`:401`) e `toxic_book` (`:412`).
- **O gate de regime do #1025 já fecha o lado calmo do predicado:** `backend/app/services/scalp_window.py:118-123` (`entry_hurdle_bp = 2 × fee_bp + spread`; `passes_entry_hurdle`), `:127` (`REGIME_SLACK = Decimal("1.5")`), `:130-142` (`entry_hurdle_bp_with_slack`, `passes_regime_gate`). Quem não cobre o custo com 50% de folga é recusado por `regime` (`scalp_engine.py:401-410`) — logo um limiar *keyed* ao predicado do gate seria **vazio** no lado calmo (nenhum ciclo calmo chega a entrar).
- **A σ da janela existe e viaja no payload:** `backend/app/services/scalp_window.py:28-36` (`WindowMetrics.vol_bp`), `:72-113` (`window_metrics`); `backend/app/services/scalp_jev_payload.py:65-69` (`build_window`) e `:132` (`state.window.vol_bp`); o registo de entrada já a grava (`scalp_jev_log.py:313-322`).
- **A régua do #1025 existe e é read-only:** `scripts/scalp_jev_eval.py` — `DEFAULT_FEE_BP = 10` (`:66`), `REGIME_SLACK` (`:68`), `MIN_NON_OVERLAPPING_WINDOWS = 30` (`:70`), `MIN_BUCKET_TRADES = 20` (`:71`), `CONFIDENCE_BUCKET_WIDTH = 0.1` (`:72`). `_stats` (`:462-485`) devolve `n`, `n_priced`, contagem de barreiras, `mean_signed_bp`, `expectancy_net_bp` e `abs_realized_p50` — **não** devolve acurácia nem cobertura. `confidence_bucket` (`:511-519`); `build_report` (`:615+`) segmenta por σ (mediana da amostra, `:690-708`) e pelo predicado do gate (`:709-733`) e propõe o **menor bucket positivo** (`:740-757`) — **não** por retorno líquido esperado × cobertura e **não** por regime; declara insuficiência (`:672-687`, `:749-752`, `:856-866`). A régua lê o log com `EntryRe`/`ReturnRe`/`RefusalRe` (`:90-94`) e tolera campos aditivos (`KVRe`, `:94`).
- **A taxa maker real por perna** é lida da conta pelo #1025 (`_fee_terms`) e a régua toma-a por `--fee-bp` (`scripts/scalp_jev_eval.py:912`), com a banda 12–16 bp documentada (`:61-66`).
- **DEV-only:** `ops/systemd/criptofarol-dev-runtime-worker.service` arma `RUN_SCALP_LOOP=1`; o log de diagnóstico é armado pelo mesmo flag (`scalp_jev_log.py:93-108`) e o unit PROD não tem a flag.

UI impact: none
live_route: N/A régua read-only e limiar de confiança no backend/harness do scalp Jev; não há tela de produto
surface: new

Sem rota autenticada, sem landing, sem HTML. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`. Prototype **N/A** — não há superfície visual neste card (backend/harness: régua e decisão), logo não há página viva a clonar nem HTML de protótipo. Impeccable **N/A** — não há UI nem copy visível a polir; os gates de Design e de Aprovação de Design continuam a valer (esta entrega é OpenSpec + relatório, e o pai publica a crítica). Nota de leitura do gate: `surface: new` refere-se à **nova capability de decisão** (régua de retorno líquido + política de limiar por regime), **não** a uma superfície de tela nova.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Vocabulário

Dois "regimes" distintos, que **não** se confundem neste design:

- **Regime de mercado (σ):** calmo (`vol_bp` < fronteira) e ativo (`vol_bp` ≥ fronteira), pela σ da janela de 900 s (`WindowMetrics.vol_bp`) contra **uma** fronteira configurada. É o eixo do **limiar por regime** deste card.
- **Gate de regime (`skip_reason="regime"`):** gate do #1025 (`expected_move_bp ≥ entry_hurdle_bp × 1,5`) que **não** se toca. A confusão entre os dois é o risco de leitura deste card.

Outros termos:

- **População elegível de um regime:** ciclos de janela não sobreposta com resposta do modelo que passam **todos** os gates alimentados pela resposta **excepto** a confiança (`hold`, `jev_late`, `hurdle`, `regime`, `toxic_book`) — isto é, os ciclos que o limiar de confiança deixa realmente operar. Declarada a leitura da previsão em vigor (dependência #1029).
- **Faixa de confiança:** bucket de largura `CONFIDENCE_BUCKET_WIDTH = 0,1` (`scripts/scalp_jev_eval.py:72`), como hoje (`confidence_bucket`, `:511-519`).
- **Acurácia da faixa:** fracção dos ciclos com preço cuja realização assinada a 900 s é **positiva** (direcção certa); reportada, **nunca** critério de escolha do limiar.
- **Retorno líquido de um ciclo:** realização assinada a 900 s (bp) menos o round-trip real `2 × taxa maker por perna`.
- **Cobertura de um limiar `t`:** `nº de ciclos elegíveis com confiança ≥ t / nº de ciclos elegíveis` do regime.
- **Retorno líquido esperado de um limiar `t`:** `ganho esperado(t) × cobertura(t)`, com `ganho esperado(t)` = média do retorno líquido dos ciclos que passam. Equivale a `soma do retorno líquido dos ciclos que passam / nº de ciclos elegíveis`.
- **Confiança separa:** existe um limiar com retorno líquido esperado **positivo**, **estritamente melhor** que aceitar tudo (limiar 0) e amostra suficiente. Se não existir, a confiança **não separa**.
- **Política de confiança de um regime:** `numérico` (valor em [0,1] justificado pelo relatório) | `desligado` (remoção: decisão por previsão × custo × regime) | `fechado` (não opera).
- **Valor em uso:** o valor configurado que está em uso (`CONFIDENCE_MIN = 0.7` / `SCALP_CONFIDENCE_MIN`), preservado e reportado; **nunca** reescrito por um relatório insuficiente.
- **Fronteira de regime:** valor configurado de σ (bp) que separa calmo de ativo — **única**, lida pela régua e pela decisão.

## Goals / Non-Goals

**Goals:**

- A régua passa a mostrar, **por faixa de confiança e por regime**, acurácia, retorno líquido e **tamanho da amostra**.
- A régua passa a mostrar, para um limiar candidato, **quantos ciclos ele deixa passar** (cobertura) e o **retorno líquido esperado** desses ciclos, com a **taxa real por perna**.
- O limiar da decisão é **um por regime** de mercado (σ), cada um justificado pela faixa daquele regime; regime **sem amostra suficiente fica fechado** e não opera.
- O limiar em uso é **explícito e reversível por configuração**; nenhum limiar é adotado sem relatório suficiente.
- Com **amostra insuficiente**, o valor em uso é mantido, a insuficiência é **declarada** (nunca concluída) e o bot **não opera**.
- Se a confiança **não separa** ciclos bons de ruins, o relatório diz isso explicitamente e o limiar é **desligado** (caminho de remoção existente), com a decisão passando a previsão × custo × regime.
- Régua **read-only**, decisão **log-only**, DEV-only; nada de painel/Monitor, `/api/scalp/status`, rota, HTML, base de dados nova, backtest ou PROD.

**Non-Goals:**

- Mudar a pergunta ao modelo (é o #1029) ou implementar já a leitura por faixa.
- Mudar a geometria alvo/stop, o tempo de espera ou o escape de saída (decisões do #1025).
- Reabrir #1006/#1008/#1001, o gate de regime do #1025, a ladder `score → bp` ou o corte de toxicidade.
- Expor no painel/Monitor/`/api/scalp/status`; base de dados nova, dashboard, exportação/Drive, backtest, PROD.
- Segredos em qualquer artefacto, registo ou evidência.

## Decisions

1. **A régua reporta acurácia e retorno líquido por faixa de confiança, com o tamanho da amostra, por regime.** A `_stats` da régua (`scripts/scalp_jev_eval.py:462-485`) ganha a **acurácia** (`nº de ciclos com realização assinada > 0 / nº com preço`) ao lado do `expectancy_net_bp` que já produz, e a tabela de faixas passa a mostrar `n`, `n com preço`, acurácia e retorno líquido. A acurácia é **reportada**, não escolhe nada.
   Alternativa rejeitada — **escolher o limiar pela acurácia da faixa**: é literalmente o que o Entra proíbe («e não por acurácia bruta»); a acurácia ignora o custo e o tamanho do movimento.
   Alternativa rejeitada — **manter só a expectancy por faixa de hoje**: o Critério pede acurácia **e** retorno por faixa, com amostra; e a expectancy por faixa sozinha não mostra cobertura.

2. **O limiar é escolhido por retorno líquido esperado (`ganho esperado × cobertura`), com a taxa real por perna.** Para cada limiar candidato `t` (limite inferior das faixas), a régua calcula, sobre a **população elegível do regime**, `cobertura(t)`, `ganho esperado(t)` e `retorno líquido esperado(t) = ganho esperado(t) × cobertura(t)`; o limiar do regime é o `argmax` do retorno líquido esperado entre os candidatos com amostra suficiente. O relatório mostra a linha do limiar escolhido com **quantos ciclos deixa passar** e o retorno líquido esperado desses ciclos.
   Alternativa rejeitada — **menor faixa com expectancy positiva (regra do #1025, `:740-757`)**: maximiza a expectancy *por ciclo*, ignora a cobertura (a «fração de ciclos que passam» do Entra) e não é por regime; escolhe limiares que deixam passar quase nada.
   Alternativa rejeitada — **escolher pelo total absoluto de bp em vez do retorno esperado por ciclo**: é a mesma maximização de `soma/|população|` (o produto `ganho × cobertura`), mas escrita de forma que esconde a cobertura do operador; o Critério exige as duas grandezas visíveis.
   Alternativa rejeitada — **varrer só os limites de faixa existentes**: é o que o instrumento já tem (bucket edges, `:72`); varrer refinamentos de 0,01 é P3, não contrato.

3. **O limiar é um por regime de mercado (σ), com uma fronteira única partilhada pela régua e pela decisão.** O eixo é a σ da janela (`WindowMetrics.vol_bp`) contra **uma** fronteira configurada (bp): calmo abaixo, ativo a partir dela. A régua usa a mesma fronteira (não a mediana da amostra) para segmentar e mostra a mediana apenas como **referência**; o relatório declara a fronteira usada, e a decisão aplica a política do regime correspondente.
   Alternativa rejeitada — **regime pelo predicado do gate de regime do #1025** (`expected_move_bp ≥ custo × 1,5`): esse gate **já fecha** o lado calmo (`scalp_engine.py:401-410`), logo um limiar calmo seria **vazio** (nenhum ciclo calmo entra) e não haveria «faixa que justifica o limiar daquele regime» no lado calmo — contra o Critério. Além disso o predicado lê `expected_move_bp`, cuja leitura é exactamente o que o #1029 muda.
   Alternativa rejeitada — **fronteira = mediana da amostra (segmentação σ de hoje, `:690-708`)**: é uma estatística que muda com a amostra e **não é reproduzível no momento da decisão**; o limiar calibrado seria aplicado a uma população diferente da que o relatório mediu.
   Alternativa rejeitada — **não ter fronteira (aplicar o limiar médio às duas metades da amostra)**: não é «um por regime»; o Critério pede dois, cada um justificado pela sua faixa.

4. **Política de confiança por regime: `numérico` | `desligado` | `fechado`.** O motor puro recebe a política do regime e o regime de mercado por parâmetro; `numérico` mantém o gate `low_confidence` com o valor daquele regime; `desligado` é o caminho de remoção existente (`scalp_service.py:96-120`, `none|off|disabled` → `None`, o motor não produz `low_confidence`) e a decisão passa a previsão × custo × regime; `fechado` **não opera** e fecha o ciclo com token próprio, sem comparação de limiar.
   Alternativa rejeitada — **manter um limiar único global**: é o estado que o card corrige; não é «um por regime».
   Alternativa rejeitada — **valores por regime inferidos automaticamente do relatório sem configuração**: o Entra exige o limiar **explícito e reversível por configuração**; um valor derivado e aplicado sozinho não é reversível nem auditável.
   Alternativa rejeitada — **reutilizar o token `regime` para o regime fechado**: confundiria «não cobre o custo com folga» (gate do #1025) com «regime sem amostra»; o fecho tem de ser **declarado** com token próprio.

5. **Fecho por amostra insuficiente é estado explícito, e o valor em uso é preservado.** Um regime fica `fechado` quando a sua população elegível com preço não chega ao mínimo (`MIN_NON_OVERLAPPING_WINDOWS = 30`) ou quando nenhuma faixa contribuinte chega a `MIN_BUCKET_TRADES = 20`. Nesse caso o bot **não opera** nesse regime, o relatório **declara** a insuficiência e o **valor em uso é preservado e reportado** (não é reescrito, não é inventado um número). Só um relatório **suficiente** abre o regime com um valor justificado.
   Alternativa rejeitada — **depender de o valor em uso (0,7) ser inalcançável para o bot não operar**: é o acidente que o card existe para corrigir («um valor que nenhuma resposta alcança»); se o valor em uso fosse alcançável (ou fosse trocado por configuração sem relatório), o bot operaria com um número sem régua — o fecho tem de ser estado, não coincidência.
   Alternativa rejeitada — **fechar o regime com um valor numérico impossível em vez de um estado**: pareceria calibrado e voltaria a esconder a insuficiência (a insignificância da «insuficiência declarada»).

6. **Separação da confiança é decidida por retorno líquido, e a não-separação desliga o limiar.** A confiança **separa** no regime quando existe um limiar com retorno líquido esperado **positivo** e **estritamente melhor** que aceitar tudo (limiar 0) sobre a população elegível com amostra suficiente. Se não existir, o relatório **declara** que a confiança não separa ciclos bons de ruins e a política do regime fica `desligado` — a decisão passa a previsão × custo × regime, o caminho de remoção já existente.
   Alternativa rejeitada — **testar separação por monotonicidade/correlação da acurácia com a confiança**: é diagnóstico de acurácia, não de dinheiro; a decisão do dono é por resultado líquido.
   Alternativa rejeitada — **manter o limiar «desligado por defeito» e abrir só com o relatório**: isso *é* o `fechado` deste design (política sem relatório); `desligado` fica reservado ao veredicto explícito «a confiança não separa».
   Alternativa rejeitada — **quarto estado «fecha por não dar lucro»**: o Entra fecha a decisão «não separa → desliga»; acrescentar um estado novo reabriria essa decisão, pelo que a não-separação (incluindo o caso degenerado em que nenhuma faixa é positiva) fica `desligado`, como decidido.

7. **A população elegível usa os veredictos registados, e a homogeneidade da amostra é declarada.** O limiar só faz sentido sobre os ciclos que passariam os **outros** gates; a régua restringe a população aos ciclos cujos veredictos registados pelo #1028 mostram `hold`, `jev_late`, `hurdle`, `regime` e `toxic_book` a passar, e reconstrói os predicados com as regras puras do #1025 quando precisa de detalhe. O relatório **declara** a versão do modelo e a origem da confiança da amostra (#1028, `scalp_jev_log.py:325-378`) e o número de janelas excluídas por mistura/origem divergente — um limiar calibrado sobre origens (`reply_field` vs `choice_probability`) ou versões misturadas não é um limiar.
   Alternativa rejeitada — **calibrar sobre todas as respostas sem olhar aos outros gates**: «quantos ciclos o limiar deixa passar» passaria a contar ciclos que continuariam a ser recusados por custo/regime, inflacionando a cobertura.
   Alternativa rejeitada — **medir a origem/versão só de forma agregada**: sem separar por origem/versão não se sabe se a faixa mede a confiança ou o artefacto de duas fontes diferentes.
   **Fronteira declarada (dependência #1029):** a população elegível depende de `hurdle`/`regime`, que consomem `expected_move_bp`; enquanto o #1029 não existir, o relatório mede a leitura em vigor e **declara** isso. Depois do #1029, o relatório tem de ser **recalculado** — isto é uma dependência declarada, não comportamento assumido (o design não implementa a leitura por faixa).

8. **O custo da régua é a taxa real por perna da conta, registada.** O relatório continua a receber a taxa por perna por argumento (`--fee-bp`, `scripts/scalp_jev_eval.py:912`), mas o valor passado **tem** de ser a taxa maker real por perna que a decisão usa (`_fee_terms`), e o relatório **regista a taxa usada e a sua origem** (conta vs fallback conservador `10 bp`). Um relatório que use o default conservador quando a taxa real é conhecida é defeito declarado, não um número neutro.
   Alternativa rejeitada — **a régua ir à conta do utilizador buscar a fee**: transformaria um instrumento read-only/offline num cliente autenticado (novo modo de falha, credenciais no caminho da evidência).
   Alternativa rejeitada — **usar sempre o default `10 bp/perna`**: é o lado conservador do #1025, mas o Entra deste card pede explicitamente a taxa real por perna dentro da conta; o default só serve o fallback declarado.

9. **Configuração explícita e reversível, com falha fechada.** Entram configurações (nomes P3): a **fronteira** de regime (σ em bp) e a **política por regime** (`calm` / `active`), cada uma aceitando um valor numérico em [0,1], `off|none|disabled` (desligado) ou `closed` (fechado). Valor ausente, não finito ou fora de [0,1] **não** abre nada: cai em `fechado` (o default seguro é não operar). Enquanto o relatório for insuficiente, as políticas ficam `fechado` e o valor em uso é preservado; a fronteira, sem valor, deixa ambos os regimes fechados. Reverter = repor o valor em configuração.
   Alternativa rejeitada — **default numérico aberto**: abriria um regime com um número sem régua (o problema do card).
   Alternativa rejeitada — **aceitar `nan`/`inf`/valores fora de [0,1]**: comparam `False` contra tudo e desligariam o gate em silêncio — o #1025 já corrigiu esse caso (`scalp_service.py:111-119`) e ele mantém-se como falha fechada.

## Risks / Trade-offs

- [Risco] A amostra DEV nunca chega a 30 janelas elegíveis por regime e o bot fica fechado (comportamento actual, agora declarado). → Mitigação: é resultado válido e decidido no card («amostra insuficiente é declarada, nunca concluída»); o relatório mostra a contagem e a causa; a coleta continua até haver relatório suficiente; a recalibração depois do #1029 é declarada.
- [Risco] Calibrar sobre uma amostra com origens de confiança ou versões de modelo misturadas (confundir faixa com artefacto). → Mitigação: decisão 7 — o relatório declara origem/versão e as janelas excluídas por mistura; sem homogeneidade não propõe limiar.
- [Risco] A dependência #1029 mudar a população elegível (o `hurdle`/`regime` passam a ler a faixa) e invalidar em silêncio um relatório antigo. → Mitigação: decisão 7 — a leitura/modelo em vigor são declarados no relatório e a recalibração pós-#1029 é requisito declarado; nenhum valor é adotado de um relatório de leitura diferente.
- [Risco] A fronteira de regime mal configurada (ou ausente) põe o bot a aplicar o limiar da população errada ou a não operar. → Mitigação: decisões 3 e 9 — fronteira **única** partilhada pela régua e pela decisão, declarada no relatório; ausente → ambos os regimes fechados (falha fechada).
- [Risco] Maximizar o retorno líquido esperado escolher um limiar com cobertura minúscula (poucos ciclos, sorte). → Mitigação: mínimo de amostra da população elegível (30) e da faixa contribuinte (20); o relatório mostra a cobertura ao lado do ganho (decisão 2).
- [Risco] O `closed` ser lido como «mais um limiar» e o operador não ver que o bot não opera. → Mitigação: token de recusa **próprio** no registo (nunca `regime` nem `low_confidence`), com o regime de mercado e o veredicto da confiança no mesmo registo (decisão 4).
- [Risco] Um novo token de recusa quebrar a régua read-only do #1025. → Mitigação: `RefusalRe` (`scripts/scalp_jev_eval.py:92`) lê `skip_reason=(\S+)` e o `KVRe` tolera campos aditivos; o token é um **valor** novo, não um prefixo novo — a régua continua a ler o ficheiro sem alterações.
- [Risco] A régua deixar de ser read-only ao ganhar entradas novas. → Mitigação: decisão 8 — a régua continua a receber valores por argumento; o teste de read-only existente (`test_scalp_jev_eval_ruler.py::test_the_instrument_is_read_only`) mantém-se e cobre o ficheiro.
- [Trade-off] Três estados de política por regime (numérico/desligado/fechado) num só card — aceite: são exactamente os três veredictos que o Entra fixa (valor justificado, limiar desligado, regime fechado).

## Apply contract

**Contrato visível (não P3):**

- **Régua — acurácia e retorno por faixa com amostra:** por faixa de confiança (largura 0,1) e por regime (calmo/ativo), o relatório mostra `n`, `n com preço`, **acurácia** (fracção de ciclos com realização assinada positiva) e **retorno líquido** (bp), com o tamanho da amostra de cada faixa; faixa sem amostra suficiente é declarada.
- **Régua — limiar por ciclo que passa:** para um limiar candidato, o relatório mostra **quantos ciclos elegíveis ele deixa passar** (cobertura) e o **retorno líquido esperado** desses ciclos (`ganho esperado × cobertura`), sobre a **população elegível** (ciclos que passam `hold`, `jev_late`, `hurdle`, `regime` e `toxic_book`); o limiar do regime é o `argmax` do retorno líquido esperado com amostra suficiente (decisão 2).
- **Régua — um limiar por regime e fecho declarado:** o relatório mostra, para **cada** regime de mercado (calmo e ativo), a faixa que justifica o limiar daquele regime e o tamanho da amostra; regime com população elegível com preço < 30 ou sem faixa contribuinte com ≥ 20 aparece como **fechado** (não opera).
- **Régua — separação declarada:** o relatório declara, por regime, se a confiança **separa** ciclos bons de ruins pelo critério da decisão 6; quando não separa, diz isso explicitamente e propõe o limiar **desligado**.
- **Régua — insuficiência declarada:** sem relatório suficiente nenhum valor é proposto; a insuficiência é declarada (nunca concluída) e o valor em uso é preservado.
- **Régua — taxa real por perna:** o custo usado é `2 × taxa maker por perna` da conta em uso, registado no relatório com a origem (conta vs fallback conservador `10 bp`); o default conservador só é aceitável como fallback declarado.
- **Régua — homogeneidade:** o relatório declara a versão do modelo e a origem da confiança da amostra e as janelas excluídas por mistura/origem divergente; sem homogeneidade, não propõe limiar.
- **Régua — read-only:** sem escrita em produto, estado do scalp ou base de dados; sem o loop do scalp.
- **Decisão — política por regime:** a confiança passa a ter uma política por regime de mercado (σ): valor numérico justificado pelo relatório | **desligado** (remoção; decisão por previsão × custo × regime) | **fechado** (não opera).
- **Decisão — fronteira única de regime:** a σ da janela contra **uma** fronteira configurada (bp) decide o regime (calmo abaixo, ativo a partir dela); a mesma fronteira é usada pela régua; ausente → ambos os regimes fechados (falha fechada).
- **Decisão — regime fechado não opera:** um regime `fechado` fecha o ciclo com **token de recusa próprio** (nunca `regime` nem `low_confidence`), registado no ficheiro de diagnóstico do #1015 com o regime de mercado e o veredicto da confiança; o valor em uso é preservado e reportado.
- **Decisão — configuração explícita e reversível:** políticas por regime aceitam valor em [0,1], `off|none|disabled` ou `closed`; ausente/não finito/fora de [0,1] cai em `fechado`; reverter = repor a configuração.
- **Log-only e DEV-only:** o registo vai para o ficheiro único do #1015 (tecto e truncagem inalterados); nada de painel/Monitor/`/api/scalp/status`, rota, HTML, base de dados nova, backtest; PROD é T16.
- **Não-regressão dos outros gates:** o gate de regime do #1025, o hurdle, a toxicidade, a geometria alvo/stop/hold e o escape agressivo **não mudam**; a leitura da confiança é que passa a ser por regime.

**P3 — detalhe de Apply (aceito aqui, resolvido no Apply — não reabrir como P0/P1):**

- Nomes exactos das configurações (fronteira de regime e política por regime) e se o `SCALP_CONFIDENCE_MIN` único é preservado como fonte do «valor em uso»/retro-compatibilidade.
- Nome/largura exacta do token de recusa do regime fechado e das chaves aditivas do registo (regime de mercado, veredicto da confiança).
- Conjunto exacto de limiares candidatos (limites de faixa vs refinamento de 0,01) e o mínimo de amostra para a faixa contribuinte.
- Forma exacta da tabela da curva do limiar (linhas por candidato, ordem, arredondamento) e como o relatório escreve o regime fechado.
- Como o serviço calcula o regime de mercado no momento da decisão (relendo `build_window(memory)` vs lendo o `vol_bp` do payload enviado) — desde que use a **mesma** σ do payload e a fronteira partilhada.
- Como os testes injectam a população elegível (veredictos registados vs predicados reconstruídos), a fronteira e as políticas, e como provam o fail-closed.
- Se a régua mantém a segmentação por mediana σ e por predicado do gate como **referência** ao lado da segmentação pela fronteira configurada.

## Open Questions / pontos deixados ao crítico

Nenhuma pergunta ao operador — a fronteira veio grelhada e as decisões 1–9 fecham o *como*. O que fica aberto para a crítica, sem reabrir decisões do card:

1. **Valores concretos** (limiar por regime, fronteira de σ) — deliberadamente **não** fixados aqui: dependem do relatório da régua (decisões 2, 3 e 5). O Apply bloqueia no relatório; se ele declarar amostra insuficiente, as políticas ficam `fechado`, o valor em uso é preservado e o motivo fica na evidência.
2. **Eixo do regime** — escolhido como σ da janela (decisão 3) por ser ortogonal ao gate de regime do #1025 e independente do que o #1029 muda; a alternativa pelo predicado do gate fica rejeitada com motivo escrito.
3. **Dependência #1029** — a população elegível reflecte a leitura da previsão em vigor; o relatório declara-a e a recalibração depois do #1029 é requisito declarado, não comportamento assumido (decisão 7).

## Design Critique

Sem-tela. Teto 1+1+1 na 1.ª entrada: **1 autor + 1 crítico, sem rework** — nenhum P0/P1 de produto/escopo/contrato visível. Relatórios: `.impeccable/critique/1030-card-1030-jev-limiar-retorno-liquido.md` (autor) · `.impeccable/critique/1030-card-1030-jev-limiar-retorno-liquido-design-critic.md` (crítico). Snapshot T7 = o relatório do crítico.

**Veredito do crítico: PASS** — rúbrica 1–7: PASS · PASS · PASS · PASS · PASS · PASS · PASS (item 7 = sem tela: Prototype **N/A** / Impeccable **N/A** declarados com justificativa não-vazia; sem protótipo, sem acessibilidade visual, sem clone de página viva). Tokens do gate do autor em linha própria parseável e verificados: `UI impact: none` · `live_route: N/A régua read-only e limiar de confiança no backend/harness do scalp Jev; não há tela de produto` · `surface: new`; sem rota de catálogo emprestada. `proposal.md` copia `## Problema`, `## História`, `## Entra` (com critérios), `## Não entra` e `## Evidência` **verbatim** do issue grelhado (diff por secção = IDENTICAL). Bloco D4 colado verbatim (`D4_IDENTICAL`). `worktree` sem `backend/**` nem `frontend/**` tocado; `design.md` sem secção de crítica antes desta. `openspec validate card-1030-jev-limiar-retorno-liquido --strict` → `Change 'card-1030-jev-limiar-retorno-liquido' is valid`.

**P0:** nenhum
**P1:** nenhum
**P2:** nenhum

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):** 1 do crítico, somado aos já aceitos no Apply contract
- Âncora de linha do gate `low_confidence` off-by-one: o `## Context` cita `scalp_engine.py:382` (linha do `return CycleIntent`); a condição `if confidence_min is not None and jev.confidence < confidence_min:` está em `:381`. Detalhe de Apply, sem efeito no contrato visível. (crítico)
- (Já no Apply contract) nomes/valores exactos das configurações (fronteira de regime e política por regime) e retro-compatibilidade do `SCALP_CONFIDENCE_MIN` único; nome/largura do token de recusa do regime `fechado` e chaves aditivas do registo; conjunto de limiares candidatos e mínimo de amostra da faixa contribuinte; forma exacta da tabela da curva do limiar; como o serviço calcula o regime de mercado no momento da decisão (mesma σ do payload + fronteira partilhada); como os testes injectam a população elegível e provam o fail-closed; se a régua mantém a segmentação por mediana σ e pelo predicado do gate como referência.

**Disposition:** nenhum P0/P1/P2 — sem rework; o crítico correu **uma** vez (teto sem-tela). P3 → Apply. Escopo do `## Não entra` intacto: sem mudar a pergunta feita ao modelo (#1029), sem geometria alvo/stop/tempo/escape, sem reabrir #1006/#1008/#1001, sem painel/Monitor/`/api/scalp/status`, sem base de dados/Drive/backtest, PROD fora (T16). Contrato visível do dono preservado com os valores exactos: **um limiar por regime** (calmo/ativo) com **regime sem amostra suficiente fechado e não operando**; **amostra insuficiente mantém o valor em uso e o bot não opera**, insuficiência **declarada**; **confiança que não separa → limiar desligado**, decisão por **previsão × custo × regime**; limiar **explícito e reversível por configuração**. Fronteira com o #1029 **declarada** (decisão 7, risco e open question) — nenhum artefacto implementa a leitura por faixa. `tasks.md` com todas as caixas `- [ ]`.

Spawns: 2
proxy modelo: design-autor → deepseek-flash (deepseek-flash)
proxy modelo: design-critic → deepseek-flash (deepseek-flash)
