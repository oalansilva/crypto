## Why

Alan espera 45–50 min por card para ver um Design aprovável; a maior parte do turno do pai vai para rodadas extras de autor/crítico que discutem detalhe de implementação (não decisão de produto) e para rodadas que nascem só para satisfazer o parser do gate. Evidência (sessões dsh 2026-09-06): #853 (sem tela) — pai 47 min, 9 filhos em série (5 autores + 4 críticos), cada crítico reabriu um P0 novo de Apply, `design.md` ~3,3k palavras sem seção de crítica; #852 (com tela) — pai 49 min, T5 rejeitou por falta de tokens parseáveis, 6º filho só para isso.

## What Changes

- O crítico classifica achados: só produto/escopo/contrato visível reprova (P0/P1); detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply.
- Teto de rodadas: sem-tela fecha em 1 autor + 1 crítico + 1 rework; com tela mantém autor + dupla + 1 rework; segundo rework só com P0 de produto novo justificado.
- O primeiro autor já entrega o gate satisfeito (tokens parseáveis; sem-tela declara ausência + justificativa; com-tela marca só regiões clonadas); nenhuma rodada extra nasce só para o parser.
- Classificação, teto e passo do gate vão para o skill de crítica e para os prompts autocontidos do autor e do crítico, válidos nos clientes via MUST Read, sem fork.
- Nenhuma mudança de máquina: gate Python e Σ YAML intactos; sem pulo/fusão de colunas, sem fundir a dupla, sem desligar isolamento, sem afrouxar clone ou gate.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `llm-flow-emission`: crítica do crítico emite classificação P0/P1 (produto/escopo/contrato) vs P3 (detalhe de Apply aceito); teto de rodadas e passo do gate entram nos prompts autocontidos do autor e do crítico; sem-tela publica seção de crítica com P3 aceitos quando não há P0 novo.
- `design-route-clone-gate`: rubrica do crítico/dupla verifica tokens parseáveis como item próprio (sem-tela = ausência declarada + justificativa, nunca rota de catálogo emprestada; com-tela = marcações só nas regiões clonadas); comportamento de máquina inalterado.

## Impact

- Apply (após Pronto para Dev), só harness: novo `.cursor/skills/design-critic/SKILL.md`, coluna Design de `.cursor/skills/covenant-flow/SKILL.md`, textos dos prompts do pai (path a confirmar — ponto aberto), deltas OpenSpec das capabilities acima.
- Não toca `backend/`, `frontend/src/`, `scripts/process-fsm/*.py`, `.cursor/process-fsm.yaml` Σ, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`, protótipos live.
- `UI impact: none`. Prototype N/A. Snapshot N/A. Sem HTML de produto deste card.
- Origem: issue #854 (Q1–Q4=A, decididas por Alan; este Design não as reabre). Dependência sem duplicação: #673 (emissão curta do crítico).
