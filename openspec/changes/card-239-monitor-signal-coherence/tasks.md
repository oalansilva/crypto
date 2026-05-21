## 1. Diagnosis

- [x] 1.1 Trace Monitor ADA/USDT 1D moving-average data sources: opportunity payload, favorite trade payload, signal history, marker source and summary state.
- [x] 1.2 Identify whether the divergence originates in frontend resolver, backend/API payload, persisted favorite data, cache or strategy calculation.

## 2. Implementation

- [x] 2.1 Add or update a shared Monitor signal resolver so visible current state follows the latest valid chart marker direction when available.
- [x] 2.2 Keep backend raw status classification intact and preserve existing Portuguese public labels.
- [x] 2.3 Ensure Monitor modal/header/summary use the same resolved state.

## 3. Validation

- [x] 3.1 Add focused automated coverage for chart/state divergence using ADA/USDT-like fixture or the reported case.
- [x] 3.2 Run OpenSpec validation and focused frontend/backend tests.
- [x] 3.3 Run runtime validation with `./restart` and record evidence for card #239 before moving to `Done`.

## 4. Follow-up after Alan retest

- [x] 4.1 Make Monitor list sections and cards resolve `Compra`/`Venda` from favorite-backed latest markers when available, not only the chart modal.
- [x] 4.2 Prevent duplicate synthetic fallback `Venda` markers when the latest favorite-backed chart marker already drives the same state.
- [x] 4.3 Add focused regression coverage for raw `HOLDING` plus latest favorite marker `Venda`.
- [x] 4.4 Re-run OpenSpec validation and focused frontend tests.
- [ ] 4.5 Integrate in `develop`, restart runtime and update card evidence.
