## Context

Card **#1045**, Status=Design. Briefing = issue grelhado (Problema, História, Entra, Não entra). Depende de **#1043** para o estado da medição. O #1052 fica absorvido aqui. Sem reentrevista. As decisões fechadas no body não se reabrem. As duas perguntas que o body deixa em aberto estão na seção **Suposições de desenho** — não são escolha já feita pelo Alan.

A régua vive em `scripts/scalp_jev_eval.py`. É somente leitura: lê o log de diagnóstico e o OHLCV já guardado, não escreve produto e não precisa do loop. A homogeneidade está em `_homogeneity`: `len(models) <= 1 and len(origins) <= 1` trata `unknown` (ou ausente, colapsado para `"unknown"`) e a amostra elegível vazia como homogéneas. A geometria de produto é alvo +35 bp / stop −28 bp. O break-even com custo já é calculado para um par derivado; o relatório ainda não põe o break-even com e sem custo ao lado do acerto por barreira, nem o benchmark de viés casado, nem vários horizontes. Os candidatos de alvo/stop já existem (`GEOMETRY_TARGET_CANDIDATES_BP` × `GEOMETRY_STOP_CANDIDATES_BP`). Os timeframes OHLCV já lidos são 1m, 5m, 15m e 1h. A 15 min com vela de 15 min a barreira não cabe na janela.

A política de confiança por regime é a do #1030: `numeric` (limiar em [0, 1]), `off` (filtro desligado; a decisão segue previsão × custo × regime) ou `closed` (regime parado, token próprio, distinto de `regime` e de `low_confidence`). Hoje sai de env (`SCALP_CONFIDENCE_MIN_CALM`, `SCALP_CONFIDENCE_MIN_ACTIVE`, `SCALP_REGIME_BOUNDARY_BP`), lida em `scalp_service._confidence_policy_for`, com fallback **fechado**. O spec vigente do #1030 proíbe mostrar essa política no Monitor, em `/api/scalp/status` e em tabela. Este card levanta essa proibição só para o acompanhamento e para a versão aplicada. Não muda o significado dos três desfechos nem os gates `hurdle`, `regime` (custo com folga) e `toxic_book`.

O scalp do operador já está em `/monitor`, no `ScalpModule` (`interruptor`, T, clip, kill, lookback «últimos 15 min», alvo +35, stop −28). O loop é um só (`scalp_loop`) e percorre os utilizadores com o interruptor ligado. O interruptor e o kill são por utilizador (`scalp_user_states`). A política de confiança é do processo, não de cada conta.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nessas regiões. Delta fora desses blocos: o bloco «Diagnóstico do scalp» dentro do módulo Scalp BTCUSDT já existente. Sem extras. O index não é um painel de estados.

## Goals / Non-Goals

**Goals:**

- A régua reporta o benchmark de viés casado, a contribuição preditiva, a fracção de BUY, a acurácia do sinal ao lado da do buy-and-hold, o break-even com e sem custo, o acerto por barreira e o break-even, o acerto e a expectância líquida por horizonte candidato.
- Propõe uma geometria alternativa cujo break-even seja inferior ao acerto realizado, ou declara que nenhuma o consegue. Sem relatório, nada se adopta. Se nenhuma geometria ou horizonte candidato bater o break-even, declara **não operável** e não adopta parâmetro nenhum.
- `unknown` ou ausente na versão do modelo ou na origem da confiança, e a amostra elegível vazia, não são homogéneos. O relatório distingue «homogénea» de «não verificada» e conta as janelas afectadas. Sem homogeneidade verificada não há limiar proposto.
- Uma vez por dia, com o dia já fechado, só com janelas que já terminaram. Não há relatório novo a meio do dia. O diagnóstico fica no sistema com data, período, qualidade e resultado.
- A avaliação continua somente leitura. A aplicação é outra etapa. Só a política de confiança por regime do #1030: o número que a avaliação declarar, o filtro desligado, o regime parado ou o regime reaberto. Sem banda de subida ou descida. Sem mexer em alvo, stop, horizonte ou tamanho.
- A troca, quando a comparação se aplica, exige que a nova perca menos do que a actual em dados posteriores que não serviram para a escolher, já com o custo, mesmo que o líquido continue negativo. Sem essa melhoria, mantém e mostra o motivo.
- Abaixo de 200 a 300 operações independentes medidas à parte, o diagnóstico aparece e a confiança fica na mesma.
- A versão que o operador vê é a que a entrada seguinte consome. A posição já aberta sai como estava. O operador não desliga o interruptor. A mesma execução não aplica o mesmo ajuste duas vezes.
- Pausa da calibração, reversão e histórico funcionam no `/monitor`. Ligar a calibração não liga o scalper nem envia ordens. Uma falha do diagnóstico não enfraquece kill, interruptor nem os outros gates.
- O uso cotidiano não pede comando de terminal.

**Non-Goals:**

- Mudar a pergunta ao modelo (#1029).
- Redefinir o que é número, filtro desligado ou regime parado, nem o gate de regime do #1025.
- Aplicar automaticamente alvo, stop, horizonte, tamanho ou limite de perda.
- Reabrir lookback e hold do #1006, stream do #1008, interruptor/T/clip/kill do #1001.
- Operar em PROD ou mudar parâmetro sem relatório. PROD é T16.
- Base de dados nova, Drive ou backtest externo.
- Rota nova, landing, Ajuda, ou redesenhar a board e o Operar.

## Suposições de desenho

O Alan **não** fechou estas duas. Ficam visíveis para a aprovação. Se ele recusar uma, o desenho muda; até lá o Apply não trata a suposição como decisão de produto já tomada.

1. **Intervalo mínimo entre alterações da confiança.** A cadência do diagnóstico já é diária. Suposição deste desenho: **não há quarentena de vários dias**. A confiança pode mudar outra vez no dia fechado seguinte, se a amostra posterior desse dia for nova — não reutiliza as operações que escolheram a versão vigente nem as que a validaram — e os outros portões passarem. Não muda duas vezes no mesmo dia. Se essa amostra nova ainda não chegou ao mínimo, o diagnóstico do dia aparece e a confiança fica. Alternativa não escolhida aqui: impedir nova troca durante N dias de calendário. Isso seria um travão que ele não pediu; fica recusável na aprovação.

2. **Critérios de reversão automática.** Já está fechado que melhoria é perder menos, e que o operador pode reverter pela interface. Não está fechado **quando** o automático volta atrás. Suposição deste desenho: num dia fechado **posterior** ao da aplicação, se uma amostra nova de pelo menos o mesmo mínimo de operações independentes (que não validou a troca) mostrar que a versão aplicada passa a perder mais, já com o custo, do que a versão imediatamente anterior na mesma amostra, o sistema reverte para essa anterior e regista o motivo. Não inventa um terceiro número. Não reverte no próprio dia da aplicação. Falha de medição, dado vencido ou amostra não verificada **não** reverte: bloqueiam promoção e não desfazem uma versão já aceite. A reversão manual do operador não espera essa amostra. Alternativa não escolhida aqui: outro gatilho (vários dias seguidos, ou uma banda fixa de perda).

## Decisions

1. **A superfície é o `/monitor` que já tem o scalp.** O acompanhamento entra no `ScalpModule`, por baixo dos KPIs já existentes. Não há rota nova: a única página que já mostra o interruptor, o kill e o alvo/stop do operador é esta. A board e o Operar ficam. Alternativa rejeitada — página nova ou painel de quatro estados: a rota não está no catálogo e o index canónico não pode ser um painel de comparação.

2. **A avaliação e a aplicação são etapas diferentes.** `scripts/scalp_jev_eval.py` continua sem escrever produto, estado de trading ou versão. O agendamento diário chama essa avaliação e, noutra função, decide manter, aplicar, bloquear ou reverter. Alternativa rejeitada — o script passar a gravar a política: mistura a leitura com a troca e fura o critério «avaliação somente leitura».

3. **Um diagnóstico por dia UTC já fechado.** O relógio do scalp é UTC (`_utcnow`). O dia fechado é o dia de calendário UTC que já terminou. O processo que já arranca `start_scalp_loop` dispara **uma** vez, depois das 00:15 UTC, só com janelas cujo fim é ≤ 00:00 UTC desse dia. Não há segundo relatório porque passaram 15 minutos. Se nessa corrida o estado #1043 for `não medido` ou o dado estiver vencido (a vela mais nova é anterior ao fim da última janela), o diagnóstico desse dia fica bloqueado e não é reescrito mais tarde no mesmo dia. Alternativa rejeitada — repetir de 15 em 15 minutos até o OHLCV chegar: é o relatório a meio do dia que o body proíbe. Alternativa rejeitada — dia em America/Sao_Paulo: o código não tem esse fuso; introduzi-lo seria outro contrato.

4. **Operação independente e o chão da banda 200 a 300.** Operação independente é a janela não sobreposta que a régua já usa, não cada tick do Jev. O *como* operacional da banda fechada «200 a 300» é o **chão 200**: abaixo de 200 medidas à parte, o diagnóstico aparece e a confiança não muda; de 200 em diante a comparação pode aplicar. Exigir 300 seria um travão acima do chão da banda. 300 não é segundo portão. O relatório mostra a contagem. Alternativa rejeitada — usar as ~2 250 decisões com lado como se fossem independentes: a evidência do body separa isso das 67 janelas independentes.

5. **Escolha e posterior são cronológicas.** A escolha do desfecho usa só janelas anteriores ao corte. A posterior é o que veio depois, não entrou na escolha, já terminou, e está medida. A regra aleatória do benchmark usa semente gravada no diagnóstico (derivada do dia fechado), para a mesma corrida dar o mesmo número. Alternativa rejeitada — partir a amostra ao acaso: mistura o que escolheu com o que valida.

6. **O desfecho aplicado é o declarado, sem banda de passo.** Número novo = o valor em [0, 1] que a régua declarar para aquele regime, não um passo em direção ao antigo. Filtro desligado = `off`. Regime parado = `closed`. Regime reaberto = o `numeric` ou `off` que a avaliação declarar para um regime que estava parado. A regra de separação do #1030 (número só quando o retorno líquido esperado é positivo e melhor do que aceitar tudo; se não separa, filtro desligado; amostra insuficiente, regime fechado na **avaliação**) não se reescreve. Alternativa rejeitada — limitar a subida ou a descida do número: o body proíbe essa banda.

7. **«Perde menos» e «reabrir» lêem-se juntos, sem travão extra.** Entre duas políticas que já podem ser comparadas na posterior (número contra número, número contra filtro desligado, ou parar contra a vigente), aplica-se só se o líquido com custo da declarada for maior que o da vigente, mesmo que ambos sejam negativos. Parar realiza 0: ganha de uma vigente negativa e não ganha de uma vigente positiva. **Reabrir** não tem de bater 0 nem de ficar positivo. Aplica-se quando a posterior (pelo menos 200, fora da escolha) confirma que o regime deixa de estar fechado e o desfecho é o número ou o filtro desligado declarado. Exigir que a reabertura perca menos do que 0 anularia a frase fechada «reabrir se a amostra passar, sem travão extra», porque uma política ainda negativa nunca bate o zero de ficar parado. Se a posterior voltar a fechar o regime, fica parado e o motivo aparece. Alternativa rejeitada — reabrir só com líquido positivo: é o travão extra recusado.

8. **Geometria fica no relatório.** Break-even sem custo = `|stop| / (|alvo| + |stop|)`. Com custo = `(2 × taxa por perna + |stop|) / (|alvo| + |stop|)`. O acerto realizado separa alvo, stop e saída por tempo. Os horizontes candidatos são **15 min, 1 h, 4 h e 24 h**, medidos com a vela mais fina já guardada que caiba no horizonte (1m, senão 5m, 15m, 1h). Horizonte de 15 min só com vela de 15 min conta como barreira indeterminada, não como acerto zero. A proposta é o par (alvo, stop ou horizonte) cujo break-even **com custo** seja inferior ao acerto realizado; se houver vários, o de maior expectância líquida com custo. Não se grava alvo, stop nem horizonte. Se **nenhum** candidato bater o break-even, o diagnóstico diz não operável e **não adopta parâmetro nenhum**, incluindo a confiança. Se algum candidato bater, a proposta fica no relatório e a confiança ainda pode mudar pelos portões dela; o painel diz que alvo, stop e horizonte não mudaram. Alternativa rejeitada — aplicar a geometria que paga: está fora desta versão. Alternativa rejeitada — mudar a confiança mesmo quando nada bate o break-even: o critério observável diz que nenhum parâmetro é adoptado.

9. **Homogeneidade deixa de ser inerte.** Amostra elegível vazia → **não verificada**, não homogénea, sem limiar. `model` ou `confidence_origin` ausente ou `unknown` não conta como valor declarado. Só é **homogénea** uma amostra com uma versão declarada e uma origem declarada, iguais em todas as janelas elegíveis. Mistura de valores declarados → não homogénea, com a contagem de janelas afectadas. Tudo `unknown` → não verificada, e as janelas afectadas são as elegíveis. Sem isto verificado, nenhum limiar é proposto e a aplicação bloqueia. O motivo não é apresentado como desempenho negativo. Alternativa rejeitada — manter `len <= 1`: é o bug que o body absorve do #1044.

10. **O que bloqueia a promoção, sem apagar o diagnóstico.** Além da posterior abaixo de 200, da falta de melhoria e da não-operabilidade: estado #1043 `não medido`; `medição parcial` cuja cobertura não fecha o realizado do dia; dado vencido; homogeneidade não verificada; custo que não seja a taxa real por perna quando essa taxa é conhecida (o fallback com a taxa conhecida é defeito, não número neutro); benchmark que não dê para calcular. Contribuição preditiva de 0,00 bp **não** bloqueia por si: é resultado. A calibração pausada também não aplica; o diagnóstico desse dia mesmo assim fica, com motivo de bloqueio. Nenhum destes casos limpa o kill, desliga o interruptor ou afrouxa os outros gates.

11. **Onde se guarda, sem base nova.** Postgres e Alembic já usados pelo scalp. Três acrescentos nessa base, não um motor novo e não Drive: uma linha por dia fechado (única), as versões aplicadas (impressão digital única, para a mesma troca não entrar duas vezes) e o interruptor global da calibração. Sem versão aplicada, a entrada continua a ler o env do #1030 e fecha em caso de dúvida. Alternativa rejeitada — base ou ficheiro à parte: o body entrega o histórico à infraestrutura existente.

12. **A versão vista é a versão consumida.** `/api/scalp/status` passa a incluir a política vigente e o id da versão, lidos do mesmo sítio que a entrada. A entrada seguinte usa essa versão assim que a troca é aceite. A saída da posição já aberta não relê a confiança e não altera alvo, stop nem horizonte. O interruptor do utilizador não é premido. Alternativa rejeitada — escrever só o env do processo: não sobrevive a reinício e o painel pode divergir do que o scalper faz.

13. **Pausa, reversão manual e quem manda.** A calibração é global, como a política. O comando está no módulo de cada `/monitor` autenticado e grava o mesmo estado. Não escreve `enabled` nem `killed`. Nasce **pausada**: instalar não troca a confiança sozinho. O diagnóstico diário corre e aparece na mesma. Ligar a calibração não liga o scalper. Reverter manualmente escolhe a versão anterior registada, vale na entrada seguinte, não espera as 200 operações e não desliga o interruptor. O automático não reaplica, nesse dia, a impressão digital que o operador acabou de desfazer. Alternativa rejeitada — nascer ligada: a primeira noite em DEV/PROD poderia trocar a confiança sem o operador ter habilitado o comando.

14. **Benchmark.** Em cada janela independente medida: retorno do sinal, retorno de comprar-e-segurar (sempre comprado no activo) e retorno de uma regra que tira BUY com a mesma fracção de BUY do sinal, sem olhar o preço. Os três levam o mesmo custo `2 × taxa por perna`. Contribuição preditiva = média do sinal menos média da regra aleatória, em bp, por faixa de confiança, por regime e por horizonte. O drift (comprar-e-segurar) aparece ao lado e não entra nessa subtração. A acurácia do sinal aparece ao lado da acurácia do buy-and-hold, com a fracção de BUY. Alternativa rejeitada — subtrair o comprar-e-segurar e chamar-lhe contribuição preditiva: o body pede as duas coisas separadas.

15. **O painel é um diagnóstico e uma lista, não quatro cartões.** A primeira vista usa frase de trader iniciante; os números fechados são os mesmos. O index mostra o dia em que a confiança não mudou, coerente com a evidência do body (67 operações, cerca de 76 em 100 para não perder com a taxa contra cerca de 30 em 100 no alvo, confiança na mesma, scalp desligado, ajuste automático ligado). O histórico na mesma página tem uma linha de aplicar, uma de manter, uma de bloquear e uma de reverter (`data-verb`), para a homologação ver os quatro motivos sem uma grelha de estados. Break-even, homogeneidade e bp ficam na régua, não como rótulo do ecrã. Alternativa rejeitada — quatro cartões irmãos como URL canónica.

## Risks / Trade-offs

- [Uma corrida às 00:15 UTC perde o dia se o OHLCV ainda não chegou] → O diagnóstico fica bloqueado com o estado #1043, não como perda. Não há segunda corrida nesse dia. O dia seguinte avalia o que já tiver fechado.
- [Reabrir pode ligar um regime ainda negativo] → É o «sem travão extra» já fechado. O painel mostra o líquido e o motivo. Não mexe no interruptor: utilizador com scalp desligado continua sem ordem.
- [Qualquer operador autenticado pausa ou reverte a política global] → O módulo já é o controlo do operador; a política já é do processo. Não altera o interruptor nem o kill dos outros.
- [A confiança muda e a geometria em vigor continua a não se pagar, desde que outro horizonte bata o break-even] → Alvo, stop e horizonte não são aplicados. O painel diz isso. Se nenhum candidato bate, a confiança também não muda.
- [O gate de homogeneidade passa a bloquear amostras que hoje ele deixava passar] → É o comportamento pedido. O motivo é «não verificada», não «prejuízo».
- [Rollback do binário que deixe de ler a versão aplicada volta ao env e pode divergir] → Antes desse binário, a pausa está ligada ou o env é reposto com a versão vigente. A reversão de produto, no dia a dia, é o comando de reverter, não dropar tabelas.
- [Vários workers da API] → A unicidade do dia fechado e da impressão digital impedem duas aplicações. Quem perde a corrida lê o diagnóstico já gravado.

## Migration Plan

- Migração Alembic na mesma base do `scalp_user_states`. Sem backfill que invente versão: enquanto não houver versão aplicada, a entrada segue o env do #1030.
- A calibração nasce pausada. O primeiro diagnóstico diário aparece e não aplica.
- Rollback de produto: pausar a calibração e, se uma versão já tiver sido aceite, reverter para a anterior. A posição aberta não é reescrita.
- PROD só por T16, com relatório. Este change não publica PROD.

## Open Questions

Só as duas suposições acima (intervalo entre alterações; quando o automático reverte). O resto do body está fechado ou é *como* deste desenho (dia UTC, chão 200, reabrir sem ter de bater zero, calibração que nasce pausada).

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1045-jev-diagnostico-recalibracao/` → `frontend/public/prototypes/card-1045-jev-diagnostico-recalibracao/index.html`. Clone da página viva `/monitor` (base proto #1006 = `MonitorStatusTab` + `ScalpModule` vigentes) + delta só no módulo scalp. Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. `COPIED:start`/`COPIED:end` nas regiões clonadas.
- O delta é a primeira vista em frase de trader iniciante. Título «Como está o scalp». Lead: um aviso por dia, só depois que o dia fecha; este é o de 26 de setembro de 2026; hoje não há outro. Quando: 26 set 2026, sobre o dia 25 que já fechou. Dados: servem para esta leitura. Até quando: só o que já tinha fechado à meia-noite. Confiança agora: mercado calmo só entra acima de 55%; mercado agitado não entra; versão 12. Última decisão: não mudei a confiança. Amostra: 67 operações, e não dá para compará-las; cerca de 200 para mudar. Alvo e stop: cerca de 76 em 100 com a taxa, cerca de 44 em 100 sem a taxa, e o preço chegou no alvo em cerca de 30 em 100 das vezes em que bateu num dos lados. O sinal: não ganhou nada além de ficar comprado. O lado: 97 em 100 foram compra; acertar o lado ficou em 49 em 100, igual a comprar e segurar (50 em 100). Motivo: não mudei nada; ainda só há 67 operações medidas à parte, abaixo de 200, amostra não comparável; com este alvo e este stop o scalp não se paga; a confiança fica; alvo, stop e o prazo não mudam. Interruptor do scalp **Desligado**. O do ajuste diz **Ligada**, com nome acessível «Ajuste automático», «Pausar ajuste automático» e «Voltar à versão anterior». Histórico nas mesmas frases, com `data-verb` bloquear, reverter, aplicar, manter. Sem rota nova. Sem landing/Ajuda. Sem os rótulos break-even, homogeneidade ou bp no ecrã.

## Prototype Validation

- **URL canónica:** `frontend/public/prototypes/card-1045-jev-diagnostico-recalibracao/index.html`. Sem HTML irmão. T5 mede só este index.
- **Digest (UTF-8 sha256):** `index.html` `413b13da60149ce7b02a98706df13527a22d6b0c02215c575d6d448f2e89ccc6`.
- **browser_gate:** Assessment B abriu a URL pública. O HTML servido traz «Como está o scalp» e não traz «Break-even». Detector exit 0.

## Impeccable

- P2 produto: no histórico de 26 set, «Com este prazo o scalp não se paga» não é a mesma causa do motivo, que aponta o alvo e o stop. A primeira vista já diz a causa certa. Aceite.
- P3 Apply: Pausar, o interruptor e Voltar à versão anterior não mudam o estado ao clique. A vista canónica é o dia em que nada mudou.
- P3 Apply: em 1280 o Operar da linha continua cortado, como no vivo. Em 390 o placeholder da busca aparece cortado.

Snapshots: `.impeccable/critique/1045-card-1045-jev-diagnostico-recalibracao-A2.md` e `.impeccable/critique/1045-card-1045-jev-diagnostico-recalibracao-B2.md`.

## Design Critique

Dupla nova sobre a cópia de trader iniciante. Mesmo juízo do autor (Grok 4.7, `grok-4.7`). Sem P0/P1. Sem rework.

- Assessment A PASS. a1 P2 produto: uma frase do histórico fala em prazo quando a causa é o alvo e o stop. Aceite.
- Assessment A a2 P3 implementação: botões sem handler. Aceite para o Apply.
- Assessment B PASS. Detector exit 0. b1–b3 P3 implementação (Operar cortado, botões sem handler, placeholder da busca). Aceites para o Apply.
- Tokens `UI impact: affected`, `live_route: /monitor`, `surface: existing` mantidos. Landmarks da listagem presentes.

Disposition: submeter. O Alan viu esta frase e disse que melhorou.

Design Agent verdict: PASS

proxy modelo: design-autor → Grok 4.7 (grok-4.7)
proxy modelo: Assessment A → Grok 4.7 (grok-4.7)
proxy modelo: Assessment B → Grok 4.7 (grok-4.7)
