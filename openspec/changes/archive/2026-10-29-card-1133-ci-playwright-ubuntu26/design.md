## Context

Status: Design. Briefing copiado do issue #1133 (REST, 2026-10-22) em `proposal.md`. O issue deixou com o Design: a versão do Playwright, a versão fixa do sistema do CI e o jeito de refazer e aprovar as imagens de referência.

UI impact: none
live_route: N/A — card só de CI (runner, versão do Playwright, imagens de referência dos testes); nenhuma tela muda
surface: none

Sem superfície: o card mexe em `.github/workflows/`, em `frontend/package*.json`, nas imagens de referência dos testes e num teste de contrato. Nenhuma tela, componente ou texto de produto muda, e o issue proíbe mudar telas para as imagens baterem. Prototype: N/A. Impeccable: N/A (CI sem tela; as imagens de referência são fixtures de teste, não design de produto).

Estado verificado em 2026-10-22:

- `.github/workflows/ci.yml` é o único workflow e tem 15 jobs, todos com `runs-on: ubuntu-latest`: `changes`, `openspec-validate`, `qa-policy`, `new-route-playwright-coverage`, `backend-format`, `frontend-lint`, `frontend-tests`, `frontend-build`, `process-fsm`, `backend-unit-tests`, `backend-tests`, `backend-coverage-gate`, `e2e-playwright`, `qa-gate`, `deploy-staging`.
- GitHub (changelog de 2026-09-17): `ubuntu-26.04` saiu do preview em 17/09; o `ubuntu-latest` migra de 24.04 para 26.04 aos poucos entre 19/10 e 19/11/2026; quem não está pronto deve fixar `ubuntu-24.04`. A política do `actions/runner-images` mantém as 2 últimas versões GA de cada sistema; a descontinuação da mais velha começa quando a próxima vira GA. Com 26.04 GA, 24.04 é uma das duas suportadas e só entra em descontinuação quando sair a 28.04. A imagem 24.04 do GitHub está em 24.04.5.
- `frontend/package.json` declara `@playwright/test: ^1.58.2`; o lockfile resolve 1.58.2 (Chromium 145). npm em 2026-10-22: `latest` = 1.64.1 (publicada 14/10; 1.64.0 em 07/10). `engines.node`: 1.58.2 a 1.61.x pedem `>=18`; 1.64.1 pede `>=20`. O job usa Node 20; o DEV tem Node 22.22.2.
- Tabelas de dependências do `playwright-core` (pacotes do npm): 1.61.1 e 1.64.1 trazem `ubuntu24.04-x64`, `ubuntu24.04-arm64`, `ubuntu26.04-x64` e `ubuntu26.04-arm64`. Chromium: 1.61.1 = 149.0.7827.55 (revisão 1228); 1.64.1 = 156.0.8078.4 (revisão 1248).
- 28 imagens de referência em 5 pastas `frontend/tests/e2e/*-visual-critical.spec.ts-snapshots/` (18 + 4 + 2 + 2 + 2), sufixo `-linux.png`, projetos `visual-desktop` e `visual-mobile`, `maxDiffPixelRatio: 0.001`. `monitor-spot-market-orders-visual-critical.spec.ts` tira 2 capturas em sequência no mesmo teste: se a primeira falha, a segunda não é avaliada.
- Servidor DEV: Ubuntu 24.04.4 LTS, **aarch64**. O CI roda em x64. A imagem Docker do frontend (`frontend/Dockerfile`, `node:20-alpine`) só faz `npm ci` e build; não instala navegador.
- Os workflows já têm teste de contrato em `backend/tests/contract/test_backend_unit_harness.py`, rodado em todo PR e push pelo passo "Run backend unit-test harness contracts" do job `backend-unit-tests` (job sem `if`, dependência do `qa-gate`).
- Ensaio local em cópia descartável do `frontend/` (fora do git, no DEV aarch64) com `@playwright/test@1.64.1`: ver D1 "Ensaio no DEV".

## Goals / Non-Goals

**Goals:**

- `e2e-playwright` volta a instalar o Chromium e roda as suítes funcional e visual até o fim em todo PR.
- Os 15 jobs rodam num sistema fixo que não muda quando o GitHub troca o `ubuntu-latest`, com um teste que impede a volta do `ubuntu-latest`.
- As 28 imagens de referência são refeitas no mesmo ambiente do CI, com par antes/depois de cada uma e aprovação registrada de Alan antes do merge.
- `qa-gate` verde num PR deste card e no PR #1132 depois do rebase.

**Non-Goals:**

- Mudar suítes e2e, critérios do `qa-gate`, `maxDiffPixelRatio`, `retries` ou telas.
- Desligar `e2e-playwright` ou `qa-gate`, ou usar `qa-visual-skip`.
- Trocar depois a versão fixa do sistema (card próprio de Alan).
- Subir a versão do Node do CI (continua 20).

## Decisions

### D1. Playwright 1.64.1 exato

`@playwright/test` vai para `1.64.1`, sem `^`. O lockfile é regenerado com `npm install -D -E @playwright/test@1.64.1` em `frontend/`: mudam só `@playwright/test`, `playwright` e `playwright-core` (1.58.2 → 1.64.1), o `engines.node` deles (`>=20`) e sai o `fsevents` opcional do `playwright` (só macOS).

Por que 1.64.1 e não 1.61.x (a primeira com `ubuntu26.04`):

- O custo do card não diminui com a mínima: de 1.58.2 para 1.61.1 o Chromium já salta 4 versões maiores (145 → 149), então as 28 imagens precisam ser refeitas e aprovadas de qualquer jeito.
- 1.64.1 é a estável mais recente: mais tempo até a próxima subida obrigatória e suporte a 24.04 e 26.04 (x64 e arm64). Quando Alan abrir o card de troca do sistema, o Playwright já roda nos dois.
- O único requisito novo é Node ≥ 20, que o CI (Node 20), o DEV (Node 22) e a imagem `node:20-alpine` já cumprem.
- Versão exata porque a versão do Playwright fixa o Chromium, e o Chromium fixa os pixels das imagens. Um `^` deixaria um `npm install` futuro trocar o navegador sem refazer as imagens. O `npm ci` do CI já respeita o lockfile; o pin exato vale para quem roda `npm install`.

Alternativas: 1.61.1 (descartada: mesmo custo de imagens, menos fôlego); 1.62.x/1.63.x (sem vantagem sobre a última estável); ficar em 1.58.2 só fixando 24.04 (descartada: o item 2 do Entra pede versão que funcione no sistema novo).

Ensaio no DEV (2026-10-22, aarch64, Node 22, cópia do `frontend/` fora do git, `CI=1`):

- `npm ci` + `npm install -D -E @playwright/test@1.64.1` ok; `npx playwright install chromium` baixou o Chromium 156 (revisão 1248).
- Funcional com 1.64.1: 263 passed (6,9 min), nenhum skip.
- Visual com 1.64.1 contra as 28 imagens atuais: 33 passed + 1 flaky (`discovery-visual-critical.spec.ts:478`, `toBeFocused()` falhou na primeira tentativa e passou no retry; não é captura de tela). Nenhuma das 28 capturas passou de 0,001.
- Controle visual com 1.58.2 (Chromium 145) no mesmo DEV: 34 passed.

O ensaio indica que o Chromium novo muda pouco os pixels, mas não substitui o CI: o DEV é arm64 e não tem as fontes da imagem do GitHub (ver D3).

### D2. Runner fixo `ubuntu-24.04` nos 15 jobs

Os 15 `runs-on: ubuntu-latest` viram `runs-on: ubuntu-24.04`. O novo `playwright-baselines.yml` (D3) nasce com o mesmo rótulo.

Por que 24.04 e não 26.04:

- É o sistema em que o CI ficou verde até 18/10: as 28 imagens atuais batem no runner 24.04 x64 dentro de 0,001. Mas elas não foram feitas lá. Pelo fluxo vigente (`docs/crypto-overlay.md:392-398`), cada card de tela as atualiza no DEV aarch64 e as commita junto com a tela (git log das PNG: a última troca é `d4abc413`, 2026-10-02, #1075). Por isso o antes/depois que Alan vai ver mistura três efeitos: Chromium 145 → 156, aarch64 → x64 e fontes do DEV → fontes da imagem do GitHub. Fixar 24.04 tira o quarto efeito possível, a troca de sistema. A decisão de gerar no runner (D3) continua valendo: depois deste card, a referência e o gate saem do mesmo ambiente.
- É a mesma versão do DEV (24.04.4), onde os testes locais rodam.
- Suporte: com 26.04 GA, o GitHub mantém 24.04 e 26.04. A 24.04 só entra em descontinuação quando sair a 28.04, com anúncio e brownouts antes.
- 26.04 é imagem nova, com ferramentas atualizadas ou removidas (changelog do GitHub). Fixá-la juntaria duas trocas num card de desbloqueio.

Alternativa: `ubuntu-26.04` (descartada: diverge do DEV e mistura sistema novo com Chromium novo nas imagens). A troca futura para 26.04 fica para card próprio de Alan; com 1.64.1 o Playwright já roda lá.

### D3. Imagens refeitas no runner do CI por um workflow próprio

Neste card as imagens não são refeitas no DEV: o DEV é aarch64, o CI é x64, e a imagem do GitHub tem fontes que o DEV não tem. Hoje as 28 ainda cabem em 0,001 no DEV (D1), mas isso é coincidência de tela, não garantia: anti-aliasing e fonte de fallback mudam entre arquiteturas e imagens. A referência que o gate compara tem de sair do mesmo ambiente do gate, que é o runner fixado.

Alcance: a regra "gerar no runner" vale para este card e para qualquer troca futura da versão fixa do Playwright ou do runner. Os cards de tela continuam no fluxo vigente (atualizar no DEV com `--update-snapshots`, revisar o diff, commitar com a tela; `docs/crypto-overlay.md:392-398`, `docs/backlog-operating-model.md:102`). Este card não muda esses docs. Se a regra vira geral, é decisão de Alan (Open Questions).

Novo workflow `.github/workflows/playwright-baselines.yml`:

- Disparo: `pull_request` com `types: [labeled]` e `if: github.event.label.name == 'regerar-baselines'`, mais `workflow_dispatch`. O `workflow_dispatch` só aparece depois que o arquivo chega à branch padrão; neste card o disparo é o rótulo, que usa o arquivo do próprio PR.
- `runs-on: ubuntu-24.04`, `permissions: contents: read`, timeout 30 min. Não grava no repositório. Não é dependência do `qa-gate` e não muda o `ci.yml`.
- Passos: os mesmos do `e2e-playwright` até instalar o Chromium (checkout, Node 20, `npm --prefix frontend ci`, `playwright install --with-deps chromium`); guarda as 28 imagens atuais como "antes"; roda `npx playwright test --project=visual-desktop --project=visual-mobile --update-snapshots=all` com `CI=true`; compara cada par.
- `--update-snapshots=all` refaz as 28, inclusive as que ainda passariam. As 28 passam a vir do mesmo Chromium e do mesmo runner, e a sequência de 2 capturas do `monitor-spot-market-orders` não para na primeira.
- Artefato `playwright-baselines-<run_id>`: `snapshots/` com as 28 PNG novas no mesmo caminho do repositório; `comparacao/index.html`, uma página estática com um bloco por imagem (antes, depois, máscara de pixels diferentes, fração de pixels diferentes, dimensões, SHA-256 antes e depois), ordenada da maior diferença para a menor, com as idênticas marcadas; `comparacao/manifest.json` com os mesmos campos.

Alternativas descartadas:

- Refazer no DEV, ou em contêiner x64 emulado no DEV: arquitetura e fontes diferentes do runner.
- Usar o `-actual.png` do artefato de falha do `e2e-playwright`: só sai para as imagens que falham, a segunda captura do `monitor-spot-market-orders` não sai enquanto a primeira falha (mais de uma rodada), e as que passam ficam com o Chromium velho.
- Passo de atualização dentro do `e2e-playwright`: mistura gerar referência com o gate que a confere.
- Workflow temporário numa branch descartável: não passa por review e não fica no repositório para a próxima troca de Playwright ou de runner. Se o `playwright-baselines.yml` fica depois do T14 é decisão de Alan (Open Questions).

### D4. Antes/depois para Alan e aprovação registrada

1. O Apply baixa o artefato (`gh run download`), confere o SHA-256 de cada PNG com o `manifest.json` e faz um commit só com as PNG em `frontend/tests/e2e/*-snapshots/`. Esse é o "commit das imagens".
2. O `e2e-playwright` do PR tem de passar contra as imagens novas. Isso prova que a geração e o gate produzem o mesmo resultado.
3. Comparação para Alan, em dois lugares:
   - **PR, aba Files changed**: o GitHub mostra cada PNG alterada com antes e depois lado a lado (modos 2-up, Swipe e Onion skin), no navegador e presa ao commit. É a visão principal, uma imagem por vez.
   - **Comentário no card #1133**, feito pelo pai: tabela com as 28 imagens (arquivo, fração de pixels diferentes, SHA-256 novo), o **conjunto** (abaixo), link do commit das imagens no PR, link do run e nome do artefato com `comparacao/index.html` (máscara de diferença e números).
4. Âncora da aprovação: o **conjunto** é o SHA-256 da lista ordenada "SHA-256 + caminho" de todas as PNG em `frontend/tests/e2e/*-snapshots/` no topo do PR (`git ls-files -z 'frontend/tests/e2e/*-snapshots/*.png' | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum`). Ele depende só do conteúdo e do caminho de cada PNG, não do SHA de commit: um rebase que não mexe nas PNG mantém o conjunto e a aprovação; qualquer PNG diferente, nova ou removida muda o conjunto e anula a aprovação.
5. Aprovação registrada: comentário de `oalansilva` no issue #1133, digitado pelo próprio Alan, no mesmo formato de frase fixa do `qa-visual-skip`:

   ```
   Baselines aprovadas por Alan.
   Conjunto: <sha-256 do conjunto>
   ```

   Vale para todas as PNG daquele conjunto. Para recusar:

   ```
   Baselines rejeitadas por Alan.
   Conjunto: <sha-256 do conjunto>
   Rejeitadas: <arquivo>.png, ...
   Motivo: ...
   ```

6. Quem escreve: o agente (pai, Apply, QA ou qualquer filho) MUST NOT escrever `Baselines aprovadas por Alan.` nem `Baselines rejeitadas por Alan.`, nem transformar em comentário um "ok", "aprovado" ou "pode seguir" dado no chat. Só o Alan digita a frase no issue. Se ele aprovar pelo chat, o pai responde pedindo que ele cole a frase no #1133 e espera.
7. Natureza do gate: é cooperativo, como o `qa-visual-skip` e as transições T15/T18. O agente publica com o token do Alan, então o GitHub não distingue quem digitou; a garantia é a regra do item 6, não uma checagem de máquina. O gate fica fora do `qa-gate` de propósito: o Não entra proíbe mudar os critérios do `qa-gate`.
8. Regras de checagem (pai, antes do T14): recalcular o conjunto no topo do PR; exige-se um comentário de aprovação com esse conjunto e nenhum de recusa com o mesmo conjunto. Sem isso, o pai não chama `integrar_develop` (T14). Aprovação de PR no GitHub não serve: o PR é aberto pela conta do Alan, e o GitHub não deixa o autor aprovar o próprio PR.

### D5. Teste contra `ubuntu-latest` e contra versão solta

Novo `backend/tests/contract/test_ci_runner_pinned.py`, rodado pelo passo já existente de contratos do `backend-unit-tests` (sem mudar o `ci.yml` além dos `runs-on`):

- Para cada `.github/workflows/*.yml|*.yaml`: todo valor de `runs-on:` é literalmente `ubuntu-24.04`. Falha com arquivo, job e valor encontrado. Leitura por texto, sem PyYAML (que não está em `backend/requirements.txt`).
- Nenhuma ocorrência de `ubuntu-latest` em `.github/`.
- Cada job de `ci.yml` tem um `runs-on` (um job sem `runs-on` também falha).
- `@playwright/test` em `frontend/package.json` é versão exata (`^\d+\.\d+\.\d+$`) e igual a `packages["node_modules/@playwright/test"].version` do lockfile.
- O rótulo permitido (`ubuntu-24.04`) é uma constante do teste. Trocar o sistema exige mudar a constante, num diff visível de card próprio de Alan.

Efeito no `qa-gate`: o teste é a guarda do item 4 do Entra. Ele entra numa suíte que já é dependência do `qa-gate` (`backend-unit-tests`), então uma divergência de runner ou de versão deixa o `qa-gate` vermelho sem mudar a lista de `needs` nem a lógica do `qa-gate` (`ci.yml:518-557`). Os critérios do `qa-gate` não mudam. O `playwright-baselines.yml` não é `needs` do `qa-gate` nem de nenhum job do `ci.yml`.

Alternativas: `actionlint` com regra própria (dependência nova); passo novo num job do `ci.yml` (muda o workflow além do pedido); checar só o `ci.yml` (deixaria o workflow novo e os próximos sem guarda).

### D6. Ordem do Apply

1. Fixar `ubuntu-24.04` nos 15 jobs + teste D5 (versão do Playwright ainda 1.58.2, só a parte de runner). Push e PR para `develop`. O CI deve voltar ao verde de 18/10: mesmo sistema, Chromium e imagens.
2. Playwright 1.64.1 + lockfile + parte de versão do teste D5 + `playwright-baselines.yml`. Criar o rótulo `regerar-baselines` (`gh label create`) e aplicar no PR.
3. Baixar o artefato, conferir os SHA-256, commit das imagens, CI verde.
4. Comentário de comparação no card com o conjunto; esperar Alan digitar a aprovação (D4).

Em qualquer passo, se uma falha só se resolve mexendo em `frontend/tests/e2e/**` (spec, fixture, seletor), o Apply para e devolve ao pai como P0; a decisão volta para Alan (1.61.1 ou card próprio).

O passo 1 isola o efeito do runner fixo, e o passo 3 isola o efeito do Chromium.

### D7. Verificação

- `qa-gate` verde no topo do PR deste card, com o conjunto de PNG aprovado, com `e2e-playwright` instalando o Chromium 156 e rodando funcional e visual até o fim (log mostra 263 testes funcionais e 34 visuais com as 28 capturas, nenhum `skipped` novo).
- `pytest backend/tests/contract` verde no repositório; casos sintéticos no próprio teste provam a falha para `ubuntu-latest`, `ubuntu-26.04`, expressão, job sem `runs-on` e versão solta do Playwright.
- Depois do T14: o PR #1132 (#1117) é rebaseado em `develop` e o `qa-gate` dele fica verde. O link do run vai como comentário no #1133 antes da homologação.

## Risks / Trade-offs

- [Foco instável no Chromium 156] → No ensaio, `discovery-visual-critical.spec.ts:478` (`toBeFocused()`) falhou uma vez e passou no retry; com 1.58.2 não falhou. O Apply registra se repetir no CI. O retry existente (`retries: 1` em CI) não muda. O Apply não edita o teste nem o pula: se a falha passar do retry e bloquear o `e2e-playwright`, para e volta ao Alan como P0.
- [Chromium 156 quebra testes funcionais] → No ensaio no DEV, os 263 passaram. No CI, o Apply não edita nada em `frontend/tests/e2e/**` (o Não entra proíbe mudar as suítes) e não pula teste: qualquer falha que exija mexer em spec, fixture ou seletor para o Apply e volta ao Alan como P0, com a opção 1.61.1 ou card próprio. A task 4.4 confere que o PR não toca `frontend/tests/e2e/**/*.ts`.
- [Tela instável gera imagem diferente entre a geração e o gate] → O passo 2 do D4 prova a igualdade. Se uma imagem oscila, o Apply registra qual é; não mexe na tela nem no limite.
- [Alan recusa uma imagem] → Não há T14. Mudar a tela ou o teste está fora do escopo. O caminho seguinte é decisão de Alan (Open Questions).
- [Workflow novo dispara por engano] → Só com o rótulo exato, sem escrita no repositório, fora do `qa-gate`.
- [24.04 descontinuada no futuro] → Só depois da 28.04 GA, com anúncio e brownouts. O teste D5 impede troca silenciosa; a troca é card de Alan.
- [Cache de navegador no DEV] → O Chromium 1248 (com o headless shell) soma cerca de 680 MB em `~/.cache/ms-playwright`; as revisões velhas continuam lá até limpeza manual.
- P3 aceitos para o Apply: nome do script de comparação e a biblioteca de diff de pixels; layout exato da `comparacao/index.html`; texto da mensagem de falha do teste D5; uso de `--output` separado no workflow de imagens.

## Migration Plan

Sem migração de banco nem de serviço. Entra em `develop` pelo T14 do PR deste card, depois da aprovação das imagens. Os outros PRs abertos precisam de rebase em `develop` para pegar o runner fixo, o Playwright novo e as imagens novas.

Rollback: reverter o commit das imagens e o do Playwright volta para 1.58.2 com as imagens antigas, mantendo o runner fixo em 24.04. Esse é o estado verde de 18/10 e destrava o `qa-gate` sem o item 2 do Entra. Reverter também o commit do runner devolve o CI ao `ubuntu-latest` (26.04), que está quebrado; não é rollback útil.

## Open Questions

Decisões de Alan na Aprovação de Design. Nenhuma delas gera task de docs neste card.

1. **`playwright-baselines.yml` fica depois do T14?** Proposta do design: fica, para a próxima troca de Playwright ou de runner. Se Alan disser não, o Apply remove o arquivo num commit depois do commit das imagens; as PNG não mudam, então o conjunto e a aprovação continuam valendo.
2. **"Baseline só no runner + aprovação por comentário" vira regra geral?** Neste card a regra vale só para a troca de Playwright ou de runner; cards de tela seguem atualizando no DEV (`docs/crypto-overlay.md:392-398`, `docs/backlog-operating-model.md:102`). Torná-la geral, com mudança desses docs, seria card futuro de Alan.
3. **Quem faz o rebase do PR #1132 (#1117) depois do T14 deste card?** Pode ser o pai deste card, a sessão do #1117 ou o próprio Alan. A task 5.4 só registra o run do `qa-gate` do #1132; quem faz o rebase não está definido.
4. **E se Alan recusar uma imagem?** Sem T14 enquanto houver recusa para o conjunto atual. Caminhos possíveis, a escolher por Alan: (a) tentar 1.61.1 (Chromium 149), com nova geração e nova aprovação; (b) entrar só com o runner fixo (passo 1 do D6) e Playwright 1.58.2, o que destrava o `qa-gate` sem o item 2 do Entra, e a subida vai para card próprio; (c) abrir card de tela para a tela da imagem recusada e deixar este card esperando.

## Design Critique

- P1-1 (escopo) design.md permitia consertar testes e2e neste card, contra o Não entra. Resolvido no rework r1: Risks e D6 mandam parar e voltar ao Alan como P0 quando uma falha exige mexer em `frontend/tests/e2e/**`; a task 4.4 confere que o PR não toca `frontend/tests/e2e/**/*.ts`.
- P1-2 (escopo) spec virava regra permanente para todo card de tela e contradizia `docs/crypto-overlay.md:392-398` e `docs/backlog-operating-model.md:102`. Resolvido no rework r1: os requisitos 3 e 4 da spec e o alcance do D3 valem só para troca de Playwright ou de runner; permanência do workflow e regra geral viraram Open Questions 1 e 2.
- P1-3 (contrato) a aprovação por comentário de `oalansilva` podia ser escrita pelo agente com o token do Alan. Resolvido no rework r1: D4 itens 6-7, spec req 4 e task 5.2 proíbem o agente de escrever a frase ou converter um "ok" do chat; gate declarado cooperativo e fora do `qa-gate`.
- P2-1 (contrato) aprovação presa ao SHA do commit caía com rebase. Resolvido no rework r1: âncora no conjunto (SHA-256 da lista SHA-256 + caminho de cada PNG), D4 item 4 e spec req 4.
- P2-2 (contrato) efeito do D5 no `qa-gate` não estava dito. Resolvido no rework r1: parágrafo "Efeito no `qa-gate`" no D5 (vermelho via `backend-unit-tests`, sem mudar `needs` nem lógica; `playwright-baselines.yml` não é `needs`).
- P2-3 (fato) premissa de que as imagens atuais vieram do CI 24.04. Resolvido no rework r1: D2 diz que vieram do DEV aarch64 (git log, `d4abc413`) e que o antes/depois mistura Chromium, arquitetura e fontes.
- P3-1 (implementação) `ci.yml:328` tem `github-actions/ubuntu-latest` fora de `runs-on`, o que faz o D5 falhar com a task 1.1 como está. Disposition: aceito como detalhe de Apply (trocar para `ubuntu-24.04` ou restringir a checagem a `runs-on`).
- P3-2 (implementação) as tabelas 24.04/26.04 do requisito 2 não são checadas por teste. Disposition: aceito como detalhe de Apply (evidência `npm pack` + grep na task 2.1).
- P3-3 (implementação) o disparo `labeled` só se repete tirando e repondo o rótulo. Disposition: aceito como detalhe de Apply (documentar no cabeçalho do workflow).
- P3 do autor (nome do script de comparação e biblioteca de diff, layout da `comparacao/index.html`, texto da falha do teste D5, `--output` separado no workflow) mantidos. Disposition: aceito como detalhe de Apply.

Verdict: pass (após rework r1)
