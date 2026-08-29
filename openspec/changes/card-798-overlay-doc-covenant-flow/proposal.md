## Why

Agente cooperativo (dsh e qualquer cliente que `Read` docs vivos de carga) segue o path concreto `alan-workflow` e toma OUT vermelho (`FsError` / `FS_NOT_FOUND`), mesmo com o runbook certo já no git, no catálogo dsh e no stub `AGENTS.md`. Card [#798](https://github.com/oalansilva/crypto/issues/798). Pin `v1.1.4` não reescreve `overlay_doc`; o furo vive nos Markdown humanos.

## What Changes

- Reescrever **toda instrução de carga** nos quatro docs vivos deste consumidor para `covenant-flow` / `covenant-flow-environments` (paths sob `.cursor/skills/alan-workflow*` e verbos `siga`/`seguir`/`carregue`/`use`/`aplique` + `alan-workflow*`).
- Helper de Gist → `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`.
- Zero token `alan-workflow` nos 4 ficheiros; zero notas formerly/avoid.
- Banner do funil: só retarget dos nomes de skill; aviso DEV por omissão / PROD só com pedido explícito permanece.
- Não é **BREAKING**: pin, yaml, stub `AGENTS.md`, peles, produto `covenant-flow` e AND «formerly» das specs main de #773 permanecem.

## Capabilities

### New Capabilities

- `consumer-load-docs`: docs vivos de carga deste consumidor (`overlay_doc` `docs/crypto-overlay.md`, `rules.md`, `docs/backlog-operating-model.md`, banner em `docs/analytics/funil-social-site-leads-plan.md`) apontam só `covenant-flow` / `covenant-flow-environments`; helper no path pinado; `rg` vazio nos 4.

### Modified Capabilities

- (nenhuma) — não reescrever `openspec/specs/covenant-flow` nem AND «formerly» de pin (#773 Pronto). `cursor-harness` já exige nomes novos no git pinado; este card cobre o Markdown humano que `--pin` não toca.

## Impact

- Altera (Apply, após Pronto para Dev), só consumidor `oalansilva/crypto`: `docs/crypto-overlay.md`, `rules.md`, `docs/backlog-operating-model.md`, `docs/analytics/funil-social-site-leads-plan.md`.
- Não toca `.covenant-flow/overlay.yaml`, `AGENTS.md`, `.cursor/rules/harness.mdc`, peles `.dsh`/`.grok`/`.opencode`, produto `oalansilva/covenant-flow`, alias git `alan-workflow*`, host `~/.cursor/skills/alan-workflow*`, histórico `docs/release-*`/`decision-log`/palestra/archive, `openspec/specs/**` main, `backend/` / `frontend/src/`.
- Não relança dsh. Não reabre #773/#554/#786/#784. Não absorve #780.
- `UI impact: none`. Prototype N/A. Snapshot N/A. Sem HTML.
- Origem: issue #798 (DoD grelhado; Q1=B, Q2=A, Q3=A, Q4=A). Relacionado e **não** reaberto: #773 Pronto; #786/#784 Done; #554 Pronto; #780 Em Refinamento.
