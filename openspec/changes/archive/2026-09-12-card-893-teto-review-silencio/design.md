## Context

Card [#893](https://github.com/oalansilva/crypto/issues/893) (kaizen, Operação, P1). Briefing = issue grelhado. Q1–Q3 fechadas — este Design não as reabre.

Facto: o teto **já** está escrito (#884 Pronto, `main` 2026-09-10): um Apply de correção + uma onda; resto P1/P2 = bloqueio visível com o card em Code Review; pai MUST NOT patchar no transcript. Checagens de *texto* dessa lei já existiam. O buraco não é o número do teto nem o spawn-por-task (#884 tapou): o pai **transforma o teto em pergunta** e pára a coluna.

Testemunha: sessão #886 (2026-09-10), depois do #884 em `main`, duas perguntas «autorizar Apply extra **ou** aceitar residual» (P1 evidência Hermes 5.3; depois P1 novo DEV↔bot PROD); sinal determinístico (inventário, formatação, skip de ficheiro novo) misturado com onda de juízo; pai patchou no próprio transcript. Alan: não quer ciclo infinito **e** não quer decidir no meio da coluna.

Este card **muda o sítio do residual** (Q2): deixa de ser «card parado em Code Review» e passa a residual no Done com o card a seguir. O número (1+1) **não** muda. Destape máquina (#879) e hang (#880) não entram.

UI impact: none
live_route: N/A harness-only; orquestração do pai Cursor (Code Review + QA closeout); no product route
surface: new

Harness-only: orquestração do pai Cursor (Code Review + QA closeout). Sem rota de produto, sem HTML, sem pasta de protótipos. Nunca `/monitor` `/favorites` `/combo/*` `landing`.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Classificar cada achado da onda: **mecânico** vs **juízo** (Q1).
- Mecânicos juntos num único Apply de correção **sem Ask**. Juízo vai logo a residual e **não** ocupa o slot (Q1).
- Depois 1 onda de verificação. P1 restante **ou P1 novo** = residual no handoff de Done **e** no comentário do card; o card **segue** (commit, PR, QA). Sem terceiro ciclo. Sem pergunta «autorizar extra / aceitar residual». Alan vê o pacote uma vez na homologação (Q2).
- Sinal determinístico (inventário, formatação, skip de ficheiro novo no qa-gate) não reabre onda de juízo; fica no Apply/QA até verde ou teto (Q3).
- Pai MUST NOT patchar P1 no próprio transcript.
- Prova de Done = próxima sessão sem Ask de teto e sem terceiro ciclo. Sem teste automático extra.

**Non-Goals:**

- Mudar o número do teto #884 (1 correção + 1 onda). Alargar para 2–3. Ciclar até «sem achados».
- Card parado em Code Review à espera do residual (Q2 rejeitou).
- Aresta FSM; pin; dual-write noutros clientes; `AGENTS.md` always-on a crescer; overlay `clients.*.auto`.
- Destape matcher / sidecar / `loop_count` / poke ≠ `concluiu?` (#879). Hang Desktop+SSH (#880). Spawn-por-task / reviewers em série (#884 Pronto).
- Auto-merge / pular homologação. Produto Cripto / UI. Pytest novo como aceite.

## Decisions

1. **Classificação no pai, não num reviewer novo (Q1).** Cada achado da onda sai **mecânico** (conserto óbvio: ficheiro/linha/instrução, gravidade abaixo de arquitectura/produto/aceite) ou **juízo** (muda desenho, aceite, ou é robustez fora do card). Só os mecânicos entram no único Apply de correção, juntos, **sem pergunta**. Juízo vai **logo** a residual e não ocupa o slot. P0 de reviewer continua bloqueio da coluna (não entra na lista de correção). P3 continua residual classificado.

   Rejeitado: segundo reviewer de classificação. Rejeitado: juízo a gastar o slot. Rejeitado: Ask «isto é mecânico?».

2. **Residual segue para Done; o card não pára (Q2).** Depois de 1 correção + 1 onda de verificação, P1 que restar **ou P1 novo** nessa onda = residual visível no handoff de Done **e** no comentário do card. O card **segue**: commit, fecho vs `develop` (uma onda, fora deste teto), PR, QA, T14. Pai MUST NOT spawnar terceiro ciclo. Pai MUST NOT perguntar «autorizar extra / aceitar residual». Alan vê achados + residual + SHA **uma vez** na homologação (T15). Homologar continua do Alan.

   Rejeitado: bloqueio visível com card preso em Code Review (#884 Q2 antigo; este card inverte o sítio). Rejeitado: Ask no chat. Rejeitado: o pai patchar no transcript.

3. **Destape: só destino, máquina #879 intacta.** `FOLLOWUP_REVIEW` **não pergunta** hoje; ainda manda «bloqueio visível, não terceiro ciclo» — o destino #884 que este card muda. Retunar **só** essa cláusula: residual no Done, card segue, MUST NOT «autorizar extra / aceitar residual»; classificar mecânico vs juízo antes de gastar o slot. `FOLLOWUP_QA`: sinal determinístico fica no Apply/QA; não reabrir onda de juízo. MUST NOT: matcher, sidecar, `loop_count`, classificação por `description` curta, goldens de destape como aceite.

   Rejeitado: deixar destape a ordenar «bloqueio visível» (contradiz Q2). Rejeitado: tratar o Ask como se estivesse no FOLLOWUP (o Ask é o pai LLM).

4. **Sinal determinístico fica no Apply/QA (Q3).** Inventário de teste, formatação (Black) e skip de ficheiro novo no check de QA são backpressure do Apply/QA até verde ou teto. MUST NOT reabrir onda de review de juízo (`diff-reviewer` + `code-reviewer` como se fossem P1 de desenho). Fecho pós-commit continua **uma** onda vs `develop` — não é esta onda de juízo.

   Rejeitado: misturar inventário com review de juízo (testemunha #886). Rejeitado: aresta FSM para este recorte.

5. **Sem pytest extra (mesmo Q1 do #884).** Specs + Apply contract descrevem runbook e o wording da ordem destape. Done = próxima sessão. Needles já existentes MAY ser retunados se as strings se moverem — higiene, não aceite, não teste novo.

   Rejeitado: `test_card_893_*` como aceite. Rejeitado: Guard a negar Ask (seria máquina nova).

6. **`openspec-apply-change` fora.** Esse skill descreve o loop do filho Apply-coluna (tasks/P0), não o sítio do residual nem o Ask. Não o editar salvo o Apply achar um needle partido.

## Prototype

N/A — card sem tela: orquestração do pai Cursor (Code Review + QA closeout), harness-only. Sem HTML, sem clonar rota de catálogo, sem `frontend/public/prototypes/`. Impeccable / Playwright / `DESIGN.md` = N/A justificado. Nunca emprestar `/monitor` `/favorites` `/combo/*` `landing`.

## Impeccable

N/A — sem superfície visual; não há pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana (Aprovação de Design → Pronto para Dev) permanecem.

## Apply contract

- Editar `.cursor/skills/covenant-flow/SKILL.md`:
  - Implementação / Code Review: classificar mecânico vs juízo; mecânicos → um Apply de correção **sem Ask**; juízo → residual (não ocupa o slot); após 1 correção + 1 onda, P1 restante ou P1 novo = residual no Done (handoff + comentário) e o card **segue**; MUST NOT perguntar «autorizar extra / aceitar residual»; MUST NOT terceiro ciclo; pai MUST NOT corrigir no próprio transcript; fecho pós-commit continua uma onda.
  - Prompts autocontidos: bloco curto «teto em silêncio» (classificar; 1+1; residual no Done; sem Ask).
  - QA closeout: sinal determinístico (inventário, formatação, skip de ficheiro novo) fica no Apply/QA até verde ou teto; MUST NOT reabrir onda de juízo.
- Retunar wording de destino em `FOLLOWUP_REVIEW` e `FOLLOWUP_QA` (`scripts/process-fsm/subagent_stop.py`). MUST NOT mudar matcher, sidecar, `loop_count`, classificação, nem perguntas `concluiu?`.
- `openspec-apply-change`: não editar salvo needle partido.
- Aplicar deltas OpenSpec `cursor-harness`, `llm-flow-emission`, `cursor-code-review`.
- MUST NOT: produto, `.cursor/process-fsm.yaml`, `AGENTS.md` always-on a crescer, overlay `clients.*.auto`, pin, dual-write `.dsh/` `.grok/` `.opencode/`, HTML de protótipo, `CONTEXT.md`, `docs/adr/`, teste automático extra como aceite.
- Needles existentes: só retune se as strings deste contrato as partirem. Não criar `test_card_893_*`.

## Risks / Trade-offs

- [Pai continua a ignorar texto e a perguntar] → três camadas visíveis (runbook + prompt autocontido + destape destino); prova = próxima sessão, não pytest.
- [Classificar mal: juízo tratado como mecânico] → residual no Done ainda apanha o que restar após 1+1; homologação vê o pacote. Não alargar o teto.
- [Classificar mal: mecânico tratado como juízo] → vai a residual sem gastar o slot; aceite Q1 (juízo não ocupa correção). Não Ask.
- [Destape wording vs #879] → só o texto de destino; máquina destape intocada.
- [FOLLOWUP_QA vs fecho vs develop] → Q3 não corta a onda de fecho pós-commit; corta reabrir juízo por inventário/Black/skip.
- [Needles `FOLLOWUP_*`] → retune mecânico no Apply, P3, não aceite.

## Migration / Rollout

1. Apply na branch do card (runbook + FOLLOWUP destino + deltas OpenSpec). Integração em `develop` no T14 habitual.
2. Sem pin, sem dual-write, sem HTML.
3. Rollback: reverter o SKILL + FOLLOWUP destino; specs voltam no archive do lote. Máquina destape #879 não entra no rollback.
4. Prova: próxima sessão de um card neste cliente sem Ask de teto e sem terceiro ciclo.

## Open Questions

Nenhuma. Q1–Q3 fechadas no issue. *Como* acima.

## Design Critique

Crítico isolado (sem-tela, 1 critic, inherit, sem transcript). Prototype: N/A justificado (`UI impact: none`). Teto 1+1+1: sem rework (zero P0/P1 de produto/escopo).

Token check:
- `UI impact: none` — linha própria.
- `live_route: N/A harness-only; orquestração do pai Cursor (Code Review + QA closeout); no product route` — ausência + justificativa; nunca `/monitor` `/favorites` `/combo/*` `landing`.
- `surface: new` — linha própria; isenta catálogo (par `live_route: N/A`).
- Prototype N/A justificado. Impeccable N/A justificado.

- **P0** — nenhum.
- **P1** — nenhum.
- **P3** (aceitos, Apply) — copy exacto de `FOLLOWUP_REVIEW` / `FOLLOWUP_QA` (só cláusula de destino; matcher/sidecar/`loop_count`/classificador/`concluiu?` ficam #879); onda só-juízo (sem Apply de correção, residual + segue, sem onda extra); Q3 «teto» ≠ pular Black/inventário no qa-gate (T14 continua verde; Q3 só proíbe reabrir onda de juízo); needles `FOLLOWUP_*` já existentes se as strings partirem.
- **Disposition:** D1–D6 honram Entra/não entra e Q1–Q3. Classificar mecânico vs juízo; 1 correção sem Ask; residual no Done (handoff + comentário), card segue, não preso em Code Review; sinal determinístico não reabre onda de juízo; sem terceiro ciclo; sem self-patch. Número do teto #884 (1+1) intacto. Máquina destape #879 intocada. Sem aresta FSM. Sem UI de produto.
- **Riscos não bloqueantes:** pai pode continuar a ignorar texto (prova = próxima sessão); classificação errada ainda cai no residual do Done e na homologação.

Design Agent verdict: PASS
