## ADDED Requirements

### Requirement: Lista única com classe e moeda
Favoritos (`/favorites`) SHALL listar cripto, ações e ETFs na mesma tabela (desktop) e nos mesmos cartões (celular). Cada linha MUST mostrar a classe (chip Cripto, Ação ou ETF, nas cores do seletor de ativos) e a moeda da classe (USDT para cripto, USD para ação e ETF) junto do símbolo. Nenhuma linha MUST mostrar as duas moedas, e nenhum valor em preço MUST aparecer sem a moeda da linha. A lista MUST NOT somar nem converter valores entre USD e USDT.

#### Scenario: Linha de ação
- **WHEN** Favoritos mostra o favorito de NVDA gerado em lote
- **THEN** a linha MUST mostrar "NVDA", o chip "Ação" e "USD"

#### Scenario: Linha de cripto
- **WHEN** Favoritos mostra o favorito de BTC/USDT
- **THEN** a linha MUST mostrar o chip "Cripto" e "USDT"

### Requirement: Precisão, convenções e período efetivo em cada linha
Cada linha SHALL mostrar à vista, no bloco da estratégia: a precisão efetiva ("Precisão intrabar (15m)", ou "Precisão diária · sem 15m de <início> a <fim>" em âmbar com ícone), as convenções da classe em uma linha ("Binance Spot · 24/7 · 365 dias/ano" ou "Binance Ações · NY · split · 252/ano") e o período efetivo ("Período efetivo <início> – <fim>"). Num `<details>` fechado ("Limitações e origem" em ação/ETF, "Origem" em cripto do lote), a linha MUST trazer as convenções completas ("Binance Ações · pregão regular de Nova York · ajustado por split · 252 pregões/ano"), as limitações de ação e ETF (fração simulada, taxa assumida quando não confirmada, preços ajustados) e, em favorito gerado em lote, "Gerado em lote <id8> · <data>". As células símbolo e estratégia MUST NOT ter `aria-label` que esconda a classe, a moeda e a precisão do nome acessível. Favorito antigo sem esses dados MUST dizer que eles aparecem na próxima atualização diária, sem inventar precisão.

#### Scenario: Precisão diária visível
- **WHEN** o favorito de NVDA rodou em precisão diária
- **THEN** a linha MUST mostrar "Precisão diária · sem 15m de 11 nov. 2014 a 18 mai. 2026"
- **AND** MUST mostrar "Período efetivo 11 nov. 2014 – 23 out. 2026"

#### Scenario: Limitações e origem
- **WHEN** Alan abre "Limitações e origem" na linha de NVDA
- **THEN** a linha MUST mostrar as convenções completas, "simulação com fração · taxa assumida · preços ajustados podem diferir do negociado" e "Gerado em lote 7f3c2a91 · 24 out. 2026"

#### Scenario: Favorito antigo
- **WHEN** um favorito de cripto ainda não tem `execution`
- **THEN** a linha MUST dizer "Precisão e período efetivo: aparecem na próxima atualização diária"

### Requirement: Filtro por classe e ordenação comum
Favoritos SHALL ter o filtro "Classe" (Todas, Cripto, Ações, ETFs, com contagem) antes dos filtros existentes, valendo para tabela e cartões. Os selects de filtro MUST mostrar o anel de foco (`:focus-visible`). A ordenação existente (Ret/T %, Return, Sharpe, Trades) MUST ordenar todas as classes juntas. A contagem "N filtradas" e o rodapé MUST refletir o filtro.

#### Scenario: Só ações
- **WHEN** Alan escolhe Classe = Ações
- **THEN** só os favoritos de ações MUST aparecer e a contagem MUST mudar

#### Scenario: Ordenar por retorno
- **WHEN** Alan ordena por Return com cripto, ação e ETF na lista
- **THEN** as linhas MUST seguir o retorno, sem separar por classe

### Requirement: Monitor, Telegram e Revalidar fora para ação e ETF até o #1122
Nas linhas e nos cartões de ação e ETF, as estrelas do Monitor, o botão Telegram e "Revalidar" SHALL ficar visíveis, sem estrela marcada, com `aria-disabled="true"`, focáveis e com o motivo ligado por `aria-describedby`; a linha MUST dizer "Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs". O clique MUST NOT mudar nada. O resumo por estrelas ("Acompanhar N", "Interesse alto N", "Top picks N") e o filtro por estrelas MUST contar só cripto, com a nota "Monitor, Telegram e Revalidar: ainda não para ações e ETFs. Os N favoritos de ação e ETF ficam fora destes níveis."

#### Scenario: Estrela em NVDA
- **WHEN** Alan foca ou clica numa estrela, no Telegram ou em Revalidar da linha de NVDA
- **THEN** o controle MUST ser anunciado como indisponível, com "Monitor, Telegram e Revalidar: ainda não para ações e ETFs", e nada MUST mudar

#### Scenario: Resumo do Monitor
- **WHEN** Favoritos lista BTC/USDT (1 estrela), NVDA e SPY gerados em lote
- **THEN** "Acompanhar" MUST contar 1 e a nota MUST dizer que os 2 favoritos de ação e ETF ficam fora destes níveis

### Requirement: Faixa do lote
Aberto com `?lote=<id8>`, Favoritos SHALL mostrar só os favoritos gravados por esse lote, com uma faixa `role=status` "Mostrando só o lote <id8> (<data>)…" e o botão "Mostrar todos os favoritos" (alvo de 44 px), que limpa o filtro e devolve o foco ao filtro Classe.

#### Scenario: Chegar pelo fim do lote
- **WHEN** Alan abre `/favorites?lote=7f3c2a91`
- **THEN** só BTC/USDT, NVDA e SPY do lote MUST aparecer, com a faixa do lote

### Requirement: API de favoritos com identidade de classe
`GET /api/favorites/` SHALL devolver `asset = {symbol, asset_id, asset_class, name, currency}` em cada favorito: do `metrics.asset` gravado ou, em favorito antigo, resolvido pelo catálogo (cripto pelo `/` do símbolo).

#### Scenario: Favorito antigo de cripto
- **WHEN** um favorito antigo de ETH/USDT não tem `metrics.asset`
- **THEN** a resposta MUST trazer `asset.asset_class = "crypto"` e `asset.currency = "USDT"`
