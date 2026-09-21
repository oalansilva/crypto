# Snapshot Impeccable — card-1001 (design-autor)

Method: autor-only (dupla A/B no pai; este filho MUST NOT spawn Assessment A/B). Detector CLI + Playwright browser gate neste contexto.

Target: `frontend/public/prototypes/card-1001-scalp-direcional-jev/index.html`
Mode: Operate
`DESIGN.md`: autoridade visual, não sobrescrito.

UI impact: affected
live_route: /monitor
surface: existing

## Brief (shape)

- audience: utilizador autenticado no Monitor, com ou sem chave Spot
- outcome: ligar/desligar o scalp na própria conta Binance; ler calibração, P&L e kill
- direction: clone `/monitor` + faixa persistente acima dos KPIs
- scope: interruptor + painel + copy 24/7 em landing/Ajuda; board e Operar intactos

## Detector

`node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-1001-scalp-direcional-jev/index.html` → `[]` exit 0.

## Browser gate

Playwright Chromium headless, `http://127.0.0.1:8877/prototypes/card-1001-scalp-direcional-jev/`.

| Viewport | Default | Ligado | Kill |
| --- | --- | --- | --- |
| 1280×800 | `1001-autor-desktop-1280x800-off.png` | `…-on.png` | `…-kill.png` |
| 390×844 | `1001-autor-mobile-390x844-off.png` | `…-on.png` | `…-kill.png` |

130 asserts PASS. 0 page errors. Landmarks `/monitor` presentes. Sem «estratégia lucrativa» / «formador de mercado». P&L negativo visível no estado ligado e kill.

Gate JSON: `1001-autor-gate.json`.

## Heuristics (autor, não substitui A/B)

| # | Heuristic | Score | Note |
|---|-----------|-------|------|
| 1 | Visibility of System Status | 3 | Switch + status + kill banner; proto fixtures for no-key/kill |
| 2 | Match System / Real World | 3 | Vocabulário do issue (T, clip, post-only, kill) |
| 3 | User Control and Freedom | 4 | Desligar é o mesmo interruptor; religar após kill é explícito |
| 4 | Consistency and Standards | 3 | Clone do shell/board; faixa no mesmo tema |
| 5 | Error Prevention | 3 | Sem Spot → switch disabled; default off |
| 6 | Recognition Rather Than Recall | 3 | Calibração e P&L no sítio; Operar continua visível |
| 7 | Flexibility and Efficiency | 3 | Um switch; sem modal extra |
| 8 | Aesthetic and Minimalist Design | 3 | Faixa densa Operate; proto buttons secundários |
| 9 | Error Recovery | 3 | Kill explica que não religa sozinho |
| 10 | Help and Documentation | 3 | Nota da chave Spot; extras landing/ajuda |
| **Total** | | **31/40** | Good |

## Priority issues (autor)

Nenhum P0/P1 de produto neste snapshot. P3 já aceitos no `design.md` (clip Operar incumbente, overlay vs faixa, formato da calibração).

- **[P3] Proto fixtures** «Simular kill» / «Ver sem chave Spot» não vão ao produto. Apply não os pinta.
- **[P3] Clip da coluna Operar a 1280** — incumbente da board.
- **[P3] Search mobile corta o placeholder** — incumbente do clone.

## Clone gate

`design_clone_gate.classify` = PASS. Pares COPIED 10/10. copied UTF-8 21077. Landmarks `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia.

## Verdict

Design Agent verdict: **pendente** (dupla A/B no pai). Autor: clone + delta aplicável; browser_gate PASS.

Design fecha em 1+1+1: este artefacto é o autor. Sem `## Design Critique` aqui.
