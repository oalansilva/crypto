# favorites-class-comparison Specification

## Purpose
TBD - created by archiving change card-1120-lote-multiclasse. Update Purpose after archive.
## Requirements
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

### Requirement: Estrelas e Revalidar valem para ação e ETF; a estrela é a porta do Monitor
Nas linhas e nos cartões de ação e ETF, as estrelas e "Revalidar" SHALL funcionar como na cripto. O resumo por estrelas ("Acompanhar N", "Interesse alto N", "Top picks N") e o filtro por estrelas MUST contar todas as classes. A nota "Monitor, Telegram e Revalidar: ainda não para ações e ETFs…" e o texto "Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs" MUST sair; no lugar deles, a linha MUST mostrar o status de atualização (`favorite-backtest-refresh`). A configuração da fonte antiga MUST aparecer como "Stooq · fonte antiga · diário", e não como "Binance Ações".

Favoritos MUST NOT ter controle de alerta (`monitor-telegram-favorite-toggle`). Em todas as classes:
- abaixo do subtítulo, a ajuda "Com pelo menos 1 estrela, a estratégia entra no Monitor e manda alerta no Telegram, ligado por padrão (desligue no Monitor). Sem estrela, fica só aqui; lote e Descoberta salvam sem estrela.";
- na célula das estrelas da linha e do cartão, a legenda "No Monitor" (com estrela) ou "Fora do Monitor" (sem estrela);
- ao dar a primeira estrela, o status da página MUST dizer "<ativo> <tempo> entrou no Monitor com o alerta ligado." e a legenda ao lado da estrela MUST dizer "No Monitor · alerta ligado"; ao tirar a última, o status MUST dizer "<ativo> <tempo> saiu do Monitor e não manda mais alerta.";
- no resumo por estrelas, "Acompanhar" (1 estrela) MUST dizer "No Monitor, com alerta ligado", e não "Monitorar quando fizer sentido";
- no cartão do celular, cada estrela MUST ter alvo de pelo menos 44 px.

#### Scenario: Estrela em NVDA
- **WHEN** Alan marca 2 estrelas na linha de NVDA
- **THEN** o nível MUST ser gravado e NVDA MUST entrar no Monitor e no resumo "Interesse alto"

#### Scenario: Primeira estrela em QQQ do lote
- **WHEN** Alan dá 1 estrela ao favorito de QQQ 1d gravado pelo lote, sem estrela
- **THEN** a legenda MUST mudar de "Fora do Monitor" para "No Monitor · alerta ligado"
- **AND** o status MUST dizer "QQQ 1d entrou no Monitor com o alerta ligado."

#### Scenario: Linha da fonte antiga
- **WHEN** Favoritos lista um favorito de NVDA da fonte antiga
- **THEN** a linha MUST mostrar "Stooq · fonte antiga · diário" e nenhum controle de alerta

