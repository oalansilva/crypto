Use project skills when applying: `.cursor/skills/openspec-apply-change`, `alan-workflow`. Apply só com `Status=Pronto para Dev`. Design-critic / Impeccable N/A (`UI impact: none`). Não editar `grilling` vendor, `grok_stubs.py`, stubs `.grok/skills/*`, nem `.cursor/process-fsm.yaml`.

## 1. Runbook (grill-card + alan-workflow)

- [x] 1.1 Update `.cursor/skills/grill-card/SKILL.md`: Q fechada → N≥2 alternativas reais em `options[]` da ferramenta do host (`AskUserQuestion` Cursor, `ask_user_question` Grok); recomendada primeiro com `(Recommended)`; Other não conta no N; Q aberta sem `options[]` fictícias; fallback Matt com escolhas no **corpo** e `➡️` só recomendação; filho devolve Qs com opções A/B/… listadas + recomendação (dump D5) e **não** chama a ferramenta do host; comentário canônico idempotente (não duplicar; texto exato = deixar; texto errado = editar/minimizar)
- [x] 1.2 Add **one line** to the Grill-card section of `.cursor/skills/alan-workflow/SKILL.md`: the parent calls the host tool with **all** closed-Q options and does not collapse to the recommended. Do not rewrite `.cursor/skills/grilling/SKILL.md`

## 2. Specs

- [x] 2.1 Apply spec deltas: `grill-card` (host options, open Q, fallback, dump filho→pai, comentário idempotente, vendor/stubs intactos) and minimum `cursor-harness` (parent relay line). Do **not** delta `process-harness` or the stub generator

## 3. Pytest needles (`scripts/process-fsm`)

- [x] 3.1 Extend `scripts/process-fsm/test_grill_card.py` (and/or add a sibling test file in that dir). Needles:
  - `AskUserQuestion` and `ask_user_question` in `.cursor/skills/grill-card/SKILL.md`
  - `N≥2` or `N>=2` in `grill-card`
  - `Other` does not count (`não conta` near `Other`) in `grill-card`
  - `.cursor/skills/grilling/SKILL.md` still contains `❓` and `➡️` and does **not** contain `AskUserQuestion` or `ask_user_question`
  - Grill-card section of `.cursor/skills/alan-workflow/SKILL.md` contains the relay line (`todas as options` / does not collapse)
  - `.grok/skills/grill-card/SKILL.md` and `.grok/skills/grilling/SKILL.md` do **not** contain `AskUserQuestion` or `ask_user_question`
- [x] 3.2 `pytest scripts/process-fsm -q` stays green. Do not treat a real Grok+Cursor session as a QA gate

## 4. Validate

- [x] 4.1 `openspec validate --change card-755-grilling-host-options --type change --strict`

## 5. UI none verify

- [x] 5.1 UI impact: none — no `frontend/src/`, no product `backend/`, no prototype HTML, no `.cursor/process-fsm.yaml`, no `scripts/process-fsm/grok_stubs.py`, no `.grok/skills/*` edits, `AGENTS.md` always-on unchanged
- [x] 5.2 Do not post another canonical comment on #755 (already has a premature one; idempotent rule). Homologation (Alan, not QA): real session on both clients confirms N≥2 on the host card
