## Why

O card #469 entregou `/combo/discovery` e fechou Done com `e2e-playwright`/`qa-gate` verdes sem nenhum spec da rota nova. A regra 13 (QA visual obrigatório) existia, mas era voluntária: rota nova + spec inexistente = pipeline verde. A divergência só apareceu no teste manual do Alan.

## What Changes

- Check de CI detecta rota nova em `App.tsx` (ou equivalente) sem spec correspondente em `frontend/tests/e2e/` e falha o check dedicado/`qa-gate` apontando a rota e o spec esperado.
- Spec novo cobre desktop e mobile com snapshots versionados em `*-snapshots/` revisados no diff do PR.
- Dispensa só com label `qa-visual-skip` + comentário explícito de Alan (`QA visual dispensado por Alan.` + `Motivo:` não vazio).
- Evidência no run (artifacts de screenshot da tela nova) permanece disponível.
- `AGENTS.md`/`rules.md` passam a apontar o mecanismo automatizado, não a execução voluntária.
- Não cobre specs de protótipo estático (isso é #568).

## Capabilities

### New Capabilities

- `new-route-playwright-coverage`: detecção fail-closed de rota de app sem spec funcional+visual.

### Modified Capabilities

- `ci-testing-hardening`: `qa-gate` passa a exigir cobertura Playwright de rota nova.
- `delivery-qa-stage`: Done/QA não aceitam rota nova sem spec ou dispensa auditável.

## Impact

- Script/check de CI (inventário de rotas vs specs).
- `.github/workflows/ci.yml` (`qa-gate` ou job dedicado).
- `AGENTS.md` / `rules.md`.
- Baseline: rotas já existentes precisam de mapa explícito (allowlist da cobertura atual) para não quebrar o lote nas rotas antigas sem spec.
