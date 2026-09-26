# Assessment A — card 1001 · change card-1001-scalp-direcional-jev

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem `move_agent_to_root`. Única escrita: este arquivo + PNGs `1001-A-*` + JSON de gate.

`proxy modelo: Assessment A → Grok 4.6 (grok-4.6)`

## Metadata

- card: 1001 — Scalp direcional Binance (Jev): ordem limitadora que não cruza, teto = USDT livre (máx. US$ 100)
- change: `card-1001-scalp-direcional-jev`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1001-scalp-direcional-jev`
- branch / q_git: `card-1001-scalp-direcional-jev`
- tuple: `bound_card=1001` · Status=Design (prompt do pai; MUST NOT arrastar)
- data (UTC): 2026-09-21T02:12Z
- UI impact (rubrica D4): **affected** · `live_route: /monitor` · `surface: existing` — linhas próprias 9–11 de `design.md` (parseáveis)
- Issue: REST `gh api repos/oalansilva/crypto/issues/1001` (não `gh issue view`). Fronteira grelhada (Problema / História / Entra / Não entra). Sem reentrevista. Não reaberta.
- Digest proto (autor, verificado nesta sessão):
  - canónico `index.html` sha256 `f05701794415896410db11db13a900334dd91d45061d875fae3720fb0e353cc8` · 44239 B
  - extra `landing.html` sha256 `a6c48425dff61dcb5e2f30f46384e37a11bcbfe46fa2e9cc7606af5bf82a05d0` · 27342 B
  - extra `ajuda.html` sha256 `99002d6a7f630b74d90ccc4c7ab6c52fd7711323f8c117d58d0975a2062a3bb1` · 11221 B
  - `design.md` sha256 `f7ddb1119015be852a8603ce5e658fd3a9825f067a14101dbf8c0527b0970323` · 11404 B
- Servido HTTPS == local: IDENTICAL (sha256 e bytes iguais nos três HTML; HTTP 200)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Tooling: Playwright Python + Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`, headless) contra HTTPS real. Viewports 1280×800 e 390×844. Detector Impeccable `detect.mjs --json` → `[]` exit 0. 0 pageerror. 1 console 404 `posthog-config.js` (Caddy/dev, não deste card).
- Mode: Impeccable Operate. `DESIGN.md` autoridade visual, não sobrescrito. Sem redesign da board.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | Landmarks `/monitor` |
|---|---|---|
| `https://dev.criptofarol.com.br/monitor` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | 0 (SPA shell 455 B → login) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) HTML local, (3) fonte viva `MonitorStatusTab.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser (90/90 neste filho).

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 9–11:

```
UI impact: affected
live_route: /monitor
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/monitor`; módulo Scalp BTCUSDT **irmão** da board (faixa persistente no `page`, entre `page-sub` e KPIs); **não** superfície nova; **não** dentro do Operar. Regiões clonadas marcadas (`COPIED:start`/`COPIED:end` 10/10): shell autenticado + workbench `table.signals` + Status / Preço / Distância / 7d (`data-landmark`) / Risco até stop / Tags / Operar / Par / Estratégia. Delta fora desses blocos. URL canónica **não** é painel ANTES/DEPOIS. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `index.html` | `f05701794415896410db11db13a900334dd91d45061d875fae3720fb0e353cc8` | 44239 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-1001-scalp-direcional-jev/` | idêntico | 44239 | 200 |
| disco `landing.html` | `a6c48425dff61dcb5e2f30f46384e37a11bcbfe46fa2e9cc7606af5bf82a05d0` | 27342 | — |
| HTTPS `…/landing.html` | idêntico | 27342 | 200 |
| disco `ajuda.html` | `99002d6a7f630b74d90ccc4c7ab6c52fd7711323f8c117d58d0975a2062a3bb1` | 11221 | — |
| HTTPS `…/ajuda.html` | idêntico | 11221 | 200 |
| `design.md` Prototype digest do autor | prefixo `f0570179…` igual | 44239 | — |

Disco == HTTPS: IDENTICAL.

## Fidelidade (clone da página viva)

Catálogo `/monitor` (`route-landmarks.yaml`): selector `table.signals` · texts `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`, `Operar`, `Par / Estratégia`.

Vivo HEAD `MonitorStatusTab.tsx` L1363: `{showTechnicalColumns ? <th className="col-spark" data-landmark="7d">Gráfico</th> : null}` — o texto visível incumbente é **Gráfico**, o landmark canónico é `data-landmark="7d"`. Risco do autor: «Landmark `7d` some no clone» → mitigado. Não é P0.

| Landmark | Vivo `MonitorStatusTab.tsx` | Proto `index.html` + Playwright + PNG |
|---|---|---|
| `table.signals` | tabela da board | count=2 (Em posição + Saída), visível desktop; hidden no mobile `@media max-width:740px` (cards), igual ao clone |
| Status / Preço / Distância / Risco até stop / Tags / Operar / Par / Estratégia | thead | exact visíveis no desktop (2 theads); Operar também nas cards mobile |
| 7d | `data-landmark="7d"` + texto Gráfico | `data-landmark="7d"` count=1, texto CSS `GRÁFICO` |
| Operar | botão de linha + `SpotMarketTradePanel` no vivo | botões Operar desktop e mobile; **não** redesenhados; ligar o scalp **não** os desactiva (sem mutex) |

Anti-padrões P0:

- URL canónica `…/prototypes/card-1001-scalp-direcional-jev/` → `index.html` é o Monitor autenticado (shell 224px + topbar + `page-sub` + **faixa scalp** + KPIs + `table.signals`). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. Texto visível `ANTES/DEPOIS` = 0 (o comentário de fonte não conta como galeria).
- Não é grelha de N estados no lugar da listagem. Default = Operate, interruptor **Desligado**.
- Extras `landing.html` / `ajuda.html` **não** são o index.
- Pares `COPIED:start`/`COPIED:end` = 10/10. Soma UTF-8 copiada medida aqui (inner CSS+HTML) 20580 vs autor 21077 — diferença de contagem T5, não contrato de tela.
- Chrome (sidebar 224px, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Monitor activa) = **folha**, não prova. Prova = landmarks do catálogo no proto canónico, alinhados ao TSX, + delta só na faixa.

## Produto (escopo — não reabrir grelha)

Delta pedido (issue #1001): feature de **produção** (não lab); interruptor **por utilizador**, default desligado, persiste; ordens na Spot **desse** utilizador (Meu Perfil, a mesma do Operar); sem saque; sem conta da casa; módulo no `/monitor` acima dos KPIs; estados desligado / ligado / parado por kill; sem chave Spot → não liga + aponta Meu Perfil; copy «não é bot 24/7» deixa de ser absoluta (landing + Ajuda); Operar intacto; sem mutex; sem «estratégia lucrativa» / «formador de mercado»; calibração visível; P&L negativo tão visível quanto o positivo.

| Aceite visível | Evidência (Playwright + pixels + HTML) | Disposition |
|---|---|---|
| Feature produção, não lab | módulo no `/monitor` autenticado; copy sem «lab» / «só Alan» | OK |
| Interruptor por utilizador; default desligado | `data-state=off`, `aria-checked=false`, rótulo **Desligado** no load (desktop e mobile) | OK |
| Persiste após reinício | contrato escrito (decisão 1 + P3 tabela/JSON); HTML estático demonstra o default off, não a persistência | aceito-P3-Apply |
| Ordens na Spot do utilizador; sem saque; sem conta da casa | «a sua conta Binance» + «Mesma chave Spot de Meu Perfil» + «Nunca saque» no painel | OK |
| Módulo acima dos KPIs | bounding box scalp.y < kpis.y; pixels: faixa entre `page-sub` e KPIs | OK |
| Estados desligado / ligado / parado por kill | fixtures + PNGs off/on/kill; kill banner «Parado por kill (−2% de T). Não religa sozinho.»; religar = o mesmo switch | OK |
| Sem chave Spot: não liga + aponta Meu Perfil | nokey: switch `disabled`, `aria-checked=false`, status «Sem chave Spot em Meu Perfil — não envia. Configure a chave Spot (a mesma do Operar).»; click force não liga | OK |
| Copy 24/7 deixa de ser absoluta (landing + Ajuda) | FAQ «Não por omissão…»; benefício/confiança admitem scalp post-only; Ajuda grelha Carteira admite scalp default off. Sem «não é bot 24/7» | OK no contrato nomeado; residual P2 no rodapé/heading (abaixo) |
| Operar intacto; sem mutex | botões Operar visíveis e não-disabled com scalp on (desktop e mobile) | OK |
| Sem «estratégia lucrativa» / «formador de mercado» no painel | `index` body sem as strings (landing FAQ usa a negação exigida pela decisão 2) | OK |
| Calibração visível | slot «Calibração» sempre; `—` off / `4/9 · 2s` on / `4/11 · 2s` kill | OK (formato = P3 aceito) |
| P&L negativo tão visível quanto o positivo | on `−US$ 0,42` classe `neg` vermelho; kill `−US$ 2,00` classe `neg`; CSS `.pos` existe para o positivo | OK |
| Meu Perfil: cláusula da mesma chave | **não** há extra `perfil.html`; Monitor já nomeia a chave; `design.md` Apply contract + task 5.3 | P2 cobertura — Apply pinta; não bloqueia o canónico |

Não-goals respeitados: board não redesenhada; Operar não redesenhado (modal vivo `SpotMarketTradePanel` fica no Apply, não neste proto); sem futuros/alavancagem/segundo par; sem formador de mercado; sem chave TypeSafe no painel.

## UX

Hierarquia: shell autenticado → chrome Monitor → **faixa Scalp BTCUSDT** (h2 + switch 44px + 5 métricas + status + nota) → KPIs da board → filtros → `table.signals` / cards. Uma decisão (ligar/desligar). Operar continua ao lado, no sítio de sempre.

Carga cognitiva: **baixa–média (Operate)**. Cinco células (T / clip / inventário / calibração / P&L) no tecto Operate; a frase de estado diz o que o loop faz agora. Fixtures «Simular kill» / «Ver sem chave Spot» são proto-only (P3) e não devem ir ao produto.

Prevenção: default off; sem Spot o switch não liga. Recuperação: o mesmo interruptor desliga e religa após kill; o Farol/Monitor não cai. Kill não zera a carteira (copy visível).

## Acessibilidade

- `lang=pt-BR`; `:focus-visible` 2px `#3b82f6`; `prefers-reduced-motion`.
- Interruptor **nomeado**: `role="switch"` + `aria-labelledby="scalp-title"` («Scalp BTCUSDT») + texto visível Desligado/Ligado. Teclado: nativo button; Space no foco liga (assert nesta sessão). Alvo ≥44px desktop e mobile (largura total no 390).
- Estados do switch anunciáveis via `aria-checked`. Kill automático **não** tem `aria-live` / `role="status"|"alert"` no banner nem no `#scalp-status` — P2, não P0 (o controlo principal continua anunciável; o banner é visualmente o canal do kill).
- Contraste (WCAG, medido): switch off 13.36:1; switch on (`#181a20` em `#fcd535`) 12.18:1; P&L neg `#f6465d` em `#1e2329` **4.48:1** (incumbente `trading-down`, à rasca de 4.5); P&L pos 7.44:1; status 14.69:1; nota `#707a8a` em `#181a20` 4.01:1 (incumbente muted, 11.5px — P3). Disabled = opacidade 0.45 (excepção 1.4.3; a frase de Meu Perfil está a contraste cheio).
- Cor do P&L negativo não é a única via: glifo `−` + `US$` no texto.

## Responsividade

Desktop 1280: faixa + KPIs 5 colunas + tabela com landmarks; coluna Operar clipa «Ver Trades»/«Operar» (incumbente P3). Mobile 390: switch full-width; KPIs 2 colunas (P&L na última fila); tabela `display:none`; cards com Operar intacto; kill banner wrapa; search corta o placeholder (incumbente).

## Estados

Mock cobre: **off** (default) · **on** (P&L neg + calibração + Operar vivo) · **kill** (banner + P&L −US$ 2,00 + switch age como off + religar no mesmo switch) · **nokey** (disabled + Meu Perfil). Não mocka: Jev indisponível (decisão 4, copy já escrita), P&L positivo, aviso de inventário clipado após Operar (P3 aceito), persistência pós-reload, log de ticks. Cobertura do aceite visível do Entra está fechada.

## Design specificity

A composição é o Monitor autenticado do Farol + faixa scalp BTCUSDT. Não iria a um SaaS genérico inalterado: AppNav Cripto Farol, `table.signals`, Em posição / Saída / cobertura, Operar, tokens Binance (`DESIGN.md`). Modo Impeccable: **Operate**. Delta = só a faixa + copy 24/7 nos extras.

## Heurísticas Nielsen (0–4, Operate)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 3 | Switch + status + banner kill; falta live region no kill e fixture Jev indisponível |
| 2 | Match between system and real world | 3 | Vocabulário do issue (T, clip, post-only, kill); residual «quem decide é sempre você» no rodapé da landing |
| 3 | User control and freedom | 4 | O mesmo interruptor liga, desliga e religa após kill; sem mutex com Operar |
| 4 | Consistency and standards | 3 | Clone do shell/board; faixa no tema Monitor / `DESIGN.md` |
| 5 | Error prevention | 4 | Default off; sem Spot o switch não liga |
| 6 | Recognition rather than recall | 3 | Calibração e P&L no sítio; Operar continua visível |
| 7 | Flexibility and efficiency | 3 | Um switch; sem modal extra; teclado nativo |
| 8 | Aesthetic and minimalist design | 3 | Faixa densa Operate; botões de fixture são proto-only |
| 9 | Help users recognize, diagnose, recover | 3 | Kill explica que não religa sozinho; nokey aponta Meu Perfil |
| 10 | Help and documentation | 3 | Nota da chave no painel; FAQ landing completa; Ajuda mais magra |
| **Total** | | **32/40** | Good |

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2] Landing ainda diz «quem decide é sempre você»** no `risk-note` e o heading de confiança «não para decidir por você», enquanto o FAQ/benefício da mesma página já admitem o loop sem confirmar cada ordem. O absoluto nomeado «não é bot 24/7» **saiu**. Dual leitura (disclaimer de investimento vs. «o Farol nunca executa»). **Visível:** rodapé do signup + h2 da secção confiança. Disposition: **n/a** (não bloqueia; Apply da copy landing pode alinhar o rodapé à decisão 2 sem reabrir grelha).
- **[P2] Ajuda: intro menciona carteira sem a distinção Spot/scalp; a grelha Carteira admite o scalp default-off mas não diz que, ligado, envia post-only sem confirmar cada ordem.** Spec `user-onboarding` pede a distinção no intro *se* mencionar carteira. OnboardingGuide **correctamente** não nomeia Operar (Q7=B). **Visível:** header + artigo Carteira em `ajuda.html`. Disposition: **n/a** (não bloqueia; landing FAQ cobre a verdade; Apply Help).
- **[P2] Kill/status sem `aria-live` / `role="status"|"alert"`.** O interruptor é anunciável (`role=switch` + `aria-checked`); o kill automático (sem foco no switch) não empurra status message (WCAG 4.1.3). **Visível:** `#scalp-status` e `#scalp-kill` sem live region. Disposition: **n/a** (não bloqueia; Apply a11y).
- **[P2] Sem extra Meu Perfil nesta onda.** Contrato visível do `design.md` pede uma cláusula de que a mesma chave Spot alimenta o scalp se ligar. Monitor já o diz. Disposition: **n/a** (não bloqueia o canónico `/monitor`; Apply task 5.3).
- **[P2] Estado «Jev indisponível — sem envio live» não mockado.** Decisão 4 já escreve a copy e proíbe o segredo. Os três estados do Entra (off/on/kill) estão cobertos. Disposition: **aceito-P3-Apply** (não reabrir como P0/P1).

### P3 — detalhe de Apply / incumbente (não reabrir como P0/P1)

Já aceitos no `design.md` (reafirmados, não reabertos):

- Tabela vs JSON do estado persistido. Disposition: **aceito-P3-Apply**
- Worker/loop vs request; cliente HTTP Jev / stand-in; flag post-only `GTX`. Disposition: **aceito-P3-Apply**
- Formato numérico da calibração (`4/9 · 2s`). Disposition: **aceito-P3-Apply**
- Overlay vs faixa (vivo = faixa no `page`). Disposition: **aceito-P3-Apply**
- Wording exacto do aviso de inventário clipado após Operar. Disposition: **aceito-P3-Apply**
- Detector `side-tab` mobile; clip Operar/Ver Trades a 1280. Disposition: **aceito-P3-Apply**

Novos P3 desta sessão:

- **[P3] Fixtures proto** «Simular kill» / «Ver sem chave Spot» / «Voltar com chave Spot» não vão ao produto. Disposition: **aceito-P3-Apply**
- **[P3] Search mobile corta o placeholder** — incumbente do clone. Disposition: **aceito-P3-Apply**
- **[P3] Modal Operar ausente no proto** — o card não o redesenha; Apply mantém `SpotMarketTradePanel`. Disposition: **aceito-P3-Apply**
- **[P3] Sem fixture de P&L positivo** — a regra visível (negativo tão visível) está demonstrada a vermelho + glifo `−`; `.pos` já existe. Disposition: **aceito-P3-Apply**
- **[P3] Contraste P&L/kill 4.48:1 e nota 4.01:1** — tokens incumbentes `trading-down` / `muted`. Disposition: **aceito-P3-Apply**
- **[P3] 404 `posthog-config.js`** no DEV — não é deste card. Disposition: **n/a**
- **[P3] 7d visível como Gráfico** — incumbente HEAD, landmark `data-landmark="7d"` presente. Disposition: **n/a**

## Disposition (resumo)

| Finding | Gravidade | Disposition |
|---|---|---|
| (nenhum P0/P1) | — | n/a |
| Landing residual «quem decide é sempre você» / «não para decidir por você» | P2 | n/a |
| Ajuda intro/grelha incompleta vs spec Spot/scalp | P2 | n/a |
| Kill/status sem live region | P2 | n/a |
| Extra Meu Perfil ausente | P2 | n/a |
| Jev indisponível não mockado | P2 | aceito-P3-Apply |
| P3 já no `design.md` + fixtures/clip/contraste incumbente | P3 | aceito-P3-Apply |

## Tokens do autor

**ok**

- `UI impact: affected` — linha própria 9
- `live_route: /monitor` — linha própria 10
- `surface: existing` — linha própria 11
- regiões clonadas = shell + `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia
- URL canónica = clone `/monitor` + delta faixa scalp; **não** painel ANTES/DEPOIS

## Verdict

**PASS**

Nenhum P0/P1 de produto/escopo/contrato visível. Teto 1+1+1: este artefacto é o Assessment A; P3 aceitos ficam no Apply; P2 residuais não justificam segundo rework.

Design fecha em 1+1+1: sem `## Design Critique` aqui (o pai publica).

## Artefactos desta sessão

- `.impeccable/critique/1001-card-1001-scalp-direcional-jev-assessment-A.md` (este arquivo)
- `.impeccable/critique/1001-A-gate.json`
- `.impeccable/critique/1001-A-desktop-1280x800-{off,on,kill,nokey}.png`
- `.impeccable/critique/1001-A-mobile-390x844-{off,on,kill,nokey}.png`
- `.impeccable/critique/1001-A-landing-desktop-1280x800.png`
- `.impeccable/critique/1001-A-ajuda-desktop-1280x800.png`
