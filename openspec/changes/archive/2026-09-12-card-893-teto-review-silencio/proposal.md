## Why

O teto de review já está escrito (#884 Pronto): um Apply de correção + uma onda; o resto era bloqueio visível. Na sessão #886 o pai transformou esse teto em pergunta («autorizar extra / aceitar residual»), parou o card em Code Review, misturou sinal determinístico com onda de juízo e patchou P1 no próprio transcript. Quem sofre é o Alan: o relógio pára até ele decidir no meio da coluna.

## What Changes

- Cada achado da onda sai classificado: **mecânico** (conserto óbvio, ficheiro/linha, abaixo de arquitectura/produto/aceite) vs **juízo** (muda desenho, aceite, ou é robustez fora do card) (Q1).
- Mecânicos da lista vão **juntos** a **um** Apply de correção, **sem pergunta**. Juízo **não** ocupa esse slot: vai logo para residual (Q1).
- Depois **uma** onda de verificação. P1 que restar **ou P1 novo** = residual visível no handoff de Done **e** no comentário do card. O card **segue** (commit, PR, QA). **Não** nasce terceiro ciclo. **Não** aparece pergunta «autorizar extra / aceitar residual». Alan vê o pacote uma vez na homologação (Q2).
- Sinal determinístico (inventário de teste, formatação, skip de ficheiro novo no check de QA) **não** reabre onda de review de juízo; o ajuste fica no Apply ou no QA até verde ou teto (Q3).
- Pai **não** patcha P1 no próprio transcript (já era lei no #884; prova = a sessão não mostra o pai a fechar P1 no chat).
- O número do teto do #884 **não muda**: 1 correção + 1 onda. Muda o sítio do residual: deixa de ficar preso em Code Review.
- Prova de Done = próxima sessão sem pergunta de teto e sem terceiro ciclo. Sem teste automático extra (mesmo Q1 do #884). Needles existentes MAY ser retunados se as strings se moverem (higiene, não aceite).
- App/UI não mudam.

**Não muda / não entra:** pingue-pongo spawn-por-task (#884 Pronto); destape máquina (#879); hang Desktop+SSH (#880); aresta FSM; pin; dual-write noutros clientes; `AGENTS.md` always-on a crescer; auto-merge / pular homologação; ciclar até «sem achados»; alargar o teto para 2–3 correções; produto Cripto.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs de harness/emissão/review já existentes. Este card não inventa coluna nem capability.

### Modified Capabilities

- `cursor-harness`: classificar mecânico vs juízo; mecânicos no único Apply de correção sem Ask; juízo vai a residual sem ocupar o slot; após 1 correção + 1 onda, P1 restante ou P1 novo = residual no Done e o card segue; pai MUST NOT Ask e MUST NOT self-patch; sinal determinístico de QA fica no Apply/QA, fora da onda de juízo; número do teto 1+1 intacto.
- `llm-flow-emission`: o que o pai **emite** — sem pergunta «autorizar extra / aceitar residual»; residual no handoff de Done e no comentário do card; o card continua (commit, PR, QA); não terceiro ciclo.
- `cursor-code-review`: happy path depois da onda de verificação é residual + continuar, não Ask e não terceiro ciclo; juízo não entra no Apply de correção.

## Impact

- Skill Cursor: `.cursor/skills/covenant-flow/SKILL.md` (Implementação / Code Review: classificar; mecânico sem Ask; juízo a residual; residual no Done; card segue; QA closeout: sinal determinístico não reabre onda de juízo). `openspec-apply-change` não descreve o sítio do residual — fora deste Apply salvo o Apply o achar necessário.
- Wording da **ordem** destape (`FOLLOWUP_REVIEW` / `FOLLOWUP_QA` em `scripts/process-fsm/subagent_stop.py`) **só** a cláusula de destino: hoje `FOLLOWUP_REVIEW` **não pergunta**, mas ainda manda «bloqueio visível» (#884). Q2 muda o sítio → residual no Done, card segue, MUST NOT «autorizar extra / aceitar residual». Matcher, sidecar, `loop_count`, classificação e poke ≠ `concluiu?` permanecem #879.
- Specs acima. Sem produto (`backend/` / UI). Sem `.cursor/process-fsm.yaml`. Sem pin novo. Sem dual-write `.dsh/` / `.grok/` / `.opencode/`.
- Needles **já existentes** em `scripts/process-fsm/test_*.py` MAY ser retunados se as strings do runbook/ordem se moverem. **Não** é aceite deste card.
- `UI impact: none`. Prototype N/A. Snapshot N/A.
