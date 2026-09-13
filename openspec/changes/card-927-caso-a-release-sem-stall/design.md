## Context

Card [#927](https://github.com/oalansilva/crypto/issues/927) (kaizen, Operação, P0). Briefing = issue grelhado. Q1 `fecho-aviso`, Q2 `os-dois`, Q3 `para-e-diz` — este Design não as reabre.

Stall T16 do 2º pacote 2026-09-12 (#916+#917 → PR #922 em produção, health ok, cards não foram a Pronto). Fora do lote, na develop: #897 #899 #904 em Done não homologados. O `post` actual passa só se develop e produção são o mesmo commit, **ou** se develop é ancestral de produção **e** as árvores são idênticas. Caso A deixa develop à frente com árvore diferente → blocker. Overlay 5b manda sync produção → develop para árvores idênticas. A dança do 1º pacote (#913+#914+#915) foi rejeitada; #924 (merge normal produção → develop) é o padrão que deve bastar; #926 é recusado.

Job `e2e-playwright`: `timeout-minutes: 30`; `needs` só `qa-policy`; **não** espera `frontend-build`. Fecho T16: paging `unbound` não é deny se o git é develop/release-*; em produção/`docs-*`/`sync-*` a recusa é a palavra seca `unbound`.

UI impact: none
live_route: N/A
surface: new

Processo/release-guard/CI, sem rota autenticada nem landing. Sem HTML. Nunca emprestar `/monitor` `/favorites` `/combo/*` `landing`.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Fecho PASS neste turno quando o lote homologado já está em produção (cada card do lote tem commit lá) **e** a produção está contida na develop (`origin/main` ancestral de `origin/develop`, igualdade de commit incluída). Extra na develop = aviso. Bloqueia se a develop não contém a produção.
- Um PR merge normal produção → develop no pós-produção. Recusa substituir a develop / merge que descarta o outro lado / restore.
- Pacote incompleto para localmente, sem abrir o PR.
- Build do ecrã falhou ⇒ o teste longo nem arranca.
- Fecho no git errado para e diz a próxima acção; não muda sozinho.

**Non-Goals:**

- Fechar o lote #916/#917 neste card.
- Homologado sem comentário (#658); campos Project vazios (#910); Caso B (#617).
- Watcher nativo de 35 min do CI.
- Write de produto com chat unbound.
- Proibir Caso A; exigir árvores iguais / dança de 3 PRs; auto-switch de git; só um dos dois cortes.
- Helper `scripts/release-casoa-closeout.sh` como aceite (MAY).
- Produto `backend/**` / `frontend/src/**`. HTML de protótipo.

## Decisions

1. **Alinhamento `post` = produção contida na develop (Q1).** Trocar o predicado actual (`mesmo commit` **ou** `develop` ancestral de `main` **e** árvores iguais) por: PASS se `origin/main` é ancestral de `origin/develop` (ou o mesmo commit). Extra na develop (commits/árvore) = warn com inventário, não blocker. FAIL se `origin/main` não é ancestral de `origin/develop`. Árvores iguais e «develop ancestral de produção» deixam de ser aceite.

   Rejeitado: árvores iguais. Rejeitado: dança de 3 PRs. Rejeitado: esperar develop limpa (proibir Caso A).

2. **Sync 5b = 1 PR merge normal `main → develop`.** Overlay passo 5b e o runbook de `release-*` mandam exactamente esse PR. Recusam: substituir a ponta de develop pela árvore de produção; merge `ours`/ancestrar; apagar Done e restore (#913+#914+#915; #926). Ensaio: #924 sozinho passa. Se o primeiro `post` falhar porque develop ainda não contém produção, o runbook diz: completar o merge normal e repetir `post`. Não muda git sozinho.

3. **Pacote incompleto = compile local fail-closed antes do PR (Q2, primeiro corte).** Em `release-*` com PR de código, o `pre` (ou o runbook Caso A imediatamente antes de `gh pr create`) corre um compile frontend local que falha se faltar módulo nascido fora do lote (ex.: #916 sem o ficheiro do #897). Exit non-zero ⇒ não abre o PR. O guard permanece read-only quanto a refs git: o compile MUST NOT gravar `frontend/dist` tracked como efeito do guard (`tsc --noEmit` ou equivalente). P3: script exacto.

4. **E2E não arranca se `frontend-build` falhou (Q2, segundo corte).** `e2e-playwright` passa a `needs: [qa-policy, frontend-build]` e só começa quando `frontend-build` é `success` (e, em PR, `qa-policy` success). O teto do job continua 30 min; deixa de se gastar num ecrã que já não compilou. Watcher 35 min não entra. P3: expressão `if:` no YAML.

5. **T16 no git errado = reject com próxima acção (Q3).** `fechar_release` com `q_git` `main` (produção), `docs-*` ou `sync-*` rejeita sem mover Status, sem `checkout`/`switch`. `message` diz: mudar para `develop` ou `release-*` e repetir. `reason` MUST NOT ser só `unbound`. Paging unbound em develop/release-* continua a não ser deny de T16. P3: token exacto de `reason`.

6. **Commit em produção por card do lote.** `post` (com `RELEASE_CARDS`) bloqueia se algum id do pacote não tem commit alcançável em `origin/main` que referencie `#<id>` (convenção squash já usada). Não fecha #916/#917. P3: regex/word-boundary.

7. **Helper MAY.** `scripts/release-casoa-closeout.sh` só se overlay + guard não cobrirem env do `post` e a recusa de git errado. Não é aceite.

## Risks / Trade-offs

- [Risco] `post` antigo «develop ancestral de main com árvores iguais» deixa de PASS sem o merge `main → develop` → Mitigação: é o aceite Q1; o runbook 5b manda o 1 PR.
- [Risco] Compile local no `pre` atrasa o gate ou viola read-only se correr `vite build` → Mitigação: typecheck `--noEmit` / temp dir; P3 de Apply.
- [Risco] `e2e-playwright` serializa atrás de `frontend-build` no caminho feliz (~minutos a mais no verde) → aceite: não gastar 30 min no vermelho.
- [Risco] Mapa card→commit no `post` falha por squash sem `#N` → Mitigação: convenção já existente; P3 regex; fail-closed.
- [Trade-off] Extra na develop (Done não homologado) fica em produção? Não: o lote continua a sair por Caso A (cherry-picks); o extra fica só na develop, aviso no `post`.
- [P3 Apply] Script de compile; token `reason` T16; `if:` YAML; regex `#N`; helper MAY; wording exacto do passo 5b no overlay.

## Prototype

N/A — card sem tela: processo/release-guard/CI. Sem rota autenticada, sem landing, sem HTML, sem clonar catálogo, sem `frontend/public/prototypes/`. Impeccable / Playwright visual / `DESIGN.md` = N/A justificado. Nunca emprestar `/monitor` `/favorites` `/combo/*` `landing`.

## Impeccable

N/A — `UI impact: none`; não há superfície visual nem pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana permanecem.

## Apply contract

- `scripts/release-guard`: predicado `post` = `origin/main` ancestral de `origin/develop` (ou mesmo commit); extra develop = warn; FAIL se develop não contém produção; `pre` em `release-*` código = compile frontend fail-closed sem write tracked de `dist`; `post` exige `#N` em `origin/main` por card de `RELEASE_CARDS`.
- `docs/crypto-overlay.md` passo 5b + runbook Caso A: 1 PR merge normal `main → develop`; recusa #926 e #913+#914+#915; compile local antes do PR; T16 no git errado = próxima acção. Skill `covenant-flow` só o recorte 5b/1 PR se o pin duplicar o passo. `AGENTS.md` always-on MUST NOT crescer.
- `.github/workflows/ci.yml`: `e2e-playwright` depende de `frontend-build` e não arranca se o build falhou.
- `scripts/process-fsm/process_event.py` (+ testes injectados): `fechar_release` em `main`/`docs-*`/`sync-*` reject com `message` de próxima acção; MUST NOT auto-switch; MUST NOT `reason=unbound` seco.
- Deltas OpenSpec: `release-worktree-hygiene`, `release-archive-via-release-branch`, `ci-testing-hardening`, `process-fsm-event`.
- MUST NOT: produto UI/backend; fechar #916/#917; Caso B; watcher 35 min; auto-switch; dual-write; `CONTEXT.md`/`docs/adr/`; HTML de protótipo. A secção de crítica fica para o pai depois do crítico.
- Helper `scripts/release-casoa-closeout.sh` MAY.

## Migration / Rollout

N/A de dados. Depois de Pronto para Dev: Apply no worktree desta branch; o próximo Caso A usa o `post` novo. Rollback = reverter o predicado e o `needs` do e2e.

## Open Questions

Nenhuma — Q1–Q3 fechadas no issue. P3 acima são detalhe de Apply, não perguntas de operador.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3** `if:` de `e2e-playwright` (live usa `always()`; só `needs: frontend-build` não impede o arranque) — aceite, detalhe de Apply
- **P3** Script exacto do compile local (`tsc --noEmit` / sem write tracked de `dist`) — aceite, detalhe de Apply
- **P3** Token exacto de `reason` T16 (live `q_git=main` ainda espera `unbound`) — aceite, detalhe de Apply
- **P3** Regex/word-boundary `#N` no mapa card→commit — aceite, detalhe de Apply
- **P3** Wording exacto do overlay 5b + recorte pin se duplicar — aceite, detalhe de Apply
- **P3** Helper `scripts/release-casoa-closeout.sh` MAY — aceite, detalhe de Apply

Pendências não bloqueantes: as P3 acima. Sem P0/P1 aberto.

- Prototype: N/A — processo/release-guard/CI, sem ecrã, sem HTML
- Snapshot: `.impeccable/critique/927-card-927-caso-a-release-sem-stall-2026-09-13T012021Z.md`
- Tokens: `UI impact: none` / `live_route: N/A` / `surface: new`

Design Agent verdict: PASS
