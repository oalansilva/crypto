## 1. Canonical workflow and skill

- [x] 1.1 Create a coordinated change/branch in the versioned source of `alan-workflow`, update the global stage contract there, and record its independent commit and rollback evidence on card #362.
- [x] 1.2 Update and validate the Codex project skill for automatic stage-model routing, requiring exact agent names, `fork_turns="none"`, self-contained role packets, static bootstrap acceptance, no server-security changes, and runtime evidence only for Luna lanes when actually used.
- [x] 1.3 Leave generated OpenSpec and Cursor adapters untouched; document Codex as the only supported client for automatic routing.

## 2. Project-scoped model profiles

- [x] 2.1 Pin the project primary session to `gpt-5.6-sol` with `high` reasoning while preserving multiagent limits.
- [x] 2.2 Add the `crypto_luna_implementer` profile with Luna Max, workspace-write, `Pronto para Dev` preflight, `/opsx:apply`, scoped ownership, and focused verification.
- [x] 2.3 Add the `crypto_luna_reviewer` profile with Luna Max, a required fresh thread, read-only sandbox, exact-diff review, and no self-fixes.
- [x] 2.4 Add the `crypto_luna_release_manager` profile with Luna Max, `danger-full-access`, explicit-release/homologation preflight, release guards, no code edits, and auditable closeout.

## 3. Local operating contract

- [x] 3.1 Update `AGENTS.md` with the fixed executor for each OpenSpec/status/release stage, the bootstrap exception, and removal of contradictory generic routing guidance.
- [x] 3.2 Update `rules.md` with the short normative stage-model mapping, static bootstrap acceptance, no server-security changes, no Terra/fallback rule, and failure behavior.
- [x] 3.3 Preserve the captured rollback of the previous Project 1 readme, update its operational description with static bootstrap acceptance and post-activation runtime evidence, and record the revised digest/evidence.

## 4. Contract validation

- [x] 4.1 Update focused tests that parse Codex TOML and assert exact profiles, models, efforts, all sandboxes, `fork_turns="none"`, self-contained role-packet fields, stage gates, static bootstrap acceptance, no server-security changes, no-fallback instructions, and Codex-only scope.
- [x] 4.2 Complete fixture coverage for the read-only runtime inspector, including invalid JSON, multiple session metadata, mismatched thread identity and conflicting model/effort/sandbox/permission metadata while preserving the strict output allowlist.
- [x] 4.3 Revalidate the Codex skill with the official skill validator; validate TOML, model/effort availability, focused workflow tests, OpenSpec, and `git diff --check` after the approved redesign.

## 5. Bootstrap acceptance and delivery

- [x] 5.1 Validate the installed routing statically through TOML parsing, exact profile/model/effort/sandbox assertions, skill validation, OpenSpec and focused tests; query `${CODEX_HOME:-$HOME/.codex}/models_cache.json` with `jq -e` and prove Sol supports `high` while Luna supports `max`; document that runtime evidence is collected only when each lane is naturally used, without pre-spawning agents or changing server security.
- [ ] 5.2 Run a fresh independent read-only Codex review on the bootstrap diff, resolve/classify findings, commit/push that content as the reviewed SHA, and move the card to QA. Require the exact Luna reviewer for tasks started after the profiles are versioned and loaded.
- [ ] 5.3 Run Sol High `/opsx:verify` and mandatory QA evidence on the reviewed SHA, integrate in `develop`, prove integrated-tree equivalence or revalidate affected checks, execute `./restart`, validate application health at the DEV URL (not agent-routing runtime proof), and publish the Done technical handoff.

Bootstrap decision (2026-08-02): Alan explicitly rejected changes to server
configuration for runtime smoke tests. The card accepts profile installation by
static contract validation. Runtime metadata remains mandatory when a lane is
actually used after activation; release manager is never pre-spawned without an
authorized release.

Rework gate (2026-08-02): Alan reapproved the revised design by moving the card
to `Pronto para Dev`; implementation resumed under the bootstrap exception and
the card advanced to `Code Review` after focused validation.
