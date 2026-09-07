# Assessment B (detector + browser real) — card 852 · change card-852-descoberta-tres-modos

> Assessor B isolado, modelo `muse-spark-1.3-contributor-free`, sem transcript de A. Foco: detector + browser real.
> Sem visão (sem revisão de pixels — geometria/layout via DOM e computed style).
> Nada movido (Status, branch, worktree); nenhuma edição fora deste arquivo.

- UTC: 2026-09-06T18-19Z
- Protótipo: `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html` (branch `card-852-descoberta-tres-modos`)
- Servido: https://dev.criptofarol.com.br/prototypes/card-852-descoberta-tres-modos/ — HTTP 200, 32397 bytes
- Digest servido == local: `9b298054e8874fc80ebbde1d16b5cec3c896816f168bd8802c9b4034aae4ef13` (confirmado nesta sessão, duas pontas)
- Rota viva: https://dev.criptofarol.com.br/combo/discovery (autenticada — sem sessão; avaliada via fonte `frontend/src/pages/DiscoveryPage.tsx` + `scripts/process-fsm/route-landmarks.yaml`, sem usar /login como evidência)
- Browser: Chrome for Testing 153 (ms-playwright chromium-1243), Playwright Python 1.62, desktop 1440×900 + mobile 390×844

## 1. Detector (estático, na árvore)

- Landmarks do catálogo (`Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`): os 3 presentes no `index.html` (h1 linha 110, `aria-label="Rascunho de varredura"` 129, `aria-label="Preflight da varredura"` 165 + h2 `Preflight` 166). Fonte viva contém os 3 (`DiscoveryPage.tsx` linhas 1155, 1443, 1607/1610). → nenhum landmark ausente → sem P0.
- Jargão no caminho feliz (Montar, texto visível): sem UUID/token/hash/#PF-/dedup/lease (matches só em comentário HTML, `data-testid="start-sweep"` e texto dentro de `<details>`). Exceções registradas abaixo como P3 (`Snapshot válido` em `#pf-state`, fora do `<details>`; chip `RUNNING`).
- Links quebrados/recursos: nenhum `<img>`, nenhum fetch/XHR; único `href` externo é `data:` (favicon inline); demais `href="#"` com `preventDefault` + binding. Gate registrou 0 responses ≥400. → sem finding.
- A11y estática: `<html lang="pt-BR">`, `<title>`, tablist com `aria-selected`/`aria-controls` + setas ArrowLeft/Right, progressbar com `aria-valuemin/max/now=14/24`, `role=alert` no bloco, `aria-live` em preflight/paginação, traps de modal com Escape e ciclo Tab, `caption.sr` com regra de rank estável. Sem `<img>` sem alt (não há imagens). Sem skip-link (observação, não finding — página protótipo de painel único).
- Balanço de tags (parser próprio): EXATAMENTE 2 mismatches — `unclosed header (245) before /div (246)` + `stray /div (264)`; idem `(269)/(270)/(281)`. Nenhum outro erro estrutural. → causa raiz do achado P1 abaixo.

## 2. Browser real (matriz ação→resultado, observável)

Gate principal: 29/31 PASS desktop+mobile; extras: todos PASS; console/pageerrors/recursos: 0.

| # | Ação | Resultado |
|---|------|-----------|
| 1 | GET protótipo (desktop) | 200, título contém Descoberta — PASS |
| 2–4 | Landmarks h1/Preflight/Rascunho visíveis | PASS ×3 |
| 5 | Estado padrão: só Montar ativa | PASS (`#panel-montar.active` único) |
| 6 | Preflight 3 linhas contém "combinações" | PASS (`24 combinações · ~48min estimado · últimos 2 anos`) |
| 7 | CTA casa `/Iniciar varredura — \d+, ~/` | PASS |
| 8 | Sem jargão duro visível no Montar | PASS |
| 9 | Sim `acomp` → voltar à tab Montar: CTA desabilitado + bloco nomeia diferença + link | PASS (`Existe varredura igual em curso — ver progresso…`; outro escopo quando rascunho difere — coberto pelo `else` do fonte) |
| 10 | `ver progresso` abre Acompanhando | PASS |
| 11 | Progressbar `aria-valuemax=24`, now 14 | PASS |
| 12 | Decidir: 6 th exatos (Rank, Candidato, Calmar, Max DD, Trades/cobertura, Ação) | PASS |
| 13 | 12 linhas + `Página 1 de 2` + `24 de 24 candidatos` | PASS |
| 14 | Expansão de linha (`aria-expanded`, `− detalhes`) | PASS |
| 15–16 | Modal Promover contém resumo de risco / Tier 3 (**escopo `#m-promote`** = dialog) | **FAIL ×2 — ver P1** (texto do dialog = só header; `.risk`/`.dest`/ações fora do dialog) |
| 17 | Confirmar cita Favoritos | PASS (`Candidato promovido a favorito tier 3. Veja em Favoritos → Tier 3.`) |
| 18 | Escape fecha + foco retorna ao botão | PASS |
| 19 | Modal avançado tem 2 ações | PASS (Selecionar filtrados / Limpar + Aplicar) |
| 20 | Seleção inline sem modal (busca `rsi` filtra 8→1, contador) | PASS |
| 21–23 | Mobile 390: Montar visível, CTA visível, Decidir 12 linhas | PASS ×3 |
| 24–26 | Zero console errors / pageerrors / recursos ≥400 (desktop+mobile) | PASS ×3 |
| 27 | Rank global estável sob filtro (`#1,#2,#3` → filtro BTC `#1,#7,#13,#19`) | PASS |
| 28 | Bloqueio real: limpar templates → impedimento `Escolha ao menos 1 template.` + CTA disabled + `pf-state=Bloqueado` | PASS |
| 29 | Fidelidade: sem toggle Antes/Depois; modos trocam markup (1 visível por vez); não é só-chrome (leaderboard 24 linhas, rascunho, preflight, modais) | PASS (P0s de fidelidade não disparam) |

## 3. Findings (toda finding com classificação e disposition)

- **P1 — Modais com markup inválido: `</div>` no lugar de `</header>` (linhas 246 e 270).** O parser fecha `#m-promote`/`#m-adv` logo após o header; `.body` (resumo de risco, Tier 3/onde-ver-depois, botões) vira irmão do dialog, filho direto de `.modal-bg`. Efeitos medidos: (a) dialog contém só o header (`dialog contains .risk = False`); semântica `role=dialog` quebrada (critérios 6 e 7 no plano estrutural); (b) layout quebrado — desktop: card-header 520px + corpo 522px lado a lado como itens flex, sem `padding:20px` de `.modal .body`; mobile 390: corpo espremido a ~209px ao lado do header; (c) comportamento preservado (abrir/confirmar/Escape/trap funcionam porque o JS opera no escopo `.modal-bg`). O gate do autor (25/25) não pegou porque os asserts eram em escopo de página, não de dialog. **Disposition: BLOCKED — fix no protótipo (trocar os 2 `</div>` por `</header>`) + re-gate dos asserts 15–16 em escopo de dialog + checagem de geometria (corpo dentro do card 520px, padding 20px); apply NÃO copiar o typo. Reexecução exigida; evidência atual do modal é inválida como spec visual.**
- **P3 — `Snapshot válido` visível no caminho feliz (`#pf-state`, fora do `<details>`).** `snapshot` está na lista avoid do issue/§4; spec manda detalhe técnico para bloco expansível. **Disposition: não-bloqueante — renomear (ex.: `Servidor OK`) ou mover para dentro do `<details>`; aceitar se o autor justificar como status, não jargão.**
- **P3 — Chip `RUNNING` (inglês) no modo Acompanhando.** Vocabulário esperado: `Acompanhando`. **Disposition: não-bloqueante — trocar por `EM CURSO`.**
- **P0 — nenhum.** Landmarks 3/3 no protótipo e na fonte viva; sem toggle Antes/Depois; protótipo não é só-chrome; servido == local.

Observações (não-findings): menção `Short volta quando houver dados` implementa a decisão operador (consistência, sem ofertar short) — aceito; tabs + simulador `só protótipo` permitem qualquer modo a qualquer hora — artefato de simulação rotulado, apply deve derivar o modo do sweep; `data-testid="start-sweep"` contém "sweep" mas não é linguagem visível — aceito; contraste de cores não verificável sem visão — pendente de revisão humana nos PNGs `/tmp/card852-*.png`.

## 4. Veredito parcial

**BLOCKED** — 1 achado P1 (modais: spec visual e semântica de dialog quebradas nas 2 viewports) invalida o PASS do autor nos critérios de promoção/a11y até o fix de 2 linhas + re-gate. Todo o resto (29/31 + extras, console limpo, digest, landmarks, fidelidade) PASS. Sem sessão autenticada: rota viva avaliada só via fonte — sem evidência de regressão no produto (nada foi editado no produto).

## 5. Pendências

1. Autor corrigir `</div>`→`</header>` (linhas 246, 270) e re-gatear asserts de modal em escopo de dialog + geometria desktop/mobile.
2. Revisão humana de pixels nos `/tmp/card852-*.png` (modelo sem visão) — inclui confirmar P1 visualmente e contraste.
3. Decisão P3 (`Snapshot válido`, `RUNNING`) — wording do autor ou aceite justificado.
4. Rota viva `/combo/discovery` em browser autenticado (fora do meu alcance sem sessão) — fica para T6/verificação do apply.
