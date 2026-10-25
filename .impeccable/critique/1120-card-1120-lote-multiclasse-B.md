> Proveniência: Assessment B (detector + browser real), papel `assessment-b`, faixa `juizo`, modelo da captura **Opus 5.5** (`claude-opus-5-5`, effort `high`), captura `assess-b1.capture.json` (attempt `d554c9a8-6cb6-4ff1-a5a7-c9c5c1797583`), 2026-10-24T23:37Z.

# Assessment B (detector + browser real): card 1120 · change card-1120-lote-multiclasse

> Assessor B isolado. Não vi o transcript do pai nem o de A. O snapshot A existe na pasta e **não** foi lido. Não houve nested-spawn. Cliente Claude Code (adapter cooperativo, sem modo Auto).
> Este filho escreveu um único arquivo: este snapshot. Screenshots, JSON e scripts de trabalho ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/f34a4e0e-5dff-4fe2-9a98-4a3fda87bbb1/scratchpad/1120/B/` e não são versionados.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /favorites` · `surface: existing`, nas linhas 1 a 3, cada um em linha própria.

```
Assessment B 1120
snapshot: .impeccable/critique/1120-card-1120-lote-multiclasse-B.md (2026-10-24T23:37Z)
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == design.md == HTTPS (curl) == corpo visto pelo browser, IDENTICAL nos 3 HTML + live.css/delta.css/delta.js; a pasta / serve o sha do index; design.md 08f581da… bate antes e depois
detector CLI: index 9 · configure 11 · optimize 5 · delta.css 0 · delta.js 0 · live.css 39 → HTML 25 achados, 25 COPIED × 0 DELTA
detector hook (DESIGN.md da raiz): index 12 · configure 14 · optimize 8 (+3 design-system-font-size do AppNav cada, COPIED) · delta.css 0 · delta.js 0 · live.css 335 → DELTA 0
gate: design_token_gap=None · evaluate_clone_gate(HEAD)=True · landmarks(/favorites, index)=True · copied_utf8_sum(index)=82525 · classify(index,/favorites)=PASS · clone_gate_ok=True · extras configure 32805 / optimize 27841 (fora do catálogo)
browser: 434 asserts, 404 PASS, 30 FAIL (nenhum ligado a critério do Entra) · 0 console error / pageerror / ≥400 / requestfailed · Tab: 12 caminhadas, 0 parada sem anel
P0: nenhum
P1: nenhum
P2: [juízo] Otimização em 15m/1h/4h contradiz a decisão 4 · [juízo] contagem de coleta conta NVDA, cujo catálogo diz «sem lacunas» · [juízo] «Market Data: CCXT» no lote misto · [juízo] Otimização com «Select Strategy…» e «Ready to Optimize» ao lado do lote rodando
P3: [mecânico] marcador dentro da tag quebra o «Ver logs» (configure l.39) · [mecânico] --fav-up fora de escopo: Sucesso/ETF/Concluído sem verde no Combo e na Otimização · [mecânico] motivo e Configuração do Confirmar fixos em 5m/1d · [mecânico] foco some depois de Encerrar · [Apply] linha viva recriada a cada render · [mecânico] filtros Symbol/Strategy/Time/Direção sem ligação no protótipo · [mecânico] contagem do detector do index no design.md · [herdado] achados do incumbente · [processo] parse_live_route captura a linha seguinte
verdict: PASS com P2-P3
```

- UTC: 2026-10-24T23:37Z
- Tupla (só leitura):
  - `bound_card=1120`
  - `q_git=card-1120-lote-multiclasse` @ `e762e470`
  - Status=**Design**, conferido via GraphQL do Project, sem mudança.
- Pacote não commitado. O `git status` mostra o protótipo, a change e o snapshot A como `??`.
- Não houve `process_event`, commit, push, comentário nem restart.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1120 --jq .body`, sem `gh issue view`. É o body grelhado, com 10 itens no Entra (5 decisões de Alan de 24/10/2026) e 5 no Não entra. As decisões não foram reabertas.
- `design.md` sha256 `08f581da0f20c10a10dfdeea8c333f32d4121ed60c9398e0f8b1764b0dd4838e`. Bate com o prompt antes e depois da rodada.

## 1. Digest servido == local

| Arquivo | sha256 (disco = tabela do design.md = HTTPS curl = browser) | bytes | HTTPS |
|---|---|---|---|
| `index.html` (canônico; `/` serve o mesmo) | `ddb921cd2c24098f9d0a899ca01551037d0a20c7af47ccde19bb9da929123922` | 108664 | 200 |
| `configure.html` | `975fbed5528746441b17d430fd5a0dc1c444e12601c0e4b028c40b01a55f8622` | 37088 | 200 |
| `optimize.html` | `4605255e5c1d1b7a5abc8b368edfaa1803d028b6a6b67bf297a74175d709cefb` | 31625 | 200 |
| `live.css` | `da9e66e69f963f98815d45baf15fbb0dc8eea0f31b3225a363a8be171b5abf7b` | 227726 | 200 |
| `delta.css` | `9a8236917c1685d260592bcb90e72af54a919431e13e781f9fad0556e26eebfb` | 17011 | 200 |
| `delta.js` | `66c996804bdccb4d22ee5da609b944dbca8bca946d3d89f357a21b22ad4b9320` | 27913 | 200 |

No Playwright, três hashes bateram com o esperado nas 6 combinações tela × viewport e na pasta `/`:

- L0: o `response.body()` da navegação.
- L0a: um `fetch(location)` feito dentro da página.
- L0b: as respostas de `live.css`, `delta.css` e `delta.js`.

## 2. Detector Impeccable

### 2a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json <arquivo>`, cwd = worktree; com e sem `--no-config --no-inline-ignores`, mesmo resultado)

Cada achado foi classificado pela região de marcador da linha (script `classify.py`). Nenhuma linha com achado tem marcador DELTA.

| Alvo | exit | Achados | COPIED | DELTA |
|---|---|---|---|---|
| `index.html` | 2 | 8× `gray-on-color` «text-zinc-400 on bg-amber-400» (l.39, 43, 47, 51 = cartões móveis; l.59, 69, 79, 89 = linhas da tabela), todos na marcação viva das estrelas. 1× `flat-type-hierarchy` (l.20, AppNav desktop) | 9 | 0 |
| `configure.html` | 2 | 7× `gray-on-color` (l.29 e l.37: zinc sobre `bg-blue-500` dos chips e checkbox vivos). 3× `ai-color-palette` (l.37 `text-purple-300`; l.39 gradiente roxo do botão Otimizar). 1× `flat-type-hierarchy` (l.20) | 11 | 0 |
| `optimize.html` | 2 | 4× `ai-color-palette` (l.29 `text-purple-400`; l.37 `text-purple-300` e gradiente do Run Optimization). 1× `flat-type-hierarchy` (l.20) | 5 | 0 |
| `delta.css` | 0 | `[]` | — | 0 |
| `delta.js` | 0 | `[]` | — | 0 |
| `live.css` | 2 | 39: 24 `gray-on-color`, 6 `ai-color-palette`, 4 `side-tab`, 2 `overused-font`, 1 `border-accent-on-rounded`, 1 `gradient-text`, 1 `layout-transition` | CSS vivo inteiro | — |

Pasta inteira (`detect.mjs --json <pasta>`): 64 = 25 HTML + 39 `live.css`. Nos HTML, **25 COPIED × 0 DELTA**.

### 2b. Modo hook (DESIGN.md da raiz; `hook-lib.loadDetector` + `designSystemOptions(…, REPO)` + `detectText`, sem escrever no cache)

| Alvo | Achados | Origem |
|---|---|---|
| `delta.css` | **0** | DELTA. Todas as cores passam por `var(--…)` (90 usos) e a rampa é 12/13/14/16 px. Os hex só aparecem no comentário de cabeçalho e como fallback (`var(--bg-input, #2b3139)`, `var(--accent-primary-hover, #f0b90b)`), os dois iguais ao `:root` vivo. |
| `delta.js` | 0 | DELTA |
| `index.html` / `configure.html` / `optimize.html` | 12 / 14 / 8 = os do CLI + 3× `design-system-font-size` 11px/10px (l.20, l.25) em cada | AppNav desktop/móvel COPIED |
| `live.css` | 335 (256 cor, 20 tamanho, 16 raio, 4 fonte, além das 39 do CLI) | CSS vivo |

O `hook.cache.json` desta sessão também registra `delta.css` e `delta.js` com `findings: []`. Nenhum achado foi silenciado e nenhum `impeccable hooks ignore-*` foi rodado.

O detector não pega um problema de token no delta. `--fav-up` só existe dentro de `.favorites-workbench` no `live.css`, mas o `delta.css` o usa também no Combo e na Otimização: no chip ETF (l.24), no estado Sucesso (l.137) e no selo Concluído (l.109). Fora de Favoritos a variável não resolve, e o browser mediu `rgb(234,236,239)` e `rgb(146,154,165)` onde o esperado era `rgb(14,203,129)` (P3-2).

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py`, importado via `python3`)

| Verificação | Resultado |
|---|---|
| `design_token_gap(design.md)` | `None` |
| `parse_ui_impact` / `parse_live_route` / `parse_surface` | `affected` / `('/favorites', 'surface: existing')` / `existing`. A regex da rota engole a linha seguinte como «justificativa». Isso é inofensivo com rota de catálogo (P3-9). |
| `load_head_catalog(repo)` contém `/favorites` | sim: `table.fav-strategies`; «Estratégias favoritas», «Symbol», «Estratégia», «Ações»; `kind: authenticated` |
| `evaluate_clone_gate` (catálogo do HEAD e catálogo em arquivo) | **True** / **True** |
| `canonical_proto_html(proto)` é o `index.html` | sim |
| `landmarks_match(/favorites, index.html)` | **True** (`table.fav-strategies` presente) |
| `copied_utf8_sum(index.html)` | **82525** (> 0; total 108664). Bate com a tabela do autor. |
| `classify(index.html, /favorites)` | **PASS** |
| `clone_gate_ok(change, proto, repo)` | **True** |
| extras | `configure.html` copied 32805 e `optimize.html` copied 27841, iguais ao autor. `/combo/configure` e `/combo/optimize` não estão no catálogo, então `classify` dá BLOCKED para qualquer rota: são extras sem gate próprio, como o design.md declara. |

Fora do gate, achei um marcador dentro de uma tag. Em `configure.html` l.39, o `<!-- COPIED:end -->` e o `<!-- DELTA:start confirmar lote … -->` estão **dentro** da tag `<button … >` do «Ver logs». O gate conta a string e os pares parecem balanceados (10/10, 7/7), mas o parser HTML lê `<!--` como atributo e fecha a tag em `-->`. O resultado no DOM:

- O botão sai com o texto `title="Ver logs do backend (últimas linhas)">Ver logs`.
- Ele fica sem `title`, com os atributos `type class <!-- copied:end --`.

Acontece nos dois viewports e é o único marcador dentro de tag nos 3 HTML (P3-1).

## 4. Browser real

Ambiente:

- Playwright Python 1.62 + Chromium headless shell 1243 (`153.0.8010.12`, arm64, `--no-sandbox`).
- `colorScheme: dark`, `locale: pt-BR`.
- **URLs públicas** `https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/` (+ `configure.html`, `optimize.html`, e a pasta `/`).
- 1440×900 (desk) e 390×844 (mob, `isMobile`, toque, DPR 2), com **contexto novo** por página × viewport e por cenário (padrão, Encerrar/tempos, lote grande/problemas).
- 56 screenshots em `shots/` e `asserts.json`.

Erros de rede e de página nas 6 combinações tela × viewport (mais `/` e a navegação pelo link do lote):

- 0 `console.error`
- 0 `pageerror`
- 0 respostas ≥ 400
- 0 `requestfailed`

### Matriz de asserts

| Página × viewport | Asserts | PASS | FAIL |
|---|---|---|---|
| `index.html` desk | 52 | 51 | 1 (F4) |
| `index.html` mob | 50 | 49 | 1 (F4) |
| `/` desk / mob | 2 / 2 | 2 / 2 | 0 |
| `configure.html` desk | 84 | 78 | 6 (C7i, C7j, C7k, C13b, C14i, C14j) |
| `configure.html` mob | 84 | 78 | 6 (idem) |
| `optimize.html` desk | 80 | 72 | 8 (idem + C15, C15b) |
| `optimize.html` mob | 80 | 72 | 8 (idem) |
| **Total** | **434** | **404** | **30** |

Asserts por grupo (d = desk, m = mob):

- **Comuns, em todas as páginas:**
  - L0, L0a e L0b: digests.
  - L1: sem erros.
  - L2 e L3a–e: sem rolagem horizontal na carga e depois de cada estado, com `scrollWidth ≤ clientWidth` e nenhum elemento fora sem contêiner.
  - M0: COPIED/DELTA em pares no corpo servido.
  - D0: a Demonstração fica `static`, no fim, sem fixed/sticky dentro.
  - X0: nenhum «o lote vem depois».
  - Todos PASS d/m.
- **Favoritos (`index.html`), todos PASS d/m, exceto F4:**
  - G0: landmarks de `/favorites`.
  - F0: 5 favoritos (tabela no desk, cartões no mob, a outra forma oculta).
  - F0b: lista única com cripto, ação e ETF.
  - F0d: ordem padrão Ret/T % decrescente.
  - R1 e R1b: NVDA «Ação · USD» e SPY «ETF · USD», sem USDT na linha.
  - R1c: BTC/ETH/SOL «Cripto · USDT», sem «USD» solto.
  - R2 e R2b: «Precisão diária · sem 15m de 11 nov. 2014 a 18 mai. 2026» e «… 2 jan. 2015 a 18 mai. 2026».
  - R2c: precisão diária em âmbar `rgb(251,191,36)`, com ícone e `data-tone=warn`.
  - R2d: BTC «Precisão intrabar (15m)» em azul `rgb(147,197,253)`, com ícone.
  - R3 e R3b: convenções por classe em cada linha.
  - R4: limitações só em ação/ETF.
  - R5 e R5b: período efetivo; favorito antigo ETH «aparecem na próxima atualização diária».
  - R6: «Gerado em lote 7f3c2a91» só em NVDA, BTC e SPY.
  - R7: «Atualização diária: ainda não para ações e ETFs».
  - R8: ATR com moeda («4.87 USD», «1834.20 USDT», «6.12 USD»; coluna avançada, desk).
  - R9: chip ETF verde em Favoritos.
  - F1, F1a e F1b: filtro Classe «Todas (5) / Cripto (3) / Ações (1) / ETFs (1)», com nome acessível, antes de Symbol na mesma faixa (desk).
  - F2 (×4): Classe = Ações → NVDA, ETFs → SPY, Cripto → 3, Todas → 5; «N filtradas» e o rodapé seguem.
  - F3 (×3) e F3b: Ordenar Return/Trades/Sharpe decrescente com as 3 classes juntas; Classe + Ordenar combinam.
  - F5, F5b e F5c: Demonstração «Pelo fim do lote» com a faixa `role=status`, 3 do lote e `aria-pressed`.
  - F6 a F6d: `?lote=7f3c2a91` mostra a faixa «Mostrando só o lote 7f3c2a91 … de todas as classes» e só BTC/NVDA/SPY (3 classes). «Mostrar todos os favoritos» tem 44 px; o clique volta a 5, limpa a URL e põe o foco no filtro Classe.
  - K1–K3: foco.
  - **F4 FAIL d/m:** Symbol = NVDA não filtra. Os selects Symbol/Strategy/Time/Direção não estão ligados no `delta.js` (P3-6).
- **Combo (`configure.html`) e Otimização (`optimize.html`):**
  - C1: nota da classe da decisão 6, texto exato no Combo e trechos na Otimização.
  - C2 e C2b: «Histórico sob demanda · coletado ao rodar o backtest ou o lote»; seleção BTC/USDT + NVDA + SPY visível.
  - C3: tempos «(só cripto)» escolhíveis (Otimização com 30m), 1d selecionado.
  - C4: texto antes de rodar exato. C4b: janela fixa na Otimização.
  - C5 a C5i, depois de clicar em rodar:
    - «Confirmar lote de 3 ativos» abre no fluxo, sem `role=dialog`/`aria-modal`, com foco no título.
    - «1 cripto (USDT), 1 ação (USD), 1 ETF (USD)».
    - **«2 de 3» precisam de coleta antes de confirmar**, com o quê (NVDA 5m, SPY 1d+5m), em faixa azul.
    - «Ficam fora: nenhum», Configuração e Favoritos.
    - Botões de 44 px; «Confirmar e rodar» em amarelo primário.
  - C6: Voltar fecha e devolve o foco ao botão de rodar.
  - C7 a C7h, no painel:
    - «Lote 7f3c2a91 · Rodando», com foco no título.
    - BTC Sucesso / NVDA Coletando histórico («página 7 de 20», `<progress 7/20>`) / SPY Na fila.
    - Chip de classe + moeda por ativo; ícone + texto por estado.
    - Linha viva `role=status aria-live=polite` só com «NVDA: coletando histórico.».
    - `role=progressbar` 1/3; «1 de 3 ativos · … · resta ~».
    - BTC «Favorito gravado … abrir em Favoritos».
  - C8: o painel vira cartões abaixo de 620 px (mob nas duas páginas e desk da Otimização). No desk do Combo fica em colunas.
  - C9 e C9b: filtro por estado só com os estados presentes e as contagens; «Na fila» → SPY, `aria-pressed`, foco no chip.
  - C10 a C10f, Pausar:
    - Pausar e Encerrar com 44 px.
    - «Pausando…» com os dois botões desabilitados e a linha viva «Pausa pedida… NVDA».
    - Depois, «Pausado» no mesmo lote: BTC mantém Sucesso e NVDA volta a «Na fila · histórico coletado; otimiza ao retomar».
    - Foco em Retomar; link para os favoritos já gravados.
  - C11: Retomar põe Rodando de novo e NVDA Otimizando «na mesma amostra».
  - C12 a C12g, Concluído:
    - NVDA e SPY «Sucesso · precisão diária» com o trecho.
    - Nota âmbar «Precisão diária em 2 ativos».
    - «Lote concluído: 3 de 3 … 3 favorito(s) gravado(s) (2 com precisão diária)».
    - Link «Ver os 3 resultados do lote em Favoritos». **Seguindo o link de verdade**, Favoritos abre com `?lote=` e só os 3 do lote.
    - No Combo fica também «Descoberta sistemática».
  - C13: Encerrar dá «Encerrado»; BTC mantém Sucesso, NVDA e SPY ficam «Não rodou» e o favorito fica.
  - C14 a C14g, **5m pelo select de Timeframe**:
    - Texto «Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — … use 15m, 1h, 4h ou 1d.», com o trecho de fora em âmbar.
    - Confirmar com «1 cripto (USDT): BTC/USDT», «0 de 1» e fora «NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m.».
    - Painel com NVDA e SPY «Fora» antes de começar; meta «0 de 1»; BTC conclui.
  - C16 a C16f, lote grande (só Combo):
    - «Lote de 2.431 ativos», sem limite.
    - Confirmar com «2.388 de 2.431», sem segunda confirmação.
    - 50 linhas, «Mostrar mais 50 · 50 de 2.431» → 100, com foco no botão.
    - O lote pausa.
  - C17 a C17h, «Lote com problemas»:
    - Os 7 estados: Sucesso, Sucesso · precisão diária, Insuficiente, Rejeitado, Falha, Pulado, Fora.
    - «Nenhum favorito gravado» em insuficiente, rejeitado e falha, cada um com o motivo (candles, walk-forward, histórico indisponível, já nos favoritos, suspenso).
    - Resumo «2 favorito(s) gravado(s) (1 com precisão diária) · sem resultado válido: 3».
    - Ícone distinto por estado e tons vermelho/âmbar.
    - Filtro Falha → SPY; «Ver os 2 resultados».
  - **FAIL d/m:**
    - C7i e C7j: «Sucesso» e o chip ETF sem verde (P3-2).
    - C7k: a linha viva é um nó novo a cada render (P3-5).
    - C13b: o foco cai no `body` depois de Encerrar (P3-4).
    - C14i e C14j: em 1m (Combo) e em 30m (Otimização), o texto antes de rodar cita o tempo certo, mas o Confirmar e o motivo por ativo dizem «5m», e a Configuração diz «5m» (P3-3).
    - C15: Otimização em 15m roda NVDA/SPY normalmente, contra a decisão 4 (P2-1).
    - C15b: a Configuração do Confirmar diz «1d» em 15m (P3-3).

Caminhada de teclado completa em página nova (`tabwalk.py`): `index` 66/57, `configure` 47/38, `optimize` 46/37 paradas (desk/mob), e o mesmo com o painel do lote aberto. **0 paradas sem anel**, COPIED ou DELTA, e o foco nunca sai da área visível. Alvos DELTA abaixo de 24 px:

- o link inline «abrir em Favoritos», dentro do texto e isento pela 2.5.8;
- o select de Timeframe, com 20 px. Ele usa as classes vivas, e o padding é zerado pelo reset `*` sem layer do `index.css` vivo. É herdado, igual ao vivo.

O que se vê nos screenshots:

- **Desk:**
  - Favoritos no shell vivo (sidebar), com a faixa de filtros em 6 colunas: Classe | Symbol | Strategy | Time | Direção | Ordenar.
  - Sob o símbolo, o chip «Ação» azul / «Cripto» amarelo / «ETF» verde, seguido da moeda.
  - No bloco da estratégia: «Atualização diária: ainda não…», a precisão (âmbar com ⚠ ou azul com ⓘ), as convenções, as limitações, o período efetivo e «Gerado em lote». As linhas ficam altas (≈ 260 px em NVDA/SPY), o que já está aceito como P3 do design.md.
  - Combo: o painel do lote abaixo de Otimizar, em colunas.
  - Otimização: o painel em cartões na coluna estreita; à direita continua «Ready to Optimize / Select a strategy template» (P2-4).
- **Mob:** filtros empilhados (Classe primeiro), cartões com «Ação · USD», painel em cartões, chips de estado quebrando linha, sem rolagem horizontal.
- **Os dois viewports do Combo:** o botão «Ver logs» mostra `title="Ver logs do backend (últimas linhas)">Ver logs` (P3-1).

## 5. Confronto com o Entra (só o visível; backend = Apply)

| Entra | Visto no browser | Disposition |
|---|---|---|
| Lote misto pelo catálogo; cada ativo com classe, fonte, sessão, ajuste e moeda guardados no resultado | Seleção BTC/USDT+NVDA+SPY; Confirmar por classe e moeda; Favoritos com convenções por linha (R3) | PASS. «Market Data: CCXT» no Combo com seleção mista é P2-3. |
| Mesmas regras do backtest individual (#1119) | Convenções e precisão iguais às do #1119 nos favoritos; o comportamento é Apply | PASS (visível). A regra de cobertura da decisão 4 na Otimização é P2-1. |
| Tempo que não serve: ação/ETF fora com motivo antes de começar, criptos rodam | C14 a C14g (5m): texto, Confirmar, «Fora» e BTC conclui | PASS. Em 1m/30m o motivo diz «5m» (P3-3). |
| Lote grande: qualquer tamanho, contagem de coleta antes de confirmar, progresso por ativo, pausa/cancelamento | C5e «2 de 3», C16 «2.388 de 2.431», «página 7 de 20» com `<progress>`, Pausar/Encerrar | PASS. P2-2 sobre o que conta como «precisa». |
| Estado por ativo: progresso, sucesso, insuficiência, rejeição e falha; problema não vira válido nem para os demais | C17 a C17h: 7 estados com motivo, «Nenhum favorito gravado», demais concluem | PASS |
| Precisão diária visível com o trecho, nunca em silêncio | Painel (C12, nota âmbar) e Favoritos (R2 a R2c) | PASS |
| Mesma amostra; pausa, cancelamento e retomada preservam concluídos e identidade | «todas na mesma amostra», C10d (mesmo id, BTC mantido), C11, C13 | PASS. Reabrir o lote ativo (`/batch/active`) não tem estado prototipado, mas é comportamento de Apply. |
| Resultado vira favorito «gerado em lote» para ação/ETF como para cripto | C12d e C12g → Favoritos `?lote=` com NVDA/SPY/BTC e «Gerado em lote 7f3c2a91» | PASS |
| Lista única ordenável, com classe, moeda (USD/USDT nunca juntos) e convenções por linha, e filtro por classe | F0b, R1 a R1c, R3, F1 a F3b | PASS. Os outros filtros vivos não estão ligados no protótipo (P3-6). |
| Verificação: BTC/USDT+NVDA+ETF gera favoritos com período efetivo, precisão e limitações; com 5m NVDA/ETF ficam fora e BTC roda; regressão cripto | C12g + R2/R4/R5; C14 a C14g; a regressão cripto é teste de contrato (decisão 15), sem tela própria | PASS |
| Não entra: Descoberta, atualização/alertas de ação/ETF, benchmark/exportação | Nenhum controle novo; «Atualização diária: ainda não para ações e ETFs»; «Exportar» é o vivo | PASS |

## 6. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Linha viva curta, barra, selo e estado por ativo. Na Otimização, a coluna larga diz «Ready to Optimize» enquanto o lote roda. | P2 |
| 2 | Match com o mundo | «Coletando histórico · página 7 de 20», «histórico coletado; otimiza ao retomar» | — |
| 4 | Consistência | Verde de Sucesso/ETF some fora de Favoritos. «Período: 15 dias» no select contra «todo o histórico» no Confirmar. | P3 |
| 5 | Prevenção de erro | Confirmar no fluxo com quem fica fora e por quê; sem segunda confirmação (decisão de Alan) | — |
| 6 | Reconhecimento | Chip de classe + moeda colado ao símbolo em toda superfície | — |
| 9 | Recuperação | Falha com motivo e «rode de novo mais tarde»; Encerrar mantém favoritos | — |

## 7. Achados

### P0: nenhum

### P1: nenhum

Nenhum assert ligado a um critério do Entra falhou. Os 30 FAIL são todos do protótipo ou de estados derivados do design.md.

### P2 (não bloqueiam; juízo de Alan ou do único rework)

- **P2-1 A Otimização em 15m/1h/4h contradiz a decisão 4.** *Produto, juízo.* Fica em `optimize.html`, ao trocar o Timeframe para 15m. Pela decisão 4 (e pelo Risks: «quase sempre ficam fora»), NVDA e SPY deveriam sair antes de começar, porque o 5m deles começa em mai. 2026, depois da janela fixa de jan. 2024. O protótipo mostra o contrário: «Lote de 3 ativos (1 cripto, 1 ação, 1 ETF)», e o Confirmar diz «1d». A nota da classe também só cita «1m, 5m e 30m». **Corrigir:** prototipar o estado «Fora: NVDA (Ação), SPY (ETF) — sem 15m/5m na janela fixa (começam em 19 mai. 2026); use 1d» e citar a regra na nota da Otimização. A alternativa é Alan aceitar que o Apply defina o texto.
- **P2-2 A contagem de coleta pode inflar.** *Produto, juízo.* Fica em `configure.html`, no Confirmar. NVDA conta como «precisa de coleta (5m do intrabar)», mas o próprio seletor diz «5m e 15m desde 19 mai. 2026 · sem lacunas · atualizado 24 out., 21:00». Pela regra da decisão 4 («compara a cobertura com a janela pedida»), toda ação com janela «todo o histórico» sempre «precisa», porque a Binance não tem 5m antes de 2026. O número que o Entra manda mostrar antes de confirmar («quantos ainda precisam de coleta») vira «quase todos», e no lote grande sai «2.388 de 2.431». **Corrigir:** definir `needs_collection` contra o que a Binance tem (início da série no catálogo até agora), não contra a janela pedida, e ajustar a amostra (NVDA sem coleta, ou com coleta só do trecho novo).
- **P2-3 «Market Data: CCXT (crypto exchange data)» com seleção mista.** *Produto, juízo.* Fica em `configure.html` e é COPIED. O Entra pede «cada ativo roda com a sua … fonte», e a decisão 3 tira `_ensure_crypto_data_source` do lote, mas o campo continua dizendo CCXT para o lote todo. **Corrigir:** dizer na decisão 6 o que o campo mostra no lote misto (p.ex. «Por ativo: CCXT para cripto, Binance Ações para ação e ETF») e pôr no protótipo.
- **P2-4 A Otimização fica com «Select Strategy…» e «Ready to Optimize» ao lado do lote rodando.** *Produto, juízo.* Fica em `optimize.html`, desk e mob. O select de template mostra o placeholder, mas o lote roda «Médias: tendência». A coluna larga da direita continua com «Ready to Optimize · Select a strategy template…» enquanto o painel do lote se espreme em cartões na coluna estreita. **Corrigir:** capturar com o template escolhido, e decidir se o painel do lote ocupa a coluna de resultado (onde hoje fica o «Ready»). Outra saída é a coluna de resultado dizer «Lote em andamento: acompanhe ao lado».

### P3 (aceitos: Apply, protótipo, herdado; não reabrir como P0/P1)

- **P3-1 Marcador dentro de tag quebra o «Ver logs».** *Mecânico, barato no rework.* Em `configure.html` l.39, `<!-- COPIED:end -->` e `<!-- DELTA:start confirmar lote … -->` ficaram dentro de `<button … title=…>`. O botão vivo «Ver logs» mostra o texto cru `title="Ver logs do backend (últimas linhas)">Ver logs`, nos dois viewports. O gate do autor (230/230) não pegou. **Corrigir:** mover os marcadores para depois do `</button>`.
- **P3-2 `--fav-up` fora de escopo no Combo e na Otimização.** *Mecânico, defeito do delta.* O token só existe em `.favorites-workbench`, e os usos estão em `delta.css` l.24, l.109 e l.137. Fora de Favoritos, «Sucesso», o selo «Concluído» e o chip ETF saem em cinza, e o verde só aparece nos Favoritos. Ícone + texto seguem distinguindo. **Corrigir:** `var(--fav-up, #0ecb81)` ou um token de `:root`. No Apply, usar o token de sucesso global.
- **P3-3 Texto fixo da amostra no Confirmar.** *Mecânico.* Em 1m (Combo) e 30m (Otimização), o Confirmar diz «não rodam em 5m», a Configuração diz «· 5m ·» e o motivo por ativo diz «não roda em 5m». Em 15m a Configuração diz «· 1d ·». No Combo, a Configuração diz «todo o histórico» enquanto o select Período mostra «15 dias». O texto do contrato (decisão 6) deve usar o tempo e o período escolhidos.
- **P3-4 O foco cai no `body` depois de Encerrar.** *Mecânico, a11y do protótipo.* O `render()` recria o `<h3>` sem `tabindex=-1` e o `focus()` não pega. O Apply deve mandar o foco ao título ou ao resumo depois de Encerrar, como já faz no Pausado (Retomar).
- **P3-5 A linha viva é recriada a cada render.** *Detalhe de Apply.* O `role=status` sai e volta via `innerHTML`, e leitores de tela podem não anunciar. O Apply mantém o nó estável e troca só o texto.
- **P3-6 Filtros Symbol/Strategy/Time/Direção sem ligação no protótipo.** *Mecânico.* Só Classe e Ordenar funcionam. O contrato («"N filtradas" e o rodapé seguem os filtros») vale para todos no Apply.
- **P3-7 A contagem do detector no `design.md` está errada para o `index.html`.** *Mecânico.* O design.md diz «`index.html` 2»; o CLI dá **9** (8 `gray-on-color` das estrelas vivas + 1 `flat-type-hierarchy`). Provavelmente o autor contou regras, não achados. `configure` 11 e `optimize` 5 batem. Todos são COPIED.
- **P3-8 Achados do incumbente clonado.** *Herdado.*
  - HTML: 25 no CLI e +9 `design-system-font-size` do AppNav no modo hook.
  - `live.css`: 39 no CLI e 335 no modo hook.
  - O select de Timeframe tem 20 px de altura pelo reset `*` sem layer do vivo.

  Nada disso está no delta, e tudo fica fora do card. Já está aceito no design.md.
- **P3-9 `parse_live_route` captura a linha seguinte (`surface: existing`) como justificativa.** *Processo.* A regex `\s+` atravessa a quebra de linha. É inofensivo com rota de catálogo, mas vale abrir item próprio fora do card.
- **P3-10 Amostra (já aceito no design.md).** O ATR de ETH/SOL é igual ao do BTC (1834.20). SOL tem apelido «(batch)» sem lote. Os formatos de número e data são misturados.

Mecânicos/Apply: P3-1 a P3-10. Juízo: P2-1 a P2-4.

## 8. Veredito

**PASS com P2-P3.** P0 e P1 zerados.

- **Digests:** batem nos 6 arquivos, do disco ao HTTPS e ao browser, e com a tabela do design.md.
- **Gate estático:** passa (`clone_gate_ok=True`, `classify(index,/favorites)=PASS`, copied 82525).
- **Detector:** 0 achados no DELTA nos dois modos; os 25 achados de HTML no CLI são todos COPIED.
- **Browser:** 404/434 asserts. Todos os critérios visíveis do Entra estão cobertos e passam em 1440 e 390:
  - lote misto;
  - 5m tira ação/ETF com motivo e roda BTC;
  - contagem de coleta antes de confirmar, inclusive com 2.431;
  - progresso por ativo com os 7 estados;
  - pausa, retomar e encerrar no mesmo lote;
  - precisão diária marcada no painel e em Favoritos;
  - lista única ordenável com classe, moeda e filtro por classe;
  - favoritos do lote abertos pelo link.

  Sem erros de console ou rede, sem rolagem horizontal, foco visível em todas as paradas.

Disposition: nenhum rework é obrigatório. Os P2 cabem no único rework do teto, ou viram nota na Aprovação de Design:

- P2-1 e P2-2 tocam estados e contagem do Entra e merecem texto ou estado no pacote.
- P2-3 e P2-4 são escolhas de tela.

P3-1, P3-2 e P3-3 são baratos se houver rework. Os demais P3 ficam aceitos para o Apply.

## 9. Referências

- Disco: `frontend/public/prototypes/card-1120-lote-multiclasse/{index,configure,optimize}.html`, `live.css`, `delta.css`, `delta.js`
- HTTPS DEV: https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/ (+ `configure.html`, `optimize.html`)
- Viewports 1440×900 e 390×844 · `colorScheme: dark` · `locale: pt-BR` · contexto novo por página × viewport × cenário
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` (CLI) e `hook-lib.loadDetector` + `designSystemOptions(…, REPO)` + `detectText` (modo hook, sem escrever cache)
- Gate: `scripts/process-fsm/design_clone_gate.py` + `scripts/process-fsm/route-landmarks.yaml` (HEAD `e762e470`)
- Scratchpad (não versionado): `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/f34a4e0e-5dff-4fe2-9a98-4a3fda87bbb1/scratchpad/1120/B/`, com:
  - scripts: `browser.py`, `tabwalk.py`, `extra.py`, `gate.py`, `classify.py`, `hookmode.mjs`, `det.sh`;
  - saídas: `asserts.json`, `tabwalk.json`, `det-*.json`, `hookmode.json`, `shots/` (56 PNG).

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
