# Design snapshot T7 — card 944

Method: dual-agent (A: 01a0a1af-e55e-70a3-a361-8a78b56b6480 · B: 01a0a1af-e55f-7812-be97-5c0dde9d065b)

Card: [#944](https://github.com/oalansilva/crypto/issues/944) · change `card-944-discovery-favorites-nomenclature` · Status=Design

Proto: https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/  
Digest: `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` (disco == HTTPS)

Tokens: `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`

## Síntese

Contrato visível confirmado nas duas grelhas (Acompanhar e Decidir), sem expandir:

Sharpe → Trades → Win% → Return → Max DD → Calmar (CAGR ÷ Max DD) → CAGR anualizado

ALPHA: Return `+12,8%` ≠ CAGR `3,7%`. Sem `Trades/cobertura` no nome da coluna. Landmarks 3/3. Sem painel ANTES/DEPOIS. Detector `[]`. `/login` não foi usado como rota.

Q1–Q3 intactas (nomes e ordem; parciais e leaderboard; CAGR extra no final).

## Findings

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 (Apply):** payload `total_return`; min-width 7 métricas; Return com sinal; data-label mobile; testes Calmar-primeiro; Montar condensado; chrome 390; chip NO-GO; mock 309/4; modal «Retorno (CAGR)»

**Disposition:** P3 no Apply. Sem rework.  
**Design Agent verdict: PASS**

## Relatórios longos

- A: `.impeccable/critique/944-card-944-discovery-favorites-nomenclature-assessment-A.md`
- B: `.impeccable/critique/944-card-944-discovery-favorites-nomenclature-assessment-B.md`

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
