# Assessment A — card 1119 · change card-1119-backtest-acoes-etfs

> Avaliador A isolado (produto / UX / acessibilidade / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem resultados do Assessment B. Sem spawn de filho. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML/CSS/JS do protótipo, OpenSpec, `backend/`, `frontend/src/` ou `DESIGN.md`. Única escrita: este arquivo.

`proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5, effort high)` — captura `.cursor/tmp/claude-evidence/assessment-a-1119-a1.capture.json` (attempt `3034036f-5b8c-47f3-8d25-d52e1aa96db8`, band `juizo`, role `assessment-a`, capture_sha256 `9adab5af54e47cedc9f6e70333d08de5a251df879da4153b317e0f4aee871d98`).

## Metadata

- card: 1119 — Rodar backtests de ações e ETFs com execução e stops realistas
- change: `card-1119-backtest-acoes-etfs`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1119-backtest-acoes-etfs`
- branch / q_git: `card-1119-backtest-acoes-etfs` @ `5fe666fe` (pacote untracked)
- tuple: `bound_card=1119` · Status esperado = Design (MUST NOT arrastar)
- data (UTC): 2026-10-23
- cliente: Claude Code (adapter cooperativo, não oficial; sem modo Auto), superfície claude-desktop
- Issue: REST `gh api repos/oalansilva/crypto/issues/1119 --jq .body`. Fronteira = body grelhado (Problema / História / Entra / Não entra + 5 decisões de Alan de 23/10/2026). Sem reentrevista.
- `design.md` sha256 `9413cd2d5568e002bf5420d52c67690cfeb0caca207424e05f5295029de03ab3` (== prompt)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Setup Impeccable: `context.mjs --target …/index.html` carregou PRODUCT.md + DESIGN.md; modo **critique**, superfície Operate (refinamento clone+delta). `DESIGN.md` é a autoridade visual e não foi tocado.
- Tooling: Playwright Python 1.62 + Chromium headless shell 1243, `pt-BR`, tema escuro, 1440×900, 390×844 e 768×1024 (extra), **na URL pública** `https://dev.criptofarol.com.br/prototypes/card-1119-backtest-acoes-etfs/`. Screenshots de trabalho em `/tmp/1119-A-shots/` (não versionados). Sem servidor local. Contraste por cor computada (sem axe-core).

## Digest (disco == servido)

| Arquivo | sha256 disco | HTTP | servido |
|---|---|---|---|
| `index.html` (também `…/card-1119-backtest-acoes-etfs/`) | `8c0f34c2b622aaa82e332c2d83c86e55d2f99f31c7328275fbe1845ef54138b3` | 200 | IDENTICAL |
| `etf-short.html` | `22053a5933ae226c29e17c276b8b25e97cccb22e235e9b0925d639ad7a8c8468` | 200 | IDENTICAL |
| `cripto.html` | `7df8f5a93d69809106c37c9bed980e7b5d091e4873d636e55736002de12519b6` | 200 | IDENTICAL |
| `configure.html` | `ac864821b28fa42467ab34a2db533e434d12ffbb082d8c3e1290f2107dcbd7ba` | 200 | IDENTICAL |
| `live.css` | `7fb6d878705b10256f16443101d7502ca2e7193ced5be9950946020e7e058944` | 200 | IDENTICAL |
| `delta.css` | `17b77fc15ed27bdece1009b375f70e300d6564f3f62309da81857c2804ae8989` | 200 | IDENTICAL |
| `delta.js` | `8f6220155b2d9626bf4d5208b1a8383b8c80488a1c4f8f37c4aa15eb4418b493` | 200 | IDENTICAL |

Disco == servido == prompt == `design.md` §Prototype Validation. Extra: `live.css` == `https://dev.criptofarol.com.br/assets/index-N9hYlmCr.css` (bundle vivo de DEV) byte a byte. Zero erro de console e zero `pageerror` nas 12 cargas (4 páginas × 3 larguras).

## Tokens parseáveis (rubrica D4)

`design.md` L1–L3, linhas próprias:

```
UI impact: affected
live_route: /combo/results
surface: existing
```

Presentes e bem formados. Regiões clonadas declaradas no §Context; `index.html` canônico de `/combo/results`; extras `etf-short.html`, `cripto.html` (mesma rota, outro estado) e `configure.html` (`/combo/configure`), nunca canônicos. Nenhuma página é painel ANTES/DEPOIS nem grelha de N estados; Demonstração no fim, no fluxo, sem `position:fixed`. **ok.**

## Cobertura do body (Entra / Não entra)

| Item do Entra | OpenSpec | Protótipo |
|---|---|---|
| Ação e ETF no backtest individual; cripto continua; resultado mostra ativo, classe, sessão, ajuste, moeda, janela coberta, versão da amostra | `equity-backtest` (aceite, identidade), `crypto-only-mvp` | chip "Ação"/"ETF"/"Cripto"; bloco "Dados e execução" com os 8 fatos; cripto.html com favorito vivo |
| 15m/1h/4h/1d só no pregão, sem atravessar fechamento, sem preencher mercado fechado | `market-history`, decisão 5 | dica no Combo; SPY "1h montado do 5m · 09:30, 10:30 … 15:30–16:00"; Calendário "Noite, fim de semana e feriado não viram candle nem lacuna"; 4h e 15m só no texto (ok) |
| Intrabar quando cobre; diária com trecho quando falta; nunca em silêncio | `backtest-precision-disclosure` | faixa de precisão nos 4 estados (faltou com trecho, falha ao ler, desligado, intrabar) + "15m não cobre a janela" na cripto |
| Gap no stop em todas as classes, com custo/slippage; sem gap nada muda; cripto pode piorar | `stop-gap-execution` | NVDA long (stop 181.74, abriu 172.10), SPY short (672.04 → 676.10), BTC long; "Stop com gap" na tabela e no cartão; contagem de gaps nas convenções; frase de cripto "calculados antes desta regra podem ter número melhor" |
| Fração permitida, com aviso e #1124 | `equity-backtest` req. fração | "Posição com fração … não confirma que a sua conta na Binance compra fração" (NVDA, SPY); ausente na cripto (correto) |
| Custos, anualização, calendário e direção por classe; short não implica venda descoberta | `equity-backtest` req. custos; decisões 9–10, 14 | "Custos … assumida", "Anualização … 252 pregões" / "365 dias × 6"; "Short simulado"; chip "Short / venda" |
| Favoritar ação/ETF recusado com motivo visível; cripto como hoje | `favorites` | botão `aria-disabled`, motivo ao lado, `role=status` ao ativar, nenhum `role=dialog`; cripto.html com botão vivo amarelo |
| Demonstrar gap long/short, split, horário de verão, sessão fechada, falta de intradiário, regressão cripto antes/depois | decisão 17, tarefas 2.4/8.2 | gap long/short, falta de intradiário e regressão cripto na tela; split e horário de verão só em teste/handoff (aceitável: é evidência, não tela) |

Não entra — nada vazou: sem ordem/stop real, sem benchmark, sem otimização em lote com ação, sem favorito/refresh/alerta de ação (recusado), Otimização/Descoberta/lote recusam, sem exportação nova (o botão "Exportar para Excel" é o vivo, inalterado). Ponto de atenção de fronteira: a seleção mista no Combo troca o porquê da recusa (ver P2 juízo abaixo).

## Fidelidade (clone da página viva)

- `live.css` é o bundle vivo inteiro (`index-N9hYlmCr.css`), conferido por sha256 contra o servido em DEV.
- `ComboResultsPage.tsx` vivo: "Voltar" + "Salvar nos Favoritos" (classe, `data-testid`, `min-h-11`, anel `#3b82f6`) idênticos; seção `aria-label="Análise da estratégia"`, chips, `dl` de métricas, Regras da estratégia, Detalhes técnicos e aviso educacional na ordem viva. O delta entra só nos blocos `DELTA`.
- `StrategyTradesTable.tsx` vivo: preço com "USDT" fixo e valores/PnL com "USD" fixo; o delta troca só o sufixo do preço pela moeda da classe e acrescenta "Stop com gap" na coluna Sinal e no cartão.
- `ComboConfigurePage.tsx` vivo: caixa Market Data (`glass … text-zinc-600`), `classNote`, "Otimizando…" e opções de timeframe preservados; o delta troca conteúdo, desabilita 1m/5m e acrescenta dicas.
- Observação de incumbente (não é delta): o `index.css` vivo tem `* { margin: 0; padding: 0 }` fora de `@layer`, que vence os utilitários do Tailwind v4 (`p-5`, `space-y-6`, `px-2.5` computam 0). Por isso o resumo, os chips e as seções vivas aparecem sem respiro e coladas, enquanto o bloco "Dados e execução" (CSS próprio) tem padding. O clone está **fiel**; o contraste visual entre delta "arrumado" e vivo "colado" é do produto, não do protótipo.
- Hook do Impeccable sinalizou `font-size` 10/11 px em `cripto.html` L20/L25: são o AppNav vivo (COPIED). Falso positivo para este card.

**Fidelidade ok.**

## Acessibilidade (medida)

- Contraste (cor computada sobre fundo efetivo, 1440 e 390): proveniência e textos do bloco `#b7bdc6`/`#181a20` 9,2:1; rótulos `dt` `#929aa5` 6,12:1; valores 14,69:1; título âmbar da faixa 10,42:1; motivo do favorito 10,24:1; botão recusado 6,94:1; "Stop com gap" 9,48:1; nota do gap 8,37:1; chip de classe 10,73:1; dicas do Combo 5,56:1. **Exceção:** caixa Market Data do Combo com o texto novo "Binance Ações · pregão regular de Nova York · ajustado por split" em `oklch(0.442 0.017 285.8)` sobre `#1e2329` = **2,16:1** (estilo herdado; ver P2).
- Alvos: "Salvar nos Favoritos" recusado 44 px de altura nas 3 larguras.
- Teclado: Tab chega a "Salvar nos Favoritos" em 13 paradas (1440) e 4 (390), depois de "Voltar"; `:focus-visible` com contorno 2 px `#3b82f6`. Enter anuncia em `role=status` "Não salvo. Ações e ETFs ainda não podem ser favoritados: …"; Space idem; nenhum `role=dialog` abre. O bloco de dados não tem paradas de foco (só leitura).
- Leitor de tela (árvore de acessibilidade): `region "Dados e execução"` → `heading level 2` → parágrafo de proveniência → `note` da precisão com `<time>` → `term/definition` dos 8 fatos → `heading level 3` "Convenções desta execução" → `list`. Botão recusado com `aria-describedby` no motivo. Combo: aviso de 5m em `role=status`, falha de coleta em `role=alert`.
- Sem rolagem horizontal do documento em nenhuma página nem largura (a tabela de operações rola dentro do `overflow-x-auto` vivo).

## Responsividade

- Fatos em 4 colunas a 1440, 2 a 768 (até 1100) e 1 a 390, como o contrato diz; convenções em 2 colunas e 1 abaixo de 760.
- 390 px: favorito recusado empilha o motivo sob o botão, à esquerda; cartão de trade mostra "Stop com gap · stop 181.74, abriu 172.10".
- Densidade a 390: o bloco "Dados e execução" mede **1.460 px** (NVDA e SPY; 1.144 na cripto) e empurra o gráfico para y≈2.085 e a lista de operações para y≈2.790, contra 976/1.654 a 1440. Ver P2 juízo.

## Heurísticas Nielsen (0–4) — só neste snapshot

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 3 | precisão efetiva sempre visível; a coleta sob demanda (até ~10 s + 30 s de espera) some dentro do "Otimizando…" |
| 2 | Match between system and real world | 3 | "Precisão diária" num 4h; datas da lista sem hora num 1h de pregão |
| 3 | User control and freedom | 3 | recusas não destroem a seleção ("a seleção foi mantida") |
| 4 | Consistency and standards | 3 | 181.74 × 181,74 (P3 aceito); cripto com preço USDT e PnL USD |
| 5 | Error prevention | 3 | 1m/5m desabilitados; o caminho até o aviso de 5m não está desenhado |
| 6 | Recognition rather than recall | 3 | gap explicado na própria linha do trade e nas convenções |
| 7 | Flexibility and efficiency | 3 | bloco fixo, sem atalho para o gráfico/lista no móvel |
| 8 | Aesthetic and minimalist design | 2 | 8 fatos + 6–7 convenções antes do gráfico; 1,7 tela no móvel |
| 9 | Recognize, diagnose, recover | 3 | alerta de coleta diz motivo e "tente de novo"; falta o estado de cobertura parcial |
| 10 | Help and documentation | 3 | convenções escritas em linguagem de operador |
| **Total** | | **29/40** | Good |

## Design specificity

Autoral para o produto: o delta fala a língua do Cripto Farol ("pregão regular de Nova York", "assumida", "não confirma que a sua conta …"), põe tom âmbar só quando a precisão caiu e coloca a marca do gap exatamente onde o olho já está (linha do trade). Nada de mundo visual novo; tokens do `DESIGN.md` e cores do incumbente. Não é intercambiável.

## Cognitive load

Single focus ok na faixa de precisão (o que mais importa vem primeiro e com tom). Falhas: (1) o bloco reúne 8 fatos + até 7 convenções num único grupo de leitura, acima de 4 por grupo; (2) no móvel não há divulgação progressiva, então a decisão "confio neste número?" exige rolar 1,7 tela antes de ver gráfico e operações. Carga média.

## What's working

- Faixa de precisão: a frase "Você pediu precisão intrabar; como ele não cobre a janela, o stop foi simulado no candle diário em toda a janela" resolve o "nunca em silêncio" do card sem jargão, com o trecho em `<time>`.
- Gap legível onde importa: "Stop com gap / stop 181.74 · abriu 172.10" na própria saída, mais a contagem nas convenções.
- Recusa de favoritar exemplar: visível antes de clicar, focável, anunciada, sem modal, e a cripto intocada.

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2 · mecânico] `etf-short.html`, "Convenções desta execução": falta "Preços ajustados".** O spec `backtest-precision-disclosure` pede a nota de preço ajustado para ação **e ETF**; só o NVDA a tem (0 ocorrências em `etf-short.html`). Corrigir: incluir o item no SPY (ETF também tem split; e "ajustado por split" já aparece na proveniência).
- **[P2 · mecânico] Faixa e fato de precisão: "Precisão diária" num backtest de 4h/1h.** No `cripto.html` (estado "15m não cobre a janela") o título diz "Precisão diária" e o texto diz "simulado no candle de 4h"; o fato diz "Diária". O mesmo valeria para o SPY 1h. Corrigir: título/fato pelo tempo gráfico ("Precisão do candle de 4h"; "diária" só no 1d), mantendo o trecho e o tom âmbar.
- **[P2 · mecânico] Combo, caixa Market Data: o texto novo do contrato fica a 2,16:1.** "Binance Ações · pregão regular de Nova York · ajustado por split" herda `text-zinc-600` do incumbente sobre fundo escuro (12 px). É texto exigido pelo spec `equity-backtest` e fica quase ilegível. Corrigir no delta com a cor secundária do produto (`#b7bdc6`, 9,2:1); uma classe.
- **[P2 · mecânico] Combo, 5m com ação: o caminho até o aviso não existe na tela desenhada.** Com NVDA selecionado, 1m/5m ficam `disabled`; o estado "NVDA em 5m" só aparece porque a Demonstração reabilita as opções. Definir o caminho real (5m já escolhido com cripto e depois NVDA adicionado) e o que acontece: o valor cai para 15m/1h com aviso, ou fica 5m e o aviso aparece **antes** de "Otimizar" (hoje só depois do clique). Dizer também se 1m/5m voltam a ficar disponíveis na seleção mista, já que ali a ação fica fora e quem roda é a cripto.
- **[P2 · mecânico] Resultado: estado "coleta falhou com parte gravada" sem desenho.** O spec `equity-backtest` diz que a execução roda no trecho coberto "and say so"; o protótipo só mostra janela coberta menor por calendário (SPY "1 ago. é sábado"). Falta o texto e o lugar (provavelmente a faixa âmbar ou a linha "Janela coberta": "A coleta de NVDA parou em DD mmm.; o backtest rodou de A a B"). Um estado a mais na Demonstração do `index.html` basta.
- **[P2 · juízo] Lista de operações sem hora em 1h/15m/4h de ação/ETF.** A coluna "Data e hora" vive só com a data (formatador UTC do incumbente); no SPY 1h a entrada e a saída de 23 set. aparecem iguais e o gap "na abertura do pregão" de 27 ago. não tem hora. Para quem quer conferir "sem candle que atravesse o fechamento" e o horário de verão, a hora (no fuso de Nova York, rotulado) é o que prova. Alan decide se entra neste card (é só formatação na lista) ou vai para depois.
- **[P2 · juízo] Densidade do bloco "Dados e execução" no móvel (1.460 px antes do gráfico).** Opções: (a) manter como está (o spec pede convenções "visíveis como texto a 390 px"); (b) manter proveniência + faixa de precisão + Janela coberta sempre visíveis e pôr os demais fatos e as convenções num `<details>` "Dados e convenções desta execução" (sem hover, legível a 390); (c) mover o bloco para depois da lista de operações, deixando só a faixa de precisão no topo. Recomendação: (b) só no móvel, se Alan aceitar que "visível" inclui um toque.
- **[P2 · juízo] Motivo de recusa "de hoje" fica falso depois deste card.** Lote, Otimização e Descoberta continuam com `EQUITY_UNSUPPORTED_MESSAGE` = "Análise ainda não disponível para ações e ETFs.", mas agora a análise de 1 ativo existe no Combo. O body diz "continuam recusados com o motivo de hoje", e o design segue a letra (decisão 3), trocando o porquê só na seleção mista do Combo. Alan confirma se "motivo de hoje" é o texto literal ou o motivo (classe ainda não suportada naquele fluxo), caso em que a frase ganharia "… nesta tela; rode 1 ação sozinha no Combo".

### P3 — detalhe de Apply (não reabrir como P0/P1)

- **[P3 · mecânico] Cripto: preço em USDT e valor/PnL/MFE/MAE/acumulado em "USD"** (incumbente do `StrategyTradesTable`). O design passa `currency` só para o preço; o Apply decide se a moeda vale para todas as colunas de dinheiro (na ação já fica tudo USD). **aceito-P3-Apply**
- **[P3 · juízo] "Otimizando…" não diz que está coletando histórico** no primeiro backtest de uma ação (1 ano de 5m ≈ 10 s, mais até 30 s de espera do lock). Uma linha "Coletando histórico de AAPL…" no mesmo botão/estado resolveria. **aceito-P3-Apply**
- **[P3] Formato de número misto** (181.74 na lista × 181,74 nas convenções; 94.829,00 × 93,610.00 na cripto) — já aceito no `design.md`. **aceito-P3-Apply**
- **[P3] Rótulos vivos em inglês no Combo** ("1 minute (só cripto)", "Simulates execution using 15-minute candles…") convivem com o delta em português; incumbente. **aceito-P3-Apply**
- **[P3] Amostra do protótipo:** "Todo o histórico" desde 2014 com 6 trades só em 2025–2026 e gráfico a partir de set. 2025; números, datas e versões são amostra (aceito no `design.md`). **aceito-P3-Apply**
- **[P3] Incumbente fora do card:** reset `* { margin:0; padding:0 }` sem `@layer` anula os utilitários de espaçamento do Tailwind no app inteiro. Não é deste card; vale um card próprio. **aceito-P3 (fora de escopo)**

## Persona red flags

- **Alan (pesquisador, decide se confia no número):** lê a faixa âmbar e entende a queda de precisão; no SPY 1h, não consegue ver em que hora o gap aconteceu nem conferir que nenhum trade cruzou o fechamento (P2 juízo de hora). No 4h cripto, "Precisão diária" o faz pensar que o stop foi simulado no diário (P2 mecânico).
- **Beta tester no celular:** abre um resultado e passa 1,7 tela de fatos antes do gráfico; o que ele procura (o gráfico e os trades) fica longe (P2 juízo densidade).
- **Usuário de leitor de tela:** fluxo de recusa bem resolvido; a caixa Market Data a 2,16:1 é problema para baixa visão, não para leitor de tela.

## Questions to consider

- Se a precisão caiu, o número merece um selo também no resumo de métricas (perto de "Retorno total"), e não só no bloco abaixo?
- O "backtest individual" otimiza parâmetros na mesma janela que mostra; a tela deveria dizer "parâmetros otimizados nesta janela" para não vender um resultado in-sample como confiável?

## Open Questions do autor

1. **O que conta como "backtest individual" na tela.**
   - (a) Recomendação do autor: Combo com 1 ativo (otimiza e abre o resultado) + `POST /api/combos/backtest` com parâmetros fixos; Otimização segue recusando até o #1120.
   - (b) Aceitar 1 ativo também na tela Otimização: invade o #1120 e a tela tem datas fixas de jan. 2024, sem período. Não recomendo.
   - (c) Só parâmetros fixos: é a leitura mais pura de "backtest individual", mas pede botão/fluxo novo no Combo, outro clone e outra rodada de Design (estoura o teto).
   - Leitura: **(a)**. É o único caminho de tela que já existe e cobre a história. Ressalva para Alan: em (a) o número exibido é o melhor da otimização na própria janela (in-sample), então "confiar no resultado" depende de walk-forward, que o Combo já oferece. Não muda o protótipo; no máximo uma linha de texto no resultado.
2. **Avisar em `/favorites` que os números de cripto mudaram com o gap.**
   - (a) Recomendação do autor: nenhum aviso novo; a explicação fica no resultado (cripto.html já diz "calculados antes desta regra podem ter número melhor onde houve gap") e o número anterior fica no histórico de runs.
   - (b) Nota única em `/favorites` no primeiro refresh depois da mudança.
   - Leitura: **(a) neste card**, mais aviso operacional no grupo do beta (Telegram) no dia do deploy. Motivo: (b) põe uma superfície nova (`/favorites`) que não está clonada nem no gate, e pede mais uma rodada de Design. O risco real é um beta tester ver o favorito piorar de um dia para o outro sem saber por quê, o que vai contra o espírito do card ("nunca em silêncio"). Se Alan quiser isso no produto, eu abriria como card próprio pequeno (selo "recalculado com a regra de gap" no favorito cujo número mudou), não dentro do #1119.

## Disposition (resumo)

| Finding | Gravidade | Classe | Quem corrige | Disposition |
|---|---|---|---|---|
| (nenhum P0/P1) | — | — | — | n/a |
| "Preços ajustados" no ETF; "Precisão diária" em 4h/1h; contraste da caixa Market Data; caminho do aviso de 5m; estado de coleta parcial | P2 | mecânico | autor (rework único, se o pai abrir) | n/a |
| Hora na lista de intradiário; densidade no móvel; texto "motivo de hoje" | P2 | juízo | Alan decide | n/a |
| Moeda das colunas da cripto; aviso de coleta no "Otimizando…"; formato de número; inglês vivo; amostra; reset CSS do incumbente | P3 | — | Apply / fora de escopo | aceito-P3-Apply |

**Verdict A: PASS** (0 P0, 0 P1; 8 P2; 6 P3).
