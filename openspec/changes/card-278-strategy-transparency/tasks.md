## 1. Canonical backend contract

- [x] 1.1 Implement typed strategy transparency manifest models and metadata for indicator labels, functions, panels, scales, colors, references and participation.
- [x] 1.2 Derive manifests from `ComboTemplate.template_data`/effective configuration, reject unresolved generic identities, and correct public copy including `ema_rsi_fibonacci`.
- [x] 1.3 Add an auditable active-strategy matrix and tabular drift validation without duplicating executable strategy rules.

## 2. Timestamped series and APIs

- [x] 2.1 Build canonical timestamped series only from manifest-declared execution columns, including ROC and deduplicating aliases/diagnostics.
- [x] 2.2 Persist/serialize timestamped series for new combo/backtest/favorite analysis results while preserving safe legacy compatibility.
- [x] 2.3 Expose the same public manifest in Favorites and Monitor, including common-user functional transparency without source code, secrets or raw diagnostics.
- [x] 2.4 Return explicit unavailable/timeframe mismatch states instead of positional alignment or silent omission.

## 3. Shared chart transparency UI

- [x] 3.1 Add frontend types/normalization for the canonical manifest and timestamped indicator points.
- [x] 3.2 Extend `StrategyChartSurface` with manifest-defined price, volume, oscillator, MACD and ATR panels synchronized by timestamp/range/crosshair.
- [x] 3.3 Add accessible legend, reference labels, logic blocks and explicit unavailable states using `DESIGN.md` tokens and 44px controls.
- [x] 3.4 Connect Favorites analysis and Monitor chart/trades flows to the same manifest/series while preserving candles, markers, zoom, entry/stop and actions.
- [x] 3.5 Clear or replace indicator panels on timeframe changes and validate desktop/mobile behavior.

## 4. Automated validation

- [x] 4.1 Add backend unit/integration tests for all active identities, manifest derivation, EMA/SMA/Bandas/volume/RSI/ADX/ROC/MACD/ATR, safe redaction and timestamp gaps.
- [x] 4.2 Add frontend tests for timestamp joins, panel/legend rendering, crosshair values, unavailable states and accessibility semantics.
- [x] 4.3 Update and run focused Playwright scenarios for Favorites and Monitor on desktop/mobile, preserving marker/trade/zoom behavior.
- [x] 4.4 Run focused backend tests, frontend lint/tests/build, OpenSpec validation and basic accessibility checklist.

## 5. Technical closeout

- [x] 5.1 Run `$openspec-verify-change` against artifacts, implementation and completed test evidence.
- [x] 5.2 Move card to Code Review, run an independent Codex review of the exact diff and fix/classify all findings before commit.
- [x] 5.3 Commit the reviewed branch, integrate into `develop`, run `./restart`, validate served Favorites/Monitor and record evidence before `Done` técnico.

## 6. Correção pós-validação DEV

- [x] 6.1 Detectar manifesto cacheado sem séries utilizáveis e hidratar a análise pelo endpoint do favorito, preservando fallback seguro.
- [x] 6.2 Cobrir favorito legado com candles/arrays alinhados e sem `analysis_strategy_transparency` em testes frontend/backend e Playwright.
- [x] 6.3 Tornar `./restart` do source DEV canônico restrito aos serviços/portas DEV e validar que não referencia nem reinicia PROD.
- [x] 6.4 Rodar apply/verify, checks focados, review independente, integrar em `develop`, reiniciar somente DEV e validar o favorito real da captura.

Use project skills under `.codex/skills` when applicable for architecture, tests, debugging, frontend, accessibility and OpenSpec work.
