> Proveniência: Assessment B, segunda onda (detector + gate estático + browser real), papel `assessment-b`, faixa `juizo`, modelo da captura **Opus 5.5** (`claude-opus-5-5`, effort `high`), captura `cf-assess-b-1123-r2.json` (attempt `3745b86c-d648-4b2f-9fa1-3306e2a48350`, capture_sha256 `bc38daad…`), wave `cf-assess-a-1123-r2.json`, birth `3745b86c-d648-4b2f-9fa1-3306e2a48350.birth.json`, cliente claude, superfície claude-desktop, 2026-10-28T06:43Z a 06:58Z.

# Assessment B r2 (detector + browser real): card 1123 · change card-1123-benchmark-exportacao

> Assessor B isolado. Não li o snapshot do Assessment A (nem o da primeira onda nem o `-A-r2.md`), nem o scratch dele. Não houve nested-spawn. Cliente Claude Code (adapter cooperativo, sem modo Auto).
> Este filho escreveu só este snapshot. Scripts, JSON e screenshots ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123B2/` e não são versionados.
> Nenhum servidor local foi aberto. O detector de browser foi injetado por `add_script_tag` em Chromium headless; não existe aba `[Human]` com overlay.
> Motivo da onda: Alan devolveu o card para Design (T6) com a decisão de 28/10/2026 (issuecomment-6462139347): no Decidir, uma referência escolhida vira **coluna extra** por candidato; ordem, ordenação e elegibilidade não mudam.

```
Assessment B 1123 r2
snapshot: .impeccable/critique/1123-card-1123-benchmark-exportacao-B-r2.md (2026-10-28T06:58Z)
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == HTTPS em 7/7 (HTTP 200; a pasta / serve o index.html); index/favorite/favorites/live.css == r2 (c1123r2/out e tabela do r2) byte a byte
detector CLI: delta 0 (index, favorite, discovery, delta.css, delta.js) · herdado 41 (favorites 2 COPIED + live.css 39) · igual ao r1 e ao r2
detector browser (Decidir, 3 estados × 1440/390): DELTA = th-hint 10 px (classe viva), 1 low-contrast 4,48:1 (token vivo), line-length ~95 car., "5 de 5 candidatos" 10 px (vivo reembalado); COPIED 28–51 por estado
gate: design_token_gap=None · evaluate_clone_gate=True · clone_gate_ok=True · classify(index,/combo/results)=PASS (56249) · discovery 47595 BLOCKED (informativo)
clone: 13/13 COPIED do discovery.html novo são substring literal da captura r3 e da minha recaptura fresca (que saiu byte-idêntica à do r3); 37/37 nas 4 páginas; 0 marcador dentro de tag; 0 byte do body fora de marcador
browser: gate do autor reexecutado 348/348 PASS (bate com o design.md); meus asserts 197/197 PASS a 1440×900 e 390×844 (toque) · 0 console.error/warning, 0 pageerror, 0 ≥400, 0 requestfailed · sem rolagem horizontal
P0: nenhum
P1: nenhum
P2: nenhum
P3: [Apply, aceito] motivo de "Sem comparação" não quebra e invade a coluna Ação · [herdado] th-hint 10 px, −3.2 p.p. 4,48:1, Promover cortado a 1440 · [polish] linha ~95 car. na faixa · [demo] "Sem amostra", "amostra vencida" e reativação sem recálculo não demonstrados · [demo] retorno (extra) do BTC/USDT ≠ janela inteira com 0 trades fora · [Apply, aceito] troca no meio do cálculo sem cancelar o timer · [processo] discovery BLOCKED no catálogo
verdict: PASS
```

- Tupla (só leitura): `bound_card=1123` · `q_git=card-1123-benchmark-exportacao` @ `9b83d25e` · Status=**Design**, conforme o prompt do pai.
- Pacote não commitado (`??`). Não houve `process_event`, commit, push, Gist, comentário, restart nem mudança de Status.
- `design.md` sha256 `2f606e3a…` igual no início e no fim da onda.

## 1. Digest servido == local; r2 intocado

| Arquivo | sha256 (disco = HTTPS) | Mudou no r3? |
|---|---|---|
| `index.html` (a pasta `/` serve o mesmo) | `7a1dd22a9b45c4581b650a9146d831a3edb8b93b3d92023ea30c388107ef132f` | não: = `c1123r2/out/index.html` e tabela do r2 |
| `favorite.html` | `9ec8f65d63db69d326d9cc2068ed3b0cb9dfeb957fab79f909e212681cbe66ec` | não: = r2 |
| `favorites.html` | `843406787f1c3bc0fd4491234490770592a01e6a1ef1613dbf7960cb0a097b33` | não: = r2 |
| `live.css` | `353ac045db2df0a13512af6bc3268d64eb4ad256a821969eb7c8118b1ba832f6` (= `index-DOHmvARO.css` vivo) | não: = r1 = r2 |
| `discovery.html` | `6c2af663c4af51bca907621dc455c1ec4cf9134e24cf5f97d65b5a3ea87de740` | sim (r2: `1f1b59db…`) |
| `delta.css` | `ad738de29c63c802af3e3175cec83e8edbfe440f83ef8d17d92de17e1d5d0c3a` | sim (r2: `7fe4936d…`) |
| `delta.js` | `8578c21f1c52f7610eecfc27f35c6d0542b02444cb2c04ee8aa9bf160e0b171c` | sim (r2: `99104f38…`) |

- Os 7 respondem HTTP 200 (`text/html`, `text/css`, `text/javascript`). Os 7 sha batem com a tabela de Prototype Validation do design.md.
- O r2 vem de duas fontes independentes da palavra do autor: a saída de montagem do r2 (`c1123r2/out/`) e a tabela do `c1123r2/pv.md`. Os mtimes de `index/favorite/favorites` (27/10 14:08) e `live.css` (27/10 13:45) também não foram tocados no r3.
- Os sha do snapshot B da primeira onda (`a739f578…` etc.) são do **r1**, anteriores ao rework r2; não servem de base para "igual ao r2".

## 2. Detector Impeccable

### 2a. CLI (`node .agents/skills/impeccable/scripts/detect.mjs --json`)

| Alvo | exit | Achados | Região |
|---|---|---|---|
| pasta do protótipo | 2 | 41 = 2 (`favorites.html`) + 39 (`live.css`) | — |
| `index.html` / `favorite.html` / `discovery.html` | 0 | `[]` | — |
| `delta.css` / `delta.js` | 0 | `[]` | — |
| `favorites.html` | 2 | 1 `gray-on-color`, 1 `flat-type-hierarchy` | COPIED (estrelas e escala vivas) |
| `live.css` | 2 | 24 `gray-on-color`, 6 `ai-color-palette`, 4 `side-tab`, 2 `overused-font`, 1 `border-accent-on-rounded`, 1 `gradient-text`, 1 `layout-transition` | CSS vivo inteiro |

- **Delta: 0.** **Herdado: 41.** Mesmas contagens do r1 e do r2.

### 2b. Detector no browser (Decidir; elementos visíveis)

`detect-antipatterns-browser.js` injetado, `impeccableDetect({serialize:false})`, cada elemento classificado pelo marcador `COPIED`/`DELTA` aberto (o walker respeita os pares `DELTA` aninhados dentro da tabela COPIED), por classe `b23*` ou pela Demonstração.

| Estado | COPIED | DELTA | DEMO | PAGE |
|---|---|---|---|---|
| 1440 padrão | 50 | 2 (`tiny-text` "5 de 5 candidatos", `line-length` faixa) | 1 | 2 |
| 1440 SPY | 50 | 5 (+ `th-hint` 10 px em 2 regras, `low-contrast` −3.2 p.p.) | 2 | 2 |
| 1440 CRCL | 50 | 5 (`th-hint` em 2 regras, `line-length` da faixa e do resumo CRCL, "5 de 5") | 6 | 2 |
| 390 padrão / SPY / CRCL | 41 | 1 / 3 / 3 | 1 / 2 / 6 | 2 |

Achados no DELTA:

- `tiny-text`/`undersized-ui-text` em `span.th-hint` "Δ CAGR · período comum" (10 px). É a classe viva da tabela (a mesma de "100% velas" e "cobertura" no COPIED): herdado.
- `low-contrast` 4,48:1 em `b` "−3.2 p.p." (`#f6465d` sobre `#1e2329`, só a 1440). É o token vivo `--accent-danger`, o mesmo do "−20%" de Max DD no COPIED: herdado.
- `tiny-text` 10 px em "5 de 5 candidatos · página 1 de 1": `span.text-xs` vivo reembalado no DELTA do Exportar (igual ao r1).
- `line-length` ~95 car./linha a 1440 em `p.b23-xref-text` e `p.b23-xref-sum` (`max-width: 75ch` a 13 px). Polish.
- Nenhum achado DELTA no diálogo nem nas células.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD)

```
lines1-3 ['UI impact: affected', 'live_route: /combo/results', 'surface: existing']
design_token_gap None
parse_live_route ('/combo/results', 'surface: existing') surface existing
evaluate_clone_gate True
clone_gate_ok True
index.html /combo/results classify PASS copied_utf8_sum 56249
favorite.html /combo/results classify PASS copied_utf8_sum 51912
favorites.html /favorites classify PASS copied_utf8_sum 89029
discovery.html /combo/discovery classify BLOCKED copied_utf8_sum 47595
```

- Os tokens D4 estão nas linhas 1 a 3, cada um em linha própria. O canônico passa e `copied_utf8_sum` bate com o design.md (56.249; discovery 47.595; favorites 89.029).
- `discovery.html` BLOCKED: o catálogo pede marcos do Montar, a captura é o Decidir. O gate só lê o canônico (informativo, igual ao r1/r2).

## 4. Clone contra a captura (fora do DELTA)

- Reexecutei o `capture.py` do r3 com saída no meu scratch (`live1/`): bundle vivo de hoje, folha `index-DOHmvARO.css`, 0 erros a 1440 e 390. **A minha `discovery.html` e a `discovery-390.html` saíram byte-idênticas às do r3** (`0624b8d0…`, `8f046026…`); a do r1 era outra (`166310f0…`), então o Decidir foi de fato recapturado.

| Página | COPIED | DELTA | Substring da recaptura fresca | Substring da captura r3 | Marcador dentro de tag | Body fora de marcador |
|---|---|---|---|---|---|---|
| `index.html` | 7 (56.200 B) | 8 (18.212 B) | 7 | 7 | 0 | vazio |
| `favorite.html` | 7 (51.863 B) | 8 (14.682 B) | 7 | 7 | 0 | vazio |
| `favorites.html` | 10 (88.959 B) | 10 (5.991 B) | 10 | 10 | 0 | vazio |
| `discovery.html` | 13 (47.504 B) | 14 (25.407 B) | 13 | 13 | 0 | vazio |

- No `discovery.html`, 11 das 13 regiões COPIED só existem na captura do Decidir (1440 e/ou 390); a 1ª (cabeça) e a última (rodapé) são comuns às capturas.
- O cabeçalho "Contra …" e as 5 células são pares `DELTA` próprios dentro da tabela COPIED, cada um com o `result_id` no nome; a faixa, o diálogo e o JSON também estão em `DELTA`. Os bytes batem com a tabela do autor.

## 5. Browser real

- Playwright Python, Chromium headless shell 1243, `colorScheme: dark`, `pt-BR`, fuso São Paulo. URL pública `https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/discovery.html` (e as outras 3 páginas para carga, console e rolagem).
- Viewports: 1440×900 e 390×844 (`isMobile`, `hasTouch`, DPR 2). Contexto novo por largura, `sessionStorage` limpo.
- **Erros:** 0 `console.error`/`warning`, 0 `pageerror`, 0 resposta ≥ 400, 0 `requestfailed`, nos meus contextos e nos do gate do autor.

### 5a. Gate do autor reexecutado

Copiei `c1123r3/gate.py` para o meu scratch (imagens no meu scratch) e rodei sem mudar assert: **348/348 PASS**, `problems: []`. Bate com o design.md.

### 5b. Asserts próprios (`browser2.py`): 197/197 PASS (94 a 1440, 97 a 390, 6 de carga das outras páginas)

**Padrão.** Ranking 1 BTC/USDT, 2 NVDA, 3 SOL/USDT, 4 SPY, — PENGU/USDT; "Ordenar por" = `delta_cagr_vs_bh` com 2 opções (`calmar_ratio`, `delta_cagr_vs_bh`). Faixa "Coluna extra · Nenhuma", sem resumo, gravação, aviso nem meta; 5 células e cabeçalho ocultos; gatilho "Comparar com outra referência" ≥ 44 px; frase "Referência do ranking: o próprio ativo… não mudam com a coluna extra…"; região viva `role=status`.

**Teclado e seletor.**
- Tab chega ao gatilho com anel `2px solid rgb(59,130,246)` e `aria-haspopup=dialog`; Enter abre.
- "Escolher referência da coluna extra", `aria-modal=true`, foco na busca, fundo travado; 640×720 a 1440 e 390×844 (tela cheia) a 390.
- 1ª opção "Próprio ativo · Padrão · Sem coluna extra…", marcada.
- 14 Tab + 5 Shift+Tab: foco sempre dentro do diálogo.
- Filtros 44 px a 390 (toque) e 36 px a 1440; Cripto = BTC/USDT e WAVES/USDT; busca "zzzz" mostra a mensagem vazia. Demais alvos ≥ 44 (opções 88–125 px).
- WAVES/USDT: rádio `disabled`, "Removido", motivo "Saiu da lista spot…" ligado por `aria-describedby`; clique não marca.
- Antes da escolha: CRCL "Sem período comum com nenhum candidato desta varredura" (tom `warn`); SPY "1 candidato com período comum curto (PENGU/USDT)" (tom `info`).
- Esc fecha sem trocar, devolve o foco ao gatilho e libera a rolagem.

**SPY (escolhido por teclado: Enter em "Usar referência").**
- Durante o cálculo: faixa `busy` com "Calculando contra SPY: k de 5 candidatos…"; células pendentes só com "Calculando…", **sem `%`, `p.p.` nem zero**; sem resumo, aviso nem linha de gravação; foco de volta no gatilho; **ordem igual durante o cálculo**.
- Depois: cabeçalho "Contra SPY · Δ CAGR · período comum" **logo antes de "Ação"**; as 5 células visíveis com `data-label="Contra SPY"`.
- BTC/USDT: "+66.8 p.p.", "SPY +15.25% a.a.", "02/01/2019 – 31/12/2024" e "USDT tratado como USD" (texto visível com ícone, não tooltip). O aviso de moeda aparece só em BTC/USDT e SOL/USDT.
- SPY: "−3.2 p.p." com sinal no texto e tom de queda (cor diferente da alta).
- PENGU/USDT: `short_overlap`, "Sem comparação" + "Período comum de 14 dias: o mínimo é 30.", sem número nem zero.
- Faixa: "SPY · ETF · USD · buy-and-hold", "Retorno de preço, sem dividendos", "…não muda a ordem…", "4 de 5 candidatos com comparação; 1 sem comparação (período comum curto).", aviso de moeda, "Gravada nesta varredura… SPY versão 5… não recalcula", botão "Trocar referência", anúncio "Coluna Contra SPY gravada… A ordem do ranking não mudou.".
- **Ordem e rank idênticos antes e depois** (comparação da lista inteira rank+ativo+`result_id`).
- 390: a célula ocupa a largura do cartão (326 de 356 px) com `::before` "Contra SPY" (rótulo à esquerda); sem rolagem horizontal.
- Planilha: status "…todas as páginas… · colunas (extra) contra SPY"; 37 colunas = Rank global, Candidato, 22 de contexto, 13 "(extra)"; linhas na ordem 1–4, —; Referência = próprio ativo e Referência (extra) = "SPY · ETF · USD"; PENGU (extra) "Histórico insuficiente…" com células vazias; aviso (extra) em BTC e não em NVDA; tipo de retorno (extra) em NVDA; "+66.8" igual à tela.

**Recarregar.** Sem nenhuma célula `busy` já no `domcontentloaded`; faixa `done`; mesmos textos nas 5 células e mesma ordem.

**QQQ.** "Coletando histórico de QQQ na Binance…" com as 5 células "Calculando…" e sem número; depois NVDA "+43.0 p.p.", ordem igual, amostra "QQQ versão 1 (coletada agora)".

**BTC/USDT como referência.** O aviso de moeda passa para NVDA e SPY; sem "Retorno de preço"; BTC contra BTC = "+11.4 p.p.", igual ao Δ do ranking no próprio ativo.

**CRCL.** `no_overlap` e "Sem comparação · Sem período comum com CRCL." nos 5, sem número nem zero; resumo "Nenhum candidato tem período comum com CRCL…"; sem aviso de moeda; ordem igual; motivo na planilha.

**Falha e "Tentar de novo".** Começa em "Coletando… QQQ"; depois `role=alert` "…Nada foi gravado: a coluna continua contra CRCL."; "Tentar de novo" 44 px; coluna CRCL mantida; recarregar depois da falha segue CRCL; "Tentar de novo" grava QQQ.

**Troca no meio do cálculo.** SPY e, 250 ms depois, BTC/USDT: termina em "Contra BTC/USDT", gravado `BTC`, nas duas larguras (ver P3-6).

**Próprio ativo.** Cabeçalho e células somem, faixa "Nenhuma", "Coluna extra removida. O ranking segue igual.", ordem igual, planilha volta a 24 colunas, status sem "(extra)"; recarregar continua sem coluna.

**Outras páginas.** `index`, `favorite.html` e `favorites.html` carregam a 1440 e 390 sem erro e sem rolagem horizontal (são byte-iguais ao r2, já cobertas pelo gate do autor).

### 5c. Medida e aritmética

- **Sobreposição** (`overlap2.py`, retângulo do texto por `Range`, 768 a 1440): o motivo do PENGU/USDT em SPY passa ~68 px da borda da célula e entra na coluna "Ação", por cima da borda do "Excluir" (`shots/el-1440-SPY-pengu-row.png`). Em CRCL passa ~3 px. A causa é `white-space: nowrap` herdado da célula viva; o `max-width: 24ch` do `span` não quebra. Ver P3-1.
- **Largura da tabela:** com e sem coluna a tabela tem 1240 px num wrapper de 1175 (a coluna extra não alarga; as outras colunas cedem). O "Promover" já fica cortado a 1440 sem coluna (defeito COPIED já aceito).
- **Aritmética da amostra** (`numbers2.py`, 12 células válidas): `CAGR = (1+R)^(365,25/dias) − 1` reproduz sCagr e rCagr; a diferença em p.p. bate com arredondamento ≤ 0,05. A única incoerência é a do P3-5.

## 6. Confronto com a decisão de Alan e o spec (só o visível)

| Item | Visto no browser | Disposition |
|---|---|---|
| Referência escolhida no Decidir vira coluna extra por candidato | "Contra <ativo>" nos 5, antes de "Ação", na tabela e no cartão | PASS |
| Ordem do ranking não muda | ordem e rank idênticos antes, durante e depois de SPY, QQQ, BTC, CRCL, falha, recarga e Próprio ativo | PASS |
| Ordenar e elegibilidade por outra referência continuam fora | "Ordenar por" segue com 2 opções; PENGU segue "Baixa amostra", sem rank | PASS |
| Mesmas regras do resultado (período comum, insuficiente sem número, moeda, retorno de preço) | short/no_overlap sem número; aviso só em moedas diferentes; "Retorno de preço" em ETF/ação | PASS |
| Gravada por varredura e usuário, sem recálculo ao abrir/recarregar/exportar | recarga sem "Calculando"; linha de gravação "não recalcula" | PASS. Reativar uma referência já gravada recalcula no protótipo (P3-4). |
| Calculando sem número; coleta; falha com "Tentar de novo" | sim, nas duas larguras | PASS |
| Planilha com 22 campos + 13 "(extra)"; sem elas no padrão | 37 / 24 colunas, Legenda com "(extra)" | PASS |
| Seletor reaproveitado (44 px no toque, desabilitado com motivo, foco, Esc) | sim | PASS |
| "Sem amostra" e "Amostra do candidato vencida" | não demonstrados (nenhum candidato nesses estados) | P3-4 |

## 7. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | "Calculando… k de 5", "Coletando…", alerta de falha, resumo com contagens, linha de gravação | — |
| 3 | Controle | Esc/Cancelar não trocam; falha mantém a anterior; "Próprio ativo" tira a coluna | — |
| 4 | Consistência | Mesmo seletor do resultado; regras iguais; BTC×BTC = Δ do ranking | — |
| 5 | Prevenção de erro | Aviso antes da escolha (CRCL, período curto); WAVES desabilitado | — |
| 8 | Estética | Motivo do insuficiente invade a coluna Ação a partir de 768 px (P3-1) | P3 |

## 8. Achados

### P0: nenhum

### P1: nenhum

### P2: nenhum

Nenhum critério da decisão de Alan nem do spec visível falhou no browser. Os tokens D4 estão em L1–L3; o gate passa; o r2 está intocado.

### P3 (aceitos: Apply, herdado, demo; não reabrir como P0/P1)

- **P3-1 Motivo de "Sem comparação" não quebra e invade "Ação".** *Detalhe de Apply (já aceito no design.md: "largura mínima da célula e quebra do motivo").*
  - Onde: `delta.css` `.b23-xc-off span`, célula PENGU/USDT em SPY/QQQ/BTC (≈68 px) e as 5 células em CRCL (≈3 px), de 768 a 1440.
  - **Correção:** `white-space: normal` em `.b23-xc-off span` (ou na `.b23-xc`). No Apply, a célula deve quebrar o motivo em até 24ch.
- **P3-2 Herdados do incumbente no delta novo.** *Herdado.* `th-hint` 10 px no cabeçalho "Contra …"; `--accent-danger` 4,48:1 sobre a linha `#1e2329` a 1440; "5 de 5 candidatos" 10 px; "Promover" cortado a 1440. Também os 41 achados CLI e os 41–50 achados COPIED por estado no browser.
- **P3-3 Linhas longas na faixa.** *Polish.* ~95 car./linha a 1440 em `.b23-xref-text`/`.b23-xref-sum` (`75ch` a 13 px). **Correção:** `max-width: 65ch`, como o r2 fez nos textos do resultado.
- **P3-4 Estados do spec sem demonstração.** *Demo.*
  - "Sem amostra" (`insufficient_sample`) e "Amostra do candidato vencida em <data>." não aparecem em nenhum candidato.
  - Reativar uma referência já gravada: o spec diz "reactivate without recomputing" e mostra a data dela; o protótipo recalcula ("Calculando contra SPY" ao voltar para SPY).
  - **Correção (Apply):** cobrir os três em 6.3/7.3a do `tasks.md`; o 7.3a hoje não cita "Sem amostra" nem a reativação.
- **P3-5 Retorno (extra) do BTC/USDT incoerente com "0 trades" fora.** *Demo.* Contra SPY e QQQ, BTC/USDT tem "Retorno da estratégia no período comum (extra)" +3532,61% e CAGR +82,06%, mas fica 0 trade fora; os mesmos trades dão +3531,39% (o valor da janela inteira na mesma linha). O mock derivou o retorno do CAGR. Só na planilha, porque a célula não mostra o retorno. O Apply calcula pelos trades.
- **P3-6 Troca no meio do cálculo sem cancelar o timer.** *Apply (já aceito: "cancelamento do job ao trocar de referência").* Em `delta.js`, os dois `tick` dividem `progress` e cada um grava a sua referência ao terminar. No meu teste terminou na última escolha nas duas larguras, mas a ordem depende do tempo.
- **P3-7 Processo.**
  - `discovery.html` dá `classify=BLOCKED` no catálogo, que pede o Montar (informativo).
  - `parse_live_route` captura `surface: existing` como justificativa (recorrente).
  - `role=alert` dentro de região `role=status` na falha (já aceito no design.md).

## 9. Veredito

**PASS.** P0, P1 e P2 zerados.

- **Gate estático:** `clone_gate_ok=True`, `classify(index,/combo/results)=PASS` (56.249), tokens L1–L3 conferidos.
- **Digests:** disco = HTTPS nos 7 arquivos; `index/favorite/favorites/live.css` byte-iguais ao r2; só `discovery.html`, `delta.css` e `delta.js` mudaram.
- **Clone:** 13/13 COPIED do Decidir novo são trechos literais da captura r3, que a minha recaptura reproduziu byte a byte.
- **Detector:** 0 no CLI do delta; no browser, só herdados e comprimento de linha.
- **Browser:** gate do autor 348/348; meus 197/197 cobrem seletor, coluna nos 5, ordem e rank idênticos, moeda, período curto, sem período comum, calculando, coleta, falha, Próprio ativo, planilha, teclado e foco, console e rolagem.

Disposition: os P3 ficam aceitos para o Apply. Se o pai ainda tiver um ajuste barato, o P3-1 (uma linha de CSS) e o P3-4 em `tasks.md` são os de maior retorno. Nenhum deles justifica rework.

## 10. Referências

- **Disco:** `frontend/public/prototypes/card-1123-benchmark-exportacao/*`; `openspec/changes/card-1123-benchmark-exportacao/design.md` (sha `2f606e3a…`), `specs/discovery-leaderboard/spec.md`, `tasks.md`.
- **HTTPS DEV:** https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/discovery.html
- **Decisão:** https://github.com/oalansilva/crypto/issues/1123#issuecomment-6462139347 (lido por `gh api`, sem comentar).
- **Scratchpad** (não versionado): `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123B2/`.
  - Scripts: `capture.py`, `clonegate.py` e `gate.py` (cópias do r3), `clonecheck.py`, `browser2.py`, `shot.py`, `overlap2.py`, `numbers2.py`, `dumpdata.py`.
  - Saídas: `det-*.json`, `served/`, `live1/`, `clonecheck.json`, `clonegate.out`, `author_gate.out`, `browser2.json`, `overlap2.json`, `gate-shots/`, `shots/`.

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5, effort high)
