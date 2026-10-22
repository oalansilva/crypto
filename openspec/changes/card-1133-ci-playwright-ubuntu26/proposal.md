## Why

Desde 22/10/2026 o `ubuntu-latest` do GitHub Actions aponta para `ubuntu-26.04`, e o Playwright 1.58.2 travado no lockfile não instala o Chromium nesse sistema. O `e2e-playwright` aborta antes de rodar qualquer teste, o `qa-gate` fica vermelho em todo PR e nenhum card passa de QA para o T14.

O texto abaixo, de `## Problema` até `## Não entra`, é cópia integral do body do issue #1133 (lido por REST em 2026-10-22). O *como* está em `design.md`.

## Problema

Desde 22/10/2026, o `ubuntu-latest` do GitHub Actions passou a ser `ubuntu-26.04` (imagem `ubuntu26/20261021.171`). O job `e2e-playwright` do CI aborta no passo `npx --prefix frontend playwright install --with-deps chromium` com:

```
Cannot install dependencies for ubuntu26.04-x64 with Playwright 1.58.2!
Error: ERROR: Playwright does not support chromium on ubuntu26.04-x64
```

Os testes funcionais e visuais nem chegam a rodar, e o `qa-gate` fica vermelho em qualquer PR. O último CI verde em `develop` foi em 18/10 (`1a06caec`), antes da troca de imagem. Não é instabilidade: rodar o job de novo dá o mesmo erro.

## História

Como Alan, quero que o `e2e-playwright` volte a rodar no CI para que o `qa-gate` reflita os testes de verdade e os cards possam passar de QA para o T14.

## Entra

- [ ] Os testes de tela do CI, funcionais e visuais, voltam a instalar o navegador e a rodar até o fim em qualquer PR. Nenhum teste é pulado nem desligado para isso.
- [ ] A ferramenta de testes de tela sobe para uma versão que funciona no sistema novo do GitHub. A versão exata fica com o Design.
- [ ] As imagens de referência das telas são refeitas com a ferramenta nova. O Alan recebe uma comparação antes/depois de cada imagem refeita e aprova antes do merge. Imagem sem aprovação não entra.
- [ ] Todo o CI, e não só os testes de tela, roda numa versão fixa do sistema. Quando o GitHub trocar a versão padrão de novo, o CI continua no mesmo sistema e não quebra em silêncio. A versão a fixar fica com o Design.
- [ ] Verificação: o check final de QA do CI fica verde num PR deste card e, depois do rebase, no PR #1132 (#1117).

## Não entra

- Mudar o conteúdo das suítes e2e ou os critérios do `qa-gate`.
- Desligar o `e2e-playwright` ou o `qa-gate`.
- Trocar depois a versão fixa do sistema do CI. Cada troca futura é decisão do Alan, com card próprio.
- Mudar o que as telas mostram para que as imagens novas batam.

## What Changes

- `@playwright/test` sobe de `^1.58.2` para `1.64.1` exato em `frontend/package.json`, com `frontend/package-lock.json` regenerado (`@playwright/test`, `playwright` e `playwright-core` em 1.64.1; Chromium 156.0.8078.4).
- Os 15 jobs de `.github/workflows/ci.yml` trocam `runs-on: ubuntu-latest` por `runs-on: ubuntu-24.04`.
- Um teste de contrato em `backend/tests/contract/` falha se algum workflow em `.github/workflows/` usar runner diferente de `ubuntu-24.04` (inclui `ubuntu-latest`) ou se o `@playwright/test` deixar de ser versão exata igual à do lockfile.
- Novo workflow `.github/workflows/playwright-baselines.yml`, disparado pelo rótulo `regerar-baselines` no PR (ou manualmente), que refaz as 28 imagens de referência no runner fixado e publica um artefato com as imagens novas e a comparação antes/depois. Não grava no repositório e não entra no `qa-gate`.
- As 28 imagens de referência em `frontend/tests/e2e/*-snapshots/` são trocadas pelas geradas por esse workflow, depois da aprovação registrada de Alan no card.
- Sem mudança no conteúdo das suítes e2e, no `qa-gate`, no `maxDiffPixelRatio` nem em telas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `ci-testing-hardening`: passa a exigir runner fixo em todos os jobs, versão exata do Playwright suportada pelo runner fixado, e imagens de referência visuais geradas no runner do CI com aprovação registrada de Alan antes do merge.

## Impact

- CI: `.github/workflows/ci.yml` (só `runs-on`), novo `.github/workflows/playwright-baselines.yml`, rótulo de PR `regerar-baselines`.
- Frontend: `frontend/package.json`, `frontend/package-lock.json` e 28 PNG em `frontend/tests/e2e/*-snapshots/`. Nenhum código de produto.
- Backend: um teste de contrato novo em `backend/tests/contract/`. Nenhum código de produto.
- DEV (Ubuntu 24.04.4, arm64): o primeiro `npx playwright install chromium` depois do `npm ci` baixa o Chromium 1248. A imagem Docker do frontend (`node:20-alpine`) não instala navegador e só precisa de Node ≥ 20.
- Desbloqueia o PR #1132 (#1117) e os outros PRs abertos, depois do rebase.
