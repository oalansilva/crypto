# Assessment B (detector + browser real) — card 1119 · change card-1119-backtest-acoes-etfs

> Assessor B isolado, sem transcript de A nem do pai (o snapshot A existe na pasta e **não** foi lido). Sem nested-spawn. Cliente Claude Code (adapter cooperativo, não oficial; sem modo Auto), superfície claude-desktop.
> Único arquivo escrito por este filho: este snapshot. Screenshots e JSON de trabalho em `/tmp/1119-B-shots/` (não versionados); scripts no scratchpad da sessão.
> Modelo da captura (`assessment-b-1119-a1.capture.json`, role `assessment-b`, faixa `juizo`): rótulo **Opus 5.5**, slug **`claude-opus-5-5`**, effort `high`.
> Tokens parseáveis do `design.md` (rubrica D4, sem reabrir o parser): `UI impact: affected` · `live_route: /combo/results` · `surface: existing`.

```
Assessment B 1119
snapshot: .impeccable/critique/1119-card-1119-backtest-acoes-etfs-B.md (2026-10-23T19:10Z)
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == esperado == HTTPS (curl) == corpo visto pelo browser, IDENTICAL nos 4 HTML + live.css, delta.css, delta.js; a pasta / serve o sha do index; design.md 9413cd2d… bate
detector (CLI detect.mjs --json): index [] · etf-short [] · cripto [] · delta.css [] · delta.js [] (delta limpo) · configure exit 2 (10, todos COPIED) · live.css exit 2 (39, CSS vivo)
detector (modo hook, DESIGN.md da raiz): delta.css 21 design-system-color (= os 21 do hook) · 3 HTML de resultado 3 design-system-font-size cada (AppNav COPIED) · configure 13 (COPIED) · live.css 336 (vivo)
hook delta.css (21): HERDADAS 15 (#b7bdc6 ×9, #fbbf24 ×4, #93c5fd ×2) · DEFEITO DO DELTA 6 (rgba(147,197,253,.32/.45) ×2, rgba(251,191,36,.42/.08) ×2, #474d57 ×2)
gate: design_token_gap=None · evaluate_clone_gate(HEAD)=True · landmarks_match(/combo/results, index)=True · copied_utf8_sum(index)=24741 > 0 · classify(index, /combo/results)=PASS · clone_gate_ok=True
browser: 221 asserts, 220 PASS, 1 FAIL (favicon.ico 404 na raiz do DEV, ambiente); foco: 8/8 caminhadas de Tab sem parada sem anel
P0: nenhum
P1: nenhum
P2: [juízo] motivo da seleção mista do Combo muda, contra «com o motivo de hoje» do Não entra · [juízo] lista de cripto com preço em USDT e valor/lucro em USD · [juízo] regressão cripto sem o «antes» na tela
P3: [mecânico] 6 cores inventadas no delta · [mecânico] 15 cores herdadas como literais · [mecânico] CLI sem DESIGN.md abaixo de frontend/ · [mecânico] reset `*` sem layer zera utilitários (risco de Apply) · [mecânico] PNG sem sha na tabela · [mecânico] favicon 404 · [juízo] estado «NVDA em 5m» · [mecânico] 15m/4h de ação sem texto prototipado · [mecânico] achados do incumbente clonado
verdict: PASS
```

- UTC: 2026-10-23T19:10Z
- Tupla (somente leitura): `bound_card=1119` · `q_git=card-1119-backtest-acoes-etfs` @ `5fe666fe` · Status=Design (bind do prompt). Pacote não commitado (`git status`: protótipo, change e o snapshot A como `??`). Sem `process_event`, sem mexer em Status, sem commit/push/Gist/comentário.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1119 --jq .body` (sem `gh issue view`). Body grelhado com Problema, História, Entra (8 itens, decisões de Alan de 23/10/2026), Não entra (5), Vínculo e Evidência. Sem reentrevista.
- `design.md` sha256 `9413cd2d5568e002bf5420d52c67690cfeb0caca207424e05f5295029de03ab3` (bate com o prompt, antes e depois da rodada).

## 1. Digest servido == local

| Arquivo | sha256 (disco = esperado = HTTPS curl = browser) | bytes | HTTPS |
|---|---|---|---|
| `index.html` (canônico; `/` serve o mesmo) | `8c0f34c2b622aaa82e332c2d83c86e55d2f99f31c7328275fbe1845ef54138b3` | 46106 | 200 |
| `etf-short.html` | `22053a5933ae226c29e17c276b8b25e97cccb22e235e9b0925d639ad7a8c8468` | 43899 | 200 |
| `cripto.html` | `7df8f5a93d69809106c37c9bed980e7b5d091e4873d636e55736002de12519b6` | 41297 | 200 |
| `configure.html` | `ac864821b28fa42467ab34a2db533e434d12ffbb082d8c3e1290f2107dcbd7ba` | 33722 | 200 |
| `live.css` | `7fb6d878705b10256f16443101d7502ca2e7193ced5be9950946020e7e058944` | 222723 | 200 |
| `delta.css` | `17b77fc15ed27bdece1009b375f70e300d6564f3f62309da81857c2804ae8989` | 6467 | 200 |
| `delta.js` | `8f6220155b2d9626bf4d5208b1a8383b8c80488a1c4f8f37c4aa15eb4418b493` | 7266 | 200 |

No Playwright, o hash do corpo da navegação (`response.body()`) e de um `fetch(location.href)` no contexto da página bateu nas 8 combinações tela × viewport (L0). O hash de `live.css`/`delta.css`/`delta.js` capturado nas respostas do browser também bateu (L0b). As 6 capturas `*-chart-{desk,mob}.png` respondem 200 e batem com o disco, mas **não estão** na tabela de sha do `design.md` (P3-5).

## 2. Detector Impeccable

### 2a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json <arquivo>`, cwd = worktree; com e sem `--no-config --no-inline-ignores`, mesmo resultado)

| Alvo | exit | Achados | Origem |
|---|---|---|---|
| `index.html` | 0 | `[]` | — |
| `etf-short.html` | 0 | `[]` | — |
| `cripto.html` | 0 | `[]` | — |
| `configure.html` | 2 | 6× `gray-on-color` (l.29, l.39: zinc sobre `bg-blue-500/20` dos chips de indicador e do checkbox) · 3× `ai-color-palette` (l.41 `text-purple-300` dos ranges; l.43 gradiente roxo→rosa do botão Otimizar) · `flat-type-hierarchy` (l.20) | Todos em COPIED: l.20 = AppNav desktop (19–21); l.29 = conteúdo vivo (28–29); l.39/41/43 = «continuação viva». Nenhum dentro de DELTA. |
| `live.css` | 2 | 39: 4 `side-tab`, `border-accent-on-rounded`, 2 `overused-font` (Inter), `gradient-text`, 24 `gray-on-color`, 6 `ai-color-palette`, `layout-transition` | CSS vivo inteiro (`index-N9hYlmCr.css`). |
| `delta.css` | 0 | `[]` | DELTA |
| `delta.js` | 0 | `[]` | DELTA |

### 2b. Modo hook (DESIGN.md da raiz do repo)

O CLI dá `[]` no `delta.css` porque procura o DESIGN.md subindo a partir do arquivo e para em `frontend/package.json`, que marca a fronteira do projeto. Assim as regras `design-system-*` nunca rodam abaixo de `frontend/`. O hook usa a raiz do repo. Reproduzi o hook sem tocar no cache, chamando `hook-lib.designSystemOptions(…, REPO)` e depois `detectText`:

| Alvo | Achados | Origem |
|---|---|---|
| `delta.css` | **21 `design-system-color`**, os mesmos 21 do `hook.cache.json` (l.22 … l.77) | DELTA, classificados abaixo |
| `delta.js` | `[]` | DELTA |
| `index.html` / `etf-short.html` / `cripto.html` | 3 cada: `design-system-font-size` 11px/10px (l.20, l.25) | AppNav desktop/móvel COPIED |
| `configure.html` | 13 (os 10 do CLI + 3 `design-system-font-size` l.20/l.25) | COPIED |
| `live.css` | 336 (257 cor, 20 tamanho, 16 raio, 4 fonte, além das regras do CLI) | CSS vivo |

### 2c. As 21 cores do hook no `delta.css`: herdada ou defeito

Busca só-leitura em `frontend/src` (TSX + CSS) e no `live.css`:

| Grupo | Linhas (`delta.css`) | Achados | Onde a tela viva usa | Classe |
|---|---|---|---|---|
| `#b7bdc6` (texto secundário) | 22, 31, 38, 44, 56, 59, 68, 74, 77 | 9 | `ComboResultsPage.tsx:465` (descrição do resultado, mesma rota), `OpportunityCard.tsx:318`, `ChartModal.tsx:694`; 2× no `live.css` | **Herdada** da tela viva. Literal no vivo, não é token do `DESIGN.md`. |
| `#fbbf24` (âmbar de aviso) | 28, 60, 67, 70 | 4 | `AssetPicker.css:10` `--ap-warn-text`, `index.css:2509` `.badge-warning`, `DiscoveryPage.tsx/.css`; 7× no `live.css` | **Herdada** (o seletor vivo dá nome a ela). A l.30 usa a mesma cor, mas o detector não a lista. |
| `#93c5fd` (azul de info) | 26, 64 | 2 | `AssetPicker.css:12` `--ap-info-text`, `DiscoveryPage.css:69`, `DiscoveryPage.tsx`; 4× no `live.css` | **Herdada** |
| `rgba(147, 197, 253, .32 / .45)` (borda azul) | 25, 64 | 2 | **Não existe** em `frontend/src` nem no `live.css`. A borda de info viva é `rgba(59, 130, 246, 0.42)` (`--ap-info-border`, `DiscoveryPage`). | **Defeito do delta** (cor inventada) |
| `rgba(251, 191, 36, .42 / .08)` (borda e fundo âmbar) | 27 | 2 | A faixa âmbar viva é `rgba(245, 158, 11, 0.42)` / `0.08` (`DiscoveryPage.tsx:1961`, `--ap-warn-border` .45). `251,191,36` só aparece no chip de conexão do Monitor (.45/.16). | **Defeito do delta** (troca o matiz de amber-500 para amber-400) |
| `#474d57` (borda do botão recusado e do painel de demonstração) | 56, 77 | 2 | **Não existe** em `frontend/src`, no `live.css` nem no `DESIGN.md`. | **Defeito do delta** na l.56 (produto). A l.77 é do painel de demonstração, que não vai para o produto. |

Resultado: 15 herdadas e 6 defeitos do delta. Nenhum achado foi silenciado e nenhum `impeccable hooks ignore-*` foi rodado; para ignorar, Alan precisa confirmar. A frase do `design.md` (Risks e Prototype Validation) de que as cores «vêm do resultado vivo e do AssetPicker.css» está certa para 15 e errada para 6 (P3-1).

Contraste dos pares do delta (WCAG, calculado): `#b7bdc6`/`#181a20` 9,2:1 · `#b7bdc6`/`#2b3139` (botão recusado) 6,94:1 · `#fbbf24` na faixa âmbar 8,92:1 · `#b7bdc6` na faixa âmbar 7,88:1 · `#93c5fd`/`#181a20` 9,64:1 · `#929aa5`/`#181a20` 6,12:1 · `#fbbf24`/`#1e2329` (linha do gap) 9,48:1. Todos ≥ AA e iguais aos números do autor.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py`, importado via `python3`)

| Verificação | Resultado |
|---|---|
| `design_token_gap(design.md)` | `None` |
| `parse_ui_impact` / `parse_live_route` / `parse_surface` | `affected` / `/combo/results` / `existing` |
| `load_head_catalog(repo)` contém `/combo/results` | sim (`.combo-page`; «Lista de operações», «Análise da estratégia»; `kind: authenticated`) |
| `evaluate_clone_gate(design, proto, repo)` (HEAD padrão e explícito) | **True** |
| `canonical_proto_html(proto)` é o `index.html` | sim |
| `landmarks_match(/combo/results, index.html)` | **True** |
| `copied_utf8_sum(index.html)` | **24741** (> 0; total 46106) |
| `classify(index.html, /combo/results)` (HEAD e arquivo padrão) | **PASS** |
| `clone_gate_ok(change, proto, repo)` | **True** |
| extras | `etf-short` 24932 / `cripto` 25568 (landmarks True) · `configure` 29361. `/combo/configure` não está no catálogo, então é um extra sem gate próprio, como declarado. Os números batem com a tabela do `design.md`. |

## 4. Browser real

Playwright Python 1.62 + Chromium 1243 (`chrome-linux-arm64`, `--no-sandbox`), headless, `colorScheme: dark`, `locale: pt-BR`. Abri **as URLs públicas** `https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/` (+ `etf-short.html`, `cripto.html`, `configure.html`). Viewports **1440×900** (desk) e **390×844** (mob), com um contexto novo por tela × viewport, e mais 1100/1024/760 px no index para a regra de colunas. 38 screenshots em `/tmp/1119-B-shots/` (`<tela>-<vp>-01-load` … `-99-final`).

Console: o único `error` foi `GET https://dev.criptofarol.com.br/favicon.ico 404`, uma vez por browser (primeira carga). É a raiz do DEV, não o protótipo: o proto não declara favicon. Por isso há 1 FAIL em L1 (P3-6). Fora isso: 0 `console.error`, 0 `pageerror`, 0 resposta ≥ 400 e 0 `requestfailed`.

### Matriz de asserts

| # | Assert | index d/m | etf d/m | cripto d/m | configure d/m |
|---|---|---|---|---|---|
| L0 | digest da página no browser == esperado | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |
| L0b | digest de live.css/delta.css/delta.js no browser | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |
| L1 | sem console error / pageerror / ≥400 / requestfailed | **FAIL**/PASS (favicon da raiz) | PASS/PASS | PASS/PASS | PASS/PASS |
| L2 | sem rolagem horizontal na carga (`scrollWidth ≤ clientWidth`, 0 elemento fora sem contêiner) | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |
| L3 | sem rolagem horizontal depois dos estados | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |
| M0 | COPIED/DELTA em pares no corpo servido | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |
| D0 | Demonstração `static`, no fim, nada fixo dentro | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |
| G0 | landmarks de `/combo/results` | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R1 | chip de classe «Ação» / «ETF» / «Cripto» | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R2 | proveniência «fonte · sessão · ajuste · moeda» | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R3 | os 8 fatos (Ativo, Fonte e sessão, Ajuste e moeda, Tempo gráfico, Janela pedida, Janela coberta, Amostra, Precisão) | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R3b | amostra «Versão N · guardada até …» | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R4 | fatos em 4 colunas (1440) / 1 coluna (390) | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R4m | 2 colunas a 1100, 1024 e 760 px, sem rolagem | PASS (3/3) | — | — | — |
| R5 | convenções: gap, custos, calendário, anualização | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R5b | gap com a contagem e o exemplo da execução | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R6 | ação/ETF: «Posição com fração» + «não confirma»; cripto sem aviso de fração | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R7 | anualização: dias corridos ÷ 365; 252 pregões (ação/ETF); 365 × 6 candles de 4h (cripto) | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R7b | custo: ação/ETF «assumida»; cripto 0,075% + slippage 0,02% sem «assumida» | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R7c | index «Preços ajustados»; cripto avisa que números antigos podem ser melhores onde houve gap | PASS/PASS | — | PASS/PASS | — |
| R7d | SPY: «Short simulado» não implica vender a descoberto | — | PASS/PASS | — | — |
| R8 | SPY: «1h montado do 5m», «15:30–16:00», «nenhum candle atravessa o fechamento» | — | PASS/PASS | — | — |
| R8b | sessão fechada: «1 ago. é sábado: o primeiro pregão é 3 ago.» | — | PASS/PASS | — | — |
| R9 | moeda: ação/ETF sem USDT na lista; cripto com preço em USDT | PASS/PASS | PASS/PASS | PASS/PASS | — |
| R10 | «Stop com gap» + «stop X · abriu Y» na tabela (1440) / «Stop com gap · stop X, abriu Y» no cartão (390) | PASS/PASS | PASS/PASS | PASS/PASS | — |
| P1 | precisão inicial: NVDA diária âmbar, `role=note`, trecho «11 nov. 2014 a 18 mai. 2026»; SPY e cripto intrabar 15m azul | PASS/PASS | PASS/PASS | PASS/PASS | — |
| P2 | estados da precisão: «error» âmbar + «Não foi possível ler»; «off» azul + «Deep Backtest desligado»; de volta a «missing»; cripto «15m não cobre» âmbar «18 mar. 2026 a 24 mar. 2026». O fato «Precisão» acompanha. | PASS ×3/PASS ×3 | — | PASS/PASS | — |
| F0 | cripto: «Salvar nos Favoritos» vivo, sem `aria-disabled` nem motivo | — | — | PASS/PASS | — |
| F1 | ação/ETF: botão visível, `aria-disabled=true`, `aria-describedby` → motivo visível | PASS/PASS | PASS/PASS | — | — |
| F2 | alvo ≥ 44 px (219×44 desk, 247×44 mob) | PASS/PASS | PASS/PASS | — | — |
| F3 | clique real de mouse: «Não salvo. …» em `role=status`, nenhum `dialog`/`aria-modal` | PASS/PASS | PASS/PASS | — | — |
| F4 | Tab alcança o botão recusado | PASS/PASS | PASS/PASS | — | — |
| F5 | foco visível no botão (outline 2px `#3b82f6`) | PASS/PASS | PASS/PASS | — | — |
| F6 | `Enter` e `Space` anunciam a recusa, sem modal, e o foco fica no botão | PASS/PASS | PASS/PASS | — | — |
| C1 | Market Data «Binance Ações · pregão regular de Nova York · ajustado por split» | — | — | — | PASS/PASS |
| C2 | AAPL «Histórico sob demanda · coletado ao rodar o backtest de 1 ativo» | — | — | — | PASS/PASS |
| C3 | nota de classe nova | — | — | — | PASS/PASS |
| C4 | 15m/1h/4h/1d habilitados; 1m/5m «(só cripto)» desabilitados; 1h escolhido | — | — | — | PASS/PASS |
| C5/C6 | dica de tempo da ação; dica do Deep Backtest (precisão diária e trecho) | — | — | — | PASS/PASS |
| C7 | texto antes de rodar «1 ação (NVDA): otimiza e abre o resultado, sem salvar em favoritos …» | — | — | — | PASS/PASS |
| C8 | seleção mista: roda só BTC/USDT e diz «Fora: NVDA (Ação)»; chip BTC entra; fonte CCXT | — | — | — | PASS/PASS |
| C9 | NVDA em 5m: «Otimizar» não roda; aviso `role=status` «Escolha 15m, 1h, 4h ou 1d»; fica na página | — | — | — | PASS/PASS |
| C10 | coleta falha sem dados: `role=alert` «Histórico de NVDA indisponível agora»; nada roda | — | — | — | PASS/PASS |
| C11 | «Otimizar» com 1 ação abre `index.html` | — | — | — | PASS/PASS |
| K1 | Tab alcança «Otimizar» com foco visível | — | — | — | PASS/PASS |
| K2 | `aria-pressed` coerente nos botões da Demonstração | — | — | — | PASS/PASS |
| K3 | foco visível em toda parada de Tab do DELTA | PASS/PASS | PASS/PASS | PASS/PASS | PASS/PASS |

**Total: 221 asserts, 220 PASS, 1 FAIL** (L1 index desk: favicon da raiz do DEV).

Caminhada de teclado completa (página nova, Tab do topo até voltar ao início): index 22/13 paradas, etf 19/10, cripto 21/12, configure 39/30 (desk/mob). Em nenhuma parada falta anel de foco, e o foco nunca cai fora da área visível. Ordem no index desk: AppNav (8 links + Recolher + conta) → Voltar → **Salvar nos Favoritos (recusado)** → Detalhes técnicos → Exportar → Demonstração.

Conferência manual dos números da amostra (regra «sem gap nada muda»):
- Toques sem gap saem no stop exato:
  - NVDA: 204,60 × 0,95 = 194,37 («Stop», 194.37).
  - SPY short: 668,30 × 1,0115 = 675,98.
  - BTC: 101.400 × 0,95 = 96.330.
- Saídas com gap saem na abertura:
  - NVDA: stop 191,30 × 0,95 = 181,74, saída a 172,10, −10,21% com custo.
  - SPY: stop 664,40 × 1,0115 = 672,04, saída a 676,10.
  - BTC: stop 99.820 × 0,95 = 94.829, saída a 93.610.
- Datas:
  - 1 ago. 2026 é sábado.
  - O meio-pregão de 27 nov. 2026 é a sexta depois de Ação de Graças (26 nov.).
  - O horário de verão vira em 8 mar. e 1 nov. 2026.

Pixels, desk: shell vivo (sidebar 224 px). O «Salvar nos Favoritos» recusado fica cinza à direita, com o motivo embaixo, e fica âmbar por 1,6 s depois do clique. Chip «Ação» azul ao lado de NVDA. «Dados e execução» com a faixa âmbar «Precisão diária», 4 colunas de fatos e as convenções em 2 colunas. Na lista, «Stop com gap» em âmbar com «stop 181.74 · abriu 172.10».
Pixels, mob: AppNav móvel. O botão recusado fica ao lado de «Voltar» com o motivo embaixo. Fatos em 1 coluna, convenções em 1 coluna, cartão de operação com «Stop com gap · stop 181.74, abriu 172.10».
Pixels, clone: o resumo vivo («Médias: tendência») aparece sem padding interno, os chips ficam sem padding e o bloco «Dados e execução» encosta no resumo (gap 0). A causa é a regra sem layer `* { margin: 0; padding: 0 }` de `frontend/src/index.css:649`, que vence os utilitários do Tailwind v4 em `@layer utilities`. É igual no vivo (herdado), e o delta só escapa porque usa CSS sem layer (P3-4).

## 5. Confronto com o Entra (só o visível; backend = Apply)

| Entra | Visto no browser | Disposition |
|---|---|---|
| Ação e ETF no backtest individual, cripto como hoje; resultado com ativo, classe, sessão, ajuste, moeda, janela coberta e versão da amostra | R1–R3b nas 3 telas de resultado; C7/C11 no Combo | PASS (o que é «backtest individual» é a Open Question 1 do `design.md`) |
| 15m, 1h, 4h e 1d no pregão, sem candle que atravesse o fechamento | C4, C5, R8 (1h), 1d no index, 5m recusado (C9) | PASS (15m/4h de ação sem texto de fato prototipado, P3-8) |
| Precisão intrabar; sem intradiário, precisão diária com o trecho, nunca em silêncio | P1/P2: faltou com trecho, falha ao ler, desligado, cripto não cobre | PASS |
| Gap no stop (long, short, cripto), com custo e slippage; sem gap nada muda | R5b, R10 e a conta manual acima | PASS |
| Fração permitida, com aviso de que não confirma a conta (#1124) | R6 | PASS |
| Custos, anualização, calendário e direção por classe; short não implica venda descoberta | R7–R7d, R8b | PASS (taxa «assumida» até o Apply confirmar) |
| Favoritar ação/ETF recusado com motivo visível; cripto como hoje | F0–F6 por clique e teclado | PASS |
| Demonstrar gap long/short, split, horário de verão, sessão fechada, falta de intradiário e regressão cripto antes/depois | Gap long/short/cripto e falta de intradiário na tela; sessão fechada (sábado); split e horário de verão em convenções e testes (decisão 17); cripto mostra o «depois» e avisa que o antigo pode ser melhor | PASS, com P2-3 sobre o «antes» |
| Não entra: lote/Descoberta continuam recusados com o motivo de hoje | C8: o lote do Combo continua deixando NVDA fora, mas com motivo **novo** | P2-1 |
| Não entra: favoritos/refresh/alertas de ação/ETF, exportação, ordens | nenhum controle novo; «Exportar para Excel» é o vivo | PASS |

## 6. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | A precisão efetiva tem faixa própria, com tom só quando cai; a recusa de favorito é anunciada | — |
| 2 | Match com o mundo | «pregão regular de Nova York», «montado do 5m», «abriu 172,10» | — |
| 4 | Consistência | Na cripto, preço em USDT e valor/lucro em USD na mesma linha | P2 |
| 5 | Prevenção de erro | 5m com ação não roda e explica; o botão recusado não abre o modal | — |
| 6 | Reconhecimento | Os 8 fatos ficam no mesmo lugar nas 3 classes | — |
| 9 | Recuperação | A coleta falha vira alerta com o motivo e o «tente de novo» | — |
| 10 | Ajuda/documentação | As convenções explicam gap, custo, calendário e anualização da própria execução | — |

## 7. Achados

### P0: nenhum

### P1: nenhum

Nenhum assert ligado a um critério do Entra falhou. O único FAIL é ambiente (favicon da raiz do DEV).

### P2 (não bloqueiam; juízo de Alan)

- **P2-1 O motivo da seleção mista do Combo muda** (`configure.html`, estado «NVDA + BTC/USDT»). *Juízo.* O Não entra diz «Combo em lote e descoberta com ação e ETF (#1120, #1121): continuam recusados com o motivo de hoje». A decisão 3 do `design.md` mantém a recusa, mas troca o porquê **só no Combo** («Fora: NVDA (Ação) — ação e ETF rodam só sozinhos, no backtest de 1 ativo»), porque o texto de hoje (`EQUITY_UNSUPPORTED_MESSAGE`, «Análise ainda não disponível para ações e ETFs») ficaria falso no Combo. A troca faz sentido, mas contraria a letra de uma decisão fechada de Alan e não está nas Open Questions. **Corrigir:** levar como Open Question 3 na Aprovação de Design, ou voltar ao texto de hoje.
- **P2-2 Moeda das colunas de valor na lista de operações da cripto** (`cripto.html`, desk e mob). *Juízo.* O preço sai em `USDT`, mas Valor da posição, Lucro/Prejuízo, Máximo favorável/adverso e Resultado acumulado saem em `USD` («95,100.00 USDT» ao lado de «95.53 USD»). É o `StrategyTradesTable.tsx:65-333` vivo (`USD` fixo), mantido de propósito como regressão. Mas o Apply contract diz «lista de operações na moeda da classe», e a proveniência diz «USDT». Para ação/ETF as duas coincidem em USD. **Corrigir:** dizer no `design.md` se as colunas de valor seguem `asset.currency` (a cripto passa a mostrar USDT, o que muda a tela de hoje) ou se ficam em `USD` nocional, com essa ressalva no contrato.
- **P2-3 Regressão cripto sem o «antes» na tela** (`cripto.html`). *Juízo.* O Entra pede «regressão cripto com antes/depois: sem gap o resultado é igual; com gap a diferença aparece e é explicada». A tela mostra o «depois» (trade com gap: stop e abertura) e uma frase genérica («calculados antes desta regra podem ter número melhor»). A tabela antes/depois vai para o handoff (decisão 17). Lendo «a diferença aparece» como algo da tela, falta o efeito no número (p.ex. «sem a regra do gap: saída a 94.829,00, −5,18%»). **Corrigir:** Alan escolhe entre handoff só (como está) e uma linha de impacto na convenção «Gap no stop».

### P3 (aceitos: Apply, clone, ambiente; não reabrir como P0/P1)

- **P3-1 Seis cores do delta não existem na tela viva.** *Mecânico.* Três trocas resolvem:
  - `rgba(147,197,253,.32/.45)` (l.25, l.64) → `--ap-info-border` `rgba(59,130,246,0.42)`.
  - `rgba(251,191,36,.42/.08)` (l.27) → `rgba(245,158,11,0.42/0.08)` da Descoberta, ou `--ap-warn-border`.
  - `#474d57` (l.56; a l.77 é só da Demonstração) → `--border-default` `#2b3139` ou um token novo declarado.

  Corrigir também a frase de Risks/Prototype Validation que chama as 21 de herdadas.
- **P3-2 Quinze cores herdadas como literais** (`#b7bdc6` ×9, `#fbbf24` ×4, `#93c5fd` ×2). *Mecânico.* São da tela viva, e por isso não são defeito do card. No Apply, usar `var(--ap-warn-text)`/`var(--ap-info-text)` do `AssetPicker.css` em vez de repetir o literal. `#b7bdc6` não é token do `DESIGN.md`: documentá-lo ou trocá-lo é decisão fora do card. Nenhum achado foi ignorado; ignorar exige Alan.
- **P3-3 O detector CLI não aplica o DESIGN.md abaixo de `frontend/`.** *Mecânico, processo.* `detect.mjs` para no `frontend/package.json` (`findDesignRoot`), e por isso o «`[]` no `delta.css`» do `design.md` não cobre as regras `design-system-*`. O hook, rodado da raiz, acha 21. A Prototype Validation deve citar os dois modos.
- **P3-4 Reset `*` sem layer zera utilitários Tailwind.** *Mecânico, risco de Apply.* `index.css:649` (`* { margin: 0; padding: 0 }`) vence `@layer utilities`, e o resumo vivo, os chips e o espaçamento entre blocos ficam com 0. O delta só tem padding porque `delta.css` também está fora de layer. Se o Apply escrever «Dados e execução» com `p-5`/`gap-*` no TSX, o bloco perde o padding do protótipo. Implementar em CSS próprio (como `AssetPicker.css`) ou conferir os pixels no E2E. Mexer no reset fica fora do card.
- **P3-5 As capturas PNG do gráfico não têm sha256 na tabela do `design.md`.** *Mecânico.* São 6 arquivos servidos e visíveis na página (`btc/nvda/spy-chart-{desk,mob}.png`). Entram na tabela de Prototype Validation.
- **P3-6 `favicon.ico` 404 na raiz de `dev.criptofarol.com.br`.** *Mecânico, ambiente.* Aparece uma vez por browser no console. Não é do proto.
- **P3-7 O estado «NVDA em 5m» reabilita 1m/5m** (`delta.js` `setSel('tf5')`), enquanto o contrato diz que ficam indisponíveis com ação. Na seleção mista, que roda só BTC, 1m/5m continuam desabilitados. *Juízo menor.* Dizer como o estado 5m + ação nasce (seleção anterior ou prefill) e se o seletor troca sozinho para 15m.
- **P3-8 Falta texto prototipado para 15m e 4h de ação no fato «Tempo gráfico».** Só 1h (SPY) e 1d (NVDA) aparecem. *Mecânico.* Seguir o padrão da decisão 5 («4h montado do 5m · 09:30–13:30 e 13:30–16:00»; meio-pregão 09:30–13:00).
- **P3-9 Achados do detector no incumbente clonado.** *Mecânico.* `configure.html`: cinza sobre azul, roxo e gradiente do botão Otimizar, hierarquia plana. AppNav: 10/11 px fora da rampa. `live.css`: 39 no CLI e 336 no modo hook. Nenhum está no delta e todos ficam fora do escopo do card.
- **P3-10 Já aceitos no `design.md`, só registrados.** «Otimizar» na seleção mista não faz nada no protótipo; números com ponto («181.74») ao lado de vírgula («181,74»); datas em inglês na lista viva; números, datas e versões da amostra.

Mecânicos: P3-1, P3-2, P3-3, P3-4, P3-5, P3-6, P3-8, P3-9, P3-10. Juízo: P2-1, P2-2, P2-3, P3-7.

## 8. Veredito

**PASS.** P0 e P1 zerados.

- **Digests:** batem do disco ao HTTPS e ao corpo visto pelo browser nos 7 arquivos da tabela.
- **Gate estático:** passa (`design_token_gap=None`, `evaluate_clone_gate=True` com o catálogo do HEAD, landmarks de `/combo/results` no index, `copied_utf8_sum=24741`, `classify=PASS`).
- **Detector:** o CLI deixa o delta limpo. No modo hook, das 21 cores do `delta.css`, 15 vêm da tela viva e 6 são do delta, todas P3 mecânicas.
- **Browser:** 220/221 asserts passam nas 4 telas × 2 viewports. Todos os critérios visíveis do Entra estão cobertos:
  - identidade da execução;
  - tempos do pregão;
  - precisão efetiva nos 4 estados, com o trecho;
  - gap long, short e cripto;
  - fração e short;
  - custo «assumido»;
  - anualização 252/365;
  - favoritar recusado com motivo visível, por clique e por teclado, sem modal;
  - cripto «como hoje»;
  - Combo com 1 ação, 5m recusado, coleta falha e seleção mista.

  Foco visível em todas as paradas e nenhuma rolagem horizontal. O único FAIL é o favicon da raiz do DEV.

Disposition: sem rework obrigatório. P2-1, P2-2 e P2-3 são decisões de Alan, que entram nas Open Questions da Aprovação de Design ou no único rework. Os P3 ficam aceitos para o Apply. P3-1 e P3-5 são baratos de corrigir no pacote se houver rework.

## 9. Referências

- Disco: `frontend/public/prototypes/card-1119-backtest-acoes-etfs/{index,etf-short,cripto,configure}.html`, `live.css`, `delta.css`, `delta.js`, `*-chart-{desk,mob}.png`
- HTTPS DEV (prova): https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/ (+ `etf-short.html`, `cripto.html`, `configure.html`)
- Viewports: 1440×900 · 390×844 (+ 1100/1024/760 no index) · `colorScheme: dark` · `locale: pt-BR`
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` (CLI) e `hook-lib.designSystemOptions` + `detectText` a partir da raiz (modo hook, sem escrever no cache)
- Gate: `scripts/process-fsm/design_clone_gate.py` + `scripts/process-fsm/route-landmarks.yaml` (HEAD)
- CSS vivo consultado (só leitura): `frontend/src/pages/ComboResultsPage.tsx`, `frontend/src/components/AssetPicker.css`, `frontend/src/index.css`, `frontend/src/pages/DiscoveryPage.{tsx,css}`, `frontend/src/components/charts/StrategyTradesTable.tsx`, `frontend/src/lib/assetSelection.ts`
- Shots e JSON: `/tmp/1119-B-shots/` (38 PNG, `asserts.json`, `det-*.json`; não versionados)

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
