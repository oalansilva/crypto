> Proveniência: Assessment B (detector + gate estático + browser real), papel `assessment-b`, faixa `juizo`, modelo da captura **Opus 5.5** (`claude-opus-5-5`, effort `high`), captura `cf-assess-b-d2.json` (attempt `f5d8aa0c-f23b-4309-b477-175072f76ef6`, capture_sha256 `17a52fba…`), wave `cf-assess-a-d2w.json` (`1122-d2`), birth `f5d8aa0c-f23b-4309-b477-175072f76ef6.birth.json`, cliente claude, superfície claude-desktop, 2026-10-27.

# Assessment B, rodada d2 (detector + browser real): card 1122 · change card-1122-favoritos-alertas-acoes-etfs

> Assessor B isolado. Não li o snapshot nem o scratch do Assessment A. Não criei filhos. Cliente Claude Code (adapter cooperativo, sem modo Auto).
> Este filho escreveu só este snapshot. Scripts, JSON e screenshots ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/c1122B-d2/` e não são versionados. A versão d1 deste snapshot fica no git.
> A rodada d2 é uma mudança sobre o que já está implementado na develop (`9b83d25e`), depois do "Não homologar" de 27/10.
> **Fronteira:** li o issue e os comentários pelo REST (22 comentários). Os três últimos não foram reabertos:
> - "Não homologar";
> - as 4 decisões da regra nova;
> - as 3 decisões do Design d2: Q1 e Q2 com a resposta recomendada, e o Monitor continua abrindo em "Em portfólio".
>
> A troca da decisão 21 para "Em portfólio" já vai para o rework e não é achado meu.

```
Assessment B 1122 d2
snapshot: .impeccable/critique/1122-card-1122-favoritos-alertas-acoes-etfs-B.md
model: Opus 5.5 (claude-opus-5-5, effort high)
pacote: não commitado; digests iguais no início e no fim (design.md e79b20b0…, index.html ca632b32…); openspec validate --strict = válido
URL pública: ainda serve a d1 (index sha d0d7aa5a…); browser no servidor local do worktree (127.0.0.1:8792, já encerrado)
gate: design_token_gap=None · clone_gate_ok=True · classify(index,/monitor)=PASS · copied_utf8_sum 120281 · COPIED 55/55 · DELTA 59/59 · 0 marcador dentro de tag
gate extras (informativo): favorites PASS · results PASS · discovery BLOCKED (catálogo) · profile sem rota no catálogo
clone vs vivo: 122/122 regiões COPIED (5 páginas) são substring literal de uma captura viva fresca (bundle index-C9_PkDmo.js / index-DOHmvARO.css); live.css = CSS vivo (353ac045…)
detector CLI: index 1 · favorites 3 · results 1 · discovery 0 · profile 1 · delta.css 0 · delta.js 0 · live.css 39 (todos os HTML em COPIED)
detector hook (DESIGN.md): delta.css 0 (eram 20 na d1) · delta.js 0 · live.css 334
detector browser (4 larguras): autoria m22 = "Catálogo · sem alerta" 10 px, parágrafos da Demonstração com 91 a 96 car./linha; 0 low-contrast em m22
browser: 373 asserts, 366 PASS, 7 FAIL (6 reais = P2-1; 1 de harness) · 0 console.error / pageerror / ≥400 / requestfailed · 0 rolagem horizontal
alturas: linhas da tabela iguais ao vivo a 1280/1024 (BTC/SOL −16 px a 1440, sem a tag) · cartões a 390 +61 a +114 px (+7 a +16%)
P0: nenhum
P1: nenhum
P2: [mecânico] detalhe aberto não reflete o estado do interruptor · [mecânico/demo] cenários não mudam a linha destacada; atraso por outro tempo gráfico (stale_detail) sem desenho
P3: [doc] Q1/Q2 respondidas ainda em Open Questions · [doc] nome acessível com a configuração · [amostra] SOL/USDT no Monitor e fora de Favoritos · [juízo] ajuda repetida em cada cartão a 390 · [doc] Impact do proposal desatualizado · [polish] "Catálogo · sem alerta" 10 px, linhas longas · [Apply] "Em Favoritos" da Descoberta sem desenho · [Apply] cor do "ligado" = verde de sinal · [Apply] vitrine depende do filtro de estrelas · [herdado] .btn sem anel, estrelas de 24/28 px, tabela a 1024 · [processo] URL pública na d1, discovery BLOCKED
verdict: PASS com rework (o rework já previsto pela decisão 3 de Alan; os P2 cabem nele)
```

## 1. Digests e validação

| Arquivo | sha256 (início = fim) | Tabela do design.md |
|---|---|---|
| `design.md` | `e79b20b0f943…` | — |
| `tasks.md` | `98b9ae6a6a1f…` | — |
| `index.html` | `ca632b32a2fb…` | igual |
| `favorites.html` | `106ff36d9e92…` | igual |
| `results.html` | `5159b303aa6c…` | igual |
| `discovery.html` | `0bb4e4e150e8…` | igual |
| `profile.html` | `2781744bf5fb…` | igual |
| `live.css` | `353ac045db2d…` (= `/assets/index-DOHmvARO.css` servido hoje) | igual |
| `delta.css` | `92fe48d60dc0…` | igual |
| `delta.js` | `7bfd0d9c90aa…` | igual |

- `openspec validate card-1122-favoritos-alertas-acoes-etfs --strict`: válido.
- `configure.html` saiu da pasta, como o design.md diz.
- O bundle vivo de hoje continua `index-C9_PkDmo.js` / `index-DOHmvARO.css`, o mesmo da captura do autor.
- A URL pública ainda responde com a d1 (`index.html` sha `d0d7aa5a…`), como o próprio design.md registra.

## 2. Gate estático (`scripts/process-fsm/design_clone_gate.py`)

```
lines1-3 ['UI impact: affected', 'live_route: /monitor', 'surface: existing']
design_token_gap None · parse_live_route ('/monitor', 'surface: existing') · parse_surface existing
evaluate_clone_gate True · clone_gate_ok True
index.html     /monitor        landmarks True  PASS     copied 120281  COPIED 55/55  DELTA 59/59  inside_tag 0
favorites.html /favorites      landmarks True  PASS     copied 152976  COPIED 49/49  DELTA 57/57  inside_tag 0
results.html   /combo/results  landmarks True  PASS     copied  44251  COPIED 5/5    DELTA 5/5    inside_tag 0
discovery.html /combo/discovery landmarks False BLOCKED copied  45943  COPIED 8/8    DELTA 8/8    inside_tag 0
profile.html   /profile        (sem rota no catálogo)   copied  29330  COPIED 5/5    DELTA 5/5    inside_tag 0
```

- Os tokens da rubrica D4 estão em L1–L3, cada um em linha própria. O `copied_utf8_sum` (120.281) é o mesmo do design.md.
- Nos extras, a soma conta os comentários internos e fica alguns bytes acima da tabela do autor. Os pares conferem.
- `discovery.html` continua BLOCKED no `classify`, porque o catálogo pede "Rascunho de varredura" e a captura é o Decidir com o modal. O gate só lê o canônico, então é informativo (P3-11).

## 3. Clone contra a página viva

- Reexecutei os scripts de captura do autor (`c1122d2/capture_d2.py`, `capture2_d2.py`) com saída no meu scratch (`live1/`, `live2/`). É a mesma API simulada, num render novo do bundle vivo de hoje, a 1440 e a 390, sem erro de página.
- Cada região COPIED, sem os DELTA aninhados e com o relógio normalizado, é **substring literal** de uma captura:

| Página | COPIED | Substring do vivo |
|---|---|---|
| `index.html` (`/monitor`, própria + vitrine) | 55 | 55 |
| `favorites.html` (própria + vitrine) | 49 | 49 |
| `results.html` | 5 | 5 |
| `discovery.html` | 8 | 8 |
| `profile.html` | 5 | 5 |

- Fora de marcador fica só o `</div>` que fecha o `#root` e espaços (54 a 76 B). É inofensivo.
- Fora do DELTA, o clone é o vivo.

## 4. Detector Impeccable

### 4a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json`)

| Alvo | Achados | Região |
|---|---|---|
| `index.html` | 1 `flat-type-hierarchy` | escala viva |
| `favorites.html` | 1 `flat-type-hierarchy`, 2 `gray-on-color` (`text-zinc-400` sobre `bg-amber-400`, L13 e L22) | estrelas vivas, em COPIED |
| `results.html` | 1 `ai-color-palette` (`text-purple-400`) | modal vivo, agora todo em COPIED (o DELTA é só a nota) |
| `discovery.html` | 0 | — |
| `profile.html` | 1 `flat-type-hierarchy` | escala viva |
| `delta.css` / `delta.js` | 0 / 0 | — |
| `live.css` | 39 | CSS vivo |

### 4b. Modo hook (DESIGN.md carregado)

- `delta.css` dá **0 achados** (na d1 eram 20).
- Todas as 30 variáveis do `delta.css` existem no `live.css`: `--hold*`, `--t-2/3`, `--line`, `--space-*`, `--text-*`, `--radius-*`, `--bg-*`, `--accent-*`, `--fav-muted-strong`.
- Os únicos valores literais são medidas de alvo ou estrutura: ícone de 14 px, checkbox de 18 px, 44 px, `min-height` de 30 px, outline de 2 px, larguras de 62/75ch e as quebras de 1024/1280.
- Conclusão: o `delta.css` usa os tokens do DESIGN.md.

### 4c. Detector no browser (`detect-antipatterns-browser.js`, regiões por marcador)

| Largura | COPIED | DELTA | DELTA-js | PAGE |
|---|---|---|---|---|
| 1440 | 336 | 25 | 27 | 8 |
| 1280 | 332 | 25 | 27 | 8 |
| 1024 | 331 | 25 | 26 | 8 |
| 390 | 345 | 19 | 39 | 8 |

- A maior parte dos DELTA é marcação viva clonada para a vitrine e os detalhes:
  - 23 `low-contrast` em `#707a8a`;
  - `cramped-padding` em `table-wrap`;
  - `side-tab` e `nested-cards`.
- **Autoria do delta (`m22-*`):**
  - `.m22-alert-none` "Catálogo · sem alerta" a 10 px (`tiny-text`/`undersized-ui-text`), ver P3-6;
  - parágrafos da Demonstração com 91 a 96 caracteres por linha, mesmo com `max-width: 75ch`, ver P3-6;
  - `body-text-viewport-edge` na ajuda do cartão a 390. É falso positivo: medi `left 64 / right 326`, dentro do cartão (`49–341`).
- Nenhum `low-contrast` em elemento `m22-*`.

## 5. Browser real

- Ambiente:
  - Playwright Python, Chromium headless shell 1243, `--no-sandbox`, tema escuro, `pt-BR`;
  - servidor local do worktree (`python3 -m http.server 8792 --directory frontend/public`, já encerrado);
  - contexto novo por página e largura: 1440×900, 1280×800, 1024×768 e 390×844 (toque, DPR 2).
- Scripts: `browser.py` (373 asserts), `probe.py` (geometria e recortes) e `live_heights.py` (alturas do `/monitor` vivo com a mesma API simulada nas 4 larguras).
- **Erros:** 0 `console.error`, 0 `pageerror`, 0 respostas ≥ 400 e 0 `requestfailed` nos 20 contextos. Sem rolagem horizontal em nenhuma página, cenário ou largura.

### Matriz

| Página | Asserts por largura | FAIL |
|---|---|---|
| Monitor | 76–79 | 2 por largura de mesa (P2-1) + 1 de harness a 390 |
| Favoritos | 14 | 0 |
| Resultado, Descoberta, Perfil | 4–5 cada | 0 |
| **Total** | **373** | **7 (366 PASS)** |

O FAIL de harness: a 390, o anel do interruptor do cartão é `solid 3px` (o `.btn` vivo), e o teste esperava 2 px. O foco está visível.

### Interruptor "Alerta" (Monitor), PASS nas 4 larguras salvo o indicado

- **Quantidade e lugar:**
  - 6 interruptores visíveis, um por estratégia;
  - célula de ações a 1440 e 1280, célula Status a 1024 (`m22-alert-compact`), cartão a 390;
  - nunca dois na mesma linha;
  - todos dentro da área visível e do Monitor. A 1024, o Monitor termina em 773 px e a linha vai até 1024 (incumbente); o interruptor fica na célula Status, dentro da área.
- **Semântica:** `<button role="switch" aria-checked>`. O nome acessível começa com "Alerta no Telegram · " e traz ativo, tempo gráfico, estratégia e configuração. Os 6 nomes são distintos, inclusive as duas NVDA.
- **Estado:** ETH/USDT desligado, os demais ligados. O estado aparece em texto ("ligado"/"desligado", `aria-hidden`) com 1 ícone visível (sino ou sino cortado). Desligado tem borda tracejada, ou seja, não depende só da cor.
- **Alvo:** 30×107 px na linha (acima dos 24 px do WCAG 2.5.8) e ≥ 44 px no cartão a 390.
- **Clique:** desligar NVDA muda as 4 cópias (linha, célula Status, cartão e detalhe já aberto), anuncia "Alerta de NVDA 1d desligado: nada sai no Telegram para esta estratégia." no `role=status` e não abre a linha.
- **Teclado:** o Tab chega ao interruptor de ETH com `:focus-visible` e outline `solid 2px` (3 px a 390). O Space liga e o Enter desliga.
- **Tags:** nenhuma tag "Alerta" visível. A frase "Ação/ETF na carteira recebe entrada e saída…" e o "ainda não marcou" saíram.
- **Detalhe (mesa):**
  - NVDA e BTC abrem com o interruptor e a ajuda "Entrada e saída saem com ou sem o ativo na carteira. Desligado, nada sai no Telegram para esta estratégia.", sem tag "Alerta";
  - **FAIL (P2-1):** depois de desligar NVDA na linha, o detalhe aberto mostra "ligado". Clicar nele deixa tudo desligado em vez de religar.
- **Cartão (390):** ajuda visível nos 6 cartões.
- **Filtro:** abre em "Todos", que é a decisão 21 do autor e vai para o rework.

### Demonstração do Monitor, PASS nas 4 larguras

| Cenário | Mensagem | Linha destacada (estado mostrado) |
|---|---|---|
| Entrada sem carteira | NVDA (Ação · USD), "Leitura atual: Compra", "não envia ordem" | NVDA "Em posição · Aberto" (coerente) |
| Saída | SPY (ETF · USD), "Leitura atual: Venda" | SPY **"Em posição"** (P2-2) |
| Cripto com saldo | BTC/USDT, "Leitura atual: Compra" | BTC "Em posição" (coerente) |
| Alerta desligado | "Nenhuma mensagem." | ETH **"Saída / cobertura"**, e o texto diz Venda → Compra (P2-2) |
| Dados atrasados | "Dados atrasados", NVDA, último 23/10 e esperado 26/10 | NVDA **"Pregão aberto · fecha 17:00"**, sem tom de atraso (P2-2) |
| Catálogo sem alerta | "Mudança nos alertas" com o texto novo | vitrine |

Na vitrine:

- a vista própria some e não fica nenhum interruptor;
- "Catálogo · sem alerta" aparece nas 2 linhas/cartões;
- a faixa `role=status` com o texto novo fica acima dos indicadores;
- "Ir para Favoritos" tem ≥ 44 px;
- desmarcar "Recebia alertas do catálogo" esconde a frase datada.

Não existe cenário de mercado fechado: a nota diz "Mercado fechado e feriado continuam só na tela". Isso não mudou nesta rodada e está implementado, então não é achado.

### Favoritos, PASS nas 4 larguras

- Não há "Alertar", "Fora da carteira", switch, sino nem `title` de Telegram visível em nenhuma largura.
- A ajuda das estrelas está presente. As legendas dão 5 "No Monitor" e 2 "Fora do Monitor" (QQQ do lote e AAPL da Descoberta, sem estrela).
- Mensagens das estrelas em QQQ:
  - 1ª estrela: "QQQ 1d entrou no Monitor com o alerta ligado.", e a legenda vira "No Monitor";
  - 1 → 2 estrelas: "o alerta no Monitor fica como estava";
  - tirar as estrelas: "QQQ 1d saiu do Monitor e não manda mais alerta.".
- A vitrine tem a faixa nova e nenhum "Alertar".
- A coluna Estratégia mede 342 px a 1440, 296 a 1280 e 90 a 1024, como o design.md diz.
- Teclado: 85 paradas (mesa) e 69 (390), **0 sem anel**.

### Resultado, Descoberta e Perfil, PASS nas 4 larguras

- **Resultado:** tem a nota nova do modal e não tem "Alertar", "nasce sem alerta" nem "No portfólio".
- **Descoberta:** tem "Promover a favorito", "Favoritos · sem estrela" e a nota nova, sem "tier 3", "Alertar" ou "No portfólio". "Em Favoritos" na linha promovida e no aviso de sucesso não tem desenho (P3-7).
- **Perfil:** tem a frase nova e não tem "catálogo" nem "Alertar".

### Teclado do Monitor

- 53 paradas na mesa e 80 a 390.
- Ficam sem anel 3 na mesa ("Telegram: on", "Tema", "Atualizar") e 45 a 390. Todas são `.btn` do `monitor-theme` em COPIED, ou seja, herdadas.
- Todos os controles do delta têm anel.

### Alturas contra a página viva (mesma API simulada)

| Estratégia | 1440 proto/vivo | 1280 | 1024 | Cartão 390 proto/vivo |
|---|---|---|---|---|
| BTC/USDT | 142 / 158 | 142 / 142 | 142 / 142 | 929 / 845 (+84) |
| NVDA (Binance) | 178 / 178 | 178 / 178 | 178 / 178 | 974 / 913 (+61) |
| SPY | 178 / 178 | 178 / 178 | 178 / 178 | 974 / 913 (+61) |
| SOL/USDT | 141 / 158 | 141 / 141 | 141 / 141 | 929 / 845 (+84) |
| ETH/USDT | 138 / 138 | 138 / 138 | 138 / 138 | 835 / 721 (+114) |
| NVDA (fonte antiga) | 177 / 177 | 177 / 177 | 177 / 177 | 929 / 867 (+62) |

- Na mesa, o interruptor cabe sem crescer a linha. BTC e SOL encolhem 16 px a 1440 porque a tag "Alerta" sai.
- No cartão, o interruptor empurra "Preço" para a linha de baixo, e a ajuda soma 3 linhas (P3-4).

## 6. Coerência design.md × specs × tasks

- **Tasks:**
  - o grupo 8 diz "Nenhuma tarefa edita design.md, specs, .design-digest ou o protótipo", e nenhuma tarefa os edita;
  - as tarefas antigas substituídas estão marcadas ("substituída pela 8.x").
- **Grupo 8 cobre a regra nova:**
  - quem recebe, `tier_filter` ignorado e carteira fora: 8.2/8.3;
  - estrela liga o alerta, lote e Descoberta sem estrela, 422: 8.3;
  - migração Q1/Q2 e semente: 8.1/8.10;
  - transição e `alert-origin`: 8.4;
  - Monitor, Favoritos e textos: 8.6/8.7/8.8;
  - testes, E2E nas 4 larguras, compare e ensaio: 8.9/8.11/8.12/8.13.
- **Grupo 8 cobre os residuais:** `stale_detail` no Monitor (8.5), marca da transição em dry-run e com `failed` (8.4) e 403/404 (8.3, com 7.3 feita).
- **Specs:**
  - `monitor-telegram-favorite-toggle`: o cenário "Unstarred marked favorite remains eligible" saiu e foi trocado por "Unstarred favorite is not eligible";
  - `favorite-telegram-alerts`: cobre entrada e saída sem carteira, carteira Binance fora, atraso a quem tem o ativo no Monitor com alerta ligado, e "(15m)" no aviso;
  - `monitor-multiclass`: traz o interruptor, a vitrine e "Dados atrasados no 15m";
  - `monitor-telegram-alerts`: remove a matriz, o escopo "Em portfólio" e o aviso de falha.
- **Monitor só exibe as estrelas:** o código (`MonitorStatusTab.tsx`, `getTierStars`) não grava tier. O único caminho de gravação de tier é `PATCH /favorites/{id}` (`FavoritesDashboard.tsx:396`), então "dar a estrela liga o alerta" num só lugar fecha a regra.
- **Pontos que o rework da decisão 21 precisa tocar** (ajuda ao pai, não é achado):
  - design.md: decisão 21, Q3, Apply contract ("admin abre em Todos") e Prototype ("visão do admin em Todos");
  - `specs/monitor-multiclass/spec.md`: última frase de "Carteira é só informação da tela" e o cenário "Admin abre o Monitor";
  - tasks: 8.6 (último bullet) e 8.11 ("admin em Todos");
  - `index.html`: o filtro "Todos" ligado.
- **Incoerências menores:** P3-1 a P3-3 e P3-5.

## 7. Achados

### P0: nenhum

### P1: nenhum

A regra nova de Alan (alerta = estratégia própria com estrela, ligada por padrão, desligada no Monitor; carteira fora; catálogo sem alerta; lote e Descoberta sem estrela) está visível e coerente no Monitor, em Favoritos e nas três telas extras. O gate passa e o clone é o vivo.

### P2 (não bloqueiam; cabem no rework já previsto)

- **P2-1 O detalhe aberto não reflete o estado atual do interruptor.** *Mecânico, protótipo.*
  - Onde: `delta.js`, `toggleDetail`. Ele clona `<template data-m22-detail-tpl>` com `aria-checked="true"` fixo.
  - Problema: depois de desligar NVDA na linha, abrir o detalhe mostra "Alerta: ligado". Clicar nele calcula `on = !true` e deixa tudo desligado (6 FAIL, 1440/1280/1024). O contrato pede "o mesmo interruptor" no detalhe, e Alan, ao testar o protótipo, vê dois estados para a mesma estratégia.
  - **Corrigir:** depois de clonar, ler o `aria-checked` atual da linha (`[data-m22-alert=id]`) e chamar `setAlert(id, estado)`.
- **P2-2 Os cenários da Demonstração não mudam a linha destacada, e o atraso por outro tempo gráfico não tem desenho.** *Mecânico, demo.*
  - Onde: `delta.js`, `setScenario`, que só destaca e mostra a mensagem.
  - Problema:
    - "Saída" destaca SPY ainda "Em posição" ao lado da mensagem de Venda;
    - "Alerta desligado" destaca ETH em "Saída / cobertura" com o texto "passa de Venda para Compra";
    - "Dados atrasados" destaca NVDA com "Pregão aberto · fecha 17:00", sem o tom âmbar nem "Sinal em espera" (na d1 os cenários trocavam o estado da linha);
    - o texto novo desta rodada para a linha retida por outro tempo gráfico ("Dados atrasados no 15m · falta 10:30" / "…último 09:30; esperado 10:30", decisão 8, spec `monitor-multiclass`, task 8.5) não aparece em nenhuma tela do protótipo.
  - **Corrigir:**
    - no cenário, trocar a pílula e o estado do mercado da linha/cartão destacado, ou dizer na nota "a linha mostra o estado antes da varredura";
    - no "Dados atrasados", mostrar NVDA 1d em atraso com o texto do `stale_detail`, por exemplo "Dados atrasados no 15m · falta 10:30".

### P3 (aceitos: Apply, protótipo, doc, herdado; não reabrir como P0/P1)

- **P3-1 Q1 e Q2 já foram respondidas e ainda estão abertas.** *Doc.* Alan respondeu às 18:42 de 27/10, as duas com a recomendada. O design.md ainda as lista em Open Questions ("a migração segue a recomendada até a resposta"). **Rework:** mover para as decisões do Design d2, junto com a Q3 ("Em portfólio").
- **P3-2 Nome acessível com a configuração.** *Doc/Apply.* O exemplo da decisão 18 e do spec é "Alerta no Telegram · NVDA 1d · Médias Móveis: Tendência em Virada". O protótipo acrescenta "· Binance Ações", e é isso que distingue as duas NVDA (mesmo ativo, tempo e estratégia). O cenário "Duas estratégias do mesmo ativo" exige nomes diferentes. **Alinhar** o texto: incluir a configuração.
- **P3-3 Amostra entre páginas.** *Amostra.*
  - SOL/USDT (1★, carteira) está no Monitor, mas não existe em `favorites.html`. Lá aparecem 5 "No Monitor" contra 6 estratégias no Monitor, o que vai contra a própria regra "Monitor = favoritos com estrela".
  - A mensagem de entrada cita "Candle: seg., 26 out. (pregão fechou às 17:00)" com o relógio da página na segunda às 15:00, com o pregão aberto.
  - **Corrigir:** somar SOL em Favoritos, ou tirar do Monitor.
- **P3-4 A ajuda se repete em cada cartão a 390.** *Juízo/polish.*
  - A mesma frase aparece 6 vezes, com +61 a +114 px por cartão (ETH 721 → 835, +16%).
  - A decisão 18 só põe a ajuda no detalhe. O spec `monitor-multiclass` manda no cartão e no detalhe, e o protótipo segue o spec.
  - **Alinhar** a decisão 18 com o spec. Se Alan preferir, a 390 a frase pode aparecer uma vez na página.
- **P3-5 O Impact do `proposal.md` está desatualizado.** *Doc.* Ainda diz:
  - "matriz com ação/ETF";
  - "falha da carteira só para cripto";
  - "o default de `notify_telegram` passa a ser falso, e as marcas de quem não é admin são zeradas";
  - "o limite fica só no aviso de falha da carteira Binance".

  Isso contradiz as decisões 3, 5 e 6. Atualizar junto com o rework.
- **P3-6 Tamanhos e linhas longas.** *Polish.*
  - "Catálogo · sem alerta" (`--text-xs` no `monitor-theme`, 10 px) fica abaixo do piso de 11 px do detector. É o mesmo tamanho da `.tag` viva, e "Sem estrela · sem alerta" segue igual.
  - Os `<p>` da Demonstração têm 91 a 96 caracteres por linha.
- **P3-7 "Em Favoritos" da Descoberta sem desenho.** *Apply.* A linha promovida e o aviso de sucesso não estão no protótipo (só o modal), mas o texto exato está na decisão 12.
- **P3-8 A cor do "ligado" usa `--hold`, o verde de sinal.** *Apply.* O DESIGN.md (regra 7) reserva verde/vermelho de trading para preço. O design.md já aceita a cor exata do interruptor como P3: confirmar no Apply, e manter o ícone e o texto.
- **P3-9 A vitrine depende do filtro de estrelas.** *Apply.* `get_favorites` decide a vitrine por `_has_monitor_candidate(rows)` com as linhas já filtradas pelo `tier_filter` da tela. Com "Estrelas: Todas", quem só tem favoritos sem estrela sai da vitrine. O spec `monitor-curated-fallback` fala de "favorito próprio com estrela": decidir no Apply se a condição ignora o filtro.
- **P3-10 Herdados (COPIED, fora do card):**
  - `.btn` do `monitor-theme` sem anel;
  - estrelas de Favoritos com 24 px na mesa e 28 px no celular, que agora são a porta do Monitor, ainda abaixo de 44 px no toque;
  - tabela do Monitor maior que a área de 1024 a 1279 px;
  - rótulos `#707a8a`;
  - reset que zera padding.

  O design.md já aceita esses pontos.
- **P3-11 Processo.**
  - A URL pública serve a d1 até o checkout DEV ter os arquivos novos. A Aprovação de Design precisa disso resolvido, ou de outro link para Alan.
  - `discovery.html` dá BLOCKED no `classify` (informativo).
  - `parse_live_route` captura `surface: existing` como justificativa (já apontado no #1120 e #1121).

Mecânicos: P2-1, P2-2, P3-1, P3-2, P3-3, P3-5. Juízo: P3-4, que Alan pode aceitar como está.

## 8. Veredito

**PASS com rework.** P0 e P1 zerados.

- **Gate:** `clone_gate_ok=True`, `classify(index,/monitor)=PASS`, copied 120.281, 55/55 COPIED e 59/59 DELTA, 0 marcador dentro de tag.
- **Clone:** as 122 regiões COPIED são substring de uma captura viva fresca, e o `live.css` é o vivo.
- **Detector:** 0 achados no `delta.css` e no `delta.js`, tanto no CLI quanto no hook com DESIGN.md (na d1 eram 20). Todos os achados dos HTML estão em COPIED.
- **Browser:**
  - interruptor com semântica, foco, alvo e sincronia corretos nas 4 larguras;
  - Favoritos sem "Alertar", com as mensagens das estrelas;
  - vitrine sem alerta;
  - textos novos nas extras;
  - console limpo e sem rolagem horizontal.

Disposition: o rework já previsto (decisão 21 → "Em portfólio", Q1/Q2 registradas) leva P2-1, P2-2, P3-1, P3-2, P3-3 e P3-5, que são baratos. Os demais P3 ficam aceitos para o Apply.

Perguntas novas para Alan: nenhuma.

## 9. Referências

- **Disco:**
  - `frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/{index,favorites,results,discovery,profile}.html`, `live.css`, `delta.css`, `delta.js`;
  - `openspec/changes/card-1122-favoritos-alertas-acoes-etfs/` (design, proposal, tasks, 14 specs).
- **Vivo:** https://dev.criptofarol.com.br/monitor, `/favorites`, `/profile`, `/combo/results` e `/combo/discovery`, com a API simulada dos scripts do autor.
- **Gate:** `scripts/process-fsm/design_clone_gate.py` + `route-landmarks.yaml` (HEAD `9b83d25e`).
- **Scratch:** `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/c1122B-d2/`.
  - Scripts: `gate.py`, `clonecheck.py`, `hookmode.mjs`, `deltatext.py`, `browser.py`, `probe.py`, `live_heights.py`.
  - Saídas: `gate.out`, `det-*.json`, `hookmode.json`, `asserts.json`, `errors.json`, `info.json`, `heights.json`, `tabwalk.json`, `detect-browser.json`, `livemeas/live_heights.json`, `live1/`, `live2/`.
  - Screenshots: `shots/`.

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
