## Context

Card [#879](https://github.com/oalansilva/crypto/issues/879) (kaizen P1, operação). Briefing = issue grelhado. Q1=automático, Q2=falha visível e pára, Q3 revogada (quatro etapas Cursor), destape = ordem — **não reabrir**. S1 continua só Code Review.

Rework 1/1 (Alan 2026-09-09, P1 de escopo no mesmo card): destape S2 também para filhos de Design (autor, crítico sem-tela, Assessment A/B) quando `status=completed` e o pai ainda espera o mesmo Task. Incidente desta sessão: autor `4bc9a67b` 20:09–20:18 completed OK; crítico `dfbef63a` 20:18:50–20:44:52 UTC `turn_ended aborted` (user `concluiu?` matou o Task). Esse aborto **não** ganha destape. Staff: não re-prompt enquanto o filho corre.

Drift actual: spec `cursor-code-review` já pede spawn autocontido **com o diff no prompt**; o spawn pede git ao filho. Ask mode bloqueia git só-leitura; o reviewer improvisa (transcripts). `.cursor/hooks.json` tem `sessionStart`, Guard e Impeccable; **não** destapa o pai quando o filho já acabou. Workaround staff: clicar no card do filho. Destape automático **não dispara** em background e **não cura** o hang do host.

UI impact: none
live_route: N/A harness-only; Cursor session orchestration (destape + review diff paste); no product route
surface: new

Harness Cursor (hooks + agentes + runbook). Sem rota, shell, copy ou HTML de produto. Impeccable/Playwright N/A.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- S1: pai cola o intervalo no Code Review; filho só-leitura devolve findings ou `No findings.` sem git e sem transcripts; sem intervalo → `ERROR: review-diff missing` e pára.
- S2: nas quatro etapas Cursor (grelha, Apply, Code Review, QA) **e** nos filhos de Design (autor, crítico sem-tela, Assessment A/B), filho **já acabou** (`completed`) e pai mudo → a sessão **avança a etapa** sozinha. Poke = ordem, não pergunta. Design-autor → spawn crítico/dupla; crítico/A/B → `## Design Critique` + Gist + `submeter_design`.
- Grelha/Apply entram por prevenção. Clicar no card do filho continua válido.

**Non-Goals:**

- Produto Descoberta / #876 / cobertura 67%. T1/T7/T15/T18. Aresta nova na FSM. QA dsh / `continue` (#858). Destapar filho ainda a trabalhar. Destapar `error`/`aborted` (este aborto de 27 min inclusive). Poke perguntar `concluiu?` / `já acabou?`. Bugbot. Reviewer Write. Filhos background. Curar hang do host. Terceira solução. Destape só por clique/`proceed`. Clientes Grok/OpenCode/dsh. Dual-write T0–T17 em `.dsh/`. Pin novo de covenant-flow. Crescer `AGENTS.md`. Overlay `clients.*.auto`. Protótipo HTML. Reabrir Q1/Q2/S1.

## Decisions

1. **S1 — o pai gera o intervalo, o filho não.** Pré-commit: o pai corre `git diff HEAD` (staged+unstaged vs HEAD) e acrescenta untracked de `git ls-files --others --exclude-standard` como hunks de ficheiro novo. Fecho: `git diff origin/<integration_branch>...HEAD` (`integration_branch` do overlay = `develop`). Alternativa rejeitada: pedir git ao filho (Ask mode bloqueia; é o drift).

2. **S1 — ficheiro obrigatório; bytes no prompt opcionais.** O pai grava o intervalo em `.cursor/tmp/review-diff.patch` (já gitignored: `.cursor/*` sem allowlist de `tmp/`). O spawn MUST conter a linha `review_diff_path:` + path. MAY colar bytes sob `## Diff`. O filho só `Read` esse path (e o `## Diff` se existir). Alternativa bytes-only rejeitada: diffs grandes estouram o prompt; o incidente foi intervalo ausente.

3. **S1 — string de erro exacta.** Se o path falta/está vazio **e** não há bytes não-vazios em `## Diff`, o filho imprime exactamente `ERROR: review-diff missing` e pára. Não lê o repo à mesma. Mesma classe visível que `ERROR: subagent spawn failed/empty`.

4. **S1 — MUST NOT no corpo dos agentes.** `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` (`readonly: true`, `model: inherit` intactos) passam a recusar: qualquer `git`; Glob/listagem de `agent-transcripts` / transcripts; inventar o intervalo a partir do working tree. O prompt continua autocontido (sem transcript Design/Apply).

5. **S2 — só `subagentStop`, nunca `subagentStart`.** `subagentStart` produz Stopped falso no fórum. O destape é `followup_message` no stop do filho. `failClosed` MUST NOT ser true (crash → `{}`; destape não é Guard). Matcher `generalPurpose`. Locator cwd-independente na mesma classe dos outros adapters Cursor.

6. **S2 — script + Python testável.** `.cursor/hooks/process-fsm-subagent-stop.sh` chama `scripts/process-fsm/subagent_stop.py` (venv backend, senão `python3`), no padrão do `sessionStart`. Goldens pytest alimentam stdin JSON e assertam stdout.

7. **S2 — guardas (todas AND).** Emitir `followup_message` só se: `status=completed` (o produto só consome o campo nesse status); `loop_count=0` (um poke por filho); sidecar `.cursor/tmp/awaiting-task.json` presente e o fingerprint de `task`/`description` bate com o stop (pai ainda à espera do mesmo Task); classificador das **quatro etapas mais filhos de Design** (grelha/`grill-card`; Apply/`apply-coluna`; `diff-reviewer`/`code-reviewer`; QA/`qa-gate`; Design-autor / `design-autor`; Design-crítico sem-tela / `design-critic`; Assessment A/B). Não classificar Design só pela palavra «Design». Ordem de match: Design-autor antes de crítico/A/B. Caso contrário `{}`. `error`/`aborted` → `{}` (o aborto de 27 min do crítico `dfbef63a` **não** destapa). Destapar filho ainda a trabalhar: não. explore/shell → `{}`. Background / `is_parallel_worker: true` (se vier no stdin) → `{}` (não cura o facto de o hook não disparar em background). Staff: não re-prompt enquanto o filho corre.

8. **S2 — sidecar é o sinal «ainda à espera».** O pai (runbook) grava o sidecar **antes** do Task das quatro etapas **e** do Task Design-autor / crítico / Assessment A/B, e apaga-o ao tratar o resultado. O hook apaga-o após poke. Pai já avançou (sidecar ausente) → sem poke extra. Filho ainda a trabalhar → `subagentStop` ainda não correu com `completed`.

9. **S2 — texto exacto do poke (ordem, nunca pergunta).** Proibido no payload: `concluiu?`, `já acabou?`, `verifique se nao concluiu`.
   - grelha: `O filho grill já devolveu. Faz o relaying das Qs / handoff T1 agora. Não perguntes se concluiu. Não spawnes outro grill.`
   - Apply: `O filho Apply já devolveu. Segue para o review: materializa o diff e spawna diff-reviewer + code-reviewer. Não perguntes se concluiu.`
   - review: `O filho reviewer já devolveu. Segue commit / push / PR agora. Não perguntes se concluiu.`
   - QA: `O filho QA já devolveu. Fecha o QA conforme o veredito (verde → integrar_develop; falhou → evidência visível). Não perguntes se concluiu.`
   - Design-autor: `O filho Design-autor já devolveu. Spawna o crítico (sem-tela) ou a dupla A/B (com-tela). Não perguntes se concluiu. Não spawnes outro autor.`
   - Design-crítico / Assessment: `O filho crítico de Design já devolveu. Escreve ## Design Critique, publica o Gist e chama submeter_design. Não perguntes se concluiu.`

10. **S2 — `loop_limit: 32`.** Default Cursor = 5; num chat `#id` cabem Design (autor + crítico/dupla) + grelha + Apply + 2 reviewers pré-commit + closing vs develop + QA + re-runs de finding. `null` = runaway. 32 cobre o mesmo chat com folga; não é teto de produto das colunas.

11. **Onde mora o runbook.** Apply edita `.cursor/skills/covenant-flow/SKILL.md` (S1 cola-diff + S2 destape/sidecar). Pin overlay permanece `v1.1.14` — este card não exige tag nova. Stubs `.grok/` / `.dsh/` / `.opencode/` continuam ponte ≤8 linhas. MUST NOT dual-write T0–T17. Overlay `clients.*.auto: false` intacto. `AGENTS.md` always-on não cresce. `.cursor/process-fsm.yaml` intocado.

12. **Goldens.** Estender `test_paging.py` / `test_guard.py` (hooks.json: `subagentStop` composto com Guard/sessionStart/Impeccable). Novo `test_subagent_stop.py`: completed+sidecar+grelha/Apply/review/QA/Design-autor/Design-crítico → ordem certa; aborted/error/ainda a trabalhar/sem sidecar/loop_count>0 → `{}`; crash fail-open. MUST NOT golden «Design-autor → {}» como regra. Asserts nos dois `agents/*.md`: `ERROR: review-diff missing`, MUST NOT git, MUST NOT transcripts.

## Apply contract

- Pai (após Pronto para Dev / filho Apply): implementar D1–D12. Sem `process_event` no filho Apply.
- Paths: `.cursor/hooks.json` (`subagentStop`, `loop_limit: 32`, sem `failClosed`); `.cursor/hooks/process-fsm-subagent-stop.sh`; `scripts/process-fsm/subagent_stop.py`; `.cursor/agents/diff-reviewer.md`; `.cursor/agents/code-reviewer.md`; `.cursor/skills/covenant-flow/SKILL.md`; testes pytest em `scripts/process-fsm/`.
- MUST NOT: `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml`, `AGENTS.md` always-on, overlay `clients.*.auto`, pin, `.dsh/` lei, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`, protótipo HTML, `subagentStart`, destape em `aborted`.

## Prototype

N/A — harness-only (orquestração da sessão Cursor: destape + cola do diff de review); nenhuma superfície de produto, rota autenticada ou landing a clonar. Sem HTML. Snapshot Impeccable N/A. Playwright N/A.

## Risks / Trade-offs

- [Sidecar cooperativo: pai esquecer de gravar] → sem destape (falha segura). Mitigação: runbook + golden do skill (`awaiting-task.json` nas quatro etapas e nos Tasks Design-autor / crítico / A/B).
- [Corrida: hook poke + pai já a continuar] → mitigação: pai apaga sidecar ao tratar o resultado; hook exige sidecar; residual = uma ordem extra rara (P3 de Apply se o produto Cursor enfileirar as duas).
- [`subagentStop` stdin sem `subagent_id`] → fingerprint `task`/`description` + path do transcript + sidecar, não inventar `subagentStart` para gravar id.
- [Default `loop_limit` 5 corta QA ou Design no mesmo `#id`] → D10 fixa 32.
- [S2 não cura hang do host nem background] → aceite na grelha; clique no card permanece.
- [Filho Design `aborted`/`error`, como o crítico `dfbef63a` 27 min] → `{}`; este aborto não ganha destape. Staff não re-prompt enquanto o filho corre.
- [Grok/OpenCode/dsh sem destape] → fora do Entra (#858 cobre QA dsh).

## Design Critique

Crítico isolado (sem-tela, 1 critic, inherit, sem transcript). Snapshot: `.impeccable/critique/879-card-879-destapar-pai-colar-diff.md`. Prototype: N/A justificado. Rework 1/1: destape S2 também em Design-autor/crítico/A/B se `completed` + sidecar.

- **P0** — nenhum.
- **P1** — nenhum.
- **P3** (aceitos, Apply) — sidecar por Task na sequência reviewer A→B e Assessment A→B; needles do classificador na `description` do Task; schema JSON do sidecar; golden «ainda a trabalhar» = ausência de `subagentStop` `completed`, não stdin inventado.
- **Disposition:** `aborted`/`error`/filho a trabalhar → `{}`; incidente `dfbef63a` fora; S1 só review; poke = ordem.
- **Riscos não bloqueantes:** S2 não cura hang do host nem background; clique no card permanece.

Design Agent verdict: PASS
