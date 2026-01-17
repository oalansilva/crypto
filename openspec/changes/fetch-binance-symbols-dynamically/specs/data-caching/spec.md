# Data Caching Spec Delta

## ADDED Requirements

### Requirement: Cache Exchange Symbols
The System SHALL cache the list of available trading pairs (symbols) fetched from the exchange API (Binance) to minimize latency and API calls.
The cache MUST be persisted to disk (e.g., JSON or SQLite) and remain valid for a configurable duration (default: 24 hours).
Ideally, the cache mechanism SHOULD be extensible to support distributed caching (e.g., Spark/Redis) for high-scale scenarios, though local file caching is sufficient for the MVP.

#### Scenario: First Fetch (Cache Miss)
Given the cache file does not exist or is older than 24 hours
When the System requests the list of symbols
Then it MUST fetch the latest markets from the Binance API
And filter the list to include ONLY pairs ending in "/USDT"
And save the filtered result to the local cache file
And return the list to the caller

#### Scenario: Subsequent Fetch (Cache Hit)
Given the cache file exists and is younger than 24 hours
When the System requests the list of symbols
Then it MUST read the list directly from the local cache file
And return the list immediately without calling the external API
