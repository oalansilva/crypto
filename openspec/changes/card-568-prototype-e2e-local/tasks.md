## 1. Specs de protótipo

- [x] 1.1 Fazer `walkforward-prototype-check` usar o origin do Playwright (`/prototypes/walk-forward-gate/`), não `dev.criptofarol.com.br`
- [x] 1.2 Fazer `card-463-prototype-gate` usar o mesmo origin local
- [x] 1.3 Fail-closed se o `index.html` do protótipo não existir no checkout

## 2. CI

- [x] 2.1 Garantir que o job `e2e-playwright` executa esses specs via webServer/preview (migrar `.mjs` para o runner se preciso)
- [x] 2.2 Confirmar que `test:e2e:visual` do app permanece no baseURL local

## 3. QA

- [x] 3.1 Rodar o spec de walk-forward contra preview local
- [x] 3.2 QA visual obrigatória (baseline inalterada)
