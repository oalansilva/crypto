# Design: card-579-homologado-comment

Este arquivo é o **refinamento do card #579**. O issue veio primeiro; o Dev implementa **a partir daqui** (Gist). OpenSpec SHALL ser superset do issue.

## UI impact

`none` — processo + `scripts/release-guard` + docs. **Não** autoriza pular `Design` / `Aprovação de Design` / `Pronto para Dev`.

## Prototype

**N/A** — sem superfície visual do produto. Helper e guard são CLI.

## Impeccable

**N/A** — `UI impact: none`.

## Origem

- Issue: [#579](https://github.com/oalansilva/crypto/issues/579)
- Tipo: story (processo) · Frente: Operacao · Prioridade: P1 · label `kaizen`
- Change: `card-579-homologado-comment`
- Recidiva: release 2026-08-17 lote 1 (F-2) e lote 2 (8 cards sem helper até o closeout)

## Card primeiro, OpenSpec mais completo

O issue define problema, escopo e aceite. Este `design.md` + specs são o contrato do `/opsx:apply`. Se o chat acrescentar detalhe no card, promover para cá e republicar o **mesmo** Gist.

## Problema

O helper já existe (`scripts/post-card-evidence-comment.sh --transition homologado`), é fail-closed e deduplica pelo marcador `Homologado por Alan na develop.`. O agente não o chama no turno do arraste; `AGENTS.md` já pede o comentário mas não diz “mesmo turno, inclusive sem lote”. O `release-guard` só checa homologação em `post`/`audit`. `normalize_release_cards` **não corre no `pre`**. Os exemplos de lote chamam `scripts/release-guard pre` **sem** `RELEASE_CARDS`. O `pre` de um PR `develop → main` passa com pacote Homologado sem evidência no card.

## Decisões

### D1 — Processo no mesmo turno (gatilho = arraste, não o lote)

Quando o agente observar `Status=Homologado` (arraste de Alan **ou** confirmação em chat), nesse **mesmo turno** o agente SHALL rodar o helper, **mesmo se não houver lote/release nesse turno**.

```bash
scripts/post-card-evidence-comment.sh --transition homologado --card <n> --commit <sha>
```

`--commit`: SHA de integração do card em `develop`; se o card já estiver em `origin/develop` e o SHA de squash não estiver à mão, usar `origin/develop` HEAD. O body canônico de `homologado` não inclui o SHA; o arg existe para dedupe do helper.

Só **depois** do helper: `release-guard pre`, PR para `main`, archive ou qualquer ação de lote.

Falha do helper (gh, dedupe fail-closed, args) **bloqueia** closeout **e** também bloqueia seguir o turno como se Homologado estivesse evidenciado. Retroativo continua permitido se o turno anterior falhou — não é o caminho feliz.

Texto canônico **não** muda:

```text
Homologado por Alan na develop.
Apto para próximo pacote de release.
```

### D2 — Guard `pre`: ramo REST próprio, com `RELEASE_CARDS` normalizado

O spec `release-worktree-hygiene` exige `pre` com **zero** `item-list` / `pr list`. O check **não** pode carregar o board.

Contrato:

1. `pre` SHALL chamar `normalize_release_cards` (local, sem GraphQL). Token inválido em modo estrito ⇒ **blocker antes de qualquer REST**. Unset/vazio ⇒ **warn** e skip do check (não inventar pacote).
2. Check de homologação no `pre` = **seção/ramo novo**, **não** o `if post|audit` atual. Sem `ensure_snapshots`, `BOARD_STATE`, `card_status`.
3. Com `CANONICAL_CARDS` preenchido: para cada ID, GET REST `issues/<n>/comments`. Ausência do marcador `Homologado por Alan na develop.` ⇒ **blocker**. Sem `gh`/auth ⇒ **blocker**.
4. Política de elegibilidade: no `pre`, **todo** ID canônico exige o marcador (o pacote de lote é o conjunto homologado; Status não está disponível). N/A por Status Homologado|Pronto permanece **somente** em `post|audit`.
5. REST de comments no `pre` é permitida e fora do orçamento GraphQL (estender a frase vigente `post|audit` → `pre|post|audit`).

O `pre` é **rede de segurança**, não o gatilho (o gatilho é D1). Sem `RELEASE_CARDS` o check não roda — por isso D3 torna a env **obrigatória nos exemplos de lote**.

### D3 — Docs

- Bloco Homologado de `AGENTS.md`: arraste/confirmação ⇒ helper **no mesmo turno, mesmo sem lote**.
- Exemplos `scripts/release-guard pre` de publicação de lote passam a exportar `RELEASE_CARDS=<pacote>` (e `RELEASE_DATE`). Sem isso o aceite “0 no momento do `pre`” não é contratável no caminho documentado.
- Skill `alan-workflow` só depois do #585; overlay do cripto em `AGENTS.md` basta neste card.

### Fora de escopo

- Webhook GitHub que posta sozinho sem agente.
- Mudar o texto canônico do comentário.
- Enforcement mecânico no board (Actions ao arrastar Status).
- Inventar pacote no `pre` via GraphQL.
- Cards #580, #581, #585.

## Critérios de aceite (do issue, para o Dev)

- Próxima release: 0 cards Homologados do pacote sem comentário canônico no momento do `pre` (com `RELEASE_CARDS` nos exemplos de lote).
- `AGENTS.md` deixa explícito: arraste Homologado ⇒ helper no mesmo turno, mesmo sem lote.

## Implementação (somente `Status=Pronto para Dev`)

1. `normalize_release_cards` também no `pre`; inválido = blocker, zero REST.
2. Nova seção homologation-comments-pre: só REST, zero `card_status`.
3. `AGENTS.md`: D1 + `RELEASE_CARDS` nos snippets de `pre` de lote.
4. Evidência: `pre` FAIL sem marcador com `RELEASE_CARDS`; PASS com marcador; warn sem env; FAIL token inválido sem chamar comments; `pre` **não** herda `BOARD_STATE`.

## Design Critique

Crítica isolada (Task read-only, mesmo modelo): **BLOCKED** inicial (P1-A/B/C/D: `pre` sem `RELEASE_CARDS` nos exemplos; `normalize_release_cards` só em post; estender seção reusa `BOARD_STATE`; helper amarrado ao lote).

**Resolução:** D1 gatilho = arraste mesmo sem lote; D2 ramo REST + normalize no `pre` + elegibilidade distinta; D3 `RELEASE_CARDS` obrigatório nos exemplos de lote.

Re-crítica isolada: P1-A/B/C/D fechados. Residual P2: `pre` sem env ainda warn/skip (snippets de lote passam a exportar). Prototype/Impeccable N/A justificado.

## Design Agent verdict

**PASS** — UI N/A; OpenSpec superset do issue #579. Pronto para Aprovação de Design (Alan).
