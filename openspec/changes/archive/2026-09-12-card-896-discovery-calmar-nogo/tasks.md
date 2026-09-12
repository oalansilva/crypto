# Tasks — card-896-discovery-calmar-nogo

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Calmar de calendário e teto

- [x] 1.1 — CAGR/Calmar da Descoberta usam `years = calendário da janela in-sample / 365` (não `n_trades/365` nem `len(equity)/365`). Max DD permanece fração 0–1. Fixture: 30 negócios em ~3 anos não produz Calmar `1e27`.
- [x] 1.2 — Antes de persistir e antes de formatar `pt-BR`: não finito ou `|Calmar| > 1000` → null / célula `N/A`; `|CAGR| > 100` → null. Honesto ~22 e `1,20` permanecem visíveis com 2 casas. UI sanitiza legado `1e27` sem backfill `#862f31de`.

## 2. Ranking GO-first

- [x] 2.1 — `rank_eligible` (parciais top-5 e Decidir): classe `GO` acima de todo não-`GO`; dentro da classe, Calmar (já corrigido) → negócios → `result_id`. N/A não toma 1º. ALPHA `RS-B109ED2C80` NO-GO fica abaixo de qualquer GO.
- [x] 2.2 — Payload de parciais/leaderboard expõe `oos_verdict.status` (`GO`/`NO-GO`) para a linha. Veredito ausente não inventa `GO`. Elegibilidade 30/90% inalterada.

## 3. UI da linha

- [x] 3.1 — Acompanhar parciais e Decidir: selo visível `GO` (azul informativo) / `NO-GO` (danger), distinto de `Baixa amostra` / `Amostra insuficiente`. Sem abrir gráfico nem promover.
- [x] 3.2 — Copy/aria: Calmar = `Calmar (CAGR anual do calendário ÷ Max DD)`; `Trades/cobertura` = `negócios / cobertura`. `30 · 100%` não é win rate. Promover permanece no NO-GO elegível. Fidelidade ao proto; landmarks e modos #852 sem regressão.

## 4. Verificação

- [x] 4.1 — Testes: calendário vs 31/365; teto → N/A; GO acima de NO-GO; selo na linha; Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 4.2 — `openspec verify` desta change.
