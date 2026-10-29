## MODIFIED Requirements

### Requirement: Incremental Data Storage

The system MUST keep a local Parquet read cache of OHLCV data for analysis performance, derived from the canonical history in PostgreSQL. The cache MUST NOT download candles from the exchange on its own: a missing period is first collected into the canonical history (only the missing part), then materialized into the cache. Each cache file MUST be identified by series and data version, and deleting it MUST NOT lose history.

#### Scenario: First Run (Download All)
- **WHEN** no cache exists for "BTC/USDT" on "1h" and the canonical history covers the requested period
- **THEN** the system MUST materialize the cache from PostgreSQL
- **AND** MUST NOT call the exchange

#### Scenario: Incremental Update (Delta Download)
- **WHEN** the canonical history ends at "2023-02-01 00:00:00" and a read asks up to "2023-03-01"
- **THEN** the system MUST collect only the missing part into the canonical history
- **AND** rebuild or extend the cache from the canonical history, under the series version

#### Scenario: Slice Retrieval (No Network)
- **WHEN** the cache for the current series version covers "2020-01-01" to "2024-01-01" and a read asks "2022-01-01" to "2022-02-01"
- **THEN** the system MUST return the slice from the Parquet cache
- **AND** MUST NOT make any network request to the exchange

#### Scenario: Stale version
- **WHEN** the series version changes after a correction
- **THEN** the cache of the previous version is not used for new reads
