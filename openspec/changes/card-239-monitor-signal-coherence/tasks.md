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
