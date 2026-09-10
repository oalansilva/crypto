# Assessment B (detector + browser real) — card 876 · change card-876-discovery-amostra-insuficiente

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste arquivo.
> Tokens parseáveis do `design.md`: `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

- UTC: 2026-09-09T0005Z
- Protótipo: `frontend/public/prototypes/card-876-discovery-amostra-insuficiente/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-876-discovery-amostra-insuficiente/
- Digest esperado: `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722`
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **sem sessão**; Playwright aterrissou em `/login` (`Bem-vindo de volta` / campo senha). `/login` **não** conta como a rota; clone avaliado pelo proto + landmarks do catálogo + fonte `DiscoveryPage.tsx`.
- Browser: Chromium 1243 (`chrome-linux-arm64`), Playwright Python, `--no-sandbox`; desktop 1440×900 + mobile 390×844.
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado. Motor URL/puppeteer indisponível (`npm install puppeteer` em falta); bytes HTML idênticos ao servido, scan estático cobre as regras do ficheiro.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722` | 33203 |
| HTTPS GET proto | `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722` | 33203 HTTP 200 |
| Esperado (prompt / design.md) | `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722` | — |

`cmp` disco vs `/tmp/card876-proto.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate; o gate é a matriz abaixo.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-876-discovery-amostra-insuficiente/index.html`
- Com `--no-advisory` e sem: saída `[]`, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.
- Motor browser/`detectUrl`: recusou (`puppeteer is required`). Não inventei finding. Evidência visual veio do Playwright (asserts + PNGs).

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Fonte viva `DiscoveryPage.tsx`: h1 `Descoberta de estratégias swing` (L1317), h2 `Rascunho de varredura` (L1759), aside `aria-label="Preflight da varredura"` + h2 `Preflight` (L1916/1919). `Baixa amostra` posto-grid permanece na fonte (L2291/2359) — o proto conserva o vizinho.
- Proto `index.html`: **8 pares** `COPIED:start` / `COPIED:end` (shell, heading, modos, rascunho, preflight, chrome Acompanhar, header leaderboard, nota rank-stable). Não é galeria de 6 estados: 3 `modepanel` (Montar / Acompanhar / Decidir), 4 linhas no Decidir (2 elegíveis + `Baixa amostra` + delta).
- Toggle Antes/Depois: **ausente**. `aria-pressed` = 0; botões «Antes»/«Depois» = 0; painel ANTES/DEPOIS no body = false. Comentário HTML: `No ANTES/DEPOIS panel`. Tabs `role=tab` **mudam markup** (`.modepanel.active` único; Acompanhar default → Montar revela Preflight/Rascunho; Decidir revela a linha). Não há P0 de `aria-pressed` sem mudança.
- URL canónico = `index.html` clone+delta, não painel ANTES/DEPOIS.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

15/15 PASS em cada viewport. Console error = 0; pageerror = 0; responses ≥400 = 0 (logo `/brand/cripto-farol-logo-v6-transparent.svg` = 200). PNGs em `/tmp/card876-B/{d1440,m390}-{montar,acomp,decidir}.png`.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | HTTP 200 no proto (não basta sozinho) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` | PASS | PASS |
| 3 | Landmark `Preflight` visível após tab Montar | PASS | PASS |
| 4 | Landmark `Rascunho de varredura` visível após tab Montar | PASS | PASS |
| 5 | Default = Acompanhar; `counter-invariant` visível | PASS | PASS |
| 6 | Quarto termo: `18 processadas = 12 sucesso + 1 falha + 1 ignoradas + 4 amostra insuficiente` | PASS | PASS |
| 7 | Decidir `data-testid=row-insufficient` visível | PASS | PASS |
| 8 | Selo `Amostra insuficiente` (não `Baixa amostra`) | PASS | PASS |
| 9 | Rank `—` | PASS | PASS |
| 10 | Calmar / Max DD / Trades/cobertura = `N/A` ×3 | PASS | PASS |
| 11 | **0** controlo Promover na linha (`button.promote` = 0; único botão = `Excluir`) | PASS | PASS |
| 12 | Excluir presente na linha | PASS | PASS |
| 13 | Parciais top-5 **sem** selo `Amostra insuficiente` | PASS | PASS |
| 14 | 0 console error / 0 pageerror | PASS | PASS |
| 15 | Sem toggle Antes/Depois; 3 painéis de modo, não grelha de 6 estados | PASS | PASS |

Vizinho clone intacto (não-delta): 1 selo `Baixa amostra` + botão desabilitado rotulado `Baixa amostra` (não é Promover na linha insuficiente).

Rota viva sem sessão: `final_url=/login`, h1 da Descoberta = 0. **Não usada como evidência de clone.**

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto (e na fonte viva); digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; clone = pares COPIED + 3 modos, não galeria; linha delta sem Promover.

### P1 — nenhum

HTML bem formado (0 unclosed/stray). Delta observável nos dois viewports. Detector `[]`.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Overflow horizontal ~4 px em 390×844** (`scrollWidth` 394). Fonte: `thead`/`th` da tabela de parciais (clone Acompanhar), não a linha `row-insufficient`. Cards do Decidir em `@media ≤720px` cabem. Detalhe de Apply / paridade da tabela viva.
- **P3-2 Jargão no chrome copiado do Acompanhar** (`Sweep ativo · #c876a01e`, `snapshot #PF-876-24`). Fora do delta deste card (fórmula + linha Decidir). Chip `EM CURSO` em PT. Aceite como clone; Apply não precisa copiar o id fictício `#PF-876-24`.
- **P3-3 Leaderboard diz `16 de 16 candidatos` com 4 `<tr>` visíveis.** Condensação de protótipo, não grelha de estados. Apply liga à paginação real.

Observações (não-findings): `N/A` com `.na` muted — distinto do selo amber; Excluir na linha insuficiente cumpre «excluir permanece»; motor URL do detector sem puppeteer — gap de tooling, não finding de UI.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]` classificado; browser gate 15/15 ×2 viewports; digest idêntico; clone+delta (não ANTES/DEPOIS, não 6 estados); `/login` não usado como prova. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-876-discovery-amostra-insuficiente/
- Digest: `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722`
- Snapshot: `.impeccable/critique/876-card-876-discovery-amostra-insuficiente-assessment-B-2026-09-09T0005Z.md`
- Gate bruto: `/tmp/card876-B/gate.json`
