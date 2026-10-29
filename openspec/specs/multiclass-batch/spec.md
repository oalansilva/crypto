# multiclass-batch Specification

## Purpose
TBD - created by archiving change card-1120-lote-multiclasse. Update Purpose after archive.
## Requirements
### Requirement: Lote aceita cripto, ação e ETF juntos
O lote do Combo (`/combo/configure`) e da Otimização (`/combo/optimize`) SHALL aceitar pares cripto, ações e ETFs do catálogo unificado na mesma seleção. Uma seleção com mais de 1 ativo MUST ser tratada como lote, mesmo quando só 1 ativo sobra para rodar. Cada ativo MUST rodar com a sua classe, fonte, sessão, ajuste e moeda, e o resultado de cada ativo MUST guardar essas informações. Ativo marcado pela Binance (suspenso, fora de mercado, sem negociação, sem regras ou removido) MUST continuar fora de análise nova, como no #1117.

#### Scenario: Lote misto 1d
- **WHEN** Alan roda o Combo com BTC/USDT, NVDA e SPY em 1d
- **THEN** o lote MUST otimizar os três ativos, um por vez, com a mesma configuração
- **AND** BTC/USDT MUST rodar como cripto (Binance Spot, 24/7, USDT) e NVDA e SPY como ação e ETF (Binance Ações, pregão regular de Nova York, ajustado, USD)

#### Scenario: Servidor aceita lote misto
- **WHEN** `POST /api/combos/backtest/batch` recebe símbolos de cripto, ação e ETF
- **THEN** o servidor MUST NOT recusar ação nem ETF com `asset_class_not_supported`
- **AND** MUST recusar só ativo marcado pela Binance ou fora do catálogo, como no #1117

#### Scenario: Fonte por ativo no Combo
- **WHEN** a seleção do Combo tem cripto e ação ou ETF
- **THEN** o campo Market Data MUST mostrar "Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)"

#### Scenario: Só 1 ativo sobra
- **WHEN** a seleção tem BTC/USDT, NVDA e SPY e o tempo é 5m
- **THEN** o pedido MUST ir como lote, com BTC/USDT rodando e NVDA e SPY como "Fora" no estado por ativo

### Requirement: Mesmas regras do backtest individual
Cada ativo do lote SHALL ser otimizado pelo mesmo caminho do backtest de 1 ativo do #1119: gap no stop, precisão efetiva declarada (sem queda silenciosa), custos, calendário e anualização por classe, tempos montados no pregão para ação e ETF. O lote MUST NOT ter regras próprias de execução.

#### Scenario: Ação no lote igual ao backtest individual
- **WHEN** NVDA 1d roda no lote e no backtest de 1 ativo com a mesma janela, configuração e amostra
- **THEN** os melhores parâmetros e as métricas MUST ser iguais

#### Scenario: Regressão do lote de cripto
- **WHEN** um lote só de cripto roda antes e depois deste card na mesma amostra
- **THEN** os resultados MUST ser iguais, salvo o que o #1119 já mudou (gap no stop)

### Requirement: Tempo gráfico que não serve tira ação e ETF antes de começar
Quando o tempo do lote não está disponível para ação e ETF (1m e 5m no Combo; 1m, 5m e 30m na Otimização), ações e ETFs SHALL ficar fora antes de o lote começar, com o motivo, e as criptos MUST rodar. Na Otimização, ação e ETF em 15m, 1h ou 4h cujo 5m (que monta esses tempos) começa depois do fim da janela fixa MUST ficar fora pelo mesmo caminho, com o motivo de cobertura. O motivo MUST citar o tempo escolhido e aparecer no texto antes de rodar, em "Ficam fora" e no estado "Fora" de cada ativo; na Otimização o conselho MUST ser "use 1d aqui ou o Combo", nunca outro tempo que também fica fora. Na seleção com ação ou ETF e cripto, esses tempos MUST aparecer marcados "(só cripto)" e continuar escolhíveis.

#### Scenario: Lote misto em 5m
- **WHEN** a seleção é BTC/USDT, NVDA e SPY e o tempo é 5m
- **THEN** o texto antes de rodar MUST dizer "Fora antes de começar: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d."
- **AND** o Confirmar lote MUST listar NVDA e SPY em "Ficam fora" com o motivo
- **AND** BTC/USDT MUST rodar e gravar o favorito

#### Scenario: Otimização com janela fixa que o 5m não cobre
- **WHEN** a Otimização roda um lote em 15m, 1h ou 4h com BTC/USDT, NVDA e SPY e a cobertura do catálogo mostra que o 5m de NVDA e de SPY começa depois de 31 jan. 2024
- **THEN** o texto antes de rodar MUST dizer "Fora antes de começar: NVDA (Ação), SPY (ETF) — o 5m deles começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período."
- **AND** NVDA MUST ficar "Fora" antes de começar com "o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela"
- **AND** o Confirmar lote MUST listar NVDA e SPY em "Ficam fora" com esse motivo, e a Configuração MUST mostrar o tempo escolhido (não "1d")

#### Scenario: Otimização em tempo só de cripto
- **WHEN** a Otimização roda o lote misto em 1m, 5m ou 30m
- **THEN** o motivo MUST dizer "ação e ETF não rodam em <tempo>; para incluí-los, use 1d aqui ou o Combo, que tem período."

#### Scenario: Só ações e ETFs em 5m
- **WHEN** a seleção tem só ações e ETFs e o tempo é 5m
- **THEN** nada MUST rodar e a tela MUST avisar antes de rodar, com o motivo e os tempos que servem

### Requirement: Confirmar lote com a contagem de coleta
Rodar com mais de 1 ativo SHALL abrir antes um painel "Confirmar lote", no fluxo da página (sem modal), com: quantos ativos vão rodar, por classe e moeda; quantos ainda precisam de coleta de histórico e de quê; quem fica fora e por quê; a configuração (template, tempo e período escolhidos); e a regra dos favoritos. Um ativo precisa de coleta quando, dentro da janela pedida, a Binance tem candles das séries que ele usa (tempo gráfico e, com intrabar, o 5m) que ainda não estão guardados — ativo sob demanda, lacuna ou o trecho desde a última coleta. O que a Binance não tem MUST NOT contar, e ativo guardado sem lacunas e atualizado MUST NOT contar. Na Otimização, o Confirmar e o painel do lote MUST ocupar a coluna de resultado, no lugar de "Ready to Optimize". O lote MUST aceitar qualquer quantidade de ativos. A contagem MUST vir de `POST /api/combos/backtest/batch/preview`, que lê a cobertura do histórico (#1118) sem coletar nada. O lote só começa em "Confirmar e rodar"; "Voltar" fecha o painel e devolve o foco ao botão de rodar.

#### Scenario: Contagem antes de confirmar
- **WHEN** Alan clica em Otimizar com BTC/USDT, NVDA e SPY em 1d, todo o histórico, com BTC/USDT e NVDA guardados sem lacunas e atualizados e SPY sob demanda
- **THEN** o painel MUST mostrar "Precisam de coleta de histórico: 1 de 3 — SPY (1d e 5m do intrabar)" e dizer que BTC/USDT e NVDA já estão guardados, sem lacunas e atualizados

#### Scenario: Série que a Binance não tem não conta
- **WHEN** a Otimização (1 a 31 jan. 2024) confirma o mesmo lote e a Binance não tem 5m de SPY em jan. 2024
- **THEN** SPY MUST contar só com "1d"
- **AND** nada MUST ser coletado nem otimizado até "Confirmar e rodar"

#### Scenario: Lote grande
- **WHEN** a seleção vem do "Todos do filtro" de Ações com 2.431 ativos
- **THEN** o lote MUST ser aceito e o painel MUST mostrar quantos dos 2.431 precisam de coleta, separando os sem histórico guardado dos que só precisam do trecho desde a última coleta, e quantos já estão guardados e atualizados

### Requirement: Coleta dentro do lote, ativo por ativo
O lote SHALL coletar o histórico que cada ativo usa (a série do tempo gráfico e, com intrabar, o 5m que monta o 15m) pela coleta sob demanda do #1118, imediatamente antes de otimizar aquele ativo. O progresso da coleta MUST aparecer no ativo (série e página atual de total). Falha de coleta sem nada guardado MUST deixar o ativo em "Falha" com o motivo; coleta parcial MUST seguir no trecho guardado, com a janela coberta no resultado (#1119).

#### Scenario: Progresso da coleta
- **WHEN** SPY está coletando o 5m do intrabar
- **THEN** a linha de SPY MUST mostrar "Coletando histórico" e "5m do intrabar · página 7 de 20" com uma barra de progresso

### Requirement: Estado por ativo
O painel do lote SHALL listar cada ativo com classe, moeda, estado e detalhe, com os estados: Na fila, Coletando histórico, Otimizando, Sucesso, Sucesso · precisão diária, Insuficiente, Rejeitado, Falha, Pulado, Fora e Não rodou. Ativo com problema (Insuficiente, Rejeitado, Falha) MUST NOT gravar favorito nem aparecer como resultado válido, e MUST NOT impedir os demais. O painel MUST ter filtro por estado com contagem, uma linha viva `role=status` com o que está acontecendo e, acima de 50 ativos, "Mostrar mais 50".

#### Scenario: Ativo insuficiente
- **WHEN** a janela coberta de AAPL tem menos candles do que a estratégia precisa
- **THEN** AAPL MUST ficar "Insuficiente" com o motivo e "Nenhum favorito gravado", e o lote MUST seguir para o próximo ativo

#### Scenario: Ativo reprovado no walk-forward
- **WHEN** o melhor candidato de QQQ é NO-GO no holdout
- **THEN** QQQ MUST ficar "Rejeitado" com o motivo e sem favorito

#### Scenario: Falha de um ativo
- **WHEN** a coleta de SPY falha sem nada guardado
- **THEN** SPY MUST ficar "Falha" com o motivo da Binance e o lote MUST seguir

#### Scenario: Já nos favoritos
- **WHEN** ETH/USDT já tem favorito com a mesma estratégia, tempo, período e direção
- **THEN** ETH/USDT MUST ficar "Pulado" com o motivo

### Requirement: Precisão diária visível no lote
Ação ou ETF cujo intradiário não cobre a janela SHALL gerar resultado válido em precisão diária (regra do #1119), com o estado "Sucesso · precisão diária", o trecho sem 15m no detalhe e uma nota do lote dizendo quantos ativos rodaram assim. A marca MUST seguir para o favorito.

#### Scenario: NVDA todo o histórico
- **WHEN** NVDA roda em 1d, todo o histórico, com intrabar, e o 15m só começa em 19 mai. 2026
- **THEN** NVDA MUST ficar "Sucesso · precisão diária" com "sem 15m de 11 nov. 2014 a 18 mai. 2026"

### Requirement: Mesma amostra por ativo
Cada ativo SHALL ser lido do provedor uma vez por execução e congelado numa amostra no começo da otimização; todas as tentativas daquele ativo MUST ler só dessa amostra, sem nova ida à Binance. A amostra (`snapshot_id`) MUST ficar no resultado e no favorito.

#### Scenario: Tentativas sem nova coleta
- **WHEN** o lote otimiza NVDA com 60 tentativas
- **THEN** o histórico de NVDA MUST ser lido do provedor uma vez e todas as tentativas MUST usar o mesmo `snapshot_id`

### Requirement: Pausar, Retomar e Encerrar duráveis
Pausar e Encerrar SHALL valer ao fim da etapa em curso (coleta ou otimização do ativo atual), com "Pausando…" enquanto isso; durante "Pausando…" os botões MUST ficar `aria-disabled` e focáveis, sem tirar o foco do usuário, e depois de Encerrar o foco MUST ir ao título do lote. Pausado MUST mostrar "Retomar" e "Encerrar"; Retomar MUST continuar o mesmo lote (mesmo id) do próximo passo, sem refazer ativos concluídos. Encerrar MUST manter os favoritos já gravados e marcar os restantes "Não rodou". O estado do lote e dos ativos MUST ser durável (sem expirar enquanto pausado) e o lote em andamento ou pausado do usuário MUST reaparecer ao reabrir o Combo ou a Otimização.

#### Scenario: Pausa e retomada
- **WHEN** Alan pausa durante a coleta de SPY e depois retoma
- **THEN** a coleta de SPY MUST terminar antes de pausar, BTC/USDT e NVDA MUST seguir com os seus resultados, e Retomar MUST otimizar SPY no mesmo lote, sem coletar de novo

#### Scenario: Encerrar
- **WHEN** Alan encerra o lote depois de BTC/USDT
- **THEN** o favorito de BTC/USDT MUST ficar e NVDA e SPY MUST ficar "Não rodou"

#### Scenario: Lote pausado bloqueia um lote novo
- **WHEN** há um lote pausado (7f3c2a91) e Alan clica em Otimizar no Combo ou em Run Optimization na Otimização
- **THEN** a tela MUST NOT abrir o Confirmar de um lote novo e MUST mostrar "Retome ou encerre o lote 7f3c2a91 antes de começar outro." com "Retomar o lote 7f3c2a91", "Encerrar o lote 7f3c2a91" e "Voltar"
- **AND** `POST /api/combos/backtest/batch` e `/preview` MUST recusar um lote novo com 409 enquanto o lote pausado existir
- **AND** depois de retomar até o fim ou encerrar o lote pausado, rodar MUST abrir o Confirmar de novo

#### Scenario: Reabrir a página
- **WHEN** Alan sai do Combo com um lote pausado e volta
- **THEN** o painel do lote pausado MUST reaparecer com os estados por ativo e "Retomar"

### Requirement: Resultado do lote vira favorito em qualquer classe
O melhor resultado de cada ativo com sucesso SHALL ser gravado como favorito, em qualquer classe, **sem estrela** (`tier` nulo; decisão 4 de Alan, 27/10/2026), com a nota "gerado em lote (<id8>)" e `notify_telegram = true` (o alerta só vale depois que o dono der a estrela), sem sobrescrever favorito existente com a mesma configuração. O favorito fica em Favoritos, fora do Monitor e sem alerta, até ganhar estrela. O favorito MUST guardar:
- `asset` (símbolo, id, classe, nome, moeda);
- a configuração (fonte, sessão, ajuste);
- `execution` (precisão pedida e efetiva, trecho sem intradiário, janela pedida e coberta);
- `conventions`;
- `data_provenance`, com o `snapshot_id`.

#### Scenario: Lote grava NVDA
- **WHEN** NVDA termina com sucesso no lote 7f3c2a91
- **THEN** um favorito de NVDA MUST ser gravado com a nota "gerado em lote (7f3c2a91)", sem estrela, classe Ação, moeda USD, configuração Binance Ações, precisão diária e janela efetiva
- **AND** ele MUST NOT aparecer no Monitor nem gerar alerta até o dono dar a estrela

#### Scenario: Lote grava cripto
- **WHEN** BTC/USDT termina com sucesso no mesmo lote
- **THEN** o favorito de BTC/USDT MUST também ser gravado sem estrela

### Requirement: Fim do lote leva aos resultados
Ao concluir, pausar ou encerrar, o painel SHALL mostrar o resumo (concluídos, favoritos gravados, quantos em precisão diária, quantos sem resultado válido) e o link "Ver os N resultados do lote em Favoritos" ("Ver o resultado do lote em Favoritos" com 1) para `/favorites?lote=<id8>`.

#### Scenario: Lote concluído
- **WHEN** o lote 7f3c2a91 termina com 3 sucessos
- **THEN** o link MUST abrir `/favorites?lote=7f3c2a91`

