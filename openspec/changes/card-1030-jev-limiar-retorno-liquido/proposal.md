Título: Scalp Jev: limiar de entrada escolhido por retorno líquido esperado, um por regime

Card criado a partir da homologação do #1025 (23/09). **Depende de #1028 e #1029.**

## Problema

A regra de confiança está num valor que nenhuma resposta alcança e que nunca foi medido contra resultado real, então a decisão não tem régua e o bot não opera.

## História

Como operador do scalp Jev, quero que o limiar de entrada seja escolhido por retorno líquido esperado e cobertura medida, para a decisão operar só quando o ganho esperado cobre o custo — e não por um número que ninguém consegue alcançar.

## Entra

- **Depende de:** #1028 (observabilidade dos gates) e #1029 (pergunta do modelo).
- O limiar de entrada passa a ser escolhido por **retorno líquido esperado** (ganho esperado × fração de ciclos que passam), com a taxa real por perna dentro da conta — e não por acurácia bruta.
- O limiar passa a ser **um por regime** (calmo e ativo), cada um justificado pela sua faixa do relatório; regime **sem amostra suficiente fica fechado** e não opera.
- A régua de avaliação passa a produzir **acurácia e retorno líquido por faixa de confiança** contra o resultado realizado, para responder se a confiança separa ciclos bons de ruins nesta amostra.
- O limiar em uso passa a ser **explícito e reversível por configuração**, com o valor justificado pelo relatório da régua.
- Enquanto a régua declarar **amostra insuficiente**, mantém-se o valor em uso e o bot **continua sem operar**; a coleta segue até haver relatório com amostra suficiente. Amostra insuficiente é **declarada**, nunca concluída.
- Se a medição mostrar que a confiança **não separa** ciclos bons de ruins, o relatório declara isso e o **limiar é desligado**, com a decisão passando a previsão × custo × regime, sem limiar de confiança — o caminho de remoção já existe e fica registrado.

Critérios observáveis:

- O relatório mostra, por faixa de confiança, acurácia e retorno líquido, com o tamanho da amostra de cada faixa.
- O relatório mostra, para **cada regime** (calmo e ativo), a faixa que justifica o limiar daquele regime e o tamanho da amostra; regime sem amostra suficiente aparece como **fechado**.
- Dado um limiar escolhido, o relatório mostra quantos ciclos ele deixa passar e qual o retorno líquido esperado desses ciclos.
- Nenhum limiar é adotado sem o relatório; com **amostra insuficiente** o valor em uso é **mantido** e o bot **não opera**, com a insuficiência **declarada**, não concluída.
- Se a confiança não separar, o relatório diz isso explicitamente e o limiar é **desligado**, com a decisão passando a previsão × custo × regime.

## Não entra

- Mudar a pergunta feita ao modelo (é o #1029).
- Mudar a geometria de alvo/stop, o tempo de espera ou o escape de saída.
- Reabrir #1006 (lookback), #1008 (stream) ou #1001 (interruptor/T/clip/kill).
- Expor no painel/Monitor.
- Produção.

## Evidência (homologação do #1025, 23/09)

- O limiar 0,7 não é alcançável: **0 de 766** respostas passam; a confiança máxima já observada foi **0,39**.
- A régua do Card A do #1025 declarou **amostra insuficiente** — e por isso o limiar ficou no valor de produto, sem calibração. Com 0 de 766 passando, a causa provável é o desenho do instrumento (card da pergunta), não falta de dados.
- A documentação pública do fornecedor recomenda escolher o limiar por **risco e retorno medidos** na própria carga, com bandas por ação, e afirma que um alvo inatingível costuma indicar que o conserto é a pergunta — não o número.
- Referência de padrão equivalente: projeto aberto de execução com confiança que otimiza o limiar por **lucro e valor esperado líquido** com os custos dentro da busca (não por acurácia).
- O limiar desligado **não** é o caminho sugerido: a própria régua indicou que a confiança não separa trade bom de ruim nesta amostra, então abrir o gate com um sinal não informativo troca "não opera" por "opera mal".


> **Nota (grelha de refinamento, 23/09):** o registo acima é histórico da homologação do #1025 e **não** é decisão deste card. A decisão desta grelha prevalece: com amostra insuficiente, o valor em uso é mantido e o bot não opera; se a confiança **não separar** ciclos bons de ruins, o limiar é **desligado** e a decisão passa a previsão × custo × regime (ver Entra).

## Why

O limiar de confiança do scalp Jev hoje é um número único (`CONFIDENCE_MIN = 0.7`) que nenhuma resposta alcança (0 de 766; máximo observado 0,39) e que nunca foi medido contra o resultado realizado. Sem uma régua que diga, por faixa de confiança e por regime, quanto a decisão ganha ou perde depois do custo real, o operador não tem como escolher um limiar — e o bot não opera. Este card fecha essa lacuna: passa a existir um instrumento que mede retorno líquido e cobertura, um limiar por regime justificado por esse relatório, e a declaração explícita quando a amostra não chega ou quando a confiança não separa.

## What Changes

- A régua read-only do #1025 (`scripts/scalp_jev_eval.py`) passa a reportar, **por faixa de confiança e por regime**, acurácia e retorno líquido com o tamanho da amostra de cada faixa; a mostrar, para um limiar candidato, **quantos ciclos ele deixa passar** e o **retorno líquido esperado** desses ciclos (ganho esperado × cobertura); e a declarar, por regime, a faixa que justifica o limiar, a insuficiência (regime **fechado**) e se a confiança **separa** ciclos bons de ruins.
- O custo usado passa a ser o da **taxa real por perna** da conta (o mesmo valor que a decisão usa), registado no relatório.
- O limiar da decisão passa a ser **um por regime** (calmo/ativo), explícito e reversível por configuração, com uma política por regime: valor numérico justificado pelo relatório, **desligado** (remoção, quando a confiança não separa) ou **fechado** (regime sem amostra suficiente — não opera).
- Com amostra insuficiente o valor em uso é mantido e o bot não opera, com a insuficiência declarada; nenhum limiar é adotado sem relatório suficiente.
- Sem tocar na pergunta ao modelo (#1029), na geometria alvo/stop/tempo/escape, no painel/Monitor, nem em PROD.

## Capabilities

### New Capabilities

- `scalp-jev-net-return-ruler`: a régua read-only passa a medir acurácia e retorno líquido **por faixa de confiança e por regime**, com tamanho de amostra; a avaliar um limiar candidato por **ciclos que passam e retorno líquido esperado (ganho esperado × cobertura)**; a declarar por regime a faixa que justifica o limiar, o regime **fechado** por amostra insuficiente e se a confiança **separa** ciclos bons de ruins; a usar a **taxa real por perna** da conta; e a declarar a homogeneidade da amostra (versão do modelo e origem da confiança).
- `scalp-confidence-threshold-per-regime`: a decisão aplica uma **política de confiança por regime** (valor numérico | desligado | fechado), sobre o **regime de mercado pela σ da janela** com uma fronteira única partilhada com a régua; um regime **fechado** não opera (recusa declarada) e mantém o valor em uso; **desligado** é o caminho de remoção existente (decisão por previsão × custo × regime); a configuração é **explícita e reversível**, e nenhum valor é adotado sem relatório suficiente.

### Modified Capabilities

- (nenhuma) — o card **estende** a régua e o gate de confiança do #1025 de forma aditiva (a régua continua read-only; o prefixo `scalp cycle refused`/`skip_reason` do #1015 e a leitura por `KVRe` mantêm-se), e não altera requisitos vigentes noutras capabilities. As capabilities do #1025 ainda estão no change `card-1025-jev-destravar-entradas` (não arquivadas em `openspec/specs/`), pelo que não são alvo de delta MODIFIED aqui.

## Impact

- `scripts/scalp_jev_eval.py`: acurácia e retorno líquido por faixa e por regime, com amostra; curva do limiar (cobertura × retorno líquido esperado); limiar por regime com fecho/desligado declarado; taxa real por perna registada; homogeneidade (versão/origem) declarada. Continua read-only (sem produto, sem base de dados, sem o loop do scalp).
- `backend/app/services/scalp_engine.py`: o gate `low_confidence` passa a ler a política do regime (valor do regime | desligado | fechado); o motor continua puro (o regime e os valores entram por parâmetro); token próprio para o regime fechado.
- `backend/app/services/scalp_service.py`: leitura da fronteira de regime e das políticas por regime a partir de configuração; cálculo do regime de mercado pela σ da janela (o mesmo valor que segue no payload); injeção no motor; o valor em uso é preservado quando não há relatório suficiente.
- `backend/app/services/scalp_jev_log.py`: o fecho do ciclo por regime fechado deixa registo visível (token próprio + veredicto da confiança), no mesmo ficheiro e formato do #1015/#1028.
- `backend/tests/`: régua (acurácia/retorno por faixa, curva do limiar, fecho/desligado/insuficiência, taxa por perna), política por regime, fronteira partilhada, valor em uso mantido, fail-closed de configuração.
- Sem `frontend/**`, sem rota, sem HTML, sem protótipo, sem painel/Monitor, sem `/api/scalp/status`, sem base de dados nova, sem exportação/Drive, sem backtest, sem PROD; sem segredos em qualquer artefacto.
