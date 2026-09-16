## Why

Quem compara o mesmo setup em Favoritos e na Descoberta se perde: os indicadores mudam de nome e de ordem, e o **Return** de Favoritos simplesmente não aparece na Descoberta. O administrador precisa reler os **mesmos nomes** na **mesma ordem** para não achar que está vendo outra estratégia.

## What Changes

- Na Descoberta, os indicadores partilhados com Favoritos usam os mesmos nomes: **Sharpe**, **Trades**, **Win%**, **Return**, **Max DD**, nessa ordem.
- Campos extra da Descoberta ficam depois desse bloco: **Calmar** (subtexto **CAGR ÷ Max DD**) e **CAGR anualizado** (nome próprio, no final).
- **Return** passa a existir como coluna. CAGR não usa esse nome nem esse sítio.
- **Trades** é o nome da coluna; cobertura de velas fica só como subtexto.
- Vale para **parciais e leaderboard**. Identidade da linha (rank, candidato, ação) permanece.
- Os números podem continuar diferentes dos de Favoritos. Este card alinha nome e ordem, não o valor.

Fora: igualar o número do Return (nem de qualquer outro indicador) ao de Favoritos; copiar a grade inteira de Favoritos (Sel, Tier, Telegram, Symbol, Stop, PF, SQN); mudar Favoritos; mudar cálculo do Calmar, ranking, filtros, seletor de ordenar ou regras GO / NO-GO; preencher métricas depois de promover (#897); Monitor, Telegram, mobile de Favoritos, Excel.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra nas capacidades já existentes da Descoberta.

### Modified Capabilities

- `discovery-leaderboard`: a grelha do Decidir mostra Sharpe → Trades → Win% → Return → Max DD → Calmar (CAGR ÷ Max DD) → CAGR anualizado, visíveis sem expandir; Return é coluna própria; CAGR anualizado fica no final e não empresta o nome Return; Trades não se chama Trades/cobertura.
- `discovery-three-modes`: parciais top-5 do Acompanhar usam os mesmos nomes e a mesma ordem; Montar permanece sem grelha de candidatos e sem delta deste card.

## Impact

- Frontend: `DiscoveryPage.tsx` / `DiscoveryPage.css` — thead e células das parciais e do leaderboard; `data-label` mobile.
- API: o JSON persistido do resultado já pode trazer `total_return` / `total_return_pct` no blob `metrics`; Apply expõe o campo na grelha se o top-level ainda não o envia.
- Specs canónicas: `openspec/specs/discovery-leaderboard`, `discovery-three-modes`.
- Protótipo: `frontend/public/prototypes/card-944-discovery-favorites-nomenclature/`.
- Sem mudança em Favoritos, motor, ranking, filtros, ordenar, GO/NO-GO, promover (#897), Monitor.
