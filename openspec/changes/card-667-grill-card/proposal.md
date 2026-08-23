## Why

Cards entram em Em Refinamento incompletos; o OpenSpec em Design reentrevista e amolece decisões. A fachada `grill-with-docs` do Matt grava `CONTEXT.md`/`docs/adr/` e não cabe na EFSM (T1 só Alan; artefato = issue). Precisamos de um adapter nosso que grelhe a história **no issue** antes do Todo, e de um OpenSpec que só sintetize.

Issue: [#667](https://github.com/oalansilva/crypto/issues/667).

## What Changes

- Skill de entrada **`grill-card`** (contrato local). Dispara o primitivo vendorado `grilling`. Despeja o DoD no body do GitHub. Comenta handoff T1. Não move Status. Não grava `CONTEXT.md` / `docs/adr/`. Não chama `/opsx:*`.
- Vendor **somente** `.cursor/skills/grilling/` (upstream mattpocock/skills, entrevista). Não vendor `grill-with-docs` nem o write de `domain-modeling`.
- Runbook: `alan-workflow` + texto de Em Refinamento em `github-project-board`.
- Stubs curtos de `context_file` (Em Refinamento / Todo / Design) em `.cursor/process-fsm.yaml`. **Não** muda `states` nem T0/T1.
- `openspec/config.yaml`: sintetizar do issue grelhado; proibido invocar grill na geração de `proposal.md`.
- Skills OpenSpec (`openspec-new-change` / `openspec-ff-change`): se o issue bound já tiver o DoD, não reentrevistar.

## Capabilities

### New Capabilities

- `grill-card`: porta de refinamento em Em Refinamento (bound_card, entrevista grilling, ledger = issue, handoff T1, proibições).

### Modified Capabilities

- `cursor-harness`: workflow skills incluem `grill-card` + `grilling`; Design sintetiza do issue; `implemente` continua wording; sem fachada Matt como porta.
- `process-fsm`: `context_file` de Em Refinamento/Todo/Design descreve o ritual; paging ≤20 linhas; T0/T1 inalterados.

## Impact

- Arquivos: `.cursor/skills/grill-card/`, `.cursor/skills/grilling/`, `.cursor/skills/alan-workflow/SKILL.md`, `.cursor/skills/github-project-board/SKILL.md`, `.cursor/process-fsm.yaml`, `openspec/config.yaml`, skills `openspec-new-change` / `openspec-ff-change`, specs acima, testes de paging/contexto se o texto do stub mudar.
- Sem `backend/`, `frontend/src/`, deploy, T1/T7/T15, coluna nova, `to-spec`, schema `grill-driven`.
- `UI impact: none`. Prototype N/A.
