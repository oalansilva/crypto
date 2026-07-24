## 1. Post-release alignment

- [x] 1.1 Add focused automated coverage for equal refs, ancestor with identical tree, divergent trees, and non-ancestor identical trees.
- [x] 1.2 Update `scripts/release-guard post` to accept only the specified semantic alignment states.

## 2. CI execution

- [x] 2.1 Restrict full push-triggered CI to `develop` and `main` while retaining pull-request validation for both targets and event-separated concurrency.
- [x] 2.2 Remove the artificial `backend-tests` dependency from Playwright while preserving both jobs as mandatory `qa-gate` dependencies.

## 3. Agent operating protocol

- [x] 3.1 Add the bounded native CI waiting protocol to the canonical global `alan-workflow` skill under its applicable repository rules.
- [x] 3.2 Add the Cripto-specific overlay and canonical watcher command to `AGENTS.md`.

## 4. Validation and evidence

- [x] 4.1 Run focused release-guard tests and validate shell/workflow syntax.
- [x] 4.2 Run OpenSpec validation and verify the implementation against proposal, design, specs, and tasks.
- [ ] 4.3 Record baseline and post-change CI evidence on issue #326 and its pull request.

Use the applicable project skills under `.codex/skills` for OpenSpec, testing, debugging, and review throughout implementation.
