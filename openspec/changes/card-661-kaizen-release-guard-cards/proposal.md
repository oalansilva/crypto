## Why

O `release-guard post` só exige um heading canônico em `docs/kaizen-log.md`. Nos três lotes de 2026-08-21 o log passou, o `post` PASS e **zero** cards Kaizen nasceram em `Em Refinamento`, apesar do contrato (máx. 3/release). A skill `kaizen` é read-only e o orquestrador omitiu a materialização sem blocker. Card [#661](https://github.com/oalansilva/crypto/issues/661).

## What Changes

- `release-guard post` exige, para a data canônica, evidência de materialização Kaizen: (a) 1–3 issues novas com label `kaizen` listadas na tabela do log **ou** (b) dedupe auditável por linha `(não criado)` com `coberto por #N` onde `#N` ainda está em fluxo no Project 1 (não `Pronto`/`Cancelado`).
- Spec `kaizen-continuous-improvement`: criação de card em `Status=Em Refinamento` (não `Todo`); novo requirement do gate no `post`.
- Spec `release-worktree-hygiene`: o check de evidência kaizen do `post` inclui cards/dedupe, não só o heading.
- Skill `kaizen` / runbook: auditoria continua read-only; materializar cards (ou dedupe válido) é passo obrigatório do closeout **antes** do `post`.
- Testes de integração do `release-guard` cobrem PASS e FAIL.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `kaizen-continuous-improvement`: Status de criação = `Em Refinamento`; gate de cards/dedupe no fechamento de release.
- `release-worktree-hygiene`: evidência kaizen do `post` inclui materialização ou dedupe válido.

## Impact

- Altera `scripts/release-guard`, `backend/tests/integration/test_release_guard.py`, specs acima, `.cursor/skills/kaizen/SKILL.md` e trecho mínimo do runbook de release (`alan-workflow` / overlay só se necessário).
- Não toca `backend/` de produto, `frontend/src/`, deploy PROD nem `process_event`.
- `UI impact: none`. Prototype N/A.
- Origem: avaliação 2026-08-21 + issue #661.
