`proveniência: Assessment A (design review produto/UX/a11y/fidelidade) → Opus 5.5 (claude-opus-5-5, effort high)` — captura `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/f34a4e0e-5dff-4fe2-9a98-4a3fda87bbb1/scratchpad/1120/assess-a1.capture.json` (attempt `090c4eab-2c0c-444e-9c80-9da4210a2bfe`, band `juizo`, role `assessment-a`, capture_sha256 `c43eaa6596ae1b38f6d025ab33b9d3a06b35628379253767c92dacc58a8340a1`, arquivo sha256 `26e242f1d6e9b776e6af2a3088e3f8834ff9fff05f43aaa31c5a83fe806c5f5f`).

# Assessment A — card 1120 · change card-1120-lote-multiclasse

> Avaliador A isolado (produto / UX / acessibilidade / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem resultados do Assessment B (não li `*1120*-B.md`, não rodei `detect.mjs`). Sem spawn de filho, sem `process_event`, sem arraste de Status, sem comentário no issue. Sem edição de `design.md`, OpenSpec, HTML/CSS/JS do protótipo, `DESIGN.md`, `backend/` ou `frontend/src/`. Única escrita: este arquivo.

## Metadata

- card: 1120 — Comparar e otimizar combos em lotes de cripto, ações e ETFs
- change: `card-1120-lote-multiclasse`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1120-lote-multiclasse`
- branch / q_git: `card-1120-lote-multiclasse` @ `e762e470` (pacote untracked; `git status` só com as duas pastas `??`)
- tuple: `bound_card=1120` · Status no board (GraphQL, projeto 1) = **Design** (conferido, não arrastado)
- data (UTC): 2026-10-24
- cliente: Claude Code (adapter cooperativo, sem modo Auto)
- Issue: REST `gh api repos/oalansilva/crypto/issues/1120 --jq .body`. Fronteira = body grelhado (Problema / História / Entra / Não entra + 5 decisões de Alan de 24/10/2026). Decisões não reabertas.
- `design.md` sha256 `08f581da0f20c10a10dfdeea8c333f32d4121ed60c9398e0f8b1764b0dd4838e` (== prompt)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Setup Impeccable: `context.mjs --target …/index.html` carregou PRODUCT.md + DESIGN.md; modo **critique**, superfície Operate (refinamento clone+delta). `DESIGN.md` é a autoridade visual e não foi tocado.
- Tooling: Playwright Python + Chromium headless shell 1243 (arm64), `pt-BR`, tema escuro, 1440×900 e 390×844, **na URL pública** `https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/` (+ `configure.html`, `optimize.html`), contexto novo por página × largura. Contraste por cor computada (canvas → sRGB, fundo efetivo compondo os ancestrais), sem axe-core. Screenshots/JSON de trabalho em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/f34a4e0e-5dff-4fe2-9a98-4a3fda87bbb1/scratchpad/1120/A/` (não versionados). Sem servidor local.

## Digest (disco == servido)

| Arquivo | sha256 disco | HTTP | servido |
|---|---|---|---|
| `index.html` (também a pasta `/`) | `ddb921cd2c24098f9d0a899ca01551037d0a20c7af47ccde19bb9da929123922` | 200 | IDENTICAL |
| `configure.html` | `975fbed5528746441b17d430fd5a0dc1c444e12601c0e4b028c40b01a55f8622` | 200 | IDENTICAL |
| `optimize.html` | `4605255e5c1d1b7a5abc8b368edfaa1803d028b6a6b67bf297a74175d709cefb` | 200 | IDENTICAL |
| `live.css` | `da9e66e69f963f98815d45baf15fbb0dc8eea0f31b3225a363a8be171b5abf7b` | 200 | IDENTICAL |
| `delta.css` | `9a8236917c1685d260592bcb90e72af54a919431e13e781f9fad0556e26eebfb` | 200 | IDENTICAL |
| `delta.js` | `66c996804bdccb4d22ee5da609b944dbca8bca946d3d89f357a21b22ad4b9320` | 200 | IDENTICAL |

Disco == servido == `design.md` §Prototype Validation. Extra: `live.css` == `https://dev.criptofarol.com.br/assets/index-B4ZdBYXJ.css` (bundle vivo servido hoje em `/favorites`) byte a byte. Zero erro de console, `pageerror` ou resposta ≥ 400 nas 6 cargas (3 páginas × 2 larguras) e nos fluxos clicados.

## Tokens parseáveis (rubrica D4)

`design.md` L1–L3, linhas próprias, sem espaço extra:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Bloco D4 em L5 **idêntico** ao da skill `design-critic` (comparação de string exata). `design_clone_gate`: `design_token_gap` = None, `classify(index.html, /favorites)` = PASS, `clone_gate_ok` = True, canônico = `index.html`. Regiões clonadas declaradas no §Context e marcadas `COPIED` (45/45, 10/10, 9/9 pares); delta só em `DELTA` (42/42, 7/7, 6/6). Extras `configure.html` e `optimize.html` nunca canônicos. Nenhuma página é ANTES/DEPOIS nem grelha de N estados; Demonstração no fim, no fluxo, sem `position:fixed`. **ok.**

## Cobertura do body (Entra / Não entra)

| Item do Entra | Decisão / spec | Protótipo |
|---|---|---|
| Lote misto pelo catálogo; cada ativo com classe, fonte, sessão, ajuste e moeda guardados | 3, 4, 12 · `multiclass-batch` | seletor com BTC/USDT + NVDA + SPY; Confirmar lote "1 cripto (USDT), 1 ação (USD), 1 ETF (USD)"; favorito com "Binance Ações · pregão regular de Nova York · ajustado por split · 252 pregões/ano" |
| Mesmas regras do backtest individual; bloqueio só-cripto cai só onde validado | 3, 11, 13 | Descoberta segue recusando (sem clone, mesmo critério do #1119). **Furo:** na Otimização, 15m/1h/4h com ação/ETF aparecem rodando (ver P1-2) |
| Tempo que não serve: ação/ETF fora com motivo antes de começar; cripto roda | 4, 6 · cenário "Lote misto em 5m" e "Otimização com janela fixa…" | 1m/5m (Combo) e 1m/5m/30m (Otimização) marcados "(só cripto)"; texto âmbar antes de rodar, "Ficam fora" no Confirmar, estado "Fora" no painel. **Falta** o "fora por cobertura" da Otimização em 15m/1h/4h |
| Lote grande: qualquer tamanho; contagem de coleta antes de confirmar; progresso por ativo; pausar/cancelar | 5, 7, 9, 10 | "Confirmar lote de 2.431 ativos · 2.388 de 2.431 precisam de coleta"; "5m do intrabar · página 7 de 20" com `progress`; Pausar → Pausando… → Pausado → Retomar; Encerrar; "Mostrar mais 50" |
| Estado por ativo: progresso, sucesso, insuficiência, rejeição, falha; problema não vira resultado nem trava os outros | 8 | "Lote com problemas": Sucesso, Sucesso · precisão diária, Insuficiente, Rejeitado, Falha, Pulado, Fora, cada um com ícone + texto + motivo e "Nenhum favorito gravado" |
| Precisão diária visível, com trecho, nunca em silêncio | 8, 9, 14 | âmbar no estado, nota do lote "Precisão diária em N ativos", e em Favoritos "Precisão diária · sem 15m de 11 nov. 2014 a 18 mai. 2026" |
| Mesma amostra; pausa/cancelamento/retomada preservam resultados e identidade | 10, 11 | "tentativa 38 de 60 · todas na mesma amostra"; mesmo id `7f3c2a91` após pausa; "histórico coletado; otimiza ao retomar, na mesma amostra"; Encerrar mantém BTC e marca "Não rodou" |
| Resultado vira favorito (nota "gerado em lote"), aceite depende do #1122 | 12 | "Gerado em lote 7f3c2a91 · 24 out. 2026"; "Atualização diária: ainda não para ações e ETFs". **Furo:** estrelas do Monitor, Telegram e Revalidar vivos nas linhas de ação/ETF (ver P1-1) |
| Comparação numa lista só, ordenável, classe + moeda + convenções por linha, filtro por classe, USD ≠ USDT | 14 | filtro Classe com contagem; chip + moeda por linha (uma moeda só por linha, conferido nas 10 linhas/cartões); ATR com moeda; Ordenar mistura classes; `?lote=` com faixa |
| Verificação (1d e 5m; regressão cripto) | 15 | 1d e 5m demonstrados no Combo e na Otimização; regressão é teste (aceitável: evidência, não tela) |

Não entra — sem geração de estratégia, sem ordem, sem Descoberta com ação/ETF, sem benchmark/exportação nova (o "Exportar" é o vivo). **Vazamento visível:** o #1122 (alertas/Telegram/Monitor/Revalidar de ação/ETF) não vazou em comportamento, mas os controles vivos continuam ativos nas linhas de NVDA/SPY sem estado nem motivo (P1-1).

## Fidelidade (clone da página viva)

- `live.css` é o bundle vivo inteiro, conferido por sha256 contra o servido em DEV hoje (`index-B4ZdBYXJ.css`, bundle JS `index-BvxVmoZs.js` = o citado no `design.md`).
- Strings vivas presentes no bundle JS de DEV: "Catálogo operacional para escolher…", "Como usar Favoritos", "Notificar Telegram desligado", "Revalidar na janela recente", "Ready to Optimize", "Template Information", "Parameter Optimization Ranges", "Descoberta sistemática (varredura)". `FavoritesDashboard.tsx` vivo: `td.symbol-col aria-label={fav.symbol}` e `td.strategy-cell aria-label=…` (L1604/L1613) reproduzidos no clone; `ComboOptimizePage.tsx` vivo põe o `BatchProgressPanel` na coluna `lg:col-span-1` (L271/L429), igual ao clone.
- "o lote vem depois" sumiu das três páginas (0 ocorrências), como manda a decisão 6.
- Não recapturei a página viva autenticada (a captura do autor usa API simulada); a fidelidade foi conferida por CSS byte a byte, marcação viva no código-fonte e strings do bundle. **Fidelidade ok.**
- Incumbentes visíveis (não são delta): botões "Otimizar"/"Run Optimization" com 22 px de altura (reset `* {padding:0}` vivo); rótulos dos filtros de Favoritos `#707a8a` sobre `#1e2329` a 3,65:1 em 11,5 px; "Backtest atualizado" verde-escuro a 3,54:1; descrição da estratégia 4,46:1; selects de Favoritos com `outline:none` e sem anel de foco.

## Acessibilidade (medida)

- Contraste do delta (cor computada sobre fundo efetivo, 1440 e 390): chips Cripto 13,55:1 · Ação 10,73:1 · ETF 9,10:1; moeda 16,35:1; precisão diária âmbar 11,59:1; intrabar azul 10,73:1; convenções/limitações/período/lote 6,81:1; faixa do lote 15,21:1; texto antes de rodar 5,56:1; nota da classe 8,83:1; Confirmar `dt` 6,12/5,60:1, `dd` 14,69/13,45:1; "Confirmar e rodar" 12,18:1; estados Insuficiente/diária 10,42:1, Rejeitado/Falha 7,35:1, Pulado/Fora 6,12:1; links 9,64:1. **Tudo ≥ 4,5:1.**
- Alvos: "Mostrar todos os favoritos", Confirmar/Voltar, Pausar/Retomar/Encerrar, "Mostrar mais", links do fim do lote = 44 px. Filtros por estado 36 px (44 px só com `pointer: coarse`) — acima do mínimo de 24 px.
- Teclado: Otimizar/Run Optimization alcançáveis com anel `#3b82f6`; Enter abre o Confirmar com foco no título (anel amarelo); Tab → Confirmar e rodar → Voltar; Voltar devolve o foco ao botão de rodar; Confirmar e rodar leva o foco ao título do lote; Tab percorre filtros por estado (`aria-pressed`), link "abrir em Favoritos", Pausar, Encerrar. **Falha:** ao ativar Pausar, o botão vira `disabled` e o foco cai em `<body>` durante todo o "Pausando…" (medido nas 4 combinações página × largura); só volta (para Retomar) quando a etapa termina. **Falha:** "Mostrar todos os favoritos" devolve o foco ao filtro Classe, mas o select vivo não tem anel de foco visível (`outline:none`, `box-shadow` transparente).
- Leitor de tela (árvore de acessibilidade do Chromium, linha NVDA): o conteúdo novo está na árvore, mas o **nome** da célula Symbol é só "NVDA" e o da célula Estratégia é o `aria-label` vivo (título + apelido + descrição), sem classe, moeda, precisão nem convenções; o nome da linha também. Navegando por célula/linha, "Ação · USD" e "Precisão diária…" não são anunciados.
- `role=status` só na linha viva do lote e na faixa do lote; Confirmar sem `role=dialog` (correto, no fluxo). Ícone + texto em todo estado.
- Sem rolagem horizontal do documento em nenhuma página, largura ou estado (padrão, Confirmar, painel, problemas).

## Responsividade

- 1440: Favoritos com 6 colunas de filtro; coluna Período some (`display:none`), período efetivo vai para a célula da estratégia, como o design diz. Linhas de 192–283 px → ~3 linhas por tela de 900 px.
- 390: cartões de 555–685 px (NVDA 685); bloco novo legível, sem corte. Chip + moeda quebram como "Ação ·" / "USD" na célula Symbol a 1440 (o ponto fica pendurado no fim da linha).
- Painel do lote: lista em grade a 894 px (Combo 1440) e cartões abaixo de 620 px (Otimização 1440 = 350 px, e 390 em ambas), via container query. Na Otimização a 1440 o Confirmar mede 1.034 px de altura e o painel vive na coluna estreita enquanto a coluna larga segue "Ready to Optimize" vazia.

## Heurísticas Nielsen (0–4) — só neste snapshot

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 3 | linha viva, progresso por ativo e "Pausando…" claros; na Otimização o painel fica espremido ao lado de um painel vazio |
| 2 | Match between system and real world | 3 | "Insuficiente", "Pulado", "Fora" explicados em palavras; Otimização manda usar 15m/1h/4h que também ficam fora |
| 3 | User control and freedom | 3 | Pausar/Retomar/Encerrar e Voltar; lote pausado + novo lote sem regra |
| 4 | Consistency and standards | 2 | estrelas/Telegram/Revalidar vivos em ação/ETF com Monitor só cripto; "Sucesso" verde em Favoritos e branco no Combo/Otimização; texto sob demanda antigo na cripto |
| 5 | Error prevention | 3 | Confirmar com contagem e "Ficam fora" antes de começar; furo dos 15m/1h/4h na Otimização |
| 6 | Recognition rather than recall | 3 | classe e moeda coladas ao símbolo; precisão onde o olho já está |
| 7 | Flexibility and efficiency | 3 | filtros por estado, `?lote=`, Mostrar mais 50; sem "rodar de novo só os que falharam" |
| 8 | Aesthetic and minimalist design | 2 | célula da estratégia com até 9 linhas; ~3 linhas por tela a 1440; cartão de 685 px |
| 9 | Recognize, diagnose, recover | 3 | Falha diz motivo e "rode de novo mais tarde"; sem atalho de recuperação |
| 10 | Help and documentation | 3 | nota da classe e texto antes de rodar em linguagem de operador |
| **Total** | | **28/40** | Good |

## Design specificity

Autoral para o produto. O delta responde à pergunta real do pesquisador ("posso comparar estas linhas?") com o chip de classe + moeda colado ao símbolo e a precisão no bloco que ele já lê; usa âmbar só quando a precisão caiu; o Confirmar no fluxo diz "2 de 3 precisam de coleta — NVDA (5m do intrabar), SPY (1d e 5m do intrabar)", que é exatamente o fato que muda a decisão de rodar. Tokens do produto (`--accent-primary`, `--ap-info-*`, `--ap-warn-*`, `--ap-danger-*`), sem mundo visual novo. Não é intercambiável.

## Cognitive load

Confirmar lote: 5 grupos (Vão rodar, Coleta, Fora, Configuração, Favoritos) — no limite, mas cada um com uma frase. Painel do lote: até 8 filtros por estado visíveis num lote com problemas (>4 opções), mitigado por mostrar só os estados presentes. Favoritos: o bloco da estratégia de ação/ETF soma 9 linhas (título, descrição, apelido, atualização, precisão, convenções, limitações, período efetivo, lote) — acima de 4 itens por grupo, e numa lista que um lote grande pode encher com milhares de linhas. Carga média-alta em Favoritos, média no lote.

## What's working

- Confirmar lote no fluxo: contagem de coleta, quem fica fora e por quê, configuração e regra de favoritos, sem modal, com foco no título e Voltar devolvendo o foco. Resolve a decisão "qualquer tamanho com contagem" sem segunda confirmação.
- Estados por ativo legíveis e honestos: cada problema diz o porquê e "Nenhum favorito gravado"; precisão diária aparece no estado, na nota do lote e no favorito com o trecho.
- Pausa ao fim da etapa com "Pausando…" que nomeia o ativo e a etapa, e "histórico coletado; otimiza ao retomar, na mesma amostra" — a promessa de mesma amostra fica visível sem jargão.

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.

### P1 — deve corrigir antes de PASS

- **[P1-1 · produto · escopo/estado] Favoritos, linhas e cartões de NVDA e SPY: estrelas do Monitor, Telegram e Revalidar continuam vivos e ativos.** A decisão 12(b) põe atualização, alertas, Telegram, estrelas no Monitor e Revalidar de ação/ETF no #1122 (Não entra do body) e o spec `crypto-only-mvp` mantém o Monitor só cripto; mas o clone mostra NVDA já com 1 estrela (contando em "Acompanhar 3", "Fila principal do Monitor"), o botão Telegram "Off"/"TG" clicável e "Revalidar" ativo, sob o cabeçalho vivo "marque estrelas … e depois acompanhe no Monitor". Alan ligaria o Telegram de NVDA ou daria 3 estrelas e nada aconteceria — exatamente o "em silêncio" que o card proíbe. **Correção:** nas linhas e cartões de ação/ETF, estrelas, Telegram e Revalidar visíveis mas `aria-disabled`, com uma linha de motivo no padrão já usado ("Monitor, Telegram e Revalidar: ainda não para ações e ETFs"), focáveis e anunciados como no favoritar recusado do #1119; o resumo por estrelas não conta ação/ETF como fila do Monitor (ou diz "N ações/ETFs ainda fora do Monitor"). Registrar na decisão 12 e no spec `favorites-class-comparison`.
- **[P1-2 · produto · estado faltante] Otimização: ação/ETF em 15m, 1h e 4h aparecem rodando, contra a decisão 4 e o cenário "Otimização com janela fixa que o 5m não cobre".** Em `optimize.html`, trocar o Timeframe para 15m/1h/4h mantém "Lote de 3 ativos (1 cripto, 1 ação, 1 ETF)…" e o Confirmar lista os três em "Vão rodar". E o texto de 1m/5m/30m na Otimização diz "para incluí-los, use 15m, 1h, 4h ou 1d" — três desses quatro tempos também os deixam fora nesta tela (o 5m começa em mai. 2026; a janela é jan. 2024). O Apply segue o protótipo como spec de layout e o E2E "seguindo o protótipo". **Correção:** em `optimize.html`, 15m/1h/4h com ação/ETF → texto âmbar "Fora antes de começar: NVDA (Ação), SPY (ETF) — o 5m deles começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período.", o mesmo em "Ficam fora" e no estado "Fora"; e o conselho de 1m/5m/30m na Otimização vira "use 1d aqui ou o Combo". Pôr os dois textos na decisão 6.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2 · mecânico · a11y] Pausar: o foco cai em `<body>` durante "Pausando…".** O botão vira `disabled` com foco nele; a pausa pode durar uma otimização inteira. Correção: `aria-disabled` no lugar de `disabled` (foco fica em "Pausando…"), ou mover o foco para o título do lote.
- **[P2 · mecânico · a11y] Nome acessível das células esconde classe, moeda e precisão.** `td.symbol-col aria-label="NVDA"` e `td.strategy-cell aria-label="<título apelido descrição>"` (vivos) viram o nome da célula e da linha; quem navega por tabela ouve "NVDA" sem "Ação · USD" e a estratégia sem "Precisão diária…". Correção no delta: tirar o `aria-label` dessas duas células (o conteúdo já é texto) ou incluir classe, moeda e precisão nele.
- **[P2 · mecânico · a11y] Foco devolvido ao filtro Classe é invisível.** "Mostrar todos os favoritos" põe o foco no select, que herda `outline:none` do vivo. Correção: `:focus-visible` com o anel do produto nos selects de `.fav-filters` (no mínimo no Classe).
- **[P2 · juízo] Otimização: painel do lote na coluna estreita (350 px) com "Ready to Optimize" vazio ao lado.** Fiel ao vivo, mas o painel novo (filtros, lista, até milhares de ativos) cabe mal ali e o Confirmar mede 1.034 px. Correção sugerida: com lote ativo, o painel (e o Confirmar) ocupam a coluna larga no lugar de "Ready to Optimize"; a container query continua servindo ao celular.
- **[P2 · juízo] Lote pausado + novo "Otimizar" sem regra.** O protótipo deixa abrir outro Confirmar e o painel do lote pausado some; pela decisão 10 (`/batch/active` = não final mais recente), o pausado voltaria a aparecer depois que o novo terminar. Ver pergunta "Lote pausado".
- **[P2 · juízo] Densidade de Favoritos.** Ação/ETF com 9 linhas na célula da estratégia (283 px a 1440, ~3 linhas por tela; cartão de 685 px a 390). Num lote de milhares, Favoritos vira rolagem longa. O P3 aceito do `design.md` adia "recolher limitações" para "se passar de ~5 linhas por tela" — já passou. Sugestão dentro do Entra (convenções seguem por linha): uma linha "Binance Ações · NY · split · 252/ano" e limitações + "Gerado em lote" atrás de um `<details>` "Limitações e origem".

### P3 — detalhe de Apply (não reabrir como P0/P1)

- **[P3] Token `--fav-up` fora de escopo no Combo/Otimização:** "Sucesso", selo "Concluído" e chip ETF ficam `#eaecef` em vez de verde (em Favoritos ficam verdes). O Apply usa o token global. **aceito-P3-Apply**
- **[P3] Texto sob demanda antigo:** "Histórico sob demanda · coletado quando uma análise pedir" segue na linha de SOL/USDT do seletor; a decisão 6 troca a string. **aceito-P3-Apply**
- **[P3] Amostra do protótipo:** "Ficam fora … não rodam em 5m" e "Configuração · 5m ·" fixos mesmo com 1m/30m; ATR "1834.20 USDT" igual em BTC/ETH/SOL; NVDA/SPY sem janela efetiva no detalhe da Otimização. **aceito-P3-Apply**
- **[P3] Plural:** "Ver os 1 resultados do lote em Favoritos". **aceito-P3-Apply**
- **[P3] Célula Symbol:** "Ação ·" quebra e deixa "USD" sozinho na linha seguinte a 1440; `nowrap` no par chip·moeda. **aceito-P3-Apply**
- **[P3] Linha viva recriada a cada render** (`innerHTML` do painel inteiro); no React o nó `role=status` deve persistir para ser anunciado. **aceito-P3-Apply**
- **[P3] "Só ações/ETFs em 5m → Nada será executado"** não demonstrado; texto e regra já na decisão 6 e no spec. **aceito-P3-Apply**
- **[P3] Incumbentes fora do card:** botões de rodar com 22 px, rótulos de filtro a 3,65:1, "Backtest atualizado" a 3,54:1, descrição a 4,46:1, modal "Strategy Comparison" (admin) sem classe/moeda (métricas em %), `TODO: Date picker (#1120)` no `ComboOptimizePage.tsx` vivo (o design põe o seletor de período como Non-Goal; o TODO fica desatualizado). **aceito-P3 (incumbente/fora de escopo)**

## Persona red flags

- **Alan (pesquisador, monta universo misto):** roda o lote misto na Otimização em 1h porque o texto de 5m mandou "use 15m, 1h, 4h ou 1d"; o protótipo diz que os três rodam, o produto os tiraria (P1-2). Em Favoritos dá estrela em NVDA esperando vê-la no Monitor e liga o Telegram — nada acontece (P1-1).
- **Lote grande (2.431 ações):** a contagem antes de confirmar e o "resta ~9h 40m" funcionam; depois, Favoritos com milhares de linhas de ~280 px e sem "rodar de novo só os que falharam" quando a Binance limitar requisições.
- **Usuário de teclado / leitor de tela:** perde o foco ao pausar; não vê onde o foco caiu depois de "Mostrar todos os favoritos"; navegando por célula não ouve a classe, a moeda nem a precisão diária.

## Questions to consider

- Com milhares de ativos, falhas por limite da Binance tendem a vir em bloco: vale um "Rodar de novo os N que falharam" no fim do lote (mesma configuração, novo lote), em vez de "rode de novo mais tarde"?
- Favoritos é a única lista de comparação; um lote grande deveria abrir já filtrado (`?lote=`) e ordenado por Ret/T, em vez de cair na lista geral?

## Perguntas para Alan

1. **Lote pausado** — Com um lote pausado, o Otimizar hoje começaria outro e o pausado sumiria da tela até o novo terminar.
   - **A — Bloquear até decidir (Recommended):** Otimizar mostra "Retome ou encerre o lote 7f3c2a91 antes de começar outro".
   - **B — Novo encerra o pausado:** o Confirmar avisa que o pausado vira "Não rodou" e mantém os favoritos dele.
   - **C — Vários lotes juntos:** cada lote pausado fica listado com o seu painel e o seu Retomar.

## Disposition (resumo)

| Finding | Gravidade | Classe | Quem corrige | Disposition |
|---|---|---|---|---|
| Controles do #1122 vivos em ação/ETF (estrelas, Telegram, Revalidar) | P1 | produto (escopo/estado) | autor (rework único) | corrigir |
| Otimização 15m/1h/4h sem "Fora por cobertura" + conselho errado | P1 | produto (estado faltante) | autor (rework único) | corrigir |
| Foco no Pausar; nome acessível das células; foco invisível no Classe | P2 | mecânico (a11y) | autor no rework, ou Apply | n/a |
| Painel na coluna estreita da Otimização; densidade de Favoritos | P2 | juízo | autor | n/a |
| Lote pausado + novo lote | P2 | juízo | Alan (pergunta) | n/a |
| Token `--fav-up`, texto sob demanda da cripto, amostra, plural, quebra chip·moeda, live region, "Nada será executado", incumbentes | P3 | apply | Apply / fora de escopo | aceito-P3-Apply |

**Verdict A: BLOCKED** (0 P0, 2 P1, 6 P2, 8 P3). Os dois P1 são pequenos e cabem no rework único do teto com-tela.
