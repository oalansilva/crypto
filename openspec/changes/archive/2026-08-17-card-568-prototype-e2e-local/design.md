## Context

`walkforward-prototype-check.spec.mjs` e `card-463-prototype-gate.spec.ts` abrem `https://dev.criptofarol.com.br/prototypes/...`. O job Playwright já sobe preview em `127.0.0.1:4173`. Push de harness quebra quando DEV está rebuildando.

## Goals / Non-Goals

**Goals:**
- Specs de protótipo usam `PLAYWRIGHT_BASE_URL` / origin do webServer.
- Fail-closed se o HTML não existe no checkout.
- Job `e2e-playwright` independente do DEV vivo.

**Non-Goals:**
- Mudar baselines visuais do app (#529 é rotas do app).
- Publicar/retirar protótipos.

## Decisions

1. **Mesmo origin do Playwright Test.** Converter o `.mjs` solto para o runner (`baseURL`) ou injetar origin via env já usada pelo job. Preferência: spec no Playwright Test com `page.goto('/prototypes/walk-forward-gate/')`.
2. **Assert de fixture.** `fs.existsSync` do `index.html` antes do goto; falha com path, não timeout.
3. **UI impact: none.**

## UI impact

`none` — só alvo do e2e de HTML estático.

## Prototype

N/A. Justificativa: não há tela nova; o HTML de walk-forward já existe e não é redesenhado.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Vite dev em 4173 não servir `public/prototypes`] → Conferir no apply; se o job já usa `npm run dev`, `public/` já é servido. Fallback: `vite preview` após build, ainda local.
- [Spec `.mjs` fora do config] → Migrar para `*.spec.ts` no `testDir` para herdar webServer.

## Migration Plan

1. OpenSpec + aprovação.
2. Retarget specs; assert de arquivo; CI local smoke.
3. QA visual do app inalterada.

## Open Questions

Nenhuma.

## Design Critique

- Escopo: retarget de e2e de HTML estático para preview local.
- Crítica isolada: PASS. Visual do app inalterado.
- Superfície visual nova: nenhuma.

## Prototype Validation

N/A — sem protótipo novo. O HTML de walk-forward/463 não é redesenhado.

Design Agent verdict: PASS
