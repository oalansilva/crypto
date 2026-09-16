# Design snapshot T7 — card 949

Method: dual-agent (A: d0bc768e-6fe4-4af8-a58b-62165403e57a · B: a76dd586-524f-4415-9183-e403ad85465c)

Card: [#949](https://github.com/oalansilva/crypto/issues/949) · change `card-949-favorito-historico-inteiro` · Status=Design

Proto: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/  
Digest index: `0d87ecd5992a5aa343c4d2249209bb8d1d0a3ae4f9f5b487ec925beb369b97e4` (disco == HTTPS)

Tokens: `UI impact: affected` · `live_route: /favorites` · `surface: existing`

## Síntese

Ao salvar depois de 70/30, o favorito **novo** grava e mostra o período escolhido completo — não o treino.

- Descoberta «todo»: lista **17/08/2017 → 15/09/2026** (71 / +210,40%), não 17/08/2017 → 24/12/2023.
- Legado Q2: SOL continua **17/08/2017 → 24/12/2023**.
- Combo 2 anos + 70/30: **15/09/2024 → 15/09/2026** (não treino, não «todo»).
- Grelha Decidir permanece 70/30; modal promover **sem** preview.
- Sem mistura 43 / Win 58,14% / 68 sob o rótulo 2023.

Landmarks `/favorites` 4/4. Sem painel ANTES/DEPOIS. Detector só `side-tab` (P3). `/login` não foi usado como prova de clone.

Q1–Q3 intactas.

## Findings

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 (Apply):** `side-tab` cards de tier; truncagem Estratégia; alvos 32/28px; 33 tr vs 71 negócios; clip Promover 1440; Preflight 01 jan 2017; leaderboard 309/26; thead clip 390; SVG vs #917; mock sem loading; mecanismo de persistência

**Disposition:** P3 no Apply. Sem rework.  
**Design Agent verdict: PASS**

## Relatórios longos

- A: `.impeccable/critique/949-card-949-favorito-historico-inteiro-assessment-A.md`
- B: `.impeccable/critique/949-card-949-favorito-historico-inteiro-assessment-B.md`

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
