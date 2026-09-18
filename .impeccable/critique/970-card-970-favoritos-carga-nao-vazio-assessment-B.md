# Assessment B (detector + browser real) — card 970 · change card-970-favoritos-carga-nao-vazio

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `970-B-*`, `970-B-gate.py` e `970-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /favorites` · `surface: existing`.

```
Assessment B 970
digest_match: yes
detector: 2 findings side-tab (index) + 2 (erro) + 2 (filtro); monitor [] — todos P3 incumbente
P0: nenhum
P1: nenhum
P3: side-tab ×2 cards mobile de tier; truncagem Estratégia; header Todas N no erro; thead/clip 390; alvos retry; clip monitor 390
verdict: PASS
```

- UTC: 2026-09-18T13:17Z
- Tuple (read-only): `bound_card=970` · `q_git=card-970-favoritos-carga-nao-vazio`. Sem `process_event`. Sem `move_agent_to_root`.
- Status GraphQL pontual (`repository.issue(number:970).projectItems`): **Design** · item `PVTI_lAHOAAHtBM4BV8b2zg7g_Uo` · Project 1 `oalansilva`. Issue OPEN *«PROD: Favoritos fica em Carregando e depois diz que não há estratégias»*.
- Protótipo canónico: `frontend/public/prototypes/card-970-favoritos-carga-nao-vazio/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/
- Irmãos (não canónicos): `erro.html` · `filtro.html`. Extra: `monitor.html`. Sem extra `/home` (`home.html` / `inicio.html` disco ausente; HTTPS 404).
- Digest index esperado: `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0` · 43492 B. Disco MUST == HTTPS: **IDENTICAL**.
- Rota viva `https://dev.criptofarol.com.br/favorites` → browser **`/login`** («Bem-vindo de volta»). Login **não** é a rota; **não** autoriza PASS de clone. Clone avaliado no proto HTTPS.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports **1440×900** e **390×844**. `colorScheme: dark`. URL canónica do proto (não `file://`). Critério igual nos dois viewports (autor usou 1280×800; 1440 cobre o mesmo contrato).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` nos quatro HTML versionados (cwd worktree). Overlay `detect.js` não injectado.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0` | 43492 |
| HTTPS GET `/prototypes/card-970-favoritos-carga-nao-vazio/` | idem | 43492 HTTP 200 · `cmp` **IDENTICAL** |
| HTTPS GET `…/index.html` | idem | 43492 · **IDENTICAL** |
| Disco `erro.html` | `0372478935f5b4a6777893657886b4eda330ef735b92f7a72eee08f31e9763f5` | 33545 · HTTPS **IDENTICAL** |
| Disco `filtro.html` | `b7e21be008c44e254c204f4d9796b801ac3fbdb740b9107cc04c9078c9dcfbaf` | 32991 · HTTPS **IDENTICAL** |
| Disco `monitor.html` | `f231f93e3c0493bffc305c1bf757cd1d7d6eecc25bbaec2e257a398396c96ee3` | 15953 · HTTPS **IDENTICAL** |

HTTP 200 isolado **não** é o gate. Digest não mudou → evidência do autor válida.

## 2. Detector Impeccable

- `index.html` exit 2 → 2 findings `side-tab` (L145 `.fav-up` / L146 `.turquoise` `border-left:3px`).
- `erro.html` / `filtro.html` exit 2 → os mesmos 2 `side-tab` no clone dos cards de tier.
- `monitor.html` → `[]`, exit 0.
- **Classificação:** P3 incumbente do clone `/favorites` (já no `design.md`: «Detector `side-tab` ×2 nos cards mobile de tier»). Slop de CSS de tier, não contrato de carga. **Não** reabre como P0/P1. Sem finding crítico.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /favorites` · `surface: existing`. **Não** é rota de catálogo emprestada (`/monitor` não é `live_route`; extra `monitor.html` declarado). Sem extra `/home`.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/favorites`: `selectors: ["table.fav-strategies"]`, `texts: ["Estratégias favoritas", "Symbol", "Estratégia", "Ações"]`.
- Index no browser (1440 e 390): `table.fav-strategies`=1; h1 «Estratégias favoritas»; thead `textContent` **Symbol** / **Estratégia** / **Ações** (innerText uppercase no 1440 — landmark presente). Filtro visível `Symbol`.
- Pares `COPIED:start`/`COPIED:end` = **4/4**; soma UTF-8 copiada **7769** (> 0); total 43492 = 7769 copied + 35723 generated. `DELTA:start`=0 no index — delta nas células da grade, não região nova / painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Substring `ANTES`/`DEPOIS` só em comentário HTML «Sem ANTES/DEPOIS» — innerText do body **não** as mostra. URL canónica = `index.html`.
- Caminho feliz visível: linhas **SOL/USDT** e **ETH/USDT**; footer **«2 estratégias carregadas»**; **ausente** «Nenhuma estratégia favorita encontrada»; **ausente** «0 estratégias carregadas».

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning relevante = 0; pageerror = 0; responses ≥400 no proto = 0. Overflow documento `scrollWidth<=clientWidth+1` no index. Gate bruto: `.impeccable/critique/970-B-gate.json`.

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /favorites` / `surface: existing` | PASS | — |
| 3 | Landmarks `/favorites`: `table.fav-strategies` + «Estratégias favoritas» + Symbol + Estratégia + Ações | PASS | PASS (cards + filtro; thead clip incumbente) |
| 4 | COPIED 4/4 · 7769 > 0; 0 botões Antes/Depois; sem painel das N | PASS | PASS |
| 5 | Feliz: SOL/USDT + ETH/USDT; **ausente** catálogo vazio; **ausente** «0 estratégias carregadas»; footer «2 estratégias carregadas» | PASS | PASS |
| 6 | `erro.html`: «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»; chrome Favoritos; **não** catálogo vazio; URL proto (não `/login`) | PASS | PASS |
| 7 | `filtro.html`: busca `ZZZ`; «Não há resultado com estes filtros.»; **ausente** catálogo vazio | PASS | PASS |
| 8 | `monitor.html`: «Não foi possível carregar as estratégias.»; **ausente** «Nenhum ativo disponível no monitor» (visível); `table.signals` | PASS | PASS (copy no DOM; clip visual P3) |
| 9 | Sem extra `/home`; 0 console / 0 pageerror | PASS | PASS |
| 10 | Detector sem finding crítico | PASS | — |

Pixels index desktop: pares SOL/USDT e ETH/USDT na grade; «2 estratégias carregadas»; colunas SYMBOL / ESTRATÉGIA / AÇÕES; sem empty. Sem botões Antes/Depois.

Pixels index mobile: cards SOLUSDT / ETHUSDT; «2 estratégias carregadas»; sem empty.

Pixels erro: copy de falha + «Tentar de novo»; chip «CARGA FALHOU»; footer «Carga falhou»; sem «Nenhuma estratégia favorita encontrada».

Pixels filtro: busca `ZZZ`; «Não há resultado com estes filtros.»; footer «0 filtradas».

Pixels monitor: «Não foi possível carregar as estratégias.» + «Tentar de novo»; **não** «Nenhum ativo disponível no monitor». 390 recorta thead/CTA (P3).

Rota viva **não usada como prova de clone** (caiu em `/login`).

## 5. Findings (toda finding classificada)

### P0 — nenhum

Clone `/favorites` com landmarks do catálogo; copied 7769 > 0; sem painel ANTES/DEPOIS; feliz com pares crypto e footer 2; irmãos erro/filtro com copy de contrato; extra monitor sem empty «Nenhum ativo…» visível; digest HTTPS == disco == esperado; detector sem crítico. Fidelidade + contrato visível ok → **não BLOCKED**.

### P1 — nenhum

Quatro estados visíveis em URLs distintas (index feliz / erro / filtro / monitor). Empty de catálogo **não** ocupa o feliz nem o erro nem o filtro. Retry permanece no proto. Login da rota viva não foi usado como PASS.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 `side-tab` ×2** nos cards mobile de tier (detector L145–146 index; irmãos iguais). Já no `design.md`.
- **P3-2 Truncagem desktop** do nome na coluna Estratégia (`Mé…` / `Salv…`). Já no Apply contract.
- **P3-3 Contadores do header (Todas 2 / Acompanhar 1 / Top picks 1) no estado de erro.** Já P3 no `design.md`.
- **P3-4 Thead clip / card-stack no 390** do clone `/favorites`. Landmarks via filtro + cards; clone vivo.
- **P3-5 Alvos do «Tentar de novo»** (44px pedido no Apply). Fora do delta de copy.
- **P3-6 Clip 390 em `monitor.html`:** thead larga + CTA «Tentar de novo» parcialmente fora da viewport. Copy completa está no DOM (`innerText` passou). Non-goal: não redesenhar Monitor. Incumbente `table.signals`.
- **P3-7 Needle «Nenhum ativo disponível no monitor» só em comentário HTML** do extra (não visível). Contrato visível cumprido.
- **P3-8 Testids / nomes internos `isError`.** Já P3 de Apply.

Observações (não-findings): overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/favorites` autenticado não usado. Nav Monitor no shell do index = clone `/favorites`, extra `/monitor` é `monitor.html`. `DELTA:start`=0 no index porque o delta é linha/footer, não região marcada.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `side-tab` classificado P3; digest idêntico nas 4 pontas e igual ao esperado; clone+delta (não ANTES/DEPOIS); `/login` vivo não usado como prova; matriz visível desktop+mobile no index e irmãos. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/
- Digest index: `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0` · 43492 B
- Snapshot: `.impeccable/critique/970-card-970-favoritos-carga-nao-vazio-assessment-B.md`
- Gate bruto: `.impeccable/critique/970-B-gate.json`
- PNGs: `970-B-desktop-1440x900-index.png`, `970-B-desktop-1440x900-erro.png`, `970-B-desktop-1440x900-filtro.png`, `970-B-desktop-1440x900-monitor.png`, `970-B-mobile-390x844-index.png`, `970-B-mobile-390x844-erro.png`, `970-B-mobile-390x844-filtro.png`, `970-B-mobile-390x844-monitor.png`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
