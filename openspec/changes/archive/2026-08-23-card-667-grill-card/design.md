## Context

Card [#667](https://github.com/oalansilva/crypto/issues/667). Ritual: grelhar a história em **Em Refinamento**; T1 só Alan; OpenSpec em Design **sintetiza** o issue. Skill de entrada **nossa**, não `grill-with-docs`.

**UI impact: none.** Harness/skills/docs de processo. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Porta `grill-card` com contrato fechado no issue (DoD).
- Vendor `grilling` sem dual-write para Hermes/`~/.codex`.
- Agente em Em Refinamento: `issue_edit` + `comment`; nunca T1; nunca OpenSpec; nunca `CONTEXT.md` na `develop`.
- Design: `/opsx:new`+`/opsx:ff` a partir do issue grelhado; Gist = superset.
- Stubs Moore curtos (paging ≤20 linhas); preservar substring canônica de Todo.

**Non-Goals:**

- 13ª coluna Backlog; schema `grill-driven`; skill `to-spec`.
- Instalar `grill-with-docs` como porta.
- Vendor write de `domain-modeling` (`CONTEXT.md`, `docs/adr/`).
- Grill obrigatório em todo T0 (Alan escolhe; cards nítidos podem T1 direto).
- Mudar atores T1/T7/T15 ou `process_event` beyond `context_file`.
- Código de produto.

## Decisions

### D1. Porta = `grill-card`; primitivo = `grilling` vendorado

Mesmo padrão `alan-workflow` ∩ OpenSpec. `.cursor/skills/grilling/SKILL.md` é cópia do upstream [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) (fronteira, uma rodada, recomendação, fato ≠ decisão). Quase não tocar. `grill-card` é a skill que o agente lê: frontmatter `disable-model-invocation: false` (ela *é* invocável); no corpo, “leia grilling e aplique o contrato abaixo”. **Não** `npx skills add grill-with-docs`. **Não** copiar as três skills e só trocar path de ADR.

### D2. Ledger = GitHub issue, não arquivos de glossário

DoD do body (PT-BR), só então comentar handoff T1:

1. Problema (uma frase, quem sofre)
2. História Como / quero / para
3. Entra / não entra
4. Vocabulário (`Termo`; `_Avoid:`)
5. Critérios observáveis
6. Riscos / perguntas — se a fronteira não zerou, **ficar** em Em Refinamento

Comentário canônico (uma linha, verificável):

`grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`

Proibido: `gh project item-edit` Status; `process_event priorizar`; Write `CONTEXT.md`; `docs/adr/`; `/opsx:*`.

### D3. Binding, coluna e disparo

`grill-card` só com `bound_card` = issue e `q=Em Refinamento` (Project 1). Sem bind ou outra coluna: recusar e não editar o issue de outro card. Fatos (código, specs) o agente busca; decisões o Alan responde. Uma rodada por turno; esperar.

**Quando disparar (fecha P1 de WHEN):**

- **Sim:** Alan pede para grelhar/afiar **ou** o card está bound em Em Refinamento **e** o body **não** tem as 6 seções do DoD (agente **oferece** `grill-card`, não arrasta).
- **Não:** automático em todo T0; não em Todo/Design; cards já nítidos (DoD completo) podem T1 sem grill.

### D4. OpenSpec não reabre a entrevista

`openspec/config.yaml` `rules.proposal` e `rules.design`:

- Usar vocabulário e não-objetivos do issue bound.
- Não introduzir sinônimos.
- Não reabrir decisões fechadas no body.
- Não invocar `grill-card` nem `grill-with-docs` ao gerar `proposal.md`.

Skills `openspec-new-change` / `openspec-ff-change`: se o body tiver as 6 seções do DoD, briefing = issue; não AskUser “o que construir?”. `/opsx:explore` não substitui `grill-card`. `/opsx:ff` **depois** do grill (Design); **não** durante o grill.

Gist continua superset. Após ff, conferir números/negativos/defaults contra o body (comentário de Design).

**Body incompleto em Design (fecha P1):** se o issue bound **não** tiver as 6 seções do DoD, o agente MUST NOT `/opsx:ff` nem completar história no chute. MUST comentar as seções em falta e permanecer em `Design`. `/opsx:explore` MAY só para furo **técnico** (código/specs existentes), nunca para reescrever a história de produto. Completar o DoD = Alan edita o issue **ou** devolve o card a Em Refinamento (processo humano; agente não inventa aresta Design→Em Refinamento).

### D5. `context_file` curto; T0/T1 intocados

Não alterar `states` nem transições. Só texto Moore:

| Estado | Stub (intenção; Todo MUST conservar a frase canônica de paging) |
| --- | --- |
| Em Refinamento | Esclarecer + `grill-card` no issue; chat ≠ T1; sem `CONTEXT.md` |
| Todo | **Obrigatório (paging):** a substring exata `Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda.` Pode acrescentar no máximo uma frase curta (“issue grelhado”) se a página sessionStart continuar ≤20 linhas |
| Design | OpenSpec + crítica; sintetizar do issue; não reentrevistar; Write produto deny |

Página sessionStart MUST permanecer ≤20 linhas (`process-fsm-paging`). `enabled_tools` de Em Refinamento permanece `[issue_edit, comment]` (sem `write_openspec`). Campo Project `Fluxo`/opção Backlog **não** vira 13ª coluna de Status.

### D6. Testes e higiene

- `pytest scripts/process-fsm -q` continua verde (substring Todo + Homologado).
- Teste de existência: `grill-card` e `grilling` são arquivos regulares (não symlink `120000`).
- `grill-card/SKILL.md` contém as proibições D2.
- Sem dual-write para Hermes/`~/.codex` (`grill-card` e `grilling` só em `.cursor/skills/` deste repo).
- `agents/openai.yaml` do pacote Matt **não** entra no repo.

### D7. Dry-run de processo (aceite)

Este card **é** o dry-run parcial (grelha já documentada no #667). Após Pronto para Dev: aplicar skills; um card-filho de produto (ou o próximo T0) demonstra grill → T1 → ff sem reentrevista. Não bloquear o apply deste card à espera do filho.

## Risks / Trade-offs

- [Agente carrega `grill-with-docs` global] → skill nossa + proibição explícita no `alan-workflow`; não versionar a fachada.
- [Stub Moore estoura 20 linhas] → uma linha extra no máximo; testes de paging são gate.
- [Issue grelhado mas Design reentrevista] → rules no `config.yaml` + skills OPSX.
- [Glossário de produto ainda espalhado] → aceito (D2); `CONTEXT.md` fica fora deste card.

## Migration Plan

Apply na branch `card-667-grill-card`. Sem migração de dados. Rollback = reverter os arquivos de skill/yaml. Cards já em Todo não são re-grelhados.

## Open Questions

Nome da porta = `grill-card` (fecha a questão do issue). Disparo = D3. Body incompleto em Design = D4.

## UI impact

**none** — sem superfície de produto.

## Prototype

N/A — `UI impact: none`.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit, duas Tasks read-only (A=`77db9ba1`, B=`805d3ca7`), sem partilhar transcript antes da síntese. Fontes: `proposal.md`, `design.md` (D1–D7), `tasks.md`, `specs/grill-card/spec.md`, `specs/cursor-harness/spec.md`, `specs/process-fsm/spec.md`. Card #667, change `card-667-grill-card`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Rodada 1: **BLOCKED** — P1 (WHEN do grill; body incompleto em Design; dual-write Hermes; `disable-model-invocation`; freeze `enabled_tools`).

Correções: D3/D4; scenarios nas specs; tasks 1.2/2.3/2.4/3.1/4.2.

Recrítica 2 (inherit, não editar): A e B **PASS**. P0/P1 abertos: nenhum. P2 não bloqueantes ignorados.

- **Escopo:** adapter `grill-card` + vendor `grilling`; ledger = issue; OpenSpec sintetiza.
- **Processo:** T0/T1 intocados; T1 Alan-only; sem coluna nova.
- **Operação:** DoD no body; handoff canônico; Design não reentrevista.

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica 2). Prototype N/A. Impeccable N/A.
