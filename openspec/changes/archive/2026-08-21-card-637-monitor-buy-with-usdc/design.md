## Context

Card [#637](https://github.com/oalansilva/crypto/issues/637). Change `card-637-monitor-buy-with-usdc`.  
**UI impact: affected** — modal Operar (compra Spot) no Monitor.  
Estratégia/sinal permanece `BASE/USDT`; só a origem do pagamento da compra pode ser USDT ou USDC.

### Decisões de produto (fechadas neste Design)

| Tema | Decisão |
| --- | --- |
| Sem par `BASEUSDC` | Bloquear com motivo acionável; sem conversão via USDT |
| Venda 100% | Permanece no par da estratégia (`BASEUSDT`); sem seletor de quote |
| Origens v1 | Somente USDT e USDC |
| Default | USDT se par negociável; senão USDC se válido; preferência de sessão quando válida |

## Goals / Non-Goals

**Goals**

- Permitir comprar o base da oportunidade pagando com USDC (ou USDT) sem mudar estratégia/gráfico.
- Tornar explícito quando o par da ordem ≠ par da estratégia.
- Fail-closed: sem par, sem saldo Spot livre da origem, notional inválido → bloqueio claro.

**Non-Goals**

- Conversão stable→stable sem comprar o ativo.
- Trocar o destino (outro base).
- Origens além de USDT/USDC; BUSD/FDUSD/EUR; quote na venda.
- Mudar Discovery/Favoritos/Combo/candles para catálogo USDC.
- Ordens limit/stop.

## Decisions

1. **Controle "Pagar com"** só no tab Comprar: segmento USDT | USDC (radiogroup). Inerte/oculto na venda (junto com saldo quote).
2. **Título do modal** continua `Operar BASE/USDT` (par da estratégia). Preço indicativo reflete USDC + símbolo da ordem quando a origem ≠ USDT.
3. **Saldo** = Spot `free` da origem selecionada; label `Saldo livre em {origem}`.
4. **Preview/submit API** passam origem + amount; backend resolve símbolo `BASE`+origem e valida filtros Binance.
5. **Confirmação** lista: Estratégia `BASE/USDT` · Ordem `BASEUSDC` · Gastar X USDC · Saldo livre origem · ≈ Y BASE · aviso MARKET · heading “Confirme sua ordem”.
6. **Preferência de sessão** (`sessionStorage`) para última origem válida; restaurada na abertura quando ainda válida.
7. **Elegibilidade Monitor** permanece “estratégia termina em USDT”; não exigir `BASEUSDC` para mostrar Operar.

## Risks / Trade-offs

- Par `BASEUSDC` pode não existir ou ter liquidez/filtros diferentes de `BASEUSDT` → UX de bloqueio deve citar o símbolo faltante.
- Usuário pode achar que mudou a estratégia → copy e confirmação separam os dois conceitos.
- Preferência de sessão com origem agora inválida → cair no default seguro.

## Migration Plan

N/A de dados. Feature flag não exigida: comportamento default permanece USDT.

## Open Questions

Nenhuma bloqueante para Aprovação de Design. Escopo de venda com escolha de quote fica para card futuro se Alan pedir.

## UI impact

`affected` — modal Operar (`SpotMarketTradePanel`) no Monitor.

## Impeccable Brief

- **Problema:** compra Spot no Monitor só aceita USDT; quem tem USDC Spot livre não consegue comprar o base da oportunidade `BASE/USDT`.
- **Usuário:** operador autenticado no Monitor com Binance Spot Trade.
- **Resultado:** escolher Pagar com USDT|USDC, ver saldo da origem, confirmar ordem no par `BASE`+origem sem mudar o sinal.
- **Direção:** delta mínimo sobre o painel claro atual (protótipos #463/#385 + `SpotMarketTradePanel`): radiogroup + labels + confirmação enriquecida; tokens Binance/`DESIGN.md`.
- **Escopo:** entry + review + estados (par indisponível, saldo insuficiente, loading saldo); venda sem seletor/saldo quote.
- **Estados:** default USDT; origem USDC com par ok; USDC sem par; saldo insuficiente USDC; loading; review com pares distintos; sell sem Pagar com.
- **Interação:** troca de origem atualiza saldo/sufixo; Continuar → review com foco no heading; Cancelar/Fechar/Escape sem ordem; Tab trap; setas no radiogroup e tabs.
- **Restrições:** fidelidade ao shell Monitor (sidebar 224px, painel claro); sem conversão oculta.

## Prototype

- **URL canônica (após sync DEV):** `https://dev.criptofarol.com.br/prototypes/card-637-monitor-buy-with-usdc/`
- **Validação desta sessão:** `http://127.0.0.1:8765/` (http.server no worktree; sync para `source`/preview bloqueado — `source` em `docs-release-2026-08-21`, unbound)
- **Path:** `frontend/public/prototypes/card-637-monitor-buy-with-usdc/index.html`
- **Espelho:** `openspec/changes/card-637-monitor-buy-with-usdc/prototype/` (não vai ao Gist)
- **Digest sha256:** `e9aa4feda0a51c2997877172c901a32992cf98108de96950587b52a0ef976588`
- **Base:** shell Monitor + modal Operar (#385/#463 + painel real); delta = Pagar com + review estratégia vs ordem + a11y paridade.
- **Viewports:** desktop 1440×900 + mobile 390×844.
- **Fluxos:** Pagar com USDC; review `BTCUSDC`; bloqueio sem par; venda sem saldo quote/Pagar com; loading.

## Prototype Validation

| Item | Resultado |
| --- | --- |
| Ferramenta | Playwright (`playwright-core` + Chromium 1234), headless |
| URL | `http://127.0.0.1:8765/` |
| Desktop | dialog open; título `Operar BTC/USDT`; USDC → saldo `800,00 USDC`; review heading + strategy `BTC/USDT` + order `BTCUSDC` + spend `250,00 USDC` |
| Sem par | erro acionável; Continuar disabled |
| Venda | `pay-with` e `quote-balance-strip` hidden |
| Loading | `carregando…` |
| Mobile | pay-with visível; review `BTCUSDC` |
| Console | sem erros |
| Screenshots | `/tmp/card-637-desktop.png`, `/tmp/card-637-mobile.png` |

## Impeccable Critique

### Assessment A (Task isolada, inherit)

- Veredito local: **PASS**
- Achados: P2 (heading/taxas review, session pref no open antigo, copy sem par, sell=alert, a11y radio/trap, loading) → corrigir no polish; nits aceitos; detector flat-type-hierarchy aceito.

### Assessment B (Task isolada, inherit)

- Veredito local inicial: **BLOCKED** (P1: saldo quote na venda; teclado/foco do modal)
- Pós-polish: P1 corrigidos — saldo/Pagar com só no buy-form; Tab trap; setas radiogroup/tabs; heading “Confirme sua ordem” com foco; copy sem par ajustada; loading scenario; preferência restaurada no open.

### Síntese

Zero P0/P1 abertos após polish. P2 aceitos para apply (taxas na review, stub de review de venda como fora do delta visual).

## Impeccable Audit

- **A11y:** radiogroup + setas; Tab trap; Escape; `aria-modal`/`inert`; focus no review heading; `aria-live` em erro/saldo.
- **Performance:** HTML estático; N/A.
- **Responsividade:** drawer mobile; asserts mobile verdes.
- **Theming:** tokens Binance do painel claro atual.
- **Detector:** `flat-type-hierarchy` warning — aceito (paridade com modal #463).
- **Integridade:** digest pós-polish registrado; mirror OpenSpec atualizado.

## Impeccable Trace

- Context: `node .agents/skills/impeccable/scripts/context.mjs --target "Monitor Operar compra Spot Pagar com USDT|USDC"`
- Detect: `node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-637-monitor-buy-with-usdc/index.html` → 1 warning aceito
- Critic A model: inherit (Task `58e78737-6ecd-440e-8dcd-3628c71ec950`)
- Critic B model: inherit (Task `45a2dd70-18fd-411f-bc64-a916286f0e02`)
- Orquestrador: mesma sessão Composer / inherit
- Digest final: `e9aa4feda0a51c2997877172c901a32992cf98108de96950587b52a0ef976588`
- Browser gate: reexecutado após polish — PASS

## Design Critique

- Dimensões cobertas: fidelidade, produto, UX, a11y, responsividade, estados.
- Correções aplicadas no protótipo (P1 B + P2 relevantes A).
- Pendências não bloqueantes: review de venda completo (fora do delta); linha Taxas no review (apply); URL DEV pública depende de sync do `source`/preview (hoje em `docs-release-2026-08-21`).
- Evidência: Prototype Validation + Trace acima.
- **Design Agent verdict: PASS**

## Apply — UI × protótipo (gate)

- Protótipo: `frontend/public/prototypes/card-637-monitor-buy-with-usdc/index.html`
- Implementação: `frontend/src/components/monitor/SpotMarketTradePanel.tsx` + estilos em `frontend/src/index.css`
- Elementos seguidos: radiogroup **Pagar com** (USDT|USDC) só na compra; saldo/input/labels por origem; preferência de sessão; review com **Estratégia / sinal** vs **Par da ordem**; venda sem seletor; elegibilidade Operar inalterada (estratégia USDT).
- Desvios: nenhum injustificado. Linha Taxas “Definidas na execução” mantida (P2 aceito no design).
- Resultado da comparação pós-apply: **PASS** (layout/controles/estados alinhados ao protótipo aprovado).
