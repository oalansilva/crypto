# Design: card-580-release-doc-same-day

Este arquivo é o **refinamento do card #580**. O issue veio primeiro; o Dev implementa **a partir daqui** (Gist). OpenSpec SHALL ser superset do issue.

## UI impact

`none` — `scripts/release-guard` e docs de processo. **Não** autoriza pular colunas de Design.

## Prototype

**N/A** — sem superfície visual do produto.

## Impeccable

**N/A** — `UI impact: none`.

## Origem

- Issue: [#580](https://github.com/oalansilva/crypto/issues/580)
- Tipo: story (processo) · Frente: Operacao · Prioridade: P1 · label `kaizen`
- Change: `card-580-release-doc-same-day`
- Incidente: 2026-08-17 lote 2; PR #578; evidência reusada `91f5620e` (lote 1)

## Card primeiro, OpenSpec mais completo

Issue = intenção. Gist = contrato do Dev. Republicar o mesmo Gist se o card ganhar detalhe.

## Problema

Hoje, em `pre`, se `docs/release-${RELEASE_DATE}.md` existe, o guard exige `PROD_DEPLOY_EVIDENCE` (proxy #518: “arquivo existe” = PR documental). Correto para o **primeiro** PR documental do dia. Errado para um **segundo PR de código** no mesmo dia: a doc do lote 1 já está no tree, `origin/develop` ainda diverge, e o operador reusa a evidência do lote anterior.

A seção “Prod deploy evidence” usa `release_published` (`develop == main`). **Não** reutilizar esse sinal para classificar documental vs código: o PR documental canônico do #518 é `develop → main` **depois do deploy**, quando `origin/develop` **já diverge** (docs/kaizen ainda não estão em `main`). `develop == main` também falha com merge `--no-ff` e com `release-*` enquanto `develop` está suja.

## Decisões

### D1 — Classificar pelo **diff do PR**, fail-closed

Depois de `git fetch --prune origin`, calcular `unpublished`:

- Se a branch atual casa `release-*`: `git diff --name-only origin/main...HEAD`
- Senão: `git diff --name-only origin/main...origin/develop`
- Se o diff não puder ser calculado: tratar como **documental** (fail-closed)

Allowlist de closeout (documental), paths relativos à raiz:

- `docs/**`
- `openspec/changes/archive/**`
- `openspec/specs/**`
- `AGENTS.md`, `rules.md`

**PR de código** se `unpublished` contém **qualquer** path fora do allowlist.

**PR documental** se a doc canônica da data existe **e** `unpublished` está vazio **ou** ⊆ allowlist.

Não usar `DOCUMENTAL_PR`. Não usar `origin/develop == origin/main` como classificador desta seção.

| Situação | `pre` Release docs |
| --- | --- |
| Sem doc, delta de código | não exige evidência (já ok) |
| Doc do dia + delta de **código** (2º lote, ex. #578) | **não** exige evidência do lote anterior; **warn** de atualizar a doc após o deploy deste pacote; **não** bloquear por placeholders da doc antiga |
| Doc do dia + delta só closeout **ou** unpublished vazio | **exige** `PROD_DEPLOY_EVIDENCE` **deste** pacote + `validate_release_doc` (PR documental lote 1 e lote 2) |

Na dúvida, documental.

### D2 — Uma doc por data

Proibido `docs/release-YYYY-MM-DD-lote2.md`. O segundo pacote **atualiza** o mesmo arquivo após o deploy. Check de docs duplicadas divergentes no `post` permanece.

### D3 — `post` amarra evidência ao **código/PROD deste lote**

A ordem #518 faz deploy PROD no merge de **código**; depois o PR documental empurra `origin/main` para um SHA só de docs. A evidência canônica é o commit publicado em PROD (ponta de código), **não** o `origin/main` pós-PR documental.

Com `PROD_DEPLOY_EVIDENCE` preenchida:

1. Primeiro token resolve para um objeto Git (`git rev-parse --verify`).
2. Esse commit é **ancestral** de `origin/main` (inclui igualdade se o `post` rodar antes do PR documental).
3. `git diff --name-only <evidence>..origin/main` ⊆ allowlist de closeout (D1). Se houver path fora do allowlist, a evidência não é deste lote (ex.: reuso de `91f5620e` no lote 2, cujo código ainda não está atrás só de docs).
4. Uma abreviação git desse commit (≥7 hex, word-boundary) aparece **pelo menos uma vez** na doc canônica. “Única” = desambigua o objeto, **não** ocorrência==1 no arquivo (a doc cita o SHA várias vezes).

Reusar SHA do lote 1 no lote 2 falha em (3). SHA completo na evidência vs prefixo de 8 na doc: comparar por objeto Git.

Se a evidência estiver vazia, o blocker existente de `PROD_DEPLOY_EVIDENCE` no `post` cobre.

### D4 — Docs de processo

`AGENTS.md` / ordem #518: **uma doc canônica por data**; vários pacotes no mesmo dia atualizam o mesmo arquivo após cada deploy. O `pre` do PR de código não herda evidência do lote anterior. O `pre` do PR documental **continua** gated. Não relaxar deploy PROD antes de `Pronto`.

### Fora de escopo

- #579, #581.
- Mudar o formato textual de `PROD_DEPLOY_EVIDENCE` (só a validação).
- Segunda doc da mesma data.
- Gate kaizen “um heading por lote” (follow-up; não misturar).

## Critérios de aceite (do issue)

- `pre` de um PR de código no mesmo dia de uma doc já publicada **não** exige evidência do lote anterior.
- Continua existindo uma única `docs/release-YYYY-MM-DD.md` por data.
- `post` do segundo pacote valida a doc atualizada com a evidência do SHA de **código/PROD daquele** lote (ancestral de `origin/main` com delta restante ⊆ allowlist).

## Implementação (somente `Status=Pronto para Dev`)

1. Substituir o `if arquivo existe ⇒ exigir evidência` pelo classificador D1.
2. `post`: D3 (evidência ancestral de `origin/main`; delta `evidence..origin/main` ⊆ allowlist; abreviação ≥7 pelo menos uma vez na doc).
3. `AGENTS.md`: D4.
4. Evidência:
   - `pre` PASS: unpublished contém path fora do allowlist, doc existe, sem evidência.
   - `pre` FAIL: doc existe, unpublished ⊆ allowlist, sem evidência (documental #518, develop pode ≠ main).
   - `post` FAIL: evidência do lote anterior (`evidence..origin/main` tem path fora do allowlist) mesmo o SHA antigo na doc.
   - `post` PASS: evidência = ponta de código deste lote; `origin/main` pode estar à frente só com closeout; abreviação na doc.

## Design Critique

Crítica isolada 1: **BLOCKED** — D1 `develop==main` quebrava o PR documental #518; D3 `grep` do SHA aceitava lote 1.

Crítica isolada 2: **BLOCKED** — D3 `evidência == origin/main` quebrava o `post` após o PR documental; proposal ainda falava igualdade de refs.

Crítica isolada 3 (read-only, pós-D3): P0/P1 fechados. D1 = diff do PR + allowlist. D3 = ancestral de `origin/main` + `git diff --name-only <evidence>..origin/main` ⊆ allowlist + abreviação ≥7 pelo menos uma vez. Proposal alinhado. Residual P2: evidência igual ao SHA só-docs ainda satisfaz ancestral+diff vazio; a prosa pede a ponta de código/PROD. Prototype/Impeccable N/A.

## Design Agent verdict

**PASS** — UI N/A; OpenSpec superset do issue #580. Pronto para Aprovação de Design (Alan).
