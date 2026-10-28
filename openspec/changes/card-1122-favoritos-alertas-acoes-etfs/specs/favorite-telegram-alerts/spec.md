## ADDED Requirements

### Requirement: Alertas saem das estratégias que cada usuário acompanha no Monitor
A varredura do Telegram SHALL avaliar, para cada usuário ativo com Telegram vinculado e alertas ligados no Perfil, só os favoritos de que ele é dono, com pelo menos 1 estrela (`tier` 1, 2 ou 3) e com o alerta ligado (`notify_telegram = true`), em cripto, ação e ETF (decisão de Alan de 27/10/2026: alerta = o que a pessoa monitora). Favorito sem estrela MUST NOT gerar alerta, mesmo com o alerta ligado. O catálogo do Cripto Farol (vitrine) MUST NOT gerar alerta para ninguém além do dono do favorito, inclusive quando quem não é admin deu estrela a uma linha do catálogo. O filtro de estrelas do sistema (`monitor_telegram_tier_filter`) MUST NOT mudar quem recebe; quando estiver preenchido, a varredura o ignora e o registra no resumo. Cada usuário MUST receber só os alertas dos próprios favoritos.

#### Scenario: Só o dono recebe
- **WHEN** o usuário A tem um favorito de NVDA e outro de BTC/USDT, os dois com estrela e alerta ligado
- **AND** o usuário B não tem esses favoritos
- **AND** a leitura dos dois favoritos muda num candle fechado
- **THEN** A MUST receber os dois alertas
- **AND** B MUST NOT receber alerta de NVDA nem de BTC/USDT

#### Scenario: Favorito sem estrela não alerta
- **WHEN** um favorito de QQQ gravado pelo lote está sem estrela e com o alerta ligado
- **AND** a leitura dele muda
- **THEN** nenhum alerta MUST sair

#### Scenario: Alerta desligado não alerta
- **WHEN** o dono desligou no Monitor o alerta do favorito de ETH/USDT 4h, que tem 2 estrelas
- **AND** a leitura dele muda
- **THEN** nenhum alerta desse favorito MUST sair

#### Scenario: Catálogo não alerta
- **WHEN** o usuário C, sem estratégia própria com estrela, vê o catálogo no Monitor e deu 1 estrela à linha de ETH/USDT do catálogo
- **AND** a leitura dessa linha muda
- **THEN** C MUST NOT receber alerta
- **AND** o dono do favorito do catálogo MUST receber só se o favorito dele tiver estrela e alerta ligado

#### Scenario: Filtro de estrelas do sistema preenchido
- **WHEN** `monitor_telegram_tier_filter` vale `1`
- **AND** um favorito com 1 estrela (`tier = 3`) e alerta ligado muda de leitura
- **THEN** o dono MUST receber o alerta
- **AND** o resumo da varredura MUST registrar que o filtro foi ignorado

### Requirement: Alerta ligado por padrão, desligado por estratégia no Monitor
O alerta de um favorito SHALL nascer ligado (`notify_telegram = true`) em todo caminho de criação (resultado, lote, Descoberta). Dar a primeira estrela a um favorito sem estrela MUST ligar o alerta dele na mesma gravação. Trocar entre 1, 2 e 3 estrelas MUST NOT mudar o alerta. Tirar todas as estrelas MUST tirar o favorito do Monitor e da varredura. Só o dono MUST poder ligar ou desligar o alerta, pelo Monitor (`monitor-multiclass`); Favoritos MUST NOT ter controle de alerta.

#### Scenario: Dar a estrela liga o alerta
- **WHEN** o dono dá 1 estrela ao favorito de QQQ, sem estrela e com o alerta desligado
- **THEN** o favorito MUST ficar com `tier = 3` e `notify_telegram = true`
- **AND** MUST aparecer no Monitor com o alerta ligado

#### Scenario: Subir de 1 para 2 estrelas
- **WHEN** o dono sobe de 1 para 2 estrelas um favorito com o alerta desligado
- **THEN** o alerta MUST continuar desligado

#### Scenario: Tirar todas as estrelas
- **WHEN** o dono tira as estrelas do favorito de SPY
- **THEN** SPY MUST sair do Monitor
- **AND** nenhum alerta de SPY MUST sair até ele ganhar estrela de novo, e então volta ligado

### Requirement: Estado e alerta por favorito
O estado observado SHALL ser guardado por favorito: leitura pública (`HOLD`/`EXIT`), candle fechado que a produziu e o horário da observação. Dois favoritos no mesmo ativo e tempo gráfico, com estratégias ou configurações diferentes, MUST ter estados separados. Cada mudança MUST gerar o próprio alerta. A primeira observação de um favorito que passa a alertar (estrela dada, alerta religado ou favorito novo) MUST só gravar a base, sem alerta. Apagar o favorito MUST apagar o estado dele.

#### Scenario: Mesmo ativo, configurações distintas
- **WHEN** o usuário tem NVDA 1d `multi_ma_crossover` na Binance Ações e NVDA 1d `multi_ma_crossover` na fonte antiga, os dois com estrela e alerta ligado
- **AND** só a leitura do favorito da Binance muda de Venda para Compra
- **THEN** o usuário MUST receber um alerta, que identifica a configuração Binance Ações
- **AND** o estado do favorito da fonte antiga MUST continuar o mesmo

#### Scenario: Duas estratégias mudam juntas
- **WHEN** dois favoritos de BTC/USDT 1d com estratégias diferentes, os dois com estrela e alerta ligado, mudam de leitura no mesmo candle
- **THEN** o dono MUST receber dois alertas, um por favorito, cada um com a sua estratégia

#### Scenario: Primeira leitura depois da estrela
- **WHEN** a varredura lê pela primeira vez um favorito que acabou de ganhar estrela
- **THEN** o estado MUST ser gravado como base e nenhum alerta MUST sair

### Requirement: Evento com identidade, sem duplicar no reinício
Cada alerta de sinal SHALL ter a chave de evento formada pelo usuário, pelo favorito, pela leitura nova e pelo início do candle fechado que a produziu. O envio MUST reservar o evento antes de chamar o Telegram (estado `sending`), e uma chave já reservada, enviada ou em dry-run MUST NOT ser enviada de novo. Reinício, reprocessamento, varredura concorrente ou nova varredura com o mesmo dado MUST NOT duplicar o evento. Uma reserva que ficou em `sending` depois de uma queda MUST virar `unknown` e MUST NOT ser reenviada. Um envio que falhou antes de o Telegram aceitar (`failed`) MUST ser tentado de novo na próxima varredura, enquanto o evento ainda for o atual. A janela de repetição por tempo (`monitor_telegram_min_repeat_minutes`) MUST NOT decidir duplicata.

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
Alertas de sinal e avisos de atraso da varredura SHALL sair cada um como uma mensagem própria, sem passar pelo limite de mensagens por usuário e janela (`monitor_telegram_rate_limit_count`, `monitor_telegram_rate_limit_window_minutes`); a chave do evento é o que impede repetição (decisão 4 de Alan, 26/10/2026). O resumo da varredura MUST NOT ter `rate_limited` para alerta de sinal nem para aviso de atraso.

#### Scenario: Sete favoritos mudam no mesmo dia
- **WHEN** sete favoritos de um usuário, com estrela e alerta ligado, mudam de leitura no mesmo candle
- **AND** o limite configurado é de 5 mensagens por 60 minutos
- **THEN** a varredura MUST mandar sete mensagens a esse usuário, uma por favorito
- **AND** nenhuma delas MUST ficar como `rate_limited`

### Requirement: Entrada e saída saem com ou sem o ativo na carteira
A carteira SHALL NOT decidir quem recebe (decisão de Alan de 27/10/2026), em cripto, ação e ETF. Toda mudança de leitura de um favorito que alerta MUST sair: `EXIT`→`HOLD` como entrada (Compra) e `HOLD`→`EXIT` como saída (Venda, com `Motivo=Stop` quando a saída é por stop). Nenhuma das duas MUST depender da marca "No portfólio", do saldo na carteira Binance ou de posição real. A cripto MUST NOT ter mais a supressão da reentrada com saldo nem a da saída sem saldo. A varredura MUST NOT ler a carteira Binance para decidir alerta.

#### Scenario: Entrada de NVDA fora da carteira
- **WHEN** NVDA não está marcada na carteira do usuário
- **AND** o favorito de NVDA dele, com estrela e alerta ligado, vai de Venda para Compra
- **THEN** o usuário MUST receber o alerta de Compra

#### Scenario: Saída de SPY
- **WHEN** o favorito de SPY, com estrela e alerta ligado, vai de Compra para Venda
- **THEN** o usuário MUST receber o alerta de Venda, com SPY na carteira ou fora dela

#### Scenario: Cripto com saldo recebe a reentrada
- **WHEN** o usuário tem saldo de BTC na Binance
- **AND** o favorito de BTC/USDT dele vai de Venda para Compra
- **THEN** o usuário MUST receber o alerta de Compra

#### Scenario: Cripto sem saldo recebe a saída
- **WHEN** o usuário não tem saldo de SOL
- **AND** o favorito de SOL/USDT dele vai de Compra para Venda
- **THEN** o usuário MUST receber o alerta de Venda

### Requirement: Carteira Binance fora da varredura
A varredura SHALL NOT buscar a carteira Binance para decidir alertas. Uma falha da carteira Binance MUST NOT pausar alerta de ninguém e MUST NOT gerar o aviso operacional "carteira indisponível". O Monitor MAY continuar mostrando o estado da carteira.

#### Scenario: Binance fora do ar na varredura
- **WHEN** a carteira Binance do usuário está indisponível no momento da varredura
- **AND** os favoritos de BTC/USDT e NVDA dele, com estrela e alerta ligado, mudam de leitura
- **THEN** o usuário MUST receber os dois alertas
- **AND** MUST NOT receber aviso operacional da carteira

### Requirement: Mensagem identifica estratégia e configuração e não é ordem
A mensagem de sinal SHALL trazer:
- o ativo com classe e moeda;
- a estratégia;
- a configuração (fonte, sessão e ajuste, no rótulo de `favorite-configuration-identity`);
- o tempo gráfico, a leitura anterior e a leitura atual;
- a data do candle fechado, o valor de entrada e o stop na moeda do ativo;
- a linha "Este alerta não envia ordem: é só o sinal da estratégia.";
- como parar de receber: "Para não receber mais desta estratégia: desligue o "Alerta" dela no Monitor ou tire a estrela em Favoritos.";
- o aviso educacional de hoje.

Favoritar ou receber alerta MUST NOT enviar ordem. Uma ordem ou execução que exista depois (Operar da cripto, histórias de operação) MUST aparecer pelos registros próprios dela e MUST NOT ser anunciada como alerta de sinal.

#### Scenario: Alerta de NVDA
- **WHEN** o alerta de entrada de NVDA 1d sai
- **THEN** a mensagem MUST conter "NVDA (Ação · USD)", o nome da estratégia, "Binance Ações · pregão regular de NY · ajustado por split", "1d", "Leitura anterior: Venda", "Leitura atual: Compra", a data do pregão, "Este alerta não envia ordem: é só o sinal da estratégia." e como desligar o "Alerta" no Monitor

#### Scenario: Nenhuma ordem
- **WHEN** um alerta sai ou um favorito é criado
- **THEN** nenhuma ordem MUST ser criada em `monitor_spot_order_requests` nem em outro lugar

### Requirement: Aviso único de atraso real
Quando um ativo acompanhado tem atraso real de dado (`market-session-awareness`), a varredura SHALL mandar um único aviso por ativo e episódio de atraso a cada usuário que tem o ativo no Monitor com alerta ligado: dono de pelo menos um favorito do ativo com estrela e `notify_telegram = true`. A carteira MUST NOT decidir quem recebe o aviso. O aviso MUST dizer:
- o ativo e a fonte;
- o último candle recebido e o esperado, da série atrasada, com o tempo gráfico dela;
- que os sinais do ativo ficam em espera até o dado normalizar;
- como parar de receber os avisos do ativo (desligar o "Alerta" das estratégias dele no Monitor).

O aviso MUST NOT se repetir enquanto o episódio durar, mesmo com vários tempos gráficos ou favoritos do mesmo ativo. Enquanto o ativo está atrasado, os favoritos dele MUST NOT gerar alerta de sinal a partir de dado incompleto. Quando o dado normaliza, o episódio MUST fechar sem mensagem, e o próximo atraso MUST abrir um episódio novo. Tempo esgotado da coleta local MUST NOT abrir episódio nem gerar aviso.

#### Scenario: Atraso de NVDA na terça
- **WHEN** a varredura de terça às 08:05 BRT não encontra o candle 1d de segunda de NVDA, que já fechou pelo calendário
- **THEN** o dono de favorito de NVDA com estrela e alerta ligado MUST receber um aviso "Dados atrasados" de NVDA, com NVDA na carteira ou fora dela
- **AND** nenhum alerta de sinal de NVDA MUST sair nessa varredura

#### Scenario: Alerta desligado não recebe o aviso
- **WHEN** NVDA está atrasada e todos os favoritos de NVDA do usuário estão com o alerta desligado
- **THEN** ele MUST NOT receber o aviso

#### Scenario: Atraso continua
- **WHEN** a varredura de quarta ainda não encontra o candle de segunda
- **THEN** nenhum aviso novo de NVDA MUST sair

#### Scenario: Cripto atrasada
- **WHEN** a varredura de domingo às 08:05 BRT não encontra o candle 1d de sábado de BTC/USDT, que fechou às 21:00 BRT de sábado
- **THEN** o dono de favorito de BTC/USDT com estrela e alerta ligado MUST receber um aviso "Dados atrasados" de BTC/USDT
- **AND** nenhum alerta de sinal de BTC/USDT MUST sair nessa varredura

#### Scenario: Atraso de outro tempo gráfico
- **WHEN** o 15m de NVDA está atrasado e o 1d de NVDA está em dia
- **THEN** o aviso MUST trazer o último e o esperado do 15m, com "(15m)", nunca "(1d)"

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

### Requirement: Transição de quem recebia pelo catálogo
Na troca, os usuários que recebiam alerta de cripto pelo catálogo curado SHALL deixar de recebê-los, sem período de transição (decisão 1 de Alan, 26/10/2026; o catálogo não alerta, 27/10/2026). "Recebia pelo catálogo" é ter pelo menos um alerta do catálogo enviado (`sent`) em `monitor_telegram_alerts` antes da troca. Cada um deles que não tem estratégia própria com estrela e alerta ligado MUST receber, na primeira varredura depois da troca, um único aviso "Mudança nos alertas" no Telegram, com os ativos que recebia e como voltar a receber (salvar nos Favoritos e dar pelo menos 1 estrela), com chave de evento própria (`transition`, uma por usuário). Quem nunca recebeu alerta do catálogo MUST NOT receber esse aviso. A marca de que a varredura da troca já rodou MUST ser gravada só numa varredura sem dry-run em que nenhuma entrega de transição terminou `failed`; em dry-run, nem a marca nem a reserva da chave `transition` MUST ser gravadas. A faixa do Monitor segue `monitor-multiclass`.

#### Scenario: Usuário só do catálogo
- **WHEN** um usuário com Telegram ligado recebeu alertas do catálogo antes da troca e não tem estratégia própria com estrela e alerta ligado
- **THEN** na primeira varredura depois da troca ele MUST receber um aviso "Mudança nos alertas"
- **AND** MUST NOT receber alerta de sinal do catálogo
- **AND** as varreduras seguintes MUST NOT repetir o aviso

#### Scenario: Usuário que nunca recebeu
- **WHEN** um usuário com Telegram ligado nunca recebeu alerta do catálogo
- **THEN** ele MUST NOT receber o aviso "Mudança nos alertas"

#### Scenario: Ensaio em dry-run
- **WHEN** a primeira varredura depois da troca roda em dry-run
- **THEN** a marca da varredura da troca MUST NOT ser gravada
- **AND** a varredura real seguinte, dentro da janela, MUST mandar o aviso

#### Scenario: Entrega falhou
- **WHEN** o aviso de transição de um usuário termina `failed`
- **THEN** a marca da varredura da troca MUST NOT ser gravada
- **AND** a varredura seguinte, dentro da janela, MUST tentar de novo só quem não recebeu
