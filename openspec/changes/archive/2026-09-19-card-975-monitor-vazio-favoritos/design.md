## Context

Card **#975**, Status=Design. Incidente DEV 2026-09-18 ~18:07 BRT em `https://dev.criptofarol.com.br/monitor`. Favoritos na mesma sessão listava estratégias; o Monitor não mostrava sinais.

Na conta do administrador: 18 favoritos. `GET /api/favorites/` 200 com 18. `GET /api/opportunities/?tier=1,2,3` (primeira carga, **sem** `refresh=true`) 200 lista vazia. Sem pedido de elegibilidade Spot a seguir. O quadro pintou «Nenhum ativo disponível no monitor». Com recomputação forçada: 11 analisadas; 7 de fora.

**Vivo hoje (pós-#970, `MonitorStatusTab.tsx`):**
- `opportunitiesLoadError && length===0` → «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + Tentar de novo.
- `length===0 && !loading` → «Nenhum ativo disponível no monitor.»
- O incidente foi **200 com lista vazia** (não falha HTTP): cai no vazio de catálogo mesmo com 18 favoritos.
- Spec #970 (`openspec/changes/card-970-favoritos-carga-nao-vazio/specs/monitor/spec.md`) só cobre fetch **fails**. Sucesso vazio MAY mostrar catálogo vazio — é o furo deste card.
- Primeira carga: `fetchOpportunities(tierFilter)` **sem** `{ refresh: true }`. O botão Atualizar manda `refresh=true`.
- Backend `GET /api/opportunities/`: cache in-memory 30s fresco / 600s stale (`allow_stale=True` quando `refresh=false`). `_write_cached_opportunities` grava também `[]`. Lista vazia cacheada **não é** `None` — a primeira visita devolve 200 `[]` sem recomputar.
- `OpportunityService._calculate_opportunities`: fetch de mercado com timeout default **8s**; pending → skip. Skips (delist / sem velas / timeout / config) não entram no payload. Cold start pode devolver `[]`, gravar cache vazio, e o stale TTL prende o quadro até um clique em Atualizar.

**Impeccable (Operate):** audience = operador que abre Monitor com Favoritos já salvos; outcome = ver sinais ou erro de carga, nunca vazio falso; direction = clone `/monitor` + delta de estados/causa, sem redesign da board; `DESIGN.md` permanece autoridade visual.

Briefing = issue grelhado #975 (Problema, História, Entra, Não entra). Q2=A gravada; cobertura 11/18 é *como*, não Q. Não reabrir.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. Irmão `erro.html` — mesmo clone + delta do erro de carga (copy actual). Sem extra `/favorites` (copy de Favoritos não muda; #970 já na base). `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Primeira visita a `/monitor` com favoritos crypto visíveis: o quadro já mostra sinais **ou** o erro de carga actual. Sem segundo clique só para sair do vazio.
- Recarregar na mesma sessão com os mesmos favoritos não prende o quadro num vazio falso.
- «Nenhum ativo disponível no monitor» só quando esta sessão não tem par crypto nos Favoritos.
- Análise que devolve `[]` / timeout / cache vazio **havendo favoritos crypto** → erro de carga (copy actual) + Tentar de novo; permanece em `/monitor`.
- Subset analisável (incidente: 11 de 18) aparece no quadro. Os skips não ganham UI nova.
- Filtro que esconde todos os sinais já carregados → «Não há resultado com estes filtros.»; não usa catálogo vazio.
- Abrir gráfico / análise continua a ter velas e trades.

**Non-Goals:**

- Redesign da board (Status, Preço, Distância, 7d, Tags, Operar, Par / Estratégia, KPIs, fluxo).
- Mudar o filtro default Na carteira vs Todos.
- Alterar o texto do erro de carga do Monitor.
- Reabrir ou alterar a lista magra de Favoritos (#970). Extra `/favorites` no proto.
- Exigir 18/18 no quadro ou superfície «7 de fora».
- Conta sem favoritos crypto: o vazio verdadeiro continua vazio.
- Ressuscitar `MonitorDashboardTab`.

## Decisions

1. **Primeira visita computa ou falha — nunca 200 vazio com favoritos (Q2=A).**
   `GET /api/opportunities/?tier=1,2,3` sem `refresh` do operador **não** devolve catálogo vazio cacheado quando o utilizador tem favoritos crypto. Cache miss, cache `[]`, ou stale `[]` → recomputar (ou erro visível). Alternativa «o operador clica Atualizar» rejeitada: é o incidente. Alternativa «frontend manda sempre `refresh=true` e o cache continua a servir `[]`» rejeitada: recarregar a tela voltaria a pedir sem refresh e ficaria preso.

2. **200 `[]` com favoritos crypto é erro de carga, não catálogo vazio.**
   O ramo vivo `length===0 && !loading` só pode pintar «Nenhum ativo disponível no monitor» quando **não** há par crypto nos Favoritos desta sessão. Havendo favoritos, `[]` (sucesso vazio, timeout que devolve lista vazia, corpo vazio) usa a copy actual de erro + Tentar de novo. Alternativa «mudar o wording» rejeitada: o operador confirmou a copy. Alternativa «manter MAY do #970 (sucesso vazio = catálogo vazio)» rejeitada: é o furo.

3. **Cobertura 11/18 é *como*, não Q de produto.**
   Quando a análise devolve um subset (skips por delist, velas em falta, timeout pontual, config), o quadro **mostra as linhas analisadas**. Este pacote **não** exige 18/18, **não** inventa aceite da antiga Q1=A, **não** cria estado «7 de fora». Se **todas** as favoritas crypto forem skipped e o payload ficar `[]`, isso cai na decisão 2 (erro de carga), não no catálogo vazio. Alternativa «esconder o quadro até 18/18» rejeitada: o incidente com refresh já tinha 11 sinais úteis.

4. **Filtro ≠ catálogo vazio.**
   Análise chegou (`opportunities.length > 0`) e um filtro (Na carteira / busca / estrela / estratégia / tempo) esconde todos → «Não há resultado com estes filtros.» O default Na carteira vs Todos **não muda**. A copy incumbente «Nenhum ativo encontrado na lista de carteira.» passa a esta frase de Entra (mesmo ramo; não é redesign). Alternativa «manter duas copies de filtro» rejeitada: Entra pede uma.

5. **Vocabulário (nasce aqui, não no issue).**
   - **Vazio falso:** quadro pinta catálogo vazio com favoritos crypto na sessão.
   - **Primeira carga:** `GET /api/opportunities/` da visita, sem `refresh=true` do operador.
   - **Recomputação forçada:** `refresh=true` (botão Atualizar / Tentar de novo).
   - **Subset analisável:** linhas que o analyzer devolveu; skips ficam fora do quadro.
   - **Catálogo vazio real:** sessão sem par crypto nos Favoritos.

## Risks / Trade-offs

- [Risco] Cache stale de `[]` (600s) prende o Monitor após um cold timeout → Mitigação: não servir nem gravar `[]` como sucesso de catálogo quando há favoritos crypto; miss/`[]` força compute ou erro.
- [Risco] Timeout 8s no cold fetch devolve `[]` e o frontend ainda trata como vazio → Mitigação: decisão 2 no frontend **e** no backend; Tentar de novo recomputa.
- [Risco] Apply manda sempre `refresh=true` e o cache deixa de servir Favoritos «Ver resultados» → Mitigação: Favoritos continua `refresh=false` no #970; este card só deixa de tratar `[]`+favoritos como catálogo. P3: Preserve o cache **não-vazio** para signal_history.
- [Risco] Apply redesenha a board ou muda o default Na carteira → Mitigação: proto clone + contrato visível; default intacto.
- [Risco] Extra `/favorites` nasce por analogia com #970 → Mitigação: proibido; copy de Favoritos não muda.
- [Risco] Curated fallback de utilizador **sem** favoritos é confundido com vazio falso → Mitigação: catálogo vazio real só sem par crypto nos Favoritos; common user sem favoritos continua o fallback existente (fora deste card).

## Migration Plan

Sem migração de schema e sem backfill. Rollback = reverter o ramo de estados no `MonitorStatusTab` e a recusa de cache `[]` com favoritos em `opportunity_routes`. Favoritos gravados não se apagam.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-975-monitor-vazio-favoritos/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/monitor` feliz (`index.html`): sessão com favoritos crypto; primeira pintura já tem linhas na `table.signals` (subset analisável, ex. SOL/USDT e ETH/USDT); landmarks Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia; **ausente** «Nenhum ativo disponível no monitor».
- `/monitor` erro (`erro.html`): «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + Tentar de novo; chrome Monitor; **ausente** «Nenhum ativo disponível no monitor»; **ausente** login.
- Filtro que esconde todos os sinais já carregados: «Não há resultado com estes filtros.»; **ausente** catálogo vazio. Default Na carteira vs Todos **não** muda.
- Análise/gráfico de um sinal continua a ter velas e trades (Apply, não o proto estático).
- `/favorites` sem regressão do #970; sem extra no proto.

**Bug vivo (contrato no Design; correção no Apply, não neste filho):**

- `MonitorStatusTab`: 200 `[]` cai em «Nenhum ativo disponível no monitor» mesmo com favoritos.
- `GET /api/opportunities/` com `refresh=false` serve cache stale/`[]` sem recomputar.
- `_calculate_opportunities` no cold timeout 8s pode skip-all e gravar `[]`.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Frontend consulta `GET /favorites/` vs o próprio endpoint de opportunities devolve flag `analysis_failed` / 503 — desde que o operador veja sinais ou o erro actual.
- Não cachear `[]` vs invalidar chave vs TTL 0 para payload vazio com favoritos.
- Primeira `fetchOpportunities` com ou sem `refresh=true`, desde que a primeira visita não dependa de um segundo clique.
- `OPPORTUNITIES_MARKET_FETCH_TIMEOUT_SECONDS` (8s) — subir, esperar, ou falhar visível: P3, desde que skip-all com favoritos não pinte catálogo vazio.
- Preservar cache **não-vazio** para Favoritos `refresh=false` / signal_history.
- Copy incumbente «Nenhum ativo encontrado na lista de carteira.» → Entra «Não há resultado com estes filtros.» no mesmo ramo.
- `MonitorDashboardTab` morto: não ressuscitar.
- Testids `monitor-load-error` (já existe) / filtro vazio.
- Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone, não redesenhar.
- Alvos 44px no «Tentar de novo» (já no vivo).

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos/` → `frontend/public/prototypes/card-975-monitor-vazio-favoritos/index.html`. Clone da página viva `/monitor` + delta do caminho feliz (quadro com sinais). Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. `COPIED:start`/`COPIED:end` no clone.
- Irmão erro: `https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos/erro.html` — mesmo clone + delta erro de carga (copy actual). Sem extra `/favorites`.
- `cp`/clone = copied; delta dos estados = generated.
- Sem painel ANTES/DEPOIS como URL canónica.
- Digest, desktop/mobile e bytes copied vs generated: ver `## Prototype Validation`.

## Prototype Validation

- **Comando (autor, local):** Python HTTP `127.0.0.1:51429` sobre `frontend/public` + Playwright Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`), `colorScheme: dark`. Evidência: `.impeccable/critique/975-autor-gate.json`. Pai após A/B: HTTPS DEV == disco IDENTICAL (`criptofarol-dev-prototypes.service` restart); Assessment A/B PASS.
- **URLs:** canónico `https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos/` (`index.html`); irmão `…/erro.html`. Sem extra `/favorites`.
- **Viewports:** desktop 1280×800 + mobile 390×844. Screenshots: `975-index-desktop-1280x800.png`, `975-index-mobile-390x844.png`, `975-erro-desktop-1280x800.png`, `975-erro-mobile-390x844.png`.
- **Ações / asserts (index, os dois viewports):** `table.signals` presente; SOL/USDT e ETH/USDT visíveis (desktop = tabela; mobile = cards incumbentes, tabela `display:none` como o vivo); **ausente** «Nenhum ativo disponível no monitor». Landmarks Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia no thead (uppercase incumbente).
- **Ações / asserts (erro):** «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + «Tentar de novo»; chrome Monitor; ausente catálogo vazio; URL continua no proto (não login).
- **Console:** 0 pageerror / 0 console.error nos dois viewports.
- **Resultado do autor:** visual PASS · FAIL 0 de contrato visível. Assessment A/B: PASS. Clip das acções da linha (Ver Trades / Operar) a 1280 é incumbente da board — P3, não redesenhar.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116` · 31012 B = 21481 copied + 9531 generated. Pares `COPIED:start`/`COPIED:end`: 7/7; soma UTF-8 copiada 21481 (> 0). T5 mede só este index.html.
  - `erro.html` `fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34` · 24112 B = 20678 copied + 3434 generated.

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #975 (Q2=A). Cobertura 11/18 fechada como *como* nas decisões 3.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Dupla PASS; P0/P1 nenhum; sem rework. P3 aceitos (Apply, não reabrir).

**P0:** nenhum  
**P1:** nenhum  
**P3 (aceitos):** thead vazio no `erro.html` (vivo é XOR erro/tabela); clip Operar/Ver Trades a 1280/1440 e busca/thead a 390; mobilebar «SOL/USDT» no erro; `lang` ausente no erro; filtro vazio sem irmão HTML; `DELTA:start=0`; button estático vs `refetch`; cache/flag já neste `design.md`; `MonitorDashboardTab` morto.

**Disposition:** P3 → Apply. Não reabrir Q2=A, copy de erro, #970 nem 18/18.

**Snapshots:** `.impeccable/critique/975-card-975-monitor-vazio-favoritos-assessment-A.md` · `.impeccable/critique/975-card-975-monitor-vazio-favoritos-assessment-B.md`

**Design Agent verdict:** PASS

- Autor: [design-autor 975](fb7f567e-02a0-4257-8df2-8949eaf507f5) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 975](3da49ae6-7472-4c6d-99a9-d161ac595799) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Assessment B: [Assessment B 975](07f2fd97-d04e-4833-9edc-e3e8797c0011) isolado; `model: cursor-grok-4.6-high`. **PASS**. digest_match yes; detector [].

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
