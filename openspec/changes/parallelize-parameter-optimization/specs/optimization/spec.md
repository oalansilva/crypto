# Specification: Parallel Parameter Optimization

## ADDED Requirements
### Requirement: Parallelize Optimization Loop
The system MUST execute backtests for parameter variations in parallel processes to utilize available CPU cores.

#### Scenario: Running optimization with multiple workers
Given a combo strategy optimization request
And the machine has 4 CPU cores
When the optimization starts for a parameter (e.g., "sma_short")
Then the system should spawn at least 3 worker processes
And the potential values for "sma_short" (e.g., 3 to 20) should be distributed among these workers
And the total execution time for that stage should be significantly less than sequential execution

#### Scenario: Fallback for unpicklable errors
Given a worker process fails due to a pickling error or exception
When the optimization is running
Then the system should catch the error
And mark that specific test value as failed
But continue executing other tests
And log the error clearly for debugging
