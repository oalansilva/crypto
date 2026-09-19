# Assessment A — card 983 · change card-983-carga-sessao-valida

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Crítico independente, onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `983-A-*` + `983-A-gate.py` / `983-A-gate.json`.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 983 — "PROD: Favoritos mostra erro de carga com sessão válida e catálogo intacto"
- change: `card-983-carga-sessao-valida`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-983-carga-sessao-valida`
- branch: `card-983-carga-sessao-valida`
- tuple: `bound_card=983` · `q_git=card-983-carga-sessao-valida` (resolver local; este filho não chama `process_event`)
- data (UTC): 2026-09-19T03:06Z
- Status observado: **Design** — GraphQL pontual `repository.issue(number:983).projectItems` → Project 1 / `oalansilva` / `fieldValueByName(Status)=Design`. GraphQL remaining=5000. MUST NOT `gh project item-list`. REST `gh api repos/oalansilva/crypto/issues/983` (não `gh issue view`): open, labels `bug` / `priority:P0` / `front:backtest` / `type:produto`.
- UI impact (rubrica D4): **affected** · `live_route: /favorites` · `surface: existing` — linhas próprias 16–18 de `design.md` (parseáveis)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium (`/usr/bin/chromium-browser`) via `xvfb-run`, HTTPS real, viewports 1280×800 e 390×844, `colorScheme: dark`. Gate `983-A-gate.json`: 195/195 PASS. 0 console error / 0 pageerror nos 6 HTML × 2 viewports.
- Q1=A, Q2=A gravadas no grill / `design.md`. **Não reabrir.** Não alongar sessão. Não desfazer #970.

## Limitação de sessão (obrigatória)

| URL pedida | HTTP | URL final (Playwright) | h1 | Landmarks |
|---|---|---|---|---|
| `https://dev.criptofarol.com.br/favorites` | 200 (SPA shell; urllib final continua `/favorites`) | `https://dev.criptofarol.com.br/login` | `Bem-vindo de volta` | `table.fav-strategies` = 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS. GET urllib no path `/favorites` devolve 200 sem 302 — HTTP 200 isolado **nunca** é PASS. Prova de sessão: Playwright client-nav → `/login`. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) fonte viva `FavoritesDashboard.tsx` / `HomePage.tsx` / `MonitorStatusTab.tsx` / `ExternalBalancesPage.tsx`, (3) catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens Binance **não** bastam.

PNG: `983-A-live-favorites.png`.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 16–18:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Regiões clonadas marcadas (linha 22): shell autenticado + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações») no **index.html**. Irmão `erro.html` — falha real #970. Extras com copy visível: `/monitor` em `monitor.html`; Início `/home` em `inicio.html`; Carteira `/external/balances` em `carteira.html` + `carteira-erro.html`. `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| ficheiro | sha256 | bytes | disco==HTTPS | COPIED pares | copied UTF-8 |
|---|---|---|---|---|---|
| `index.html` | `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145` | 43556 | IDENTICAL | 4/4 | 7781 |
| `erro.html` | `aff6abcdb57fd4267fd61945adb0d8a307e3b2c7ecdcc14a18d6c96a1fa51d19` | 33720 | IDENTICAL | 4/4 | 7729 |
| `monitor.html` | `51e5ee44f8833d254ef843bbf7893fc2657a36d7a12d476015adb0179856ee9e` | 31034 | IDENTICAL | 7/7 | 21504 |
| `inicio.html` | `48892e62a63666d741676e23e6d139fcdd89a9b3e579cc81cd773d6af0cf196a` | 14478 | IDENTICAL | 3/3 | 8806 |
| `carteira.html` | `6808e6cc9fde934f137d217b7c0fbc77b1efacadd56f8181d3c17686f6dcf6d4` | 16549 | IDENTICAL | 3/3 | 10819 |
| `carteira-erro.html` | `0b44d6a49bc09afc5250eb8de66741c4c3d28cab341391ac88a27dedf0b54f53` | 15197 | IDENTICAL | 3/3 | 10819 |

Canónico = index. copied > 0 em todos. Pasta HTML = `{index,erro,monitor,inicio,carteira,carteira-erro}` — extras são URLs próprias, **não** um painel no index. T5 mede só o index.

## Fidelidade (clone da página viva)

Catálogo `/favorites`: `selectors: ["table.fav-strategies"]` · texts `Estratégias favoritas`, `Symbol`, `Estratégia`, `Ações`.

Fonte viva `FavoritesDashboard.tsx`: h1 L1304 · `table.fav-strategies` L1513 · thead Symbol / Estratégia / Ações L1519–1534. Erro vivo L1233–1249: `role="alert"` + `data-testid=favorites-load-error` + «Não foi possível carregar as estratégias favoritas.» + «A sessão continua válida.» + `button.fav-retry`. Vazio de catálogo L1258–1259 / L1547. Bug vivo (contrato Apply, não o proto): `useQuery` L305–324 `authFetch` **sem** `signal`, `retry: false`; `isError` pinta o erro do #970 na janela de renovação.

| Landmark | Vivo | Proto + Playwright (1280 e 390) |
|---|---|---|
| `table.fav-strategies` | L1513 | count=1; desktop visível; mobile no DOM (`table-visible=false`), cards no lugar |
| `Estratégias favoritas` | h1 L1304 | h1 visível desktop e mobile |
| `Symbol` | th L1519 | thead DOM nos dois HTML; desktop visível (uppercase incumbente); mobile no card |
| `Estratégia` | th L1520 | thead DOM; nome da estratégia no card mobile |
| `Ações` | th L1534 | thead DOM; Analisar/Revalidar/Delete no card mobile |
| COPIED | — | index 4/4 · copied 7781 > 0 · erro 4/4 · 7729 > 0 |

Catálogo `/monitor` (só extra): `table.signals` · Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. Extra `monitor.html`: count=2 (secções hold + exit); 8/8 texts no thead DOM. Fonte viva `MonitorStatusTab.tsx` L1253–1264. `/home` e `/external/balances` **fora** do catálogo — clone da página viva, não emprestar landmarks de `/favorites`.

Anti-padrões P0:

- URL canónica `https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/` → index **é** a grade `/favorites` (shell 224px + workbench + `table.fav-strategies` + SOL/USDT e ETH/USDT). **Não** é painel ANTES/DEPOIS. Texto visível ANTES/DEPOIS = 0 nos 6 HTML × 2 viewports. **Não** é grelha de N estados.
- Chrome (sidebar 224px medida no desktop: 224×800, Inter/Binance, Favoritos activo, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks no proto, alinhados ao TSX.
- Extras são URLs próprias (`monitor.html`, `inicio.html`, `carteira.html`, `carteira-erro.html`). Index não as empilha.

PNGs: `983-A-desktop-1280x800-index.png` (grade + duas linhas); `983-A-mobile-390x844-index.png` (cards incumbentes).

## Produto (aceite visível — não reabrir Q1 / Q2)

Q1=A: Início e Monitor deixam de mostrar falha falsa da lista. Q2=A: Carteira mostra saldos; falha real continua «Erro ao carregar» / «Falha ao carregar saldos». Não alongar sessão. Não desfazer #970. Sessão morta → login.

| Aceite visível | Evidência (Playwright 1280×800 e 390×844) | Disposition |
|---|---|---|
| Feliz: SOL/USDT + ETH/USDT; footer «2 estratégias carregadas»; filtros Todos | index desktop = 2 `tbody tr`; mobile = 2 `.fav-mobile-card`. Ausente erro #970. Ausente «a sessão continua válida». | OK |
| Ausente catálogo vazio no feliz e no erro (cenário com favoritos) | «Nenhuma estratégia favorita encontrada» = 0 nos 2 HTML × 2 viewports | OK |
| Erro: copy #970 + «a sessão continua válida» + Tentar de novo; permanece Favoritos | erro.html: «Não foi possível carregar as estratégias favoritas.» + «A sessão continua válida.» + «Tentar de novo»; pill/footer «Carga falhou»; topbar Favoritos; URL continua no proto | OK |
| Erro: ausente login | «Bem-vindo de volta» = 0; URL ≠ `/login`. `role=alert` | OK |
| Retry aponta à lista | `.fav-retry` visível, focável, `href=index.html` (proto estático → index feliz) | OK |
| Q1=A Monitor: sinais, não falha falsa da lista | monitor.html: `table.signals` + SOL/ETH; **ausente** «Não foi possível carregar as estratégias.»; **ausente** «Nenhum ativo disponível no monitor» | OK |
| Q1=A Início: KPI com estratégia | inicio.html: «Melhor estratégia (7d)» + «Médias Móveis: Tendência Confirmada» / SOL/USDT; **ausente** «Não foi possível carregar `/api/favorites`.»; **ausente** «Nenhuma estratégia favoritada» | OK |
| Q2=A Carteira: saldos | carteira.html: BTC + ETH visíveis; **ausente** «Erro ao carregar» / «Falha ao carregar saldos» | OK |
| Q2=A Carteira falha real | carteira-erro.html: «Erro ao carregar» + «Falha ao carregar saldos» + «Tentar novamente»; URL continua no proto | OK |
| #970 não desfeito | irmão `erro.html` pina a copy do #970; sem voltar a fingir catálogo vazio | OK |
| Sem alongar sessão | sem UI de TTL / «ficar ligado»; Non-Goal intacto | OK |
| Sessão morta → login | não mockada no proto (já é o shell); live `/favorites` → `/login` observado e **descartado** como clone | OK |

Análise/gráfico com velas = Apply (não o proto estático). `MonitorDashboardTab` permanece morto. Clone Monitor = `MonitorStatusTab`.

## UX

Modo Impeccable: **Operate** / refinement. Job: abrir Favoritos (e, na mesma janela, Início / Monitor / Carteira) com sessão a renovar e ver a lista/saldos — não um erro falso, nem achar que o catálogo sumiu.

Hierarquia: AppNav → workbench Favoritos → h1 Estratégias favoritas → tiers → filtros Todos → `table.fav-strategies`. Delta óbvio sem redesign da grade: renovação com catálogo no servidor pinta as linhas; falha real continua o card #970.

Carga cognitiva: 2 pares no feliz = o contrato (incidente do administrador), não um wall. Erro nomeia a falha e oferece Tentar de novo no chrome Favoritos. Extras não competem no index.

Vale emocional do incidente (grade de erro com sessão válida e `GET /favorites/` 200) → pico (SOL/ETH na lista, ou erro #970 só quando a rede/corpo falhou de verdade) → fim (retry → lista; sessão morta já vai ao login).

## Acessibilidade

- `lang=pt-BR`; `:focus-visible` incumbente; `prefers-reduced-motion` no proto.
- Landmarks: `aside` de navegação + `h1` «Estratégias favoritas» + `table.fav-strategies`. Extra monitor: `h1` «Monitor de sinais» + `table.signals`. Extra início: `h1` «Seu snapshot diário de crypto». Extra carteira: `h1` «Carteira».
- Erro Favoritos: `role=alert` + `data-testid=favorites-load-error` (count=2 = bloco mobile + célula da tabela, como o vivo). Retry: `.fav-retry` focável (`activeElement`, **não** disabled), altura medida **44px** nos dois viewports, `tag=A` `href=index.html`.
- Carteira falha real: `role=alert` count=1; «Tentar novamente» focável (`tag=A`, não disabled). Vivo `ExternalBalancesPage` L438–445 **não** tem `role=alert` — proto anuncia; Apply pode alinhar.
- GO de estado não é só cor: texto «Não foi possível…» / «Carga falhou» / «Erro ao carregar» / pills Todas 2.
- Alvos 44px no retry Favoritos já no proto. Alvos de linha 28–32px = clone vivo / P3 já no `design.md`.

## Responsividade

- Desktop 1280×800: sidebar 224×800; `table.fav-strategies` visível; overflow-x documento = 0. Colunas densas da grade (Período/Stop/PF…) recortam à direita — incumbente, non-goal redesign. PNG `983-A-desktop-1280x800-{index,erro,monitor,inicio,carteira,carteira-erro}.png`.
- Mobile 390×844 Favoritos: sidebar 0; cards SOL/ETH no feliz; erro em card de estado + retry 44px. Overflow-x = 0. Tabela no DOM, `visible=false` como o vivo. PNG `983-A-mobile-390x844-{index,erro}.png`.
- Mobile Monitor extra: cards SOL/ETH; `table.signals` no DOM, `visible=false` como o vivo <740px. PNG `983-A-mobile-390x844-monitor.png`.
- Mobile Início / Carteira: KPI e saldos sem overflow-x. PNG `983-A-mobile-390x844-{inicio,carteira,carteira-erro}.png`.
- Busca do topbar Monitor clipa «Buscar par, est» a 390 — clone denso, P3. Acções da linha Monitor (Ver Trades / Operar) recortam a 1280 — incumbente da board, P3.

## Estados

Mock cobre: feliz Favoritos (index), falha real Favoritos (erro.html), feliz Monitor, feliz Início, feliz Carteira, falha real Carteira. Não mocka: loading, vazio real de catálogo, filtro sem resultado (já no #970), sessão morta→login (já é o shell). Cobertura de mock = P3. Vazio real reusa copy viva; mocká-lo como irmão confundiria com o incidente.

## Design specificity

A tela é Favoritos do Cripto Farol depois do incidente PROD 2026-09-18 ~22:55 BRT (carga falhou com sessão válida e catálogo intacto). Não iria a um SaaS genérico inalterado. Folha Binance; `DESIGN.md` não reescrito. Refinement, não redesign. Extras Q1/Q2 clonam Início (`/home`, chrome «Crypto»), Monitor e Carteira — não emprestam a grade de Favoritos.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Feliz lista pares; erro «Carga falhou» + copy #970; Carteira saldos ou «Erro ao carregar» |
| 2 | Match between system and real world | 4 | Copy de operador; Início deixa o path `/api/favorites` só no ramo de falha real (ausente no extra feliz) |
| 3 | User control and freedom | 4 | Tentar de novo permanece em Favoritos e aponta à lista; Carteira «Tentar novamente»; sessão morta já é login |
| 4 | Consistency and standards | 3 | Clone da grade; irmão erro mantém «Todas 2» / KPIs de sucesso na Carteira-erro (vivo XOR no ramo) |
| 5 | Error prevention | 4 | Renovação deixa de mentir erro #970; 200 que chegou ganha; #970 intacto para falha real |
| 6 | Recognition rather than recall | 4 | Estados nomeados na própria lista; operador não precisa lembrar o incidente |
| 7 | Flexibility and efficiency | 3 | Filtros do vivo no mock; retry é o acelerador; loading/vazio-real sem irmão |
| 8 | Aesthetic and minimalist design | 3 | Clone denso; clip de acções Monitor a 1280 e busca a 390 |
| 9 | Help users recognize/recover errors | 4 | Erro + retry; «isto não significa que o catálogo está vazio. A sessão continua válida.» |
| 10 | Help and documentation | 3 | Screen help incumbente; Ajuda no nav |
| **Total** | | **36/40** | **Good** |

## Cognitive load

Checklist: 1 workbench canónico; 1 lista; 2 pares no feliz. Erro não compete no index. Extras em URLs próprias. **Pass** (0 falhas). Decisão no glance ≤4 (abrir análise / retry / ir ao Monitor / ver saldos).

## Emotional journey

Vale (PROD: «Não foi possível carregar as estratégias favoritas.» / «a sessão continua válida» com catálogo 200 no backend) → pico (SOL/ETH na `table.fav-strategies`, KPI no Início, sinais no Monitor, BTC/ETH na Carteira) → fim (retry → lista; falha real continua #970; sessão morta → login). Reassegurança no irmão: o catálogo não foi apagado.

## Personas (só neste snapshot)

1. **Alex (operador diário):** abre `/favorites` na janela de renovação, vê SOL/ETH, não o erro do incidente. «Tentar de novo» com catálogo intacto cai na lista.
2. **Riley (stress do incidente):** erro #970 só para falha real; Início/Monitor/Carteira não mentem carga; #970 intacto; TTL não alonga.
3. **Sam / Casey (mobile 390):** cards repetem os pares; retry 44px visível no erro; Carteira mostra ETH/BTC ou o card de falha real.

## Strengths

- Clone estrutural de `/favorites`, não galeria ANTES/DEPOIS nem painel das N superfícies.
- Delta mínimo e óbvio: renovação = lista; falha real = copy #970 + retry.
- Q1=A e Q2=A visíveis em extras próprios. Não reabertos.
- Disco == HTTPS (index `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145`, 43556 B). copied > 0.
- `/login` descartado. Clone **não** alegado só por sidebar 224px: prova = landmarks proto × `FavoritesDashboard.tsx`. HTTP 200 isolado não foi PASS.

## Playwright (esta sessão)

- Desktop 1280×800 e mobile 390×844: aceite visível do contrato nas 6 URLs. 0 console / 0 pageerror. Overflow-x = 0.
- Live `/favorites` → Playwright `/login` (descartado). GET 200 no path não conta.
- PNGs: `983-A-desktop-1280x800-{index,erro,monitor,inicio,carteira,carteira-erro}.png`, `983-A-mobile-390x844-{index,erro,monitor,inicio,carteira,carteira-erro}.png`, `983-A-live-favorites.png`. Gate: `983-A-gate.json` (195/195).
- Landmarks `/favorites` no DOM (`th.textContent`) = Symbol / Estratégia / Ações. Uppercase visual do thead é CSS incumbente.

## Prototype Validation (rubrica)

`design.md` secção Prototype Validation presente: Playwright desktop+mobile, asserts do contrato. Esta sessão **reexecutou** o browser nas 6 URLs públicas HTTPS e confirma o aceite. Curl/GET 200 não substituiu o Playwright. Disco == HTTPS nos seis ficheiros.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível. Header «Todas 2» no irmão erro, KPIs de sucesso no `carteira-erro.html`, clip incumbente e retry estático são P3 (Apply / clone).

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** `erro.html` mantém chips «Todas 2 / Top picks 1 / Acompanhar 1» e o header de filtros durante a falha real. Vivo (`FavoritesDashboard` L1233–1545) pinta o erro **no lugar** das linhas; a contagem do header ainda mente no clone #970. Residual — não bloqueia Design. Já aceite naquele card.
- **P3-2** `carteira-erro.html` deixa KPIs de sucesso (`$1,677.60` / 2 ativos / +$86.21) acima do card «Erro ao carregar». Vivo deriva KPIs de `summary` sobre `balances`; primeira carga falhada seria 0/`—`. Apply: XOR — sem totais de sucesso se os saldos não chegaram. Contrato visível («Erro ao carregar» / «Falha ao carregar saldos») está presente.
- **P3-3** «Tentar de novo» no proto é `<a class="fav-retry" href="index.html">`; vivo = `<button>` + `refetch()`. Prova de Design = aponta à lista e é focável 44px. Apply: `refetch` / 200 em voo ganha do abort.
- **P3-4** Dois `role=alert` no `erro.html` (bloco mobile + célula da tabela), como o vivo. Apply pinta um ramo visível por viewport.
- **P3-5** Clip das acções da linha Monitor (Ver Trades / Operar) a 1280; busca do topbar clipa placeholder a 390. Incumbente da board; non-goal redesign.
- **P3-6** Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone #970, já no `design.md`. Não redesenhar.
- **P3-7** Unificar `authFetch` / axios / `HomePage.fetchJson`; `AbortSignal` no React Query; `fetchId` no `catch` da Carteira; debounce `minUsd` 320 ms. *Como* — aceite em `design.md`. Contrato visível = lista / saldos / KPI.
- **P3-8** `MonitorDashboardTab` morto: não ressuscitar. Testids `favorites-renewal-ok` / `wallet-renewal-ok` / `wallet-load-error` — Apply.
- **P3-9** Mock sem loading, sem vazio-real, sem filtro-vazio, sem sessão-morta. Sessão morta já é o shell `/login` (observado e descartado). Alvos 44px no retry Favoritos já no proto; Carteira «Tentar novamente» (copy viva, não «Tentar de novo»).
- **P3-10** Extra Início usa chrome «Crypto» (clone de `/home`), não o rótulo «Início». Não empresta `/favorites`. Não é P0 de fidelidade: o aceite Q1 é o KPI da estratégia.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1=A nem Q2=A. Não desfazer #970. Não alongar TTL. Não exigir galeria de N estados nem ANTES/DEPOIS no index. Não promover «Todas 2» no erro / KPIs no `carteira-erro` / clip 1280 / busca 390 / retry `<a>` a P0/P1. Não exigir segundo rework de Design.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks `/favorites` no index (`table.fav-strategies` + headers). Disco == HTTPS (index `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145`, 43556 B). Sem galeria/ANTES-DEPOIS como index. copied > 0. Delta = feliz da renovação com lista + `erro.html` com copy #970. Q1=A (Início KPI + Monitor `table.signals`) e Q2=A (Carteira saldos + `carteira-erro.html`) visíveis em extras. `/login` descartado. Clone **não** alegado só por sidebar 224px: prova = landmarks proto × `FavoritesDashboard.tsx`. HTTP 200 isolado não foi PASS.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 983
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P2: nenhum
P3: Todas 2 no erro.html; KPIs de sucesso no carteira-erro; retry <a href=index.html> vs refetch; alert ×2; clip Monitor 1280/busca 390; side-tab P3; authFetch/fetchId Apply; MonitorDashboardTab morto; mock sem loading/vazio-real; chrome Crypto no Início
verdict: PASS
```
