## Why

Origem: [#968](https://github.com/oalansilva/crypto/issues/968). Gist = *superset* do cartão: a grelha decide a história; este pacote **copia** Problema, História, Entra / não entra. Não é segunda entrevista. Q2=B, Q3=A, Q4=A congeladas. Q1 reclassificada — *como* no `design.md`.

## Problema

Alan, dono da release, sofre: o código homologado chega ao disco de produção, mas um processo de longa duração fica em memória no código velho — e ele só descobre depois, pela lentidão da Descoberta, que a release não valeu por inteiro.

## História

Como Alan, dono da release,
quero que subir a release ponha a correr o código publicado em **todo** processo de produção que executa código do produto em memória,
para o que foi homologado passar a valer em produção sem eu ter que descobrir depois, pela lentidão, que um processo ficou no código velho.

Factos (não são decisão):

- Overlay `.covenant-flow/overlay.yaml`: DEV lista `criptofarol-dev-discovery-worker`; PROD não lista `criptofarol-prod-discovery-worker`. PROD lista `criptofarol-prod-candle-writer` e `criptofarol-prod-telegram-alert-scan`.
- Candle-writer e telegram-alert-scan são timers oneshot: carregam código em cada execução e não o mantêm em memória entre corridas. Backend, frontend, leads, runtime-worker e discovery-worker são units de longa duração (`Type=simple` / processo persistente).
- Deploy 16/09 reiniciou backend, frontend, leads e runtime-worker. O discovery-worker ficou no PID de 15/09 até restart manual em 17/09 12:17 UTC.
- Incidente #945: o lote de 16/09 publicou a varredura ~10× mais rápida (`cc5370c`, PR #961); em PROD a Descoberta continuava ~100 s por combinação (mediana 102 s) com código velho em memória.
- `release-guard` e as docs de release de setembro omitem discovery-worker na lista de services reiniciados. O `post` hoje não recusa evidência cujo `services=` falte um unit de longa duração. Em agosto a evidência ainda incluía discovery-worker.
- A lista de produção, desde que existe, nunca incluiu o worker de varredura. Em agosto a evidência de deploy ainda o listava (host/memória); em setembro o publish passou a seguir a lista incompleta.
- Inventário vivo no host (18/09): cinco processos de longa duração ativos; varredura no boot manual de 17/09 12:17 UTC; site, API, captação e runtime ainda no boot de 16/09 22:16 UTC. Dois jobs de uma execução com timer à espera. Nenhum outro unit de produção do produto.
- Q1 reclassificada («não percebi»; não é aceite A nem B): o eixo lista de produção vs processo de longa duração a correr fora da lista não fechou — *como* no Design. Intent extra: reiniciar os serviços em produção para garantir a última versão; jobs de uma execução continuam fora.

## Entra

- **Janela do publish (Alan):** na mesma janela do deploy de produção, reiniciar todos os processos que mantêm código do produto em memória (site, API, captação, worker de runtime, worker de varredura). Jobs agendados de uma execução (escrita de candles, scan de alerta Telegram) não entram nessa janela — a próxima corrida já lê o código novo; a evidência do dia regista-os assim.
- **Garantir última versão (Alan, Q1 sem A/B):** o publish reinicia os serviços de produção que mantêm código em memória. Não inclui os jobs de uma execução.
- **Fecho — processo parado (Q2 B):** se um processo de longa duração não ficar a correr depois do restart, o fecho pode passar desde que o site e a API respondam; isso é incidente à parte.
- **Fecho — recusa (Q4 A):** se a evidência de deploy não listar o restart dos processos de longa duração da janela, ou se um processo de longa duração a correr ainda estiver no código velho, o fecho recusa de forma visível e os cards não são dados como publicados. O que já foi ao disco e já reiniciou fica; não desfazer.
- **Fecho — Descoberta (Q3 A):** não exige ver a Descoberta a correr o comportamento novo nem cronometrar varredura nesta janela. A prova desta janela é o restart dos de longa duração e a evidência completa.
- **Âmbito (Alan):** só produção. Restart de desenvolvimento, novo comando de restart fora do fecho de release e reinício de base/proxy ficam fora deste card.
- Inventário: o worker de varredura entra na lista de produção do overlay (junto com os demais de longa duração).
- A nota de release do dia lista os processos reiniciados a partir do inventário de produção, não de uma lista memorizada no chat.

## Não entra

- Mudar o restart de desenvolvimento.
- Criar um caminho novo de restart de produção fora do fecho de release.
- Reiniciar PostgreSQL ou o proxy.
- Só documentar o incidente de 16/09 sem mudar o que o próximo publish exige.
- Reiniciar timers oneshot na mesma janela só por simetria com o inventário.
- Cronometrar varredura da Descoberta na janela do publish para o fecho.
- Desfazer o que já foi ao disco ou já reiniciou quando o fecho recusa.

## What Changes

- O inventário de produção no overlay passa a incluir o worker de varredura junto com os demais processos de longa duração (site, API, captação, worker de runtime).
- Na mesma janela do deploy de produção, o publish reinicia todos os de longa duração desse inventário — não de uma lista memorizada no chat. Jobs de uma execução (escrita de candles, scan de alerta Telegram) ficam fora da janela; a evidência do dia regista-os assim.
- O `release-guard post` recusa de forma visível se `services=` omitir um de longa duração da janela, ou se um de longa duração a correr ainda estiver no código velho; os cards não são dados como publicados. O que já foi ao disco e já reiniciou fica.
- Se um de longa duração não ficar a correr depois do restart, o fecho pode passar desde que o site e a API respondam (incidente à parte).
- A nota de release do dia lista os processos reiniciados a partir do inventário de produção.
- Sem **BREAKING** de produto. Sem ecrã. Sem caminho novo de restart fora do fecho. Sem mudar o restart de desenvolvimento.

## Capabilities

### New Capabilities

- (nenhuma) — overlay, `release-guard` e nota de release já existem.

### Modified Capabilities

- `oracle-environment-map`: inventário PROD do overlay inclui o worker de varredura; a janela do publish reinicia os de longa duração desse inventário e deixa os jobs oneshot de fora; a nota do dia deriva a lista do overlay, não do chat.
- `release-worktree-hygiene`: `post` recusa evidência incompleta dos de longa duração e recusa de longa duração a correr no código velho; processo parado após restart não bloqueia o fecho se site e API respondem; não desfaz disco.
- `prod-discovery-workers`: o unit de varredura de produção entra na lista de serviços do overlay para o fecho de release o reiniciar na mesma janela.

## Impact

- `.covenant-flow/overlay.yaml` (`environments.prod.services` + classificação oneshot da janela).
- `docs/crypto-overlay.md` (fecho PROD: restart a partir do inventário; oneshot fora da janela).
- `scripts/release-guard` (`post` / evidência `services=`).
- Nota `docs/release-<data>.md` do próximo publish (lista a partir do inventário).
- Testes/fixtures do guard proporcionais. Skill `covenant-flow-environments` só o recorte da janela PROD se o pin duplicar «affected services» sem classificar longa duração vs oneshot. `AGENTS.md` always-on MUST NOT crescer. `./restart` DEV intocado.
- MUST NOT: `backend/**` / `frontend/src/**`; HTML de protótipo; PostgreSQL/proxy; caminho novo de restart fora do fecho; cronometrar Descoberta; desfazer disco.
- `UI impact: none`. Prototype N/A.
- Origem: [#968](https://github.com/oalansilva/crypto/issues/968).
