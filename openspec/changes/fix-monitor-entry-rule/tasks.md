## 1. Locate entry-distance logic

- [ ] 1.1 Find the opportunity monitor entry-distance calculation (backend)
- [ ] 1.2 Identify how trend up (short > long) and crossover pairs are currently used

## 2. Update entry-distance rule

- [ ] 2.1 Implement trend gate: if short <= long, use short→long distance (red → blue)
- [ ] 2.2 When short > long, use short→medium distance (red → orange)
- [ ] 2.3 Ensure entry validity uses (crossover short/long OR short/medium) AND trend up

## 3. Verification

- [ ] 3.1 Add/adjust any tests or checks for the new rule (backend)
- [ ] 3.2 Manually confirm /monitor reflects the corrected distance logic

> Note: use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
