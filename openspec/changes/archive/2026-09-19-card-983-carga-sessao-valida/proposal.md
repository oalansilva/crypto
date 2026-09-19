## Why

Em PROD o administrador abre `/favorites` com sessão válida e catálogo crypto intacto (`GET /api/favorites/` 200 no backend) e vê o erro de carga do #970 — «Não foi possível carregar as estratégias favoritas.» / «Carga falhou» / «Tentar de novo», com a copy «a sessão continua válida». «Tentar de novo» costuma repetir o erro. A mesma janela de renovação pinta falha falsa no Início, no Monitor e na Carteira. #970 já distingue vazio de erro; este card trata a **causa** da carga falhar quando a sessão ainda vale.

## Problema

O administrador abre Favoritos em produção com sessão válida e estratégias crypto gravadas, e a tela diz que a carga falhou — mesmo com o catálogo intacto no servidor. «Tentar de novo» costuma repetir o erro.

## História

Como administrador que abre Favoritos no dia a dia, quero que a grade carregue as estratégias crypto já salvas enquanto a sessão está válida, para escolher o que entra no Monitor sem ficar preso num erro falso nem achar que perdi o catálogo.

## Entra

- Com sessão válida e favoritos crypto gravados, abrir `/favorites` lista essas linhas — não o erro de carga, não «Nenhuma estratégia favorita encontrada».
- O caso do incidente: conta do administrador, filtros em Todos, catálogo crypto no servidor, `GET /api/favorites/` 200 no backend. Depois de abrir a tela, a grade lista os pares.
- «Tentar de novo» com o catálogo intacto e sessão válida termina na lista, não num erro preso. Um pedido a meio do caminho não deixa a tela no erro se a lista chegou (ou vai chegar) com sucesso.
- Durante a renovação do acesso, Favoritos **não** mostra erro de carga com «a sessão continua válida» quando o catálogo está no servidor.
- Na mesma janela, Início e Monitor deixam de mostrar a mesma falha falsa da lista: o operador vê os favoritos nessas telas, não o erro de carga mentiroso.
- Na mesma janela, a Carteira deixa de mostrar o erro falso («Erro ao carregar» / «Falha ao carregar saldos»): o operador vê os saldos. Falha real de rede ou resposta inválida nessa tela continua a mostrar esse erro.
- Se a sessão **morreu** de verdade, o operador vai ao login — não fica na grade de erro fingindo que a sessão vale.
- Falha real de rede ou resposta inválida **continua** a usar o erro de carga do #970 («Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»), sem voltar a fingir catálogo vazio.
- Abrir gráfico / análise de um favorito continua a mostrar velas e trades.

## Não entra

- Redesign da grade (colunas, mobile, Excel, tiers).
- Desfazer o #970 (distinção vazio vs erro vs filtro; lista da grade sem velas).
- Alongar a sessão como solução de produto (mudar quanto tempo o login dura).
- Apagar ou migrar favoritos.
- Discovery, promoção a favorito, ou métricas da grade.
- Falha de credenciais da exchange, Telegram ou «quem sou eu» na mesma janela.

## What Changes

Decisões gravadas (não reabrir): Q1=A — Início e Monitor entram (falha falsa da lista). Q2=A — Carteira entra (erro falso dos saldos some; falha real continua o erro da Carteira). Não alongar a sessão. Não desfazer #970. Sessão morta de verdade → login. Falha real de rede em Favoritos → erro do #970.

- Durante a renovação do acesso, com catálogo no servidor, `/favorites` lista os pares — não o erro do #970 com «a sessão continua válida».
- Um 200 que chegou (ou vai chegar) ganha de abort / 401 transitório: «Tentar de novo» e um pedido a meio do caminho não deixam a tela no erro se a lista chegou ou vai chegar.
- Sessão morta de verdade (refresh esgotado, sem acesso recuperável) → login. Não fica na grade de erro fingindo que a sessão vale.
- Falha real de rede ou corpo inválido em Favoritos **continua** o erro do #970 + «Tentar de novo»; não volta a fingir catálogo vazio.
- Na mesma janela, Início `/home` deixa de pintar «Não foi possível carregar `/api/favorites`.» quando a lista está no servidor; o KPI mostra a estratégia, não a falha falsa.
- Na mesma janela, Monitor `/monitor` deixa de pintar a falha falsa da lista; o operador vê os sinais, não o erro mentiroso.
- Na mesma janela, Carteira `/external/balances` deixa de pintar «Erro ao carregar» / «Falha ao carregar saldos»; o operador vê os saldos. Falha real nessa tela continua esse erro.
- Abrir gráfico / análise de um favorito continua a mostrar velas e trades. Sem alongar TTL do login. Sem redesign.

## Capabilities

### New Capabilities

- *(nenhuma)* — o contrato visível alarga specs já existentes (#970 / Início / Monitor / Carteira).

### Modified Capabilities

- `favorites-load-states`: renovação com catálogo no servidor lista os pares; abort/401 transitório não pinta o erro do #970; 200 que chegou ou vai chegar ganha; sessão morta → login; falha real continua o erro do #970.
- `home`: na janela de renovação o KPI de favoritos mostra a estratégia, não «Não foi possível carregar `/api/favorites`.»; falha real do KPI continua essa copy.
- `monitor`: na janela de renovação a board não pinta a falha falsa da lista; falha real continua o erro de carga do Monitor.
- `external-balances`: na janela de renovação a Carteira mostra os saldos, não «Erro ao carregar» / «Falha ao carregar saldos»; falha real continua esse erro.

## Impact

- Frontend: `FavoritesDashboard.tsx` (query da lista vs abort / 401 transitório / `isError`); `authFetch.ts` e `authStore.tsx` (dois caminhos de sessão: axios no arranque vs fetch nas páginas — *como*, não alongar TTL); `HomePage.tsx` (`fetchJson` da lista sem refresh); `MonitorStatusTab.tsx` (`resolveHasCryptoFavorites` / board); `ExternalBalancesPage.tsx` (saldos vs 401 transitório). `MonitorDashboardTab.tsx` permanece morto no vivo.
- Backend: sem mudar o contrato da lista magra do #970; sem alongar TTL; sem apagar favoritos. Caddy `aborting with incomplete response` em `/api/favorites/` é síntoma do corte no cliente, não um redesign de API.
- Protótipo: clone `/favorites` (canónico, lista no caminho feliz da renovação) + irmão `erro.html` (falha real #970) + extras `monitor.html` / `inicio.html` / `carteira.html` (+ `carteira-erro.html` para falha real da Carteira). Sem painel ANTES/DEPOIS no index.
