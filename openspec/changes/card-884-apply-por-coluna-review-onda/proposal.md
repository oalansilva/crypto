## Why

O runbook já manda um filho Apply por entrada em Em desenvolvimento (loop fatiado interno) e Code Review em onda. Na sessão #879 o pai ignorou isso e fez Apply → review → Apply → review em série (~71 min, 4 Apply + 5 reviews). Quem sofre é o Alan / a sessão: o relógio é a soma, não o mais lento. Este change torna esse tecto **visível na sessão** (prompts, recusa, bloqueio) sem inventar coluna nem teste automático extra.

Issue: [#884](https://github.com/oalansilva/crypto/issues/884). Testemunha: sessão #879 2026-09-09, pai `25d57e12`.

## What Changes

- Na entrada em Em desenvolvimento: **um** filho Apply até as tasks feitas ou um P0 visível. O filho não devolve o turno ao pai entre tasks. Não um spawn por task.
- Recusa visível se o Apply devolver cedo sem P0 e sem tasks feitas: o pai **não** abre review nem um segundo Apply.
- Na coluna Code Review: os **dois** reviewers nascem no **mesmo turno** do pai (dois Task na mesma mensagem), ambos sobre o intervalo já colado. Fila do host **não** falha (Q3).
- Achados P1/P2 voltam **juntos numa lista** a **no máximo um** Apply de correção por coluna; depois **uma** onda. Resto P1/P2 = bloqueio visível; **não** terceiro ciclo (Q2).
- P3 / detalhe de implementação continua aceite no Design e resolvido no Apply (teto 1+1+1 já escrito).
- Fecho depois do commit continua **uma** onda; não é o pingue-pongue deste card.
- Prova de Done = a **próxima sessão**: o pai não repetir Apply e review. Sem teste automático extra (Q1).
- Barra intocável (Q4): grelha, crítico, intervalo colado, os dois reviewers, QA nos checks. Não há mais.

**Não muda:** aresta FSM; produto Cripto; Gmail/boot; destape máquina (#879); hang/Desktop+SSH (#880); pin/dual-write noutros clientes; `AGENTS.md` always-on.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs de harness/emissão/review já existentes. Este card não inventa coluna.

### Modified Capabilities

- `cursor-harness`: tecto de um Apply por coluna (loop interno até done/P0); recusa se devolver cedo; onda dos dois reviewers no mesmo turno do pai; um ciclo de correção + bloqueio visível; sem aresta FSM.
- `llm-flow-emission`: o que o pai **emite** na sessão — dois Task no mesmo turno; lista de correção num único spawn; mensagem de bloqueio visível ao operador; destape continua poke/ordem (#879) mas **não** nasce o segundo reviewer nem o segundo Apply.
- `cursor-code-review`: happy path deixa de ser «sessão principal corrige e re-corre o reviewer afectado»; passa a ser onda no mesmo turno + no máximo um Apply de correção com a lista + uma onda; resto P1/P2 = bloqueio visível.

## Impact

- Skills Cursor: `.cursor/skills/covenant-flow/SKILL.md` (tabela de filhos, Implementação, linha sequencial do destape), `.cursor/skills/openspec-apply-change/SKILL.md` (pause entre tasks).
- Wording da **ordem** destape (`FOLLOWUP_APPLY` / `FOLLOWUP_REVIEW` em `scripts/process-fsm/subagent_stop.py`) se o Apply o escolher — máquina destape (matcher, sidecar, `loop_count`, poke ≠ `concluiu?`) permanece #879.
- Specs acima. Sem produto (`backend/` / UI). Sem `.cursor/process-fsm.yaml`. Sem pin novo. Sem dual-write `.dsh/`.
- Needles **já existentes** em `scripts/process-fsm/test_*.py` MAY ser retunados se as strings do runbook/ordem se moverem. **Não** é aceite deste card (Q1).
- `UI impact: none`. Prototype N/A. Snapshot N/A.
