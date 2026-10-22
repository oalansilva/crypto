## Why

Hoje só pares cripto em USDT podem ser escolhidos, cada tela tem um seletor diferente (lista dupla no Combo, lista inline na Descoberta, texto livre na otimização) e uma falha da Binance pode virar lista vazia ou fixa. Esta é a primeira história do épico #1116: as próximas (#1118 a #1126) dependem de um catálogo único, com identidade estável, para cripto, ações e ETFs.

## Problema

Alan não consegue escolher ações e ETFs no mesmo fluxo usado para cripto, nem distinguir catálogo, negociação disponível e cobertura de dados.

## História

Como usuário, quero pesquisar e selecionar cripto, ações e ETFs da Binance para escolher o universo das minhas análises sem listas fixas.

## Entra

- Catálogo dinâmico com **todas** as ações e ETFs que a Binance oferece (https://www.binance.com/pt/stocks/) e todos os pares cripto spot em USDT, com pesquisa, paginação e filtros por classe, nome e símbolo. NVDA, SPY e QQQ são só exemplos de verificação, nunca o escopo.
- Seleção individual e em lote com a mesma pesquisa na configuração de combo, na descoberta e na otimização; a otimização deixa de aceitar ativo digitado à mão.
- "Todos" seleciona apenas o que está no filtro atual (classe, pesquisa) e mostra quantos ativos serão incluídos antes de confirmar.
- Ação ou ETF pode ser escolhido mesmo antes de as análises aceitarem essa classe; ao rodar, o usuário recebe aviso com motivo claro de que a análise ainda não está disponível para ela, nunca erro genérico.
- Distinguir ativo listado, status de negociação e disponibilidade/cobertura histórica; a disponibilidade da conta será tratada na história de ordens.
- Ativo removido ou suspenso aparece na pesquisa marcado com estado e motivo; pode ser escolhido individualmente, mas nunca entra sozinho num lote nem no "todos". Identidade estável preserva esses ativos em resultados e favoritos antigos; não confundir ações, tokens ou símbolos semelhantes.
- Cripto continua só com pares cotados em USDT, como hoje.
- Verificação: BTC/USDT, NVDA e SPY/QQQ podem ser encontrados e selecionados; a quantidade de ações e ETFs disponíveis para escolha corresponde ao catálogo da Binance (descontados os excluídos), e limites por lote de ingestão não truncam o catálogo.
- Reconciliar catálogo estático e regras de negociação; excluir direitos de subscrição (RIGHT) e derivativos. Falha da Binance é informada ao usuário, sem virar catálogo vazio nem lista fixa de poucos ativos.

> **Decisões de Alan no Design (20/10/2026)** — [comentário no card](https://github.com/oalansilva/crypto/issues/1117#issuecomment-6282565608). Prevalecem sobre o Entra acima:
>
> 1. Ativo pausado ou retirado pela Binance (suspenso, fora de mercado, sem negociação, sem regras, removido) **não pode ser escolhido para análise nova**. Aparece na pesquisa marcado com estado e motivo, sem caixa de seleção ativa, só para explicar resultados e favoritos antigos. Substitui "pode ser escolhido individualmente".
> 2. **Lote também na otimização:** `/combo/optimize` aceita vários ativos, com a mesma pesquisa e o mesmo "Todos do filtro (N)" com contagem e confirmação.

## Não entra

- Coleta de todo o histórico do catálogo.
- Envio de ordens ou autorização de negociação por simples presença na lista.
- Pares cripto cotados em outras moedas (BTC, USDC, EUR e demais).
- Rodar backtest, combo, otimização ou descoberta com ações e ETFs: isso chega nas histórias seguintes do épico; aqui entram a escolha e o aviso.

## What Changes

- Novo catálogo persistido de ativos Binance: pares cripto spot em USDT mais ações e ETFs, reconciliados por identificador entre o catálogo estático e as regras de negociação, com RIGHT e derivativos excluídos. Cada ativo tem identidade estável, classe, estado de negociação com motivo e cobertura histórica, três informações separadas.
- Nova API de pesquisa paginada do catálogo (pesquisa por nome e símbolo, filtro por classe, contagens por classe, frescor do catálogo) e de resolução de "Todos" para o filtro atual.
- Um único seletor de ativos nas três telas: Descoberta (`/combo/discovery`), Combo (`/combo/configure`) e Otimização (`/combo/optimize`). Na Otimização o campo de texto livre sai (**BREAKING** para quem digitava o símbolo ou passava um símbolo fora do catálogo pela URL) e entram vários ativos: com N ativos ela roda o mesmo lote do Combo, uma otimização por ativo.
- "Todos" passa a significar "todos do filtro atual", com contagem e confirmação. Na Descoberta deixa de existir "catálogo inteiro com exceções" (**BREAKING**); no Combo o rádio "Todos / Seleciona" dá lugar à mesma ação.
- Suspenso, fora de mercado, sem negociação, sem regras ou removido aparece marcado com estado e motivo, sem caixa de seleção ativa: não pode ser escolhido para análise nova. Se vier de um rascunho, seleção ou favorito antigo, aparece marcado e o Preflight ou o aviso antes de rodar diz que fica de fora e por quê.
- Ação ou ETF escolhido gera aviso claro ao rodar: o Preflight da Descoberta mostra essas combinações como fora da varredura; no Combo e na Otimização, a cópia sob o botão avisa antes do clique, só ação ou ETF não executa nada e o lote misto roda só a parte cripto, com a lista do que ficou fora. O backend troca o erro genérico em inglês por uma recusa estruturada com classe e motivo.
- A falha da Binance aparece na tela: o seletor mostra a última lista válida e a data dela, ou um erro explícito quando nunca houve lista. Sai o fallback de 5 símbolos fixos.

## Capabilities

### New Capabilities

- `binance-asset-catalog`: universo Binance (cripto spot USDT, ações, ETFs), reconciliação, exclusões, estados de negociação, cobertura histórica, identidade estável, contagem verificável e comportamento sob falha da Binance.
- `asset-selection`: seletor único com pesquisa, filtro por classe, paginação, seleção individual e "Todos do filtro" com contagem nas três telas (Otimização incluída), ativos marcados não escolhíveis, aviso de classe e de marcado ao rodar.

### Modified Capabilities

- `crypto-only-mvp`: a configuração do Combo deixa de oferecer só pares cripto. Ações e ETFs podem ser escolhidos, mas as análises continuam só com cripto e recusam ação ou ETF com aviso claro.
- `discovery-catalog-selection`: "Selecionar todos" deixa de ser o catálogo inteiro com exceções e passa a ser o filtro atual com contagem. A garantia de alcance cobre o catálogo inteiro (milhares de ativos), não mais 126 símbolos.

## Impact

- Backend: novo serviço e tabelas de catálogo (PostgreSQL, Alembic), atualização periódica, rotas `GET /assets/catalog` e `POST /assets/catalog/resolve`. `GET /exchanges/binance/symbols` continua como compatibilidade, lendo do catálogo. `combo_routes.py` (`_ensure_crypto_symbol(s)` passa a recusar com código e motivo, inclusive ativo marcado em otimização e lote), `discovery_service.py` (exclusão por classe e por ativo marcado no preflight), `binance_symbol_universe.py` (sem `FALLBACK_BINANCE_USDT_SYMBOLS` como universo silencioso).
- Frontend: componente compartilhado de seleção de ativos. Em `DiscoveryPage.tsx` substitui o eixo Símbolos (inline e Edição avançada); em `ComboConfigurePage.tsx`, a lista dupla e o rádio Todos/Seleciona; em `ComboOptimizePage.tsx`, o campo de texto (com vários ativos, a página chama o lote existente `POST /combos/backtest/batch`).
- Externos: rotas públicas Binance `bapi/equity/.../get-symbols-static` e `get-exchange-info` (sem contrato público estável) e `api/v3/exchangeInfo` spot. Sem credenciais.
- Fora: coleta de histórico de ações e ETFs (#1118), execução de análises com ações e ETFs (#1119 a #1121), ordens (#1124), migração de favoritos legados (#1126). Sem PROD neste card; PROD só por T16.
