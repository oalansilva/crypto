# Design: card-569-code-review-bugbot

## Problema

O Code Review do Cripto já é uma coluna pré-commit, mas o agente executa um `Task` `generalPurpose` e o `AGENTS.md` só autoriza Bugbot se Alan pedir. O revisor nativo do Cursor quase nunca roda. As rules `.mdc` não chegam ao Bugbot. Autofix na mesma branch furaria o SHA revisado.

O usuário afetado é o agente que fecha o card e Alan, que depende de um review auditável. Não há superfície visual de produto.

## UI impact

**`UI impact: none`** — harness, docs e Automations. Nenhuma tela, rota, componente, estilo ou copy de produto muda.

## Hipótese

Se o Code Review disparar `/review-bugbot` no diff não commitado (vs HEAD) e um run `branch changes` vs `develop` no SHA de fechamento, com `BUGBOT.md` e um Task de processo read-only, o gate usa o revisor que o Cursor documenta, sem inverter o fluxo nem pular Design.

## Resultado esperado

- Todo card em `Status=Code Review` tem evidência de `/review-bugbot` (achados, no findings, ou spawn falhou).
- Pré-commit usa `uncommitted changes` (sem `Base Branch`).
- Pelo menos um run `branch changes` + `Base Branch: develop` existe para o SHA de fechamento.
- Autofix na branch existente permanece desligado (ou residual aceito por Alan).
- Agent Review automático pós-commit permanece desligado.

## Context

Estado atual: Cursor Agent é o harness (#562). Code Review = review do diff exato antes do commit, depois QA (`qa-gate` + Playwright). A skill `/review-bugbot` já existe no cliente; o contrato do repo a trata como opcional.

Constraints: mesmo modelo `inherit` no subagent de processo; Bugbot/Security Review são produtos gerenciados (Composer no Bugbot); worktree/branch por card; Design gate intacto.

## Goals / Non-Goals

**Goals:**

- Tornar `/review-bugbot` o revisor padrão do gate Code Review, com prompts fiéis à skill.
- Garantir um review `branch changes` vs `develop` por card.
- Ensinar o Bugbot o contrato do Cripto via `BUGBOT.md`.
- Separar busca de bug (Bugbot) de contrato de processo (Task read-only com `.cursor/agents/code-reviewer.md`).
- Manter Bugbot de PR como complemento de QA, com Autofix off.

**Non-Goals:**

- Ligar Agent Review automático pós-commit.
- Autofix / Cloud Agent commitando na branch do PR.
- `/babysit` na coluna Code Review.
- Security Scanner em cron.
- Qualquer mudança de produto, API, banco ou UI.

## Decisions

### D1 — Dois prompts canônicos, fiéis à skill `/review-bugbot`

A skill oficial só aceita `Diff: uncommitted changes` **ou** `Diff: branch changes`. `Base Branch` só entra na segunda forma. `uncommitted changes` compara working tree vs HEAD, não vs `develop`. Misturar `uncommitted` + `Base Branch: develop` é prompt inválido.

**Pré-commit (todo commit de implementação):** worktree absoluta + só o patch que vai no commit:

```text
Full Repository Path: <worktree absoluta>
Diff: uncommitted changes
```

Sem linha `Base Branch`. Sem o agente calcular o `git diff`.

**Contra `develop` (obrigatório uma vez por card, depois do commit de implementação e antes de Done):** a skill manda informar a base quando não é a default (`main`):

```text
Full Repository Path: <worktree absoluta>
Diff: branch changes
Base Branch: develop
```

Isso cobre commits já na branch + uncommitted vs merge-base com `develop`. `/review-security` usa o **mesmo** par de prompts quando o caminho quente dispara.

Alternativa rejeitada: só o PR no GitHub (gate depois do commit). Alternativa rejeitada: `uncommitted` + `Base Branch` (não é o contrato da skill).

### D2 — Reuso só do run `branch changes` do SHA de fechamento

O run `uncommitted` **não** substitui a comparação com `develop`. Depois do commit de implementação o card MUST ter pelo menos um `/review-bugbot` `branch changes` + `Base Branch: develop` daquele SHA. Reutilizar evidência só se esse run já existir para o SHA de fechamento. “Mesmo patch” de um `uncommitted` anterior não autoriza skip.

### D3 — Caminho quente de `/review-security` por globs

Dispara se o diff tocado casar com qualquer glob:

- `backend/app/api/**`
- `backend/app/**/auth*`
- `backend/app/**/credential*`
- `backend/app/**/wallet*`
- `backend/app/**/trading*`
- `frontend/src/**/wallet*`
- `frontend/src/**/auth*`
- `**/*credentials*`
- `**/.env*`

Cards só de `AGENTS.md` / `.cursor/` / `docs/` / OpenSpec **não** disparam. Alternativa rejeitada: a palavra solta “API”.

### D4 — Spawn vazio: 1 retry, depois fallback explícito

A skill já manda retry uma vez. Se persistir: `ERROR: subagent spawn failed/empty` no handoff. Só então um `Task` `generalPurpose` read-only cobre o gate. Fallback nunca é happy path; no Done vira residual. Duas falhas de spawn no mesmo card → residual no card, sem fingir que o Bugbot rodou.

### D5 — `BUGBOT.md` é a única rule visível ao Bugbot

Doc oficial: `.cursor/rules/*.mdc` não aplicam. Raiz sempre incluída; `backend/.cursor/BUGBOT.md` e `frontend/.cursor/BUGBOT.md` só quando o diff toca aqueles trees. Conteúdo curto: PostgreSQL; sem SQLite; Design/`Pronto para Dev` não puláveis; secrets fora; teste se `backend/**` muda; UI exige Playwright visual.

### D6 — Revisor de processo: arquivo versionado + Task `generalPurpose` read-only

`.cursor/agents/code-reviewer.md` (`readonly: true`, `model: inherit`) é a fonte do prompt. Neste cliente o `Task` não tem `subagent_type` custom: a sessão lança **um** `generalPurpose` read-only cujo prompt é o corpo desse arquivo + o diff/SHA. O arquivo também alimenta auto-delegation no Cursor desktop. Não duplica busca de bug. Spawn falho desse Task segue a mesma regra D4 (erro explícito; o Bugbot nativo continua obrigatório no happy path). Task 1.x MUST mandar invocar, não só criar o arquivo.

### D7 — Bugbot no PR é QA; Autofix Off; Incremental Review on

Patch ID local sincroniza com o PR. Autofix **Commit to Existing Branch** viola o SHA revisado — MUST Off. Create New Branch fica fora deste card. Agent Review auto-after-commit permanece off.

Se o dashboard Cursor não estiver acessível no apply, o critério Autofix Off **não** fecha: registra residual e espera comentário de Alan (`Autofix Off aceito como residual: <motivo>`). Sem esse comentário o item 3.1 permanece aberto. Incremental Review ligado é SHOULD (não bloqueia Done se o check local pré-commit + `branch changes` vs `develop` existirem).

### D8 — Exceção de modelo só para produtos gerenciados

Bugbot/Security Review usam o modelo do produto Cursor. O subagent de processo e qualquer `Task` de fallback usam `inherit`. Documentar a exceção em `AGENTS.md` para não parecer troca silenciosa de LLM.

## Risks / Trade-offs

- [Bugbot indisponível / plano sem Automations] → 1 retry; depois `ERROR` + fallback explícito; Done cita residual.
- [Default branch `main` no `branch changes`] → `Base Branch: develop` **somente** nesse prompt; omitido no `uncommitted`.
- [Autofix ligado / dashboard inacessível] → item 3.1 não fecha sem evidência ou aceite explícito de Alan.
- [Custo de review em todo commit] → Incremental no PR; pré-commit só no diff não commitado.
- [Regressão de produto] → nenhuma tela/API muda.

## Migration Plan

1. Aprovar Design (`Aprovação de Design` → `Pronto para Dev` só Alan).
2. Aplicar docs + `BUGBOT.md` + subagent na branch do card.
3. Registrar Autofix Off (settings/screenshot). Se inacessível, residual no card até Alan aceitar por comentário.
4. Rollback: reverter o commit da branch; o processo volta ao `Task` genérico.

## Open Questions

- Confirmar no dashboard se Bugbot já está enabled no `oalansilva/crypto` (apply; não bloqueia o Design).
- Fail-on-unresolved no check `Cursor Bugbot` **não** entra neste card.

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

Crítica isolada 1 (Task `inherit`, `3e56d7c4-a510-416c-98ba-f9e1dcbb2fc6`): **BLOCKED** — P1 prompt inválido (`uncommitted` + `Base Branch: develop`).

Resolução: D1/D2/specs/tasks alinhados à skill oficial.

Crítica isolada 2 (Task `inherit`, `3e4ca798-7d24-4bfe-92bf-300c6ebc79b5`): **PASS**. P1 resolvido. P2 residuais: copy “vs develop” (corrigido na Hipótese/proposal nesta rodada), Autofix Off é gate de apply (3.1). Zero P0/P1 aberto.

Referências avaliadas: `proposal.md`, `design.md`, `tasks.md`, `specs/cursor-code-review/spec.md`, `specs/cursor-harness/spec.md`, `specs/delivery-qa-stage/spec.md`, `specs/developer-tooling/spec.md`. Prototype: N/A. Impeccable: N/A.

## Design Agent verdict

`Design Agent verdict: PASS`
