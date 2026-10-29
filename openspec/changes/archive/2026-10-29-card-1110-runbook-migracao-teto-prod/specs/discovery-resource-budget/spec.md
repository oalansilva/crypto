## MODIFIED Requirements

### Requirement: DEV containment covers the complete process tree
Discovery DEV SHALL use cgroup v2 MemoryHigh=3 GiB, MemoryMax=4 GiB, MemorySwapMax=512 MiB, and Discovery PROD SHALL use MemoryHigh=4 GiB, MemoryMax=5 GiB, MemorySwapMax=512 MiB, each for all descendants, page cache and IPC. Expected limits SHALL come from a per-environment resource profile selected by `DISCOVERY_RESOURCE_PROFILE`; an unknown profile SHALL block work. The actual host MemTotal SHALL be at least the sum of all Discovery envelopes on the host (9 GiB) plus 13 GiB reserved for other services and 1 GiB host margin. Admission SHALL verify effective limits equal to the profile, MemAvailable≥8 GiB, available swap≥1 GiB and disk free≥4 GiB. Missing/incompatible containment SHALL block work. MemAvailable<2 GiB for 30 seconds SHALL abort the attempt. Retries SHALL never increase limits. An over-limit Discovery tree SHALL be contained in its own cgroup without global OOM and without stopping the other environment's Discovery or the PROD backend.

#### Scenario: Over-budget attempt in isolated test
- **WHEN** a synthetic attempt exceeds its verified isolated cgroup budget
- **THEN** its contained tree is terminated, its durable attempt remains accounted and no global OOM is induced

#### Scenario: Invalid environment
- **WHEN** limits or reserve cannot be verified
- **THEN** the optimizer does not start and resource_budget_unavailable is emitted

#### Scenario: Unit and profile diverge
- **WHEN** the installed unit limits differ from the limits of the selected profile
- **THEN** admission refuses, the sweep stays queued and resource_budget_unavailable is emitted

#### Scenario: PROD search waits for host memory
- **WHEN** Discovery PROD admission finds MemAvailable below 8 GiB because of other workloads on the shared host
- **THEN** the search does not start, no attempt or circuit failure is recorded, resource_budget_unavailable is logged, the sweep stays running without progress and the outbox redelivers it until admission passes

#### Scenario: Two envelopes no longer fit the host
- **WHEN** host MemTotal is below the sum of both Discovery envelopes plus 14 GiB
- **THEN** both Discovery DEV and Discovery PROD refuse admission with resource_budget_unavailable

#### Scenario: Normal DEV search under the lower ceiling
- **WHEN** Discovery DEV runs a normal search with MemoryHigh=3 GiB and MemoryMax=4 GiB
- **THEN** admission accepts it and the search completes with zero `high`, `max` and `oom_kill` events

### Requirement: Cache bytes and worker count are bounded
Per-process optimizer caches SHALL share one 64 MiB LRU budget, 4,096 entries and 32 snapshots compatible with #1091. Retained buffers/references SHALL count conservatively; oversized items SHALL bypass admission. Eviction/cleanup SHALL preserve identity, immutability and exact outputs. DEV and PROD SHALL each use one internal worker, bounded by floor((MemoryMax−1 GiB)/3 GiB) with minimum admissible 1, never solely CPU or Celery concurrency.

#### Scenario: Consecutive unique searches
- **WHEN** unique windows exceed cache capacity across searches
- **THEN** retained cache bytes remain ≤64 MiB, execution boundaries clear caches and outputs equal cache-disabled reference

#### Scenario: Worker count per environment
- **WHEN** the profile is `dev` with MemoryMax=4 GiB or `prod` with MemoryMax=5 GiB
- **THEN** effective workers is 1, and a profile whose MemoryMax yields fewer than one worker refuses to start

### Requirement: Recovery loops and operational health are observable
Each Discovery service, DEV and PROD, SHALL use Restart=on-failure, RestartSec=60 seconds and at most three starts per 900 seconds; after that it SHALL stay stopped until the operator acts, with no automatic reset-failed. A durable per-environment circuit SHALL block starts after three resource failures or operational interruptions in fifteen minutes, including new sweeps. Local authenticated acknowledgement SHALL verify empty groups/no active leases/healthy admission for the unit of the acknowledged environment, record actor/reason/time and never reset attempt counts or terminal sweeps. Telemetry SHALL expose cgroup memory/swap/events, RSS/PSS, cache/spool/futures, attempts/restarts, confirmed counters and heartbeat/progress ages. Alerts SHALL distinguish alive from progressing.

#### Scenario: New sweeps cannot bypass circuit
- **WHEN** three resource failures occur across different sweeps in fifteen minutes
- **THEN** starts are blocked with intervention-required alert even after restart or new sweep creation

#### Scenario: Repeated PROD failure
- **WHEN** Discovery PROD fails and systemd restarts it three times within fifteen minutes
- **THEN** each restart waits 60 seconds, the fourth start is refused and the unit stays stopped until Alan acts

#### Scenario: Acceptance evidence is bounded
- **WHEN** the original 492,480 workload and three consecutive searches run after isolated failure-injection tests
- **THEN** input/code manifests, peak memory/swap, duration, counters and zero global OOM are recorded within DEV envelope
- **AND** exact ranking/normalization/ties and post-cleanup memory thresholds from design are satisfied
