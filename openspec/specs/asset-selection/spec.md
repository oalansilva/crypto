# asset-selection Specification

## Purpose
TBD - created by archiving change card-1117-catalogo-ativos. Update Purpose after archive.
## Requirements
### Requirement: Mesmo seletor de ativos nas três telas

A configuração de combo (`/combo/configure`), a descoberta (`/combo/discovery`) e a otimização (`/combo/optimize`) SHALL usar o mesmo seletor de ativos, com a mesma pesquisa, o mesmo filtro por classe, a mesma paginação, a mesma seleção de vários ativos, o mesmo "Todos do filtro" e as mesmas marcas de estado. A otimização MUST NOT aceitar ativo digitado à mão.

#### Scenario: Otimização sem texto livre

- **WHEN** o usuário abre `/combo/optimize`
- **THEN** os ativos são escolhidos no seletor de catálogo
- **AND** não existe campo de texto livre para o símbolo

#### Scenario: Otimização com vários ativos

- **WHEN** o usuário marca BTC/USDT e ETH/USDT em `/combo/optimize`
- **THEN** os dois ficam selecionados
- **AND** a ação "Todos do filtro" está disponível, com a mesma contagem e confirmação das outras telas

#### Scenario: Símbolo fora do catálogo na URL

- **WHEN** `/combo/optimize?symbol=XYZ/USDT` é aberta e XYZ/USDT não está no catálogo
- **THEN** o seletor informa que o ativo não foi encontrado no catálogo
- **AND** nenhum ativo é marcado com esse texto

### Requirement: Pesquisa, filtro por classe e paginação

O seletor SHALL pesquisar por símbolo e por nome, sem diferenciar maiúsculas, minúsculas ou acentos, filtrar por classe (Todas, Cripto, Ações, ETFs) mostrando a contagem de cada uma e paginar os resultados, de modo que todo ativo do catálogo possa ser alcançado. O resultado SHALL mostrar para cada ativo símbolo, nome, classe, estado de negociação e disponibilidade de histórico.

#### Scenario: Encontrar os exemplos de verificação

- **WHEN** o usuário pesquisa `BTC/USDT`, `NVDA`, `SPY` ou `QQQ`
- **THEN** o ativo correspondente aparece na primeira página do resultado com sua classe e pode ser marcado

#### Scenario: Pesquisa por nome

- **WHEN** o usuário pesquisa `nvidia`
- **THEN** NVDA aparece no resultado

#### Scenario: Pesquisa sem resultado

- **WHEN** nenhum ativo corresponde à pesquisa e ao filtro
- **THEN** o seletor mostra um resultado vazio explícito, com orientação para ajustar a pesquisa ou a classe
- **AND** não mostra paginação vazia
- **AND** a seleção atual é preservada

### Requirement: "Todos" seleciona só o filtro atual, com contagem antes de confirmar

A ação "Todos" SHALL considerar apenas os ativos negociáveis do filtro atual (classe e pesquisa) e SHALL mostrar, antes de confirmar, quantos ativos serão incluídos e quantos ativos marcados do filtro ficam de fora. Confirmar SHALL somar esses ativos à seleção existente. Cancelar, inclusive pela tecla Esc, MUST NOT alterar a seleção e SHALL devolver o foco à ação "Todos". Ativos marcados MUST NOT entrar por "Todos".

#### Scenario: Todos os ETFs

- **WHEN** o filtro de classe é ETFs, sem pesquisa, e o usuário aciona "Todos"
- **THEN** o seletor pede confirmação mostrando o número de ETFs negociáveis que serão incluídos e o número de ETFs marcados que ficam de fora
- **AND** depois de confirmar, só os ETFs negociáveis do filtro entram na seleção

#### Scenario: Todos com pesquisa

- **WHEN** a pesquisa é `nvidia` em Todas as classes e o usuário confirma "Todos"
- **THEN** só os ativos negociáveis que correspondem a `nvidia` entram na seleção

#### Scenario: Cancelar a confirmação

- **WHEN** o usuário aciona "Todos" e cancela a confirmação pelo botão ou pela tecla Esc
- **THEN** a seleção continua igual
- **AND** o foco volta para a ação "Todos"

### Requirement: Ativo marcado não pode ser escolhido para análise nova

Ativo suspenso, fora de mercado, sem negociação, sem regras de negociação ou removido SHALL aparecer no resultado com o estado e o motivo, sem caixa de seleção ativa, só para explicar resultados e favoritos antigos. O usuário MUST NOT conseguir escolhê-lo para análise nova, nem item a item, nem por "Todos", pelo atalho de lote do Combo ou por outra ação que inclua vários ativos. Quando uma seleção, rascunho ou favorito antigo contém um ativo marcado, o seletor SHALL mostrá-lo marcado e indicar que ele fica de fora, e o Preflight ou o aviso antes de rodar SHALL dizer que ele ficará de fora e por quê.

#### Scenario: Ativo suspenso na pesquisa

- **WHEN** o usuário pesquisa `waves` e WAVES/USDT está suspenso pela Binance
- **THEN** WAVES/USDT aparece com o estado Suspenso e o motivo
- **AND** não pode ser marcado, e a seleção não muda

#### Scenario: Todos não inclui o marcado

- **WHEN** o filtro contém ativos negociáveis e um ativo suspenso, e o usuário confirma "Todos"
- **THEN** o ativo suspenso não entra na seleção

#### Scenario: Rascunho antigo com ativo marcado na Descoberta

- **WHEN** um rascunho salvo contém BTC/USDT e WAVES/USDT, e WAVES/USDT está suspenso
- **THEN** WAVES/USDT aparece em "Selecionados" marcado como fora, antes de qualquer resumo "+N"
- **AND** o Preflight mostra WAVES/USDT em "Fora desta varredura", com o motivo da Binance
- **AND** a varredura pode iniciar com BTC/USDT

#### Scenario: Favorito antigo com ativo marcado na otimização

- **WHEN** `/combo/optimize?symbol=WAVES/USDT` é aberta e WAVES/USDT está suspenso
- **THEN** WAVES/USDT aparece marcado como fora
- **AND** antes de rodar a tela diz que nada será executado e por quê
- **AND** ao acionar Run Optimization nenhuma otimização é iniciada

### Requirement: Ação e ETF podem ser escolhidos e geram aviso ao rodar

O seletor SHALL permitir escolher ação e ETF antes de as análises aceitarem essas classes. Antes de rodar, o Combo e a Otimização SHALL dizer o que será executado e o que fica de fora, com o motivo. Ao rodar, o usuário SHALL receber aviso com motivo claro de que a análise ainda não está disponível para ação e ETF, com os ativos afetados, nunca erro genérico. O backend SHALL recusar ação e ETF nas análises com código e motivo, não com mensagem genérica.

#### Scenario: Descoberta com cripto e ação

- **WHEN** a seleção da Descoberta tem BTC/USDT e NVDA
- **THEN** o Preflight mostra as combinações de NVDA fora da varredura, com o motivo "análise ainda não disponível para ações e ETFs"
- **AND** a varredura pode iniciar com as combinações de cripto

#### Scenario: Descoberta só com ações e ETFs

- **WHEN** a seleção da Descoberta tem apenas ações e ETFs
- **THEN** o Preflight bloqueia o início e informa o motivo, sem criar varredura

#### Scenario: Combo com uma ação

- **WHEN** o usuário escolhe só NVDA no Combo
- **THEN** o texto sob Otimizar diz, antes do clique, que nada será executado nem salvo porque a análise ainda não está disponível para ações e ETFs
- **AND** ao acionar Otimizar a tela mostra o aviso com NVDA e o motivo, e nada é executado nem salvo

#### Scenario: Lote do Combo com cripto e ETF

- **WHEN** a seleção do Combo tem pares cripto e SPY, e o usuário aciona Otimizar
- **THEN** o lote roda só com os pares cripto
- **AND** o aviso lista SPY como fora do lote, com o motivo

#### Scenario: Lote da otimização com cripto e ETF

- **WHEN** a seleção de `/combo/optimize` tem BTC/USDT, ETH/USDT e QQQ, e o usuário aciona Run Optimization
- **THEN** roda uma otimização por par cripto, como no lote do Combo, e o melhor resultado de cada um é salvo em favoritos
- **AND** a tela mostra o progresso do lote e, no fim, o resumo de sucesso, falha e ignorados com o link para os favoritos
- **AND** o aviso lista QQQ como fora do lote, com o motivo

#### Scenario: Otimização com um único par

- **WHEN** a seleção de `/combo/optimize` tem só BTC/USDT, e o usuário aciona Run Optimization
- **THEN** a otimização roda como hoje e o resultado aparece no painel da página

#### Scenario: Otimização só com ETF

- **WHEN** o usuário escolhe só QQQ em `/combo/optimize` e aciona Run Optimization
- **THEN** a tela mostra o aviso com QQQ e o motivo, e nenhuma otimização é iniciada

#### Scenario: Chamada direta à API com ação

- **WHEN** um cliente envia NVDA para backtest, otimização ou lote
- **THEN** a API recusa com código de classe não suportada, a classe e o ativo, e uma mensagem em português

#### Scenario: Chamada direta à API com ativo marcado

- **WHEN** um cliente envia um ativo suspenso para otimização ou lote
- **THEN** a API recusa com código de ativo não escolhível, o estado e o motivo

### Requirement: Falha do catálogo é mostrada no seletor

Quando a última atualização de uma classe falhou, o seletor SHALL informar a falha e a data da lista mostrada. Quando não há lista válida da classe, o seletor SHALL mostrar um único erro explícito com ação de tentar de novo. A seleção já feita MUST ser preservada, e o seletor MUST NOT mostrar lista vazia como se o catálogo estivesse vazio nem atribuir ao símbolo pesquisado a falta de resultado causada pela falha.

#### Scenario: Ações e ETFs desatualizados

- **WHEN** a atualização de ações e ETFs falhou e há uma lista anterior
- **THEN** o seletor mostra um aviso com a data da lista e continua permitindo pesquisar e escolher

#### Scenario: Cripto indisponível sem lista

- **WHEN** a classe cripto nunca foi carregada e a Binance falhou
- **THEN** o filtro Cripto mostra "indisponível" e o seletor mostra um único erro com ação de tentar de novo, em vez de um resultado vazio

#### Scenario: Pesquisa durante a falha de cripto

- **WHEN** cripto está indisponível e o usuário pesquisa `btc` em Todas as classes
- **THEN** o seletor diz que cripto está indisponível por falha da Binance
- **AND** não pede para conferir o símbolo nem mostra paginação vazia

