## Why

Em PROD o administrador abre `/monitor` com sessão válida e favoritos crypto no servidor; o servidor responde 200, mas o browser não recebe o JSON (corte de proxy) e o quadro pinta o erro do #975 à primeira. Segundos depois a mesma carga passa. Este card trata a **reação do app** a essa falha transitória — não o proxy.

## Problema

O administrador abre o Monitor em produção com sessão válida e favoritos crypto no servidor, e o quadro diz que a lista não chegou — quando o servidor respondeu 200 e a mesma carga passa segundos depois. «Tentar de novo» repete o erro enquanto o proxy da rede corporativa estiver no handshake. O operador acha que perdeu as estratégias ou que o produto está fora.

## História

Como operador que abre o Monitor a partir de uma rede corporativa (Zscaler ou proxy equivalente), quero que uma falha transitória de rede na carga seja reabsorvida pelo app, para ver os sinais e as preferências sem ficar preso num erro falso nem bater no login sem motivo.

## Entra

- Entrega já decidida: o **app** reabsorve a falha transitória (não isentar o proxy, não túnel).
- Com sessão válida e favoritos crypto no servidor, uma falha transitória na carga da lista **não** é a última palavra à primeira: o operador não fica preso no erro do #975 só porque o pedido autenticado foi cortado.
- O quadro espera dezenas de segundos (o tempo de uma abertura presa no proxy) e só então pinta o erro do #975. Se o proxy ficar preso minutos, o operador usa «Tentar de novo».
- Enquanto espera, o quadro mostra «Carregando sinais...» e os KPIs **não** aparecem como verdade (não 0 como se não houvesse sinais).
- Na mesma abertura, com sessão válida, nem o quadro de erro da lista nem o aviso «Não foi possível carregar preferências do monitor.» ficam à mostra se a carga acaba por passar.
- Depois de um erro de carga, «Tentar de novo» só pede de novo a lista já calculada — sem recomputar. «Atualizar» continua a recomputar.
- O caso do incidente: conta do administrador, 11 estratégias no servidor, sessão válida. Depois de abrir a tela, o quadro lista os pares (sem o operador ter de mudar de rede).
- Se a sessão **morreu** de verdade, o operador vai ao login — não fica no quadro de erro.
- Falha real e persistente **continua** a usar o erro de carga do #975 («Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou…» + «Tentar de novo»), sem voltar a fingir catálogo vazio.

## Não entra

- Alterar Caddy, compressão, tamanho do payload ou backend (`/api/opportunities/` devolve 200; não é a causa).
- Configurar ou isentar o Zscaler / proxy do lado do cliente (fora do controle do produto).
- Alongar a sessão ou mudar quanto tempo o login dura.
- Redesign do quadro, KPIs, filtros ou copy dos estados (mantém #970/#975).
- Telemetria/alertas de proxy corporativo.
- Favoritos, Início e Carteira ficam com o contrato do #983; se o corte de rede voltar a pintar erro lá, é outro card.

## What Changes

Decisões gravadas (não reabrir): Qs grelhadas todas A — só `/monitor`; o app reabsorve a falha transitória; espera dezenas de segundos em «Carregando sinais...» antes do erro #975; KPIs não pintam 0 como verdade durante a espera; toast de preferências não fica à mostra se a carga passa; «Tentar de novo» relê a lista já calculada; «Atualizar» recomputa; sessão morta → login; falha persistente → copy #975. Sem Caddy/backend/Zscaler/TTL/redesign/Favoritos-Início-Carteira.

- Com sessão válida e favoritos crypto no servidor, um corte transitório na carga **não** pinta o erro do #975 à primeira. O quadro espera dezenas de segundos.
- Enquanto espera: «Carregando sinais...»; KPIs **não** aparecem como 0 verdadeiro.
- Se a carga acaba por passar na mesma abertura: lista visível; **ausente** o quadro de erro; **ausente** o aviso «Não foi possível carregar preferências do monitor.».
- Caso do incidente (11 estratégias, sessão válida): depois de abrir, o quadro lista os pares sem o operador mudar de rede.
- «Tentar de novo» relê a lista já calculada (sem recomputar). «Atualizar» continua a recomputar.
- Sessão morta de verdade → login. Não fica no quadro de erro.
- Falha persistente continua o erro do #975 + «Tentar de novo»; não finge catálogo vazio.
- Copy dos estados #970/#975, board e filtros **não** mudam. Backend/Caddy **não** mudam.

## Capabilities

### New Capabilities

- `monitor-transient-load`: espera de dezenas de segundos em carga transitória; KPIs não como 0 verdadeiro; toast de preferências some se a carga passa; «Tentar de novo» relê sem recomputar vs «Atualizar» recomputa; sessão morta → login; falha persistente → copy #975.

### Modified Capabilities

- `monitor`: falha transitória de rede na carga autenticada **não** é a última palavra à primeira; KPIs durante a espera não pintam 0 como verdade; falha persistente mantém o erro de carga actual.
- `monitor-first-load`: a primeira visita com favoritos crypto espera a reabsorção do corte transitório antes de pintar o erro do #975; se a lista chega, o quadro mostra os sinais.

## Impact

- Frontend: `MonitorStatusTab.tsx` (carga / KPIs / toast de preferências / «Tentar de novo» sem `refresh=true`); `authFetch.ts` (hoje só retenta `AbortError`; `TypeError: Failed to fetch` de reset vai ao `catch` — *como* da reabsorção, sem alongar TTL). `MonitorDashboardTab` permanece morto.
- Backend / Caddy / compressão / payload: sem mudança (`GET /api/opportunities/` já devolve 200).
- Favoritos, Início e Carteira: contrato do #983 intacto; fora deste card.
- Protótipo: clone `/monitor` (canónico = lista após reabsorção) + irmãos de estado `carga.html` / `erro.html` / `sessao.html` (login). Sem extra `/favorites`. Sem painel ANTES/DEPOIS no index.
