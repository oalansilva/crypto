# Assessment A — card 1070 · change card-1070-scalp-jev-lucro-liquido

> Avaliador A isolado (produto / UX / heurísticas / contrato visível). Onda dupla com-tela, **passagem depois da invalidação I4**. Sem transcript do pai. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem `move_agent_to_root`. Única escrita: este arquivo.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 1070 — Scalp Jev: lucro líquido (backtest, geometria, taxa, P&L por trade)
- change: `card-1070-scalp-jev-lucro-liquido`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1070-scalp-jev-lucro-liquido`
- branch / q_git: `card-1070-scalp-jev-lucro-liquido` @ `3acd32c5`
- tuple: `bound_card=1070` · Status=Design (pós-I4; MUST NOT arrastar)
- data (UTC): 2026-09-29T12:37Z
- modelo desta sessão: **Grok 4.6**, slug **`cursor-grok-4.6-high`**
- UI impact (rubrica D4): **affected** · `live_route: /monitor` · `surface: existing` — linhas próprias parseáveis de `design.md`
- Issue: REST `gh api repos/oalansilva/crypto/issues/1070` não reentrevistado. Fronteira = proposal/body grelhado (Problema / História / Entra / Não entra). Decisões de 29/09 fechadas.
- Digest proto (prompt + disco + HTTPS, verificado nesta sessão):
  - canónico `index.html` sha256 `c2d0fee40fa6bd2c8b3c4028addf6033307c67d4c80fcf678f41436bc1ca2b9f` · 58181 B
  - HTTPS `https://dev.criptofarol.com.br/prototypes/card-1070-scalp-jev-lucro-liquido/` IDENTICAL (HTTP 200, mesmo sha256, mesmos bytes)
- Irmãos HTML: nenhum (`index.html` só). T5 mede só este index.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Tooling: Playwright Python + Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`, headless) contra HTTPS real. Viewports 1280×800 e 390×844. Sem despejo de HTML. Evidência = árvore visível, `innerText` de landmarks, bounding boxes, screenshots em `/tmp/1070-A` (não persistidos: este filho só escreve o snapshot).
- Mode: Impeccable **Operate**. `DESIGN.md` autoridade visual, não sobrescrito. Sem redesign da board.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | Landmarks `/monitor` |
|---|---|---|
| `https://dev.criptofarol.com.br/monitor` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | 0 (`table.signals` = 0) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) digest local == HTTPS, (3) catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. O 200 do proto coincide com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias:

```
UI impact: affected
live_route: /monitor
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/monitor`; módulo Scalp BTCUSDT já existente; **não** superfície nova; **não** dentro do Operar. Regiões clonadas marcadas (`COPIED:start`/`COPIED:end` 10/10): shell autenticado + workbench `table.signals` + Status / Preço / Distância / 7d (`data-landmark`) / Risco até stop / Tags / Operar / Par / Estratégia. Delta fora desses blocos (estado, taxa, P&L líquido, diagnóstico do conjunto). URL canónica **não** é painel ANTES/DEPOIS nem grelha de N estados. **PASS** deste item da rubrica.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-1070-scalp-jev-lucro-liquido/index.html` | `c2d0fee40fa6bd2c8b3c4028addf6033307c67d4c80fcf678f41436bc1ca2b9f` | 58181 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-1070-scalp-jev-lucro-liquido/` | idêntico | 58181 | 200 |
| prompt desta sessão | idêntico | — | — |

Disco == HTTPS == prompt: IDENTICAL. Pós-I4: o digest canónico bate; a crítica avalia **esta** superfície, não a rota de login.

## Fidelidade (clone da página viva)

Catálogo `/monitor` (`route-landmarks.yaml`): selector `table.signals` · texts `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`, `Operar`, `Par / Estratégia`.

Gate deste filho (prompt): falta de `table.signals` ou dos cabeçalhos **Status / Preço / Risco até stop / Operar** é **P0**. Grelha de N estados como URL canónica é **P0**.

| Landmark | Catálogo / vivo | Proto HTTPS + Playwright (1280) |
|---|---|---|
| `table.signals` | tabela da board | count=2, visíveis desktop (Em posição + Saída) |
| Status / Preço / Distância / Risco até stop / Tags / Operar / Par / Estratégia | thead | exact visíveis (CSS uppercase no desktop: STATUS, PREÇO, RISCO ATÉ STOP, OPERAR) |
| 7d | `data-landmark="7d"` + texto incumbente Gráfico | `data-landmark="7d"` count=1, texto visível `GRÁFICO` |
| Operar | botão de linha | visível e **não** disabled com scalp Ligado (desktop); nas cards mobile também |

Anti-padrões P0:

- URL canónica `…/prototypes/card-1070-scalp-jev-lucro-liquido/` → `index.html` é o Monitor autenticado (shell + topbar + `page-sub` + **módulo scalp** + diagnóstico + KPIs + `table.signals`). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES/DEPOIS` = 0 (único hit está em comentário de fonte; após strip de comentários = 0).
- **Não** é grelha de N estados no lugar da listagem. Zero `.state-grid` / galeria / `off.html` / `kill.html`. Um único HTML. Default canónico = Operate, interruptor **Ligado** (`aria-checked=true`), como a vista promovida do Prototype.
- Fixtures «Simular *» / «Ver taxa BNB» / «Ver sem chave Spot» são controlos proto-only **na mesma URL**, não páginas-estado. Não reclassificam a URL canónica como grelha.
- Pares `COPIED:start`/`COPIED:end` = 10/10.
- Chrome (sidebar, amarelo `#fcd535`, nav Monitor `aria-current=page`) = **folha**, não prova. Prova = landmarks do catálogo no proto canónico + delta só no módulo scalp / diagnóstico.

## Produto (escopo — não reabrir grelha)

Delta pedido (#1070): no `/monitor`, só mudam textos de estado, taxa («desconto aplicado») e P&L líquido por trade; o diagnóstico fala de alvo, stop, prazo e recorte juntos com a confiança. Board e Operar ficam. Sem rota nova, landing ou Ajuda.

Vista canónica observada (`data-state` on / load fresco):

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Clone `/monitor` + `table.signals` + Status / Preço / Risco até stop / Operar | 2 tabelas visíveis a 1280; theads com os quatro cabeçalhos (e Distância / Tags / Par) | OK |
| URL canónica ≠ grelha de N estados | 1 HTML; 0 galeria; 0 ANTES/DEPOIS visível | OK |
| Interruptor Ligado na vista promovida | `role=switch` `aria-checked=true` rótulo **Ligado**; teclado Space liga/desliga | OK |
| Lookback últimos 60 min | `#scalp-horizon` e copy do status | OK |
| Taxa «desconto aplicado» quando o BNB cobre | `7,5 bp · desconto aplicado`; hurdle `15,1 bp` | OK |
| Sem BNB a cobrir: **não** diz desconto aplicado | fixture `Ver taxa BNB` → taxa `10 bp`, hurdle `20,1 bp`, status sem a frase | OK |
| Alvo / stop da versão aplicada | `+20 bp` / `−14 bp` (não escolhidos no chat) | OK |
| P&L líquido por trade, perda visível | `−12,4 bp` e `−US$ 0,18` em vermelho + glifo `−` | OK |
| Primeira volta DEV US$ 10 fechada | status: «A primeira volta de US$ 10 fechou» | OK |
| Diagnóstico: alvo, stop, prazo, recorte + confiança | «apliquei alvo, stop, prazo e recorte juntos com a confiança»; amostra >200 no backtest; lucro exigido = backtest | OK |
| Ajuste automático distinto do scalp | segundo switch **Ligada** `aria-label="Ajuste automático"`; copy «Ligar o ajuste automático não liga o scalp» | OK |
| Kill | banner «Parado por kill (−2% de T). Não religa sozinho.»; status aponta o mesmo interruptor | OK |
| Posição presa | banner + status: limitadora do fim do prazo; mercado só com teto; Operar continua | OK |
| Sem chave Spot | switch `disabled` + «Configure a chave Spot (a mesma do Operar)» | OK |
| Operar intacto; sem mutex | botões Operar `disabled=false` com scalp on, kill, stuck e nokey | OK |
| Sem «BNB habilitado; desconto não aplicado» na vista que aplica desconto | 0 ocorrências dessa string | OK |
| Clip ≤ US$ 10; T = US$ 100 | células CLIP / TETO T visíveis; T/clip não sobem | OK |

Não-goals respeitados: board não redesenhada; Operar não redesenhado; sem landing/Ajuda/rota nova; sem saque; sem PROD.

## UX

Hierarquia desktop: shell autenticado → chrome Monitor → **módulo Scalp BTCUSDT** (h2 + switch + 12 células + status + nota) → **diagnóstico do dia** (aviso aberto + histórico) → KPIs da board (`y≈1709`) → filtros → `table.signals` (`y≈1960`). Uma decisão de envio (ligar/desligar o scalp). Operar continua na coluna de sempre.

Carga cognitiva: **média–alta (Operate)**. O aceite exige estado + taxa + P&L + diagnóstico do conjunto visíveis; isso empurra a board para baixo do fold. 12 células no módulo (T / clip / lookback / inventário / calibração / P&L do dia / hurdle / taxa / alvo / stop / P&L líquido bp / P&L líquido US$) passam o tecto de 4 por grupo. Fixtures proto-only somam uma fila extra de escolhas que **não** vão ao produto.

Prevenção: sem Spot o switch não liga; kill não religa sozinho; BNB sem saldo não mente «desconto aplicado». Recuperação: o mesmo interruptor desliga e religa após kill; posição presa deixa Operar vivo; «Voltei atrás» no histórico mostra reversão do conjunto.

Pico emocional: a perda da primeira volta (`−US$ 0,18` / `−12,4 bp`) está tão visível quanto um ganho — alinha com o critério observável.

## Acessibilidade

- `lang` / h1 `sr-only` «Monitor de sinais»; `:focus-visible` 2px `#3b82f6` no switch (medido); teclado Space no foco altera `aria-checked` true→false→true.
- Interruptor do scalp **nomeado**: `role="switch"` + `aria-labelledby="scalp-title"` («Scalp BTCUSDT») + texto visível Ligado/Desligado.
- Ajuste automático: `aria-label="Ajuste automático"` + texto Ligada.
- Kill / posição presa **sem** `aria-live` / `role="status"|"alert"` — P2 (o controlo principal continua anunciável; o banner automático não empurra mensagem).
- Contraste (WCAG, medido contra `#1e2329`): P&L líquido `#f6465d` **4.48:1** (incumbente `trading-down`, à rasca de 4.5); taxa branca 15.82:1; status 14.69:1; switch on (`#181a20` em `#fcd535`) 12.18:1. Cor do P&L negativo não é a única via: glifo `−` + `US$` / `bp` no texto.
- Disabled (nokey) = switch não clicável; a frase de Meu Perfil está visível.

## Responsividade

Desktop 1280: módulo + diagnóstico + KPIs + tabela com landmarks; Operar da linha visível (clip incumbente possível, P3).

Mobile 390 (load fresco, **Ligado**): módulo e P&L líquido `−12,4 bp` visíveis; diagnóstico continua aberto e comprido; `table.signals` sai do fluxo visual (cards `monitor-card-*`); cards BTC/USDT e ETH/USDT trazem **Operar** não-disabled. Não é P0: é o clone incumbente (tabela→cards), não a ausência do contrato Status/Preço/Risco/Operar no canónico desktop.

## Estados

Mock cobre, cada um em load fresco desta sessão:

| Estado | Switch | Contrato visível |
|---|---|---|
| **on** (canónico) | Ligado | taxa com desconto; P&L líquido negativo; diagnóstico Apliquei |
| **off** (Space / haskey) | Desligado | «não envia ordem deste scalp»; P&L líquido pode ir a `—` |
| **kill** | age como off | banner kill; religar = o mesmo switch |
| **posição** | Ligado | hold 60 min; alvo/stop; sem entrada nova |
| **último resultado** | Ligado | copy de perda visível / primeira volta conta |
| **presa** | Ligado | limitadora falhou; teto; Operar disponível |
| **BNB sem desconto** | Ligado | `10 bp` **sem** «desconto aplicado»; hurdle 20,1 bp |
| **nokey** | Desligado disabled | aponta Meu Perfil |

Não mocka: P&L positivo (regra visível já demonstrada no negativo); persistência pós-reload (P3 Apply); Jev em tempo real (proto estático).

## Design specificity

A composição é o Monitor autenticado do Farol + módulo Scalp BTCUSDT + diagnóstico do conjunto. Não iria a um SaaS genérico inalterado: AppNav Cripto Farol, `table.signals`, Em posição / Saída, Operar, tokens Binance, vocabulário bp/hurdle/post-only/kill. Modo Impeccable: **Operate**. Delta = copy de estado/taxa/P&L + diagnóstico (alvo, stop, prazo, recorte, confiança).

## Heurísticas Nielsen (0–4, Operate)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 3 | Switch + status + diagnóstico; falta live region no kill/presa |
| 2 | Match between system and real world | 3 | Vocabulário do issue (bp, hurdle, post-only, backtest); Ligado vs Ligada |
| 3 | User control and freedom | 4 | O mesmo interruptor liga, desliga e religa após kill; sem mutex com Operar |
| 4 | Consistency and standards | 3 | Clone do shell/board; dois switches amarelos para objectos distintos |
| 5 | Error prevention | 4 | Nokey não liga; BNB sem saldo não mente desconto; kill não auto-religa |
| 6 | Recognition rather than recall | 3 | Taxa, P&L e geometria no sítio; diagnóstico longo pede leitura |
| 7 | Flexibility and efficiency | 3 | Teclado nativo no switch; um caminho Operate |
| 8 | Aesthetic and minimalist design | 2 | 12 células + aviso do dia aberto + fila de fixtures proto-only |
| 9 | Help users recognize, diagnose, recover | 3 | Kill / presa / nokey explicam o próximo passo |
| 10 | Help and documentation | 3 | Nota da chave + diagnóstico do dia; Ajuda fora de escopo |
| **Total** | | **31/40** | Good |

## Cognitive load

Checklist: falham single focus (diagnóstico vs board), chunking (12 células), one-thing-at-a-time (aviso do dia), progressive disclosure (diagnóstico aberto). 4 falhas = carga alta. **Não é P0**: a tarefa (ler estado, taxa, P&L líquido, Operar ao lado) completa-se; o ruído tem workaround (scroll). P2.

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.
  - `table.signals` presente (2 visíveis a 1280) com Status / Preço / Risco até stop / Operar.
  - URL canónica = clone Operate `/monitor`, não grelha de N estados.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2] Módulo com 12 células + diagnóstico do dia aberto empurra a board para baixo do fold** (KPIs `y≈1709`, tabela `y≈1960` a 1280; no 390 o Operar das cards só depois de um scroll longo). O aceite pede esses textos; a forma (tudo expandido, sem disclosure) compete com a listagem. **Visível:** bloco «Como está o scalp» + histórico. Disposition: **n/a** (não bloqueia; Apply pode colapsar o aviso sem cortar o contrato).
- **[P2] KPI «P&L» do dia mostra o mesmo `−US$ 0,18` que «P&L líquido US$» do último trade.** Dois sítios, um número — o operador pode ler «dia» = «última volta». O critério pede o líquido **por trade** visível; o do dia já inclui taxas no incumbente. **Visível:** duas células adjacentes. Disposition: **n/a**.
- **[P2] Dois switches amarelos Ligado / Ligada** (scalp vs ajuste automático). Copy esclarece que o ajuste não manda ordem; o chrome é o mesmo. Risco de tocar no errado. Disposition: **n/a**.
- **[P2] Kill e «posição presa» sem `aria-live` / `role="status"|"alert"`.** WCAG 4.1.3: mudança automática não anunciada se o foco não está no switch. Disposition: **n/a** (Apply a11y).

### P3 — detalhe de Apply / incumbente (não reabrir como P0/P1)

- **[P3] Fixtures proto** «Simular kill / posição / último resultado / posição presa», «Ver taxa BNB», «Ver sem chave Spot» não vão ao produto. Disposition: **aceito-P3-Apply**
- **[P3] «Pausar ajuste automático» / «Voltar à versão anterior»** são controlos de produto no proto; o *como* do persistir é Apply. Disposition: **aceito-P3-Apply**
- **[P3] Contraste P&L 4.48:1** — token incumbente `trading-down`. Disposition: **aceito-P3-Apply**
- **[P3] 7d visível como Gráfico** — incumbente; landmark `data-landmark="7d"` presente. Disposition: **n/a**
- **[P3] Modal Operar ausente no proto** — o card não o redesenha. Disposition: **aceito-P3-Apply**
- **[P3] Sem fixture de P&L positivo** — a regra (negativo tão visível) está no glifo `−` + vermelho. Disposition: **aceito-P3-Apply**
- **[P3] Tabela mobile em cards** — clone incumbente. Disposition: **aceito-P3-Apply**
- **[P3] Backtest / aggTrades / BCa / teto 10 bp** — *como*, não tela. Disposition: **aceito-P3-Apply**

## Disposition (resumo)

| Finding | Gravidade | Disposition |
|---|---|---|
| (nenhum P0/P1) | — | n/a |
| Diagnóstico + 12 células empurram a board | P2 | n/a |
| P&L do dia = P&L líquido da última volta | P2 | n/a |
| Ligado vs Ligada (dois switches) | P2 | n/a |
| Kill/presa sem live region | P2 | n/a |
| Fixtures, contraste, 7d/Gráfico, modal, cards, *como* do backtest | P3 | aceito-P3-Apply |

## Tokens do autor

**ok**

- `UI impact: affected`
- `live_route: /monitor`
- `surface: existing`
- regiões clonadas = shell + `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia
- URL canónica = clone `/monitor` + delta de copy no scalp/diagnóstico; **não** painel ANTES/DEPOIS; **não** grelha de N estados

## Verdict

**PASS**

Nenhum P0/P1 de produto/escopo/contrato visível. Teto 1+1+1: este artefacto é o Assessment A pós-I4; P3 aceitos ficam no Apply; P2 residuais não justificam segundo rework.

Design fecha em 1+1+1: sem `## Design Critique` aqui (o pai publica).

## Artefactos desta sessão

- `.impeccable/critique/1070-card-1070-scalp-jev-lucro-liquido-A.md` (este arquivo; única escrita)
