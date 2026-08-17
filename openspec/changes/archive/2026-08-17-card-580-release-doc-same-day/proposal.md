# Proposal: card-580-release-doc-same-day

## Why

`scripts/release-guard pre` trata a existência de `docs/release-YYYY-MM-DD.md` como PR documental e exige `PROD_DEPLOY_EVIDENCE`. No segundo pacote de 2026-08-17 a doc do lote 1 já existia; o PR de código `develop → main` (#578) só passou no `pre` reusando a evidência do deploy `91f5620e`, que não era deste pacote. O gate #518 assume um pacote por data; o cripto precisa de um segundo pacote no mesmo dia sem herdar evidência alheia nem criar segunda doc.

## What Changes

- Distinguir PR de **código** vs **documental** pelo **diff de arquivos** (`origin/main...HEAD` se a branch atual é `release-*`, senão `origin/main...origin/develop`) contra um allowlist de closeout (`docs/**`, archive OpenSpec, `AGENTS.md`/`rules.md`). **Não** usar igualdade `origin/develop == origin/main`.
- Um segundo pacote no mesmo dia **não** faz o `pre` do PR de código exigir `PROD_DEPLOY_EVIDENCE` do lote anterior só porque a doc do dia já existe.
- Continua existindo **uma única** `docs/release-YYYY-MM-DD.md` por data (atualizar o arquivo após o deploy do segundo lote; não criar `-lote2`).
- O `post` valida que o SHA de `PROD_DEPLOY_EVIDENCE` é o commit de **código/PROD deste lote** (ancestral de `origin/main` cujo delta restante ⊆ allowlist), não um SHA de lote anterior nem o SHA só-docs do PR documental.

## UI impact

`none`

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `release-worktree-hygiene`: o requisito “Documentação canônica é validada antes do PR documental” deixa de tratar “arquivo existe” como sinônimo de PR documental.

## Impact

`scripts/release-guard` seção “Release docs”; `AGENTS.md` / ordem de fechamento se a redação ainda disser “um pacote por data” de forma absoluta. Sem UI.
