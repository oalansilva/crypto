# discovery-resource-budget Specification

## Purpose
TBD - created by archiving change card-1093-discovery-memory. Update Purpose after archive.
## Requirements
### Requirement: DEV containment covers the complete process tree
Discovery DEV SHALL use cgroup v2 MemoryHigh=5 GiB, MemoryMax=6 GiB, MemorySwapMax=512 MiB for all descendants, page cache and IPC. The actual host inventory SHALL support 16 GiB reserved for other services plus 1 GiB host margin outside Discovery. Admission SHALL verify effective limits, MemAvailable≥8 GiB, available swap≥1 GiB and disk free≥4 GiB. Missing/incompatible containment SHALL block work. MemAvailable<2 GiB for 30 seconds SHALL abort the attempt. Retries SHALL never increase limits.

#### Scenario: Over-budget attempt in isolated test
- **WHEN** a synthetic attempt exceeds its verified isolated cgroup budget
- **THEN** its contained tree is terminated, its durable attempt remains accounted and no global OOM is induced

#### Scenario: Invalid environment
- **WHEN** limits or reserve cannot be verified
- **THEN** the optimizer does not start and resource_budget_unavailable is emitted

### Requirement: Cache bytes and worker count are bounded
Per-process optimizer caches SHALL share one 64 MiB LRU budget, 4,096 entries and 32 snapshots compatible with #1091. Retained buffers/references SHALL count conservatively; oversized items SHALL bypass admission. Eviction/cleanup SHALL preserve identity, immutability and exact outputs. DEV SHALL use one internal worker, bounded by floor((MemoryMax−2 GiB)/3 GiB), never solely CPU or Celery concurrency.

#### Scenario: Consecutive unique searches
- **WHEN** unique windows exceed cache capacity across searches
- **THEN** retained cache bytes remain ≤64 MiB, execution boundaries clear caches and outputs equal cache-disabled reference

### Requirement: Solo cleanup terminates all attempt children
A lost/failed attempt SHALL stop submission, terminate its exclusive supervisor group, escalate SIGTERM to SIGKILL after ten seconds and prove cleanup within twenty seconds before another pool starts. Unproven cleanup SHALL fail the service for systemd control-group cleanup. OOMPolicy=kill and KillMode=control-group SHALL contain whole-service failure. Pending-future cancellation or Celery soft limits SHALL NOT substitute for termination.

#### Scenario: One child breaks the pool
- **WHEN** a child is killed while another still runs
- **THEN** all attempt children stop, no later round runs and no replacement starts before cleanup is proven

### Requirement: Recovery loops and operational health are observable
The service SHALL use Restart=on-failure, RestartSec=60 seconds and at most three starts per 900 seconds. A durable per-environment circuit SHALL block starts after three resource failures or operational interruptions in fifteen minutes, including new sweeps. Local authenticated acknowledgement SHALL verify empty groups/no active leases/healthy admission, record actor/reason/time and never reset attempt counts or terminal sweeps. Telemetry SHALL expose cgroup memory/swap/events, RSS/PSS, cache/spool/futures, attempts/restarts, confirmed counters and heartbeat/progress ages. Alerts SHALL distinguish alive from progressing.

#### Scenario: New sweeps cannot bypass circuit
- **WHEN** three resource failures occur across different sweeps in fifteen minutes
- **THEN** starts are blocked with intervention-required alert even after restart or new sweep creation

#### Scenario: Acceptance evidence is bounded
- **WHEN** the original 492,480 workload and three consecutive searches run after isolated failure-injection tests
- **THEN** input/code manifests, peak memory/swap, duration, counters and zero global OOM are recorded within DEV envelope
- **AND** exact ranking/normalization/ties and post-cleanup memory thresholds from design are satisfied

