## 1. Skill de crítica (só no Apply, após Pronto para Dev)

- [ ] 1.1 Criar `.cursor/skills/design-critic/SKILL.md` (canónico; path confirmado com Alan) com classificação P0/P1 vs P3, teto 1+1+1 / autor+dupla+1 rework, e passo do gate no autor — colar o bloco exacto D4 do `design.md`
- [ ] 1.2 MUST NOT criar nem editar skill neste Design; MUST NOT ressuscitar `.agents/skills/` como canónico sem confirmação do Alan

## 2. Runbook + prompts do pai

- [ ] 2.1 Na coluna Design de `.cursor/skills/covenant-flow/SKILL.md`, colar o mesmo bloco D4 (dsh lê o runbook canónico; MUST NOT dual-write lei em `.dsh/` nem `.grok/`)
- [ ] 2.2 Aplicar classificação + teto + passo do gate aos prompts autocontidos do autor e do crítico (paths confirmados com Alan), válidos nos clientes via MUST Read, sem fork

## 3. Fora de escopo (confirmação)

- [ ] 3.1 Diff deste card sem `backend/`, `frontend/src/`, `scripts/process-fsm/*.py`, `.cursor/process-fsm.yaml` Σ, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`, protótipo HTML
- [ ] 3.2 `openspec validate --change card-854-design-teto-gate` verde; `UI impact: none` + `live_route: N/A` justificado + `surface: new`, sem proto dir → gate local True
