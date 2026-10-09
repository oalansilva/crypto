## Context

Card [#1022](https://github.com/oalansilva/crypto/issues/1022). O Guard em `scripts/process-fsm/guard.py` classifica `openspec/changes/**` como `design_globs` e, com `q is None` fora de `card-<id>-*`, devolve `fail_closed` (`decide()`: `kind != "product"` ∧ `kind == "design"` ∧ `not _card_branch(q_git)`). Em `release-*`, `resolve.py` não casa `CARD_GIT_RE` (`^card-(\d+)(?:-.*)?$`), logo `bound_card=⊥` e o provider de Status é chamado com `None` → `q` permanece `None`. Deny observado: `reason=fail_closed q=None q_git=release-2026-08-26 bound_card=⊥` (transcript `db8bccf2-008c-47bc-9805-449756d07f29`); recidiva no lote 2026-09-22 com cherry-pick `bc6382d5` e de novo em 2026-09-27 (kaizen F-5, coberto por este card).

O overlay já manda commitar o archive **na** `release-*` (card #617, `docs/crypto-overlay.md` caminho B). O desvio worktree-do-card + cherry-pick contradiz esse runbook. `bound_card=⊥` / paging unbound **não** são deny de T16; o bloqueio é só a escrita de `design_globs`.

UI impact: none
live_route: N/A
Harness de escrita OpenSpec em closeout; sem tela, rota autenticada ou landing.
surface: none

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Archive OpenSpec do pacote Homologado executável em `q_git=release-*` pelo caminho oficial, sem bloqueio só por não haver um único `bound_card` na sessão.
- Cada path de `openspec/changes/**` identificado ao card, ao Status vivo e à pertinência ao pacote **antes** do allow.
- Deny visível (motivo no `agent_message`/`reason`) quando o pacote, o Status ou a pertinência não se provam.
- Produto, protótipos e contextos que não sejam `release-*` inalterados.
- Regressão do deny registado + allow com contexto válido + deny fora do pacote.
- #1059 consome este contrato; sem segunda implementação nem confirmação extra de Alan.

**Non-Goals:**

- Nova coluna, evento, hook ou `enabled_tools` na FSM.
- Ligar `bound_card` à `release-*` (pacote é N cards; `bound_card` continua singular e `⊥`).
- Formalizar worktree-do-card + cherry-pick como caminho oficial.
- Ampliar escrita para `frontend/public/prototypes/**`, `backend/**`, `frontend/src/**`, `develop`/`main`, ou changes sem id de card no nome.
- Executar uma release, mover Status, ou absorver continuidade/manifesto/evidências/fecho geral de #1059.
- Substituir T7/T15/T18 humanos.

## Decisions

1. **Via: resolver o contexto dos cards do pacote para o archive em `release-*`.** O runbook #617 já commita o archive nessa branch. O fail_closed dispara só porque a sessão de closeout é unbound, não porque o pacote seja desconhecido. A via worktree+cherry-pick (usada em `bc6382d5` e no lote 2026-09-26) é o desvio a eliminar, não o contrato. A frase antiga “decisão de Alan” não cria aprovação operacional extra; T7 permanece o único gate de Design.

2. **`bound_card` permanece `⊥` em `release-*`.** `resolve.py` não muda. Um único bound mentiria para um pacote de vários cards e reintroduziria o bloqueio do critério 1. O Guard, **depois** de classificar `kind == "design"` e **antes** do `fail_closed` genérico, tenta a excepção de archive: `q_git` casa `release-*` (mesmo predicado que `t16.lote_git`, sem incluir `develop`) e cada path de design no envelope é um path de change OpenSpec mapeável.

3. **Pertinência pelo prefixo do nome da change, não por lista nem por título fuzzy.** Do path relativo: `openspec/changes/<change>/…` ou `openspec/changes/archive/<YYYY-MM-DD>-<change>/…`. O id vem de `^(card|issue)-(\d+)` no `<change>` (o mesmo `mapping=name` do `release-guard`). Título/score fuzzy **não** libera escrita. Sem id → deny `fail_closed` (pacote/pertinência não identificados). `frontend/public/prototypes/**` nunca entra na excepção.

4. **Estado vivo do card mapeado, não a sessão.** Com `q` de sessão `None`, o Guard chama o `status_provider` já injectável com o id mapeado (não com `bound_card`). Allow só se o Status for exactamente `Homologado`. `None`/timeout/quota → deny `fail_closed` (estado não resolvido). Qualquer outro Status (`Design`, `Em desenvolvimento`, `Pronto`, `Cancelado`, …) → deny `outside_package`. Pytest continua a injectar o provider; MUST NOT chamar GitHub nos unit tests. Envelope com vários paths: **todos** os design paths têm de passar; um só fora do pacote nega o envelope.

5. **Lista declarada é recorte, nunca token de allow.** Se `RELEASE_CARDS` está definido, `t16.parse_package_cards` MUST ser válido e o id mapeado MUST pertencer à lista **e** continuar `Homologado` no provider. Lista inválida, id ausente da lista, ou lista sem Status vivo → deny. `RELEASE_CARDS` vazio/ausente **não** libera; o allow independe da lista quando o id mapeado prova `Homologado` em `release-*`. Nome da branch sozinho também não libera.

6. **Motivo informado, resto do Guard intacto.** Deny da excepção usa `fail_closed` quando falta identificação/Status, e `outside_package` quando o card está resolvido mas não pertence ao pacote Homologado. `agent_message` nomeia reason, `q`, `q_git`, `bound_card` e o id mapeado quando existir. Product writes, sidecar, Status `item-edit`, `canonical_card_branch`, overlay em falta e fail-closed em `develop`/`card-*` não mudam. Sem estado, evento, hook ou `enabled_tools` novo.

7. **Runbook = caminho normal; cherry-pick sai.** Overlay (secção publicação / caminho B) e a secção Release de `covenant-flow` passam a dizer: com release solicitada, o agente identifica os Homologado, arquiva as changes `card-<id>-*` / `issue-<id>-*` **na** `release-*`, e não pede confirmação extra nem abre worktree só para furar o Guard. Próximo `/kaizen release` aplicável registra se a recorrência F-1/#1022 encerrou. #1059 MUST reutilizar `decide()`; MUST NOT copiar uma segunda allow-list.

## Risks / Trade-offs

- [Change OpenSpec sem prefixo `card-<id>`/`issue-<id>`] → deny `fail_closed`; o closeout mapeia ou renomeia **antes** de escrever; fuzzy do `release-guard` não é token de Write.
- [Status GraphQL unread/quota no closeout] → deny `fail_closed` visível; não inferir Homologado do chat nem de `RELEASE_CARDS`.
- [Branch `release-*` residual com cards já Homologado de outro lote] → allow só das changes cujo id está Homologado agora; produto e in-flight continuam deny. Residual de branch é higiene #759, não deste card.
- [Envelope misto prototype + archive] → deny o envelope; o agente separa as escritas.
- [Pin do núcleo covenant-flow] → fora deste card (P3 de Apply / #1059); o contrato observável é `decide()` neste consumidor.

## Migration Plan

Após T7/T8: alterar só a ramificação `design` + `q is None` em `guard.py`, testes injectados em `scripts/process-fsm/test_guard.py`, e o texto do overlay + skill Release. Rollback = reverter esses diffs; o fail_closed anterior regressa. Sem migração de dados, sem deploy de UI, sem executar lote.

## Open Questions

Nenhuma. A via e os predicados de allow/deny fecham os critérios do Entra.

## Prototype

N/A. Sem HTML.

## Impeccable

N/A — sem-tela; não há Design visual, rota viva nem digest. Gates Design e aprovação humana (T7) permanecem.

## Apply contract

- Só após `Status=Pronto para Dev`/T8.
- Excepção de archive em `decide()`; `resolve.py` e a FSM intocados.
- Fixtures: replay `fail_closed` em `release-*` unbound sem pacote; allow com `status_provider(id)=Homologado`; deny `outside_package`; deny em `develop`, produto e protótipo.
- Overlay + skill: caminho oficial na `release-*`; cherry-pick deixa de ser o normal; #1059 consome o mesmo `decide()`.
- Não marcar evidência Kaizen do *próximo* lote como task feita neste card.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3:** nenhum

Pendências não bloqueantes: nenhuma. Sem P0/P1 aberto.

- Prototype: N/A — guard/processo, sem ecrã, sem HTML
- Snapshot: N/A — sem-tela; não houve crítica visual
- Tokens: `UI impact: none` / `live_route: N/A` / `surface: none`
- Spawns: 2
- proxy modelo: design-autor → Grok 4.6 (grok-4.6)
- proxy modelo: design-critic → Grok 4.6 (grok-4.6)

O mapa vigente em `origin/develop` pede juízo `Grok 4.6` / `cursor-grok-4.6-high`. Este host não aceita esse slug Cursor; o spawn usou `grok-4.6`, não inherit do pai.

Design Agent verdict: PASS
