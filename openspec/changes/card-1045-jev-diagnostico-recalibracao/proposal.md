## Why

A régua do scalp Jev ainda compara o sinal com a referência que esconde o viés de compra, não justifica a geometria alvo/stop contra o custo, e só corre se o operador a lançar no terminal. O diagnóstico periódico, a aplicação controlada da confiança por regime e o acompanhamento têm de viver no sistema.

## Problema

A estratégia do scalp Jev é avaliada contra a referência errada e desenhada com uma geometria que não se paga. O resultado é uma expectância negativa por construção: com alvo +35 bp e stop −28 bp contra ~20 bp de round-trip, o custo consome 57% de cada vitória e o acerto exigido sobe de 44,4% para 76,2%; o preço só atinge o alvo em 29,8% dos casos em que toca uma barreira. A par disso, o sinal é comprador em 97,5% das decisões e vem a ser medido contra a moeda ao ar — a referência que, na prática, esconde precisamente este enviesamento e dá mérito que o sinal não tem.

Além disso, o operador precisa executar a régua manualmente no terminal. Falta um ciclo integrado ao sistema que rode o diagnóstico periodicamente, valide propostas, aplique apenas os ajustes autorizados e mostre o resultado, o histórico e os motivos de bloqueio ou reversão.

## História

Como operador do scalp Jev, quero que a avaliação me diga se o sinal tem informação real (e não apenas exposição à subida do mercado) e que a geometria de alvo/stop seja justificada pelo acerto realizado contra o custo, para que a decisão de operar assente numa expectância positiva medida — e não em números de produto nunca validados.

Quero também que esse diagnóstico seja periódico e que o sistema possa ajustar automaticamente os parâmetros autorizados quando a evidência permitir, com acompanhamento e reversão pela interface, sem depender de comandos manuais.

## Entra

- **Benchmark de viés casado:** a régua passa a comparar o sinal contra (a) comprar-e-segurar do próprio activo e (b) uma **regra aleatória com o mesmo viés direccional** do sinal; a *contribuição preditiva* (sinal − regra aleatória de mesmo viés) passa a ser reportada por faixa de confiança, por regime e por horizonte.
- **Acurácia contra a fasquia certa:** a acurácia do sinal passa a ser apresentada ao lado da acurácia do buy-and-hold, explicitando o viés direccional medido (fracção de BUY).
- **Recalibração da geometria alvo/stop:** a régua calcula e reporta o **break-even win rate** da geometria em uso com e sem custo, e mede o acerto realizado por barreira (alvo/stop/saída por tempo); propõe uma geometria alternativa (alvo, stop ou horizonte) cujo break-even seja **inferior** ao acerto realizado, ou declara que nenhuma o consegue.
- **Gate de geometria:** nenhuma geometria é adoptada sem o relatório; se nenhuma alternativa bater o break-even medido, a estratégia fica **declarada como não operável** nesse horizonte (não se inventa um alvo).
- **Gate de homogeneidade utilizável (absorve o #1044):** `unknown` (ou ausente) em versão do modelo / origem da confiança **não** conta como amostra homogénea; uma amostra elegível **vazia** também **não** é declarada homogénea. Sem homogeneidade verificada nenhum limiar é proposto, e o relatório distingue "homogénea" de "não verificada" com o número de janelas afectadas.
- **Horizonte como parâmetro medido, não fixo:** o relatório mostra o break-even e a expectância líquida em vários horizontes candidatos, para o horizonte ser escolhido pelo ponto em que o custo deixa de dominar o alvo.

### Diagnóstico periódico, aplicação controlada e acompanhamento

- **Execução periódica integrada:** rodar a avaliação automaticamente uma vez por dia, com o dia já fechado, só com janelas que já terminaram; não há relatório novo a meio do dia só porque passou um quarto de hora. Registrar a data, o período avaliado, a qualidade dos dados e o resultado de cada execução.
- **Qualidade antes de ajuste:** consumir os estados de medição do #1043 e os gates de homogeneidade, custo, benchmark e viabilidade deste card. Falha de leitura, dados vencidos, cobertura inadequada ou amostra não verificada impedem promover novos parâmetros; os motivos ficam explícitos. O automático só muda a confiança depois de 200 a 300 operações independentes medidas à parte, que não serviram para escolher o ajuste; com menos, o diagnóstico aparece e a confiança fica na mesma.
- **Validar antes de aplicar:** comparar a proposta com a configuração vigente em dados posteriores e separados dos usados para escolhê-la, considerando custos. Trocar quando a nova perde menos do que a actual nesses dados, mesmo que o resultado líquido continue negativo; prejuízo menor conta como melhoria. Quando não houver essa melhoria, manter a configuração e explicar o motivo.
- **Ajustes automáticos delimitados:** na primeira versão, aplicar automaticamente apenas a política de confiança por regime já suportada pelo #1030. Pode pôr um número novo, desligar o filtro de confiança ou parar o regime, e também reabrir um regime parado se a amostra passar — o desfecho que a avaliação declarar, sem travão extra. Não há banda de subida ou descida por passo. Preservar a semântica dos controles existentes. A avaliação e as propostas de alvo, stop e horizonte continuam integralmente no escopo original; sua aplicação automática não integra esta primeira versão.
- **Versão efetivamente usada:** registrar os valores anterior e novo, a evidência, o motivo e a versão aplicada; garantir que a versão exibida corresponda à consumida pelo scalper. Assim que a troca é aceite, a entrada seguinte e o que o operador vê já usam a confiança nova; a posição que já estava aberta sai como estava, e o operador não precisa de desligar o interruptor. Repetir uma execução não pode aplicar o mesmo ajuste duas vezes.
- **Acompanhamento e reversão:** acompanhar os resultados após cada alteração, permitir retornar a uma versão anterior e definir os critérios de reversão automática. Expor comando de reversão pelo operador e histórico das decisões.
- **Controle do operador:** permitir habilitar e pausar a calibração automática, respeitando alterações manuais, interruptor e kill existentes. Habilitar calibração não liga o scalper nem executa ordens por si só; a falha do diagnóstico não enfraquece proteções já existentes.
- **Integração na interface:** mostrar último diagnóstico, qualidade e período dos dados, configuração vigente, último ajuste e motivo de manter, aplicar, bloquear ou reverter, com histórico acessível no sistema. O operador não precisa executar comandos no uso cotidiano.
- **Decisões fechadas:**
  - O diagnóstico corre uma vez por dia, com o dia já fechado: um diagnóstico por dia, só com janelas que já terminaram. Não há relatório novo a meio do dia só porque passou um quarto de hora.
  - O automático só muda a confiança depois de 200 a 300 operações independentes medidas à parte, que não serviram para escolher o ajuste. Com menos, o diagnóstico aparece e a confiança fica na mesma.
  - O automático aplica o desfecho que a avaliação declarar: pode pôr um número novo, desligar o filtro de confiança ou parar o regime, e também reabrir um regime parado se a amostra passar. Sem travão extra. Não mexe em alvo, stop, horizonte nem tamanho nesta primeira versão. Não há banda de subida ou descida por passo.
  - A troca acontece quando a nova perde menos do que a actual em dados posteriores que não serviram para a escolher, já com o custo descontado, mesmo que o resultado líquido continue negativo. Prejuízo menor conta como melhoria. Se não houver essa melhoria, mantém a actual e o operador vê o motivo.
  - Assim que a troca é aceite, a entrada seguinte e o que o operador vê já usam a confiança nova. A posição que já estava aberta sai como estava. O operador não precisa de desligar o interruptor.
- **Ainda em aberto:**
  - **Intervalo mínimo entre alterações:** a cadência já é diária, mas não ficou decidido se a confiança pode mudar outra vez no dia seguinte ou só passados vários dias.
  - **Critérios de reversão automática:** já se sabe que melhoria é ficar menos mau, mas não ficou decidido quando voltar atrás (por exemplo voltar a perder mais do que a versão anterior, versus outro gatilho).

### Critérios observáveis

- O relatório mostra, para a geometria em uso, o break-even win rate com e sem custo e o acerto realizado por barreira, lado a lado.
- O relatório mostra a contribuição preditiva do sinal (sinal − regra aleatória de mesmo viés) e distingue-a do simple drift do mercado.
- O relatório mostra a fracção de BUY do sinal e a acurácia do buy-and-hold ao lado da do sinal.
- O relatório apresenta, por horizonte candidato, break-even, acerto realizado e expectância líquida.
- Se nenhuma geometria/horizonte candidato bater o break-even, o relatório declara a estratégia não operável e nenhum parâmetro é adoptado.
- Uma amostra com `model=unknown`/`confidence_origin=unknown` — ou uma amostra elegível vazia — aparece como **não homogénea / não verificada** e não permite proposta de limiar; só uma amostra com versão e origem declaradas e iguais é declarada homogénea.
- A avaliação continua **somente leitura**; a aplicação de ajustes ocorre em uma etapa própria, condicionada à validação. Na confiança do regime, o automático aplica o desfecho declarado (número novo, filtro desligado, regime parado ou regime reaberto) e não há banda de subida ou descida por passo.
- Com a automação habilitada, o diagnóstico corre sozinho uma vez por dia, só com janelas que já terminaram, e aparece no sistema com data e resultado. Não há relatório novo a meio do dia só porque passou um quarto de hora.
- Uma proposta válida é aplicada assim que a troca é aceite e passa a ser consumida pelo scalper: a entrada seguinte e o que o operador vê já usam a confiança nova, com versão e valores anterior/novo visíveis. A posição que já estava aberta sai como estava. O operador não precisa de desligar o interruptor.
- Falhas de medição, dados inválidos ou amostra não verificada bloqueiam a promoção e mostram o motivo; não são apresentados como evidência de desempenho negativo. Abaixo de 200 a 300 operações independentes medidas à parte, o diagnóstico aparece e a confiança fica na mesma.
- Se a nova não perde menos do que a actual em dados posteriores, já com o custo descontado, a configuração mantém-se e o operador vê o motivo — mesmo que o resultado líquido continue negativo.
- Não há banda de subida ou descida por passo: aplica-se o desfecho que a avaliação declarar. Execuções repetidas não aplicam o mesmo ajuste duas vezes.
- Pausa da calibração e reversão de versão funcionam pelo sistema, com histórico verificável.
- A homologação em DEV demonstra pela interface diagnóstico, aplicação permitida, bloqueio e reversão; publicação PROD continua pelo fluxo de release.

## Não entra

- Mudar a pergunta feita ao modelo (é o #1029).
- Redefinir a semântica da política por regime e dos controles do #1030. Este card passa a permitir a aplicação automática dos valores autorizados, usando o mecanismo existente e os critérios acima.
- Ajustar automaticamente tamanho de posição, limites de perda, alvo, stop ou horizonte nesta primeira versão.
- Reabrir #1006 (lookback), #1008 (stream), #1001 (interruptor/T/clip/kill) ou o gate de regime do #1025.
- Operar em produção ou alterar parâmetros de produto sem relatório; PROD é T16.
- Base de dados nova, Drive ou backtest externo. A persistência do histórico e das versões usa a infraestrutura existente; acompanhamento no sistema passa a fazer parte do escopo.

## What Changes

- A avaliação passa a reportar benchmark de viés casado (comprar-e-segurar e regra aleatória com o mesmo viés), contribuição preditiva, acurácia ao lado do buy-and-hold, fracção de BUY, break-even com e sem custo, acerto por barreira e horizontes candidatos. Propõe geometria ou declara o horizonte não operável. Não adopta alvo, stop, horizonte nem tamanho.
- O gate de homogeneidade deixa de tratar `unknown`, origem ausente ou amostra elegível vazia como homogénea. Sem homogeneidade verificada não há proposta de limiar. O relatório distingue «homogénea» de «não verificada».
- A avaliação continua somente leitura. Uma etapa própria, uma vez por dia com o dia já fechado, pode aplicar só o desfecho de confiança por regime já definido no #1030 (número novo, filtro desligado, regime parado ou regime reaberto), sem banda de passo, depois da validação em dados posteriores. Abaixo de 200 a 300 operações independentes medidas à parte, o diagnóstico aparece e a confiança fica.
- A versão aplicada é a que o scalper consome na entrada seguinte. Posição já aberta sai como estava. O interruptor não se desliga. Repetir a execução não aplica o mesmo ajuste outra vez.
- No módulo Scalp BTCUSDT já existente em `/monitor`: último diagnóstico, qualidade e período, configuração vigente, último ajuste, motivo (manter, aplicar, bloquear ou reverter), pausa da calibração, reversão e histórico. Sem comando de terminal no uso cotidiano. Sem rota nova.
- Duas perguntas que o body deixa em aberto ficam como suposição de desenho no `design.md`, à espera da aprovação — não como decisão já tomada pelo Alan.

## Capabilities

### New Capabilities

- `scalp-jev-diagnostico-recalibracao`: diagnóstico diário do dia fechado, portões de qualidade, aplicação validada só da política de confiança por regime, versão consumida pelo scalper, pausa, reversão e histórico no módulo já existente.

### Modified Capabilities

- `scalp-jev-eval-ruler`: o relatório passa a incluir benchmark de viés casado, break-even com e sem custo, acerto por barreira e horizontes candidatos; a geometria é proposta ou declarada não operável, sem ser adoptada; a avaliação permanece somente leitura.
- `scalp-jev-net-return-ruler`: homogeneidade deixa de aceitar `unknown`, origem ausente ou amostra elegível vazia; distingue «homogénea» de «não verificada».
- `scalp-confidence-threshold-per-regime`: a proibição de mostrar a política no Monitor e de a persistir deixa de valer para o acompanhamento deste card; os três desfechos (número, filtro desligado, regime fechado) e os outros gates mantêm-se; a versão aplicada é a consumida na entrada.
- `monitor`: o módulo Scalp BTCUSDT em `/monitor` mostra o diagnóstico, a configuração vigente, o motivo e o histórico, sem redesenhar a board nem o Operar.

## Impact

- Frontend: delta no `ScalpModule` dentro de `/monitor`. Board (`table.signals`) e Operar intactos. Sem landing, Ajuda ou rota nova.
- Backend: a régua em `scripts/scalp_jev_eval.py` ganha o relatório novo e o gate de homogeneidade corrigido, e continua sem escrever produto. A aplicação e o histórico usam o Postgres e o Alembic já existentes (não uma base nova, não Drive, não backtest externo). O loop do scalp lê a versão aplicada na entrada e não a usa para mudar a saída da posição aberta.
- Depende de #1043 para o estado da medição. Não reabre #1029, #1006, #1008, #1001 nem o gate de regime do #1025. PROD continua T16.
- Protótipo: clone de `/monitor` com o delta no módulo scalp. `frontend/public/prototypes/card-1045-jev-diagnostico-recalibracao/index.html`.

