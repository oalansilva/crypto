## Why

Hoje um diff pode sair de `Code Review` para integração sem uma evidência automatizada única de qualidade visual, testes e runtime. O Playwright é opt-in e limitado por paths, permitindo que mudanças de backend, operação ou documentação avancem sem a regressão visual padrão solicitada para todos os cards.

## What Changes

- Introduz o estágio operacional `QA` entre `Code Review` e `Done`, com ciclo explícito de retorno para correção quando houver falha.
- Define um `qa-gate` agregado que só aprova uma entrega quando todos os checks obrigatórios terminarem com sucesso.
- Torna a regressão visual Playwright obrigatória em todo card por padrão, inclusive quando não houver mudança em `frontend/**`.
- Permite dispensa somente mediante comentário explícito do Alan no card e label rastreável `qa-visual-skip`.
- Estabiliza seletores e fixtures obsoletos da suíte funcional Playwright para que o novo gate obrigatório tenha sinal confiável.
- Alinha a política global, regras locais, GitHub Project, CI, evidências e requisitos de runtime antes de `Done`.

## Capabilities

### New Capabilities

- `delivery-qa-stage`: Define o estágio QA, seus critérios de entrada/saída, o ciclo de falha e a evidência exigida antes do Done técnico.

### Modified Capabilities

- `ci-testing-hardening`: Amplia a CI para um gate agregado obrigatório e para regressão visual Playwright sempre habilitada, com artefatos e dispensa auditável.

## Impact

- GitHub Project 1: opções e documentação do campo `Status`, além do substatus `Fluxo`.
- Processo: skill global `alan-workflow`, `AGENTS.md` e `rules.md` do Cripto Farol.
- CI e QA: `.github/workflows/ci.yml`, scripts do frontend, configuração/especificações Playwright, estabilização dos testes funcionais existentes e política de artefatos.
- Runtime: validação PostgreSQL, integração em `develop`, `./restart` e smoke da URL antes de `Done`.
