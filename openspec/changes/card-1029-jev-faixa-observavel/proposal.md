Título: Scalp Jev: previsão do modelo como faixa observável, não número interpolado

Card criado a partir da homologação do #1025 (23/09). **Depende de #1028** (veredicto dos gates no log).

Este card **assenta** no registo do #1028 (Done técnico): não reabre o veredicto dos gates, a origem da confiança, a versão pinada do modelo, a faixa de toxicidade nem o tempo limite. É **SEM-TELA** (backend/registo do scalp Jev; nada de UI, nada de painel); a homologação do #1025 (23/09) e o registo do #1028 são a evidência de partida.

> **Nota do que este card faz:** a previsão do modelo deixa de ser lida como um número em pontos-base interpolado entre níveis e passa a ser lida como **posição numa escala ordenada** contra o **custo real do ciclo** — três faixas (**abaixo do custo · cobre o custo · cobre com folga**) cujas fronteiras acompanham a taxa real do ciclo. A interpolação linear sai do caminho de decisão (o artefacto 15,0 / 15,35 / 14,30 / 9,60 deixa de ser produzido); o registo passa a mostrar **faixa + posição na escala** e nunca um bp interpolado; e um **A/B** mede se uma janela de estado maior aumenta a confiança (mínimo de 30 janelas de 900 s não sobrepostas; abaixo disso escreve **amostra insuficiente**).

## Problema

Quem opera o scalp Jev vê a previsão de movimento tratada como um número em pontos-base, mas o modelo devolve uma posição numa escala ordenada sem significado métrico — então o valor comparado com o custo da operação não mede o que parece medir.

## História

Como operador do scalp Jev, quero que a previsão do modelo seja lida como o que ela é — uma posição ordenada ou uma faixa — e comparada com o custo por faixa, para a decisão deixar de depender de uma conversão que o próprio fornecedor diz para não fazer.

## Entra

- **Depende de:** #1028 — o A/B e a leitura por faixa exigem o registro novo.
- A pergunta sobre o tamanho do movimento passa a ser descrita por **faixas observáveis ancoradas no custo real** da operação, e não por números nus. Hoje os dez níveis são apenas "0 bp", "5 bp", "10 bp"… — nada no estado enviado permite julgar a diferença entre dois níveis vizinhos.
- A decisão de entrada passa a comparar **faixa com custo** (posição na escala contra a faixa que cobre o custo), e deixa de converter a posição num valor em pontos-base para comparar.
- Um **teste A/B** mede se uma janela de estado maior aumenta a confiança, para verificar se a compressão do estado atual (feita para baratear a chamada) suprimiu o sinal.

Critérios observáveis:

- Dada uma resposta cuja posição na escala fica abaixo da faixa do custo, o ciclo é recusado por custo — e não por confiança.
- Dada uma resposta na faixa mais alta, o ciclo passa a regra de custo.
- O registro mostra sempre a faixa escolhida e a posição na escala, nunca um valor em pontos-base derivado por interpolação.
- As dez opções atuais ficam quantizadas nos limites dos níveis (o famoso 15,0 / 15,35 / 14,30); depois do card, o registro não produz mais esse artefato de interpolação.
- O A/B registra a confiança média com a janela atual e com a janela maior, com a mesma versão de modelo fixa, e declara o tamanho da amostra.

Decisões fechadas (grelha 23/09):

- As faixas são **relativas ao custo de cada ciclo** — **abaixo do custo**, **cobre o custo** e **cobre com folga** — e as fronteiras acompanham a taxa real do ciclo (não há faixas fixas na escala).
- O modelo continua a responder **uma posição na escala** (as dez opções continuam a existir); o que muda é o rótulo que ele vê (faixas em vez de números nus) e a leitura contra o custo.
- Posição abaixo do custo é recusa **por custo**, com um motivo só no registro — igual a qualquer outra posição abaixo do custo; a faixa mais baixa não ganha motivo próprio.
- Posição entre dois níveis credita o **nível já alcançado** (arredonda para baixo): só passa quem atinge o nível inteiro que cobre o custo.
- O A/B conclui com **mínimo de 30 janelas de 900 s não sobrepostas**; abaixo disso não conclui e o registro escreve **amostra insuficiente**.

## Não entra

- Mudar o valor do limiar de confiança (é o card do limiar).
- Mudar a geometria de alvo/stop, o tempo de espera ou o escape de saída.
- Mudar o corte de toxicidade (é o card de observabilidade).
- Expor no painel/Monitor.
- Produção.

## Evidência (homologação do #1025, 23/09)

- A conversão atual interpola linearmente entre níveis de uma escala ordinal: os valores registrados saem quantizados nos limites dos níveis (15,0 · 15,35 · 14,30 · 9,60), o que é artefato da interpolação e não medição.
- A documentação pública do fornecedor é explícita: não usar a posição na escala para calcular a magnitude exata de um número entre dois níveis; a escala é ordenada, não métrica. A versão atual do modelo tem calibração fraca entre níveis.
- A mesma documentação aponta que confiança baixa numa escala costuma significar níveis ambíguos ou estado insuficiente para julgar — o que combina com a confiança de 0,07 a 0,19 observada.
- O #1025 listou "mudar a escada de níveis" como **não entra**, condicionado a evidência de que ela estava capada. Essa evidência agora existe e vem do fornecedor, não da amostra.



## Como (resumo técnico da solução)

- **Faixas relativas ao custo do ciclo, sem limiar novo.** A resposta do modelo é lida como **posição na escala**; o nível creditado é o **nível já alcançado** (arredonda para baixo) e o seu bp exato é comparado com o custo **real** do ciclo reusando os predicados que já existem (`passes_entry_hurdle` = `2 × fee_bp + spread_bp`, estrito `>`; `passes_regime_gate` = hurdle × 1,5, `>=`). O resultado é uma das três faixas — `below_cost`, `covers_cost`, `covers_with_slack` — e a decisão fecha pelo token de custo que já existe (`hurdle` para abaixo do custo, `regime` para cobre-sem-folga), com **um motivo só**.
- **A interpolação linear sai do caminho de decisão.** `_bp_from_score` (interpolação entre níveis) deixa de alimentar a decisão; passa a existir um **nível creditado** (índice inteiro → bp exato da escada). `expected_move_bp` passa a carregar esse bp exato do nível já alcançado — muda de significado (declarado como contrato visível) e nunca é interpolado.
- **O registo mostra faixa + posição, nunca bp interpolado.** Os registos (retorno da chamada e ciclo) ganham, de forma aditiva, a **faixa escolhida** e a **posição na escala** (o `score` cru já é registado hoje); o bp, quando aparece, é o bp exato de um nível da escada. O artefacto quantizado 15,0 / 15,35 / 14,30 / 9,60 deixa de ser produzido.
- **O rótulo que o modelo vê são as faixas daquele ciclo.** As dez opções continuam a existir e a resposta continua a ser uma posição; o que muda é o rótulo de cada opção, que passa a ser a sua faixa face ao custo real do ciclo, em vez de um número nu.
- **A/B da janela de estado.** Uma leitura **read-only** sobre os registos de diagnóstico mede a **confiança média** com a janela atual e com a janela maior, com a **mesma versão fixa de modelo** (pin do #1028), declara o **tamanho da amostra** e só conclui com **≥30 janelas de 900 s não sobrepostas**; abaixo disso escreve **amostra insuficiente**.
- **Não-regressão declarada.** Os gates que não são de custo (confiança, `hold`, atraso, toxicidade) e os gates de dimensionamento ficam iguais; a decisão de custo muda **por desenho** (nível creditado em vez de valor interpolado) e isso é contrato visível, não regressão.
- **Só DEV nesta entrega**; o destino é o ficheiro de diagnóstico do #1015 (ficheiro único, tecto e truncagem de cauda inalterados). Sem `frontend/**`, sem rota/HTML, sem painel/Monitor, sem base de dados, sem dashboard/exportação/Drive/backtest, sem PROD.

## Capabilities

### New Capabilities

- `scalp-jev-cost-band`: a decisão de entrada compara a **faixa do nível já alcançado** com o **custo real do ciclo** (abaixo do custo · cobre o custo · cobre com folga), reusando as comparações de custo existentes e sem limiar novo; abaixo do custo é recusa por custo com **um motivo só**; a faixa mais alta passa a regra de custo; o nível entre dois pontos credita o **nível já alcançado** (arredonda para baixo); a pergunta mantém as **dez opções** e a resposta como **posição**, com o rótulo em faixas em vez de números nus.
- `scalp-jev-scale-record`: o registo (retorno da chamada e ciclo) mostra sempre a **faixa escolhida** e a **posição na escala**, e **nunca** um valor em pontos-base derivado por interpolação; a interpolação linear sai do caminho de decisão e o artefacto quantizado (15,0 / 15,35 / 14,30) deixa de ser produzido; só log, sem superfície de produto.
- `scalp-jev-window-ab`: o **A/B** registra a confiança média com a **janela atual** e com a **janela maior**, com a **mesma versão fixa de modelo** e o **tamanho da amostra** declarado; conclui apenas com **≥30 janelas de 900 s não sobrepostas**; abaixo disso **amostra insuficiente**; read-only, sem mudar a decisão.

### Modified Capabilities

- (nenhuma) — a change é **aditiva** sobre o registo do #1028 e não altera nenhum requisito vigente além do que as decisões do dono exigem. O prefixo `scalp cycle refused` / a chave `skip_reason` do #1015 e os campos do #1028 são preservados (a régua read-only do #1025 `scripts/scalp_jev_eval.py` continua a ler o ficheiro sem alterações); o painel, o payload de decisão e a cadência não mudam.

## Impact

- `backend/app/services/scalp_jev.py`: `_bp_from_score` (interpolação linear, l.65-81) sai do caminho de decisão; `_expected_move_bp` (l.284-299) passa a devolver o bp do **nível já alcançado**; `_expected_move_bp_criteria` (l.55-62) passa a rotular as dez opções pelas **faixas do ciclo** (precisa do custo do ciclo); `_map_systemone` (l.302-321) leva a posição/nível no `JevSignal`; `log_call_return` (l.452-470) leva a faixa e a posição.
- `backend/app/services/scalp_window.py`: os predicados `passes_entry_hurdle` (l.122-123) e `passes_regime_gate` (l.135-142) são **reusados** (não mudam); é a partir deles que as três faixas são materializadas.
- `backend/app/services/scalp_engine.py`: `reply_gate_verdicts` (l.218-242) e os gates de custo (l.390-410) passam a decidir pela **faixa do nível creditado**; `GATE_ORDER` (l.47-54) e os tokens `hurdle`/`regime` mantêm-se; o `JevSignal` (l.161-174) leva a posição/nível.
- `backend/app/services/scalp_jev_log.py`: campos **aditivos** de faixa/posição nos registos (`log_call_return` l.327-378, `_cycle_suffix` l.390-421, `log_cycle_refusal`/`log_cycle_sent` l.424-482) sem mudar o ficheiro, o tecto nem a truncagem; o braço do A/B entra de forma aditiva.
- `backend/app/services/scalp_service.py`: `_gate_verdict_fields`/`_write_cycle_record` (l.806-841) levam a faixa e a posição ao registo do ciclo.
- Análise A/B **read-only** sobre o ficheiro de diagnóstico (sem tocar na decisão nem no painel).
- Sem `frontend/**`, sem rota nova, sem painel/Monitor, sem `/api/scalp/status`, sem base de dados, sem exportação/Drive, sem backtest, sem PROD.
