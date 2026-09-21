## Context

Card **#995**, Status=Design. Incidente PROD 2026-09-19 ~22:08 BRT em `https://criptofarol.com.br/monitor`. Quadro «Não foi possível carregar as estratégias.» / «A lista de favoritos não chegou. Isto não significa que não há estratégias.» / «Tentar de novo», KPIs a 0, toast «Não foi possível carregar preferências do monitor.». Dois minutos depois, sem mudar nada, a mesma conta carregou o Monitor, abriu gráfico e enviou ordem.

Logs PROD (`criptofarol-prod-backend`, Caddy), SHA `563eccf4` (hotfix #983 já publicado): `GET /api/opportunities/?tier=1%2C2%2C3` **com** Authorization termina **200** no uvicorn; Caddy `aborting with incomplete response` / `connection reset by peer` (0,8–3,3 s) — o browser não recebe o JSON → `fetch` rejeita → o quadro pinta erro. Sem `GET /api/favorites/` nem eligibility a seguir. No mesmo segundo, clone **sem** Authorization e URL já descodificada → **401**. Par «200 autenticado + 401 sem auth + reset» em 7 dias: **25×**, só IP Zscaler. Só respostas grandes sofrem reset. `authFetch` só retenta `AbortError`; `TypeError: Failed to fetch` vai direto ao `catch`.

**Vivo hoje (pós-#970 / #975 / #983, desta branch):**
- `opportunitiesLoadError && length===0` → copy #975 + «Tentar de novo» com `{ refresh: true }` (recomputa).
- Enquanto `loading && length===0`, o quadro mostra «Carregando sinais...», mas os KPIs já pintam 0 (saem da lista vazia).
- `fetchMonitorContext` no primeiro `catch` de preferências dispara o toast «Não foi possível carregar preferências do monitor.» — mesmo se a lista acabar por passar.
- «Atualizar» e «Tentar de novo» mandam `refresh=true`. O subtítulo «Atualização contínua a cada 30s» é copy: a carga é abertura, filtro, Atualizar e Tentar de novo.
- #983 cobriu 401/abort na renovação; não cobre reset de rede nem o toast de preferências.

**Impeccable (Operate):** audience = operador em rede corporativa (Zscaler) que abre Monitor com sessão válida; outcome = ver sinais após corte transitório, ou #975 só se persistir, ou login se a sessão morreu; direction = clone `/monitor` + delta de estados, sem redesign; `DESIGN.md` permanece autoridade visual. Shape: Qs grelhadas todas A — não reentrevistar.

Briefing = issue grelhado #995 (Problema, História, Entra, Não entra). Q4=A: só Monitor.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. Irmãos de estado da mesma superfície: `carga.html` (espera), `erro.html` (falha persistente #975), `sessao.html` (login). Sem extra `/favorites` / `/home` / Carteira (Q4=A). `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Com sessão válida e favoritos crypto no servidor, um corte transitório na carga **não** pinta o #975 à primeira. O quadro espera dezenas de segundos.
- Enquanto espera: «Carregando sinais...»; KPIs **não** aparecem como 0 verdadeiro.
- Se a carga passa na mesma abertura: lista visível; ausente o quadro de erro; ausente o toast de preferências.
- Caso do incidente (11 estratégias, sessão válida): depois de abrir, o quadro lista os pares sem mudar de rede.
- «Tentar de novo» relê a lista já calculada (sem recomputar). «Atualizar» continua a recomputar.
- Sessão morta → login. Falha persistente → copy #975 + «Tentar de novo». Sem fingir catálogo vazio.

**Non-Goals:**

- Alterar Caddy, compressão, tamanho do payload ou backend (`/api/opportunities/` já 200).
- Configurar ou isentar Zscaler / proxy do cliente.
- Alongar a sessão / TTL do login.
- Redesign do quadro, KPIs, filtros ou copy dos estados (#970/#975).
- Telemetria de proxy corporativo.
- Favoritos, Início e Carteira (contrato #983).
- Ressuscitar `MonitorDashboardTab`.

## Decisions

1. **A primeira falha de rede autenticada não é a última palavra (Q=A).**
   O app reabsorve o corte transitório. Alternativa «isentar o Zscaler / túnel» rejeitada: Não entra. Alternativa «pintar #975 no primeiro `Failed to fetch`» rejeitada: é o incidente. Alternativa «mudar Caddy/gzip» rejeitada: o servidor já 200.

2. **Espera de dezenas de segundos em «Carregando sinais...» antes do #975.**
   O tempo cobre uma abertura presa no handshake do proxy. Se o proxy ficar minutos, o operador usa «Tentar de novo». Alternativa «spinner infinito» rejeitada: falha persistente precisa do #975. Alternativa «timeout de 8s do AbortError actual» rejeitada: o reset não é AbortError.

3. **KPIs durante a espera não pintam 0 como verdade.**
   Valores numéricos ficam pendentes (`—` no proto) até a lista chegar. Labels da faixa **não** mudam. Alternativa «esconder a faixa inteira» rejeitada: seria redesign. Alternativa «manter 0 da lista vazia» rejeitada: Entra.

4. **Toast de preferências não fica à mostra se a carga passa.**
   Na mesma abertura com sessão válida, o aviso «Não foi possível carregar preferências do monitor.» não permanece quando a lista chega. Alternativa «toast no primeiro 401 do clone sem Authorization» rejeitada: é o candidato do incidente.

5. **«Tentar de novo» relê; «Atualizar» recomputa.**
   Depois do erro, retry pede a lista já calculada (`refresh` ausente). Atualizar continua `refresh=true`. Alternativa «os dois recomputam» rejeitada: no incidente uma das 4 falhas foi a recomputação do retry.

6. **Sessão morta ≠ falha persistente.**
   Morta → login. Persistente → copy #975, sem catálogo vazio. Alternativa «ficar no #975 a fingir que a sessão vale» rejeitada: Entra.

7. **Vocabulário (nasce aqui, não no issue).**
   - **Falha transitória:** corte de rede (`TypeError: Failed to fetch` / reset) com sessão ainda válida e lista no servidor.
   - **Espera:** dezenas de segundos em «Carregando sinais...» antes de pintar #975.
   - **Relê:** novo pedido da lista já calculada, sem `refresh=true`.
   - **Recomputar:** `refresh=true` (botão Atualizar).
   - **Sessão morta:** refresh esgotado; o operador vai ao login.

## Risks / Trade-offs

- [Risco] Apply alonga TTL do login para «resolver» o reset → Mitigação: Non-Goal; o contrato é reabsorver o corte, não durar mais a sessão.
- [Risco] Apply muda Caddy/gzip/payload → Mitigação: Não entra; backend já 200.
- [Risco] «Tentar de novo» continua `refresh=true` e dispara outra recomputação no handshake → Mitigação: decisão 5; proto `data-load-mode="reread"`.
- [Risco] KPIs 0 durante «Carregando sinais...» continuam a mentir → Mitigação: decisão 3; proto `data-kpi-pending`.
- [Risco] Toast de preferências dispara no primeiro fail e fica visível depois do sucesso → Mitigação: decisão 4; proto sem o aviso no index/carga.
- [Risco] Extra Favoritos/Início/Carteira nasce por analogia com #983 → Mitigação: Q4=A; proibido.
- [Risco] Apply ressuscita `MonitorDashboardTab` → Mitigação: P3; o vivo é `MonitorStatusTab`.

## Migration Plan

Sem migração de schema e sem backfill. Rollback = reverter o tratamento de `Failed to fetch` / toast / KPIs pendentes / retry sem `refresh` no `MonitorStatusTab` e `authFetch`. Favoritos gravados não se apagam. TTL do login não muda. Caddy não muda.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-995-monitor-retry-rede/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/monitor` feliz (`index.html`): sessão válida; `table.signals` com SOL/USDT e ETH/USDT; landmarks Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia; KPIs com valores reais (não 0 de lista vazia); **ausente** «Não foi possível carregar as estratégias.»; **ausente** «Não foi possível carregar preferências do monitor.»; **ausente** «Nenhum ativo disponível no monitor». «Atualizar» presente com `data-load-mode="recompute"`.
- `/monitor` carga (`carga.html`): «Carregando sinais...»; KPIs **não** mostram `0` como contagem concluída; **ausente** o quadro #975; **ausente** o toast de preferências; **ausente** catálogo vazio.
- `/monitor` erro persistente (`erro.html`): «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + «Tentar de novo» (`data-load-mode="reread"`, aponta à lista); chrome Monitor; KPIs **não** mostram `0` como verdade; **ausente** catálogo vazio; URL continua no proto (não login).
- Sessão morta (`sessao.html`): login vivo («Bem-vindo de volta» + «Entrar»); **ausente** o quadro #975.
- Análise/gráfico continua a ter velas e trades (Apply, não o proto estático).
- `/favorites`, `/home`, Carteira: sem extra; contrato #983 intacto.

**Bug vivo (contrato no Design; correção no Apply, não neste filho):**

- `authFetch` só retenta `AbortError`; `TypeError: Failed to fetch` (reset) cai no `catch` e pinta #975 à primeira.
- `fetchOpportunities(..., { refresh: true })` no «Tentar de novo» recomputa.
- KPIs derivam da lista vazia e pintam 0 durante «Carregando sinais...».
- `fetchMonitorContext` toasta preferências no primeiro fail, mesmo se a carga passar.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Contagem exacta de retries / backoff / teto em ms (desde que a espera seja dezenas de segundos, não 8s).
- Retry em `authFetch` vs fila no `MonitorStatusTab`.
- Placeholder `-` / skeleton / `aria-busy` na faixa de KPIs — desde que 0 não pinte como verdade.
- Não disparar o toast vs disparar e retirar quando a carga passa.
- `MonitorDashboardTab` morto: não ressuscitar.
- Testids `monitor-retry` / `monitor-refresh` / `monitor-loading` / `data-kpi-pending`.
- Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone, não redesenhar.
- Alvos 44px no «Tentar de novo» (já no vivo).
- Thead vazio no `erro.html` (vivo é XOR erro/tabela) — incumbente #975.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/` → `frontend/public/prototypes/card-995-monitor-retry-rede/index.html`. Clone da página viva `/monitor` + delta da lista após reabsorção. Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. `COPIED:start`/`COPIED:end` no clone.
- Irmão carga: `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/carga.html`.
- Irmão erro: `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/erro.html`.
- Irmão sessão morta: `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/sessao.html` (clone `/login`).
- Sem extra `/favorites`. Sem painel ANTES/DEPOIS como URL canónica.
- `cp`/clone = copied; delta dos estados = generated.
- Digest, desktop/mobile e bytes copied vs generated: ver `## Prototype Validation`.

## Prototype Validation

- **Comando (autor, local):** Python HTTP sobre `frontend/public` + Playwright Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`), `colorScheme: dark`. Evidência: `.impeccable/critique/995-autor-gate.json`. Não `curl` contra DEV (worktree ≠ `environments.dev.source`).
- **URLs:** canónico `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/` (`index.html`); irmãos `…/carga.html`, `…/erro.html`, `…/sessao.html`. Sem extra `/favorites`.
- **Viewports:** desktop 1280×800 + mobile 390×844.
- **Ações / asserts (index):** `table.signals`; SOL/USDT e ETH/USDT; landmarks Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; ausente #975; ausente toast de preferências; ausente catálogo vazio.
- **Ações / asserts (carga):** «Carregando sinais...»; KPI `0` como verdade **ausente**; ausente #975; ausente toast.
- **Ações / asserts (erro):** copy #975 + «Tentar de novo»; ausente catálogo vazio; URL continua no proto.
- **Ações / asserts (sessao):** «Bem-vindo de volta» + «Entrar»; ausente quadro #975.
- **Console:** 0 pageerror / 0 console.error nos oito viewports.
- **Resultado do autor:** visual PASS · FAIL 0 de contrato visível. Detector CLI: `flat-type-hierarchy` no clone `/login` (P3 incumbente, não redesenhar). `em-dash-overuse` no rascunho de KPIs pendentes — polido para hífen incumbente `-`.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a` · 31568 B = 22008 copied + 9560 generated. Pares `COPIED:start`/`COPIED:end`: 7/7. T5 mede só este index.html.
  - `carga.html` `00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4` · 23657 B = 20719 copied + 2938 generated. Pares 4/4.
  - `erro.html` `86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223` · 24773 B = 21328 copied + 3445 generated. Pares 5/5.
  - `sessao.html` `7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584` · 4933 B = 4169 copied + 764 generated. Pares 3/3.

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #995 (Qs todas A; Q4=A só Monitor).

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Sem P0 novo de produto → sem segundo rework; P3 aceitos e Design submetido.

Relatórios: `.impeccable/critique/995-card-995-monitor-retry-rede.md` (autor); `.impeccable/critique/995-card-995-monitor-retry-rede-assessment-A.md`; `.impeccable/critique/995-card-995-monitor-retry-rede-assessment-B.md`.

**P0:** nenhum (autor, A, B)
**P1:** nenhum (autor, A, B)
**P2:** nenhum (A, B)
**P3 (aceitos → Apply):** clip Operar/Ver Trades; busca truncada a 390; thead vazio no `erro.html`; mobilebar «SOL/USDT 1d» em carga/erro; `flat-type-hierarchy` no clone `/login`; retries/backoff; `authFetch` vs fila; placeholder KPI `-`; toast não disparar vs retirar; `MonitorDashboardTab` morto; retry `<a href>` vs refetch; URL pública 404 até o servidor de protótipos ver o worktree (não é contrato de produto).

**Disposition:** P3 → Apply. Não reabrir Qs=A, copy #975, Caddy/Zscaler/TTL, nem extras Favoritos/Início/Carteira.

**Design Agent verdict:** PASS

- Autor: `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`. Browser gate 8/8.
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)` · PASS
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)` · PASS
