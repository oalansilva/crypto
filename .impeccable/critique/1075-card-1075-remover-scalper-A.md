# Assessment A — card 1075 · change card-1075-remover-scalper

> Avaliador A isolado (produto / UX / heurísticas / contrato visível). Onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem `move_agent_to_root`. Única escrita: este arquivo.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 1075 — Remover o scalper (Scalp Jev) inteiro: tela, laço, ordens, tabelas e specs
- change: `card-1075-remover-scalper`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1075-remover-scalper`
- branch / q_git: `card-1075-remover-scalper` @ `3a2a3e94` (HEAD = develop; change + proto **untracked**, típico de Design)
- tuple: `bound_card=1075` · Status=Design (prompt do pai; MUST NOT arrastar)
- data (UTC): 2026-10-02T02:34Z
- modelo desta sessão: **Grok 4.6**, slug **`cursor-grok-4.6-high`**
- UI impact (rubrica D4): **affected** · `live_route: /monitor` · `surface: existing` — linhas próprias parseáveis de `design.md`
- Issue: REST `gh api repos/oalansilva/crypto/issues/1075` (não `gh issue view`). Fronteira = body grelhado (Problema / História / Entra / Não entra) = `proposal.md`. Sem reentrevista.
- Digest proto (prompt + disco + HTTPS, verificado nesta sessão):
  - canónico `index.html` sha256 `9f5dcb0c48f0de71ffdf02ce92a781bb720f1e1a01eeabc6e205025b6aab71f3` · 31551 B
  - extra `landing.html` sha256 `4f1bd81b49609a566261cdd8ee485a257d19d7c2740e826ba26c43201b1b53a4` · 27413 B
  - extra `ajuda.html` sha256 `8ea541e1c58e9e0bceb1ee23cc5e3f5fb6ae07b59c439921571fea0838826fd4` · 11219 B
  - extra `perfil.html` sha256 `cbb5a18df175b5da41ba8a01db888284579648528b69a80e93f131dd8a0db53e` · 11189 B
  - extra `credenciais.html` sha256 `a0c48788dd1d25fb0c02a59a5a7fc0cd1df4e88cc9c741364e28f1d6b42c24b1` · 9653 B
  - `design.md` sha256 `629150612b680198ff7523f77f404853ebe17cab298d1a9b2a9a06380943fde1` · 1508 palavras · 10644 B
- Servido HTTPS == disco: IDENTICAL (sha256 e bytes iguais nos cinco HTML; HTTP 200)
- Irmãos HTML: os quatro extras **não** entram no index (só citados em comentário de fonte). T5 mede o index.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Tooling: Playwright Python + Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`, headless) contra HTTPS real. Viewports 1280×800 e 390×844. Browser MCP Cursor tentado (`browser_tabs` cria tab e evapora; `browser_navigate` recusa sem tab estável) — fallback Playwright, mesmo método das avaliações A #1070/#1001. Evidência em `/tmp/1075-A` (não persistida: este filho só escreve o snapshot).
- Mode: Impeccable **Operate**. `DESIGN.md` autoridade visual, não sobrescrito. Sem redesign da board.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | Landmarks `/monitor` |
|---|---|---|
| `https://dev.criptofarol.com.br/monitor` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | 0 (`table.signals` = 0) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) digest local == HTTPS, (3) catálogo `scripts/process-fsm/route-landmarks.yaml`, (4) incumbente `MonitorStatusTab.tsx` (ainda importa `ScalpModule` — o Apply é que o tira). Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

Landing viva `https://criptofarol.com.br/` (HTTP 200, 27210 B, sha256 distinto do extra): **ainda menciona scalp** no FAQ (4 hits visíveis). Isso é o incumbente a cortar, não prova do proto.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias:

```
UI impact: affected
live_route: /monitor
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/monitor`; **não** superfície nova; delta = ausência do módulo Scalp BTCUSDT; board (Em posição, Saída/cobertura, KPIs, filtros, `table.signals`, Operar) continua. Extras na mesma pasta, cada um clone da página viva + copy sem scalper/scalp e sem anunciar que saiu; **não** entram no index. URL canónica **não** é painel ANTES/DEPOIS nem grelha de N estados. `COPIED:start`/`COPIED:end` = 7/7 no index (tokens + monitor-theme + AppNav + chrome KPIs/filterbar + Em posição + `table.signals` + Saída/cobertura). **PASS** deste item da rubrica.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `index.html` | `9f5dcb0c48f0de71ffdf02ce92a781bb720f1e1a01eeabc6e205025b6aab71f3` | 31551 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-1075-remover-scalper/` | idêntico | 31551 | 200 |
| prompt desta sessão | idêntico | — | — |
| disco `landing.html` | `4f1bd81b49609a566261cdd8ee485a257d19d7c2740e826ba26c43201b1b53a4` | 27413 | 200 HTTPS |
| disco `ajuda.html` | `8ea541e1c58e9e0bceb1ee23cc5e3f5fb6ae07b59c439921571fea0838826fd4` | 11219 | 200 HTTPS |
| disco `perfil.html` | `cbb5a18df175b5da41ba8a01db888284579648528b69a80e93f131dd8a0db53e` | 11189 | 200 HTTPS |
| disco `credenciais.html` | `a0c48788dd1d25fb0c02a59a5a7fc0cd1df4e88cc9c741364e28f1d6b42c24b1` | 9653 | 200 HTTPS |

Disco == HTTPS == prompt (index): IDENTICAL.

## Fidelidade (clone da página viva)

Catálogo `/monitor` (`route-landmarks.yaml`): selector `table.signals` · texts `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`, `Operar`, `Par / Estratégia`.

Incumbente HEAD `MonitorStatusTab.tsx`: `<ScalpModule />` ainda entre o chrome e a board; thead `data-landmark="7d"` com texto visível **Gráfico**. O proto **omite** o módulo (contrato) e usa cabeçalho visível `7d` (CSS `7D`) — o texto do catálogo está; o atributo `data-landmark` não. Isso é P3 de clone, não P0 (o gate P0 deste card é ausência do scalper + board intacta, não o spark label).

| Landmark | Catálogo / vivo | Proto HTTPS + Playwright (1280) |
|---|---|---|
| `table.signals` | tabela da board | count=2, visíveis desktop (Em posição + Saída); `y≈473` e `y≈673` |
| Status / Preço / Distância / Risco até stop / Tags / Operar / Par / Estratégia | thead | exact visíveis (CSS uppercase: STATUS, PREÇO, RISCO ATÉ STOP, OPERAR) |
| 7d | catálogo = texto `7d`; vivo = `Gráfico` + `data-landmark="7d"` | texto `7d` visível ×2; `data-landmark="7d"` = 0 |
| Operar | botão de linha | 2 botões visíveis, `disabled=false` (desktop); nas cards mobile também |
| Em posição / Saída / cobertura | secções + KPIs | KPIs 4 colunas (`Em posição 1` / `Saída / cobertura 1` / `Total 2` / `Em carteira 2`); filtros `Em portfólio` |

Anti-padrões P0:

- URL canónica `…/prototypes/card-1075-remover-scalper/` → `index.html` é o Monitor autenticado (shell 224px + topbar + `page-sub` + KPIs + filterbar + `table.signals`). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES/DEPOIS` = 0 (único hit `ANTES` está em comentário de fonte «Sem ANTES/DEPOIS»).
- **Não** é grelha de N estados. Zero `.state-grid` / galeria / `review-bar` / `off.html` / `kill.html`. Um único HTML canónico. Extras são URLs irmãs, não o index.
- `COPIED:start`/`COPIED:end` = 7/7.
- Chrome (sidebar 224px, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Monitor `aria-current=page`, Inter/BinanceNova) = **folha**, não prova. Prova = landmarks do catálogo no proto canónico + **ausência** do módulo scalp no sítio onde o vivo ainda monta `ScalpModule`.
- `Telegram: on` no topbar = chrome incumbente de alertas, **não** anúncio de descontinuação.

## Produto (escopo — não reabrir grelha)

Delta pedido (#1075 Entra.1, visível nesta onda): o módulo do scalper some do Monitor; Em posição, Saída/cobertura, KPIs e filtros ficam. Ajuda, Perfil, Credenciais e landing deixam de mencionar scalper/scalp e **não** anunciam que saiu.

Entra.2–5 (API 404, DROP de tabelas, flags, specs) são **fora da tela** — P3 de Apply, não reabertos como P0/P1.

Vista canónica observada (load fresco, sem fixtures):

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Módulo Scalp BTCUSDT ausente (desktop e mobile) | 0 `role=switch`; 0 id/class/aria `scalp*`; innerText sem `scalp`/`scalper`/`jev`; KPIs `y=170` (1280) imediatamente após o `page-sub` | OK |
| Em posição, Saída/cobertura, KPIs, filtros ficam | 4 KPIs + filterbar + 2 `table.signals` (1280); no 390, KPIs + filtros + cards SOL/ETH | OK |
| `table.signals` + Status / Preço / Risco até stop / Operar | 2 tabelas visíveis a 1280; theads com os quatro (e Distância / Tags / Par / 7d) | OK |
| URL canónica ≠ grelha de N estados ≠ ANTES/DEPOIS | 1 HTML; 0 galeria; 0 `review-bar`; 0 botões Antes/Depois | OK |
| Operar intacto; sem mutex (não há scalp para mutex) | botões Operar `disabled=false` desktop e mobile | OK |
| Extras sem menção visível a scalper/scalp | landing / ajuda / perfil / credenciais: innerText `scalp` = 0 (1280 e 390) | OK |
| Sem banner / Telegram / texto de descontinuação | 0 `descontinu` / `removemos` / `não está mais`; 0 banner de saída. «Telegram: on» = chrome Monitor. Landing «se saiu antes» = histórico da estratégia, não descontinuação | OK |
| Landing: cortar scalp, manter Operar com confirmação e nunca saque | FAQ «Não. O Operar pede confirmação em cada clique. Nunca saque.»; «Não opera sozinho» **sem** a cláusula scalp do vivo; 0 `post-only` / `limitadora` / `24/7` | OK |
| Perfil: Spot para Operar, sem scalp | «Spot Trade (sem saque) opcional para Operar no Monitor» | OK |
| Credenciais: Spot para Operar/stop, sem scalp | «Spot Trading (sem withdraw)» / «proteger stop e Operar no Monitor» | OK |
| Ajuda: carteira opcional + Operar com confirmação, sem scalp | intro «carteira Binance e opcional (leitura e Operar com confirmacao)» | OK |
| Não restaurar «nunca envia ordem» como absoluto | Operar continua a confirmar cada clique; decisão 2 respeitada | OK |

Não-goals respeitados na tela: board não redesenhada; Operar/Carteira/chave Spot não removidos; sem stub «o scalper saiu»; sem 410/banner. API/migração/flags = Apply.

Contraste vivo vs extra (prova do corte, não do clone autenticado): landing pública ainda diz «Há um scalp direcional BTCUSDT que você pode ligar no Monitor» (4 hits). O extra `landing.html` corta essas frases e deixa o Operar.

## UX

Hierarquia desktop: shell autenticado → chrome Monitor → **KPIs** (`y=170`) → filtros (`y=292`) → Em posição / `table.signals` (`y≈421–473`). Não há faixa Scalp BTCUSDT entre `page-sub` e KPIs. Uma tarefa: ler a board e Operar. Carga **baixa (Operate)** — o delta *reduz* ruído face ao #1070 (12 células + diagnóstico).

Mobile 390: primeiro viewport = topbar + KPIs empilhados + filtros; cards SOL/ETH `y≈915` / `y≈1256` (abaixo do fold). Clone incumbente ≤740px (tabela `display:none` via `.table-wrap`), não ausência do contrato. Cards trazem **Operar** não-disabled.

Prevenção: o proto não esconde o módulo com CSS/`hidden` — o markup do scalp não existe (`scalp_dom=[]`). Recuperação: não há kill/switch a religar; o caminho de envio que fica é o Operar de sempre.

Pico emocional: a board volta a ser a primeira coisa que o trader autenticado vê. Sem interruptor amarelo a competir com Operar.

## Acessibilidade

- `lang=pt-BR`; h1 `sr-only` «Monitor de sinais»; `:focus-visible` 2px `#3b82f6` (Tab em Favoritos → Monitor → …, medido).
- 0 `role=switch` (o interruptor do scalp saiu — correcto). 0 `aria-live` extra (não há banner de kill a anunciar).
- Contraste: shell incumbente `#0b0e11`; amarelo `#fcd535` nos CTAs; pills Em posição / Saída com texto, não só cor.
- Search desktop 22px de altura — incumbente compacto, não o delta.
- Ajuda: `<title>` ainda «Como usar o Cripto Farol — protótipo card-718». O h1 visível está limpo. Tab do browser vaza o número de outro card — P3, não contrato de copy.

## Responsividade

Desktop 1280: sidebar 224px `display:flex`; 2 `table.signals` visíveis; mobile-cards `visible=0`. Coluna Operar da linha SOL clipa «Ver Trades» no primeiro screenshot (incumbente P3).

Mobile 390: sidebar `none`; `.table-wrap { display:none }`; 2 `.mobile-card` visíveis com Em posição / Saída / cobertura e Operar. Search corta o placeholder (incumbente). Sem módulo scalp acima dos KPIs.

Landing / ajuda / perfil / credenciais a 390: 0 hits visíveis `scalp`.

## Estados

O aceite visível deste card **não** é uma máquina de estados do scalp (off/on/kill). O estado canónico é **um**: Monitor sem o módulo, board viva. Não há fixtures «Simular *». Não mocka: 404 `/api/scalp/status`, restart sem flags, ausência de log Jev — Apply.

Extras cobrem as quatro superfícies de copy. `OnboardingGuide` (Q7=B) fora deste proto, como o `design.md` manda.

## Design specificity

A composição é o Monitor autenticado do Farol **sem** a faixa Scalp BTCUSDT. Não iria a um SaaS genérico inalterado: AppNav Cripto Farol, `table.signals`, Em posição / Saída / cobertura, Operar, tokens Binance (`DESIGN.md`), vocabulário de risco até stop. Landing v4 + FAQ do Farol. Modo Impeccable: **Operate**. Delta = ausência do módulo + corte de cláusulas scalp nas extras, sem anúncio.

## Heurísticas Nielsen (0–4, Operate)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | KPIs + última leitura + badges; o módulo que mentia estado de envio saiu |
| 2 | Match between system and real world | 4 | Vocabulário do issue; FAQ admite Operar com confirmação e não finge «nunca envia» |
| 3 | User control and freedom | 3 | Operar fica; filtros do proto são estáticos (clone) |
| 4 | Consistency and standards | 3 | Clone do shell/board; thead `7d` vs vivo `Gráfico`; title Ajuda card-718 |
| 5 | Error prevention | 4 | Sem CSS-hide; sem stub de descontinuação; Operar não perdeu a confirmação |
| 6 | Recognition rather than recall | 4 | Board no sítio de sempre; nada a recordar do scalp |
| 7 | Flexibility and efficiency | 3 | Um caminho Operate; proto estático |
| 8 | Aesthetic and minimalist design | 4 | Primeiro viewport = board; saiu a faixa de 12 células |
| 9 | Help users recognize, diagnose, recover | 3 | Sem kill a recuperar; Operar/Carteira continuam o caminho de envio |
| 10 | Help and documentation | 3 | Extra Ajuda + FAQ landing sem scalp; title Ajuda ainda diz card-718 |
| **Total** | | **35/40** | Good |

## Cognitive load

Checklist: single focus **passa** (board é a tarefa); chunking **passa** (4 KPIs); grouping **passa**; hierarchy **passa**; one-thing-at-a-time **passa**; minimal choices **passa** no delta (filtros incumbentes ≤4); working memory **passa**; progressive disclosure **falha 1** no mobile (KPIs empilhados empurram as cards — incumbente ≤740px). **1 falha = carga baixa.**

## Brief (só neste snapshot)

Quem vê o Monitor deixa de encontrar o interruptor Scalp BTCUSDT; a board (Em posição, Saída/cobertura, KPIs, filtros, Operar) é outra vez a superfície. Visitante na landing e leitor de Ajuda/Perfil/Credenciais deixam de ler cláusulas de scalp e **não** são informados de que «saiu». Audience: trader autenticado no `/monitor` (e Alan em T7). Outcome: ausência do módulo, resto igual. Direction: Operate — clone da página viva + delta = omissão. Mode: **Operate**.

## Personas

- **Trader beta no `/monitor`:** abre a tela e a primeira grelha é Em posição / Saída. Sem switch amarelo a competir com Operar. Sem red flag.
- **Alan em T7:** o index é o Monitor, não um painel ANTES/DEPOIS. A prova é o vazio entre `page-sub` e KPIs. Sem red flag.
- **Visitante da landing / leitor de Ajuda:** FAQ «É um robô que opera por mim?» responde com Operar+confirmação, sem a excepção post-only do scalp. Perfil/Credenciais apontam Spot para Operar, não para um loop. Sem red flag de descontinuação.

## Strengths

1. Clone da **página**, não da folha de tokens: landmarks, KPIs e Operar no sítio; o delta é um buraco honesto.
2. Copy das extras corta a menção **sem** restaurar o absoluto «nunca envia» e **sem** anunciar a saída.
3. URL canónica única; extras fora do index; digest disco == HTTPS == prompt.

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.
  - `table.signals` presente (2 visíveis a 1280) com Status / Preço / Risco até stop / Operar.
  - URL canónica = clone Operate `/monitor`, não grelha de N estados nem ANTES/DEPOIS.
  - Módulo do scalper ausente em desktop e mobile (0 switch, 0 texto visível `scalp`/`scalper`/`jev`).
  - Extras sem menção visível e sem texto de descontinuação.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- nenhum de produto/escopo/contrato. Residuais de clone (7d vs Gráfico, title Ajuda, clip Operar) descem a P3.

### P3 — detalhe de Apply / incumbente (não reabrir como P0/P1)

Já aceitos no `design.md` (reafirmados, não reabertos):

- Nome/corpo da migração Alembic; inventário `scalp_*` / systemd / overlay. Disposition: **aceito-P3-Apply**
- Como o runtime-worker arranca sem `RUN_SCALP_LOOP`. Disposition: **aceito-P3-Apply**
- Recriação dos snapshots Playwright do Monitor. Disposition: **aceito-P3-Apply**
- `/api/scalp/status` → 404; flags; apagar changes #1045/#1070. Disposition: **aceito-P3-Apply**

Novos P3 desta sessão:

- **[P3] Thead `7d` vs vivo `Gráfico` + `data-landmark="7d"` ausente.** Catálogo pede o texto `7d` (presente); o incumbente mostra Gráfico. Apply pinta a coluna viva. Disposition: **aceito-P3-Apply**
- **[P3] `<title>` da Ajuda ainda «protótipo card-718».** H1 visível está limpo; a tab do browser vaza o clone. Disposition: **aceito-P3-Apply**
- **[P3] Comentários HTML nomeiam scalper/scalp** («Delta: módulo do scalper ausente»). Não entram no innerText. Disposition: **n/a**
- **[P3] Clip Operar/Ver Trades a 1280; search mobile corta placeholder; tabela→cards ≤740px.** Incumbente. Disposition: **aceito-P3-Apply**
- **[P3] Nav de Credenciais mais magra** (sem Descoberta/Combo/Admin) vs Perfil. Clone da superfície, não do Monitor. Disposition: **aceito-P3-Apply**
- **[P3] Ajuda sem acentos** (`estrategias`, `confirmacao`) — herança do clone #718. Disposition: **aceito-P3-Apply**
- **[P3] Modal Operar ausente no proto** — o card não o redesenha. Disposition: **aceito-P3-Apply**
- **[P3] `ScalpModule.tsx` ainda no incumbente** — prova de que o Apply tem trabalho; o proto já mostra o depois. Disposition: **aceito-P3-Apply**

## Disposition (resumo)

| Finding | Gravidade | Disposition |
|---|---|---|
| (nenhum P0/P1) | — | n/a |
| 7d vs Gráfico / landmark; title Ajuda card-718; clip incumbente; comments; API/migração/flags | P3 | aceito-P3-Apply |

## Tokens do autor

**ok**

- `UI impact: affected`
- `live_route: /monitor`
- `surface: existing`
- regiões clonadas = shell + chrome KPIs/filterbar + Em posição + `table.signals` + Saída/cobertura (Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia)
- URL canónica = clone `/monitor` + delta = módulo ausente; **não** painel ANTES/DEPOIS; **não** grelha de N estados
- extras = copy sem scalp e sem descontinuação; não são o index

## Verdict

**PASS**

Nenhum P0/P1 de produto/escopo/contrato visível. Teto 1+1+1: este artefacto é o Assessment A; P3 aceitos ficam no Apply; nenhum P2 justifica segundo rework.

Design fecha em 1+1+1: sem `## Design Critique` aqui (o pai publica).

## Artefactos desta sessão

- `.impeccable/critique/1075-card-1075-remover-scalper-A.md` (este arquivo; única escrita)
