## Why

O job `e2e-playwright` quebrou na push do #562 (harness, sem UI) porque `walkforward-prototype-check.spec.mjs` (e o spec do protótipo #463) fazem `page.goto('https://dev.criptofarol.com.br/prototypes/...')`. Se o frontend DEV está rebuildando, fora do ar ou atrasado, qualquer push falha com timeout de 30s numa URL externa. O spec de protótipo estático não deve depender do DEV vivo.

## What Changes

- Specs e2e de `frontend/public/prototypes/` passam a usar o webServer/preview do job Playwright (`PLAYWRIGHT_BASE_URL` / `http://127.0.0.1:4173`), nunca `https://dev.criptofarol.com.br`.
- Protótipo ausente no checkout falha de imediato (fail-closed), não com timeout de URL externa.
- Não alterar o contrato de QA visual versionado das telas do app.
- UI impact: none.

## Capabilities

### New Capabilities

- `prototype-e2e-local-preview`: e2e de protótipo estático usa preview local do CI e falha fechado se o HTML não estiver no checkout.

### Modified Capabilities

- `ci-testing-hardening`: testes automatizados de protótipo não dependem da URL viva de DEV.

## Impact

- `frontend/tests/e2e/walkforward-prototype-check.spec.mjs`
- `frontend/tests/e2e/card-463-prototype-gate.spec.ts`
- Possível ajuste de `package.json` / job `e2e-playwright` se o spec `.mjs` não passar pelo `webServer` do Playwright Test.
- Sem mudança de UI de produto.
