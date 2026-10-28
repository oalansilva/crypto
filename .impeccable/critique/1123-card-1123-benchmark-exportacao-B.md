> Proveniência: Assessment B (detector + gate estático + browser real), papel `assessment-b`, faixa `juizo`, modelo da captura **Opus 5.5** (`claude-opus-5-5`, effort `high`), captura `cf-assess-b-1123.json` (attempt `a0d799a1-352b-4982-8f7b-f115f4945fdc`, capture_sha256 `5065bbde…`), wave `cf-assess-a-1123.json`, birth `a0d799a1-352b-4982-8f7b-f115f4945fdc.birth.json`, cliente claude, superfície claude-desktop, 2026-10-27T13:59Z.

# Assessment B (detector + browser real): card 1123 · change card-1123-benchmark-exportacao

> Assessor B isolado. Não li o snapshot nem o scratch do Assessment A, e não houve nested-spawn. Cliente Claude Code (adapter cooperativo, sem modo Auto).
> Este filho escreveu só este snapshot. Scripts, JSON e os 26 screenshots ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123B/` e não são versionados.
> Nenhum servidor local foi aberto. O detector de browser foi injetado por `add_script_tag` em Chromium headless, então não existe aba `[Human]` com overlay.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/results` · `surface: existing`, nas linhas 1 a 3, cada um em linha própria. As regiões clonadas estão nomeadas logo abaixo do bloco D4. Os P3 aceitos estão em Risks / Trade-offs.

```
Assessment B 1123
snapshot: .impeccable/critique/1123-card-1123-benchmark-exportacao-B.md (2026-10-27T13:59Z)
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == HTTPS em 7/7 arquivos (HTTP 200); a pasta / serve o index.html; live.css == index-DOHmvARO.css que o /combo/results vivo referencia hoje (353ac045…); design.md 9a6235f5… igual no início e no fim
detector CLI: index 0 · favorite 0 · favorites 2 (COPIED) · discovery 0 · delta.css 0 · delta.js 0 · live.css 39 (herdado); pasta inteira 41
detector browser (4 páginas, 12 estados, 1440 e 390): autoria do delta = 5 tipos (sombra do modal, 3 line-length, 1 viewport-edge a 390); DELTA herdado 1 (10 px "3 de 3 candidatos"); DEMO só no protótipo; 0 low-contrast no delta
gate: design_token_gap=None · evaluate_clone_gate=True · clone_gate_ok=True · classify(index,/combo/results)=PASS · copied_utf8_sum 56249 · 0 marcador dentro de tag
clone vs vivo: 29/29 regiões COPIED (4 páginas) são substring literal de uma captura viva fresca
browser: gate do autor reexecutado 144/144 PASS; meus asserts 190, 188 PASS, 2 FAIL reais (P2-1) · 0 console error / pageerror / ≥400 / requestfailed · sem rolagem horizontal
P0: nenhum
P1: nenhum
P2: [contrato] seletor sem o estado "ativo indisponível, desabilitado com motivo" · [contrato, mecânico] prévia da planilha da Descoberta com 14 dos 22 campos de contexto
P3: [a11y/Apply] filtros de classe 36 px · [polish] linhas longas · [herdado] sombra do modal, 10 px, Exportar 40 px, achados COPIED · [processo] diálogo e JSON fora de marcador; discovery BLOCKED no catálogo · [demo] short, <30 dias, ETF no próprio ativo · [aceito] 365 x 365,25 na mesma tela · [Apply] números do estado pendente no DOM
verdict: PASS com rework (leve, opcional dentro do teto)
```

- UTC: 2026-10-27T13:50Z a 13:59Z.
- Tupla (só leitura): `bound_card=1123` · `q_git=card-1123-benchmark-exportacao` @ `9b83d25e` · Status=**Design**, conforme o prompt do pai.
- Pacote não commitado: o protótipo e a change estão `??`.
- Não houve `process_event`, commit, push, Gist, comentário nem restart.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1123 --jq .body`, sem `gh issue view`. O body grelhado tem 9 itens no Entra (4 decisões de Alan de 27/10/2026) e 4 no Não entra. As decisões não foram reabertas. A única pergunta aberta do design.md é o mínimo de 30 dias.

## 1. Digest servido == local

| Arquivo | sha256 (disco = HTTPS) | bytes |
|---|---|---|
| `index.html` (a pasta `/` serve o mesmo) | `a739f5787d80dbf521d315a5cb637552e1ccd61e314ca234867e891104866df4` | 72364 |
| `favorite.html` | `378044d31488b108c3aa51dacd66bb1d3aa7d5a727e332d351514e1bb18fe769` | 66551 |
| `favorites.html` | `f34ce6026aeebd627e528c95e2c4ffc28fc37218635273399dbbbf75c862c38e` | 95694 |
| `discovery.html` | `d4642588271663f27249874ee3e524de1397c19fc1f5dc89d3fce8ff078cb42e` | 44786 |
| `live.css` | `353ac045db2df0a13512af6bc3268d64eb4ad256a821969eb7c8118b1ba832f6` (= `/assets/index-DOHmvARO.css`; o `/combo/results` vivo referencia `index-C9_PkDmo.js` + `index-DOHmvARO.css`) | 254138 |
| `delta.css` | `6893f4308bc2270b33c712ceb115ba4041e38c345f83baf6f68fb5c7c1950718` | 12880 |
| `delta.js` | `ac7ef49362e953c5725f676c63465ebaf95d898fd7d6bfaa5c192369e9ea1a67` | 13140 |

- Os 7 arquivos respondem HTTP 200, e os prefixos batem com a tabela de Prototype Validation do design.md.
- Conferi os digests de novo no fim e não houve mudança.

## 2. Detector Impeccable

### 2a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json`)

| Alvo | exit | Achados | Região |
|---|---|---|---|
| pasta do protótipo | 2 | 41 = 2 (`favorites.html`) + 39 (`live.css`) | — |
| `index.html` | 0 | `[]` | — |
| `favorite.html` | 0 | `[]` | — |
| `favorites.html` | 2 | 1 `gray-on-color` (`text-zinc-400` sobre `bg-amber-400`), 1 `flat-type-hierarchy` (12/14/18 px) | as duas classes só aparecem em COPIED (16 e 14 ocorrências, 0 em DELTA). São as estrelas vivas e a escala viva. |
| `discovery.html` | 0 | `[]` | — |
| `delta.css` | 0 | `[]` | — |
| `delta.js` | 0 | `[]` | — |
| `live.css` | 2 | 39: 24 `gray-on-color`, 6 `ai-color-palette`, 4 `side-tab`, 2 `overused-font`, 1 `border-accent-on-rounded`, 1 `gradient-text`, 1 `layout-transition` | CSS vivo inteiro, COPIED |

- **Delta:** 0 achados.
- **Herdado:** 41. O design.md já aceita os de `favorites.html` como P3.

### 2b. Detector no browser

Usei `detect-antipatterns-browser.js` injetado, com `impeccableDetect({serialize:false})`. Cada elemento foi classificado pelo marcador `COPIED`/`DELTA` aberto em volta dele, por classe `b23*` ou pela Demonstração. Varri estes estados a 1440 e a 390:

- canônico: carga, diálogo aberto, SPY e CRCL;
- favorito: carga e "não registrada";
- Favoritos e Descoberta: carga.

Só elementos visíveis:

| Página · estado (1440) | COPIED | DELTA | DEMO | PAGE |
|---|---|---|---|---|
| index carga / SPY | 122 | 0 | 3 | 3 |
| index diálogo | 122 | 2 | 3 | 3 |
| index CRCL | 122 | 1 | 4 | 3 |
| favorite carga / não registrada | 110 | 0 / 1 | 3 | 3 |
| favorites | 26 | 0 | 11 | 2 |
| discovery | 41 | 1 | 2 | 2 |

A 390 o padrão é o mesmo. COPIED: index 107/108, favorite 95, favorites 37, discovery 33. No DELTA há 1 `body-text-viewport-edge` no diálogo e 1 `tiny-text` na Descoberta.

Achados no DELTA:

- `gpt-thin-border-wide-shadow` em `.b23-dialog` (1 px de borda e 64 px de blur). É a sombra do modal copiada do incumbente, já aceita como P3 no design.md.
- `line-length` com cerca de 92 a 99 caracteres por linha a 1440 em três lugares: `p.b23-dlg-desc`, o motivo do CRCL e o texto "Comparação não registrada…" (P3-2).
- `body-text-viewport-edge` em `p.b23-dlg-desc` a 390. É falso positivo: o `<p>` vai até a borda da caixa, mas tem `padding: 0 20px`, e o screenshot mostra margem.
- `tiny-text` de 10 px em "3 de 3 candidatos · página 1 de 1". É o `span.text-xs` vivo, reembalado no DELTA do botão Exportar, então conta como herdado.

Os achados DEMO são `line-length` dos textos de introdução, `cramped-padding` do `.b23-sheet-wrap` e `th` de 11,2 px na prévia da planilha. Só existem no protótipo.

Não há `low-contrast` nem `undersized-ui-text` em elemento do delta. O COPIED traz os de sempre da página viva: `undersized-ui-text`, `low-contrast`, `nested-cards` e `cramped-padding`.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py` importado)

```
lines1-3 ['UI impact: affected', 'live_route: /combo/results', 'surface: existing']
design_token_gap None
parse_live_route ('/combo/results', 'surface: existing')
catalog (load_head_catalog) ['/combo/discovery', '/combo/results', '/combo/select', '/favorites', '/monitor', 'landing']
/combo/results entry: selectors ['.combo-page'], texts ['Lista de operações', 'Análise da estratégia']
evaluate_clone_gate True
clone_gate_ok True
index.html     /combo/results    landmarks True  classify PASS     copied 56249  COPIED 7 (56.200 B)  DELTA 6 (5.766 B)  inside_tag 0
favorite.html  /combo/results    landmarks True  classify PASS     copied 51912  COPIED 7 (51.863 B)  DELTA 6 (5.775 B)  inside_tag 0
favorites.html /favorites        landmarks True  classify PASS     copied 89015  COPIED 8 (88.959 B)  DELTA 7 (1.614 B)  inside_tag 0
discovery.html /combo/discovery  landmarks False classify BLOCKED  copied 39293  COPIED 7 (39.244 B)  DELTA 6 (2.522 B)  inside_tag 0
```

- O canônico passa, e `copied_utf8_sum` (56.249) é o mesmo número do design.md.
- Os bytes de COPIED e DELTA por página batem com a tabela do autor.
- `discovery.html` dá BLOCKED no `classify`: o catálogo pede "Preflight" e "Rascunho de varredura", e a captura é o Decidir. O gate só lê o canônico, então é informativo (P3-5).
- `parse_live_route` continua levando `surface: existing` como justificativa. Isso já foi visto no #1120 a #1122 (P3-5).

## 4. Clone contra a página viva (fora do DELTA)

- Reexecutei o `capture.py` do autor com saída no meu scratch (`live1/`). A API é a mesma simulada, mas o render é novo, do bundle vivo de hoje, a 1440 e a 390, sem erros de página. A folha carregada é `index-DOHmvARO.css`.
- Para cada região COPIED, testei se ela é **substring literal** de alguma captura fresca:

| Página | COPIED | Substring do vivo fresco | Substring da captura do autor |
|---|---|---|---|
| `index.html` (`/combo/results`, BTC rodada nova) | 7 | 7 | 7 |
| `favorite.html` (`/combo/results` aberto de Favoritos) | 7 | 7 | 7 |
| `favorites.html` | 8 | 8 | 8 |
| `discovery.html` (Decidir) | 7 | 7 | 7 |

- Comparei o screenshot vivo (`live1/results-btc-1440.png`) com o protótipo a 1440. Shell, cabeçalho, cartão de resumo, "Dados e execução", regras e lista de operações são os mesmos. A seção nova entra entre o cartão de resumo e "Dados e execução". O gráfico do clone fica vazio porque é `canvas`, e isso está declarado no design.md.
- Fora dos marcadores existe conteúdo no `<body>`: o diálogo "Escolher referência" e o `<script id="b23-data">`. São 9,2 KB no index, 7,7 no favorite, 3,8 em favorites e 1,9 em discovery. O design.md diz "DELTA no fim do body", mas esse trecho não tem marcador `DELTA` (P3-5). O conteúdo é todo `b23`, então não é clone escondido.
- `live.css` é byte-idêntico ao CSS vivo servido hoje. Fora do DELTA, o clone é o vivo.

## 5. Browser real

- Playwright Python com Chromium headless shell 1243, `colorScheme: dark`, `pt-BR`, fuso São Paulo.
- **URL pública:** `https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/` e as 3 páginas extras.
- Viewports: 1440×900 e 390×844 (`isMobile`, toque, DPR 2). Contexto novo por página.
- **Erros:** 0 `console.error`, 0 `pageerror`, 0 respostas ≥ 400 e 0 `requestfailed` nos 8 contextos meus e nos 2 do gate do autor.

### 5a. Gate do autor reexecutado

Copiei `c1123/gate.py` para o meu scratch, com saída das imagens no meu scratch, e rodei sem mudar nenhum assert: **144/144 PASS**, `problems: []`. Bate com o design.md.

Os asserts cobrem:

- os marcos;
- a ordem da seção;
- o padrão igual a "Retorno total";
- a armadilha de foco: 12 Tab e 3 Shift+Tab;
- os filtros ETFs e "sol";
- o Esc e o retorno do foco;
- SPY (gravando, aviso com as duas moedas, período comum, feriado de NY, retorno de preço, gravação);
- SOL (3 trades fora, Δ em queda);
- QQQ (coleta sem números);
- CRCL (sem números nem zero);
- a planilha de trades;
- a falha na coleta com "Tentar de novo";
- o favorito (SPY gravada, aviso, 2 trades fora, não registrada e "Comparar com o próprio ativo");
- Favoritos ("Ref.: SPY", "(deduzido)", "não registrado");
- a Descoberta (frase, 44 px, todas as páginas).

### 5b. Asserts próprios (`browser.py`)

| Página × viewport | Asserts | PASS | FAIL |
|---|---|---|---|
| index 1440 / 390 | 71 / 71 | 70 / 70 | 1 / 1 |
| favorite 1440 / 390 | 11 / 11 | 11 / 11 | 0 |
| favorites 1440 / 390 | 8 / 8 | 8 / 8 | 0 |
| discovery 1440 / 390 | 5 / 5 | 5 / 5 | 0 |
| **Total** | **190** | **188** | **2** |

Numa primeira rodada houve 4 FAIL de harness, corrigidos no script:

- `locator.check()` no rádio é coberto pelo rótulo; passei a clicar no `label`;
- "B&H" era procurado na tabela, mas no Decidir vivo ele está na ordenação "CAGR vs B&H".

**FAIL reais (2):** nenhuma opção do seletor está desabilitada, a 1440 e a 390. Ver P2-1.

**Canônico, PASS d/m:**

- **Ordem:** resumo → "Comparação com referência" → "Dados e execução".
- **Padrão:**
  - "BTC/USDT (próprio ativo)", com o retorno igual ao `[data-metric=return]` vivo;
  - sem aviso de moeda e sem "retorno de preço";
  - "Nada: a referência cobre o período inteiro";
  - nota do salvar presente, ao lado de "Salvar nos Favoritos".
- **Teclado:**
  - Tab até "Trocar referência" mostra o anel `2px solid rgb(59,130,246)`; o botão tem `aria-haspopup=dialog`;
  - Enter abre o seletor com o foco na busca e trava a rolagem do fundo;
  - ArrowDown no grupo de rádios seleciona SPY, e o rótulo focado ganha anel;
  - Cancelar fecha sem trocar, devolve o foco e libera a rolagem;
  - clique fora fecha (1440);
  - Enter em "Usar referência" grava, e o foco volta ao gatilho.
- **Seletor:**
  - a 1440 é um diálogo de 640×720; a 390 ocupa a tela (390×844);
  - a 1ª opção é "BTC/USDT · Padrão · Próprio ativo";
  - os filtros têm `aria-pressed`; "Ações" mostra NVDA e CRCL;
  - a busca "zzzz" mostra "Nenhum ativo do catálogo com esse texto.".
- **Alvos do diálogo:**
  - Fechar 44×44, opções 88 px, Cancelar e Usar ≥ 44;
  - busca 42 px dentro de um rótulo de 44;
  - **filtros 36 px** (P3-1);
  - nenhum alvo abaixo de 24 px.
- **Gravando SPY:** a região viva (`role=status`, `polite`) mostra "Gravando a comparação com SPY…", sem grade, fatos nem linha de gravação. Depois anuncia "Referência trocada para SPY e gravada.".
- **SPY:** estão todos visíveis:
  - "USDT tratado como USD, sem conversão.";
  - "BTC/USDT em USDT, SPY em USD";
  - "02 jan. 2019 – 31 dez. 2024 · 2.190 dias";
  - "01 jan. 2019 (sem pregão em Nova York) · 0 trades";
  - "Retorno de preço, sem dividendos";
  - "SPY versão 5";
  - "Gravada neste resultado em 27/10/2026, 14:32.".

  O aviso é texto com ícone (`role=note`), não tooltip.
- **Volta ao próprio ativo:** grava "BTC/USDT (próprio ativo)", e o aviso some.
- **SOL:** "01 jan. 2019 – 10 ago. 2020 da estratégia · 3 trades fora". O retorno é diferente do "Retorno total". O Δ negativo tem cor `rgb(246,70,93)` e o texto "a favor da referência", então o sentido não depende só da cor.
- **CRCL:** "Sem comparação" e o motivo, sem nenhum `\d%` e sem "p.p.", e sem período comum. A região viva diz "Referência CRCL gravada sem comparação: histórico insuficiente.".
- **QQQ:** spinner durante a coleta, depois a amostra "QQQ versão 1 (coletada agora)". A falha simulada depois de QQQ diz "…a referência continua QQQ.".
- **Planilha de trades:** o status (`role=status`) cita "Trades, Contexto e Legenda". A aba Contexto tem os 22 campos do spec, e a tabela rola dentro do quadro a 390.
- Sem rolagem horizontal na carga, em SPY e no fim.

**Favorito, PASS d/m:**

- Abre com SPY, "Gravada no favorito NVDA Trend em 27/10/2026, 09:14." e "SPY versão 5 (fixada pelo favorito)". Não há nota de salvar.
- O retorno é igual ao "Retorno total", e SPY aparece como retorno de preço.
- CRCL, que tem período comum dentro do favorito, deixa "6 trades fora".
- "Não registrada" mostra "Trocar referência" e "Comparar com o próprio ativo", este com ≥ 44 px.
- A planilha sai com "não registrado".

**Favoritos, PASS d/m:**

- Exatamente 1 "Ref.: SPY · comparação gravada 27/10" visível: na linha a 1440 e no cartão a 390.
- O status do Exportar é `polite`.
- A planilha tem "Cripto (deduzido)", "USDT (deduzido)", "não registrado" e o aviso de moeda, e os 22 cabeçalhos de contexto na ordem do spec, depois de Name e Symbol.
- O botão Exportar vivo tem 40 px (herdado).

**Descoberta, PASS d/m:**

- A frase "…Trocar a referência num resultado ou favorito não muda este ranking." está presente.
- "Exportar planilha" tem 44 px e anel de foco, e o status `polite` diz "todas as páginas".
- O ranking segue com a ordenação "CAGR vs B&H" e o rank global.
- A prévia da planilha tem **16 cabeçalhos**: "Rank global", "Candidato" e 14 de contexto (P2-2).

### 5c. Aritmética da amostra (`numbers.py`)

Para as 11 referências válidas, `CAGR = (1+R)^(365,25/dias) − 1` e a diferença em p.p. batem com o que a tela mostra, com arredondamento de no máximo 0,1 p.p. Dois exemplos são ETH (30,9 contra 30,8 na tela) e CRCL no favorito (rCagr 114,59 contra 114,53). A amostra é coerente com a regra do design.md.

## 6. Confronto com o Entra (só o visível; backend = Apply)

| Entra | Visto no browser | Disposition |
|---|---|---|
| Referência padrão = próprio ativo; troca por qualquer cripto/ação/ETF do catálogo; coleta na escolha | Padrão "(próprio ativo)"; seletor com 3 classes; QQQ "Coletando… na Binance" | PASS. O estado de indisponível do catálogo não foi prototipado (P2-1). |
| Escolha depois de rodar, gravada no resultado ou favorito e na planilha; ranking no próprio ativo | "Gravada neste resultado" / "Gravada no favorito"; "Ref.: SPY" em Favoritos; frase na Descoberta | PASS |
| Janela comum com o que ficou de fora; insuficiente com motivo, sem zero | SPY (feriado NY, 0 trades), SOL (3 trades), CRCL sem números | PASS. "<30 dias" e short não demonstrados (P3-6). |
| Moedas diferentes: percentual e aviso visível | Aviso âmbar com as duas moedas; ausente em NVDA×SPY e cripto×cripto | PASS |
| Retorno de preço, sem dividendos | Linha "Tipo de retorno" em SPY, QQQ, NVDA e CRCL | PASS |
| Três planilhas com contexto completo | Trades: 22 campos. Favoritos: 22 campos. Descoberta: a prévia tem 14 (falta Período pedido, entre outros) | Trades e Favoritos PASS. A Descoberta diverge do spec (P2-2). |
| Sem recálculo escondido | "Abrir ou exportar de novo não recalcula"; amostra "fixada pelo favorito"; falha não grava | PASS (visível) |
| Favoritos antigos: "deduzido" / "não registrado" | Linha "BTC antigo" na planilha; "Comparação não registrada" no favorito | PASS |
| Verificação (NVDA×SPY, ETF próprio, BTC×SPY, insuficiente, troca no favorito, 3 planilhas, antigo, ranking) | Todos demonstrados, menos "ETF comparado com o próprio ativo": o próprio ativo só aparece em BTC e NVDA | PASS, com lacuna de demo (P3-6) |
| Não entra: fonte nova, escolha antes de rodar, dividendos, carteira/fiscal | Nenhum controle novo nos formulários; só catálogo e Binance | PASS |

## 7. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Gravando, coletando, falha, insuficiente e não registrada, cada um com texto próprio na região viva; linha de gravação com data e amostra | — |
| 2 | Mundo real | "sem pregão em Nova York", "a favor da estratégia/referência", moedas escritas | — |
| 3 | Controle | Cancelar, Esc e clique fora não trocam nada; falha mantém a anterior; "Tentar de novo" | — |
| 4 | Consistência | Mesma moldura `r19` e o mesmo aviso de precisão. A mesma tela diz "dias corridos ÷ 365" nas convenções e usa 365,25 na seção (aceito, P3-7). | P3 |
| 5 | Prevenção de erro | Insuficiente nunca vira número. Ativo indisponível sem desenho no seletor (P2-1). | P2 |
| 9 | Recuperação | Falha na coleta com motivo, o que fica e "Tentar de novo" | — |

## 8. Achados

### P0: nenhum

### P1: nenhum

Nenhum critério do Entra falhou no browser. Os tokens D4 estão em L1 a L3, e o gate passa.

### P2 (não bloqueiam; o único rework ou juízo de Alan)

- **P2-1 O seletor não tem o estado "ativo marcado/indisponível, desabilitado com o motivo do catálogo".** *Contrato.*
  - Onde: `index.html`/`favorite.html`, `[data-b23-dialog] .b23-list`. As 7 opções estão todas habilitadas.
  - Problema: o design.md §3 e o spec `benchmark-reference-choice` ("Marked or unavailable catalog assets SHALL be shown disabled with the catalog reason") pedem esse estado. Sem desenho, o Apply teria de inventar o visual e onde aparece o motivo.
  - **Corrigir:** uma 8ª opção desabilitada (por exemplo, um ativo "marcado" do catálogo) com o motivo na linha de histórico, `disabled` no rádio e `aria-describedby`. Ou dizer no design.md que reusa literalmente o estado desabilitado do `AssetPicker` vivo.
- **P2-2 A prévia da planilha da Descoberta mostra 14 dos 22 campos de contexto.** *Contrato, mecânico.*
  - Onde: `discovery.html`, DELTA "demonstração da planilha do ranking". Cabeçalhos: Classe, Moeda, Fonte, Sessão, Ajuste, Período efetivo, Modo de execução, Versão da amostra, Referência, Período comum, CAGR anualizado, CAGR da referência, Diferença de CAGR (p.p.), Aviso de moeda.
  - Problema: o spec `result-context-export` diz "the three workbooks carry the same context headers in the same order", e o Entra lista "período pedido e efetivo". Faltam Período pedido, Tipo de retorno da referência, Fora do período comum, Retorno da estratégia e Retorno da referência no período comum, Situação da comparação, Versão da amostra da referência e Comparação gravada em. "CAGR da estratégia no período comum" aparece como "CAGR anualizado". Trades e Favoritos estão completos.
  - **Corrigir:** gerar a prévia da Descoberta pelo mesmo cabeçalho de 22 campos (vazio ou "não registrado" onde não se aplica, e retornos derivados do CAGR e da janela, como o design.md §7 já diz). Ou registrar no design.md quais colunas a Descoberta deixa vazias.

### P3 (aceitos: Apply, protótipo, herdado; não reabrir como P0/P1)

- **P3-1 Filtros de classe do seletor com 36 px.** *A11y, Apply.* Todas, Cripto, Ações e ETFs medem 36 px a 1440 e a 390 (toque). O Apply contract pede 44 px no seletor. Passa do mínimo de 24 px. **Apply:** `min-height: 44px` em `.b23-filters button` no celular.
- **P3-2 Linhas longas.** *Polish.* São de 92 a 99 caracteres por linha a 1440 em:
  - `p.b23-dlg-desc`;
  - o motivo de "Sem comparação" (`max-width: 78ch` com 13 px);
  - o parágrafo de "Comparação não registrada".

  `max-width: 65ch` resolve.
- **P3-3 Herdados do incumbente.**
  - A sombra do modal: `gpt-thin-border-wide-shadow`, já aceita.
  - O `span.text-xs` de 10 px "3 de 3 candidatos" reembalado no DELTA da Descoberta.
  - O "Exportar" de Favoritos com 40 px.
  - Os 2 achados CLI de `favorites.html` e os 39 de `live.css`.
  - No browser, de 26 a 122 achados COPIED por estado a 1440 e de 33 a 108 a 390 (`undersized-ui-text`, `low-contrast`, `nested-cards`, `cramped-padding`).
- **P3-4 Números do estado pendente no DOM.** *Apply.* Em `delta.js`, `render()` preenche a grade com os números da referência nova durante "Gravando/Coletando" (usa `current.state`, não `state`), e só o CSS os esconde. **Apply:** não renderizar números antes da gravação voltar.
- **P3-5 Processo.**
  - O diálogo e o `<script id="b23-data">` ficam fora de qualquer marcador. O design.md diz "DELTA no fim do body"; marcar com `DELTA:start/end`.
  - `discovery.html` dá `classify=BLOCKED` contra o catálogo, que pede "Preflight" e "Rascunho de varredura" no Decidir. O gate só lê o canônico.
  - `parse_live_route` captura `surface: existing` como justificativa (recorrente).
- **P3-6 Lacunas da Demonstração.** *Demo.* Os specs cobrem todos estes casos, e o E2E deve exercitá-los:
  - estratégia short ("buy-and-hold long-only");
  - período comum menor que 30 dias ("Período comum de N dias: o mínimo é 30.", ligado à pergunta aberta);
  - ETF comparado com o próprio ativo ("SPY (próprio ativo)" com retorno de preço), que é item da Verificação do Entra.
- **P3-7 365 x 365,25 na mesma tela.** *Aceito.* As "Convenções desta execução" dizem "dias corridos ÷ 365", e a seção calcula com 365,25. O design.md aceita isso. Mudança barata: o subtítulo da seção diria "CAGR com dias corridos ÷ 365,25".

Mecânicos: P2-2 e P3-1 a P3-5. Contrato/produto: P2-1.

## 9. Veredito

**PASS com rework (leve, opcional dentro do teto).** P0 e P1 zerados.

- **Gate estático:** `clone_gate_ok=True` e `classify(index,/combo/results)=PASS`, com copied 56.249 e os tokens L1–L3 conferidos.
- **Digests:** batem do disco ao HTTPS nos 7 arquivos, e o `live.css` é igual ao CSS que o `/combo/results` vivo serve hoje.
- **Clone:** as 29 regiões COPIED são substring literal de uma captura viva fresca.
- **Detector:** 0 achados no CLI do delta. No browser, o delta só tem a sombra herdada e o comprimento de linha.
- **Browser:** o gate do autor reproduz 144/144. Meus 188/190 cobrem teclado, alvos, regiões vivas, estados e planilhas a 1440 e 390, com console limpo e sem rolagem horizontal.

Disposition:

- P2-1 e P2-2 merecem o único rework: são baratos e fecham dois itens visíveis do spec (o estado desabilitado e o mesmo cabeçalho nas três planilhas).
- Sem rework, os dois P2 viram nota na Aprovação de Design, e os P3 ficam aceitos para o Apply.

## 10. Referências

- **Disco:** `frontend/public/prototypes/card-1123-benchmark-exportacao/{index,favorite,favorites,discovery}.html`, `live.css`, `delta.css`, `delta.js`; `openspec/changes/card-1123-benchmark-exportacao/design.md` (sha `9a6235f5…`) e `specs/`.
- **HTTPS DEV:** https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/. Vivo: https://dev.criptofarol.com.br/combo/results (shell 200, bundle `index-C9_PkDmo.js` / `index-DOHmvARO.css`), renderizado com a API simulada do autor.
- **Detector:**
  - CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json`;
  - browser: `detector/detect-antipatterns-browser.js` injetado com `autoScan:false`.
- **Gate:** `scripts/process-fsm/design_clone_gate.py` + `route-landmarks.yaml` (HEAD `9b83d25e`).
- **Scratchpad** (não versionado): `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123B/`.
  - Scripts: `det.sh`, `gate.py`, `clonecheck.py`, `numbers.py`, `author_gate.py`, `browser.py`.
  - Saídas: `det-*.json`, `gate.out`, `clonecheck.json`, `browser.json`, `served/`, `live1/`, `gate-shots/`.
  - Screenshots `shots/`, 26 no total:
    - `{1440,390}-index-{top,own,spy,sol,crcl,fail,full}`;
    - `{1440,390}-dialog`;
    - `{1440,390}-favorite-{spy,crcl,unrec}`;
    - `{1440,390}-favorites`;
    - `{1440,390}-discovery`.

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
