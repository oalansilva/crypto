# Assessment B (detector + browser real) — card 1078 · change card-1078-opcoes-periodo

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Único ficheiro escrito neste filho: este snapshot (shots de trabalho em `/tmp/1078-B-shots/`, não versionados).
> Modelo declarado: rótulo **Grok 4.6**, slug **`cursor-grok-4.6-high`**.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 1078
model: Grok 4.6 (cursor-grok-4.6-high)
digest_match: disk==expected==HTTP local IDENTICAL; HTTPS DEV 404 (não usado como prova)
detector: [] index exit 0; [] combo exit 0
P0: nenhum
P1: nenhum
P2: nenhum
P3: HTTPS 404 até publicar; hint Combo custom vazio cai em «todo o histórico»; date input mm/dd/yyyy do Chromium; período abaixo da 1ª dobra; Acompanhar «todo o histórico»+Short; clip Ação; copy «sem campo para alterar»; overlay detect.js não injectado
verdict: PASS
```

- UTC: 2026-10-05T01:52Z
- Tuple (read-only): `bound_card=1078` · `q_git=card-1078-opcoes-periodo` · Status=Design (bind do prompt; issue OPEN). Sem `process_event`. Sem `move_agent_to_root`. Sem arraste de Status.
- REST `gh api repos/oalansilva/crypto/issues/1078`: OPEN *«crie mais opções de peridos»*. Body grelhado: mesma lista nas duas telas; Descoberta abre em 15 dias; Combo marca inicial em aberto; Personalizado valida datas; janela curta não bloqueia.
- Protótipo canónico: `frontend/public/prototypes/card-1078-opcoes-periodo/index.html`.
- Extra (não canónico): `combo.html` — clone `/combo/configure`.
- Servido DEV: https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/ → HTTP **404** título `Protótipo não encontrado` (source DEV / worktrees publicados ainda sem este `index.html`). **Registado.** Evidência do browser = HTTP local do disco, não `file://`, não o 404.
- HTTP local: `http://127.0.0.1:18781/prototypes/card-1078-opcoes-periodo/` (cwd `frontend/public`).
- Digest index esperado (prompt / `design.md`): `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` · 61431 B. Disco == HTTP local == esperado: **IDENTICAL**.
- Digest combo esperado: `c7328b35ac09763e4ebac63f3628792030d00378e2c12403a31c172e004511b8` · 19187 B. Disco == HTTP local == esperado: **IDENTICAL**.
- Rota viva `https://dev.criptofarol.com.br/combo/discovery` → browser **`/login`** («Bem-vindo de volta» · EMAIL · SENHA · Entrar). Login **não** é a rota; **não** autoriza PASS de clone. Clone avaliado no proto local (digest idêntico ao disco) + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`, `executable_path` do cache host. IDE browser do host **sem tab** (lista vazia). Viewports **1440×900** e **390×844**. `colorScheme: dark`. Screenshots de trabalho em `/tmp/1078-B-shots/` (não versionados). Snapshots **não** vazios (index desktop montar 138551 B · mobile period 49890 B; combo desktop 93141 B · mobile period 54680 B) → **não BLOCKED**.
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no `index.html` e no `combo.html` (cwd worktree). Overlay `detect.js` não injectado.
- `design_clone_gate.classify(html, '/combo/discovery')` = **PASS**.

## 1. Digest servido == local

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| Disco `index.html` | `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` | 61431 | — |
| Esperado (prompt / `design.md`) | idem | 61431 · **IDENTICAL** | — |
| HTTP local GET `…/card-1078-opcoes-periodo/` | idem | 61431 HTTP **200** · **IDENTICAL** | |
| Browser (Playwright carregou o HTTP local) | o mesmo documento | 61431 | 200 |
| Disco/HTTP local `combo.html` | `c7328b35ac09763e4ebac63f3628792030d00378e2c12403a31c172e004511b8` | 19187 HTTP **200** · **IDENTICAL** | |
| HTTPS GET `/prototypes/card-1078-opcoes-periodo/` | *não é o proto* | 604 | **404** «Protótipo não encontrado» |
| HTTPS GET `…/index.html` | *não é o proto* | 614 | **404** |
| HTTPS GET `…/combo.html` | *não é o proto* | 614 | **404** |

`cmp` disco vs HTTP local (index e combo): **IDENTICAL**. Disco vs HTTPS: **DIFFER** (DEV ainda não publica este worktree). HTTP 200 isolado **não** é o gate. Digest que o browser viu **bate com o disco**.

## 2. Detector Impeccable

- Alvo canónico: `frontend/public/prototypes/card-1078-opcoes-periodo/index.html`
- CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, **exit 0**.
- Extra: mesmo comando em `combo.html` → `[]`, **exit 0**.
- Ignore list: `.impeccable/critique/ignore.md` **ausente**.
- Overlay live `detect.js`: **não injectado** (CLI + Playwright; IDE browser sem tab; sem live-server Impeccable deste filho).
- **Classificação:** detector verde. Nada a reabrir como P0/P1.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias (antes de Context): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`. **Não** é rota de catálogo emprestada. **PASS** deste item da rubrica — não reabrir parser.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Index no browser (1440 e 390): h1 `Descoberta de estratégias swing`; `Preflight` visível (desktop na 1ª dobra; mobile após scroll); `Rascunho de varredura` visível. Landmarks 3/3.
- Pares `COPIED:start`/`COPIED:end` index = **15/15**; soma UTF-8 copiada **27836** (> 0); total 61431; generated 33595. Bate com `design.md`. `DELTA:start`/`DELTA:end` = **6/6** (período, Preflight da janela, evidência Decidir).
- Extra `combo.html`: COPIED **4/4**; soma UTF-8 **4885** (> 0); DELTA 2 (lista de período + janela/Preflight Combo). URL extra, nunca canónica.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0** nos dois viewports e nas duas páginas. `innerText` do body **não** contém ANTES/DEPOIS (único hit no comentário HTML). URL canónica = `index.html` clone+delta, default Montar `aria-selected=true`. **Sem grelha «N estados ⇒ N cards».** Extra Combo não fundido no index.
- Chrome 224px no desktop (`offsetWidth=224`); **sozinho não passa** — listing + Preflight + rascunho visíveis. Mobile sidebar `display:none` (0px); chrome via mobilebar.
- `lang=pt-BR`. `meta color-scheme=dark`. Título visível: «Descoberta de estratégias swing». Login chrome **ausente** no proto.
- Ranking Calmar vs CAGR **intacto** no rascunho. Direção Descoberta: só Long no Montar (sem controlo Short). Combo extra mantém Direction Long/Short do incumbente `/combo/configure` — não é furo de Descoberta.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844, colorScheme dark)

Console error do **index/combo isolados** = 0 pageerror; responses ≥400 no prefixo proto local = 0. Os 2 `Failed to load resource 404` no saco 1440 vieram das navegações HTTPS 404 / live `/login`, não do proto. Overflow documento `scrollWidth==clientWidth` (1440/1440 e 390/390). `curl`/HTTP 200 não substitui.

Fluxo exercido: vista canónica HTTP local nos dois viewports; extra Combo no mesmo prefixo; Personalizado (vazio, só inicial, só final, inicial>final, final>hoje, válido); 15d e 1m com Iniciar enabled; Decidir com selo; live `/combo/discovery` sem sessão → `/login` (não usada como prova); HTTPS proto 404. Este filho MUST NOT autenticar Playwright na viva.

Lista visível (select `#sel-period`, ordem exacta) nas duas páginas: `15 dias`, `1 mês`, `3 meses`, `6 meses`, `1 ano`, `2 anos`, `Personalizado`, `Todo o histórico`. Zero «Últimos N» / «Todo o período».

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == HTTP local == esperado (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing` | PASS | — |
| 3 | Landmarks `/combo/discovery`: h1 + Preflight + Rascunho | PASS (Preflight na 1ª dobra) | PASS (Preflight após scroll) |
| 4 | Chrome 224px **não** é a prova sozinha | PASS (sidebar 224 + rascunho + Preflight) | PASS (sidebar 0; listing via page) |
| 5 | COPIED 15/15 · 27836 > 0; 0 botões Antes/Depois; sem painel das N | PASS | PASS |
| 6 | Mesma lista de 8 opções, mesma ordem, nas duas páginas | PASS | PASS |
| 7 | Descoberta abre em 15 dias; Preflight/rascunho com rótulo + janela `[20 set. 2026, 05 out. 2026)` | PASS | PASS |
| 8 | Combo abre em incumbente `Todo o histórico`; sem banner de default novo | PASS | PASS |
| 9 | 15d e 1m: Iniciar **enabled**; impedimentos hidden | PASS | PASS |
| 10 | Personalizado revela Data Inicial + Data Final; vazio bloqueia com «Seleccione Data Inicial e Data Final.» | PASS | PASS |
| 11 | Só inicial → «Seleccione Data Final.»; só final → «Seleccione Data Inicial.» | PASS | PASS |
| 12 | Inicial depois da final bloqueia; final depois de hoje bloqueia | PASS | PASS |
| 13 | Personalizado válido: Iniciar enabled; Preflight mostra janela | PASS | PASS |
| 14 | Decidir: selo `Amostra insuficiente` (janela 15 dias); Promover dessa linha disabled | PASS | PASS |
| 15 | Live `/combo/discovery` sem sessão → `/login`; login **não** usado como PASS | PASS | PASS |
| 16 | Detector `[]`; proto local 0 pageerror / 0 ≥400 | PASS | PASS |

Pixels desktop Montar: shell autenticado (sidebar Descoberta 224px); h1 Descoberta de estratégias swing; 3 modos Montar seleccionado; rascunho Templates/Símbolos/TF 1 dia + Long; **Período histórico = 15 dias**; Ranking Calmar; Preflight `1 combinação · ~2 min estimado · 15 dias [20 set. 2026, 05 out. 2026)`; CTA Iniciar amarelo enabled. Sem «Bem-vindo de volta». Sem ANTES/DEPOIS.

Pixels desktop Personalizado vazio: select Personalizado; Data Inicial + Data Final visíveis (`type=date`); Preflight «Bloqueado — veja o que falta» + «Seleccione Data Inicial e Data Final.»; CTA disabled.

Pixels desktop Decidir: Leaderboard Calmar · janela UTC 15 dias; linha `RS-1078-15D` selo **Amostra insuficiente** · BTC/USDT · 1d · Long · métricas N/A · botão Ação disabled. GO/NO-GO das outras linhas intactos.

Pixels mobile Montar (após scroll): Período histórico 15 dias; Preflight 15 dias + janela; Iniciar enabled. Personalizado: as duas datas + Preflight bloqueado. Decidir card: selo Amostra insuficiente + CTA disabled.

Pixels Combo desktop/mobile: Template Information + Configuration; Período **Todo o histórico** (incumbente, sem copy de decisão); lista nova no select; Personalizado revela datas e bloqueia; Iniciar Combo enabled no default `all`. Direction Long/Short = clone configure.

Pixels live Discovery (ambos): card de login. **Não confrontado com o proto.**

Pixels HTTPS proto: `Protótipo não encontrado`. **Não** é evidência do HTML deste card.

## 5. Confronta Entra (só o visível no proto; backend/API = Apply)

| Entra visível | Proto (browser) | Disposition |
|---|---|---|
| Mesma lista nas duas telas, nesta ordem | 8 opções idênticas index + combo | PASS |
| Descoberta abre em 15 dias; Preflight/rascunho com rótulo + janela | selected `15d`; linha 3 + pf-period com `[20 set. 2026, 05 out. 2026)` | PASS |
| Combo: lista nova; marca ao abrir = incumbente `all`; não apresentada como decisão | selected `Todo o histórico`; 0 banner «default novo»; hint «todo o histórico disponível» | PASS |
| Personalizado pede as duas datas; inválido bloqueia e nomeia o que falta | copy da decisão 6 nos 5 caminhos; CTA disabled | PASS |
| Janela curta (15d / 1m + 1d) deixa iniciar; selo Amostra insuficiente nas linhas curtas | Iniciar enabled; Decidir selo + Promover disabled | PASS |
| Ranking / Short Descoberta / Monitor / Favoritos fora | Calmar intacto; Montar só Long; index ≠ Monitor/Favoritos | PASS |
| `period_type` worker / `resolve_optimizer_date_range` | Não são tela | P3 Apply |

## 6. Nielsen (observado no browser; sem ensaio de personas)

Assessment B não pontua design-director (isso é A). Heurísticas só como evidência visível:

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Preflight muda para Bloqueado; linha 3 + pf-period seguem o select | — |
| 2 | Match com o mundo | 15 dias / 1 mês / Personalizado / Todo o histórico | — |
| 3 | Controlo do utilizador | Select + datas + Iniciar; modos Montar/Acompanhar/Decidir | — |
| 4 | Consistência | Lista partilhada nas duas telas; Combo não herda 15d | — |
| 5 | Prevenção de erro | Datas inválidas bloqueiam CTA; copy nomeia o furo | — |
| 6 | Reconhecimento | Opções visíveis no select; datas inline (sem modal) | — |
| 7 | Flexibilidade | 8 janelas + custom; proto estático | P3 |
| 8 | Estética / densidade | Período abaixo da 1ª dobra; clip Ação desktop | P3 incumbente |
| 9 | Recuperação | Impedimentos inline; valid custom reabilita | — |
| 10 | Ajuda | Copy «Falta fazer»; custo «sem campo para alterar» é meta de mock | P3 |

## 7. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto; digest disco == HTTP local == browser == esperado; HTTPS 404 registado e **não** usado como prova; sem painel ANTES/DEPOIS; 15 pares COPIED com bytes > 0; lista idêntica nas duas páginas; Descoberta default 15 dias visível; Combo default incumbente `Todo o histórico` **não** apresentado como decisão deste card; Personalizado bloqueia os quatro inválidos e aceita o válido; 15d/1m não bloqueiam início; selo Amostra insuficiente no Decidir; detector `[]`. `/login` não conta como clone. HTTP 200 sozinho não sustentaria o veredito. Snapshots Playwright não vazios.

### P1 — nenhum

Delta observável nos dois viewports (select + Preflight + datas após scroll no 390). Selo tem texto `Amostra insuficiente` (não só cor). Combo não marca 15 dias como default novo.

### P2 — nenhum

Hint Combo em Personalizado vazio ainda diz «todo o histórico disponível» (fallback `HINTS.all`) **enquanto** o Preflight já nomeia as datas em falta e o CTA está disabled. Copy conflitante, mas o contrato de bloqueio está visível. Polish, não furo de produto — **P3**, não P1/P2.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 HTTPS DEV 404** até o pai publicar o proto. Disco == HTTP local == esperado. Não invalida o clone.
- **P3-2 Hint Combo em Personalizado sem datas** cai em «Será usado todo o histórico…» (`HINTS.all`). Impedimento e CTA disabled estão correctos. Apply: hint próprio para custom incompleto.
- **P3-3 `type=date` mostra `mm/dd/yyyy`** no Chromium en-US desta VM. Labels em PT. Locale do picker = motor, não copy do card.
- **P3-4 Campo Período abaixo da 1ª dobra** (1440 e 390). Preflight desktop já mostra 15 dias na dobra; mobile precisa de scroll. Layout incumbente do Montar condensado.
- **P3-5 Acompanhar rascunho congelado** ainda «Long + Short · todo o histórico» (chrome copiado). Delta deste card está no Montar/Decidir; bag «3 amostra insuficiente» testemunha janela curta.
- **P3-6 Coluna Ação recortada no desktop** (`Amostra in` / `Promover`). Nit do clone da grelha; o selo e o disabled passaram no DOM.
- **P3-7 Copy proto no Preflight** «sem campo para alterar» — meta do mock de custo; Apply usa o rótulo operacional.
- **P3-8 Overlay `detect.js` não injectado**; evidência = CLI `[]` + Playwright. IDE browser sem tab.
- **P3-9 Chrome `#0d7990ca` / snapshot 492 / `#PF-492` / `7 de 8`** mock.
- **P3-10 Direction Short no Combo** = clone `/combo/configure`. Não entra na Descoberta.
- **P3-11 Chaves internas `15d`/`1m`/…/`custom`/`all`** e `resolve_optimizer_date_range` — detalhe de Apply (já no `design.md`).

Observações (não-findings): `/login` não conta como clone. HTTPS 404 não invalida o proto do disco. Combo `Todo o histórico` seleccionado **é** o incumbente, não uma marca nova decidida. Ranking Calmar intacto. `playwright-cli-headed` / tab IDE ausentes; fallback Playwright Python + Chromium 1243.

## 8. Veredito

**PASS** — zero P0/P1/P2 abertos; detector `[]`; digest disco == HTTP local == esperado `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` (index) e `c7328b35ac09763e4ebac63f3628792030d00378e2c12403a31c172e004511b8` (combo); clone+delta (não ANTES/DEPOIS, não grelha das N); `/login` vivo não usado como prova; matriz visível desktop+mobile no index e no extra Combo; contrato visível (lista partilhada, Descoberta 15 dias, Personalizado bloqueia inválido, janela curta inicia, Combo sem default novo) exercido no browser. HTTP 200 sozinho não sustentaria este veredito. Snapshots Playwright não vazios. HTTPS DEV ainda sem este proto (registado).

Disposition: crítico não pede rework. P3 aceites no Apply.

## 9. Referências

- Proto URL canónica (ainda 404 no DEV): https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/
- Extra Combo: https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/combo.html
- Disco: `frontend/public/prototypes/card-1078-opcoes-periodo/index.html` · `combo.html`
- HTTP local (evidência): `http://127.0.0.1:18781/prototypes/card-1078-opcoes-periodo/`
- Digest index: `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` · 61431 B
- Digest combo: `c7328b35ac09763e4ebac63f3628792030d00378e2c12403a31c172e004511b8` · 19187 B
- Live (não-prova): https://dev.criptofarol.com.br/combo/discovery → `/login`
- Viewports: 1440×900 · 390×844 · `colorScheme: dark`
- HTTP proto local: **200** · digest bate: **sim** (disco == local == esperado)
- HTTPS proto: **404**
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]` exit 0 (index e combo)
- Clone gate: `classify(..., '/combo/discovery')` = PASS
- Shots: `/tmp/1078-B-shots/` (não versionados)
- Modelo: Grok 4.6 · `cursor-grok-4.6-high`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
