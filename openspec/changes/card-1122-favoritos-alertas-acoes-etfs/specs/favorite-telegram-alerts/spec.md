## ADDED Requirements

### Requirement: Alertas saem dos favoritos de cada usuário
A varredura do Telegram SHALL avaliar, para cada usuário ativo com Telegram vinculado e alertas ligados, só os favoritos de que ele é dono e que estão marcados "Alertar" (`notify_telegram = true`), em cripto, ação e ETF. O catálogo curado do admin MUST NOT ser origem de alerta para outro usuário. O filtro de estrelas do sistema (`monitor_telegram_tier_filter`) MUST continuar valendo sobre o nível do próprio favorito. Cada usuário MUST receber só os alertas dos próprios favoritos.

#### Scenario: Só quem marcou recebe
- **WHEN** o usuário A marcou "Alertar" num favorito de NVDA e noutro de BTC/USDT, ambos na carteira de A
- **AND** o usuário B não tem esses favoritos
- **AND** a leitura dos dois favoritos muda num candle fechado
- **THEN** A MUST receber os dois alertas
- **AND** B MUST NOT receber alerta de NVDA nem de BTC/USDT

#### Scenario: Favorito do catálogo não alerta outro usuário
- **WHEN** o admin marcou "Alertar" num favorito dele de ETH/USDT
- **AND** o usuário C vê esse favorito só pela vitrine do catálogo no Monitor
- **THEN** C MUST NOT receber alerta desse favorito
- **AND** o admin MUST receber, se ETH/USDT estiver na carteira dele

#### Scenario: Favorito sem a marca não alerta
- **WHEN** um favorito do usuário A tem `notify_telegram = false`
- **THEN** a varredura MUST NOT gerar alerta desse favorito para ninguém

### Requirement: Estado e alerta por favorito
O estado observado SHALL ser guardado por favorito: leitura pública (`HOLD`/`EXIT`), candle fechado que a produziu e o horário da observação. Dois favoritos no mesmo ativo e tempo gráfico, com estratégias ou configurações diferentes, MUST ter estados separados. Cada mudança MUST gerar o próprio alerta. A primeira observação de um favorito MUST só gravar a base, sem alerta. Apagar o favorito MUST apagar o estado dele.

#### Scenario: Mesmo ativo, configurações distintas
- **WHEN** o usuário tem NVDA 1d `multi_ma_crossover` na Binance Ações e NVDA 1d `multi_ma_crossover` na fonte antiga, os dois marcados "Alertar" e NVDA na carteira
- **AND** só a leitura do favorito da Binance muda de Venda para Compra
- **THEN** o usuário MUST receber um alerta, que identifica a configuração Binance Ações
- **AND** o estado do favorito da fonte antiga MUST continuar o mesmo

#### Scenario: Duas estratégias mudam juntas
- **WHEN** dois favoritos de BTC/USDT 1d com estratégias diferentes mudam de leitura no mesmo candle
- **THEN** o dono MUST receber dois alertas, um por favorito, cada um com a sua estratégia

#### Scenario: Favorito novo não dispara na primeira leitura
- **WHEN** a varredura lê pela primeira vez um favorito recém-marcado
- **THEN** o estado MUST ser gravado como base e nenhum alerta MUST sair

### Requirement: Evento com identidade, sem duplicar no reinício
Cada alerta de sinal SHALL ter a chave de evento formada pelo usuário, pelo favorito, pela leitura nova e pelo início do candle fechado que a produziu. O envio MUST reservar o evento antes de chamar o Telegram (estado `sending`), e uma chave já reservada, enviada ou em dry-run MUST NOT ser enviada de novo. Reinício, reprocessamento, varredura concorrente ou nova varredura com o mesmo dado MUST NOT duplicar o evento. Uma reserva que ficou em `sending` depois de uma queda MUST virar `unknown` e MUST NOT ser reenviada. Um envio que falhou antes de o Telegram aceitar (`failed`) MUST ser tentado de novo na próxima varredura, enquanto o evento ainda for o atual. A janela de repetição por tempo (`monitor_telegram_min_repeat_minutes`) MUST deixar de decidir duplicata.

#### Scenario: Varredura repetida
- **WHEN** a varredura roda duas vezes seguidas com o mesmo candle fechado de NVDA
- **THEN** o alerta de NVDA MUST sair uma vez só

#### Scenario: Queda no meio do envio
- **WHEN** o processo cai depois de reservar o evento e antes de gravar o resultado
- **THEN** a próxima varredura MUST marcar o evento como `unknown`
- **AND** MUST NOT reenviá-lo

#### Scenario: Volta legítima à mesma leitura
- **WHEN** um favorito vai de Venda para Compra num candle, de Compra para Venda noutro e de Venda para Compra num terceiro
- **THEN** cada mudança MUST gerar o seu alerta, porque os candles são diferentes

### Requirement: Varredura sem limite de mensagens por hora
Alertas de sinal e avisos de atraso da varredura SHALL sair cada um como uma mensagem própria, sem passar pelo limite de mensagens por usuário e janela (`monitor_telegram_rate_limit_count`, `monitor_telegram_rate_limit_window_minutes`); a chave do evento é o que impede repetição (decisão 4 de Alan, 26/10/2026). O limite configurável MUST continuar valendo só para o aviso operacional de falha da carteira Binance. O resumo da varredura MUST NOT ter `rate_limited` para alerta de sinal nem para aviso de atraso.

#### Scenario: Sete favoritos mudam no mesmo dia
- **WHEN** sete favoritos marcados "Alertar" de um usuário, com os ativos na carteira, mudam de leitura no mesmo candle
- **AND** o limite configurado é de 5 mensagens por 60 minutos
- **THEN** a varredura MUST mandar sete mensagens a esse usuário, uma por favorito
- **AND** nenhuma delas MUST ficar como `rate_limited`

#### Scenario: Limite só no aviso de falha da carteira
- **WHEN** a carteira Binance do usuário falha em duas varreduras dentro da janela do limite
- **THEN** só um aviso operacional de falha MUST sair nessa janela

### Requirement: Entrada e saída de ação e ETF na carteira
Para ação e ETF, a carteira SHALL ser a marcação manual do usuário (`MonitorPreference.in_portfolio`). Com o ativo marcado na carteira, a entrada (`EXIT`→`HOLD`) e a saída (`HOLD`→`EXIT`) MUST sair. Nenhuma das duas MUST depender de posição na Binance. Sem a marca na carteira, o favorito de ação ou ETF MUST NOT gerar alerta. A cripto MUST manter a matriz de hoje: posição derivada da carteira Binance quando houver credencial; sem credencial, a marca manual com só a entrada. Quando a posição real de ação/ETF existir (#1124), a regra de ação/ETF MUST passar a seguir a posição, como na cripto.

#### Scenario: Saída de NVDA na carteira
- **WHEN** NVDA está marcada na carteira do usuário e o favorito marcado muda de Compra para Venda
- **THEN** o usuário MUST receber o alerta de Venda

#### Scenario: Entrada de SPY na carteira
- **WHEN** SPY está marcado na carteira e o favorito muda de Venda para Compra
- **THEN** o usuário MUST receber o alerta de Compra

#### Scenario: Ação fora da carteira
- **WHEN** NVDA não está marcada na carteira do usuário
- **THEN** nenhum alerta de NVDA MUST sair para ele

#### Scenario: Cripto sem mudança
- **WHEN** o usuário tem BTC/USDT, credencial Binance e nenhuma posição de BTC
- **THEN** a matriz de hoje MUST decidir o alerta de BTC/USDT, sem mudança

### Requirement: Mensagem identifica estratégia e configuração e não é ordem
A mensagem de sinal SHALL trazer:
- o ativo com classe e moeda;
- a estratégia;
- a configuração (fonte, sessão e ajuste, no rótulo de `favorite-configuration-identity`);
- o tempo gráfico, a leitura anterior e a leitura atual;
- a data do candle fechado, o valor de entrada e o stop na moeda do ativo;
- a linha "Este alerta não envia ordem: é só o sinal da estratégia.";
- o aviso educacional de hoje.

Favoritar ou receber alerta MUST NOT enviar ordem. Uma ordem ou execução que exista depois (Operar da cripto, histórias de operação) MUST aparecer pelos registros próprios dela e MUST NOT ser anunciada como alerta de sinal.

#### Scenario: Alerta de NVDA
- **WHEN** o alerta de entrada de NVDA 1d sai
- **THEN** a mensagem MUST conter "NVDA (Ação · USD)", o nome da estratégia, "Binance Ações · pregão regular de NY · ajustado por split", "1d", "Leitura anterior: Venda", "Leitura atual: Compra", a data do pregão e "Este alerta não envia ordem: é só o sinal da estratégia."

#### Scenario: Nenhuma ordem
- **WHEN** um alerta sai ou um favorito é criado
- **THEN** nenhuma ordem MUST ser criada em `monitor_spot_order_requests` nem em outro lugar

### Requirement: Aviso único de atraso real
Quando um ativo monitorado tem atraso real de dado (`market-session-awareness`: falta o candle de um pregão ou bloco que o calendário diz que já fechou, detectado na varredura seguinte mesmo com o mercado fechado), a varredura SHALL mandar um único aviso por ativo e episódio de atraso a cada usuário que receberia alerta daquele ativo, ou seja, que tem um favorito dele marcado "Alertar", com o ativo na carteira. O aviso MUST dizer:
- o ativo e a fonte;
- o último candle recebido e o esperado;
- que os sinais do ativo ficam em espera até o dado normalizar.

O aviso MUST NOT se repetir enquanto o episódio durar, mesmo com vários tempos gráficos ou favoritos do mesmo ativo. Enquanto o ativo está atrasado, os favoritos dele MUST NOT gerar alerta de sinal a partir de dado incompleto. Quando o dado normaliza, o episódio MUST fechar sem mensagem, e o próximo atraso MUST abrir um episódio novo.

#### Scenario: Atraso de NVDA na terça
- **WHEN** a varredura de terça às 08:05 BRT não encontra o candle 1d de segunda de NVDA, que já fechou pelo calendário
- **THEN** o dono de favorito marcado de NVDA, com NVDA na carteira, MUST receber um aviso "Dados atrasados" de NVDA
- **AND** nenhum alerta de sinal de NVDA MUST sair nessa varredura

#### Scenario: Atraso continua
- **WHEN** a varredura de quarta ainda não encontra o candle de segunda
- **THEN** nenhum aviso novo de NVDA MUST sair

#### Scenario: Cripto atrasada
- **WHEN** a varredura de domingo às 08:05 BRT não encontra o candle 1d de sábado de BTC/USDT, que fechou às 21:00 BRT de sábado
- **THEN** o dono de favorito marcado de BTC/USDT, no escopo da carteira, MUST receber um aviso "Dados atrasados" de BTC/USDT
- **AND** nenhum alerta de sinal de BTC/USDT MUST sair nessa varredura

#### Scenario: Recuperação
- **WHEN** o candle chega e a varredura seguinte lê a série completa
- **THEN** o episódio MUST fechar sem mensagem no Telegram
- **AND** se a leitura do favorito mudou, o alerta de sinal MUST sair, com a data do candle que a produziu

### Requirement: Mercado fechado só na tela
Mercado fechado, fora do pregão, fim de semana, feriado e abertura MUST NOT gerar mensagem no Telegram. Esses estados SHALL aparecer só no Monitor (`monitor-multiclass`).

#### Scenario: Sábado
- **WHEN** a varredura de sábado às 08:05 BRT lê NVDA, com o último candle de sexta
- **THEN** nenhum aviso de atraso nem mensagem de mercado fechado MUST sair

#### Scenario: Feriado
- **WHEN** a varredura roda no dia seguinte a um feriado de Nova York
- **THEN** a falta do candle do feriado MUST NOT virar atraso

### Requirement: Falha da carteira Binance pausa só a cripto
Quando a sincronização da carteira Binance de um usuário falha, a varredura SHALL pausar só os alertas de cripto que dependem da posição desse usuário e mandar o aviso operacional de hoje, com limite por usuário. O aviso MUST dizer que os alertas de cripto estão pausados e que ações e ETFs seguem. Os alertas de ação e ETF do mesmo usuário MUST continuar.

#### Scenario: Carteira fora, NVDA segue
- **WHEN** a carteira Binance do usuário falha na varredura
- **AND** o favorito marcado de NVDA, na carteira, muda de leitura
- **THEN** o usuário MUST receber o alerta de NVDA e o aviso operacional
- **AND** MUST NOT receber o alerta de BTC/USDT dessa varredura

### Requirement: Transição de quem recebia pelo catálogo
No deploy, os usuários que hoje recebem alerta de cripto pelo catálogo curado e não têm favorito próprio marcado "Alertar" SHALL deixar de recebê-los, sem período de transição (decisão 1 de Alan, 26/10/2026). "Recebia pelo catálogo" é ter pelo menos um alerta do catálogo enviado (`sent`) em `monitor_telegram_alerts` antes do deploy. Cada um deles MUST receber, no dia da troca, um único aviso "Mudança nos alertas" no Telegram, com os ativos que recebia e como voltar a receber, com chave de evento própria (`transition`, uma por usuário). Quem nunca recebeu alerta do catálogo MUST NOT receber esse aviso. A faixa do Monitor segue `monitor-multiclass`.

#### Scenario: Usuário só do catálogo
- **WHEN** um usuário com Telegram ligado recebeu alertas do catálogo antes do deploy e não tem favorito próprio marcado "Alertar"
- **THEN** na primeira varredura depois do deploy ele MUST receber um aviso "Mudança nos alertas"
- **AND** MUST NOT receber alerta de sinal
- **AND** as varreduras seguintes MUST NOT repetir o aviso

#### Scenario: Usuário que nunca recebeu
- **WHEN** um usuário com Telegram ligado nunca recebeu alerta do catálogo e não tem favorito marcado
- **THEN** ele MUST NOT receber o aviso "Mudança nos alertas"
