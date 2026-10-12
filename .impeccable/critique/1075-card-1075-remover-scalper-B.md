# Assessment B (detector + browser real) — card 1075 · change card-1075-remover-scalper

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Único ficheiro escrito neste filho: este snapshot (shots de trabalho em `/tmp/1075-B-shots/`, não versionados).
> Modelo declarado: rótulo **Grok 4.6**, slug **`cursor-grok-4.6-high`**.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /monitor` · `surface: existing`.

```
Assessment B 1075
model: Grok 4.6 (cursor-grok-4.6-high)
digest_match: disk==HTTPS==expected IDENTICAL; HTTP 200
detector: [] index exit 0
P0: nenhum
P1: nenhum
P2: nenhum
P3: DELTA:start=0; tabela mobile 0×0+cards; clip Operar; busca truncada 390; posthog 404 no extra landing; title Ajuda card-718; overlay detect.js não injectado
verdict: PASS
```

- UTC: 2026-10-02T02:33Z
- Tuple (read-only): `bound_card=1075` · `q_git=card-1075-remover-scalper` · Status=Design (bind do prompt; issue OPEN). Sem `process_event`. Sem `move_agent_to_root`.
- REST `gh api repos/oalansilva/crypto/issues/1075`: OPEN *«Remover o scalper (Scalp Jev) inteiro: tela, laço, ordens, tabelas e specs»*.
- Protótipo canónico: `frontend/public/prototypes/card-1075-remover-scalper/index.html`.
- Extras (não canónicos): `landing.html`, `ajuda.html`, `perfil.html`, `credenciais.html` — HTTP 200, digest disco == HTTPS.
- Servido: https://dev.criptofarol.com.br/prototypes/card-1075-remover-scalper/ → HTTP **200** `text/html; charset=utf-8` · 31551 B.
- Digest index esperado (prompt): `9f5dcb0c48f0de71ffdf02ce92a781bb720f1e1a01eeabc6e205025b6aab71f3` · 31551 B. Disco == HTTPS dir == HTTPS `index.html` == esperado: **IDENTICAL**.
- Rota viva `https://dev.criptofarol.com.br/monitor` → browser **`/login`** («Bem-vindo de volta» · EMAIL · SENHA · Entrar). Login **não** é a rota; **não** autoriza PASS de clone. GET curl `/monitor` HTTP 200 · 455 B (shell Vite) **não** é PASS. Clone avaliado no proto servido (digest idêntico ao disco).
- Landing viva: `https://criptofarol.com.br/` HTTP **200** · 27210 B · sha256 `ac72b30f01c26471612ba40ca1cab1346b8a7e904fcf4875edeff1ddb1f87205`. Ainda contém 4 menções visíveis a «scalp» (produto vivo, pré-Apply). Extra `landing.html` tem **0** menções visíveis.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`, `executable_path` do cache host. `playwright-cli-headed` **ausente** no PATH; IDE browser do host **sem tab** («No browser tab available»). Viewports **1440×900** e **390×844**. `colorScheme: dark`. URL pública HTTPS (digest idêntico ao disco; `curl`/HTTP 200 **não** substitui). Screenshots de trabalho em `/tmp/1075-B-shots/` (não versionados). Snapshots **não** vazios (index desktop 128043 B · mobile 75445 B; landing extra desktop 2411971 B · mobile 1314871 B) → **não BLOCKED**.
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no `index.html` (cwd worktree). Overlay `detect.js` não injectado.
- `design_clone_gate.classify(html, '/monitor')` = **PASS**. `clone_gate_ok` = **True**. `classify(landing.html, 'landing')` = **PASS**.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `9f5dcb0c48f0de71ffdf02ce92a781bb720f1e1a01eeabc6e205025b6aab71f3` | 31551 |
| Esperado (prompt) | idem | 31551 · **IDENTICAL** |
| HTTPS GET `/prototypes/card-1075-remover-scalper/` | idem | 31551 HTTP **200** · **IDENTICAL** |
| HTTPS GET `…/index.html` | idem | 31551 HTTP **200** · **IDENTICAL** |
| Disco/HTTPS `landing.html` | `4f1bd81b49609a566261cdd8ee485a257d19d7c2740e826ba26c43201b1b53a4` | 27413 · HTTP **200** |
| Disco/HTTPS `ajuda.html` | `8ea541e1c58e9e0bceb1ee23cc5e3f5fb6ae07b59c439921571fea0838826fd4` | 11219 · HTTP **200** |
| Disco/HTTPS `perfil.html` | `cbb5a18df175b5da41ba8a01db888284579648528b69a80e93f131dd8a0db53e` | 11189 · HTTP **200** |
| Disco/HTTPS `credenciais.html` | `a0c48788dd1d25fb0c02a59a5a7fc0cd1df4e88cc9c741364e28f1d6b42c24b1` | 9653 · HTTP **200** |

HTTP 200 isolado **não** é o gate. Contrato visível medido no browser Playwright sobre a URL canónica (bytes == disco == esperado). Sem dump de HTML neste snapshot nem no retorno ao pai.

## 2. Detector Impeccable

- Alvo: `index.html` (canónico). CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-1075-remover-scalper/index.html`.
- Resultado: `[]`, **exit 0**.
- Sem finding crítico. Sem `flat-type-hierarchy`, `overused-font`, `side-tab`.
- Ignore list: `.impeccable/critique/ignore.md` **ausente**.
- Overlay live `detect.js`: **não injectado** (CLI + Playwright; IDE browser sem tab; sem live-server deste filho).
- **Classificação:** detector verde. Nada a reabrir como P0/P1. Polish incumbente do clone (cards mobile, clip Operar) não disparou o detector.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /monitor` · `surface: existing`. **Não** é rota de catálogo emprestada.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/monitor`: `selectors: ["table.signals"]`, `texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]`.
- Index no browser (1440 e 390): `table.signals`=**2** (Em posição + Saída / cobertura). `innerText` do thead desktop: `PAR / ESTRATÉGIA · STATUS · PREÇO · DISTÂNCIA · 7D · RISCO ATÉ STOP · TAGS · OPERAR` (maiúsculas por `text-transform` — **não** é landmark em falta). Landmark `7d` presente como texto `7d` / `7D` no thead (não só `Gráfico`). Sidebar **224px** no desktop (`offsetWidth=224`); **chrome 224px sozinho não passa** — listing visível 1170×126 ×2. Tokens `--bg-primary/#0b0e11` etc. presentes e **insuficientes sozinhos**.
- Mobile 390: tabelas no DOM com `offsetWidth=0` / `offsetHeight=0` (listagem desktop escondida como o vivo); cards incumbentes mostram **SOLUSDT** (Em posição) e **ETHUSDT** (Saída/cobertura) + botão **Operar**. Landmarks permanecem no `textContent` do thead.
- Pares `COPIED:start`/`COPIED:end` index = **7/7**; soma UTF-8 copiada **21854** (> 0); total 31551. `DELTA:start`/`DELTA:end` = **0/0** — o delta é a **ausência** do módulo scalper dentro da topologia copiada, não uma região nova / painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. `innerText` do body do index **não** contém ANTES/DEPOIS. URL canónica = `index.html`. **Sem grelha «N estados ⇒ N cards».** Sem `scalp-module` / `[class*='scalp']` no DOM.
- Extras **não fundidos** no index: sem FAQ, sem «Quero meus 6 meses», sem Meu Perfil/Credenciais como superfície. Filenames dos extras só no comentário HTML do proto (não visível).
- `lang=pt-BR`. Título visível: «Monitor de sinais». Proto title: «Monitor de sinais — Cripto Farol». Login chrome **ausente** no proto.
- Needle visível `scalp`/`scalper` no `innerText` do index, landing extra, ajuda, perfil e credenciais = **[]**. Menções a scalp no source = só comentários HTML (`DELTA: módulo do scalper ausente` / `zero menção a scalper/scalp`). Sem banner / Telegram / texto de descontinuação.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error do **index isolado** = 0; warning = 0; pageerror = 0; responses ≥400 no index isolado = 0 (logo + mark 200). Overflow documento `scrollWidth<=clientWidth+1` (1440==1440; 390==390). `curl`/HTTP 200 não substitui.

Landing extra: console error 1 = 404 `./posthog-config.js` (script do clone v4; ficheiro **não** está nesta pasta do proto). Não é furo de produto do Monitor. «saiu» no innerText = frase incumbente «Confira como a estratégia se saiu antes» — **falso positivo** de descontinuação.

Fluxo exercido: vista canónica HTTPS nos dois viewports; extras no mesmo prefixo; landing viva; Monitor DEV sem sessão → `/login` (não usada como prova). Este filho MUST NOT autenticar Playwright na viva.

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == HTTPS == esperado (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /monitor` / `surface: existing` | PASS | — |
| 3 | Landmarks `/monitor`: `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia | PASS (2 tabelas visíveis 1170×126; thead 7D) | PASS (cards SOLUSDT/ETHUSDT + thead no DOM; tabela 0×0 incumbente) |
| 4 | Chrome 224px **não** é a prova sozinha | PASS (sidebar 224 + listing + KPIs) | PASS (sidebar `display:none`; listing via cards) |
| 5 | COPIED 7/7 · 21854 > 0; 0 botões Antes/Depois; sem painel das N | PASS | PASS |
| 6 | Módulo scalper ausente; zero innerText scalp/scalper; sem anunciar saída | PASS | PASS |
| 7 | Board intacta: Em posição (1) · Saída/cobertura (1) · KPIs 1/1/2/2 · filtros · Operar | PASS | PASS (Operar nos cards) |
| 8 | Extras não fundidos no index | PASS | PASS |
| 9 | Extra landing: FAQ + «Quero meus 6 meses grátis» + 0 scalp visível (vivo ainda tem 4) | PASS | PASS |
| 10 | Ajuda / Perfil / Credenciais: 0 scalp visível; Operar/Spot ficam | PASS | PASS |
| 11 | Live `/monitor` sem sessão → `/login`; login **não** usado como PASS | PASS | PASS |
| 12 | Detector `[]`; index isolado 0 console / 0 pageerror | PASS | PASS |

Pixels desktop index: shell autenticado (sidebar Monitor 224px, Favoritos/Descoberta/Combo/Carteira/Ajuda); **sem** bloco Scalp BTCUSDT entre page-sub e KPIs; KPIs Em posição 1 / Saída 1 / Total 2 / Em carteira 2; filtros Em portfólio / Timeframe / Estrelas; tabelas SOLUSDT Em posição $148.22 e ETHUSDT Saída $3,412.50; headers PAR / ESTRATÉGIA · STATUS · PREÇO · DISTÂNCIA · 7D · RISCO ATÉ STOP · TAGS · OPERAR; botões Abrir Gráfico / Ver Trades / Operar. Sem empty. Sem «Bem-vindo de volta».

Pixels mobile index: mesmo chrome de Monitor (título, KPIs, filtros); cards SOLUSDT / ETHUSDT com Operar; busca truncada («Buscar par, est»); sem grelha de estados; sem módulo scalp.

Pixels live Monitor (ambos): card de login. **Não confrontado com o proto.**

Pixels landing extra (ambos): hero «Comprar ou vender cripto? O Cripto Farol responde.» · FAQ · CTA «Quero meus 6 meses grátis». Sem scalp visível. Sem ANTES/DEPOIS como painel.

Pixels landing viva (ambos): mesma topologia v4; **ainda** fala em scalp direcional BTCUSDT no FAQ/copy (produto pré-Apply). Não é defeito do proto extra.

## 5. Confronta Entra (só o visível no proto; backend/API = Apply)

| Entra visível | Proto (browser) | Disposition |
|---|---|---|
| Some o módulo do scalper em `/monitor` (desktop e mobile) | Sem Scalp BTCUSDT, sem interruptor, sem `[class*='scalp']`; KPIs/board/Operar ficam | PASS |
| Em posição, Saída/cobertura, KPIs e filtros ficam | 1+1 linhas, KPIs 1/1/2/2, filtros visíveis | PASS |
| Ajuda / Perfil / Credenciais / landing v4 sem scalper/scalp | innerText extras = 0 hits; vivo ainda tem 4 (pré-Apply) | PASS |
| Sem banner, Telegram ou texto de descontinuação | Sem match de descontinuação; «se saiu antes» é copy v4 de backtest | PASS |
| Extras não entram no index; sem painel de 6 estados nem ANTES/DEPOIS | Index = clone `/monitor`; 0 botões Antes/Depois | PASS |
| Operar / Carteira / chave Spot ficam | Operar nas linhas/cards; Credenciais Spot para Operar; Perfil Spot sem saque | PASS |
| `/api/scalp/status` 404, flags, migração, Jev | Não são tela; não geram P0/P1 de browser | P3 Apply |

## 6. Nielsen (observado no browser; sem ensaio de personas)

Assessment B não pontua design-director (isso é A). Heurísticas só como evidência visível:

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Monitor de sinais, última leitura 18:07, KPIs, Status nas linhas | — |
| 2 | Match com o mundo | Par/estratégia, preço, distância, risco até stop | — |
| 3 | Controlo do utilizador | Filtros, Operar, Recolher menu, Voltar ao Perfil | — |
| 4 | Consistência | Clone do workbench `/monitor` + tokens; extras clonam as próprias vivas | — |
| 5 | Prevenção de erro | Credenciais: «Não use e-mail ou senha»; Spot sem saque | — |
| 6 | Reconhecimento | Headers da board iguais ao catálogo | — |
| 7 | Flexibilidade | Filtros Timeframe/Estrelas; proto estático | P3 |
| 8 | Estética / densidade | Clip Operar desktop; busca truncada 390 | P3 incumbente |
| 9 | Recuperação | Sem empty/error dedicado no clone (fixtures 1+1) | P3 |
| 10 | Ajuda | Extra `/help` separado; index sem fundir guia | — |

## 7. Findings (toda finding classificada)

### P0 — nenhum

Clone `/monitor` com landmarks do catálogo (`table.signals` ×2 + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia). Copied 21854 > 0. Sem painel ANTES/DEPOIS nem grelha das N como URL canónica. Chrome 224px e `--bg-*` não foram tratados como prova suficiente. Login da rota viva **não** foi usado como PASS. HTTP 200 sozinho não sustentaria o veredito. Snapshots Playwright não vazios. Detector sem crítico. Landmark em falta **não** observado. Zero menção visível a scalper/scalp no index e nos extras. Extras de copy não fundidos no index. Delta = módulo ausente na topologia.

### P1 — nenhum

Delta de produto visível no sítio certo: o módulo scalper não está entre o page-sub e os KPIs; a board e o Operar continuam. Sem furo de escopo (landing/Ajuda/Perfil/Credenciais são URLs irmãs, não o canónico). Sem anúncio de saída.

### P2 — nenhum

Densidade, clip Operar e truncagem da busca são polish do clone incumbente; **não** furo de produto/escopo/contrato visível. Não reabre como P0/P1.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 `DELTA:start`=0** no index: o delta é ausência do módulo (não região marcada). Copied 7/7 > 0; classify PASS.
- **P3-2 Tabela `0×0` no 390** com cards SOLUSDT/ETHUSDT — clone vivo. Landmarks via thead no DOM + cards + Operar.
- **P3-3 Clip / empilhamento da coluna Operar** (Ver Trades sobre Operar) no desktop — incumbente; non-goal: não redesenhar o Monitor.
- **P3-4 Truncagem da busca a 390** («Buscar par, est») — incumbente.
- **P3-5 Extra `landing.html` 404 `./posthog-config.js`** — o clone v4 aponta para o sibling; a pasta do card não o copia. Copy/FAQ/CTA medidos no HTML. Detalhe de proto/Apply, não contrato do Monitor.
- **P3-6 Title da Ajuda** ainda `Como usar o Cripto Farol — protótipo card-718` — chrome de extra, não produto do index.
- **P3-7 Overlay `detect.js` não injectado**; evidência = CLI `[]` + Playwright. IDE browser sem tab.
- **P3-8 GET `/monitor` 455 B / redirect `/login`** — sem sessão. Não é defeito do proto. Não usado como PASS.
- **P3-9 Landing viva ainda menciona scalp** (4 hits visíveis). Esperado até Apply; o extra do card já está a 0. Não é P0 do proto.

Observações (não-findings): `hasLogin=true` em credenciais/landing extra é falso positivo do regex EMAIL/SENHA (formulário de API / qualificação), não chrome de `/login`. «se saiu antes» ≠ descontinuação. Index isolado **não** pede posthog (confirmação: só logo+mark 200). `playwright-cli-headed` ausente; fallback Playwright Python + Chromium 1243.

## 8. Veredito

**PASS** — zero P0/P1/P2 abertos; detector `[]`; digest disco == HTTPS == esperado `9f5dcb0c48f0de71ffdf02ce92a781bb720f1e1a01eeabc6e205025b6aab71f3`; clone+delta (módulo scalper ausente; não ANTES/DEPOIS, não grelha das N); extras de copy separados e sem scalp visível; `/login` vivo não usado como prova; matriz visível desktop+mobile no index e na landing extra. HTTP 200 sozinho não sustentaria este veredito. Snapshots Playwright não vazios.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 9. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-1075-remover-scalper/
- Disco: `frontend/public/prototypes/card-1075-remover-scalper/index.html`
- Digest: `9f5dcb0c48f0de71ffdf02ce92a781bb720f1e1a01eeabc6e205025b6aab71f3` · 31551 B
- Extras: `landing.html` · `ajuda.html` · `perfil.html` · `credenciais.html`
- Landing viva: https://criptofarol.com.br/
- Live (não-prova): https://dev.criptofarol.com.br/monitor → `/login`
- Viewports: 1440×900 · 390×844
- HTTP proto: **200**
- Digest bate: **sim** (disco == HTTPS == esperado)
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]` exit 0
- Clone gate: `classify(..., '/monitor')` = PASS · `clone_gate_ok` = True
- Modelo: Grok 4.6 · `cursor-grok-4.6-high`
- Slug Impeccable: `ic-prototypes-card-1075-remover-scalper-index-html`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
