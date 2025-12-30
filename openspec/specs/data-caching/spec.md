# data-caching Specification

## Purpose
TBD - created by archiving change incremental-data-storage. Update Purpose after archive.
## Requirements
### Requirement: Incremental Data Storage

The system MUST store OHLCV data locally in Parquet format to ensure high performance and avoid redundant downloads.
When specific time ranges are requested, the system MUST check local storage first.
If local data exists, it MUST determine the latest timestamp stored and ONLY download data from that point forward (incremental update).
New data MUST be appended to the local storage (Parquet file), ensuring the dataset grows over time without gaps.

#### Scenario: First Run (Download All)
Given that no local data exists for "BTC/USDT" on "1h" timeframe
When `fetch_data` is called for a period (e.g., 2023-01 to 2023-02)
Then the system MUST download data from the earliest available point or the start of the requested period
And save it to `data/storage/exchange/symbol/timeframe.parquet`

#### Scenario: Incremental Update (Delta Download)
Given that local data exists up to "2023-02-01 00:00:00"
When `fetch_data` is called with a range ending in "2023-03-01"
Then the system MUST read the keys/metadata from the local Parquet file
And determine the last timestamp is "2023-02-01"
And download ONLY the data from "2023-02-01" to "2023-03-01" (plus/minus 1 candle logic)
And append this new data to the Parquet file

#### Scenario: Slice Retrieval (No Network)
Given that local data exists from "2020-01-01" to "2024-01-01"
When `fetch_data` is called for "2022-01-01" to "2022-02-01"
Then the system MUST load the data from the Parquet file
And return the DataFrame sliced to the requested period
And MUST NOT make any network requests to the exchange

