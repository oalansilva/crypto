UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1117](https://github.com/oalansilva/crypto/issues/1117), primeira história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado, com as 5 decisões de Alan de 20/10/2026. Depois da crítica A/B, Alan decidiu mais dois pontos no Design ([comentário](https://github.com/oalansilva/crypto/issues/1117#issuecomment-6282565608)), e eles prevalecem sobre o body: ativo pausado ou retirado pela Binance não pode ser escolhido para análise nova (decisão 5), e a otimização aceita vários ativos com o mesmo "Todos do filtro" (decisão 7). Não houve reentrevista.

Estado atual em `develop` @ 1a06caec:

- Três telas escolhem ativo, cada uma de um jeito. A Descoberta (`DiscoveryPage.tsx`) tem lista inline de 30 itens mais "Edição avançada" com o modo `all` e exceções. O Combo (`ComboConfigurePage.tsx`) tem o rádio `Todos/Seleciona`, uma lista dupla e o atalho Top 10. A Otimização (`ComboOptimizePage.tsx`, `/combo/optimize`, só admin) tem campo de texto livre com padrão `BTC/USDT`.
- Descoberta e Combo leem `GET /exchanges/binance/symbols`: CCXT `load_markets`, só `/USDT`, cache de 24h em arquivo, sem estado de negociação. Pares em `BREAK` aparecem sem marca. Se a Binance falha sem cache, a rota dá erro 500 e as telas mostram "Carregando catálogo…" sem fim.
- `binance_symbol_universe.py`, o universo da ingestão de candles, cai em `FALLBACK_BINANCE_USDT_SYMBOLS` (5 pares) quando `exchangeInfo` e o cache falham.
- `combo_routes.py` recusa símbolo sem `/` com HTTP 400 e mensagem genérica em inglês ("The MVP supports only crypto pairs").
- O lote do Combo já existe: com N ativos, `ComboConfigurePage.tsx` chama `POST /combos/backtest/batch` (`symbols`, template, timeframe, datas, faixas). `batch_backtest_service.py` roda uma otimização por ativo com a mesma configuração e salva o melhor resultado de cada um como favorito novo ("gerado em lote", tier 3), sem sobrescrever favorito igual (conta como ignorado). A tela faz polling e mostra "X de N ativos", ativo atual, tempo, Pausar e Encerrar, e no fim "sucesso, falha, ignorados", erros por ativo e o link para Strategy Favorites.
- Leitura pública Binance de 20/10/2026, base dos números do protótipo:
  - Catálogo estático: 7.969 registros (4.840 STOCK, 3.128 ETF, 1 RIGHT).
  - Regras de negociação: 7.956 registros. 7.955 estão nas duas listas, 14 só no estático e 1 (CEPT) só nas regras.
  - Estados de negociação: `BUY_SELL` 7.860, `OFFMARKET` 79, `NONE` 17.
  - Entre os STOCK há 3 rights, 4 direitos de valor contingente e 1 warrant.
  - Spot USDT: 725 pares, 511 `TRADING` e 214 `BREAK`.

**Audience:** Alan e administradores que montam varredura, combo ou otimização.
**Outcome:** um seletor único encontra e escolhe qualquer ativo Binance elegível. Ele mostra classe, negociação e histórico separados, "Todos" respeita o filtro, ativo pausado ou retirado não é escolhível, ação e ETF geram aviso claro e falha da Binance é visível.
**Direction:** clone+delta Operate. Tokens Binance do `DESIGN.md`, sem mundo visual novo.
**Scope:** seletor de ativos nas três telas, catálogo no backend, recusa de classe nas análises. Coleta de histórico, execução com ações e ETFs, ordens e migração de favoritos legados ficam fora.

Regiões clonadas, só estas:

- `index.html` (canônico, `/combo/discovery`): shell AppNav, heading e ações, 3 modos, cabeçalho do Rascunho, eixo Templates (resumo, "Edição avançada" e busca inline, como no vivo), Timeframes e Direção, Período e Ranking (vivos desde #1078), rodapé do Rascunho, cabeçalho e total do Preflight, custos e metadados do Preflight, fecho do Preflight, Acompanhar (progresso e parciais), Decidir (cabeçalho, evidência, filtros, grade, nota). Ficam marcadas com `COPIED:start`/`COPIED:end`.
- `combo.html` (extra, `/combo/configure`): shell AppNav com Combo ativo, Template Information, Market Data, Timeframe, Período, Direction, Deep Backtest e walk-forward, dica de período e impedimentos, card Otimizar.
- `optimize.html` (extra, `/combo/optimize`): shell AppNav, Strategy Template, Timeframe, Parameter Ranges e Run Optimization, painel "Ready to Optimize".

O delta está só nos blocos `DELTA:start`/`DELTA:end`: o seletor de ativos, o bloco "Fora desta varredura" e o CTA do Preflight, a cópia antes do clique e o aviso ao Otimizar e ao rodar (com o progresso do lote na Otimização), e o painel "Demonstração". O painel fica no fim de cada página, sem `position:fixed`, e não cobre conteúdo.

## Goals / Non-Goals

**Goals:**

- Catálogo com todos os pares spot USDT, todas as ações e todos os ETFs da Binance, menos RIGHT e derivativos. A contagem precisa ser verificável contra a Binance.
- O mesmo seletor nas três telas: pesquisa por símbolo e nome, filtro por classe com contagens, paginação, vários ativos e "Todos do filtro (N)", e classe, negociação e histórico separados em cada linha.
- "Todos do filtro (N)" com confirmação que mostra quantos entram e quantos marcados ficam de fora.
- Ativo marcado (suspenso, fora de mercado, sem negociação, sem regras ou removido) aparece com estado e motivo, sem caixa de seleção ativa: não pode ser escolhido para análise nova. Em seleção ou favorito antigo, aparece marcado e fica de fora com aviso.
- Ação e ETF são escolhíveis e geram aviso claro ao rodar. A API recusa com código e motivo.
- Falha da Binance aparece por classe: com lista anterior há aviso e a data da lista; sem lista há erro e "Tentar de novo". Nunca lista vazia nem fixa.
- Identidade estável: favoritos e resultados de cripto continuam apontando para o mesmo ativo.

**Non-Goals:**

- Coleta de histórico de ações e ETFs (#1118) e execução de análises com essas classes (#1119 a #1121).
- Disponibilidade da conta e ordens (#1124). Migração de favoritos legados sem `/` (#1126).
- Pares cripto cotados em BTC, USDC, EUR e outras moedas.
- Mudar Monitor, Favoritos, ranking, período ou Short. A regra "marcado não entra em análise nova" vale para as análises iniciadas nas três telas; Monitor, Favoritos e a reabertura de resultados salvos não mudam.

## Decisions

1. **Página primária = `/combo/discovery`; extras `/combo/configure` e `/combo/optimize`.** As três têm o seletor com copy visível, então cada uma ganha um clone próprio. O index não é um painel das três. Alternativa rejeitada: clonar só a Descoberta, o que deixaria a Otimização sem desenho da troca do texto livre.

2. **Um componente compartilhado, "Seletor de ativos".**
   - Estrutura de cima para baixo: contagem selecionada por classe, frescor do catálogo, aviso de falha, pesquisa, filtros `Todas · Cripto · Ações · ETFs` com contagem, lista paginada, `Todos do filtro (N)`, `Limpar seleção`, confirmação inline e "Selecionados" com chips removíveis.
   - O eixo "Símbolos" da Descoberta passa a se chamar "Ativos", porque inclui ações e ETFs, e perde a "Edição avançada". O seletor inline já cobre busca, classe e paginação.
   - O eixo Templates não muda: o protótipo clona o bloco vivo (contagem, "Seleção manual", chips, "Edição avançada" e busca inline). Na grade do Rascunho, Ativos ocupa a linha inteira por causa da densidade; Templates fica na sua própria linha, com o mesmo conteúdo.
   - No Combo, o seletor substitui o rádio `Todos/Seleciona` e a lista dupla. O Top 10 continua (incumbente), mas só adiciona os negociáveis da lista. `Limpar (1 ativo)` continua voltando para BTC/USDT, como hoje.
   - Na Otimização, o seletor é o mesmo da Descoberta: vários ativos, "Todos do filtro (N)" com confirmação e "Limpar seleção". Não há Top 10, que não existe na página viva. Sem `?symbol=`, a seleção inicial continua BTC/USDT, como hoje (decisão 7).
   - Alternativa rejeitada: manter três seletores e só trocar a fonte, o que contraria o "mesma pesquisa" do Entra.

3. **Cada linha separa três fatos.**
   - Classe: Cripto, Ação ou ETF.
   - Negociação: `Negociável`, `Suspenso`, `Fora de mercado`, `Sem negociação`, `Sem regras de negociação` ou `Removido`.
   - Histórico: `Histórico local desde …`, `Histórico sob demanda` (cripto ainda sem candles locais), `Histórico não coletado` (ação e ETF até a #1118) ou `Histórico local até …` (marcados).
   - Ativo marcado ganha borda tracejada, caixa de seleção desabilitada e motivo na linha, com o complemento "Não pode ser escolhido para análise nova; aparece para explicar resultados e favoritos antigos." A disponibilidade da conta não aparece (#1124).
   - Frescor do catálogo e histórico usam `--text-tertiary` (6,1 a 6,8:1 nos fundos do seletor), não `--text-muted`.

4. **"Todos" = filtro atual, por soma, com confirmação.**
   - O botão mostra `Todos do filtro (N)`, em que N conta só os negociáveis da classe e da pesquisa atuais.
   - A confirmação inline (`role=alertdialog`) diz, por exemplo: "Incluir 3.112 ETFs negociáveis na seleção? 16 ativos marcados ficam de fora: suspensos, fora de mercado, sem negociação, sem regras ou removidos não podem ser escolhidos para análise nova. O que já está selecionado continua."
   - Ao abrir, o foco vai para "Incluir". Esc e "Cancelar" fecham sem mudar nada e devolvem o foco a "Todos do filtro".
   - Confirmar soma os ativos à seleção como itens explícitos.
   - Não existe mais "catálogo inteiro com exceções" (MODIFIED em `discovery-catalog-selection`). A soma vem da palavra "incluídos" do Entra, e a confirmação mostra o total.
   - Alternativa rejeitada: substituir a seleção, o que apagaria escolhas anteriores sem pedir.

5. **Ativo marcado não pode ser escolhido para análise nova (decisão de Alan, 20/10/2026).** Substitui a leitura anterior ("escolhido individualmente") e a decisão 4 do body.
   - Na pesquisa: aparece com classe, estado, histórico e motivo, mas sem caixa de seleção ativa. Clicar na linha não muda a seleção. "Todos", Top 10 e qualquer ação de lote também o deixam de fora.
   - Seleção antiga: rascunho, snapshot, favorito ou `?symbol=` que contenha um ativo marcado reidrata a lista como está. Em "Selecionados", o ativo aparece tracejado, com o estado e "fica de fora", sempre antes do "+N". A contagem diz "1 marcado fica de fora", e uma nota sob "Selecionados" diz que a Binance pausou ou retirou o ativo e que ele não entra em análise nova. O × o remove, e depois ele não volta pela pesquisa.
   - Ao rodar: a Descoberta lista o ativo em "Fora desta varredura" com o motivo da Binance. Combo e Otimização dizem o mesmo na cópia sob o botão, antes do clique, e no aviso depois. Se nada sobra para rodar, nada é executado.
   - Backend: otimização, lote e preflight da Descoberta recusam ou excluem o ativo marcado (decisão 14).

6. **Aviso de classe ao rodar, no padrão de exclusão que a Descoberta já usa.**
   - Descoberta: o Preflight já exclui combinações incompatíveis com motivo (`exclusions`, `excluded_count`). Ação e ETF ganham o motivo "análise ainda não disponível para ações e ETFs". O bloco "Fora desta varredura: N ativos (K combinações)" lista os 3 primeiros e "e mais N". A varredura inicia com as combinações de cripto. Se só houver ações e ETFs, o Preflight bloqueia com esse motivo.
   - Combo: a cópia sob Otimizar diz, antes do clique, o que roda e o que fica fora. Com só ação ou ETF ela diz "Nada será executado nem salvo: NVDA (Ação) — a análise ainda não está disponível para ações e ETFs.", e Otimizar mostra o alerta sem executar nem salvar. No lote misto, roda só a parte cripto e o aviso lista o que ficou fora.
   - Otimização: a mesma regra do lote do Combo (decisão 7). Com só ação, ETF ou marcado, nada é iniciado. No lote misto, roda a parte cripto e o aviso lista o que ficou fora.
   - O que conta é quantos pares rodam depois de tirar ações, ETFs e marcados: 1 segue o caminho de 1 ativo; 2 ou mais seguem o lote.
   - Em todos os casos a seleção fica preservada e há uma nota fixa sob "Selecionados". Os textos dizem "fora" e o motivo, para que o aviso de ação/ETF e o de marcado leiam igual nas três telas.
   - Alternativa rejeitada: bloquear qualquer seleção mista, porque obriga a desfazer escolhas e diverge do incumbente da Descoberta.

7. **Otimização: sem texto livre, com vários ativos e o lote que o Combo já usa (decisão de Alan, 20/10/2026).**
   - Seleção: o seletor completo (decisão 2). `?symbol=` que existe no catálogo pré-marca o ativo. Se ele estiver marcado, entra como seleção antiga e fica de fora (decisão 5). Se não estiver no catálogo, nada é marcado e aparece "XYZ/USDT não está no catálogo da Binance". O backend `/combos/optimize` valida o ativo contra o catálogo.
   - O que roda: só pares cripto negociáveis.
     - Com 1 par, a página faz o que faz hoje: `POST /combos/optimize`, e o resultado aparece no painel ao lado ("Optimization Complete").
     - Com N pares, a página chama o lote do Combo, `POST /combos/backtest/batch`, com os `symbols` que rodam e o que a página já manda para 1 ativo (template, timeframe, datas, faixas). Os demais campos ficam no padrão do lote. Roda uma otimização por ativo, com a mesma configuração. O melhor resultado de cada um vira favorito novo "gerado em lote" (tier 3); favorito igual não é sobrescrito e conta como ignorado.
   - Como os resultados aparecem: sob Run Optimization, o mesmo painel de progresso do Combo ("0 de N ativos", ativo atual, tempo decorrido e restante, Pausar, Encerrar). No fim, o mesmo resumo: "X sucesso, Y falha, Z ignorado(s)", erros por ativo e o link "Abrir Strategy Favorites". O painel "Ready to Optimize" continua para o caso de 1 ativo.
   - Cópia antes do clique: "1 ativo: otimiza e mostra o resultado ao lado." ou "N ativos: lote, uma otimização por ativo com o mesmo template, timeframe e faixas. O melhor resultado de cada um é salvo em favoritos.", mais "Fora: …" quando há ação, ETF ou marcado.
   - Nenhum fluxo novo: lote, progresso, resumo e favoritos são os do Combo. A página não ganha campos de período, direção, Deep Backtest nem walk-forward.

8. **Falha da Binance por classe.**
   - Com lista anterior: aviso âmbar ("Ações e ETFs desatualizados… Mostrando a lista válida de 19 out. 2026, 18:00"). A pesquisa e a escolha continuam.
   - Sem lista: um alerta vermelho só, no topo do seletor ("Cripto indisponível… Tentar de novo", com o botão em linha própria). A contagem da classe vira "indisponível". O filtro Cripto mostra uma linha neutra que remete ao alerta, sem repeti-lo e sem paginador.
   - Pesquisa durante a falha: sem resultado, o vazio diz "Nenhuma ação ou ETF para "btc". Cripto está indisponível agora por falha da Binance…", em vez de mandar conferir o símbolo. Sem resultado, o paginador some.
   - A seleção feita é preservada.
   - No protótipo, esses estados vêm do painel "Demonstração · catálogo", no fim da página. Ele também restaura uma seleção antiga com WAVES/USDT (index e combo) e abre `?symbol=` (optimize). Os demais estados vêm de interação.

9. **Catálogo persistido (P3, como).**
   - Tabela PostgreSQL `asset_catalog` com uma linha por ativo. Campos: `asset_id`, classe, símbolo, nome, ids da Binance, estado e motivo, `first_seen_at`, `last_seen_at`, `removed_at` e resumo de cobertura.
   - Tabela `asset_catalog_refresh` com uma linha por atualização e classe. Campos: início, fim, ok ou erro com motivo, e contagens de entrada, excluídos por motivo e resultado.
   - Migração Alembic. Sem SQLite em runtime.

10. **Identidade (P3).**
    - `asset_id = binance:spot:<BASE>/USDT` ou `binance:equity:<ac>`, em que `ac` é o identificador `EQ_*` da Binance.
    - Favorito ou resultado com `/` resolve para `binance:spot:…`. Ticker sem `/` não é resolvido para ação.
    - Payloads de análise passam a levar `asset_id` junto do `symbol`. Cripto continua com `symbol: "BTC/USDT"` por compatibilidade.

11. **Reconciliação e exclusões (P3).**
    - Ações e ETFs: união por `ac` entre `get-symbols-static` e `get-exchange-info`.
    - Excluídos e contados por motivo: `t=RIGHT`, nome terminado em Warrant(s), Right(s) ou Rights Offering, "Contingent Value Right", sufixos `.WS` e `.RT`, e o registro sem cadastro estático (classe desconhecida).
    - Na leitura de 20/10: 7.970 na união − 10 excluídos = 7.960 escolhíveis (4.832 ações, 3.128 ETFs).
    - Mapa de estado: `BUY_SELL` → Negociável; `OFFMARKET` → Fora de mercado; `NONE` → Sem negociação; ausente das regras → Sem regras de negociação; ausente das duas listas numa atualização posterior → Removido.
    - Cripto: `api/v3/exchangeInfo`, `quoteAsset=USDT`. `TRADING` com spot permitido → Negociável; `BREAK`, `HALT` ou spot desligado → Suspenso; sumiu → Removido.
    - Exclusões explícitas de `excluded_symbols.json` ficam fora.
    - `dlt` (remoção anunciada) vira motivo informativo e não muda o estado. Campos de sentido não documentado (`os`, `att`, `opt`) ficam guardados sem interpretação.

12. **Atualização e falha (P3).**
    - Job agendado por classe, a cada 6h, mais um gatilho manual de admin para "Tentar de novo".
    - Conta como falha: rede, 429, HTTP 200 com `code ≠ 000000`, schema inesperado, ou resultado menor que 50% da última lista válida.
    - Na falha, a atualização não toca as linhas da classe e grava o erro. A API devolve `freshness` por classe (`ok | stale | unavailable`, `updated_at`, motivo).
    - Backfill de removidos: os símbolos com `/` presentes em favoritos e resultados que não estão no catálogo entram como Removido na primeira atualização.

13. **API (P3).**
    - `GET /assets/catalog?q=&class=&page=&page_size=` devolve `items`, `total`, `eligible_total`, contagens por classe e `freshness`.
    - `POST /assets/catalog/resolve {q, class}` devolve os `asset_ids` negociáveis do filtro, para o "Todos".
    - A pesquisa ignora caixa e acento. A ordem é: símbolo exato, prefixo, depois nome.
    - Tamanho de página: 6 no protótipo, decidido no Apply.
    - `GET /exchanges/binance/symbols` continua por compatibilidade, lendo do catálogo os cripto negociáveis.

14. **Recusa estruturada (P3).** `_ensure_crypto_symbol(s)` passa a usar o catálogo.
    - Ação ou ETF recebe HTTP 422 com `detail={code:"asset_class_not_supported", asset_class, assets:[…], message:"Análise ainda não disponível para ações e ETFs…"}`.
    - Ativo marcado em `/combos/optimize` e `/combos/backtest/batch` recebe 422 com `code:"asset_not_selectable"`, o estado e o motivo. No preflight da Descoberta, cada combinação dele vai para `exclusions` com esse motivo.
    - Símbolo desconhecido recebe `code:"asset_not_in_catalog"`.
    - O frontend manda ao lote só os pares que rodam. Uma chamada direta com ação, ETF ou marcado é recusada inteira. O frontend mostra `message`. `_ensure_crypto_data_source` não muda.

15. **Ingestão sem fallback fixo (P3).** `resolve_binance_ohlcv_symbol_universe` lê os cripto negociáveis do catálogo. Sem catálogo e sem `exchangeInfo`, a rodada registra a falha e não roda. A ordem de prioridade de `_apply_limit` vira uma constante só de ordenação. `MARKET_OHLCV_SYMBOL_LIMIT` continua só na ingestão e nunca toca o catálogo.

## Risks / Trade-offs

- [Risco] As rotas BAPI de ações não têm contrato público estável → Mitigação: adaptador isolado, validação de schema e de `code`, guarda de queda brusca e falha visível (decisões 11 e 12).
- [Risco] Selecionar milhares de ativos estoura o limite de combinações da Descoberta → Mitigação: o limite atual do Preflight continua mandando, sem mudança.
- [Risco] A regra atual de sufixo `UP`/`DOWN` de `is_excluded_symbol` também exclui SYRUP/USDT, um par legítimo → Mitigação: P3. O Apply revê a regra contra a lista atual. Tokens alavancados UP/DOWN não constam mais no spot.
- [Risco] Seleções antigas da Descoberta em modo `all` → Mitigação: snapshots já guardam a lista concreta de símbolos e o restore reidrata essa lista.
- [Risco] Payload grande ao selecionar 3.112 ETFs → Mitigação: P3 (`resolve` no servidor; o rascunho guarda os ids).
- [Risco] "Todos do filtro" na Otimização pode disparar um lote de 511 pares → Mitigação: a confirmação mostra a contagem antes, e o lote já tem Pausar, Encerrar e "ignorado" para favorito repetido. É o mesmo risco do Combo hoje.
- [Trade-off] Cores âmbar, azul e vermelha (`#fbbf24`, `#93c5fd`, `#ff8294`) e tamanhos de 10, 11 e 18px vêm do incumbente clonado e o hook do Impeccable os sinaliza. Ficam como estão para ser fiéis à página viva.

## Migration Plan

1. Alembic cria `asset_catalog` e `asset_catalog_refresh`. A primeira atualização popula as duas classes e faz o backfill de removidos.
2. As rotas novas entram com a compatibilidade de `/exchanges/binance/symbols`. Depois o frontend troca os três seletores.
3. As recusas 400 genéricas viram 422 estruturadas. Clientes que liam o texto em inglês passam a ler `detail.message`.
4. Rollback: os seletores voltam para `/exchanges/binance/symbols`. As tabelas ficam sem leitor. Nenhum dado de favorito ou resultado muda.
5. PROD só por T16.

## Open Questions

Nenhuma de produto. As duas leituras que a crítica A levou a Alan foram decididas por ele em 20/10/2026 ([comentário](https://github.com/oalansilva/crypto/issues/1117#issuecomment-6282565608)):

- Ativo marcado não pode ser escolhido para análise nova (decisão 5).
- A Otimização aceita vários ativos e "Todos do filtro", e roda o lote do Combo (decisão 7).

O lote misto roda a parte cripto com aviso (decisão 6). Esse é o padrão de exclusões do Preflight vivo e vale igual no Combo e na Otimização.

## Apply contract

O Apply lê este `design.md` e os HTML em `frontend/public/prototypes/card-1117-catalogo-ativos/` como spec de layout.

**Contrato visível (não P3):**

- Seletor único nas três telas, com pesquisa, classe, paginação, vários ativos e os três fatos por linha.
- "Todos do filtro (N)" com confirmação, contagens de incluídos e de marcados, e soma à seleção. Esc e Cancelar fecham sem mudar nada e devolvem o foco ao botão.
- Ativo marcado sem caixa ativa e nunca escolhível para análise nova. Em seleção antiga aparece "fica de fora", antes do "+N", e o Preflight ou o aviso diz por quê.
- Eixo "Ativos" na Descoberta, sem "Edição avançada" de símbolos. Eixo Templates como no vivo.
- Ação, ETF e marcado: cópia antes do clique e aviso ao rodar com os textos das decisões 5 a 7. A Descoberta inicia só com cripto e bloqueia quando nada sobra.
- Otimização sem texto livre, `?symbol=` validado, vários ativos e "Todos do filtro". 1 par roda como hoje; N pares rodam o lote do Combo, com o mesmo progresso e resumo.
- Falha por classe: lista anterior com aviso, ou um único erro com "Tentar de novo". A pesquisa vazia durante a falha culpa a Binance, não o símbolo, e sem resultado não há paginador.
- Combo: default BTC/USDT, Top 10 e `Limpar (1 ativo)` como hoje.
- × dos chips com alvo de 44×44px.

**P3 aceito (Apply):** decisões 9 a 15, tamanho de página, nomes internos e de rotas, cadência do job, limite de 50% e sua configuração, regra UP/DOWN, como a seleção é guardada no rascunho e no snapshot, combo vazio após remover o último chip (o incumbente volta ao padrão), testes. Também: a Otimização passa a usar `authFetch` para o lote (rota de admin); quais padrões do lote valem para os campos que a página não tem; cópia "Incluir 3 (2 novos)" quando parte já está selecionada; variante compacta do seletor na coluna estreita da Otimização; chrome glass/zinc/roxo do vivo em `/combo/configure` e `/combo/optimize`; "Edição avançada" de Templates fica inerte no protótipo (o workbench vivo não muda); amostra de 31 itens e Top 10 com AVAX/MATIC fora da amostra.

## Prototype

- Canônico: `frontend/public/prototypes/card-1117-catalogo-ativos/index.html`, clone de `/combo/discovery` com o delta só no eixo de ativos e no Preflight. Vista inicial: Montar com BTC/USDT e NVDA selecionados, Preflight com 1 combinação e "Fora desta varredura: 1 ativo". Interações:
  - pesquisar `nvidia` → `Todos do filtro (3)`;
  - escolher a classe ETFs → `Todos` → "3.112 ETFs negociáveis… 16 marcados"; Esc fecha e devolve o foco;
  - pesquisar `waves` → Suspenso com motivo, caixa desabilitada, `Todos (0)`;
  - pesquisar `zzzz` → vazio com orientação;
  - `Limpar` → impedimento "Escolha ao menos 1 ativo.";
  - Demonstração → "Restaurar rascunho antigo com WAVES/USDT" → chip "fica de fora", nota e "Fora desta varredura" com o motivo da Binance;
  - Demonstração → falha de ações/ETFs ou de cripto (pesquisar `btc` durante a falha).
- Extra `combo.html`: clone de `/combo/configure`. Delta no seletor, no Top 10, na cópia sob Otimizar e no aviso (só NVDA → "Nada será executado nem salvo…"; misto → "Lote iniciado com 8 pares cripto. Fora do lote: NVDA (Ação), SPY (ETF)"; seleção antiga BTC+WAVES → roda BTC e WAVES fica de fora).
- Extra `optimize.html`: clone de `/combo/optimize` com vários ativos. BTC+ETH+QQQ → "Lote iniciado com 2 pares cripto", QQQ fora, progresso "0 de 2 ativos". Cripto → Todos (511) → lote de 511. Só QQQ → nada roda. Demonstração abre `?symbol=XYZ/USDT` (não marca nada), `?symbol=NVDA` e `?symbol=WAVES/USDT` (favorito antigo: marcado, fica de fora, nada roda).
- Nenhuma página é um painel ANTES/DEPOIS nem "N estados".

## Prototype Validation

Evidência do rework r1 (20/10/2026). A evidência anterior (sha256 `adc5399a…`, `273d89b5…`, `cd932a7e…`) não vale mais.

| Arquivo | Bytes | sha256 | COPIED | DELTA |
|---|---|---|---|---|
| `index.html` (canônico) | 106.147 | `a75e14057dbb2a1a1f4ce3ac2065ee4b411044ba0e9e3bd9dc7630b7f60bbfee` | 20/20 pares, 34.389 B | 4/4 |
| `combo.html` | 58.748 | `419b0b2b6832e8d53553ddb97fa2d5c095bf15d1227fd6dc1f76b24fadc952ff` | 8/8 pares, 7.100 B | 3/3 |
| `optimize.html` | 55.421 | `597672b03a6baf428fe14512099da4643937df116986b71d8fa5dd5762cc8d7d` | 4/4 pares, 4.695 B | 3/3 |

- O CSS de `<head>` clonado não está marcado (mesma convenção do #1078), por isso o gerado inclui o CSS do delta, o CSS do bloco Templates e o JS de demonstração.
- Gate: `design_token_gap` = None; `evaluate_clone_gate` = True com `route-landmarks.yaml` (landmarks `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`); `classify(index.html, /combo/discovery)` = PASS.
- Detector `.agents/skills/impeccable/scripts/detect.mjs --json`: `[]` nas três telas.
- Navegador: `python3 -m http.server 53171 --bind 127.0.0.1` (cwd `frontend/public`, processo morto no fim), URL `http://127.0.0.1:53171/prototypes/card-1117-catalogo-ativos/` mais `combo.html` e `optimize.html` (e `?symbol=XYZ/USDT`, `?symbol=NVDA`, `?symbol=WAVES/USDT`). Playwright Python com Chromium headless shell 1243, `locale pt-BR`, `colorScheme dark`, viewports 1440×900 e 390×844. Digest servido = disco nas três telas.
- Resultado: **223/223 asserts PASS**, zero erro de console e zero `pageerror`, sem scroll horizontal na carga nem depois das interações.
- Ações e asserts, nas três telas e nos dois viewports:
  - "nvidia" encontra NVDA primeiro e dá `Todos do filtro (3)`; o filtro Ações fica com `aria-pressed=true` e só mostra ações;
  - BTC/USDT, NVDA, SPY e QQQ aparecem na primeira página;
  - WAVES/USDT aparece Suspenso, com o motivo "status BREAK" e "Não pode ser escolhido"; a caixa está desabilitada, clicar na linha não muda a contagem, e `Todos do filtro (0)` fica desabilitado;
  - ETFs → `Todos do filtro (3.112)` → `alertdialog` com 3.112 e 16 marcados de fora; Esc fecha, a seleção não muda e o foco volta ao botão; Cancelar não muda; Incluir soma 3.112 ETFs e deixa IBIC (Fora de mercado) de fora;
  - × dos chips com 44×44px; `.ap-fresh` e `.fact.hist` em `--text-tertiary` (#929aa5);
  - painel Demonstração sem `position:fixed`, e o filtro Cripto não fica coberto;
  - falha de cripto: um único alerta, com "Tentar de novo" em linha própria; "btc" diz falha da Binance, não "Confira o símbolo", e o paginador some; o filtro Cripto mostra uma linha neutra, sem segundo alerta; "Tentar de novo" restaura a lista.
- Só em `index.html`: landmarks visíveis; Templates clonado ("Edição avançada", busca inline, 17 templates); inicial BTC+NVDA com NVDA em "Fora desta varredura"; Limpar → "Escolha ao menos 1 ativo."; só NVDA bloqueia; rascunho antigo com WAVES → primeiro chip "fica de fora", Preflight com "WAVES/USDT (Cripto, Suspenso) … não entra em análise nova", nota e "1 marcado fica de fora".
- Só em `combo.html`: default BTC/USDT e `Limpar (1 ativo)`, sem rádio Todos/Seleciona; só NVDA → cópia "Nada será executado nem salvo… ações e ETFs" antes do clique (sem "favoritos") e alerta ao Otimizar; Top 10 + SPY → cópia de batch com o que fica fora, e "Lote iniciado com 8 pares cripto" com NVDA e SPY fora; Top 10 sem marcados; seleção antiga BTC+WAVES → cópia e aviso com WAVES fora.
- Só em `optimize.html`: sem `input[type=text]` nem `textarea`; linhas com checkbox e "Todos do filtro"; BTC+ETH+QQQ → "Lote iniciado com 2 pares cripto", QQQ fora e "0 de 2 ativos"; Cripto → `Todos do filtro (511)` → confirmação com 511 e 214, Esc devolve o foco, Incluir → 511 selecionados → lote de 511; só QQQ → cópia e alerta sem rodar; `?symbol=XYZ/USDT` sem marcar nada, `?symbol=NVDA` marca NVDA, `?symbol=WAVES/USDT` marca como fora e nada roda.
- browser_gate: a dupla A/B não roda de novo (teto 1+1+1). O pai publica a URL pública.

## Impeccable

Operate, refinamento de três incumbentes. Tokens Binance clonados. O delta usa a rampa 12/13/14px do `DESIGN.md`, alvos de 44px (inclusive o × dos chips), foco visível, `aria-pressed` nos filtros, `role=alertdialog` na confirmação com Esc, `aria-live` nas contagens e `--text-tertiary` nos textos de 12px. A seção de crítica fica para o pai, depois da dupla.

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework (r1, com as decisões de Alan no Design e os achados mecânicos da dupla). Nenhum segundo rework.

- Autor: `design-autor 1117 a1` (isolado). Rework: `design-autor 1117 r1` (isolado).
- Assessment A: `assessment-a 1117 a1` (isolado). Assessment B: `assessment-b 1117 a1` (isolado, detector + navegador).
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1117-catalogo-ativos/
- Protos extras: https://dev.criptofarol.com.br/prototypes/card-1117-catalogo-ativos/combo.html e https://dev.criptofarol.com.br/prototypes/card-1117-catalogo-ativos/optimize.html
- Snapshots: `.impeccable/critique/1117-card-1117-catalogo-ativos-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1**: nenhum.
- **P2 de juízo, decididos por Alan no Design** ([comentário](https://github.com/oalansilva/crypto/issues/1117#issuecomment-6282565608)):
  - Ativo pausado ou retirado pela Binance não pode ser escolhido para análise nova; ele aparece marcado só para explicar resultados e favoritos antigos.
  - A otimização também tem lote.
  - Os dois foram aplicados no r1.
- **P2 mecânicos, corrigidos no r1:**
  - copy do Combo com só ação ou ETF;
  - vazio da pesquisa durante a falha de cripto;
  - Templates clonados do vivo;
  - contraste AA de `.ap-fresh` e `.fact.hist`;
  - Esc na confirmação do "Todos";
  - painel Demonstração fora de `position:fixed`;
  - × dos chips com 44px;
  - "Tentar de novo" em 390px.
- **P3 aceitos, para o Apply:**
  - o protótipo usa amostras na paginação e no Top 10;
  - "Incluir 3 (2 novos)";
  - seletor compacto na coluna estreita da otimização;
  - visual glass/roxo vivo no Combo e na Otimização;
  - "Edição avançada" de Templates sem ação;
  - lote da otimização por rota de admin (`authFetch`);
  - padrões do lote para campos ausentes na otimização;
  - contagem de Templates herdada a 4,01:1 (igual ao vivo);
  - overlay `detect.js` não injectado (a evidência é o detector por CLI e o Playwright);
  - as decisões 9–15 são mecanismo.
- **Disposition:** "não entra em análise nova" vale para as análises iniciadas nas três telas. Monitor, Favoritos e a reabertura de resultados salvos não mudam (Non-Goals).

### Proxies

- `design.md` words: 4725 (antes desta seção)
- HTML generated vs copied (`index.html`): 71758 vs 34389
- Spawns: 4
- `proxy modelo: design-autor → Opus 5.5 (claude-opus-5-5)` (a1 e r1)
- `proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5)`
- `proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5)`

Design Agent verdict: PASS
