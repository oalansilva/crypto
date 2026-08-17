# Design: card-569-code-review-bugbot

## Problema

O Code Review do Cripto já é uma coluna pré-commit, mas o agente executa um `Task` `generalPurpose` sem prompt versionado e sem comparar com `develop`. O design aprovado em 2026-08-17 tornava `/review-bugbot` obrigatório. Alan recusou ligar o produto Bugbot por custo (usage-based por PR/push). Autofix na mesma branch furaria o SHA revisado.

O usuário afetado é o agente que fecha o card e Alan, que depende de um review auditável sem fatura extra. Não há superfície visual de produto.

## UI impact

**`UI impact: none`** — harness, docs e Automations. Nenhuma tela, rota, componente, estilo ou copy de produto muda.

## Hipótese

Se o Code Review disparar dois `Task` `inherit`/`readonly` (diff-reviewer no patch + code-reviewer de processo), com regras em `BUGBOT.md` e comparação `origin/develop...HEAD` no SHA de fechamento, o gate fica melhor que o `Task` genérico atual **e** evita o custo do Bugbot-produto. `/review-bugbot` permanece atalho opcional se Alan pedir num card caro.

## Resultado esperado

- Todo card em `Status=Code Review` tem evidência dos dois reviewers locais (achados, no findings, ou spawn falhou).
- Pré-commit revisa o diff não commitado vs HEAD.
- Fechamento revisa `origin/develop...HEAD` **ainda na branch do card**.
- Bugbot de dashboard permanece Off de propósito (custo). `/review-bugbot` / `/review-security` só se Alan pedir.
- Autofix na branch existente e Agent Review automático pós-commit permanecem desligados.

## Context

Estado atual: Cursor Agent é o harness (#562). Code Review = review do diff exato antes do commit, depois QA (`qa-gate` + Playwright). A skill `/review-bugbot` existe no cliente, mas o produto cobrado não será ligado.

Constraints: mesmo modelo `inherit` nos dois reviewers; worktree/branch por card; Design gate intacto; aprovação anterior (Bugbot obrigatório) está **obsoleta**.

## Goals / Non-Goals

**Goals:**

- Substituir o `Task` genérico por dois prompts versionados (`diff-reviewer` + `code-reviewer`).
- Garantir um review vs `develop` por card, na branch do card.
- Ensinar o contrato do Cripto via `BUGBOT.md` (lido pelos reviewers locais).
- Separar busca de bug (diff-reviewer) de contrato de processo (code-reviewer).
- Deixar `/review-bugbot` e `/review-security` opcionais.

**Non-Goals:**

- Ligar Automations/Bugbot no dashboard (custo).
- Ligar Agent Review automático pós-commit.
- Autofix / Cloud Agent commitando na branch do PR.
- `/babysit` na coluna Code Review.
- Qualquer mudança de produto, API, banco ou UI.

## Decisions

### D1 — Caminho feliz: dois tipos de reviewer, dois momentos

Dois `Task` `generalPurpose` read-only, `model: inherit` (tipos, não um único par na coluna):

1. Prompt = corpo de `.cursor/agents/diff-reviewer.md` + intervalo do diff.
2. Prompt = corpo de `.cursor/agents/code-reviewer.md` + o diff/SHA sob revisão.

A sessão principal corrige ou classifica achados. Os reviewers **não** editam. Alternativa rejeitada: `/review-bugbot` obrigatório (custo do produto). Alternativa rejeitada: continuar com `Task` genérico (prompt não versionado, sem `develop`).

### D2 — Dois momentos, base `develop` explícita; fechamento antes de QA

O revisor local **pode** receber o intervalo git (diferente da skill Bugbot, que não aceita `uncommitted` + `Base Branch`).

**Pré-commit (todo commit de implementação, ainda em `Status=Code Review`):** working tree vs HEAD. Rodar **os dois** reviewers nesse patch. O agente informa o diff vs HEAD no prompt.

**Fechamento (obrigatório imediatamente após o commit de implementação, ainda na branch do card, antes de `Status=QA`):** `diff-reviewer` em `origin/develop...HEAD`. Nunca depois do squash em `develop` (diff vazio). O `code-reviewer` MAY reusar o run pré-commit se o processo não mudou; o vs-`develop` do `diff-reviewer` NÃO reusa o uncommitted. Reuso do vs-`develop` só se este run já existir para o mesmo SHA.

### D3 — Bugbot/Security Review opcionais

`/review-bugbot` e `/review-security` **não** são o happy path. Só disparam se Alan pedir no card (comentário ou chat). Globs de caminho quente (auth/credencial/trading/wallet/API) **não** ligam o produto automaticamente; o diff-reviewer local já cobre segurança nesses paths via `BUGBOT.md`.

Se Alan pedir, usar os prompts canônicos da skill (`uncommitted changes` sem Base Branch; `branch changes` + `Base Branch: develop`).

### D4 — Spawn vazio: 1 retry, depois erro explícito

Se qualquer um dos dois Tasks falhar (0 messages / 0 parts / sessão ausente): 1 retry. Se persistir: `ERROR: subagent spawn failed/empty` no handoff. A sessão principal MAY completar o review ela mesma e registrar residual no Done. Fallback silencioso é proibido. Não fingir que o reviewer rodou.

### D5 — `BUGBOT.md` continua sendo a rule versionada do review

Mesmo com Bugbot Off, o arquivo ensina PostgreSQL, Design/`Pronto para Dev`, secrets, testes e Playwright. O diff-reviewer MUST ler raiz + aninhados quando o diff toca `backend/` ou `frontend/`. Files `.cursor/rules/*.mdc` não substituem esse contrato. Mantém o arquivo pronto se Alan ligar Bugbot no futuro.

### D6 — Autofix e Agent Review automático permanecem Off

Não commitar Autofix na branch existente. Agent Review auto-after-commit permanece off (inverteria o gate pré-commit). Item 3.1 deixa de ser “Autofix Off no dashboard”: Alan recusou ligar Bugbot; o residual é **Bugbot Off de propósito**.

### D7 — Sem exceção de modelo no caminho feliz

Os dois reviewers e qualquer fallback usam `inherit`. Não há produto gerenciado no default. Se Alan pedir `/review-bugbot`, esse run MAY usar o modelo do produto Cursor; isso não troca o LLM da sessão.

### D8 — Evidência de Done cita os reviewers locais

O helper `--review` continua obrigatório em `--transition done`. O texto cita `diff-reviewer` (uncommitted e vs develop) e `code-reviewer`. Não exige linhas `/review-bugbot`.

## Risks / Trade-offs

- [Reviewer local é o mesmo modelo do chat] → menos “olho treinado” que Bugbot-produto; mitigação: prompt versionado + `develop` explícito + segundo reviewer de processo.
- [Custo Bugbot] → produto Off; atalho opcional se Alan pedir.
- [Spawn vazio dos dois Tasks] → 1 retry + ERROR + residual; Done não mente.
- [Review vs develop depois do squash] → proibido; sempre na branch do card.
- [Regressão de produto] → nenhuma tela/API muda.

## Migration Plan

1. Aprovar o **novo** Design (`Aprovação de Design` → `Pronto para Dev` só Alan). A aprovação do plano Bugbot-obrigatório está obsoleta.
2. Aplicar docs + `diff-reviewer.md` + `code-reviewer.md` + `BUGBOT.md` na branch do card.
3. Registrar Bugbot Off de propósito (chat Alan 2026-08-17).
4. Rollback: reverter o commit da branch; o processo volta ao `Task` genérico.

## Open Questions

- Nenhuma bloqueante. `/review-bugbot` no futuro é decisão de Alan, fora deste card.

## Prototype

**N/A** — harness/docs. Nenhuma superfície visual de produto é criada, alterada ou removida. Não há URL de protótipo.

## Prototype Validation

**N/A** — sem protótipo. Browser gate não se aplica.

## Impeccable Brief

**N/A** — `UI impact: none`. Sem superfície para `context -> shape -> prototype`.

## Impeccable Critique

**N/A** — sem UI. Assessment A/B de produto/UX/a11y não se aplicam.

## Impeccable Audit

**N/A** — sem UI para acessibilidade, performance visual, theming ou integridade de implementação de tela.

## Impeccable Trace

**N/A** — pipeline Impeccable não executado; justificativa: card de processo/harness sem HTML/CSS/JS de produto.

## Design Critique

Crítica isolada 1 (Task `inherit`, `3e56d7c4-a510-416c-98ba-f9e1dcbb2fc6`): **BLOCKED** — P1 prompt inválido (`uncommitted` + `Base Branch: develop`) no plano Bugbot.

Resolução (plano antigo): D1/D2 alinhados à skill oficial. Superado pelo pivot.

Crítica isolada 2 (Task `inherit`, `3e4ca798-7d24-4bfe-92bf-300c6ebc79b5`): **PASS** do plano Bugbot-obrigatório. **Obsoleta** após Alan recusar ligar Bugbot por custo (2026-08-17).

Crítica isolada 3 (Task `inherit`, `35f2d0ba-098d-4eea-aaae-7f5ac421e47c`): **PASS**. Zero P0/P1. Pacote coerente com Bugbot Off por custo; happy path = dois reviewers locais `inherit`/`readonly`, pré-commit vs HEAD, fechamento `origin/develop...HEAD` na branch, skills pagas só se Alan pedir.

P2 de redação resolvidos nesta rodada: D1 distingue tipos vs momentos; D2 manda o vs-`develop` imediatamente após o commit e **antes** de `Status=QA`. P2 residual (fallback da sessão principal após spawn vazio) aceito: Done MUST citar o ERROR. P3 nome da change/`BUGBOT.md` aceitos (risco de leitura).

Referências avaliadas: `proposal.md`, `design.md`, `tasks.md`, `specs/cursor-code-review/spec.md`, `specs/cursor-harness/spec.md`, `specs/delivery-qa-stage/spec.md`, `specs/developer-tooling/spec.md`. Prototype: N/A. Impeccable: N/A.

## Design Agent verdict

`Design Agent verdict: PASS`
