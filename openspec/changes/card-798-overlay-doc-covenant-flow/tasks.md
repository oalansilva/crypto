## 1. overlay_doc

- [x] 1.1 Em `docs/crypto-overlay.md`, retarget **toda** instrução de carga (path `.cursor/skills/alan-workflow*` e verbos `siga`/`seguir`/`carregue`/`use`/`aplique` + `alan-workflow*`) para `covenant-flow` / `covenant-flow-environments` segundo o mapeamento D5 do `design.md` (skill Cursor: `.cursor/skills/covenant-flow/SKILL.md`)
- [x] 1.2 Trocar o helper para `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`
- [x] 1.3 MUST NOT escrever nota formerly/avoid; MUST NOT editar `.covenant-flow/overlay.yaml`

## 2. rules.md

- [x] 2.1 Em `rules.md`, retarget as instruções de carga (path `.cursor/skills/alan-workflow/` e «Siga/aplique/execute/seguem `alan-workflow*`») para `covenant-flow` / `covenant-flow-environments` (D5)
- [x] 2.2 MUST NOT redefinir o papel de `rules.md` vs stub `AGENTS.md`; MUST NOT nota formerly/avoid

## 3. Cinzentos

- [x] 3.1 Em `docs/backlog-operating-model.md`, Visual QA aponta `covenant-flow` (não o path morto)
- [x] 3.2 No banner Hermes de `docs/analytics/funil-social-site-leads-plan.md`, nomes `covenant-flow` + `covenant-flow-environments`; aviso DEV por omissão / PROD só com pedido explícito permanece; MUST NOT apagar o banner

## 4. Verificação

- [x] 4.1 `rg -n 'alan-workflow' docs/crypto-overlay.md rules.md docs/backlog-operating-model.md docs/analytics/funil-social-site-leads-plan.md` devolve vazio
- [x] 4.2 Pasta `.cursor/skills/alan-workflow*` continua ausente; MUST NOT recriá-la
- [x] 4.3 Confirmar zero diff neste card em `AGENTS.md`, `.cursor/rules/harness.mdc`, `.covenant-flow/overlay.yaml`, `openspec/specs/**` main, `backend/`, `frontend/src/`, `frontend/public/prototypes/`
- [x] 4.4 `openspec validate --change card-798-overlay-doc-covenant-flow` verde; `UI impact: none` — zero HTML de protótipo
