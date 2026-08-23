## Context

Card [#661](https://github.com/oalansilva/crypto/issues/661) (kaizen P1). O gate #518 exige heading `Kaizen release` no log; não exige issues no board. Em 2026-08-21 três lotes fecharam com “(não criado)” e Em Refinamento vazia de cards novos.

**UI impact: none.** Guard/CLI/docs de processo. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- `post` FAIL sem materialização Kaizen válida para a `RELEASE_DATE`.
- `post` PASS com 0 cards novos só com dedupe válido (cobertura em fluxo) ou seção explícita sem achados acionáveis.
- Specs + skill alinhados; testes de integração PASS/FAIL.
- Parsing determinístico a partir da tabela já usada no log.

**Non-Goals:**

- Criar issues automaticamente no `release-guard` (só valida).
- Consultar GitHub Issues label fora do Project 1 Status (Status do board é a fonte).
- Reabrir cards Pronto; isso é escopo de #660 (dedupe) — este card só enforce no guard.
- Mudar T16 / `process_event`.
- UI de produto.

## Decisions

1. **Fonte canônica = tabela sob cada `## YYYY-MM-DD — Kaizen release`.**  
   O guard já acha o heading da data. Estende: para **todas** as seções Kaizen release da mesma `RELEASE_DATE`, localiza o próximo heading `###` cujo texto **começa com** `Cards kaizen criados` (sufixo livre, ex. `(máx. 3/release)`). Parseia a tabela markdown até o próximo `##`/`###`. União das linhas de todas as seções da data.

2. **Classificação de linhas (após descartar header e separador `|---|`).**  
   Cada linha de dados cai em exatamente uma classe:  
   - **created:** primeira célula casa `^\s*#\d+\b` (ex. `#658 — …`). Contagem = issues distintas.  
   - **dedupe:** primeira célula casa `(não criado)` (case-insensitive) **e** a linha contém `coberto por` seguido de um ou mais `#\d+` (separados por `/`, `,` ou espaço). Extrair **todos** os `#N` após `coberto por`; **todos** devem passar no check de fluxo (D3).  
   - **invalid:** qualquer outra linha de dados — inclui `(não criado)` sem `coberto por #N`, texto `observação; sem card novo`, célula vazia com conteúdo residual, etc.  
   - Marcador `Sem achados acionáveis` (case-insensitive) é procurado no **corpo** da união das seções (fora da exigência de estar na tabela). Só vale se, após o parse, **não** houver linhas de dados na união das tabelas (tabela ausente ou só header/separador).

3. **Cobertura “em fluxo”.**  
   Status do `#N` no Project 1 (snapshot `BOARD_JSON` / `FAKE_BOARD_JSON` do post): válido se Status presente e **∉** `{Pronto, Cancelado}` (ex. `Em Refinamento`, `Todo`, `Homologado` contam como em fluxo). Ausente no board ⇒ FAIL. Em testes, stub do board. O path (a) confia na listagem do log para cards **criados** (não revalida Status/label no board); só o dedupe exige Status.

4. **Regra de PASS/FAIL (precedência).**  
   Avaliar nesta ordem:  
   1. Se existe **qualquer** linha `invalid` ⇒ **FAIL** (mesmo com 1–3 created ou marcador).  
   2. Se qualquer `#N` de dedupe tem Status terminal/ausente ⇒ **FAIL**.  
   3. Se `created_count` > 3 ⇒ **FAIL**.  
   4. Se `created_count` ∈ [1, 3] ⇒ **PASS** (linhas dedupe válidas extras permitidas).  
   5. Se `created_count` == 0: **PASS** só se (a) marcador `Sem achados acionáveis` com zero linhas de dados **ou** (b) ≥1 linha dedupe e todas as coberturas em fluxo.  
   6. Caso contrário ⇒ **FAIL** (sem tabela, tabela vazia sem marcador, etc.).

5. **Skill read-only preservada.**  
   Skill `kaizen` continua “não muta board”. Documenta que o **orquestrador do closeout** materializa cards/dedupe antes do `post`; o guard é o enforcement. Label `kaizen` é contrato de criação (orquestrador); o guard **não** verifica a label via API.

6. **Spec Status = Em Refinamento.**  
   Corrige o texto legado `Status=Todo` no requirement de registro de melhorias.

7. **Fail-closed no board.**  
   Reusar o carregamento de board do `post`. Se o snapshot estiver indisponível/incompleto (`BOARD_STATE != ok` ou equivalente) **e** houver ao menos uma linha dedupe (checagem de cobertura necessária) ⇒ **FAIL** com mensagem explícita de fail-closed. Se só há created (1–3) e zero dedupe, board down não bloqueia este check.

## Risks / Trade-offs

- [Log com formato livre quebra o parse] → documentar o template na skill; FAIL explícito ensina o formato.
- [Vários lotes no mesmo dia] → união por data; um lote sem tabela pode ser coberto por outro — aceitável se a data no total satisfaz a regra; se um lote omitir e outro criar 3, PASS. Mitigação futura (#660): exigir tabela por heading.
- [Card criado mas não na tabela] → FAIL até listar; intencional (evidência no log).
- [Cobertura Em Refinamento antiga] → dedupe válido; Alan tria.

## Migration Plan

Aditivo no `post`. Releases antigas já Pronto não reexecutam. Próximo `post` precisa da tabela correta. Rollback = reverter o bloco no `release-guard` + testes.

## Open Questions

Nenhuma bloqueante. Formato da tabela já existe no log.

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

Crítica isolada inherit (read-only, duas rodadas). Fontes: `proposal.md`, `design.md` (D1–D7), `tasks.md`, `specs/kaizen-continuous-improvement/spec.md`, `specs/release-worktree-hygiene/spec.md`, `scripts/release-guard` (check kaizen-log), fixtures `_post_ready`. Card #661, change `card-661-kaizen-release-guard-cards`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Primeira crítica: **BLOCKED** — P1 (precedência invalid vs created; multi-ID `coberto por`; prefixo da tabela; fail-closed board nas specs; taxonomia; scenario do marcador).

Correções: D1–D7 reescritas; specs com scenarios PASS/FAIL/fail-closed; tasks 2.x/3.x alinhadas.

Recrítica 2 (inherit, não editar): todos os P1 da rodada 1 fechados. P2 aceitos: path (a) não revalida board nos created; união multi-lote no mesmo dia.

- **Escopo:** `post` exige materialização Kaizen (cards 1–3 / dedupe em fluxo / marcador).
- **Processo:** skill kaizen read-only; orquestrador materializa; guard enforce.
- **Operação:** parse determinístico da tabela; fail-closed com board down + dedupe.

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica 2). Prototype N/A. Impeccable N/A.
