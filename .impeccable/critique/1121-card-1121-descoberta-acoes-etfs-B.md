> Proveniência: Assessment B (detector + browser real), papel `assessment-b`, faixa `juizo`, modelo da captura **Opus 5.5** (`claude-opus-5-5`, effort `high`), captura `assessment-b-1121-a2.capture.json` (attempt `ace2400b-4b64-476f-a17a-91c4656f7b04`), wave `assessment-a-1121-a2.capture.json`, birth `ace2400b-4b64-476f-a17a-91c4656f7b04.birth.json`, 2026-10-26T01:47Z.

# Assessment B (detector + browser real): card 1121 · change card-1121-descoberta-acoes-etfs

> Assessor B isolado. Não vi o transcript do pai nem o de A. O snapshot A (`1121-…-A.md`) existe na pasta e **não** foi lido. Não houve nested-spawn. Cliente Claude Code (adapter cooperativo, sem modo Auto).
> Este filho escreveu este snapshot e screenshots `card-1121-B-*.png` nesta pasta. Scripts e JSON ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/a6864850-8db3-4162-8fa9-5cbe144d5d69/scratchpad/c1121-b/` e não são versionados.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`, nas linhas 1 a 3, cada um em linha própria. A lista de regiões clonadas (COPIED) e a de DELTA estão em Context; os P3 aceitos estão em Risks / Trade-offs.

```
Assessment B 1121
snapshot: .impeccable/critique/1121-card-1121-descoberta-acoes-etfs-B.md (2026-10-26T01:47Z)
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == HTTPS (curl) == corpo da navegação no browser, IDENTICAL em index.html/live.css/delta.css/delta.js; live.css == /assets/index-BKQOezYM.css vivo (sha 876e5fe6…); design.md cbb94a72… igual antes e depois
detector CLI: index 0 · delta.css 0 · delta.js 0 · live.css 39 · hook (DESIGN.md): 0 · 0 · 0 · 331
detector browser (injetado nos 4 modos + 3 cenários): únicos desk COPIED 93 × DELTA 14 · mob COPIED 86 × DELTA 11; dos DELTA, 3 de autoria do delta (1 tamanho + 2 line-length, desk), 3 do painel Demonstração, 8 herdam estilo vivo
gate: design_token_gap=None · evaluate_clone_gate(HEAD)=True · landmarks(/combo/discovery)=True · copied_utf8_sum=70236 · classify=PASS · clone_gate_ok=True · 38/38 COPIED · 38/38 DELTA · 0 marcador dentro de tag
clone vs vivo (DEV com API simulada, testid/id fora do DELTA): Montar 37 iguais/0 diferentes · Acompanhando 15/1 (dado) · Decidir 22/1 (dado) · Modal 16/0
browser: 280 asserts, 271 PASS, 9 FAIL (7 de harness, re-testados PASS; 2 reais = P2-3) + 32 verificações extras · 0 console error / pageerror / ≥400 / requestfailed · Tab: 6 caminhadas, 0 parada sem anel
P0: nenhum
P1: nenhum
P2: [produto, juízo] falha some da vista no fim (salto ao Decidir) · [produto, juízo] densidade da linha do candidato · [mecânico] período passado: 4 sucessos no contador, 3 linhas válidas no Decidir
P3: [mecânico] «Destino obrigatório» 9,6 px · [mecânico] «em execução» fixo no Decidir terminal · [Apply] nota do teto duplica `over-limit-note` · [mecânico] foco no body após confirmar cancelamento · [amostra] id «RS-NVDD4121E5» · [polish] line-length das notas · [polish] «·» órfão na linha da classe · [herdado] Promover cortado a 1440, selects de 18 px, padding zerado, achados COPIED · [processo] parse_live_route
verdict: PASS com rework (leve, opcional dentro do teto)
```

- UTC: 2026-10-26T01:47Z
- Tupla (só leitura):
  - `bound_card=1121`
  - `q_git=card-1121-descoberta-acoes-etfs` @ `5bd1695f`
  - Status=**Design**, conferido via GraphQL do Project, sem mudança.
- Pacote não commitado: `git status` mostra o protótipo, a change e o snapshot A como `??`.
- Não houve `process_event`, commit, push, Gist, comentário nem restart.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1121 --jq .body` (sem `gh issue view`). Body grelhado com 9 itens no Entra (4 decisões de Alan de 26/10/2026) e 2 no Não entra. As decisões não foram reabertas.

## 1. Digest servido == local

| Arquivo | sha256 (disco = HTTPS curl = browser) | bytes |
|---|---|---|
| `index.html` (a pasta `/` serve o mesmo) | `46f32c0f17d787a13552235d75d15946a10fa79baa1f51b107f6d7a65e5204d2` | 88165 |
| `live.css` | `876e5fe61e1b444bbf20e81ba5b05aeaf01577ef260b228df9a2eddcf0424b2a` (= `index-BKQOezYM.css` servido hoje em DEV) | 241100 |
| `delta.css` | `1e920760eda8c3c0ad2fdbc4f9eed10742c3d07ab6dd7e0a6fc7612a9964767d` | 9003 |
| `delta.js` | `5e162462943c0f2ca3296c5129107d10327e2f874aa6a018a29b39aa72eaf904` | 36257 |

Os bytes batem com a tabela de Prototype Validation do design.md. O risco «URL pública responde 404 até o pai reiniciar o serviço» não vale mais: a URL pública responde 200 com o mesmo sha.

## 2. Detector Impeccable

### 2a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json <arquivo>`, cwd = worktree; com e sem `--no-config --no-inline-ignores`)

| Alvo | exit | Achados |
|---|---|---|
| `index.html` | 0 | `[]` (o motor estático não acha nada no HTML clonado) |
| `delta.css` | 0 | `[]` |
| `delta.js` | 0 | `[]` |
| `live.css` | 2 | 39: 24 `gray-on-color`, 6 `ai-color-palette`, 4 `side-tab`, 2 `overused-font`, 1 `border-accent-on-rounded`, 1 `gradient-text`, 1 `layout-transition`. CSS vivo inteiro, COPIED. |

O modo URL do CLI pede `puppeteer`, que não está instalado. Por isso a varredura de página foi feita injetando `detect-antipatterns-browser.js` (o mesmo script que o modo URL injeta) via Playwright (2c).

### 2b. Modo hook (DESIGN.md da raiz; `hook-lib.loadDetector` + `readConfig` + `designSystemOptions(…, REPO)`; `detectHtml`/`detectText`, sem escrever cache)

`index.html` 0 · `delta.css` 0 · `delta.js` 0 · `live.css` 331 (os 39 do CLI + 252 `design-system-color`, 20 `design-system-font-size`, 16 `design-system-radius`, 4 `design-system-font`). O `delta.css` só usa `var(--…)` de `:root`: `--ap-info-*`, `--ap-warn-*` e `--ap-danger-*` estão em `:root` no `live.css`. O verde do ETF usa `var(--fav-up, #0ecb81)` com fallback (`--fav-up` só existe em `.favorites-workbench`), e o browser mediu `rgb(14,203,129)` no chip ETF e em «Concluído». O defeito P3-2 do #1120 não se repete.

### 2c. Detector no browser (`window.impeccableDetect({serialize:false})`; cada elemento classificado pelo marcador `COPIED`/`DELTA` anterior a ele no DOM; nó criado pelo `delta.js` depois da carga = DELTA-js)

Estados varridos em 1440 e 390: Montar (misto, passado, teto), Acompanhando (etapa 1, falha), Decidir (misto, passado) e modal NVDA. Achados únicos (tipo + seletor + detalhe):

| Viewport | COPIED | DELTA |
|---|---|---|
| 1440 | 93 (31 `undersized-ui-text`, 20 `tiny-text`, 13 `cramped-padding`, 12 `low-contrast`, 6 `line-length`, 6 `nested-cards` e mais 5 avulsos) | 14 |
| 390 | 86 (mesmo perfil + 5 `text-occlusion`, 1 `body-text-viewport-edge`) | 11 |

Os 14 achados DELTA a 1440 se dividem assim:

- **Autoria do delta (contam): 3.**
  - `.d21-dest small` «Destino obrigatório» com 9,6 px (P3-1).
  - `line-length` em `.d21-assets-head p` (~189 caracteres por linha) e em `.d21-lb-note` (~196) a 1440 (P3-6). Somem a 390.
- **Painel Demonstração (só protótipo): 3.** Os botões têm `padding` vertical 0 (mas `min-height: 44px`), e o `<p>` tem 171 caracteres por linha.
- **Herdam estilo vivo (P3 herdado): 8.**
  - O `<span>` do DELTA dentro do chip vivo `preflight-state` (10 px: «Pronto para iniciar», «Bloqueado — veja o que falta»), do `leaderboard-meta` (10 px) e do `preflight-breakdown` (11 px).
  - «Data Inicial» e «Data Final» com `text-xs`, que é 10 px no token vivo, iguais ao JSX vivo (`DiscoveryPage.tsx:2302`).
  - «Excluir» a 10 px nas linhas insuficientes, que são clones da linha viva.

Nenhum achado `low-contrast` no DELTA. Nenhum `script-error`.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py` importado; `clone_gate_ok` é o que `process_event.files_g_design` chama)

```
lines1-3 ['UI impact: affected', 'live_route: /combo/discovery', 'surface: existing']
design_token_gap None
parse_ui_impact affected
parse_live_route ('/combo/discovery', 'surface: existing')
parse_surface existing
catalog has route True          (load_head_catalog: texts "Descoberta de estratégias swing", "Preflight", "Rascunho de varredura"; selectors [])
canonical len 88165
landmarks_match True
copied_utf8_sum 70236
classify PASS
clone_gate_ok True
COPIED start/end 38 38 DELTA 38 38
delta_utf8_sum 12978
markers inside tag 0
```

Os números batem com o design.md (70.236 / 12.978 / 88.165; 38/38). `parse_live_route` continua levando a linha seguinte como «justificativa» (P3-9, processo, inofensivo com rota de catálogo).

## 4. Clone contra a página viva (fora do DELTA)

- `live.css` é byte-idêntico ao CSS servido hoje (`/assets/index-BKQOezYM.css`).
- A página viva `https://dev.criptofarol.com.br/combo/discovery` foi renderizada com a API simulada (auth, templates, catálogo com BTC/USDT, NVDA e SPY, Preflight com a resposta de hoje, sweep `c1121mix` com 3 resultados).
- Para cada elemento visível com `data-testid`/`id` em cada modo, comparei tag e classes (sem as `d21-*`) com o elemento do protótipo de mesma chave:

| Modo | Iguais | Classe/tag diferente | Só no protótipo | Só no vivo |
|---|---|---|---|---|
| Montar (com template, BTC/USDT+NVDA+SPY, 1d, Todo o histórico) | 37 | 0 | `preflight-classes`, `survivorship-note` (DELTA); `#pick…EQ_MSFT` (dado da lista) | `preflight-class-out` «Fora desta varredura: 2 ativos» (o que o DELTA substitui); `#pick…EQ_NVDA` (dado) |
| Acompanhando | 15 | `partial-return-1` (`positive` × `na`: dado do mock) | `sweep-assets`, `#d21-live`, `#d21-asset-list`, `d21-precision` (DELTA) | — |
| Decidir | 22 | `decidir-return-1` (dado) | `survivorship-decidir`, `class-filter`, `class-copy`, `d21-precision` (DELTA) | — |
| Modal | 16 | 0 | `d21-precision` (DELTA) | — |

O `mode-*` aparece como «só protótipo» nos três modos por artefato do recorte (no vivo, o `tabpanel` é a própria raiz). Fora do DELTA, só divergem dado e estado. A 390 px, o resultado é o mesmo.

A mesma renderização mostra que o vivo, a 1440, já corta a coluna Ação: a tabela tem 1240 px num contêiner de 1175 px com `overflow-x:auto`, e o Promover termina em x=1477 com a borda em 1420. O protótipo dá os mesmos números com e sem o bloco do delta (P3-8, herdado).

## 5. Browser real

- Playwright Python 1.62 + Chromium headless shell 1243, `--no-sandbox`, `colorScheme: dark`, `locale: pt-BR`, fuso São Paulo.
- **URL pública** `https://dev.criptofarol.com.br/prototypes/card-1121-descoberta-acoes-etfs/`.
- 1440×900 (desk) e 390×844 (mob, `isMobile`, toque, DPR 2), com contexto novo por cenário: misto, período passado, teto, falha e cancelar.
- Scripts `browser.py`, `extra.py`, `extra2.py`, `overflow2.py`, `live.py` e `gate.py`. Os PNG estão nesta pasta com o prefixo `card-1121-B-`: 20 do protótipo e 6 do vivo simulado.

Erros: **0** `console.error`, **0** `pageerror`, **0** respostas ≥ 400 e **0** `requestfailed` nos 10 contextos. O logo `/brand/…` carrega no domínio DEV. Os ids do DOM são únicos.

### Matriz

| Cenário × viewport | Asserts | PASS | FAIL |
|---|---|---|---|
| Misto desk / mob | 94 / 94 | 92 / 91 | 2 / 3 → harness |
| Período passado desk / mob | 20 / 20 | 19 / 19 | 1 / 1 → **P2-3** |
| Teto desk / mob | 12 / 12 | 12 / 12 | 0 |
| Falha desk / mob | 7 / 7 | 6 / 6 | 1 / 1 → harness (timing) |
| Cancelar desk / mob | 7 / 7 | 7 / 7 | 0 |
| **Total** | **280** | **271** | **9** |

Os 7 FAIL de harness foram re-testados em `extra.py`/`extra2.py` (32 verificações) e passam:

- «nome acessível»: o `innerText` volta «CLASSE» por causa do `uppercase`. `getByRole('combobox', {name: /Classe/})` acha 1.
- «Tab preso no modal»: o teste começava com o foco no `body`. A partir do confirmar, 14 Tab e 14 Shift+Tab ficam no `#promotion-modal`.
- «faixa 1 trilha no móvel»: a expectativa estava errada. A faixa viva é `grid-cols-2` abaixo de 768 px (COPIED).
- «falha» (timing): o salto ao Decidir em ~404 ms escondeu o painel antes do screenshot. Re-testado: SPY fora do ranking, «Todas (2) · Cripto (1) · Ações (1) · ETFs (0)».

**Misto (decisões 2, 7, 9, 10, 11 e 12), todos PASS d/m:**

- **Montar:**
  - Sem «a Descoberta vem depois», sem «rodam só com cripto», sem «Inclua ao menos 1 par cripto».
  - Nota da classe com o texto exato da decisão 2; «Histórico sob demanda · coletado ao rodar a varredura» nas linhas sob demanda.
  - Chips BTC/USDT, NVDA e SPY; «3 selecionados · 1 cripto · 1 ação · 1 ETF».
  - Preflight:
    - «Pronto para iniciar» e total 3;
    - «Vão rodar 3 ativos: 1 cripto (USDT) · 1 ação · 1 ETF (USD)»;
    - «Precisam de coleta de histórico: 1 de 3 — SPY», com NVDA «já guardado» (o problema P2-2 do #1120 não se repete);
    - «Precisão diária prevista em 1d: NVDA … SPY: sem histórico guardado», em âmbar com ícone;
    - viés de sobrevivência em cinza neutro `rgb(146,154,165)` com «2 jan. 2003»;
    - teto oculto e taxa por classe.
  - «Iniciar varredura — 3, ~6min» habilitado; datas ocultas; Período «Todo o histórico».
  - Demonstração `static` no fim, sem fixed/sticky.
- **Acompanhando:**
  - Iniciar leva ao Acompanhando com o foco em `#progress-heading` e a aba «Acompanhando #c1121mix».
  - «Por ativo»:
    - começa com BTC «Rodando · 1d» e NVDA/SPY «Na fila»; chip + moeda por ativo;
    - 4 colunas no desk e cartão de 2 trilhas abaixo de 620 px;
    - linha viva `role=status aria-live=polite` só com «BTC/USDT: rodando · 1d».
  - Etapa 1:
    - BTC «Concluído» em verde, com «Precisão intrabar (15m) · período efetivo …»;
    - NVDA «Coletando histórico · 1d · página 3 de 6»;
    - Parciais só com BTC, e a linha mostra «BTC/USDT · 1d · Long» viva + chip + moeda.
  - Pausar:
    - «Varredura pausada», botão «Retomar», NVDA «Pausado na coleta · 1d · página 3 de 6 · retoma daqui»;
    - o foco fica no botão e a linha viva diz «Varredura pausada.»;
    - Avançar não anda enquanto pausado. Retomar volta a «Varredura em execução».
  - Etapa 3: NVDA «Concluído · precisão diária» em âmbar com ⚠ e «Sem 15m de 2 jan. 2003 a 31 dez. 2025». Etapa 4: SPY «Coletando histórico · 5m do intrabar · página 7 de 16». O contador «processadas =» fica.
- **Decidir:**
  - No fim, a tela vai ao Decidir com o foco em `#leaderboard-title`.
  - 3 linhas:
    - «BTC/USDT · 1d · Long · Cripto · USDT», «NVDA · 1d · Long · Ação · USD», «SPY · 1d · Long · ETF · USD»;
    - uma moeda por linha, sem USDT nas linhas USD;
    - NVDA «Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025» em `rgb(251,191,36)` com ícone; BTC «Precisão intrabar (15m)» em `rgb(147,197,253)` com ícone;
    - convenções por classe e «Período efetivo» por linha;
    - chips amarelo, azul e verde; rank 1/2/3.
  - Cabeçalho «3 classes · janela, candles e amostra em cada linha · taxa por lado: cripto 0,075% · ação e ETF 0,10%»; sobrevivência «janela desde 2 jan. 2003»; nota de cobertura por calendário.
  - Filtro Classe:
    - «Todas (3) / Cripto (1) / Ações (1) / ETFs (1)», antes de Símbolo, com 5 trilhas a 1440;
    - Ações deixa só NVDA com **rank 2** e «1 de 3»; ETFs deixa SPY com rank 3; «Limpar filtros» volta a Todas.
- **Modal:**
  - Promover NVDA abre o modal:
    - `role=dialog aria-modal=true`, título «Promover a favorito» e foco no confirmar;
    - identidade «Ação · USD · Precisão diária … · Binance Ações · NY · split · 252/ano · Período efetivo 2 jan. 2003 … · Amostra 8b41d7e2 · guardada enquanto o favorito existir · Direção Long»;
    - destino «Favoritos · sem nível de estrela» + «Monitor, Telegram e Revalidar: ainda não para ações e ETFs», com o destino tier 3 oculto; confirmar «Promover a favorito».
  - Esc, Voltar e Fechar devolvem o foco ao Promover NVDA.
  - Confirmar: «Favorito · sem estrela» + «Ver em Favoritos» (`/favorites`, 44 px), foco no estado promovido e toast `role=status`.
  - BTC: «Promover a favorito tier 3», sem destino de ação, «Amostra 3f9a0c21», e depois «Favorito tier 3» sem link.
  - O modal cabe na tela: desk 578 px em 900, mob 639 px em 844.
- Sem rolagem horizontal da página em nenhum estado (`scrollWidth ≤ clientWidth` e nenhum elemento fora sem contêiner de rolagem).

**Período passado:**

- Montar:
  - `aria-pressed`, Personalizado com 2019-01-01 e 2020-12-31 visíveis, 4h marcado;
  - «Sem candles prováveis em 4h: NVDA e SPY», total 6, sobrevivência «1 jan. 2019 – 31 dez. 2020».
- Fim:
  - NVDA e SPY «Concluído · precisão diária» com «4h: Amostra insuficiente — sem candles de 4h de … nessa janela»;
  - 2 linhas «Amostra insuficiente» com rank «—» e sem Promover; NVDA «Precisão diária · sem 15m de 2 jan. 2019 a 31 dez. 2020»; sobrevivência no Decidir com a janela.
- **FAIL d/m (P2-3):** o contador diz «4 sucesso + 2 amostra insuficiente» e BTC «2 de 2 combinações», mas o Decidir só tem 3 linhas válidas. Falta BTC 4h, e aparece «5 de 5 candidatos» com «Cripto (1)».

**Teto:**

- «Bloqueado — veja o que falta», total 2.433 e `role=alert` com «Acima do teto de 1.000 combinações» em `rgb(255,130,148)`, «2.433 combinações válidas passam do limite de 1.000: 2.433 ativos (1 cripto · 2.431 ações · 1 ETF) …», «Estreite a seleção …» e «Nenhuma varredura foi criada».
- Iniciar desabilitado; Avançar não inicia; coleta e previsão ocultas.
- Voltar ao misto reabilita Iniciar.

**Falha:**

- SPY passa de «Coletando histórico · 1d …» a «tentativa 2 de 3» e depois a «Falha: a Binance não respondeu ao histórico de SPY nas 3 tentativas», em vermelho com ícone.
- O título fica «Varredura concluída com falhas» e o contador mostra «1 falha». SPY sai do ranking.
- ~404 ms depois, a tela salta para o Decidir. Ali não há menção a SPY nem à falha (P2-1). A aba Acompanhando continua disponível e mostra a Falha.

**Cancelar:**

- A confirmação viva (`alertdialog`) abre com o foco em «Confirmar cancelamento». «Continuar» devolve o foco a Cancelar.
- Ao confirmar, NVDA e SPY ficam «Não rodou · varredura cancelada» e o título vira «Varredura cancelada».
- O foco cai no `body` até o salto ao Decidir (P3-4). O Decidir fica só com BTC.

**Teclado (`extra2.py` + `browser.py`):**

- Paradas: Montar 34 (desk) / 25 (mob); Decidir 33–44 / 24; modal 3 em ciclo.
- **0 paradas sem anel**, DELTA ou COPIED.
- No desk, Promover e Excluir focados ficam fora da área visível na horizontal: é o corte herdado (P3-8).
- O único alvo DELTA abaixo de 24 px é o select Classe (18 px, `padding` 0). Usa as classes vivas, e os três selects vivos ao lado medem os mesmos 18 px (reset `*` herdado).

**Densidade (rubrica 5):**

| Linha | sem o bloco DELTA | com o bloco |
|---|---|---|
| Decidir a 1440 | 197 px | BTC 333 · NVDA 368 · SPY 422 (+136 a +171) |
| Decidir a 390 | 583 px | 719 · 754 · 776 |

- A coluna Candidato tem 246 px a 1440. As convenções quebram («365 / dias/ano», «252/ano» sozinho) e o «·» antes da moeda fica órfão no fim da linha. O mesmo acontece no cartão «Por ativo» a 390 («BTC/USDT [Cripto] ·» / «USDT»).
- Classe, moeda, precisão e convenções aparecem em toda linha, e nunca há duas moedas (Entra).

## 6. Confronto com o Entra (só o visível; backend = Apply)

| Entra | Visto no browser | Disposition |
|---|---|---|
| Três classes na mesma varredura; cada ativo com classe, fonte, sessão, ajuste e moeda | Preflight «Vão rodar 3 ativos …», nota da classe, convenções por linha | PASS |
| Mesma amostra, sem vazamento | «Amostra 8b41d7e2 · guardada enquanto o favorito existir»; é comportamento de Apply/teste de contrato (decisões 4 e 13) | PASS (visível) |
| Precisão diária visível com o trecho; sem candles = estado explícito, nunca resultado | Previsão no Preflight; âmbar com trecho no Acompanhar, no Decidir e no modal; 4h «Amostra insuficiente» sem rank e sem Promover | PASS. A contagem do período passado é P2-3. |
| Teto 1.000 recusa e pede para estreitar | Cenário teto completo, Iniciar desabilitado | PASS. Duplicidade com `over-limit-note` é P3-3. |
| Orçamento, progresso, cancelamento e retomada; falha não vira aprovada | Coleta com página N de M, Pausar/Retomar, Cancelar «Não rodou», tentativa 2 de 3 → Falha fora do ranking | PASS. A falha some da vista no fim (P2-1). |
| Ranking numa lista só, com classe, moeda, convenções e filtro por classe; USD ≠ USDT | Decidir com 3 classes, filtro com contagem e rank global preservado, uma moeda por linha | PASS. Densidade é P2-2. |
| Candidato vira favorito como no lote; cripto como hoje | NVDA «Promover a favorito» → «Favorito · sem estrela» + «Ver em Favoritos»; BTC tier 3 | PASS. O aceite depende do #1122 (decisão de Alan). |
| Viés de sobrevivência explícito | Preflight e Decidir, cinza neutro, com a janela | PASS. A Open Question A/B segue com Alan. |
| Verificação | Misto até favorito; NVDA em todo o histórico com precisão diária; 2.433 recusado. A regressão cripto é teste de contrato | PASS |
| Não entra: ordens, novas famílias | Nenhum controle novo | PASS |

## 7. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Linha viva, estado por ativo com ícone + texto. No terminal, o salto ao Decidir esconde a falha e o cabeçalho segue «em execução». | P2/P3 |
| 4 | Consistência | Chips de classe nas cores do seletor e de Favoritos; rótulos de precisão iguais aos de Favoritos | — |
| 5 | Prevenção de erro | Teto recusa antes de criar; Iniciar desabilitado; previsão de precisão e de «sem candles» antes de iniciar | — |
| 6 | Reconhecimento | Classe + moeda coladas ao símbolo em toda superfície | — |
| 8 | Estética/minimalismo | O bloco do candidato soma de 4 a 6 linhas numa coluna de 246 px | P2 |
| 9 | Recuperação | Falha com motivo e tentativas; Cancelar mantém concluídos | — |

## 8. Achados

### P0: nenhum

### P1: nenhum

Nenhum critério do Entra falhou no browser. Os tokens da rubrica D4 estão em L1–L3 e o gate passa.

### P2 (não bloqueiam; juízo de Alan ou o único rework)

- **P2-1 A falha some da vista no fim.** *Produto, juízo.*
  - Onde: `[data-d21-panel=decidir]` (`delta.js` `renderDecidir`) e `[data-testid=leaderboard-meta]`.
  - No terminal, a página salta ao Decidir em ~400 ms. É comportamento vivo (card 852, `DiscoveryPage.tsx:1524`).
  - Com a falha de SPY, o Decidir mostra «Todas (2) · ETFs (0)» e o cabeçalho «em execução», sem dizer que SPY foi tentado e falhou. «Varredura concluída com falhas» e o estado «Falha: …» só aparecem por ~400 ms ou se o usuário voltar à aba Acompanhando.
  - O Entra («falha não vira estratégia aprovada») está cumprido, mas o estado explícito por ativo sai de cena justo no fim.
  - **Corrigir:** uma linha no Decidir, junto ao viés de sobrevivência, por exemplo «Sem resultado: SPY — Falha: a Binance não respondeu ao histórico nas 3 tentativas · ver Por ativo». Ela cobre também insuficientes de outros tempos. Alternativa: não saltar quando houver falha.
- **P2-2 Densidade da linha do candidato.** *Produto, juízo.*
  - Onde: `.d21-rowdata` no `td` Candidato do Decidir e das Parciais.
  - A linha cresce de 197 para 333–422 px a 1440 (+70 a 87%) e de 583 para 719–776 px a 390. As convenções quebram dentro da coluna de 246 px.
  - O design.md aceita como P3 «ordem das linhas do bloco do candidato», não a altura.
  - **Corrigir** (sem tirar nada do Entra): juntar em 2 linhas, «NVDA · 1d · Long · [Ação] USD · ⚠ Precisão diária (2003–2025)» e «Binance Ações · NY · split · 252/ano · 2 jan. 2003 – 23 out. 2026». Outra saída é deixar a coluna Candidato crescer. Alan pode também aceitar como está.
- **P2-3 Período passado: contagens incoerentes.** *Mecânico, barato.*
  - Onde: `delta.js` `renderDecidir`/`PAST`.
  - O cenário tem 6 combinações. O contador diz «4 sucesso + 2 amostra insuficiente» e BTC «2 de 2 combinações», mas o Decidir só tem BTC 1d, NVDA 1d e SPY 1d. Falta BTC 4h, e aparecem «5 de 5 candidatos» e «Cripto (1)».
  - **Corrigir:** gerar a linha BTC 4h no cenário passado (como `insufficientRow`, mas elegível), ou ajustar a linha do tempo para BTC 1 de 2.

### P3 (aceitos: Apply, protótipo, herdado; não reabrir como P0/P1)

- **P3-1 «Destino obrigatório» a 9,6 px.** *Mecânico.* Em `delta.css` `.d21-dest small`, que fica sem `font-size` e herda `smaller` de 12 px. O irmão vivo (tier 3) mede 11,2 px. **Corrigir:** igualar ao vivo (`font-size: 11.2px` ou as classes vivas `block text-[var(--text-muted)]`).
- **P3-2 Estado fixo no Decidir terminal.** *Mecânico.* O `[data-testid=leaderboard-meta]` segue «Varredura #c1121mix · em execução» depois de concluída, cancelada ou com falha (o vivo usa `STATE_LABEL[viewSweep.state]`). O chip do Acompanhar mostra `PARTIAL_FAILURE`/`COMPLETED` crus, como o vivo faz (`state.toUpperCase()`).
- **P3-3 A nota do teto duplica a do vivo no Apply.** *Detalhe de Apply.* Com `overLimit`, o vivo mostra `[data-testid=over-limit-note]` («{errors.total} Reduza templates…») no lugar da nota do escudo. No protótipo fica a nota do escudo e entra o bloco `.d21-limit`. O Apply decide se o bloco novo substitui o `over-limit-note`, para não haver duas recusas.
- **P3-4 Foco no `body` depois de confirmar o cancelamento.** *Mecânico, a11y.* `closeConfirm()` foca Cancelar e o `renderAcomp` esconde Cancelar em seguida. O foco só volta com o salto ao Decidir (~400 ms). Apply: foco no título do progresso.
- **P3-5 Id de amostra «RS-NVDD4121E5».** *Amostra.* `insufficientRow` faz `replace('A1','D4')`, que pega o «A1» de «NVDA1121». Ids são amostra (aceito no design.md).
- **P3-6 Linhas longas.** *Polish.* A 1440, `.d21-assets-head p` tem ~189 caracteres por linha e `.d21-lb-note` ~196. `max-width: 75ch` resolve.
- **P3-7 «·» órfão e moeda na linha de baixo.** *Polish.* No `.d21-symline` do Decidir (desk) e no `.d21-asset` do cartão «Por ativo» (mob). Agrupar «[chip] · moeda» com `white-space: nowrap`.
- **P3-8 Herdados do incumbente (COPIED, fora do card).**
  - Coluna Ação: a tabela do Decidir e das Parciais tem 1240 px num contêiner de 1175 a 1440, então Promover e Excluir ficam cortados e, focados, fora da vista. É idêntico no vivo simulado.
  - Os selects da faixa medem 18 px com `padding` 0 (reset `*`). O select Classe (DELTA) usa as mesmas classes.
  - Os cartões do modal têm `padding` 0.
  - Os tamanhos de 10/11 px dos chips e notas vivos alcançam os `<span>` DELTA.
  - Detector: 93/86 achados únicos COPIED no browser e 39/331 no `live.css`.
  - O design.md já aceita o reset, os achados do AppNav e dos botões vivos e os selects sem ligação.
- **P3-9 `parse_live_route` captura `surface: existing` como justificativa.** *Processo.* A regex atravessa a quebra de linha. É inofensivo com rota de catálogo. Item fora do card, já apontado no #1120.

Mecânicos/Apply: P2-3 e P3-1 a P3-9. Juízo: P2-1 e P2-2.

## 9. Veredito

**PASS com rework (leve, opcional dentro do teto).** P0 e P1 zerados.

- **Gate estático:** `clone_gate_ok=True`, `classify=PASS`, copied 70.236; tokens L1–L3 conferidos.
- **Digests:** batem do disco ao HTTPS e ao browser; `live.css` igual ao CSS vivo de hoje.
- **Clone:** fora do DELTA, só dado e estado divergem do vivo.
- **Detector:** 0 achados no estático do delta. No browser, 3 achados de autoria do delta (P3-1 e P3-6), nenhum de contraste.
- **Browser:** todos os cenários da Demonstração e o modal funcionam a 1440 e 390. Sem rolagem horizontal, foco visível em todas as paradas, console limpo.

Disposition:

- P2-1 e P2-3 merecem o único rework: são baratos e tocam estados do Entra (falha visível e contagem do período passado). P3-1 e P3-5 vão junto, de graça.
- P2-2 é escolha de Alan (compactar ou aceitar).
- Sem rework, os P2 viram nota na Aprovação de Design, e os P3 ficam aceitos para o Apply.

## 10. Referências

- Disco: `frontend/public/prototypes/card-1121-descoberta-acoes-etfs/{index.html,live.css,delta.css,delta.js}`; `openspec/changes/card-1121-descoberta-acoes-etfs/design.md` (sha `cbb94a72…`)
- HTTPS DEV: https://dev.criptofarol.com.br/prototypes/card-1121-descoberta-acoes-etfs/ · vivo: https://dev.criptofarol.com.br/combo/discovery (API simulada)
- Detector:
  - CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json`;
  - hook: `hook-lib.loadDetector` + `designSystemOptions(readConfig(REPO), det, REPO)`;
  - browser: `detect-antipatterns-browser.js` injetado com `autoScan:false` e `impeccableDetect({serialize:false})`.
- Gate: `scripts/process-fsm/design_clone_gate.py` + `route-landmarks.yaml` (HEAD `5bd1695f`)
- Scratchpad (não versionado): `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/a6864850-8db3-4162-8fa9-5cbe144d5d69/scratchpad/c1121-b/`, com:
  - scripts: `gate.py`, `browser.py`, `extra.py`, `extra2.py`, `overflow2.py`, `live.py`, `hookmode.mjs`;
  - saídas: `asserts.json`, `extra.json`, `detect-browser.json`, `tabwalk.json`, `errors.json`, `live-diff.json`, `hookmode.json`, `det/`.
- Screenshots: `.impeccable/critique/card-1121-B-{desk,mob}-*.png` (20) e `card-1121-B-live-{desk,mob}-*.png` (6)

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
