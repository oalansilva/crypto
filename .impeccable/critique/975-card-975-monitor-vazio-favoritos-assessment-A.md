# Assessment A — card 975 · change card-975-monitor-vazio-favoritos

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Crítico independente, onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `975-A-*` + `975-A-gate.py` / `975-A-gate.json`.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 975 — "DEV: Monitor fica vazio com Favoritos carregados"
- change: `card-975-monitor-vazio-favoritos`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-975-monitor-vazio-favoritos`
- branch: `card-975-monitor-vazio-favoritos`
- tuple: `bound_card=975` · `q_git=card-975-monitor-vazio-favoritos` (resolver local; este filho não chama `process_event`)
- data (UTC): 2026-09-18T23:30Z
- Status observado: **Design** — GraphQL pontual `repository.issue(number:975).projectItems` → Project 1 / `oalansilva` / `fieldValueByName(Status)=Design`. GraphQL remaining=4979. MUST NOT `gh project item-list`. REST `gh api repos/oalansilva/crypto/issues/975` (não `gh issue view`).
- UI impact (rubrica D4): **affected** · `live_route: /monitor` · `surface: existing` — linhas próprias 20–22 de `design.md` (parseáveis)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium (`/usr/bin/chromium-browser`) via `xvfb-run`, HTTPS real, viewports 1280×800 e 390×844, `colorScheme: dark`. Gate `975-A-gate.json`: 92/92 PASS. 0 console error / 0 pageerror nos 2 HTML × 2 viewports.
- Q2=A gravada no grill / `design.md`. Cobertura 11/18 é *como*. Copy de erro não muda. **Não reabrir.**

## Limitação de sessão (obrigatória)

| URL pedida | HTTP | URL final (Playwright) | h1 | Landmarks |
|---|---|---|---|---|
| `https://dev.criptofarol.com.br/monitor` | 200 (SPA shell) | `https://dev.criptofarol.com.br/login` | `Bem-vindo de volta` | `table.signals` = 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS. GET urllib no path `/monitor` devolve 200 sem 302 — HTTP 200 isolado **nunca** é PASS. Prova de sessão: Playwright client-nav → `/login`. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) fonte viva `MonitorStatusTab.tsx`, (3) catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens Binance **não** bastam.

PNG: `975-A-live-monitor.png`.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 20–22:

```
UI impact: affected
live_route: /monitor
surface: existing
```

Regiões clonadas marcadas (linha 26): shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. Irmão `erro.html` — mesmo clone + delta do erro de carga (copy actual). Sem extra `/favorites`. Sem `live_route` emprestada. `COPIED:start`/`COPIED:end` nas regiões clonadas. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| ficheiro | sha256 | bytes | disco==HTTPS | COPIED pares | copied UTF-8 |
|---|---|---|---|---|---|
| `index.html` | `542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116` | 31012 | IDENTICAL | 7/7 | 21481 |
| `erro.html` | `fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34` | 24112 | IDENTICAL | 5/5 | 20678 |

Canónico = index. copied > 0 em ambos. Pasta HTML = `{index,erro}` — **ausente** `favorites.html`. T5 mede só o index.

## Fidelidade (clone da página viva)

Catálogo `/monitor`: `selectors: ["table.signals"]` · texts `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`, `Operar`, `Par / Estratégia`.

Fonte viva `MonitorStatusTab.tsx`: `table.signals` L1203 · thead Par / Estratégia, Status, Preço, Distância, 7d, Risco até stop, Tags L1207–1214 · acções na linha (Operar) L1363–1388. Erro vivo L1113–1126: `role="alert"` + `data-testid=monitor-load-error` + copy actual + Tentar de novo. Vazio de catálogo L1128–1134: «Nenhum ativo disponível no monitor.» Bug vivo (contrato Apply, não o proto): 200 `[]` cai no ramo `length===0 && !loading` mesmo com favoritos.

Landmarks medidos no **DOM** (`th.textContent`), não em `innerText` (CSS `text-transform:uppercase` no thead — o gate do autor marcou `landmarks_missing` por esse falso negativo; A confirma os 8 texts no thead).

| Landmark | Vivo | Proto + Playwright (1280 e 390) |
|---|---|---|
| `table.signals` | L1203 | index count=2 (secções hold + exit); erro count=1. Desktop visível no index. Mobile index: DOM presente, `table-wrap { display:none }` como o vivo; cards no lugar |
| `Par / Estratégia` | th L1207 | thead DOM nos dois HTML; desktop visível (uppercase incumbente) |
| `Status` | th L1208 | thead DOM |
| `Preço` | th L1209 | thead DOM |
| `Distância` | th L1210 | thead DOM (admin / clone técnico) |
| `7d` | th L1211 | thead DOM |
| `Risco até stop` | th L1212 | thead DOM |
| `Tags` | th L1213 | thead DOM |
| `Operar` | botão L1368 / proto th | thead proto + botão na linha. Vivo: th de acções vazio (`actions-cell`) — P3 |
| COPIED | — | index 7/7 · copied 21481 > 0 · erro 5/5 · 20678 > 0 |

Anti-padrões P0:

- URL canónica `…/prototypes/card-975-monitor-vazio-favoritos/` → index **é** a board `/monitor` (shell 224px + KPIs + filterbar + `table.signals` + SOL/USDT e ETH/USDT). **Não** é painel ANTES/DEPOIS. Texto visível ANTES/DEPOIS = 0 nos 2 HTML × 2 viewports.
- Não é grelha de N estados no lugar da listagem. Index = caminho feliz (subset analisável). Erro é irmão. Nunca um painel das N como URL canónica.
- Sem extra `/favorites`. Copy de Favoritos / #970 **não reabre**.
- `MonitorDashboardTab` permanece morto. Clone = `MonitorStatusTab` / `table.signals`.
- Chrome (sidebar 224px medida no desktop, Inter/Binance, Monitor activo, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks no proto, alinhados ao TSX.

PNGs: `975-A-desktop-1280x800-index.png` (board com thead + duas linhas); `975-A-mobile-390x844-index.png` (cards incumbentes).

## Produto (aceite visível — não reabrir Q2)

Q2=A: primeira visita já sinais **ou** erro, sem segundo clique. Copy de erro actual fica. Filtro default não muda. #970 não reabre. Cobertura 11/18 é *como* (subset no quadro; skip-all → erro).

| Aceite visível | Evidência (Playwright 1280×800 e 390×844) | Disposition |
|---|---|---|
| Feliz: primeira pintura já tem linhas; SOL/USDT + ETH/USDT | index desktop = 2 `tr.head-row`; mobile = 2 `.mobile-card`. Sem clique. | OK |
| Ausente catálogo vazio no feliz e no erro (cenário com favoritos) | «Nenhum ativo disponível no monitor» = 0 nos 2 HTML × 2 viewports | OK |
| Erro: copy actual + Tentar de novo; permanece Monitor | erro.html: «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + «Tentar de novo»; topbar Monitor; URL continua no proto | OK |
| Erro: ausente login | «Bem-vindo de volta» = 0; URL ≠ `/login`. `role=alert` | OK |
| Q2=A sem segundo clique | index já pinta sinais; erro já pinta alerta. Atualizar não é o caminho feliz | OK |
| Filtro default não muda | `monitor-filter-in-portfolio` com `.on`; `monitor-filter-all` sem `.on`. Label viva **Em portfólio** (TSX L1067), não «Na carteira» do body do issue — clone do vivo | OK |
| #970 não reabre | pasta HTML = `{index,erro}`; ausente `favorites.html` | OK |
| Subset 11/18 como *como* | 2 linhas de exemplo no quadro; skip-all = irmão erro (não catálogo vazio). Sem superfície «7 de fora» | OK |

Filtro que esconde todos («Não há resultado com estes filtros.») **não** tem irmão HTML. Anti-padrão «N estados ⇒ N cards» proíbe galeria no index; extra `/favorites` também proibido. Mock do ramo de filtro = P3 (copy já aceite em `design.md` para Apply). Análise/gráfico com velas = Apply (não o proto estático).

## UX

Modo Impeccable: **Operate** / refinement. Job: abrir Monitor com Favoritos já salvos e ver sinais, ou um erro com retry — nunca vazio falso.

Hierarquia: AppNav → workbench Monitor → KPIs → filterbar (Em portfólio default) → secções Em posição / Saída → `table.signals`. Delta óbvio sem redesign da board: a primeira pintura deixa de ser o catálogo vazio do incidente.

Carga cognitiva: 2 pares no feliz = o contrato (subset), não um wall de 18. Erro nomeia a falha e oferece Tentar de novo no chrome Monitor.

Vale emocional do incidente (Monitor «vazio» com 18 favoritos) → pico (SOL/ETH na board, ou erro explícito) → fim (retry sem login; recarregar não prende).

## Acessibilidade

- `lang=pt-BR`; `:focus-visible` incumbente; `prefers-reduced-motion` no proto.
- Landmarks: `aside[aria-label=Navegação principal]` + `h1` «Monitor de sinais» + `filterbar` `aria-label="Filtros do monitor"` + `table.signals`.
- Erro: `role=alert` + `data-testid=monitor-load-error`. Retry: `<button class="monitor-retry">`, focável (focus programático = activeElement), **não** disabled. Altura medida 44px nos dois viewports (`desktop-erro-retry-44` / `mobile-erro-retry-44`).
- GO de estado não é só cor: texto «Não foi possível…» / pills Em posição · Saída / cobertura.
- Alvos 44px no retry já no vivo / P3 aceite em `design.md`. Botões de linha 30px = clone vivo, não redesenhar.

## Responsividade

- Desktop 1280×800: sidebar 224×800; `table.signals` visível; overflow-x documento = 0. Acções da linha (Ver Trades / Operar) recortam à direita — incumbente da board, P3 já no autor. PNG `975-A-desktop-1280x800-{index,erro}.png`.
- Mobile 390×844 index: sidebar 0; cards SOL/ETH; tabela `display:none` como o vivo. Overflow-x = 0. PNG `975-A-mobile-390x844-index.png`.
- Mobile 390×844 erro: alerta + retry visíveis a largura do board. Thead vazio ainda pinta por `table-wrap { display:block }` inline (vivo esconde tabela <740px e o ramo de erro **substitui** a tabela). P3. PNG `975-A-mobile-390x844-erro.png`.
- Busca do topbar clipa «Buscar par, est» a 390 — clone denso, P3.

## Estados

Mock cobre: feliz (index, primeira pintura com subset) e erro de carga (erro.html, skip-all / análise `[]` com favoritos). Não mocka: loading, filtro sem resultado, catálogo vazio **real** (sessão sem par crypto), sessão morta→login (já é o shell). Cobertura de mock = P3. Vazio real reusa copy viva; mocká-lo como irmão confundiria com o incidente.

## Design specificity

A tela é o Monitor do Cripto Farol depois do incidente DEV 2026-09-18 18:07 (200 `[]` pintou catálogo vazio com 18 favoritos). Não iria a um SaaS genérico inalterado. Folha Binance; `DESIGN.md` não reescrito. Refinement, não redesign.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Feliz lista pares; erro nomeia falha de carga; KPIs 0 no erro |
| 2 | Match between system and real world | 4 | Copy de operador; erro actual confirmado; não path de API na board |
| 3 | User control and freedom | 4 | Tentar de novo permanece em `/monitor` (Q2=A); sem segundo clique no feliz |
| 4 | Consistency and standards | 3 | Clone da board; erro.html junta card de erro **e** thead vazio (vivo é XOR) |
| 5 | Error prevention | 4 | 200 `[]`+favoritos deixa de mentir catálogo vazio; skip-all → erro |
| 6 | Recognition rather than recall | 4 | Estados nomeados na própria board; operador não precisa lembrar o incidente |
| 7 | Flexibility and efficiency | 3 | Filtros do vivo no mock; retry é o acelerador; filtro vazio sem irmão |
| 8 | Aesthetic and minimalist design | 3 | Clone denso; clip de acções a 1280 e busca a 390 |
| 9 | Help users recognize/recover errors | 4 | Erro + retry; «isto não significa que não há estratégias» |
| 10 | Help and documentation | 3 | Screen help incumbente; Ajuda no nav |
| **Total** | | **36/40** | **Good** |

## Cognitive load

Checklist: 1 workbench; 1 board; 2 pares no feliz. Erro não compete no index. **Pass** (0 falhas). Decisão no glance ≤4 (abrir gráfico / trades / operar / retry).

## Emotional journey

Vale (DEV: «Nenhum ativo disponível no monitor» com 18 favoritos na mesma sessão) → pico (SOL/ETH na `table.signals`, ou erro com retry) → fim (primeira visita já resolve; recarregar não prende). Reassegurança: «A lista de favoritos não chegou. Isto não significa que não há estratégias.»

## Personas (só neste snapshot)

1. **Alex (operador diário):** abre `/monitor`, vê SOL/ETH na primeira pintura, não o vazio do incidente. Sem clicar Atualizar.
2. **Riley (stress do incidente):** erro ≠ vazio; skip-all ≠ «Nenhum ativo disponível no monitor»; Favoritos / #970 intacto.
3. **Sam / Casey (mobile 390):** cards repetem os pares; retry 44px visível. Thead vazio residual no erro (P3).

## Strengths

- Clone estrutural de `/monitor`, não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: primeira pintura = sinais (subset) **ou** erro actual.
- Q2=A visível sem segundo clique. Copy de erro intacta. Default Em portfólio intacto.
- Sem extra `/favorites`. Cobertura parcial no quadro, sem UI «7 de fora».
- Erro é `monitor-empty-card` a largura do board (não o retry clipado *dentro* da tabela, P2 do #970).

## Playwright (esta sessão)

- Desktop 1280×800 e mobile 390×844: aceite visível do contrato nas 2 URLs. 0 console / 0 pageerror. Overflow-x = 0.
- Live `/monitor` → Playwright `/login` (descartado). GET 200 no path não conta.
- PNGs: `975-A-desktop-1280x800-{index,erro}.png`, `975-A-mobile-390x844-{index,erro}.png`, `975-A-live-monitor.png`. Gate: `975-A-gate.json` (92/92).
- Landmarks no DOM (`th.textContent`) = 8/8. Uppercase visual do thead é CSS incumbente.

## Prototype Validation (rubrica)

`design.md` secção Prototype Validation presente: Playwright desktop+mobile, asserts do contrato. Esta sessão **reexecutou** o browser nas 2 URLs públicas HTTPS e confirma o aceite. Curl/GET 200 não substituiu o Playwright. Disco == HTTPS nos dois ficheiros.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível. Thead vazio no irmão erro e clip incumbente da board são P3 (Apply / clone).

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** `erro.html` pinta card de erro **e** thead vazio de `table.signals` (desktop; mobile forçado com `display:block` inline). Vivo (`MonitorStatusTab` L1113–1146) é XOR: erro **substitui** a tabela. T5 mede só o index; Apply pinta o ramo vivo. Residual — não bloqueia Design.
- **P3-2** Clip das acções da linha (Ver Trades / Operar) a 1280 — incumbente da board; já no autor / `design.md`.
- **P3-3** Busca do topbar clipa placeholder a 390. Clone denso; non-goal redesign.
- **P3-4** Mobilebar do erro ainda diz «SOL/USDT 1d» (chrome copiado). Não é linha de sinal (`head-row` = 0). Apply: chrome de erro sem par fantasma.
- **P3-5** Thead proto tem `<th>Operar</th>`; vivo deixa o th de acções vazio. Catalog pede o texto «Operar» (está nos botões). Não redesenhar.
- **P3-6** Filtro sem resultado («Não há resultado com estes filtros.») sem irmão HTML. Copy já aceite em `design.md`. Não nascer galeria / `filtro.html` no index.
- **P3-7** «Tentar de novo» é `<button>` estático no proto; vivo = `fetchOpportunities(..., { refresh: true })`. Testid `monitor-load-error` já existe.
- **P3-8** Frontend consulta `/favorites/` vs flag `analysis_failed` / 503 — já aceite. Não cachear `[]` vs invalidar chave vs TTL 0. Timeout 8s. Cache **não-vazio** para Favoritos / signal_history.
- **P3-9** `MonitorDashboardTab` morto: não ressuscitar. Detector `side-tab` nos cards mobile de tier — incumbente do clone, já no Apply.
- **P3-10** Alvos 44px no retry (já no vivo). Mock sem loading e sem vazio-real. Sessão morta já é o shell `/login`.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q2=A. Não reabrir copy de erro. Não reabrir #970. Não exigir 18/18 nem superfície «7 de fora». Não exigir segundo rework de Design. Não promover thead vazio do irmão / clip 1280 / busca 390 / th Operar a P0/P1.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks `/monitor` no index (`table.signals` + 8 texts no DOM). Disco == HTTPS (index `542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116`, 31012 B). Sem galeria/ANTES-DEPOIS como index. copied > 0. Delta = feliz com sinais na primeira pintura + erro.html com copy actual. `/login` descartado. Clone **não** alegado só por sidebar 224px: prova = landmarks proto × `MonitorStatusTab.tsx`. HTTP 200 isolado não foi PASS.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 975
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P2: nenhum
P3: thead vazio no erro.html (vivo XOR); clip acções 1280; busca 390; mobilebar SOL no erro; th Operar vs actions-cell vazio; filtro vazio sem irmão; button vs refetch; cache/flag P3 já no design; MonitorDashboardTab morto; mock sem loading/vazio-real
verdict: PASS
```
