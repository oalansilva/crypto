## 1. FSM yaml

- [x] 1.1 Em `.cursor/process-fsm.yaml`: Σ + T18 `Done --nao_homologar, Alan, guard motivo_visivel--> Em desenvolvimento` (`set_status`); `enabled_events[Done] = [homologar, nao_homologar, cancelar]`; I2 inclui T18; stub Done nomeia T15/T18; `enabled_tools[Done]` permanece `[]`
- [x] 1.2 T15, T6/T7 e Homologado sem aresta inversa neste diff

## 2. evaluate + process_event

- [x] 2.1 `scripts/process-fsm/fsm.py`: `LEGAL_SIGMA` + `nao_homologar`; `EXPECTED_MATRIX` T18; `ALAN_GATES` T18; `EvalContext.motivo_visivel`; `NAMED_GUARDS` mapeia `motivo_visivel`
- [x] 2.2 `HUMAN_EVENTS` em `process_event.py` inclui `nao_homologar` (CLI Agent rejeita; mover não corre)

## 3. Testes

- [x] 3.1 `test_fsm.py`: T18 Alan + guarda true → Em desenvolvimento; guarda false/None → reject, fica Done; actor Agent → reject
- [x] 3.2 Validator falha se T18 omitir Alan; `test_process_event.py`: `nao_homologar` reject, mover vazio
- [x] 3.3 `pytest scripts/process-fsm -q` verde; testes MUST NOT chamar GitHub

## 4. Overlay / skill / always-on

- [x] 4.1 `docs/crypto-overlay.md`: não-regressão Done→Em desenvolvimento exceptua só T18 humano com motivo; Agent/archive/commit/PR/merge/closeout continuam proibidos
- [x] 4.2 Skill `covenant-flow` (gates humanos) e `github-project-board`: par homologar / não homologar em Done; destino Em desenvolvimento
- [x] 4.3 `AGENTS.md`: Alan-only inclui T18; MUST NOT dual-write lei em `.dsh/` nem `.grok/`

## 5. Fora de escopo

- [x] 5.1 Diff sem `backend/`, `frontend/src/`, HTML de protótipo, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`
- [x] 5.2 `openspec validate --change card-859-devolver-homologacao` verde; `UI impact: none` + `live_route: N/A` justificado + `surface: new`, sem proto dir
