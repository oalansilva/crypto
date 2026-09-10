## ADDED Requirements

### Requirement: KPI e seção de posição com o mesmo nome sem tag divergente

O Monitor (`/monitor`) SHALL exibir o KPI de posição e o título da seção de posição com o mesmo nome `Em posição`, sem tag de ação divergente.

#### Scenario: Leitura do KPI de posição e do título da seção

- **WHEN** o operador lê o KPI de posição e o título da seção com sinais visíveis
- **THEN** os dois mostram o mesmo nome `Em posição`
- **AND** nenhuma tag `Compra` é exibida nos KPIs
- **AND** nenhum badge `Estado Compra/Venda` nem `Estado hold/exit` visível nos headers das seções

### Requirement: KPI e seção de saída com o mesmo nome sem tag divergente

O Monitor (`/monitor`) SHALL exibir o KPI de saída e o título da seção de saída com o mesmo nome `Saída / cobertura`, sem tag de ação divergente.

#### Scenario: Leitura do KPI de saída e do título da seção de saída

- **WHEN** o operador lê o KPI e o título da seção de saída com sinais de saída
- **THEN** os dois mostram o mesmo nome `Saída / cobertura`
- **AND** nenhuma tag `Venda` é exibida nos KPIs
- **AND** nenhum badge `Estado Compra/Venda` nem `Estado hold/exit` visível nos headers das seções

### Requirement: Coluna Status e card mobile com o nome canónico da seção

O Monitor (`/monitor`) SHALL exibir na coluna Status de `table.signals` e no rótulo de estado visível do card mobile o mesmo nome canónico da seção correspondente — `Em posição` na seção hold e `Saída / cobertura` na seção exit — e SHALL NOT usar `Compra` ou `Venda` como nome de estado da board nessas superfícies.

#### Scenario: Leitura do Status da linha na tabela

- **WHEN** o operador lê a coluna Status de uma linha na `table.signals` da seção em posição
- **THEN** o texto visível é `Em posição`
- **AND** o texto visível não é `Compra` nem `Venda`

#### Scenario: Leitura do Status da linha de saída

- **WHEN** o operador lê a coluna Status de uma linha na `table.signals` da seção de saída
- **THEN** o texto visível é `Saída / cobertura`
- **AND** o texto visível não é `Compra` nem `Venda`

#### Scenario: Leitura do rótulo de estado no card mobile

- **WHEN** o operador vê o card mobile de um sinal (viewport em que `.mobile-cards` substitui a tabela)
- **THEN** o rótulo de estado visível é `Em posição` ou `Saída / cobertura`, conforme a seção
- **AND** o rótulo não é `Compra` nem `Venda`

### Requirement: Ajuda ensina os nomes canónicos como estados do Monitor

A copy visível da Ajuda `/help` (parágrafo Monitor em `HelpPage.tsx`) e do `ScreenHelpPanel` no `/monitor` que descrevem os estados do Monitor SHALL usar `Em posição` e `Saída / cobertura`, e SHALL NOT ensinar `Compra` / `Venda` como estados do Monitor. Troca estrita: o restante do guia não é reescrito; lado de ordem Spot (`comprar` / `vender` como acção) MAY permanecer.

#### Scenario: Parágrafo Monitor na página Ajuda

- **WHEN** o operador lê o artigo Monitor em `/help`
- **THEN** o parágrafo cita `Em posição` e `Saída / cobertura`
- **AND** o parágrafo não cita `Compra` nem `Venda` como estados do Monitor

#### Scenario: Painel Como usar o Monitor

- **WHEN** o operador lê o `ScreenHelpPanel` em `/monitor`
- **THEN** o painel cita `Em posição` e `Saída / cobertura`
- **AND** o painel não ensina `Compra` nem `Venda` como estados do Monitor

### Requirement: Busca do Monitor sem hint falso de atalho

A busca do Monitor (`/monitor`) SHALL NOT exibir hint falso de atalho — nenhum texto de tecla `⌘K` (nem sinónimo `Cmd+K`) visível — e SHALL NOT implementar foco por teclado neste card.

#### Scenario: Observação da busca

- **WHEN** o operador observa a busca do Monitor
- **THEN** não existe hint falso visível
- **AND** pressionar ⌘K/Ctrl+K não precisa focar nada (sem atalho neste card)

### Requirement: Regra HOLD/EXIT inalterada e lado de ordem intocado

A regra de sinal HOLD/EXIT do Monitor SHALL permanecer inalterada — só copy/atalho mudam. Marcadores do gráfico e lado de ordem Spot SHALL continuar a usar `Compra` / `Venda` como BUY/SELL (`markerLabel`); este card SHALL NOT criar um terceiro estado nem vocabulário de entrada potencial.

#### Scenario: Sinal em qualquer estado

- **WHEN** o operador observa qualquer estado
- **THEN** nada mudou no sinal (só copy/atalho)

#### Scenario: Gráfico e Spot

- **WHEN** o operador vê marcadores do gráfico ou o painel Spot
- **THEN** o lado de ordem permanece `Compra` / `Venda` (BUY/SELL)
- **AND** nenhuma seção de entrada potencial foi adicionada ao Monitor
