## Context

A página Carteira (`frontend/src/pages/ExternalBalancesPage.tsx`) mostra a tabela de saldos Binance com fundo uniforme (`bg-[#101c2a]`) em todas as linhas, o que dificulta acompanhar cada ativo horizontalmente. O card #413 pede linhas intercaladas (zebra) e a remoção dos textos descritivos redundantes: o subtítulo do header ("Saldos lidos da Binance Spot por chave API read-only..."), a nota técnica sob o título Balances ("Layout responsivo: tabela no desktop e cards no mobile.") e o chip "Binance · read-only".

O projeto segue o `DESIGN.md` (tokens: `surface-card-dark` #1e2329, hairline-on-dark #2b3139, hover via branco translúcido) e o shell dark do app (canvas #07111a).

## Goals / Non-Goals

**Goals:**
- Zebra sutil na tabela desktop que torne cada linha identificável sem gritar.
- Preservar hover, cores semânticas (PnL verde/vermelho), barra de participação e header.
- Remover os três textos/indicadores redundantes: subtítulo do header, nota técnica sob Balances e chip "Binance · read-only".

**Non-Goals:**
- Sem zebra nos cards mobile (mantidos como estão).
- Sem mudança de dados, API, backend, ordenação ou densidade.
- Sem redesenho de layout, cores ou tipografia fora do delta.

## Decisions

- **Zebra com `even:bg-white/[0.03]`** (ou equivalente sutil de baixa opacidade sobre `#101c2a`): tom baixo o suficiente para não competir com textos `text-slate-400/500`, mas perceptível para guiar a leitura. Alternativa avaliada: `bg-white/[0.05]` — descartada por reduzir contraste dos textos secundários.
- **Hover sobrepõe a zebra**: manter `hover:bg-white/[0.03]` → no hover a linha fica clara independente da paridade; o zebra usa `even:` para não conflitar.
- **Mobile intacto**: cards já separados por borda; zebra não se aplica.
- **Remoção de texto com reuso de espaço**: o header mantém apenas título "Carteira", breadcrumb e linha "Última sincronização"; o subtítulo, o chip "Binance · read-only" e a nota técnica sob Balances são eliminados sem substituição (decisão de Alan de simplificar o status visual).

## Risks / Trade-offs

- [Zebra visível demais] → Mitigação: usar opacidade baixa (0.03) e validar visualmente contra `DESIGN.md` no browser (desktop/mobile).
- [Baseline do Playwright visual quebra] → Mitigação: atualizar snapshots da tela Carteira junto com a mudança e revisar o `diff.png` via subagent vision.
- [Indicador "Binance · read-only" sair da página junto com o subtítulo] → Mitigação: remoção explícita pedida por Alan; a informação de origem read-only permanece disponível no perfil/credenciais Binance (não regressa o contrato de segurança, apenas a superfície).

## Open Questions

Nenhuma. Decisões de escopo registradas no card #413 (Review PO).

## Prototype

- **URL HTTP navegável:** `https://dev.criptofarol.com.br/prototypes/wallet-easier-reading/`
- **Caminho versionado:** `frontend/public/prototypes/wallet-easier-reading/index.html` (também publicado em `dist/prototypes/wallet-easier-reading/index.html` no frontend DEV)
- **Versão:** v2 (após targeted fixes de PnL e zebra explícita), validada em 2026-08-08
- **Base do sistema atual:** tela real `/external/balances` (`frontend/src/pages/ExternalBalancesPage.tsx`) — shell dark (#07111a), header com breadcrumb + título, 4 KPIs, filtros e tabela com 8 colunas clonados; delta: zebra nas linhas + remoção do subtítulo, da nota técnica e do chip "Binance · read-only"
- **Escopo desktop/mobile:** tabela desktop com zebra; mobile usa cards sem zebra (inalterados)
- **Fluxos/estados representados:** estado padrão com 2 linhas (BTC/ETH), hover, PnL up/down; loading não representado (delta estático)

## Impeccable Brief

- **Problema:** leitura horizontal da tabela de saldos dificultada pelo fundo uniforme; textos descritivos redundantes poluem o header, o título da seção e o status visual.
- **Usuário:** investidor beta autenticado que consulta a carteira Binance read-only.
- **Resultado esperado:** cada linha identificável de forma rápida (zebra sutil), com PnL verde/vermelho, barra de participação e hover preservados; sem textos redundantes e sem chip de status.
- **Direção:** clone da UI atual com delta mínimo; zebra `#16243a` sobre painel `#101c2a` (Δ 1.10:1, perceptível sem competir com textos).
- **Escopo:** `ExternalBalancesPage.tsx` apenas; mobile cards inalterados; sem mudança de API/dados.
- **Estados/interação:** estado padrão, hover sobrepõe zebra, ordenação/filtros existentes não mudam.
- **Restrições:** `DESIGN.md` como autoridade visual; cores semânticas trading up `#0ecb81`/down `#f6465d` (protótipo usa `--up #6ee7b7`/`--down #fda4af` conforme app real em TSX).

## Impeccable Critique

### Assessment A (produto/UX/a11y/responsividade) — critic read-only, mesmo LLM/modelo da sessão principal

Achados (navegador real, computed styles, contraste WCAG, hover, foco, DOM, console):
- P1 → **CORRIGIDO**: cores semânticas de PnL (up/down) ausentes na tabela desktop do protótipo; aplicado `.pnl .usd.up/.down` e `.pnl .pct.up/.down` com `var(--up)`/`var(--down)`. Revalidação: BTC `rgb(110,231,183)`, ETH `rgb(253,164,175)` — PASS.
- P2 → **ACEITO (observação)**: zebra no limite inferior de utilidade (1.10:1) — aceito por ser sutil e não competir com textos (objetivo do card).
- P2 → **ACEITO (pré-existente)**: contraste do texto faint `#64748b` (12px) sobre zebra = 3.27:1 (falha AA 4.5) — padrão já existente no app (~3.6 no painel); zebra degrada ~0.3pt; fora do escopo do card.
- P2 → **ACEITO**: buttons de ordenação do thead não representados no protótipo estático (affordance existe na tela real e não muda com o card).
- Fidelidade de shell/header/chips/KPIs/filtros: OK. Skip link, `th scope="col"`, thead sticky: OK.

**Veredito Assessment A: PASS** (revalidação após targeted fix; zero P0/P1 aberto).

### Assessment B (detector técnico + navegador) — critic read-only, mesmo LLM/modelo da sessão principal

Asserts (Playwright real, 1440x900 e 390x844, console capturado):
| Assert | Resultado |
|---|---|
| Zebra: linhas pares/ímpares com background computado diferente | PASS (`#101c2a` vs `#16243a`) |
| Hover real sobrescreve zebra nas duas paridades | PASS |
| Subtítulo header removido | PASS |
| Nota "Layout responsivo..." removida | PASS |
| Chip "Binance · read-only" removido (ausente do DOM e da tela) | PASS |
| Console zero erros (0 error, 0 pageerror) | PASS |
| Mobile 390px: tabela `display:none`, cards visíveis, sem overflow | PASS |
| Sintaxe HTML (tags, aria, th scope, skip link) | PASS |

Achados:
- P2 → **CORRIGIDO**: zebra ímpar sem cor explícita (herdava `.panel`) — aplicado `nth-child(odd){ background: var(--row) }`.
- P2 → **ACEITO**: linha "total_usd do servidor disponível" mantida (não é um dos 2 textos do escopo); `.note` final é anotação do protótipo, não vai para produção.
- P2 → **ACEITO**: hover 4% branco é feedback sutil; contraste preservado em ambas as zebras (sem regressão vs produção).

**Veredito Assessment B: PASS** (zero P0/P1).

## Impeccable Audit

- **Acessibilidade:** skip link funcional; 8 `th scope="col"`; thead sticky; outline 2px sky no foco; chip removido não deixa elementos órfãos (header continua com breadcrumb, título e linha de sincronização). Texto strong `#f1f5f9` 14.2:1 e muted `#94a3b8` 6.1:1 sobre zebra — OK. Achado faint 3.27:1 pré-existente classificado (fora do escopo).
- **Performance:** delta estático sem JS, sem requests; zero custo adicional.
- **Responsividade:** breakpoint 767/768 consistente com `md:` da tela real; mobile sem overflow horizontal.
- **Theming:** tokens dark do app respeitados; cores semânticas up/down aplicadas nas linhas.
- **Integridade de implementação:** implementação alvo = mesma estrutura TSX clonada (linhas `tr`, `even:`/`hover:`), delta mapeado 1:1 para `ExternalBalancesPage.tsx`.

## Impeccable Trace

- **Pipeline:** context.mjs (target `ExternalBalancesPage.tsx`, PRODUCT.md conservado, DESIGN.md intacto) → shape (Impeccable Brief acima) → prototype v1 → critique A/B (critics read-only separados, mesmo LLM/modelo/versão da sessão principal, contexts independentes) → audit → targeted fixes (1 rodada: PnL up/down na tabela + zebra explícita odd) → polish (nenhum achado extra) → **escopo ampliado por Alan: remoção do chip "Binance · read-only"** → protótipo v3 (chip removido) → revalidação em navegador real (browser gate) → veredito final.
- **Comandos de validação:** `npx playwright test --config=frontend/pw-prototype.config.ts` (2 specs, desktop 1440x900 + mobile 390x844, 2 passed) e script `gate-final.cjs` contra a URL pública `https://dev.criptofarol.com.br/prototypes/wallet-easier-reading/` (desktop + mobile, computed styles e console) — verdes nas versões v2 e v3 servidas.
- **Digest da versão validada:** `index.html` v3 (zebra odd/even explícita + PnL up/down + chip "Binance · read-only" removido) servido em `dist/prototypes/wallet-easier-reading/` do frontend DEV; revalidado após rebuild e após a publicação no dist (nenhuma alteração posterior ao gate).
- **Prova de igualdade de modelo:** Assessment A e B executados como subagents `general` herdando o LLM/modelo e a versão exatos da sessão principal (opencode-go/deepseek-v4-flash); sem fallback, sem troca de modelo; contexts isolados e read-only (nenhuma edição por critics). Exceção de visão não usada nesta etapa (julgamento por computed styles/contraste, não pixels).
- **Findings do detector:** nenhum achado do hook/plugin durante as edições do protótipo.
- **Vínculo com Prototype Validation:** versão validada = versão servida (URL pública), digest e asserts registrados abaixo.

## Prototype Validation

- **URL servida:** `https://dev.criptofarol.com.br/prototypes/wallet-easier-reading/` (200 OK; preview 5175 → dist DEV).
- **Viewports:** desktop 1440x900 e mobile 390x844 (Playwright real, headless).
- **Ações/asserts:**
  - Desktop: tabela visível; zebra com backgrounds distintos por linha (`rgb(16,28,42)` vs `rgb(22,36,58)`); PnL BTC verde `rgb(110,231,183)` e ETH vermelho `rgb(253,164,175)`; subtítulo, nota técnica e chip "Binance · read-only" ausentes do body; hover sobrepõe zebra (2 specs Playwright + script gate-final) — PASS.
  - Mobile: tabela `display:none`, cards visíveis, sem zebra nos cards, sem overflow; subtítulo, nota e chip ausentes — PASS.
  - Console/page errors: NONE em ambos viewports.
- **Resultado:** verde na v3 (após remoção do chip, revalidada em navegador real). Nenhuma alteração após esta validação (versão servida = versão local v3).

## Design Critique

- **Achados por dimensão:** produto (zebra resolve leitura; remoção conforme card) — sem achados; UX — P2 zebra sutil aceito; a11y — P2 faint pré-existente aceito (fora do escopo); responsividade — conforme escopo (cards mobile intactos); estados — hover OK, loading não representado (delta estático); fidelidade — shell/header/KPIs/filtros conferem com a tela real; delta óbvio e contido.
- **Correções realizadas:** PnL up/down na tabela desktop (P1 Assessment A); zebra odd explícita (P2 Assessment B); chip "Binance · read-only" removido (escopo ampliado por Alan, revalidado em v3).
- **Riscos/pendências não bloqueantes:** baseline Playwright visual da tela Carteira será atualizada na implementação (esperado); nota `.note` do protótipo não vai para produção.
- **Referências avaliadas:** protótipo v3 (URL pública acima), `design.md` v2, specs `external-balances` delta, tela real `ExternalBalancesPage.tsx`.
- **`Design Agent verdict: PASS`** — zero P0/P1 aberto, browser gate e asserts críticos verdes, sem erros de console, evidência de igualdade de modelo dos critics registrada.
