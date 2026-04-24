## 1. OpenSpec And Data Contract

- [x] 1.1 Create proposal, design, and specs for automatic chart pattern detection.
- [x] 1.2 Define event shape with pattern, direction, confidence, timestamp, reference price, source, dedupe key, and metadata.

## 2. Storage And API Read Path

- [x] 2.1 Add nullable `chart_patterns` JSONB storage to `market_indicator` and startup schema guard.
- [x] 2.2 Include `chart_patterns` in latest/time-series read queries.
- [x] 2.3 Serialize detected pattern events idempotently during indicator upsert.

## 3. Detection Pipeline

- [x] 3.1 Implement deterministic golden cross and death cross rules using stored SMA 20/50 values.
- [x] 3.2 Implement deterministic double top and double bottom rules using local pivots, neckline confirmation, and tolerance.
- [x] 3.3 Implement confidence scoring clamped to 0-100.
- [x] 3.4 Implement deduplication to avoid repeated nearby events.
- [x] 3.5 Integrate detector into `MarketIndicatorService._compute_indicators`.

## 4. Validation

- [x] 4.1 Add unit tests for cross detection, double top/bottom detection, confidence bounds, and deduplication.
- [x] 4.2 Add tests for market indicator serialization/read shape.
- [x] 4.3 Run targeted backend tests for the new detector and market indicator service.
