## Context

Card [#854](https://github.com/oalansilva/crypto/issues/854) (processo/harness, frente Operação, P1). Briefing = issue. Q1–Q4=A, decididas por Alan — este Design não as reabre nem reentrevista.

Medido no #853: `design.md` ~3,3k palavras com detalhe de ORM; cada crítico reabriu um P0 novo de Apply; gate reprova rota de catálogo em card sem tela. Medido no #852: T5 rejeitou por falta de tokens parseáveis. Fatos: gate local existe (`scripts/process-fsm/design_clone_gate.py`); o body referencia `.agents/skills/design-critic/SKILL.md`, mas o canónico neste repo é `.cursor/skills/` e não há `design-critic` lá (decisão 4).

UI impact: none
live_route: N/A card de processo sem tela
surface: new

Harness/processo (skill + prompts + rubrica do gate). Sem rota, shell, copy ou HTML de produto.

## Goals / Non-Goals

**Goals:**

- Crítico isolado classifica: só produto/escopo/contrato visível gera P0/P1; detalhe de implementação é P3 aceito, resolvido no Apply (Q2=A).
- Teto sem-tela 1 autor + 1 crítico + 1 rework; com-tela autor + dupla + 1 rework; segundo rework só com P0 novo de produto justificado (Q1=A, Q3=A).
- Gate passa já no primeiro autor; nenhuma rodada extra só para o parser; crítico/dupla verifica tokens como item de rubrica.
- Regra no skill de crítica + prompts autocontidos do autor e do crítico, válidos nos clientes via MUST Read, sem fork.

**Non-Goals:**

- Pular/fundir colunas; fundir a dupla em UI com tela; desligar isolamento do crítico; afrouxar clone da página viva ou o gate; mudar effort (#673); serializar cards.
- Reabrir Q1–Q4. Máquina adivinhar `UI impact`/`surface` mentido em copy visível (segue skill/A/B). Criar ou editar skill neste Design (só no Apply).
- Auto-aplicar classificação/teto a este próprio Design de forma circular — a regra é apenas documentada aqui.

## Decisions

1. **Classificação (Q2=A).** Reprova (P0/P1): problema de produto, escopo ou contrato visível — tela, estados, acessibilidade, escopo furado. P3 "detalhe de Apply": detalhe de implementação (ORM, nomes internos, polish), registado como aceito em `design.md` e resolvido no Apply; o crítico não o reabre como P0/P1.
2. **Teto (Q1=A, Q3=A).** Sem-tela: 1+1+1. Com-tela: autor + dupla + 1 rework. Segundo rework só com P0 de produto novo justificado no prompt; fora disso o pai escreve a seção de crítica com os P3 aceitos e submete.
3. **Gate no primeiro autor.** Autor devolve artefatos já com tokens em linha própria parseável; sem-tela declara ausência + justificativa curta (Q4=A, nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. Crítico/dupla confere os tokens como item da rubrica; nada de rodada extra só para o parser.
4. **Onde mora a regra.** Apply cria `.cursor/skills/design-critic/SKILL.md` (canónico; skill nova — criação proibida neste Design, só no Apply) e atualiza a coluna Design de `.cursor/skills/covenant-flow/SKILL.md`, mais os prompts autocontidos do pai; tudo válido nos clientes via MUST Read, sem fork. Texto exacto a colar (vale para skill e prompts):

   > **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

5. **Máquina intacta.** `design_clone_gate.py`, `route-landmarks.yaml`, Σ YAML e T5 inalterados; este card passa como UI none harness (`N/A` justificado + `surface: new`, sem proto).

## Apply contract

- Apply cria `.cursor/skills/design-critic/SKILL.md` com o bloco D4; atualiza a coluna Design de `.cursor/skills/covenant-flow/SKILL.md` com o mesmo bloco; aplica os prompts do pai (path confirmado com Alan).
- MUST NOT neste card: `backend/`, `frontend/src/`, `scripts/process-fsm/*.py`, `.cursor/process-fsm.yaml`, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`, protótipo HTML, dual-write de lei em `.dsh/`/`.grok/`.
- Critério 4 do issue fecha quando classificação + teto + passo do gate estão no skill e nos prompts do autor e do crítico.

## Riscos / pontos abertos p/ Alan

- Skill-em-falta: confirmar que o Apply deve criar `.cursor/skills/design-critic/SKILL.md` (canónico) em vez de ressuscitar `.agents/skills/design-critic/SKILL.md`.
- Confirmar onde moram os "prompts autocontidos do pai" (spawns dsh/Cursor) antes do Apply os editar.
- Fronteira com #673 (emissão curta do crítico): este card trata classificação/teto/gate-no-autor e não duplica esforço — confirmar que basta referência.

## Design Critique

- **Veredito:** PASS — 1 autor + 1 crítico isolado, sem rework (nenhum P0/P1 de produto/escopo/contrato). Teto respeitado: sem-tela 1+1+1; com-tela manteria autor+dupla+1 rework.
- **Gate no autor:** `UI impact: none` (l.7) + `live_route: N/A card de processo sem tela` (l.8) + `surface: new` (l.9), linhas próprias parseáveis; sem protótipo HTML; `clone_gate_ok=True` já no primeiro autor (crítico re-verificou) — nenhuma rodada extra para parser.
- **Classificação (Q2=A):** só produto/escopo/contrato visível reprovaria; detalhe de implementação = P3 aceito. Crítico não reabriu P3 como P0/P1.
- **P3 aceitos (detalhe de Apply, publicado aqui e resolvido no Apply):** (a) path exacto dos prompts autocontidos do pai a confirmar com Alan; (b) confirmação canónica `.cursor/skills/design-critic/` vs `.agents/`; (c) fronteira sem-duplicação com #673.
- **Spawns:** 2 (1 autor + 1 crítico isolado; 0 rework). Prototype N/A.
