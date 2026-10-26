> Proveniência: Assessment B (detector + gate estático + browser real), papel `assessment-b`, faixa `juizo`, modelo da captura **Opus 5.5** (`claude-opus-5-5`, effort `high`), captura `cf-assess-b-1122.json` (attempt `44558289-2276-4517-99a4-ae2f0ad366b7`, capture_sha256 `7e384188…`), wave `cf-assess-a-1122.json` (`1122-d1`), birth `44558289-2276-4517-99a4-ae2f0ad366b7.birth.json`, cliente claude, superfície claude-desktop, 2026-10-26T18:25Z.

# Assessment B (detector + browser real): card 1122 · change card-1122-favoritos-alertas-acoes-etfs

> Assessor B isolado. Não li o snapshot nem o scratch do Assessment A. Não houve nested-spawn. Cliente Claude Code (adapter cooperativo, sem modo Auto).
> Este filho escreveu só este snapshot e os screenshots `card-1122-B-*.png` nesta pasta. Scripts e JSON ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/c1122B/` e não são versionados.
> Para a captura viva fresca (seção 4), reexecutei os scripts de captura do autor (`c1122/capture.py`, `capture2.py`) com saída no meu scratch: mesmo mock de API, render novo do bundle vivo de hoje.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /monitor` · `surface: existing`, nas linhas 1 a 3, cada um em linha própria. Regiões COPIED e DELTA listadas em Context; P3 aceitos em Risks / Trade-offs.

```
Assessment B 1122
snapshot: .impeccable/critique/1122-card-1122-favoritos-alertas-acoes-etfs-B.md (2026-10-26T18:25Z)
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == HTTPS (curl) em 9/9 arquivos (HTTP 200); a pasta / serve o index.html; live.css == /assets/index-WJwiIv3A.css vivo de hoje (8f4edf0a…); design.md d4d64e7e… igual no início e no fim
detector CLI: index 1 · favorites 2 · results 1 · configure 8 · discovery 0 · profile 1 · delta.css 0 · delta.js 0 · live.css 39
detector hook (DESIGN.md): HTML iguais ao CLI · delta.css 20 (10 cor, 7 tamanho, 3 raio) · delta.js 0 · live.css 331
detector browser (6 páginas, estados do delta): únicos desk COPIED 222 × DELTA 68 · mob COPIED 197 × DELTA 89; dos DELTA, só desk 21 / mob 14 em elementos m22-* (8/4 do painel Demonstração), o resto é marcação viva clonada; 0 low-contrast de autoria do delta
gate: design_token_gap=None · evaluate_clone_gate(HEAD)=True · clone_gate_ok=True · classify(index,/monitor)=PASS · copied_utf8_sum 59679 · 23/23 COPIED · 23/23 DELTA · 0 marcador dentro de tag
gate extras (informativo): favorites PASS · results PASS · discovery BLOCKED (falta "Rascunho de varredura", captura do Decidir) · configure/profile sem rota no catálogo
clone vs vivo: 65/65 regiões COPIED (6 páginas) são substring literal de uma captura viva fresca; texto fora de marcador = 0 em todas
browser: 363 asserts, 347 PASS, 16 FAIL (11 de harness, re-testados PASS ou conferidos na fonte; 5 reais = P2-1 e P3-1) · 0 console error / pageerror / ≥400 / requestfailed
P0: nenhum
P1: nenhum
P2: [mecânico] Ver Trades da fonte antiga habilitado no cartão · [mecânico] detalhe da linha NVDA fonte antiga diz "Em posição" com preços de BTC · [produto] Monitor sem estado de dado insuficiente · [produto, juízo] densidade da linha de ação/ETF a 1440
P3: [a11y/Apply] modal Salvar com aria-modal sem prender Tab · [a11y/Apply] Alertar das linhas cripto sem aria-label até o 1º clique · [amostra] estrelas de NVDA fonte antiga e "6 ativos" · [polish] ícone "NVD" 9 px · [polish] linhas longas · [polish] link "Ver em Favoritos" inline · [herdado] .btn sem anel, 10 px, padding 0 · [processo] discovery.html BLOCKED no catálogo e parse_live_route · [Apply] hook DESIGN.md no delta.css · [demo] lacunas da Demonstração
verdict: PASS com rework (leve, opcional dentro do teto)
```

- UTC: 2026-10-26T18:25Z
- Tupla (só leitura): `bound_card=1122` · `q_git=card-1122-favoritos-alertas-acoes-etfs` @ `f093e2cc` · Status=**Design**, conforme o prompt do pai. A leitura GraphQL do Project foi recusada pela guarda do worktree e não foi refeita.
- Pacote não commitado: `git status` mostra a pasta do protótipo e a change como `??`.
- Não houve `process_event`, commit, push, Gist, comentário nem restart.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1122` e `/comments`, sem `gh issue view`. Body grelhado: 10 itens no Entra (5 decisões de Alan de 26/10/2026) e 4 no Não entra. Comentários: "card nítido; sem grill" e o handoff do grill-card. As decisões não foram reabertas. A "Transição da cripto" está aberta como pergunta 1 do design.md.

## 1. Digest servido == local

| Arquivo | sha256 (disco = HTTPS) | bytes |
|---|---|---|
| `index.html` (a pasta `/` serve o mesmo) | `b7a4971379428845d9f78717c41a0a072ccf74f760a6f8f5e8c308645126c9d7` | 121525 |
| `favorites.html` | `99d0fdb1ac13811186db56a7479e85ce20f244fe44c765e20e3f0215cb796dea` | 107766 |
| `results.html` | `5953caa17e29ceededc10ec31846577626cfca7c24e85e02fd52d0c3a9db2ca4` | 46431 |
| `configure.html` | `d94216041b570e1168d4024b7ab81e758d7ff6df43ffae13637b38623215b3db` | 33736 |
| `discovery.html` | `d1f32be145edd65ff863b0dc74ac9c26d2c64ae26520faca07c968596e79f3df` | 47445 |
| `profile.html` | `9824fe0bc64d86c53263362da7b6afec029b9057b69df6a0c5eff9122cd7f30d` | 30564 |
| `live.css` | `8f4edf0aca9aca6ff4414384993cab1adb18042e4443ee074fe5ee9a6d569183` (= `index-WJwiIv3A.css` servido hoje em DEV; o `/monitor` vivo referencia `index-DUWqPrYj.js` + `index-WJwiIv3A.css`) | 248557 |
| `delta.css` | `d83e8e504da566369683ed9b398d5600dd9267ea24aaac17bbcb375f71175f00` | 7271 |
| `delta.js` | `9be14c630d273439eee7e4214492e606f69411db775d53fd500bf274e9358f18` | 19132 |

Os 9 arquivos respondem HTTP 200, e os prefixos batem com a tabela de Prototype Validation do design.md. O risco "URL pública responde 404 até o pai reiniciar o serviço" (Risks) já não vale. Os digests foram conferidos de novo no fim, sem mudança.

## 2. Detector Impeccable

### 2a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json <arquivo>`)

| Alvo | exit | Achados | Região |
|---|---|---|---|
| `index.html` | 2 | 1 `flat-type-hierarchy` (12/14/18 px) | página inteira; vem da escala viva |
| `favorites.html` | 2 | 1 `flat-type-hierarchy`, 1 `gray-on-color` (`text-zinc-400` sobre `bg-amber-400`) | o par de classes é o das estrelas vivas: 4×/10× em COPIED e 14×/6× nas linhas DELTA clonadas da linha viva |
| `results.html` | 2 | 1 `ai-color-palette` (`text-purple-400`) | "Sharpe Ratio" do modal: marcação viva do `SaveFavoriteModal`, levada para o bloco DELTA |
| `configure.html` | 2 | 4 `gray-on-color`, 3 `ai-color-palette`, 1 `flat-type-hierarchy` | todos em COPIED |
| `discovery.html` | 0 | `[]` | — |
| `profile.html` | 2 | 1 `flat-type-hierarchy` | página inteira |
| `delta.css` | 0 | `[]` | — |
| `delta.js` | 0 | `[]` | — |
| `live.css` | 2 | 39 (24 `gray-on-color`, 6 `ai-color-palette`, 4 `side-tab`, 2 `overused-font`, 1 `border-accent-on-rounded`, 1 `gradient-text`, 1 `layout-transition`) | CSS vivo inteiro, COPIED |

Os HTML capturados têm o corpo numa linha só (L13/L14). Por isso, a região de cada achado foi localizada procurando a classe denunciada entre os marcadores, e não pelo número da linha.

### 2b. Modo hook (`hook-lib.loadDetector` + `readConfig` + `designSystemOptions(…, REPO)`; DESIGN.md carregado)

- HTML: iguais ao CLI.
- `delta.js`: 0.
- `live.css`: 331 (os 39 do CLI mais 292 `design-system-*`).
- `delta.css`: 20, todos fora da escala do DESIGN.md:
  - 10 `design-system-color`: `#b7bdc6` ×7 e `#474d57` ×3;
  - 7 `design-system-font-size`: 11 px ×4, 9, 10 e 15 px;
  - 3 `design-system-radius`: 5 e 10 px ×2.

O design.md aceita como P3 as cores literais e os 11 px. Os 9, 10 e 15 px e os raios de 5 e 10 px são da mesma família, mas não estão listados (P3-9).

### 2c. Detector no browser (`detect-antipatterns-browser.js` injetado, `impeccableDetect({serialize:false})`)

Cada elemento foi classificado pelo marcador `COPIED`/`DELTA` que o contém. Nó criado pelo `delta.js` depois da carga conta como DELTA-js. Estados varridos a 1440 e 390:

- Monitor: aberto, atraso e transição.
- Favoritos: dono e vitrine.
- Resultado: modal.
- Combo, Descoberta e Perfil: carga.

| Viewport | COPIED | DELTA | PAGE |
|---|---|---|---|
| 1440 | 222 | 68 | 8 |
| 390 | 197 | 89 | 8 |

Os DELTA se dividem assim:

- **Marcação viva clonada para as linhas, cartões e detalhes de NVDA/SPY** (sem classe `m22-*`): desk 48, mob 77. São `undersized-ui-text` (tags e rótulos de 10 px), `low-contrast` (`#707a8a` sobre `#181a20`, 4,0:1: "Lote … · ref", "Sinal · Em posição", "Destino obrigatório" da Descoberta), `cramped-padding`, `side-tab` e `nested-cards`, todos com a mesma classe da linha de BTC viva. Contam como herdados (P3-7).
- **Painel Demonstração** (só protótipo): desk 8, mob 4. Botões com padding vertical 0 (mas `min-height: 44px`) e `<p>` com cerca de 92 caracteres por linha.
- **Autoria do delta (contam):** desk 13, mob 10.
  - Tag "Alerta" a 10 px (×4). É o tamanho da `.tag` viva ("Carteira", "Strategy" medem 10 px), então é herdado.
  - `.pair-icon.m22-eq` a 9 px, com o texto "NVD"/"SPY" (×3; a viva é 10 px com "BTC"). Ver P3-4.
  - `.m22-cat-none` "Catálogo · não alerta" a 11 px (×5).
  - `p.m22-modal-note` com cerca de 112 caracteres por linha a 1440, encostando na borda do viewport a 390 (o padding do modal é zerado pelo reset vivo). Ver P3-5.

Nenhum `low-contrast` em elemento `m22-*`. Nenhum `script-error`.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py` importado; `clone_gate_ok` é o que `process_event` chama)

```
lines1-3 ['UI impact: affected', 'live_route: /monitor', 'surface: existing']
design_token_gap None
parse_ui_impact affected
parse_live_route ('/monitor', 'surface: existing')
parse_surface existing
catalog (load_head_catalog) ['/combo/discovery', '/combo/results', '/combo/select', '/favorites', '/monitor', 'landing']
/monitor entry: selectors ["table.signals"], texts Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia
evaluate_clone_gate True
clone_gate_ok True
index.html     /monitor          landmarks True  classify PASS     copied 59679  COPIED 23/23 DELTA 23/23  inside_tag 0  121525 B
favorites.html /favorites        landmarks True  classify PASS     copied 55574  COPIED 19/19 DELTA 23/23  inside_tag 0
results.html   /combo/results    landmarks True  classify PASS     copied 38998  COPIED 6/6   DELTA 6/6    inside_tag 0
configure.html /combo/configure  (sem rota no catálogo)            copied 32565  COPIED 5/5   DELTA 5/5    inside_tag 0
discovery.html /combo/discovery  landmarks False classify BLOCKED  copied 45527  COPIED 7/7   DELTA 7/7    inside_tag 0
profile.html   /profile          (sem rota no catálogo)            copied 29330  COPIED 5/5   DELTA 5/5    inside_tag 0
```

- O canônico passa, e o número de `copied_utf8_sum` (59.679) é o mesmo do design.md.
- Nos extras, a minha soma de COPIED conta os nós de comentário internos, por isso dá alguns bytes acima da tabela do autor, que conta sem os marcadores. Os pares conferem.
- `discovery.html` é BLOCKED no `classify`: falta o texto "Rascunho de varredura", porque a captura é o Decidir com o modal aberto. O gate só lê o canônico, então isso é informativo (P3-8).
- `parse_live_route` continua levando a linha seguinte (`surface: existing`) como justificativa. É inofensivo com rota de catálogo (P3-8).

## 4. Clone contra a página viva (fora do DELTA)

- Rodei os scripts de captura do autor com saída no meu scratch (`live1/`, `live2/`). É o mesmo mock de API, mas um render novo do bundle vivo de hoje (`index-DUWqPrYj.js`), a 1440 e a 390, sem erros de página.
- Rotas e estados capturados: `/monitor` (fechado e com BTC aberto), `/favorites`, `/profile`, `/combo/results` (NVDA e modal de BTC), `/combo/configure` com NVDA e `/combo/discovery` com o modal de NVDA.
- Para cada região COPIED, testei se o conteúdo (sem os blocos DELTA aninhados, com o relógio HH:MM:SS normalizado) é **substring literal** de alguma dessas capturas:

| Página | Regiões COPIED | Substring do vivo |
|---|---|---|
| `index.html` (`/monitor`) | 23 | 23 |
| `favorites.html` | 19 | 19 |
| `results.html` | 6 | 6 |
| `configure.html` | 5 | 5 |
| `discovery.html` | 7 | 7 |
| `profile.html` | 5 | 5 |

- O texto fora de qualquer marcador no `<body>` é vazio em todas as páginas (só espaço, 38 a 132 B).
- `live.css` é byte-idêntico ao CSS vivo servido hoje.
- Fora do DELTA, o clone é o vivo.

## 5. Browser real

- Playwright Python 1.62 com Chromium headless shell 1243 (`--no-sandbox`), `colorScheme: dark`, `pt-BR`, fuso São Paulo.
- **URL pública:** `https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/` e as 5 páginas extras.
- Viewports: 1440×900 (desk) e 390×844 (mob, `isMobile`, toque, DPR 2). Contexto novo por página.
- Scripts: `browser.py` (352 asserts), `extra.py` (11) e `extra2.py` (medidas).
- Screenshots `card-1122-B-*.png` nesta pasta: 35 no total.

**Erros:** 0 `console.error`, 0 `pageerror`, 0 respostas ≥ 400 e 0 `requestfailed` nos 12 contextos.

### Matriz

| Página × viewport | Asserts | PASS | FAIL |
|---|---|---|---|
| Monitor desk / mob | 133 / 126 | 131 / 123 | 2 / 3 |
| Favoritos desk / mob | 17 / 16 | 15 / 15 | 2 / 1 |
| Resultado desk / mob | 15 / 15 | 12 / 12 | 3 / 3 |
| Combo, Descoberta, Perfil desk / mob | 15 / 15 | 15 / 15 | 0 |
| `extra.py` (re-testes) | 11 | 9 | 2 |
| **Total** | **363** | **347** | **16** |

**FAIL de harness (11), re-testados PASS ou conferidos na fonte:**

- A pílula "SAÍDA / COBERTURA" e o cabeçalho "ALERTAR" vêm do `innerText` com `uppercase`. Pelo `textContent`, dão "Saída / cobertura" e "Alertar", ambos PASS.
- Os links "Marcar em Favoritos" e "Ver em Favoritos" apontam para `favorites.html`, o clone na mesma pasta. O teste esperava `/favorites`. Com o alvo do clone, passam (44 px no link da faixa).
- O resumo de Favoritos: "Interesse alto" e "2" estão em nós sem espaço entre eles. Na fonte, o resumo é "Acompanhar 1 · Interesse alto 2 · Top picks 1 · Sem estrela 1", o que bate com as estrelas das 5 linhas (BTC 3, NVDA-b 2, ETH 2, SPY 1, NVDA-s 0).

**FAIL reais (5):**

- Resultado d/m: o Tab sai do modal na 4ª parada (2). Com o foco fora, o Esc não fecha (2). Ver P3-1.
- Monitor mob: Ver Trades do cartão de NVDA (fonte antiga) está habilitado (1). Ver P2-1.

**Monitor, todos PASS d/m (salvo o indicado):**

- **Carga** (pregão aberto):
  - NVDA (Binance Ações) e SPY ficam em Em posição; NVDA (fonte antiga) em Saída / cobertura.
  - Linha de identidade:
    - NVDA: "Ação · USD · Binance Ações · NY · split";
    - SPY: "ETF · USD · Binance Ações · NY · split";
    - NVDA antiga: "Ação · USD · Stooq · fonte antiga · diário".
  - As duas NVDA se distinguem só por essa linha, e há 2 linhas/cartões NVDA.
  - "Alerta" aparece em BTC, SOL, NVDA-b e SPY (4), e não em NVDA-s.
  - A cripto não mostra estado de mercado.
  - Indicadores "Em posição 4 · Saída / cobertura 2 · Total 6 · Em carteira 6".
- **Cenários**: em cada um, conferi o tom, o texto, o ícone (1 visível) e o "Sinal em espera" só no atraso, nas 3 linhas e nos 3 cartões.

  | Cenário | Estado de NVDA-b · SPY · NVDA-s | Telegram |
  |---|---|---|
  | Seg. 15:00 | aberto "fecha 17:00 (16:00 em NY)" ×3 | 0 mensagens |
  | Sáb. | fechado "fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)" ×3 | 1: entrada de NVDA com "NVDA (Ação · USD)", Estratégia, "Configuração: Binance Ações · pregão regular de NY · ajustado por split", "TimeFrame: 1d", leituras, "Candle: sex., 23 out. 2026 (pregão fechou às 17:00 BRT)", valores em USD, "Ordem: nenhuma enviada", sem USDT |
  | Feriado 26/11 | fechado "feriado em Nova York · abre sex., 27 nov., 11:30 (09:30 em NY)", em cinza | 0 |
  | Ter. 08:05 | NVDA-b `stale` em âmbar `rgb(240,185,11)`, "Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out." + "Sinal em espera até o dado normalizar"; SPY e NVDA-s "fora do pregão · abre hoje, 10:30" | 1: "Dados atrasados" com ativo, fonte, último, esperado e "em espera" |
  | Qua. 08:05 | fechado ×3; NVDA-b vai para Saída / cobertura, contagens (3)/(3) | 1: saída de NVDA, "Leitura atual: Venda", "Ordem: nenhuma enviada" |
  | Transição | aberto ×3; a faixa `role=status` fica acima dos indicadores, com "Marcar em Favoritos" de 44 px; nenhum "Alerta" nas linhas | 1: "Mudança nos alertas" |

  Nenhuma mensagem de mercado fechado ou feriado. Voltar ao aberto devolve NVDA-b a Em posição. Sem rolagem horizontal em nenhum cenário.
- **Fonte antiga:** na linha (desk), Abrir Gráfico e Ver Trades têm `aria-disabled="true"` e "Fonte antiga: gráfico depois da migração para a Binance". **No cartão (390), só Abrir Gráfico tem isso** (P2-1). Em NVDA-b, os dois botões estão habilitados.
- **Detalhe (desk):**
  - O chevron de NVDA-b abre com `aria-expanded=true` e mostra "Ação/ETF na carteira recebe entrada e saída no Telegram.".
  - O detalhe de NVDA-s abre, mas o conteúdo diz "Em posição" e mostra stop/entrada de BTC (P2-2).
  - O detalhe de BTC copiado abre.
- **Carteira (desk):** desmarcar NVDA vira "○ Carteira", e "Em portfólio" esconde as duas NVDA. "Todos" as traz de volta. Remarcar volta a "● Carteira".
- **Timeframe (desk):** as opções são todas/4h/1d, e 4h esconde NVDA e SPY.
- **Cartão (mob):** o controle de carteira e a ajuda "Ação/ETF na carteira recebe entrada e saída no Telegram." ficam visíveis.

**Favoritos, todos PASS d/m:**

- Nenhum "ainda não" na página.
- A coluna "Alertar" aparece a 1440.
- NVDA-b fica ligado, NVDA-s desligado e SPY ligado, com `aria-label` "Alertar no Telegram: ligado/desligado". O clique alterna, atualiza o `aria-label` e anuncia "Alertar no Telegram desligado para NVDA." na região viva.
- A estrela da fonte antiga liga.
- Textos "último pregão 23/10", "Stooq · fonte antiga · diário" e "Aguardando dados: 40 de 200 candles" (este na lista da Demonstração).
- "Revalidar na janela recente" está habilitado em NVDA, NVDA e SPY.
- **Vitrine:**
  - a faixa `role=status` "Estas estratégias são o catálogo … e não mandam alerta …" aparece;
  - não há controle Alertar (0 visíveis);
  - "Catálogo · não alerta" aparece ×5.
- O Alertar das linhas cripto (COPIED) não tem `aria-label` e mantém o title vivo "Notificar Telegram ativo" até o primeiro clique (P3-2).

**Resultado, d/m:**

- "Salvar nos Favoritos" está habilitado.
- O modal é `role=dialog` com `aria-modal=true` e `aria-label`, e abre com o foco no nome.
- Ele mostra "NVDA · Ação · USD", "Binance Ações · pregão regular de NY · ajustado por split · 1d · Long" e a nota "Depois de salvar, marque "Alertar" em Favoritos … O favorito nasce sem alerta."
- **Salvar:** "Salvo em Favoritos com a configuração Binance Ações. Ver em Favoritos" com `role=status`, e o Salvar fica desabilitado.
- **Esc logo após abrir:** fecha e devolve o foco ao Salvar.
- **Duplicata:** "Já está nos favoritos com esta configuração (fonte, sessão e ajuste). Nada foi salvo." com `role=alert`, sem a mensagem de sucesso.
- **FAIL:** a sequência de Tab é nome → notas → "Ver Parâmetros" → Salvar → `body` → links da página. Com o foco fora, o Esc não fecha (P3-1).

**Combo, Descoberta e Perfil, PASS d/m:**

- Combo: "1 ação (NVDA): otimiza e abre o resultado; para acompanhar, salve nos Favoritos por lá."
- Descoberta: "Promover a favorito tier 3", "Tier 3 · observação" com a configuração Binance Ações e "Alertar". Sem "ainda não para ações e ETFs" e sem "sem nível de estrela".
- Perfil: "… favorito seu marcado "Alertar" (cripto, ação ou ETF) com o ativo na sua carteira. Mercado fechado e feriado aparecem só no Monitor." Sem "catálogo".

**Teclado:**

- Favoritos: 74 paradas (desk) e 60 (mob), **0 sem anel**.
- Monitor: 55 (desk) e 73 (mob) paradas. Ficam sem anel 10 (desk) e 45 (mob). Todas são `.btn` do `monitor-theme`, iguais nas linhas/cartões COPIED de BTC/SOL/ETH: "Telegram: on", "Tema", "Atualizar", "No portfólio", "Preço", "Exportar", "Reavaliar", "Confirmar gestão", "Abrir Gráfico" e "Ver Trades". O delta clona essa marcação (P3-7).
- Os controles próprios do delta têm anel: a faixa, os botões da Demonstração e o Alertar.

**Densidade (rubrica 5, `extra2.py`):**

| Linha | BTC (vivo) | NVDA/SPY aberto | NVDA atrasado |
|---|---|---|---|
| Monitor a 1440 | 158 px | 230 px (+46%) | 305 px (+93%) |
| Cartão a 390 | 815 px | 935 px (+15%) | 982 px (+20%) |

A coluna "Par / Estratégia" tem 188 px a 1440. A caixa âmbar do atraso quebra em 5 linhas, e "Pregão aberto · fecha 17:00 (16:00 em NY)" em 3.

## 6. Confronto com o Entra (só o visível; backend = Apply)

| Entra | Visto no browser | Disposition |
|---|---|---|
| Favoritos conservam fonte, sessão, ajuste e identidade; configurações distintas não colidem | NVDA Binance × NVDA Stooq lado a lado no Monitor e em Favoritos, cada um com estrelas, Alertar e estado; duplicata "com esta configuração (fonte, sessão e ajuste)" | PASS |
| Atualização respeita calendário, candle fechado, dados insuficientes; fim de semana/feriado sem falso stale | "Backtest atualizado … · último pregão 23/10", "Aguardando dados: 40 de 200 candles", falha só no atraso real; sábado e feriado sem atraso | PASS em Favoritos. O Monitor não tem estado de dado insuficiente (P2-3). |
| Canais existentes atendem ação/ETF e distinguem sinal, atraso e fechado; restart não duplica | Mensagens de sinal, de atraso e nenhuma de fechado. Idempotência é spec/Apply. | PASS (visível) |
| Quem recebe: os próprios favoritos marcados, inclusive cripto | Alertar do dono em todas as classes; vitrine "Catálogo · não alerta"; frase do Perfil | PASS |
| Transição da cripto (decidir no Design com Alan) | Recomendação A demonstrada (aviso único + faixa); pergunta aberta 1 do design.md | Com Alan (não é defeito) |
| Entrada e saída de ação/ETF na carteira | Entrada no sábado e saída na quarta, com NVDA na carteira; texto de ajuda no detalhe e no cartão | PASS |
| Um alerta por favorito, que identifica estratégia e configuração | Estados separados das duas NVDA nas linhas; a mensagem traz Estratégia e Configuração | PASS. O detalhe de NVDA-s contradiz o estado (P2-2). |
| Atraso: aviso único por ativo; fechado só na tela | Atraso de terça com 1 aviso; quarta com recuperação sem mensagem; fechado sem mensagem | PASS |
| Alerta não envia ordem | "Ordem: nenhuma enviada — o alerta é só o sinal da estratégia." | PASS |
| Validar ação, ETF, cripto, configurações distintas, atraso, fechado, recuperação | Demonstração cobre ação, ETF, as duas configurações, atraso, fechado e recuperação. Cripto só na transição. | PASS (lacunas da demo em P3-10) |
| Não entra: canais novos, robô, compra/venda, migração da fonte antiga, Telegram de fechado | Nenhum controle novo; a fonte antiga coexiste sem migrar; nenhuma mensagem de fechado | PASS |

## 7. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Estado do mercado com ícone + texto em cada linha de ação/ETF; atraso âmbar com último/esperado; a faixa da transição diz por que o alerta parou | — |
| 2 | Mundo real | Horários em BRT com NY entre parênteses; "pregão", "feriado em Nova York" | — |
| 4 | Consistência | A identidade "Binance Ações · NY · split" é igual no Monitor, em Favoritos e no modal. Já a fonte antiga tem ★★ no Monitor e nenhuma estrela em Favoritos, e o detalhe de NVDA-s contradiz a linha. | P2/P3 |
| 5 | Prevenção de erro | Duplicata recusada com o motivo; favorito nasce sem Alertar | — |
| 8 | Estética/minimalismo | A linha de ação/ETF cresce de 46 a 93% a 1440 | P2 |
| 9 | Recuperação | Recuperação sem ruído no Telegram; "Sinal em espera" explica a ausência de sinal | — |

## 8. Achados

### P0: nenhum

### P1: nenhum

Nenhum critério do Entra falhou no browser. Os tokens da rubrica D4 estão em L1–L3, e o gate passa.

### P2 (não bloqueiam; o único rework ou juízo de Alan)

- **P2-1 Ver Trades da fonte antiga habilitado no cartão.** *Mecânico.*
  - Onde: `index.html`, DELTA "cartão NVDA fonte antiga", `article[data-m22-card="nvda-s"]`.
  - Problema: Abrir Gráfico tem `aria-disabled`, `data-m22-off` e o title, mas Ver Trades não tem nenhum dos três. A 390, o botão parece ativo. Isso contraria o contrato (`monitor-multiclass`: "na fonte antiga, os dois botões MUST ficar visíveis e indisponíveis"). Na linha de 1440 está certo.
  - **Corrigir:** copiar os três atributos para o Ver Trades do cartão.
- **P2-2 Detalhe da linha de NVDA (fonte antiga) contradiz o estado.** *Mecânico.*
  - Onde: `tr[data-m22-detail="nvda-s"]` (1440).
  - Problema: a linha e o cartão dizem "Saída / cobertura · Saída confirmada", mas o detalhe aberto mostra "Em posição", "Sinal · Em posição", "Compra / Stop" com stop $99,877.76 e entrada $105,134.49, que são preços de BTC, ao lado de preço atual $182.31. Isso enfraquece justamente o que o card mostra: as duas NVDA têm estados separados.
  - **Corrigir:** gerar o detalhe de NVDA-s a partir do cartão dela, com "Saída confirmada" e "Risco residual".
- **P2-3 O Monitor não tem estado de dado insuficiente.** *Produto.*
  - Onde: `.m22-mkt` (tons `open`/`closed`/`stale`) e Demonstração do Monitor.
  - Problema: o spec `market-session-awareness` ("Dado insuficiente é estado próprio … com a contagem disponível e a necessária … MUST NOT gerar alerta nem aviso") vale para o sistema. Só Favoritos o mostra ("Aguardando dados: 40 de 200 candles", na lista da Demonstração). No Monitor, um ticker recém-listado não tem desenho, e o Apply teria de inventar o estado ou cair no "Sem candle válido" vivo.
  - **Corrigir:** um 4º tom em `.m22-mkt` (cinza, ícone): "Dados insuficientes · 40 de 200 candles · sem sinal até completar". Somar uma linha ou cenário na Demonstração, ou dizer no design.md que o Monitor reusa o texto de Favoritos.
- **P2-4 Densidade da linha de ação/ETF no Monitor a 1440.** *Produto, juízo.*
  - Onde: `td` Par / Estratégia (`.m22-id`, `.m22-mkt`, `.m22-hold-note`).
  - Problema: a linha cresce de 158 para 230 px aberta (+46%) e 305 px atrasada (+93%), na coluna de 188 px. A caixa âmbar quebra em 5 linhas. O design.md aceita a coluna estreita como herdada, mas não o crescimento.
  - **Corrigir:** pôr o estado do mercado sob a pílula de Status (coluna mais larga) e abreviar a identidade ("Ação · USD · Binance · NY · split"), ou deixar a coluna crescer. Alan pode aceitar como está.

### P3 (aceitos: Apply, protótipo, herdado; não reabrir como P0/P1)

- **P3-1 O modal Salvar declara `aria-modal=true` sem prender o Tab.** *A11y, Apply.*
  - O foco sai para o `body` e para a página depois de Salvar.
  - O Esc só fecha com o foco dentro (`keydown` no modal).
  - O `SaveFavoriteModal` vivo não tem nem semântica de diálogo.
  - **Apply:** prender o foco e tratar o Esc no documento.
- **P3-2 O Alertar das linhas cripto (COPIED) só ganha `aria-label` no primeiro clique.** *A11y, Apply.* Até lá fica o title vivo "Notificar Telegram ativo". O contrato (decisão 3) já pede o `aria-label` em todas as linhas.
- **P3-3 Amostra entre páginas.** *Amostra.*
  - NVDA da fonte antiga tem ★★ no Monitor, mas "sem estrela" em Favoritos.
  - "Em carteira 6 · ativos rastreados" conta NVDA duas vezes (são 5 ativos).
  - A faixa traz a data fixa "Até 26/10".
- **P3-4 Ícone "NVD" a 9 px.** *Polish.* Em `.pair-icon.m22-eq`, o vivo usa 10 px com 3 letras do par. Para ticker de 4 letras, "NVDA" a 9 px ou o logo.
- **P3-5 Linhas longas.** *Polish.*
  - `p.m22-modal-note` tem cerca de 112 caracteres por linha a 1440 e encosta na borda a 390 (padding do modal zerado pelo reset vivo, já aceito).
  - Os `<p>` da Demonstração têm cerca de 92.
  - `max-width: 75ch` resolve.
- **P3-6 Link "Ver em Favoritos" inline.** *Polish.* Tem 15 px de altura a 1440. Link inline é isento do alvo de 24 px; um botão de 44 px ajudaria no celular.
- **P3-7 Herdados do incumbente (COPIED, fora do card).**
  - `.btn` do `monitor-theme` sem anel de foco.
  - Tags de 10 px; "Alerta" segue a `.tag` viva.
  - Rótulos `#707a8a` com 4,0:1.
  - Reset que zera padding.
  - Detector no browser: 222/197 achados únicos COPIED e 48/77 na marcação viva clonada para as linhas de ação/ETF.
  - O design.md já aceita o reset, a coluna estreita, os valores em "$" e o logo absoluto.
- **P3-8 Processo.**
  - `discovery.html` dá `classify=BLOCKED` contra o catálogo (`/combo/discovery` pede "Rascunho de varredura", que não existe no Decidir com modal). O gate só lê o canônico, então é inofensivo.
  - `parse_live_route` captura `surface: existing` como justificativa. Já apontado no #1120 e no #1121.
- **P3-9 Hook DESIGN.md no `delta.css`.** *Apply.* São 20 achados:
  - cores `#b7bdc6` e `#474d57`;
  - tamanhos de 9, 10, 11 e 15 px;
  - raios de 5 e 10 px.

  O design.md aceita as cores e os 11 px. Os demais são da mesma família (casar com o `monitor-theme`) e devem entrar na lista de P3 aceitos.
- **P3-10 Lacunas da Demonstração.** *Demo.* Não há cenário de cripto atrasada (`monitor-multiclass`: "A cripto MUST mostrar só "Dados atrasados""). Também não há dois favoritos marcados do mesmo ativo mudando juntos: NVDA-s nem está marcada para alertar, e a nota "não mudou, então não gerou alerta" não prova a separação. Os specs cobrem os dois casos, e o E2E deve exercitá-los.

Mecânicos: P2-1, P2-2 e P3-1 a P3-9. Produto ou juízo: P2-3 e P2-4.

## 9. Veredito

**PASS com rework (leve, opcional dentro do teto).** P0 e P1 zerados.

- **Gate estático:** `clone_gate_ok=True` e `classify(index,/monitor)=PASS`, com copied 59.679 e os tokens L1–L3 conferidos.
- **Digests:** batem do disco ao HTTPS nos 9 arquivos, e o `live.css` é igual ao CSS vivo de hoje.
- **Clone:** as 65 regiões COPIED são substring literal de uma captura viva fresca.
- **Detector:** 0 achados no estático de `delta.css`/`delta.js`. No browser, os achados de autoria do delta são de tamanho e de comprimento de linha (P3-4, P3-5), nenhum de contraste.
- **Browser:** os seis cenários do Monitor, o Alertar, a vitrine, salvar, a duplicata e os textos das 3 extras funcionam a 1440 e 390. Sem rolagem horizontal, console limpo, controles do delta com anel.

Disposition:

- P2-1 e P2-2 merecem o único rework: são baratos e tocam o contrato visível (fonte antiga indisponível e estados separados das duas NVDA).
- P2-3 cabe no mesmo rework, com um tom a mais no `.m22-mkt`.
- P2-4 é escolha de Alan: compactar ou aceitar.
- Sem rework, os P2 viram nota na Aprovação de Design, e os P3 ficam aceitos para o Apply.

## 10. Referências

- **Disco:** `frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/{index,favorites,results,configure,discovery,profile}.html`, `live.css`, `delta.css`, `delta.js`; `openspec/changes/card-1122-favoritos-alertas-acoes-etfs/design.md` (sha `d4d64e7e…`).
- **HTTPS DEV:** https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/. Vivo: https://dev.criptofarol.com.br/monitor e as rotas `/favorites`, `/profile`, `/combo/results`, `/combo/configure`, `/combo/discovery`, renderizadas com a API simulada.
- **Detector:**
  - CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json`;
  - hook: `hook-lib.loadDetector` + `designSystemOptions(readConfig(REPO), det, REPO)`;
  - browser: `detect-antipatterns-browser.js` injetado com `autoScan:false`.
- **Gate:** `scripts/process-fsm/design_clone_gate.py` + `route-landmarks.yaml` (HEAD `f093e2cc`).
- **Scratchpad** (não versionado): `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/c1122B/`.
  - Scripts: `gate.py`, `detclass.py`, `detclass2.py`, `deltatext.py`, `hookmode.mjs`, `browser.py`, `extra.py`, `extra2.py`, `clonecheck.py`.
  - Saídas: `det-*.json`, `hookmode.json`, `asserts.json`, `extra.json`, `extra2.json`, `info.json`, `detect-browser.json`, `tabwalk.json`, `errors.json`, `clonecheck.json`, `live1/`, `live2/`.
- **Screenshots** (`.impeccable/critique/card-1122-B-*.png`, 35):
  - Monitor desk/mob: `{desk,mob}-monitor-{open,weekend,holiday,stale,recovery,transition,top}`.
  - Monitor, recortes: `desk-monitor-stale-row-nvda`, `desk-monitor-detail-nvda`, `desk-monitor-detail-nvda-fonte-antiga`, `mob-monitor-stale-card-nvda`, `mob-monitor-card-nvda-fonte-antiga`.
  - Favoritos: `{desk,mob}-favorites-{owner,catalog}`.
  - Resultado: `{desk,mob}-results-{modal,ok,dup}`.
  - Extras: `{desk,mob}-{configure,discovery,profile}`.

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
