## ADDED Requirements

### Requirement: Catálogo cobre cripto spot USDT, ações e ETFs da Binance

O sistema SHALL manter um catálogo único de ativos Binance com três classes: cripto (todos os pares spot cotados em USDT), ação e ETF (todos os instrumentos de ações e ETFs que a Binance oferece). O catálogo MUST NOT incluir pares cripto cotados em outras moedas (BTC, USDC, EUR e demais), direitos de subscrição (RIGHT) nem derivativos. Os exemplos NVDA, SPY e QQQ servem só para verificação e MUST NOT limitar o escopo.

#### Scenario: Exemplos de verificação estão no catálogo

- **WHEN** o catálogo foi atualizado com sucesso
- **THEN** BTC/USDT aparece com classe cripto, NVDA com classe ação, e SPY e QQQ com classe ETF

#### Scenario: Par fora de USDT não entra

- **WHEN** a Binance lista ETH/BTC ou BTC/USDC
- **THEN** esses pares não aparecem no catálogo

#### Scenario: RIGHT e derivativos ficam fora

- **WHEN** a origem de ações traz um instrumento do tipo RIGHT, um warrant ou um direito de valor contingente
- **THEN** o instrumento não aparece no catálogo
- **AND** entra na contagem de excluídos da atualização, com o motivo da exclusão

### Requirement: Reconciliação por identificador entre catálogo estático e regras de negociação

Para ações e ETFs, o sistema SHALL juntar o catálogo estático (nome, classe) e as regras de negociação (estado de negociação) pelo identificador do instrumento na Binance, nunca pela posição na lista nem pelo nome. As contagens SHALL ser verificáveis: a quantidade de ações e ETFs disponíveis para escolha MUST ser igual à união reconciliada menos os excluídos, e cada atualização MUST registrar as contagens de entrada, de excluídos (por motivo) e o resultado por classe.

#### Scenario: Instrumento só no catálogo estático

- **WHEN** um instrumento existe no catálogo estático e não existe nas regras de negociação
- **THEN** ele aparece no catálogo marcado como sem regras de negociação, com esse motivo

#### Scenario: Contagem confere com a Binance

- **WHEN** uma atualização termina com sucesso
- **THEN** o total de ações e ETFs disponíveis para escolha é igual à união reconciliada menos os excluídos registrados nessa atualização

#### Scenario: Limite de ingestão não trunca o catálogo

- **WHEN** a ingestão de candles está configurada com limite de símbolos por rodada
- **THEN** o catálogo e a pesquisa continuam com todos os ativos, sem efeito desse limite

### Requirement: Listagem, negociação e histórico são informações separadas

Cada ativo do catálogo SHALL expor separadamente: (1) se está listado no catálogo atual da Binance; (2) o estado de negociação, com motivo quando não negociável; (3) a disponibilidade de histórico. A presença no catálogo MUST NOT ser apresentada como autorização de negociação nem como disponibilidade da conta, que pertencem à história de ordens.

#### Scenario: Ação sem histórico coletado

- **WHEN** o usuário vê NVDA no catálogo
- **THEN** o estado de negociação e a disponibilidade de histórico aparecem como informações distintas
- **AND** a falta de histórico coletado não é mostrada como suspensão nem como erro

#### Scenario: Presença não autoriza ordem

- **WHEN** um ativo aparece como negociável
- **THEN** nada no catálogo afirma que a conta do usuário pode negociá-lo

### Requirement: Estados marcados de ativo suspenso ou removido

O sistema SHALL marcar com estado e motivo todo ativo não negociável: suspenso ou pausado pela Binance, fora de mercado, sem negociação, sem regras de negociação ou removido (deixou de constar no catálogo atual). Ativo marcado MUST continuar no catálogo e na pesquisa, para explicar resultados e favoritos antigos. Ele MUST NOT poder ser escolhido para análise nova, nem item a item nem por "Todos" ou outra ação de lote, e as análises novas (otimização, lote e varredura da Descoberta) MUST recusá-lo ou excluí-lo com o estado e o motivo.

#### Scenario: Par cripto sai da Binance

- **WHEN** um par USDT que estava no catálogo deixa de aparecer na lista spot da Binance
- **THEN** ele continua no catálogo com estado removido e a data em que deixou de aparecer

#### Scenario: Ação fora de mercado

- **WHEN** as regras de negociação marcam uma ação como fora de mercado
- **THEN** ela aparece na pesquisa com estado fora de mercado e motivo legível
- **AND** não pode ser escolhida para análise nova

#### Scenario: Análise nova com ativo marcado

- **WHEN** uma otimização, um lote ou uma varredura recebe um ativo suspenso, fora de mercado, sem negociação, sem regras ou removido
- **THEN** o sistema não executa a análise para esse ativo
- **AND** informa o estado e o motivo

### Requirement: Identidade estável de ativo

Cada ativo SHALL ter um identificador estável que combina origem, mercado e o identificador da Binance, e que não muda com nome, ordem ou estado. Favoritos e resultados antigos de cripto (símbolo com `/`) SHALL apontar para o ativo cripto correspondente. O sistema MUST NOT associar um registro antigo a ação ou ETF por semelhança de ticker, nem confundir ação, token ou símbolo parecido.

#### Scenario: Favorito antigo de par removido

- **WHEN** um favorito antigo usa um par USDT que saiu da Binance
- **THEN** o favorito continua apontando para o mesmo ativo, agora marcado como removido

#### Scenario: Ticker parecido não é fundido

- **WHEN** um registro antigo usa um ticker sem `/` que coincide com uma ação do catálogo
- **THEN** o registro não é associado a essa ação automaticamente

### Requirement: Falha da Binance é visível e não vira lista vazia nem fixa

Quando a atualização de uma classe falhar (rede, limite de requisições, HTTP 200 com código de erro de negócio, formato inesperado ou resultado muito menor que o anterior sem explicação), o sistema SHALL manter a última lista válida dessa classe e informar ao usuário a falha e a data da lista mostrada. Sem lista válida anterior, o sistema SHALL mostrar erro explícito dessa classe. O sistema MUST NOT trocar o catálogo por lista vazia nem por lista fixa de poucos ativos.

#### Scenario: Falha com lista anterior

- **WHEN** a atualização de ações e ETFs falha e existe uma lista válida anterior
- **THEN** a pesquisa continua com a lista anterior
- **AND** a tela informa que a Binance não respondeu e de quando é a lista mostrada

#### Scenario: Falha sem lista anterior

- **WHEN** a atualização de uma classe falha e não há lista válida anterior
- **THEN** a tela informa que aquela classe está indisponível e oferece tentar de novo
- **AND** nenhum ativo fixo aparece no lugar

#### Scenario: Universo de ingestão sem fallback fixo

- **WHEN** a lista spot da Binance e o catálogo salvo estão indisponíveis
- **THEN** a ingestão de candles registra a falha e não roda com uma lista fixa de 5 pares
