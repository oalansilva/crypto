## Context

Card [#884](https://github.com/oalansilva/crypto/issues/884) (kaizen, Operação, P1). Briefing = issue grelhado. Q1–Q4 fechadas — este Design não as reabre.

Facto: o runbook **já** diz 1 filho Apply (loop fatiado interno) e Code Review = onda (`covenant-flow` tabela de filhos; `openspec-apply-change` «One child per Em desenvolvimento column»). Specs `cursor-harness` / `llm-flow-emission` já falam em filho-coluna e dual-reviewer wave. Checagens de *texto* dessa lei já existiam no dia do incidente e teriam passado. O buraco não é lei em falta: o pai **ignorou** o que se via mal na sessão.

Testemunha: sessão #879 2026-09-09, pai `25d57e12`, 4 Apply + 5 reviews em série, ~71 min. Soma `durationMs` ~139 s (host não preso em I/O). Destape `concluiu?` desse dia = #879; hang Desktop+SSH = #880 — não entram.

Três fios no código que **empurram** a série mesmo com a lei escrita:

1. `openspec-apply-change` manda **Pause** se a task for pouco clara e devolver o turno ao pai entre tasks.
2. `covenant-flow` Destape S2: «Após destape de `diff-reviewer`, o pai spawna `code-reviewer`» — o segundo reviewer nasce **tarde**. Sidecar único `.cursor/tmp/awaiting-task.json` (#879) reforça a série.
3. `cursor-code-review`: «The primary session SHALL fix … then re-run the affected reviewer when the uncommitted diff changed» — pingue-pongue por achado. `FOLLOWUP_REVIEW` ainda diz «Segue commit» depois de *um* reviewer.

UI impact: none
live_route: N/A harness-only; orquestração do pai Cursor (Apply + Code Review); no product route
surface: new

Harness-only: orquestração do pai Cursor (Apply + Code Review). Sem rota de produto, sem HTML, sem pasta de protótipos. Nunca `/monitor` `/favorites` `/combo/*` `landing`.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Sessão: um Apply por coluna até tasks feitas ou P0 visível; sem spawn por task.
- Sessão: onda = dois Task no mesmo turno do pai; relógio = o mais lento; fila do host não falha (Q3).
- Sessão: no máximo um Apply de correção com a lista P1/P2 + uma onda; resto = bloqueio visível (Q2).
- Prova de Done = próxima sessão sem pingue-pongue (Q1). Barra Q4 intacta.

**Non-Goals:**

- Aresta FSM; agente a arrastar T1/T7/T15/T18; coluna nova.
- Pytest novo como aceite (Q1). Tratar checagem de texto da lei como se tivesse apanhado o incidente.
- Gmail/boot; destape/`concluiu?` (#879); hang/Desktop+SSH/Landlock (#880).
- Produto Cripto; pin/dual-write noutros clientes; `AGENTS.md` always-on a crescer; overlay `clients.*.auto`.
- Cortar grelha, crítico, intervalo colado, os dois reviewers ou QA nos checks (Q4).
- Exigir paralelismo real do host; terceiro ciclo Apply+review.

## Decisions

1. **Como o pai deixa de pingue-pongar (lei já escrita).** Camada visível, sem δ: (a) prompt autocontido do filho Apply — «és o único Apply desta coluna; loop até done ou P0 visível; não devolvas entre tasks»; (b) recusa visível se devolver cedo sem P0 — destape **não** autoriza review nem segundo Apply; (c) tecto no spawn do pai — 1 Apply inicial + no máximo 1 de correção por coluna. O Apply skill deixa de tratar «Pause / ask parent» como happy path entre tasks (P0 visível continua a parar a coluna).

   Rejeitado: pytest novo / Guard a negar o N-ésimo spawn (Q1; e seria aresta). Rejeitado: só «sublinhar o runbook» — no dia do incidente o texto já estava lá. Rejeitado: o filho Apply spawnar reviewers (nested, #729).

2. **Como nasce a onda no mesmo turno (Q3).** O pai emite **dois** Task na **mesma** mensagem de assistente (`diff-reviewer` + `code-reviewer`), ambos com o intervalo já colado. Fila do host é aceite; o relógio que conta é o do mais lento. Sidecar destape permanece **um** ficheiro (#879): o pai **não** espera destape do primeiro para nascer o segundo. Destape do primeiro = espera o par / não commita / não duplica o segundo.

   Rejeitado: exigir `run_in_background` + paralelismo real (Q3). Rejeitado: dois sidecars / mudar matcher destape (reabre #879). Rejeitado: manter «Após destape de `diff-reviewer`, o pai spawna `code-reviewer`» — é exactamente a série da testemunha.

3. **Como o bloqueio visível após 1 ciclo de correção.** Depois de 1 Apply com a lista + 1 onda, P1/P2 que restarem = mensagem ao operador no chat (e handoff), card fica na coluna Code Review. Não há terceira coluna, não há T18, não há evento novo. Pai MUST NOT corrigir no próprio transcript.

   Rejeitado: «re-run the affected reviewer» por achado (`cursor-code-review` actual). Rejeitado: o pai patchar. Fecho pós-commit continua **uma** onda — fora deste pingue-pongue.

4. **Sem pytest extra (Q1).** Specs + Apply contract descrevem runbook, prompts autocontidos e o *wording* da ordem destape. Done = próxima sessão. Needles **já existentes** (`test_card_729_activity_children.py`, `test_subagent_stop.py` constantes `FOLLOWUP_*`) MAY ser retunados se as strings se moverem — higiene, não aceite, não C1–C8 novos.

   Wording destape (máquina intacta: matcher, sidecar, `loop_count`, poke ≠ `concluiu?`): `FOLLOWUP_APPLY` deixa de mandar review se o filho devolveu cedo; se tasks feitas ou P0, manda a **onda no mesmo turno** e «não spawnes outro Apply». `FOLLOWUP_REVIEW` deixa de mandar commit após *um* reviewer: espera o par; se os dois devolveram com P1/P2 → um Apply com a lista; se limpo → commit; nunca nascer o outro reviewer agora.

## Prototype

N/A — card sem tela: orquestração do pai Cursor (Apply + Code Review), harness-only. Sem HTML, sem clonar rota de catálogo, sem `frontend/public/prototypes/`. Impeccable / Playwright / `DESIGN.md` = N/A justificado.

## Apply contract

- Editar `.cursor/skills/covenant-flow/SKILL.md`: tabela Em desenvolvimento / Code Review; Implementação; apagar a linha sequencial «Após destape de `diff-reviewer`, o pai spawna `code-reviewer`»; prompts autocontidos (tecto, recusa, onda no mesmo turno, lista, bloqueio visível).
- Editar `.cursor/skills/openspec-apply-change/SKILL.md`: loop até done ou P0; pause entre tasks **não** devolve ao pai; continua MUST NOT reviewers / `process_event` / commit.
- Retunar `FOLLOWUP_APPLY` e `FOLLOWUP_REVIEW` em `scripts/process-fsm/subagent_stop.py` (wording da ordem). MUST NOT mudar matcher, sidecar, `loop_count`, classificação, nem perguntas `concluiu?`.
- Aplicar deltas OpenSpec `cursor-harness`, `llm-flow-emission`, `cursor-code-review`.
- MUST NOT: produto, `.cursor/process-fsm.yaml`, `AGENTS.md` always-on a crescer, overlay `clients.*.auto`, pin, dual-write `.dsh/`, HTML de protótipo, `CONTEXT.md`, `docs/adr/`, teste automático extra como aceite.
- Needles existentes: só retune se as strings deste contrato as partirem. Não criar `test_card_884_*`.

## Risks / Trade-offs

- [Pai continua a ignorar texto] → três camadas visíveis (prompt + recusa + tecto) e destape *wording*; prova = próxima sessão, não pytest (Q1).
- [Destape wording vs #879] → só o texto da ordem; máquina destape intocada. Residual: sidecar único não destapa os dois ao mesmo tempo — aceite (Q3 fila).
- [FOLLOWUP_APPLY dispara com Apply incompleto] → recusa visível; não abrir review.
- [Fecho vs develop confundido com pingue-pongue] → fecho permanece uma onda, fora do tecto de correção pré-commit.
- [Needles `FOLLOWUP_*` / #729] → retune mecânico no Apply, P3, não aceite.

## Open Questions

Nenhuma. Q1–Q4 fechadas no issue. *Como* acima.

## Design Critique

Crítico isolado (sem-tela, 1 critic, inherit, sem transcript). Snapshot: `.impeccable/critique/884-card-884-apply-por-coluna-review-onda.md`. Prototype: N/A justificado (`UI impact: none`). Teto 1+1+1: sem rework (zero P0/P1).

- **P0** — nenhum.
- **P1** — nenhum.
- **P3** (aceitos, Apply) — copy exacto de `FOLLOWUP_APPLY` / `FOLLOWUP_REVIEW`; sidecar único na onda (espera o par; MUST NOT dois sidecars); templates Pause em `openspec-apply-change`; P0 de reviewer vs lista P1/P2.
- **Disposition:** D1–D4 honram Entra/não entra e Q1–Q4; prova = próxima sessão; máquina destape #879 intocada.
- **Riscos não bloqueantes:** pai pode continuar a ignorar texto; sidecar único não destapa os dois ao mesmo tempo (Q3 fila).

Design Agent verdict: PASS
