# Design: Monitor — remover alvo derivado (card #803)

UI impact: affected
live_route: /monitor
surface: existing

## Context

Card [#803](https://github.com/oalansilva/crypto/issues/803), Status=Design. HOLD no Monitor mostra **alvo** calculado no frontend (`last_price * (1 ± dist/100)` em `OpportunityCard.tsx` e de novo em `ChartModal.tsx`). Não é take-profit nem ordem. Compete com stop e distâncias. O #792 pediu risco explícito; a spec canónica `opportunity-monitor` ainda manda `alvo`. Este card remove o campo nas duas superfícies e atualiza a spec para o Apply não o reintroduzir.

Anti-referência: proto #792 (ainda tem alvo). Base do clone = aquele HTML (já é clone de `/monitor`), com delta só no kv HOLD e no painel de risco do modal.

## Goals / Non-Goals

**Goals:** HOLD sem rótulo/valor `alvo` no card e no modal; ordem `distância até saída` → `distância até stop` → `stop` → `entrada` → `preço atual`; manter `indisponível — dado não confiável`, frase de cenário e EXIT residual; apagar cálculo `alvoPrice`/`chartAlvoPrice` (sem linha escondida nem número equivalente).

**Non-Goals:** TP/Kelly/campo `alvo` no backend; stop na Binance; Telegram; redesign da tabela/gráfico além de tirar alvo; terceiro status visível.

## Decisions

1. **D: atualizar `opportunity-monitor`.** MODIFIED no requisito HOLD (e unavailable/EXIT) para o Apply não poder reintroduzir `alvo` a partir da spec canónica.
2. **D: card e modal no mesmo recorte.** Mesma ordem, mesmo corte, sem `alvo`. ChartModal é duplicata hoje; Apply espelha a remoção.
3. **D: clone da topologia viva via base #792 + delta.** Não galeria de cards. `table.signals` + landmarks `/monitor`. Antes = vivo/#792 com alvo; Depois = sem alvo. Toggle muda markup (`data-prototype-variant` + innerHTML do kv / `hidden` na linha do modal).
4. **Fonte de verdade do risco permanece top-level `opportunity.*`.** Só some o derivado de alvo no frontend.
5. **Stale não inventa linha de alvo.** Campos afetados ficam `indisponível — dado não confiável`; não há “alvo indisponível”.

## Audience / Outcome / Direction / Scope

- **Audience:** trader do beta no `/monitor` (e Alan em T7).
- **Outcome:** olhar HOLD e ver risco real (stop/distâncias), sem estimativa que parece TP.
- **Direction:** refinement Operate — Binance dark, clone `/monitor`, delta só no kv/modal.
- **Scope:** 4 linhas (SOL HOLD, ETH stale, ADA EXIT vazio, LINK EXIT residual) + modal de risco. Fora: Kelly, corretora, redesign.

## Apply contract

- `OpportunityCard.tsx`: remover `alvoPrice`/`alvoStr` e o par `<dt>alvo</dt><dd>…`; ordem HOLD = saída → stop% → stop → entrada → preço atual. Sem placeholder.
- `ChartModal.tsx`: remover `chartAlvoPrice` e a row `Alvo` (~790). Mesmo recorte do card.
- Spec: aplicar o delta `openspec/changes/card-803-monitor-remover-alvo/specs/opportunity-monitor/spec.md` na canónica.
- Testes: grep e ajustar e2e/unit que afirmem `alvo`/`Alvo`/`alvoPrice` (hoje só os dois componentes; re-grep no Apply). Aceite 1–5.
- Proto já feito em Design; Apply não reescreve o HTML.

Rollback: restaurar as linhas de alvo nos dois ficheiros. Sem migration.

## Risks / Trade-offs

- [Spec #792 ainda pede alvo] → delta MODIFIED neste change; senão Apply reintroduz.
- [Card vs modal divergirem] → mesmo recorte nos dois ficheiros + proto com modal.
- [e2e ainda esperarem alvo] → tarefa de grep no Apply.

## Prototype

- URL: `https://dev.criptofarol.com.br/prototypes/card-803-monitor-remover-alvo/`
- Path: `frontend/public/prototypes/card-803-monitor-remover-alvo/index.html`
- sha256: `24fc626805ebbb3561f4cc3fbf45c0572e00a520b306a24274ce9e49cf2bb92d` (103142 bytes)
- Copied vs generated UTF-8: copied 82027 / generated 21115 (`copied_utf8_sum` > 0)
- Viewports: desktop 1280×800, mobile 390×844
- Base: clone #792 da rota `/monitor` (shell AppNav, KPIs, filterbar, `table.signals`, 4 linhas). Delta: kv HOLD sem alvo; toggle Antes restaura alvo; overlay do gráfico com o mesmo recorte.
- Fluxos: SOL HOLD confiável · ETH HOLD stale · ADA EXIT vazio · LINK EXIT residual. Abrir Gráfico abre o painel de risco.
- `DESIGN.md` não reescrito.

## Prototype Validation

- URL: `https://dev.criptofarol.com.br/prototypes/card-803-monitor-remover-alvo/` (200 após restart do unit `criptofarol-dev-prototypes`; ficheiro no worktree)
- Viewports: 1280×800 e 390×844 (Playwright Chromium)
- Asserts:
  - Depois HOLD kv: sem `alvo`/`Alvo`; dts = saída → stop% → stop → entrada → preço atual — PASS
  - Antes: mesma ordem com `alvo` no markup; `data-prototype-variant` after/before/after — PASS
  - ETH stale: `indisponível — dado não confiável`, sem linha alvo — PASS
  - EXIT: preço atual + Risco residual, sem alvo — PASS
  - Modal SOL: Depois linha Alvo `hidden`/não visível; Antes visível — PASS
  - Landmarks HTML `/monitor` + `table.signals` visível a 1280 — PASS
  - Console do proto: 0 erros que quebrem o fluxo — PASS
  - Login live `/monitor` (`admin@example.com`): 401, ficou em `/login` — miss, não bloqueia (clone #792 + landmarks)
- Evidência: `output/playwright/card-803-desktop-1280.png`, `card-803-desktop-table-1280.png`, `card-803-mobile-390.png`, `validate-803.json`
- Crítica A/B e a secção de crítica no design ficam com o pai.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2 (accepted-residual):** 4 linhas começam expandidas (kv abaixo da dobra); modal Depois guarda `[data-alvo-row] hidden` — Apply MUST apagar a row, não CSS-hide; overlay do gráfico é recorte de risco, não clone pixel do ChartModal; `.row-actions` herdado #792; residual LINK é fixture
- **P3 (accepted-residual):** 7d = `-`; testids duplicados; modal sem trap/Escape; `aria-label` Expandir estático; detector Inter/em-dash/dark-glow = FP do clone; live `/monitor` sem sessão = miss (não é clone)
- Prototype: `https://dev.criptofarol.com.br/prototypes/card-803-monitor-remover-alvo/` digest `24fc626805ebbb3561f4cc3fbf45c0572e00a520b306a24274ce9e49cf2bb92d`
- Snapshot A: `.impeccable/critique/803-card-803-monitor-remover-alvo-A.md`
- Snapshot B: `.impeccable/critique/803-card-803-monitor-remover-alvo-B.md`
- Design Agent verdict: PASS
