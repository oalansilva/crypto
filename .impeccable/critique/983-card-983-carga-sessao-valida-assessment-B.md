# Assessment B (detector + browser real) — card 983 · change card-983-carga-sessao-valida

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `983-B-*`, `983-B-gate.py` e `983-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /favorites` · `surface: existing`.

```
Assessment B 983
digest_match: yes
detector: 2 findings side-tab (index) + 2 (erro); monitor/inicio/carteira/carteira-erro [] — todos P3 incumbente
P0: nenhum
P1: nenhum
P3: side-tab ×2 cards mobile de tier; truncagem Estratégia 1440; header Todas 2 no erro; thead/cards 390; clip Operar/Ver Trades monitor 1440; mobilebar SOL no monitor; DELTA:start=0
verdict: PASS
```

- UTC: 2026-09-19T03:05Z
- Tuple (read-only): `bound_card=983` · `q_git=card-983-carga-sessao-valida`. Sem `process_event`. Sem `move_agent_to_root`.
- Status GraphQL pontual (`repository.issue(number:983).projectItems`): **Design** · item `PVTI_lAHOAAHtBM4BV8b2zg7sRmk` · Project 1 `oalansilva`. GraphQL remaining=4826. MUST NOT `gh project item-list`.
- REST `gh api repos/oalansilva/crypto/issues/983` (não `gh issue view`): OPEN *«PROD: Favoritos mostra erro de carga com sessão válida e catálogo intacto»* · labels `bug` `priority:P0` `front:backtest` `type:produto`.
- Protótipo canónico: `frontend/public/prototypes/card-983-carga-sessao-valida/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/
- Irmão (não canónico): `erro.html`. Extras: `monitor.html` · `inicio.html` · `carteira.html` · `carteira-erro.html`.
- Digest index esperado: `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145` · 43556 B. Disco MUST == HTTPS: **IDENTICAL**.
- Irmão `erro.html`: sha256 `aff6abcdb57fd4267fd61945adb0d8a307e3b2c7ecdcc14a18d6c96a1fa51d19` · 33720 B. Disco == HTTPS: **IDENTICAL**.
- Extras: monitor `51e5ee44f8833d254ef843bbf7893fc2657a36d7a12d476015adb0179856ee9e` · 31034 B; inicio `48892e62a63666d741676e23e6d139fcdd89a9b3e579cc81cd773d6af0cf196a` · 14478 B; carteira `6808e6cc9fde934f137d217b7c0fbc77b1efacadd56f8181d3c17686f6dcf6d4` · 16549 B; carteira-erro `0b44d6a49bc09afc5250eb8de66741c4c3d28cab341391ac88a27dedf0b54f53` · 15197 B. Todos IDENTICAL disco == HTTPS.
- Rota viva `https://dev.criptofarol.com.br/favorites` → browser **`/login`** («Bem-vindo de volta»). Login **não** é a rota; **não** autoriza PASS de clone. GET curl `/favorites` HTTP 200 · 455 B (shell Vite) **não** é PASS. Clone avaliado no proto HTTPS.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports **1440×900** e **390×844**. `colorScheme: dark`. URL canónica do proto (não `file://`). Critério igual nos dois viewports (autor usou 1280×800; 1440 cobre o mesmo contrato).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` nos seis HTML versionados (cwd worktree). Overlay `detect.js` não injectado.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145` | 43556 |
| HTTPS GET `/prototypes/card-983-carga-sessao-valida/` | idem | 43556 HTTP 200 · `cmp` **IDENTICAL** |
| HTTPS GET `…/index.html` | idem | 43556 · **IDENTICAL** |
| Esperado (prompt / `design.md`) | idem | 43556 |
| Disco `erro.html` | `aff6abcdb57fd4267fd61945adb0d8a307e3b2c7ecdcc14a18d6c96a1fa51d19` | 33720 · HTTPS **IDENTICAL** |
| Disco `monitor.html` | `51e5ee44f8833d254ef843bbf7893fc2657a36d7a12d476015adb0179856ee9e` | 31034 · HTTPS **IDENTICAL** |
| Disco `inicio.html` | `48892e62a63666d741676e23e6d139fcdd89a9b3e579cc81cd773d6af0cf196a` | 14478 · HTTPS **IDENTICAL** |
| Disco `carteira.html` | `6808e6cc9fde934f137d217b7c0fbc77b1efacadd56f8181d3c17686f6dcf6d4` | 16549 · HTTPS **IDENTICAL** |
| Disco `carteira-erro.html` | `0b44d6a49bc09afc5250eb8de66741c4c3d28cab341391ac88a27dedf0b54f53` | 15197 · HTTPS **IDENTICAL** |

HTTP 200 isolado **não** é o gate. Digest não mudou → evidência do autor válida.

## 2. Detector Impeccable

- Alvos: `index.html`, `erro.html`, `monitor.html`, `inicio.html`, `carteira.html`, `carteira-erro.html`.
- `index.html` exit 2 → 2 findings `side-tab` (L145 `.fav-up` / L146 `.turquoise` `border-left:3px`).
- `erro.html` exit 2 → os mesmos 2 `side-tab` no clone dos cards de tier (L143 / L144).
- `monitor.html` / `inicio.html` / `carteira.html` / `carteira-erro.html` → `[]`, exit 0.
- **Classificação:** P3 incumbente do clone `/favorites` (já no `design.md`: «Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone #970, não redesenhar»). Slop de CSS de tier, não contrato de carga/renovação. **Não** reabre como P0/P1. Sem finding crítico.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /favorites` · `surface: existing`. **Não** é rota de catálogo emprestada. Extras Monitor / Início / Carteira declarados como URLs próprias.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/favorites`: `selectors: ["table.fav-strategies"]`, `texts: ["Estratégias favoritas", "Symbol", "Estratégia", "Ações"]`.
- Index no browser (1440 e 390): `table.fav-strategies`=**1**; h1 «Estratégias favoritas»; thead `textContent` **Symbol** / **Estratégia** / **Ações** (innerText uppercase no 1440 — landmark presente). Filtro visível `Symbol` / `Todos`. Sidebar 224px no desktop (`offsetWidth=224`); **chrome 224px sozinho não passa** — a listing `table.fav-strategies` + headers está no DOM e visível no 1440.
- Mobile 390: tabela `display:none` como o vivo; cards incumbentes mostram SOL/USDT e ETH/USDT. Landmarks permanecem no HTML/`textContent` do thead + filtro.
- Pares `COPIED:start`/`COPIED:end` index = **4/4**; soma UTF-8 copiada **7781** (> 0); total 43556 = 7781 copied + 35775 generated. `erro.html` 4/4 · 7729 copied. `monitor.html` 7/7 · 21504 copied. `inicio.html` 3/3 · 8806. `carteira.html` / `carteira-erro.html` 3/3 · 10819. `DELTA:start`=0 — delta nas linhas/tbody/KPI, não região nova / painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Substring `ANTES`/`DEPOIS` só em comentário HTML («Sem painel ANTES/DEPOIS») — innerText do body **não** as mostra. URL canónica = `index.html`. Sem grelha «N estados».
- Caminho feliz visível: linhas **SOL/USDT** e **ETH/USDT**; footer **«2 estratégias carregadas»**; **ausente** «Não foi possível carregar as estratégias favoritas.»; **ausente** «Nenhuma estratégia favorita encontrada»; **ausente** «A sessão continua válida» no index.
- `lang=pt-BR` em todas as páginas versionadas.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning relevante = 0; pageerror = 0; responses ≥400 no proto = 0. Overflow documento `scrollWidth<=clientWidth+1` (1440==1440; 390==390). Gate bruto: `.impeccable/critique/983-B-gate.json`. «Tentar de novo» box 133.3×**44** px; `href=index.html`.

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /favorites` / `surface: existing` | PASS | — |
| 3 | Landmarks `/favorites`: `table.fav-strategies` + «Estratégias favoritas» + Symbol + Estratégia + Ações | PASS (1 tabela + thead) | PASS (cards + filtro; thead no DOM; tabela incumbente `display:none`) |
| 4 | Chrome 224px **não** é a prova sozinha | PASS (sidebar 224 + listing) | PASS (sidebar hidden; listing via cards) |
| 5 | COPIED 4/4 · 7781 > 0; 0 botões Antes/Depois; sem painel das N / ANTES/DEPOIS | PASS | PASS |
| 6 | Feliz: SOL/USDT + ETH/USDT; footer «2 estratégias carregadas»; **ausente** catálogo vazio; **ausente** erro #970 | PASS | PASS |
| 7 | `erro.html`: «Não foi possível carregar as estratégias favoritas.» + «A sessão continua válida» + «Tentar de novo»; chrome Favoritos; **não** catálogo vazio; URL proto (não `/login`) | PASS | PASS |
| 8 | `monitor.html`: `table.signals` + landmarks Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; SOL/ETH; **ausente** falha falsa / empty | PASS | PASS (cards + thead no DOM) |
| 9 | `inicio.html`: KPI «Melhor estratégia (7d)» + «Médias Móveis: Tendência Confirmada»; **ausente** «Não foi possível carregar `/api/favorites`.» | PASS | PASS |
| 10 | `carteira.html`: saldos ETH/BTC visíveis; **ausente** «Erro ao carregar» / «Falha ao carregar saldos» | PASS | PASS (cards ETH $1,415.50 · BTC $262.10) |
| 11 | `carteira-erro.html`: «Erro ao carregar» + «Falha ao carregar saldos»; URL proto (não `/login`) | PASS | PASS |
| 12 | 0 console / 0 pageerror; detector sem finding crítico | PASS | PASS |
| 13 | Live `/favorites` sem sessão → `/login`; login **não** usado como PASS | PASS | — |

Pixels index desktop: pares SOL/USDT e ETH/USDT na `table.fav-strategies`; headers SYMBOL / ESTRATÉGIA / AÇÕES; footer «2 estratégias carregadas»; filtro Todos; sem empty; sem erro #970. Sem botões Antes/Depois. Coluna Estratégia trunca `Mé…` / `Salv…` (clip incumbente).

Pixels index mobile: cards SOL/USDT · ETH/USDT com nomes de estratégia completos; footer «2 estratégias carregadas»; sem empty.

Pixels erro desktop: copy de falha #970 + «Isto não significa que o catálogo está vazio. A sessão continua válida.» + «Tentar de novo» 44px; chip «CARGA FALHOU»; footer «Carga falhou»; **não** «Nenhuma estratégia favorita encontrada».

Pixels erro mobile: mesma copy + retry 44px visível; sem linhas de catálogo.

Pixels monitor desktop: `table.signals` ×2 (Em posição + Saída / cobertura); SOL/USDT + ETH/USDT; KPIs 1/1/2/2; default Em portfólio; sem empty / sem «Não foi possível carregar as estratégias.». Coluna Operar empilha «Ver Trades» sobre «Operar» (clip incumbente).

Pixels monitor mobile: cards SOL/USDT · ETH/USDT; mobilebar «SOL/USDT 1d» (chrome clone); tabela `display:none`; sem empty.

Pixels inicio desktop+mobile: KPI «MELHOR ESTRATÉGIA (7D)» (CSS `text-transform:uppercase`) com «Médias Móveis: Tendência Confirmada» + SOL/USDT; sem erro falso da lista.

Pixels carteira desktop: tabela ETH/BTC com valores USD; **não** «Erro ao carregar». Mobile: cards ETH · $1,415.50 / BTC · $262.10.

Pixels carteira-erro: painel «Erro ao carregar» / «Falha ao carregar saldos» + «Tentar novamente»; chrome Carteira; URL proto.

Rota viva **não usada como prova de clone** (caiu em `/login`). HTTP 200 do GET `/favorites` (455 B) **não** conta.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Clone `/favorites` com landmarks do catálogo; copied 7781 > 0; sem painel ANTES/DEPOIS nem grelha das N no index; feliz com pares crypto e footer 2; irmão erro com copy #970 + Tentar de novo; extras Monitor/Início/Carteira mostram lista/saldos (não erro falso); `carteira-erro.html` mantém erro real; digest HTTPS == disco == esperado em todas as pontas; detector sem crítico. Fidelidade + contrato visível ok → **não BLOCKED**. Chrome 224px não foi tratado como prova suficiente.

### P1 — nenhum

Seis URLs distintas (index feliz / erro / monitor / inicio / carteira / carteira-erro). Empty de catálogo **não** ocupa o feliz nem o erro. Retry permanece no proto e aponta à lista. Login da rota viva não foi usado como PASS. Extras não estão no index como galeria.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 `side-tab` ×2** nos cards mobile de tier (detector L145–146 index; irmão erro L143–144). Já no `design.md`.
- **P3-2 Truncagem desktop** do nome na coluna Estratégia (`Mé…` / `Salv…`). Incumbente #970; Non-goal: não redesenhar a grade.
- **P3-3 Contadores do header (Todas 2 / Top picks 1 / Acompanhar 1) no estado de erro.** Incumbente #970.
- **P3-4 Thead clip / card-stack no 390** do clone `/favorites`. Landmarks via filtro + cards; clone vivo.
- **P3-5 Alvos do «Tentar de novo»** — medido 133.3×**44** px nos dois viewports. Já P3 no Apply contract; altura cumprida.
- **P3-6 Clip desktop da coluna Operar no extra `monitor.html`** («Ver Trades» / «Operar» empilhados). Incumbente Monitor; Non-goal: não redesenhar.
- **P3-7 Mobilebar `SOL/USDT 1d` no extra `monitor.html`** — chrome incumbente; não é catálogo vazio nem linha de sinal.
- **P3-8 `DELTA:start`=0** no index: delta é tbody/linhas/footer, não região marcada. Copied 4/4 > 0.
- **P3-9 Unificar `authFetch` / axios / `fetchJson`; `AbortSignal`; `fetchId` no catch da Carteira; `MonitorDashboardTab` morto; testids.** Já P3 de Apply no `design.md`. Contrato visível (lista/saldos) cumprido no proto.

Observações (não-findings): overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/favorites` autenticado não usado. Nav Monitor no shell do index = clone `/favorites`, extra `/monitor` é `monitor.html`. KPI do Início pinta o rótulo em uppercase via CSS; innerText casefold confirma «Melhor estratégia (7d)». Needle «Nenhuma estratégia favorita encontrada» **ausente** inclusive no HTML do index e do erro.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `side-tab` classificado P3; digest idêntico nas 6 pontas e igual ao esperado; clone+delta (não ANTES/DEPOIS); `/login` vivo não usado como prova; matriz visível desktop+mobile no index, irmão erro e extras. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/
- Digest index: `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145` · 43556 B
- Digest erro: `aff6abcdb57fd4267fd61945adb0d8a307e3b2c7ecdcc14a18d6c96a1fa51d19` · 33720 B
- Snapshot: `.impeccable/critique/983-card-983-carga-sessao-valida-assessment-B.md`
- Gate bruto: `.impeccable/critique/983-B-gate.json`
- PNGs: `983-B-desktop-1440x900-index.png`, `983-B-desktop-1440x900-erro.png`, `983-B-desktop-1440x900-monitor.png`, `983-B-desktop-1440x900-inicio.png`, `983-B-desktop-1440x900-carteira.png`, `983-B-desktop-1440x900-carteira-erro.png`, `983-B-mobile-390x844-index.png`, `983-B-mobile-390x844-erro.png`, `983-B-mobile-390x844-monitor.png`, `983-B-mobile-390x844-inicio.png`, `983-B-mobile-390x844-carteira.png`, `983-B-mobile-390x844-carteira-erro.png`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
