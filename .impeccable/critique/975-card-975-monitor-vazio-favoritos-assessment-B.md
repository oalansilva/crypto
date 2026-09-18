# Assessment B (detector + browser real) — card 975 · change card-975-monitor-vazio-favoritos

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `975-B-*`, `975-B-gate.py` e `975-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /monitor` · `surface: existing`.

```
Assessment B 975
digest_match: yes
detector: [] (index + erro, exit 0)
P0: nenhum
P1: nenhum
P3: clip Operar/Ver Trades 1440; thead clip 390 no erro; mobilebar SOL no erro; lang ausente no erro; DELTA:start=0; filtro.html ausente
verdict: PASS
```

- UTC: 2026-09-18T23:26Z
- Tuple (read-only): `bound_card=975` · `q_git=card-975-monitor-vazio-favoritos`. Sem `process_event`. Sem `move_agent_to_root`.
- Status GraphQL pontual (`repository.issue(number:975).projectItems`): **Design** · item `PVTI_lAHOAAHtBM4BV8b2zg7pnLg` · Project 1 `oalansilva` (`MVP Cripto - Beta Fechado`). GraphQL remaining=4975. MUST NOT `gh project item-list`.
- REST `gh api repos/oalansilva/crypto/issues/975` (não `gh issue view`): OPEN *«DEV: Monitor fica vazio com Favoritos carregados»* · labels `bug` `priority:P0` `front:monitor` `type:produto`.
- Protótipo canónico: `frontend/public/prototypes/card-975-monitor-vazio-favoritos/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos/
- Irmão (não canónico): `erro.html`. Sem extra `/favorites`. `filtro.html` / `home.html` / `inicio.html` disco ausente; HTTPS 404.
- Digest index esperado: `542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116` · 31012 B. Disco MUST == HTTPS: **IDENTICAL**.
- Irmão `erro.html`: sha256 `fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34` · 24112 B. Disco == HTTPS: **IDENTICAL**.
- Rota viva `https://dev.criptofarol.com.br/monitor` → browser **`/login`** («Bem-vindo de volta»). Login **não** é a rota; **não** autoriza PASS de clone. GET curl `/monitor` HTTP 200 · 455 B (shell Vite) **não** é PASS. Clone avaliado no proto HTTPS.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports **1440×900** e **390×844**. `colorScheme: dark`. URL canónica do proto (não `file://`). Critério igual nos dois viewports (autor usou 1280×800; 1440 cobre o mesmo contrato).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` nos dois HTML versionados (cwd worktree). Overlay `detect.js` não injectado.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116` | 31012 |
| HTTPS GET `/prototypes/card-975-monitor-vazio-favoritos/` | idem | 31012 HTTP 200 · `cmp` **IDENTICAL** |
| HTTPS GET `…/index.html` | idem | 31012 · **IDENTICAL** |
| Esperado (prompt / `design.md`) | idem | 31012 |
| Disco `erro.html` | `fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34` | 24112 · HTTPS **IDENTICAL** |

HTTP 200 isolado **não** é o gate. Digest não mudou → evidência do autor válida.

## 2. Detector Impeccable

- Alvos: `index.html` e `erro.html`.
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0 nos dois.
- Sem finding crítico. Sem `side-tab` (o `design.md` aceitava `side-tab` ×2 como P3 incumbente; o HTML versionado **não** dispara o detector).
- **Classificação:** nenhum finding de detector para reabrir como P0/P1.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /monitor` · `surface: existing`. **Não** é rota de catálogo emprestada. Sem extra `/favorites`.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/monitor`: `selectors: ["table.signals"]`, `texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]`.
- Index no browser (1440 e 390): `table.signals`=**2** (secções Em posição + Saída / cobertura); thead `textContent` contém todos os 8 texts do catálogo (innerText uppercase no 1440 — landmark presente). Sidebar 224px no desktop (`offsetWidth=224`); **chrome 224px sozinho não passa** — a listing `table.signals` + headers está no DOM e visível no 1440.
- Mobile 390: tabela `display:none` como o vivo; cards incumbentes mostram SOL/USDT e ETH/USDT. Landmarks permanecem no HTML/`textContent` do thead.
- Pares `COPIED:start`/`COPIED:end` index = **7/7**; soma UTF-8 copiada **21481** (> 0); total 31012 = 21481 copied + 9531 generated. `erro.html` 5/5 · 20678 copied. `DELTA:start`=0 — delta nas linhas/tbody, não região nova / painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Substring `ANTES`/`DEPOIS` só em comentário HTML do index («Sem painel ANTES/DEPOIS») — innerText do body **não** as mostra. URL canónica = `index.html`. Sem grelha «N estados».
- Caminho feliz visível: linhas **SOL/USDT** (Cruzamento EMA · Em posição) e **ETH/USDT** (RSI swing · Saída / cobertura); KPIs 1 / 1 / 2 / 2; default **Em portfólio** + Todos intacto; **ausente** «Nenhum ativo disponível no monitor».
- `lang=pt-BR` no index; ausente no `erro.html` (P3).

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning relevante = 0; pageerror = 0; responses ≥400 no proto = 0. Overflow documento `scrollWidth<=clientWidth+1` (1440==1440; 390==390). Gate bruto: `.impeccable/critique/975-B-gate.json`. «Tentar de novo» box 126.2×**44** px.

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /monitor` / `surface: existing` | PASS | — |
| 3 | Landmarks `/monitor`: `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia | PASS (2 tabelas + thead) | PASS (cards + thead no DOM; tabela `display:none` incumbente) |
| 4 | Chrome 224px **não** é a prova sozinha | PASS (sidebar 224 + listing) | PASS (sidebar hidden; listing via cards) |
| 5 | COPIED 7/7 · 21481 > 0; 0 botões Antes/Depois; sem painel das N / ANTES/DEPOIS | PASS | PASS |
| 6 | Feliz: SOL/USDT + ETH/USDT; **ausente** «Nenhum ativo disponível no monitor» | PASS | PASS |
| 7 | `erro.html`: «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + «Tentar de novo»; chrome Monitor; **não** catálogo vazio; URL proto (não `/login`) | PASS | PASS |
| 8 | Sem extra `/favorites`; 0 console / 0 pageerror | PASS | PASS |
| 9 | Detector sem finding crítico | PASS | — |
| 10 | Live `/monitor` sem sessão → `/login`; login **não** usado como PASS | PASS | — |

Pixels index desktop: pares SOL/USDT e ETH/USDT na `table.signals`; headers PAR / ESTRATÉGIA · STATUS · PREÇO · DISTÂNCIA · 7D · RISCO ATÉ STOP · TAGS · OPERAR; KPIs 1/1/2/2; filtro Em portfólio; sem empty. Sem botões Antes/Depois. Coluna Operar empilha «Ver Trades» sobre «Operar» (clip incumbente).

Pixels index mobile: cards SOL/USDT · ETH/USDT; KPIs empilhados; «2 resultados»; sem empty. Thead da tabela não é a superfície visível (cards).

Pixels erro desktop: copy de falha + «Tentar de novo» 44px; KPIs a 0; thead vazia visível; **não** «Nenhum ativo disponível no monitor».

Pixels erro mobile: mesma copy + retry; thead larga recortada à direita (P3); mobilebar «SOL/USDT 1d» (chrome clone, não linha de sinal).

Rota viva **não usada como prova de clone** (caiu em `/login`). HTTP 200 do GET `/monitor` (455 B) **não** conta.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Clone `/monitor` com landmarks do catálogo; copied 21481 > 0; sem painel ANTES/DEPOIS nem grelha das N; feliz com pares crypto; irmão erro com copy actual + Tentar de novo; empty de catálogo **ausente** no index e no erro (DOM e innerText); digest HTTPS == disco == esperado; detector `[]`. Fidelidade + contrato visível ok → **não BLOCKED**. Chrome 224px não foi tratado como prova suficiente.

### P1 — nenhum

Dois estados visíveis em URLs distintas (index feliz / erro). Empty de catálogo **não** ocupa o feliz nem o erro. Retry permanece no proto. Login da rota viva não foi usado como PASS. Estado de filtro («Não há resultado com estes filtros.») não tem URL irmã — ver P3; o Prototype do `design.md` só declara index + erro.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Clip desktop da coluna Operar** («Ver Trades» / «Operar» empilhados). Já no `design.md` (clip a 1280 da board — incumbente, não redesenhar).
- **P3-2 Thead clip no 390 em `erro.html`:** tabela larga (`table.signals`) recorta TAGS / OPERAR. Copy de erro completa no DOM. Non-goal: não redesenhar Monitor.
- **P3-3 Cards mobile no index** (tabela `display:none`) — clone vivo. Landmarks via thead no DOM + cards SOL/ETH.
- **P3-4 Mobilebar `SOL/USDT 1d` no `erro.html`** — chrome incumbente; não é catálogo vazio nem linha de sinal.
- **P3-5 `lang` ausente no `erro.html`** (index tem `pt-BR`).
- **P3-6 `DELTA:start`=0** no index: delta é tbody/linhas, não região marcada. Copied 7/7 > 0.
- **P3-7 `filtro.html` ausente** (disco + HTTPS 404). Copy de Entra «Não há resultado com estes filtros.» só no `design.md`. Prototype canónico = index + erro; não é galeria das N no index.
- **P3-8 Alvos `row-action` 30px** vs retry já a 44px. Retry medido 44px. Já P3 no Apply contract.
- **P3-9 Detector `side-tab`** antecipado no `design.md` — **não disparou** neste HTML. Sem finding.

Observações (não-findings): overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/monitor` autenticado não usado. Default visível «Em portfólio» (não o wording «Na carteira» do Entra) — clone incumbente; default vs Todos **não muda**. Needle «Nenhum ativo disponível no monitor» **ausente** inclusive no HTML (não só no innerText).

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]`; digest idêntico nas pontas index/erro e igual ao esperado; clone+delta (não ANTES/DEPOIS); `/login` vivo não usado como prova; matriz visível desktop+mobile no index e no irmão erro. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos/
- Digest index: `542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116` · 31012 B
- Digest erro: `fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34` · 24112 B
- Snapshot: `.impeccable/critique/975-card-975-monitor-vazio-favoritos-assessment-B.md`
- Gate bruto: `.impeccable/critique/975-B-gate.json`
- PNGs: `975-B-desktop-1440x900-index.png`, `975-B-desktop-1440x900-erro.png`, `975-B-mobile-390x844-index.png`, `975-B-mobile-390x844-erro.png`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
