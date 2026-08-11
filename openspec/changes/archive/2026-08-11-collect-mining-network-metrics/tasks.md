## 1. OpenSpec And Contract

- [x] 1.1 Create proposal, design, spec delta, and tasks.
- [x] 1.2 Define mining metric endpoints, response contract, MA/ATH rules, and sharp-drop threshold.
- [x] 1.3 Use relevant project skills and subagents for mapping, implementation validation, and review when applicable.

## 2. Glassnode Connector

- [x] 2.1 Add Glassnode mining metric endpoint mapping for hash rate, difficulty, and total miner revenue.
- [x] 2.2 Preserve existing API key, cache, rate-limit, and provider error behavior.

## 3. Backend Domain Service

- [x] 3.1 Add mining network metric service using the existing Glassnode connector.
- [x] 3.2 Sort and enrich numeric series points with 7d and 30d trailing moving averages.
- [x] 3.3 Track ATH value/timestamp within the fetched series.
- [x] 3.4 Emit `sharp_drop` alerts only when latest value is more than 10% below MA7.
- [x] 3.5 Keep empty, insufficient, and non-numeric series valid without crashing.

## 4. API Surface

- [x] 4.1 Add `GET /api/onchain/glassnode/{asset}/mining-metrics`.
- [x] 4.2 Return metric summaries, enriched points, ATH data, source metadata, and cached status.
- [x] 4.3 Map validation/config/rate-limit errors to the existing Glassnode HTTP statuses.

## 5. Validation

- [x] 5.1 Add unit tests for moving averages, ATH, alert threshold, boundary behavior, and non-numeric payloads.
- [x] 5.2 Add connector tests for mining endpoint mapping.
- [x] 5.3 Add route tests for payload and error mapping.
- [x] 5.4 Run OpenSpec validation and targeted backend tests.
