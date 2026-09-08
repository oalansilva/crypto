## Why

Em Done, Alan só consegue homologar ou cancelar. Recusar a homologação e devolver o **mesmo** card para correção não existe — testemunha #852: a entrega em DEV saiu diferente do protótipo e a sessão respondeu que Done não volta. Sem este gesto, o único par em Done é avançar ou matar o card.

## What Changes

- Em Done, Alan passa a ter o par **homologar** ou **não homologar** / devolver o mesmo card (não cancelar, não issue nova).
- Não homologar, com motivo visível no card, devolve o item para **Em desenvolvimento**. Destino fixo; não QA, não Design.
- Sem motivo visível no card, a recusa **não conta**: o card permanece em Done.
- Depois da correção, o card segue o caminho já existente até Done; o par homologar / não homologar volta a aparecer. Não fica homologado por ter estado em Done antes.
- Só Alan homologa e só Alan não-homologa. `process_event` rejeita os dois se o actor for Agent.
- Overlay anti-regressão Done→Em desenvolvimento fura **apenas** neste gesto humano — não no agente, não em archive/commit/PR/merge/closeout.
- **Não muda:** Aprovação de Design (devolver/aprovar), priorizar, desfazer Homologado, produto #852, frontend/backend de produto.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `process-fsm`: Σ ganha o evento humano `nao_homologar`; aresta T18 Done → Em desenvolvimento, actor Alan, guarda `motivo_visivel`; `enabled_events[Done]` inclui o evento; I2 passa a listar T18 como Alan-only.
- `process-fsm-event`: `nao_homologar` entra nos eventos humanos; `process_event()` rejeita (mover não corre) tal como `homologar` / `devolver_design`.

## Impact

- Apply (após Pronto para Dev): `.cursor/process-fsm.yaml`, `scripts/process-fsm/` (Σ, evaluate, HUMAN_EVENTS, testes), stub Moore de Done, skill `covenant-flow` / `github-project-board`, `AGENTS.md` (Alan-only inclui T18), parágrafo de não-regressão em `docs/crypto-overlay.md`.
- MUST NOT: `backend/`, `frontend/src/`, HTML de protótipo, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`, dual-write de lei em `.dsh/` / `.grok/`.
- `UI impact: none`. Prototype N/A. Snapshot N/A.
- Origem: issue #859 (grelha 2026-09-07, q1–q4=A). Não reabre recorte, destino, motivo obrigatório nem Homologado já promovido.
