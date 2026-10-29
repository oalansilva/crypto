## ADDED Requirements

### Requirement: Favorito guarda fonte, sessão e ajuste
Todo favorito SHALL guardar a configuração de dados com que foi executado: fonte (`ccxt`, `binance_equity`, `stooq`), sessão (`24x7`, `regular_ny`, `eod`) e ajuste (`none`, `split`, `legacy`). A gravação vem do resultado (lote, Descoberta, resultado individual) e, em favorito antigo, de um backfill:
- par com `/` → `ccxt`, `24x7`, `none`;
- `parameters.data_source = binance_equity` → `binance_equity`, `regular_ny`, `split`, ou o que `analysis_conventions` disser;
- ticker sem fonte → `stooq`, `eod`, `legacy`.

A configuração MUST voltar em `GET /api/favorites/` e em cada oportunidade do Monitor, com um rótulo curto e um longo:
- cripto: "Binance Spot · 24/7";
- ação e ETF da Binance: "Binance Ações · NY · split" (longo: "Binance Ações · pregão regular de NY · ajustado por split");
- fonte antiga: "Stooq · fonte antiga · diário".

#### Scenario: Backfill do favorito de lote
- **WHEN** a migração encontra um favorito de NVDA gravado pelo lote com `parameters.data_source = binance_equity`
- **THEN** a configuração dele MUST ser `binance_equity`, `regular_ny`, `split`

#### Scenario: Favorito antigo de ticker
- **WHEN** a migração encontra um favorito de AAPL sem `data_source`
- **THEN** a configuração MUST ser `stooq`, `eod`, `legacy`, com o rótulo "Stooq · fonte antiga · diário"

### Requirement: Chave de duplicata inclui a configuração
A duplicata de favorito SHALL ser decidida por: usuário, estratégia, símbolo, tempo gráfico, período, direção, fonte, sessão e ajuste. `lock_and_find_duplicate` e `find_existing_favorite` MUST comparar os três campos novos e MUST incluí-los na chave do lock. `GET /api/favorites/exists` MUST aceitar `data_source`, `session` e `adjustment`; sem eles, a configuração MUST ser a padrão do símbolo pela classe do catálogo (cripto `ccxt`; ação/ETF `binance_equity`). A mesma configuração repetida MUST ser recusada com 409 "Estratégia já existe nos favoritos com esta configuração". Uma configuração diferente MUST coexistir.

#### Scenario: NVDA em duas fontes
- **WHEN** o usuário já tem NVDA 1d `multi_ma_crossover` Long da fonte antiga
- **AND** salva o mesmo NVDA 1d `multi_ma_crossover` Long da Binance Ações
- **THEN** o segundo favorito MUST ser gravado

#### Scenario: Mesma configuração
- **WHEN** o usuário salva de novo NVDA 1d `multi_ma_crossover` Long da Binance Ações, mesmo período
- **THEN** a API MUST responder 409 e nada MUST ser gravado

### Requirement: Ação e ETF são favoritáveis como a cripto
`POST /api/favorites/` SHALL aceitar ação e ETF, gravando a configuração, `analysis_asset`, `analysis_execution` e `analysis_conventions` do resultado. Na página do resultado, "Salvar nos Favoritos" de ação ou ETF MUST abrir o mesmo modal da cripto, com a linha de identidade (ativo, classe, moeda e configuração longa). O modal MUST trazer a nota "O favorito entra sem estrela, só em Favoritos. Dê pelo menos 1 estrela lá para acompanhar no Monitor e receber os sinais no Telegram; o alerta já vem ligado e você desliga no Monitor." A duplicata MUST aparecer no modal como texto. O modal MUST prender o foco, fechar com Esc onde quer que esteja o foco e devolver o foco a "Salvar nos Favoritos"; depois de salvar, o foco MUST ir para "Ver em Favoritos" (alvo de 44 px). Saem: o código `asset_class_not_favoritable` e os textos "Ações e ETFs ainda não podem ser favoritados…" (resultado) e "…sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados." (Combo com 1 ativo). O Combo com 1 ação ou ETF MUST continuar abrindo o resultado e passa a dizer "NVDA: otimiza e abre o resultado; para acompanhar, salve nos Favoritos por lá.".

#### Scenario: Salvar NVDA pelo resultado
- **WHEN** Alan ativa "Salvar nos Favoritos" no resultado de NVDA 1d
- **THEN** o modal MUST abrir com "NVDA · Ação · USD · Binance Ações · pregão regular de NY · ajustado por split"
- **AND** salvar MUST gravar o favorito com a configuração e as chaves `analysis_*`

#### Scenario: Duplicata no modal
- **WHEN** o favorito com a mesma configuração já existe
- **THEN** o modal MUST mostrar "Já está nos favoritos com esta configuração (fonte, sessão e ajuste)." e nada MUST ser gravado

### Requirement: Lote e Descoberta salvam sem estrela; alerta ligado por padrão
Favorito criado pelo lote ou pela Descoberta SHALL nascer sem estrela (`tier` nulo) em qualquer classe: fica em Favoritos, fora do Monitor e sem alerta, até o dono dar a estrela (decisão 4 de Alan, 27/10/2026). O favorito salvo pelo resultado individual também nasce sem estrela. Todo favorito novo, por qualquer caminho, MUST nascer com o alerta ligado (`notify_telegram = true`), que só tem efeito com estrela (`favorite-telegram-alerts`). O default da coluna `notify_telegram` MUST ser verdadeiro.

#### Scenario: Lote com 300 ações
- **WHEN** um lote grava 300 favoritos de ação
- **THEN** os 300 MUST ficar sem estrela e com `notify_telegram = true`
- **AND** nenhum deles MUST aparecer no Monitor nem gerar alerta até o dono dar a estrela

#### Scenario: Salvar NVDA pelo resultado
- **WHEN** Alan salva NVDA 1d pela página do resultado
- **THEN** o favorito MUST ficar sem estrela, fora do Monitor e com `notify_telegram = true`
