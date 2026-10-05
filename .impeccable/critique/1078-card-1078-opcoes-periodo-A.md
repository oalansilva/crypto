# Assessment A — card 1078 · change card-1078-opcoes-periodo

> Avaliador A isolado (produto / UX / acessibilidade / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem resultados do Assessment B. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem `move_agent_to_root`. Única escrita: este arquivo.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 1078 — crie mais opções de peridos (lista partilhada de período na Descoberta e no Combo)
- change: `card-1078-opcoes-periodo`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1078-opcoes-periodo`
- branch / q_git: `card-1078-opcoes-periodo` @ `26c8aa2c` (HEAD; HTML proto ainda untracked)
- tuple: `bound_card=1078` · Status esperado=Design (MUST NOT arrastar)
- data (UTC): 2026-10-05T01:50Z
- modelo desta sessão: **Grok 4.6**, slug **`cursor-grok-4.6-high`**
- UI impact (rubrica D4): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias parseáveis de `design.md` (L1–L3)
- Issue: REST `gh api repos/oalansilva/crypto/issues/1078` (OPEN). Fronteira = body grelhado (Problema / História / Entra / Não entra). Sem reentrevista.
- Digest proto (disco + Vite local 5173/5175 IDENTICAL; HTTPS público 404):
  - canónico `index.html` sha256 `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` · 61431 B = 27836 copied + 33595 generated (pares `COPIED:start`/`COPIED:end` 15/15)
  - extra `combo.html` sha256 `c7328b35ac09763e4ebac63f3628792030d00378e2c12403a31c172e004511b8` · 19187 B
  - `http://127.0.0.1:5173/prototypes/card-1078-opcoes-periodo/` IDENTICAL (HTTP 200, mesmo sha256, mesmos bytes)
  - `http://127.0.0.1:5175/prototypes/card-1078-opcoes-periodo/` IDENTICAL
  - `http://127.0.0.1:5173/prototypes/card-1078-opcoes-periodo/combo.html` IDENTICAL
  - HTTPS `https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/` → HTTP 404, 604 B, página «Protótipo não encontrado» (pai ainda não publicou; `design.md` §Prototype Validation já diz que a dupla abre a URL pública depois do pai publicar)
- Irmãos HTML: `combo.html` extra (nunca canónico; T5 mede só o index).
- Ignore list: `.impeccable/critique/ignore.md` ausente
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Tooling: Playwright Python 1.62 + Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`, headless) contra Vite local IDENTICAL. Viewports 1280×800 e 390×844. Browser MCP: live `/combo/discovery` → `/login`; tab nova a `127.0.0.1:5173` → `chrome-error://chromewebdata/` (localhost inacessível ao MCP). Evidência = Playwright. Screenshots em `/tmp/1078-A` (não persistidos: este filho só escreve o snapshot).
- Mode: Impeccable **Operate**. `DESIGN.md` autoridade visual, não sobrescrito. Sem redesign da Descoberta.

## Limitação de sessão (obrigatória)

| URL pedida | URL final / evidência | Landmarks `/combo/discovery` |
|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | SPA autentica; pixels = cartão **Bem-vindo de volta** (login). Playwright `page.url` ficou `/combo/discovery` mas h1 da Descoberta = 0. MCP: URL final `/login`, h1 `Bem-vindo de volta` | 0 |
| HTTPS proto canónico | HTTP 404 «Protótipo não encontrado» | n/a |
| MCP `http://127.0.0.1:5173/prototypes/card-1078-opcoes-periodo/` | `chrome-error://chromewebdata/` | n/a |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico local com digest == `design.md` / prompt, (2) catálogo `scripts/process-fsm/route-landmarks.yaml`, (3) fonte viva `DiscoveryPage.tsx` / `ComboConfigurePage.tsx` (só leitura). Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. O 200 do proto local coincide com digest e com asserts de landmark/contrato no browser. HTTPS público 404 não é P0 de produto (publicação do pai).

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/discovery`; **não** superfície nova; **não** empresta `/combo/select` nem `/favorites`. Extra `combo.html` clona `/combo/configure` e **nunca** é URL canónica. Regiões clonadas marcadas (`COPIED:start`/`COPIED:end` 15/15 no index): shell AppNav; heading; 3 modos; cartão Rascunho; Preflight; chrome Acompanhar; grelha Decidir. Delta só no campo Período + datas Personalizado + copy de Preflight / selo de amostra. URL canónica **não** é painel ANTES/DEPOIS nem grelha de N estados. **PASS** deste item da rubrica.

## Digest proto (disco == local servido)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-1078-opcoes-periodo/index.html` | `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` | 61431 | — |
| disco `combo.html` | `c7328b35ac09763e4ebac63f3628792030d00378e2c12403a31c172e004511b8` | 19187 | — |
| Vite `127.0.0.1:5173` index + combo | idêntico | 61431 / 19187 | 200 |
| Vite `127.0.0.1:5175` index + combo | idêntico | 61431 / 19187 | 200 |
| `design.md` §Prototype Validation | idêntico (index) | 61431 | — |
| HTTPS `dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/` | 404 «Protótipo não encontrado» | 604 | 404 |

Disco == Vite 5173/5175 == prompt: IDENTICAL. HTTPS ainda não publicado.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

Fonte viva `DiscoveryPage.tsx` (só leitura): h1 Descoberta; aside `aria-label="Preflight da varredura"`; h2 `Rascunho de varredura`; seletor incumbente `all` / `2y` / `6m` com rótulos «Todo o histórico» / «Últimos 2 anos» / «Últimos 6 meses»; default `useState('all')`.

Fonte viva `ComboConfigurePage.tsx` (só leitura): `useState<PeriodKey>('all')`; rótulo incumbente «Todo o período»; lista `Últimos 6 meses` / `Últimos 2 anos` / `Todo o período`. Hint «todo o histórico disponível».

| Landmark | Catálogo / vivo | Proto 5173 + Playwright (1280 e 390) |
|---|---|---|
| `Descoberta de estratégias swing` | h1 | h1 visível no default Montar; exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 `Preflight` | h2 visível no default Montar; aside `aria-label="Preflight da varredura"` |
| `Rascunho de varredura` | h2 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2 visível no default Montar |

Anti-padrões P0:

- URL canónica (index) é a Descoberta autenticada (shell 224px + breadcrumb Combo/Varreduras + h1 + 3 modos + Montar + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES`/`DEPOIS` = 0 (único hit está em comentário de fonte: «sem painel ANTES/DEPOIS»).
- **Não** é grelha de N estados no lugar da listagem. Default canónico = Montar (`#panel-montar.active`). Tabs **trocam markup** (`.modepanel.active` único; Acompanhar revela progresso+parciais; Decidir revela `table.lb` + selo).
- Pares `COPIED:start`/`COPIED:end` = 15/15; soma UTF-8 copiada > 0.
- Extra `combo.html`: h2 `Template Information` + `Configuration`; nav Combo `aria-current=page`; **não** é URL canónica.
- Chrome (sidebar, amarelo `#fcd535`, nav Descoberta `aria-current=page`) = **folha**, não prova. Prova = landmarks do catálogo no proto canónico + delta só no período / Preflight / selo.

## Produto (escopo — não reabrir grelha)

Contrato grelhado observado (`Entra` do issue #1078 via REST; Playwright 1280 e 390):

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Mesma lista nas duas telas, nesta ordem | index + combo: `15 dias`, `1 mês`, `3 meses`, `6 meses`, `1 ano`, `2 anos`, `Personalizado`, `Todo o histórico`. 0 «Últimos 6 meses» / «Últimos 2 anos» / «Todo o período» | OK |
| Descoberta abre em 15 dias | load fresco: `selected=15d` «15 dias»; Preflight `15 dias [20 set. 2026, 05 out. 2026)`; CTA `Iniciar varredura — 1, ~2 min` enabled | OK |
| Combo marca inicial = incumbente `all`, não decisão | combo load: `selected=all` «Todo o histórico»; hint «todo o histórico disponível»; HTML comenta «NÃO é decisão #1078»; innerText sem «decisão» / «default novo» | OK (aberto no issue) |
| Personalizado: datas vazias bloqueiam e nomeiam | custom vazio: datas visíveis; CTA disabled; «Seleccione Data Inicial e Data Final.»; estado «Bloqueado — veja o que falta» | OK |
| Só uma data | só inicial → «Seleccione Data Final.»; só final → «Seleccione Data Inicial.» | OK |
| Data Inicial depois da Data Final | 04 out. > 01 out.: «Data Inicial não pode ser depois da Data Final.»; CTA disabled | OK |
| Data Final no futuro | JS `2026-10-20` / `2026-12-01` (picker nativo tem `max=hoje`): «Data Final não pode ser depois de hoje.»; CTA disabled | OK |
| Janela curta não bloqueia o início | 15d e 1m: CTA enabled; 0 impedimento; Decidir tem selo `Amostra insuficiente` (1 linha, rank —) | OK |
| Todo o histórico sem inventar datas | `all`: Preflight «Todo o histórico» sem par `[start, end)` | OK |
| Ranking / Short / Monitor / Favoritos intactos | Ranking Calmar vs CAGR vs B&H permanece; Short só Long na Descoberta; Monitor/Favoritos só nav | OK |

Não-goals respeitados na tela: sem Monitor; sem colunas de Favoritos; ranking principal intacto; Short fora do Montar da Descoberta.

## UX

Hierarquia desktop: shell autenticado → h1 Descoberta → tablist 3 modos → **Montar** (Rascunho + Preflight). Uma decisão de período (select) + progressive disclosure das datas só em Personalizado. Combo extra: Template Information → Configuration → Período + hint.

Carga cognitiva: **média-baixa (Operate)**. 8 opções no select (não 8 rádios); datas só quando `custom`. Default 15 dias reduz o passo. Combo 8 opções iguais — um vocabulário.

Prevenção: `type=date` + `max=hoje`; CTA desactiva com impedimento nomeado. Recuperação: voltar a 15d / `all` reabilita; Novo rascunho no Acompanhar volta a Montar.

Pico: Preflight a ecoar rótulo + janela no glance (`15 dias [20 set. 2026, 05 out. 2026)`) — alinha com o problema grelhado (varredura na janela escolhida, não nas 3 opções antigas).

## Acessibilidade

- `lang="pt-BR"`; `:focus-visible` 2px `#3b82f6`; `select`/`input`/`button` `min-height: 44px`.
- Tabs `role=tablist/tab/tabpanel` + `aria-controls` + setas + roving tabindex; 1 painel `.active`.
- Progressbar ARIA completa (`valuemin/max/now` + label).
- Tabelas em `role=region` `tabindex=0` + caption sr-only.
- Seletor: `select` nativo `aria-label="Período histórico"` / Combo `aria-label="Período"`; datas `aria-label="Data Inicial"` / `Data Final`.
- Impedimentos em lista visível + `aria-live="polite"` na linha de 3 da Descoberta.
- Contraste: tokens incumbentes Binance (`--accent #fcd535`, `--success`, `--danger-text`). Sem par novo.
- Placeholder `mm/dd/yyyy` nos `input type=date` = locale do Chromium headless (en-US), não copy do proto. Apply: widget nativo no browser pt-BR.

## Responsividade

Desktop 1280: sidebar 224px; heading + Rascunho | Preflight; período + ranking 2 colunas; datas Personalizado 2 colunas. Overflow estrutural `scrollWidth==clientWidth` 1280. Combo: Período ao lado do Timeframe; datas debaixo do select.

Mobile 390: sidebar some; mobilebar; Preflight abaixo da dobra (clone do Montar incumbente, P3); período e ranking empilhados; datas empilhadas; CTA visível. Overflow 390==390. Combo custom: datas em coluna; impedimento + CTA no thumb zone.

## Estados

| Estado | Proto | Apply deve… |
|---|---|---|
| Descoberta default 15 dias + 1d | ✓ CTA enabled; janela visível | `useState` Descoberta `15d`; não repor `all` |
| Combo default `all` | ✓ «Todo o histórico»; hint incumbente | **não** mudar `useState` inicial do Combo |
| Personalizado vazio / 1 data / ordem / futuro | ✓ bloqueia + copy da decisão 6 | mesmas frases; CTA disabled |
| Personalizado válido | ✓ CTA enabled; janela nas 3 linhas | persistir `custom` + datas |
| 15d / 1m com 1d | ✓ inicia; Decidir selo amostra | listing-gate existente; sem limiar novo |
| `all` | ✓ rótulo sem datas inventadas | `null, null` |
| loading / erro / 403 / sessão | ausente (mock) | preservar vivo |
| Modal Promover | ausente | preservar vivo |

## Design specificity

A composição canónica é a Descoberta autenticada do Farol (AppNav, 3 modos, Rascunho, Preflight, leaderboard Calmar, selo GO/NO-GO / Amostra insuficiente). Não iria a um SaaS genérico inalterado. Modo Impeccable: **Operate**. Delta = lista de período, default 15 dias, Personalizado inline, copy de Preflight.

Combo extra reusa o shell Binance (o vivo `/combo/configure` ainda é glass claro + dual-list + CTA «Otimizar»). Condensação de chrome = P3 Apply, não furo de lista/default.

## Heurísticas Nielsen (0–4, Operate) — só neste snapshot

| # | Heurística | Score | Nota |
|---|-----------|-------|------|
| 1 | Visibility of system status | 3 | Preflight muda Pronto/Bloqueado; Combo hint mente em custom inválido |
| 2 | Match between system and real world | 4 | «15 dias», «Personalizado», «Todo o histórico» no vocabulário do Entra |
| 3 | User Control and Freedom | 3 | tabs + novo rascunho + select reversível; sem undo das datas |
| 4 | Consistency and Standards | 3 | mesma lista nas duas telas; Combo chrome ≠ vivo glass |
| 5 | Error prevention | 4 | `max=hoje`; CTA disabled; copy nomeia o furo |
| 6 | Recognition rather than recall | 4 | opções visíveis no select; datas só quando precisas |
| 7 | Flexibility and efficiency | 3 | teclado nas tabs; um caminho Operate |
| 8 | Aesthetic and minimalist design | 3 | delta cabe no Montar; Combo omite dual-list/ranges |
| 9 | Help users recognize, diagnose, recover | 3 | copy da decisão 6 na Descoberta; Combo hint contradiz o impedimento |
| 10 | Help and documentation | 3 | hint Combo + Preflight; Ajuda fora de escopo |
| **Total** | | **33/40** | Good |

## Cognitive load

Checklist: single focus no período; chunking do select; datas em progressive disclosure. 8 opções no dropdown (não no glance). Falha residual: Combo mostra hint de histórico cheio **e** «Falta fazer» ao mesmo tempo. **Não é P0.** 1 falha → carga baixa-média.

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.
  - Landmarks 3/3 no proto canónico (Montar para Preflight/Rascunho).
  - URL canónica = clone Operate `/combo/discovery`, não grelha de N estados nem ANTES/DEPOIS.
  - Lista idêntica; Descoberta default 15 dias; Combo `all` sem fingir decisão; Personalizado bloqueia com a copy do Entra; janela curta inicia + selo.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2] Combo `combo.html`: o hint azul afirma a janela (ou «todo o histórico») enquanto o Personalizado está inválido.** Custom vazio: impedimento «Seleccione Data Inicial e Data Final.» **e** hint «Será usado todo o histórico disponível para os símbolos escolhidos.» Data Final futura (ordenado): impedimento «Data Final não pode ser depois de hoje.» **e** hint «Preflight e varredura usam 2026-10-04 → 2026-12-01.» CTA está disabled. **Visível:** caixa azul vs caixa «Falta fazer», desktop e mobile. Disposition: **n/a** (não bloqueia; Apply no Combo só actualiza o hint quando `custom` for válido; nunca reciclar o texto de `all` nem afirmar datas futuras).

### P3 — detalhe de Apply / incumbente (não reabrir como P0/P1)

- **[P3] Montar condensado vs vivo:** eixos em chips (1 template / 1 símbolo) sem workbench/listas inline; CTA `Iniciar varredura — N, ~T` presente. Landmarks Preflight + Rascunho presentes. Disposition: **aceito-P3-Apply** — Apply lê `DiscoveryPage.tsx`.
- **[P3] Combo condensado vs vivo:** dual-list de símbolos, Parameter Optimization Ranges e CTA «Otimizar» (gradiente) omitidos; proto usa shell Binance escuro + «Iniciar Combo». Lista/default/Personalizado estão. Disposition: **aceito-P3-Apply** — Apply lê `ComboConfigurePage.tsx`.
- **[P3] Acompanhar «Long + Short · todo o histórico»** no rascunho congelado — mock de sweep antigo, não o default novo do Montar. Disposition: **aceito-P3-Apply**
- **[P3] Linha meta Estimativa continua `~2 min` com Personalizado bloqueado** (a linha de 3 já mostra `—`). Disposition: **aceito-P3-Apply**
- **[P3] Modal Promover / estados loading-erro-403-sessão ausentes** no mock. Disposition: **aceito-P3-Apply**
- **[P3] HTTPS público 404** — publicação do pai, não furo de produto. Digest local == Vite == `design.md`. Disposition: **aceito-P3-Apply** (pai publica)
- **[P3] Chaves `15d`/`1m`/`3m`/`6m`/`1y`/`2y`/`custom`/`all`**, `resolve_optimizer_date_range`, `getPeriodDates`, UTC do «hoje», `max` do `input type=date`. Disposition: **aceito-P3-Apply** (já no `design.md`)
- **[P3] Locale `mm/dd/yyyy` no Chromium headless** — widget nativo; `lang=pt-BR` no HTML. Disposition: **aceito-P3-Apply**

## Disposition (resumo)

| Finding | Gravidade | Classe | Bloqueia? | Disposition |
|---|---|---|---|---|
| (nenhum P0/P1) | — | — | não | n/a |
| Combo hint mente em Personalizado inválido | P2 | produto visível (copy) | não | n/a |
| Montar/Combo condensados, Acompanhar estático, Estimativa stale, modal, HTTPS 404, chaves, locale date | P3 | detalhe de Apply | não | aceito-P3-Apply |

## Tokens do autor

**ok**

- `UI impact: affected`
- `live_route: /combo/discovery`
- `surface: existing`
- regiões clonadas = shell + heading + 3 modos + Rascunho + Preflight + Acompanhar + Decidir; extra Combo = Template Information + Configuration
- URL canónica = clone `/combo/discovery` + delta período; **não** painel ANTES/DEPOIS; **não** grelha de N estados; `combo.html` nunca canónico

## Verdict

**PASS**

Nenhum P0/P1 de produto/escopo/contrato visível. Teto 1+1+1: este artefacto é o Assessment A; P3 aceitos ficam no Apply; P2 residual do hint Combo não justifica segundo rework.

Design fecha em 1+1+1: sem `## Design Critique` aqui (o pai publica).

## Artefactos desta sessão

- `.impeccable/critique/1078-card-1078-opcoes-periodo-A.md` (este arquivo; única escrita)
