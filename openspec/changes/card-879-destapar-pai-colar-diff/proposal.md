## Why

Na sessão Cursor o pai fica mudo depois do filho já ter acabado (Alan escreve `concluiu?` / `avance` — sintoma), e o Code Review improvisa sem o intervalo na mão (Ask mode bloqueia git; o filho lista transcripts). Incidente #876 / PR #878: ~49 min entre `turn_ended` do filho e o push do pai; reviewer sem diff colado.

Rework Design (Alan 2026-09-09, mesmo card): o hang repetiu-se nesta sessão de Design. Autor `4bc9a67b` 20:09–20:18 `completed` OK; crítico `dfbef63a` 20:18:50–20:44:52 UTC `turn_ended aborted` (o `concluiu?` do user matou o Task). Recorte aceite: destapar também filhos de Design quando `status=completed` e o pai ainda espera o mesmo Task. Este aborto de 27 min **não** ganha destape — o filho não completed. Q1/Q2/S1 não reabrem.

## What Changes

- **S1 — só Code Review:** o pai materializa o intervalo (HEAD vs uncommitted; depois `origin/develop...HEAD`) e entrega-o no prompt e/ou num ficheiro que o filho só lê. O reviewer `readonly` conclui sem git e sem listar transcripts. Sem intervalo: falha visível `ERROR: review-diff missing` e o review pára.
- **S2 — quatro etapas Cursor (grelha, Apply, Code Review, QA) e filhos de Design (autor, crítico sem-tela, Assessment A/B):** hook `subagentStop` injecta `followup_message` com **ordem de concluir a etapa** quando o filho já acabou (`status=completed`) e o pai ainda espera o mesmo Task. Não pergunta `concluiu?`. Não destapa filho ainda a trabalhar, nem `error`/`aborted`, nem background. Design-autor completed → spawn crítico/dupla; crítico/A/B completed → pai escreve `## Design Critique`, publica o Gist e chama `submeter_design`.
- Agentes `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` passam a recusar git e transcripts no corpo.
- Runbook `covenant-flow` (consumidor, sem pin novo) descreve colar o diff e o poke-como-ordem.
- Goldens pytest do adapter Cursor (hooks.json + script de destape + agentes). Overlay `clients.*.auto: false` intacto. `AGENTS.md` always-on não cresce.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `cursor-code-review`: spawn autocontido exige intervalo já materializado pelo pai; filho MUST NOT git / MUST NOT listar transcripts; sem intervalo → `ERROR: review-diff missing` e pára.
- `cursor-harness`: `.cursor/hooks.json` regista `subagentStop` (não `subagentStart`) com `followup_message` de ordem, `loop_limit` alto o bastante para Design+Apply+reviews+QA no mesmo chat `#id`; runbook Cursor documenta destape das quatro etapas, dos filhos de Design e o contrato S1 do pai. O classificador do destape vive neste adapter (`subagent_stop.py`), não em `llm-flow-emission`.
- `llm-flow-emission`: o prompt dos reviewers é o ficheiro versionado **mais** o intervalo colado (path e/ou bytes); MUST NOT herdar git-fetch nem transcripts do pai.

## Impact

- Apply (após Pronto para Dev), só harness Cursor: `.cursor/hooks.json`, novo adapter `.cursor/hooks/process-fsm-subagent-stop.sh` + módulo Python testável em `scripts/process-fsm/`, `.cursor/agents/{diff,code}-reviewer.md`, `.cursor/skills/covenant-flow/SKILL.md`, testes `scripts/process-fsm/test_*.py`, deltas OpenSpec acima.
- MUST NOT: `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml` (sem aresta nova), dual-write T0–T17 em `.dsh/` / `.grok/`, pin `covenant-flow` (fica `v1.1.14`), overlay `clients.*.auto`, `AGENTS.md` always-on, produto #876, QA dsh #858, Bugbot, reviewer Write, `subagentStart`, destape em `aborted`.
- `UI impact: none`. Prototype N/A. Snapshot N/A. Clientes Grok/OpenCode/dsh fora do Entra.
- Origem: issue #879 (grelha fechada; Q1 automático, Q2 falha visível, Q3 revogada → quatro etapas; destape = ordem) + recorte Design no mesmo card. S2 não substitui S1.
