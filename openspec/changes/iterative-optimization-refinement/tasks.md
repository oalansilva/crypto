# Tasks: Iterative Optimization Refinement

- [ ] Wrap `run_optimization` loop in a `while` convergence loop <!-- id: 0 -->
- [ ] Implement parameter snapshot and comparison logic <!-- id: 1 -->
- [ ] Add explicit logging for Rounds and Convergence <!-- id: 2 -->
- [ ] Verify that parameters from Round N-1 are used as context for Round N (already verified by "full_params" fix, but critical to re-verify) <!-- id: 3 -->
- [ ] Test convergence with a small parameter set (ensure it stops when stable) <!-- id: 4 -->
