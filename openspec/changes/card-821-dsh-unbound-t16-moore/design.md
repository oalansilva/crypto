## Context

Card [#821](https://github.com/oalansilva/crypto/issues/821). Status observado: **Design**. Briefing = issue grelhado (DoD completo). Este Design **não** reabre as decisões de operador nem entrevista Alan.

Nas sessões dsh `session-ffe87792` e `session-766065f3` (2026-09-03) Alan pediu `suba a release` no cwd canónico DEV. O root recusou T16 em ~8s, 0 tools. Recidiva `session-35e78019` (2026-09-07, `fechar release`): o root leu a skill `covenant-flow` e **mesmo assim** deny unbound («sem aresta T16»), raciocínio «skipping overlay load per guardrails». Header ainda injeta o stub Moore `bound_card=⊥. Write produto deny. Não carregue playbook de release.` mais `enabled_events: (unbound)`.

`page()` em `scripts/process-fsm/paging.py` é o compilador único da página Moore. Os quatro injectores consomem o mesmo texto: Cursor `sessionStart`, Grok ficheiro gerado, OpenCode `system.transform`, dsh `covenant-flow:moore`. `lote_git("develop")` já deixa `process_event fechar_release` avaliar unbound (`test_fechar_release_unbound_develop_evaluates`). A δ não recusou T16; o modelo leu o stub como deny. #613 já cortou o playbook Homologado/release always-on; pedido explícito **continua** a carregar overlay. Cursor/Grok cooperam; dsh é o outlier.

Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.13`, `clients.dsh.auto: false`.

UI impact: none
live_route: N/A harness-only; dsh Moore page / T16 closeout; no product route
surface: new

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Pedido explícito `suba a release` / `fechar release` / `subir lote` em sessão dsh **sem card** (`q=None`, `bound_card=⊥`, `q_git=develop`): o root **não** encerra com deny textual por `bound_card=⊥`; carrega overlay on-demand e inicia o playbook T16 (≥1 tool: overlay / `covenant-flow-environments` / `release-guard` / board / `process_event fechar_release`).
- Write de produto em `develop` / unbound **continua deny**.
- Unbound idle (sem pedido de release) **não** despeja playbook Homologado/release always-on (#613 intacto).
- O mesmo stub atinge os quatro injectores; Cursor/Grok não regridem no pedido explícito. DoD humano = **só o dsh** (dump `:3080`). Goldens pytest cobrem idle vs excepção; **não** exigem dump nos quatro clientes.

**Non-Goals:**

- Reabrir #613 / #652 / #812 / #782 / #784 / #786 / #817 como trabalho.
- Auto dsh (`clients.dsh.auto` permanece `false`). Vendorar `deepseek-ai/deepseek-harness`. Dual-write Hermes / `~/.codex/skills/`.
- Mudar Σ / colunas / `fechar_release` / `M_lote` / `process_event.py` / `t16.py` / `guard.py` `decide()`. Produto `backend/` / `frontend/src/`.
- Crescer `AGENTS.md` com o runbook de 12 colunas. Executar um lote PROD neste card.
- Exigir `bound_card` na sessão para T16. Closeout explícito com card bound e coluna unread (residual: `unread_page()`).
- DoD humano com dump nos quatro clientes. NLU no compilador `page()` (paging é sessionStart, não parse do turno).
- Emprestar rotas de catálogo `/monitor` `/favorites` `/combo/*` ou `landing`. HTML / `DESIGN.md` de produto. Impeccable/Playwright visual.

## Decisions

1. **Alavanca = rewording de `UNBOUND_PAGE` no compilador único.**  
   Recidiva: ler `covenant-flow` **não** chega se o header ainda diz «Não carregue playbook de release.» Inject só dsh seria dual-write da lei e deixaria o fallback Cursor e os outros três clientes com o stub antigo. Nota always-on em `AGENTS.md` já aponta overlay on-demand para release; o modelo escolheu a linha mais específica do stub. **Escolha:** mudar `UNBOUND_PAGE` em `paging.py`. Os quatro injectores passam a ver a excepção sem despejar Homologado/`release-guard pre`/`deploy PROD`. Alternativa rejeitada: só skill. Alternativa rejeitada: inject dsh paralelo. Alternativa rejeitada: crescer `AGENTS.md`.

2. **Texto pinado do stub (uma linha; página ≤20).**  
   Constante `UNBOUND_PAGE`:

   `bound_card=⊥. Write produto deny. Playbook de release não é always-on. Pedido explícito suba a release / fechar release / subir lote: carregue overlay e inicie T16.`

   MUST conter `Write produto deny`. MUST conter as três frases de pedido explícito. MUST NOT conter `Não carregue playbook de release.` MUST NOT conter o stub Homologado (`T16 = process_event fechar_release com M_lote live. Chat ≠ δ.`), `release-guard`, nem `deploy PROD`. Nomear `subir lote` **como wording do chat** não é dump do playbook; os goldens unbound deixam de usar `subir lote` como needle de dump. Envelope D2 #613 intacto (tupla, `enabled_events: (unbound)`, footer overlay on-demand). Alternativa rejeitada: duas linhas de runbook T16 no stub ( magoa #613 e o teto Moore). Alternativa rejeitada: listar `fechar_release` em `enabled_events` unbound (display ≠ lei; inventaria aresta na página).

3. **A excepção vive no stub always-injected, não num parser de chat.**  
   `page()` corre no `sessionStart` / assemble; **não** vê o turno. Idle unbound e closeout explícito partilham o mesmo texto: idle = «não despeje playbook»; explícito = «carregue overlay e inicie T16». NLU ≠ δ continua para T1/T7/T15/T18 e para Write. Chat `suba a release` **não** é o evento T16; é o pedido que autoriza carregar o playbook. Alternativa rejeitada: hook per-turn no dsh a detectar needles (quarto cliente só; não cobre o header que o modelo já leu).

4. **Fallback Cursor = a mesma constante.**  
   `.cursor/hooks/process-fsm-session-start.sh` hardcodeia o stub antigo. `test_session_start_adapter_fallback` afirma `UNBOUND_PAGE in ctx`. Apply MUST actualizar o fallback para o texto pinado em D2 (Python e bash iguais). Grok/OpenCode/dsh não têm este hardcode; chamam `paging.py`. Alternativa rejeitada: fallback mínimo sem a excepção (Python em falta voltaria ao deny T16).

5. **`unread_page()` não muda.**  
   O stub Status unread com `bound_card=N` ainda diz `Não carregue playbook de release.` Fora do Entra (operador: só sessão sem card). Residual explícito; não é P0 deste card. Alternativa rejeitada: «já que estamos no compilador, limpar os dois» (fura o Entra e mistura o residual).

6. **Reforço de uma linha na skill, não no always-on.**  
   Secção Release de `.cursor/skills/covenant-flow/SKILL.md`: `bound_card=⊥` e `enabled_events: (unbound)` são display do paging, não deny de T16; pedido explícito unbound em `develop`/`release-*` carrega overlay + `covenant-flow-environments` e segue T16; Write de produto continua deny. Stubs `.dsh/` `.grok/` `.opencode/` intactos (≤8, MUST Read). `AGENTS.md` **não** cresce. Alternativa rejeitada: copiar o playbook T16 para a skill (já proibido). Alternativa rejeitada: só o stub sem a linha (recidiva mostrou o modelo a «saltar overlay per guardrails» depois de ler o runbook).

7. **Nucleo via pin; δ / T16 / produto intocados.**  
   `paging.py` é nucleus (`implantar --pin` copia `scripts/process-fsm/`). Apply: delta no produto `oalansilva/covenant-flow`, `git ls-remote --tags`, próximo patch livre após `v1.1.13`, rebase no tip (irmãos #858/#859 e afins partilham pele), `implantar --pin` no Cripto. `clients.dsh.auto: false`. MUST NOT editar `process-fsm.yaml`, `process_event.py`, `t16.py`, `fsm.py`, `guard.py` `decide()`, `backend/`, `frontend/src/`. `test_fechar_release_unbound_develop_evaluates` permanece verde sem mudança. Alternativa rejeitada: só patch no consumidor (o próximo `--pin` reverte o stub).

### Golden cases (pytest `scripts/process-fsm`, sem GitHub, sem dump live)

| # | Caso | Esperado |
| --- | --- | --- |
| G1 | `page()` `bound_card=⊥` `q_git=develop` | `UNBOUND_PAGE` no ctx; `Write produto deny`; sem stub Homologado; sem `release-guard`; sem `deploy PROD`; sem `Não carregue playbook de release.`; contém `suba a release` e `fechar release`; ≤20 linhas; `enabled_events: (unbound)` |
| G2 | o mesmo ctx (idle + excepção) | dump de playbook ausente **e** wording overlay/T16 presente |
| G3 | `unread_page("821")` / bound N + Status unread | **ainda** contém `Não carregue playbook de release.`; `UNBOUND_PAGE` ausente; `bound_card=⊥` ausente no header |
| G4 | `page()` Todo e Homologado | needles de dump (`release-guard`, `deploy PROD`) ausentes; stub yaml intacto; Todo MAY continuar a proibir `subir lote` no *playbook dump* (página Todo ≠ stub unbound) |
| G5 | fallback `process-fsm-session-start.sh` sem Python | stdout JSON; `UNBOUND_PAGE` no `additional_context`; sem `docs/crypto-overlay.md`; sem `release-guard` |
| G6 | `test_fechar_release_unbound_develop_evaluates` | intacto; fontes `process_event.py` / `t16.py` sem diff deste card |
| G7 | `AGENTS.md` | ≤40 linhas não vazias; sem tabela T0–T17; ponteiro overlay on-demand intacto |
| G8 | overlay | `clients.dsh.auto` é false; `pin` = tag cravada após `v1.1.13` |

Homologação humana (não substitui G1–G8; bloqueia Auto): dump autenticado `http://127.0.0.1:3080` de um closeout explícito unbound em que o root chama ≥1 tool do **playbook T16**. Só `skill` + `read` do SKILL.md **falha**. Dump Cursor/Grok/OpenCode **não** é critério.

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#821`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica. Este filho autor **não** chama `process_event`, **não** T5, **não** commit/push.
- (1) `paging.py`: substituir `UNBOUND_PAGE` pelo texto D2. **Não** editar `unread_page()`. (2) `.cursor/hooks/process-fsm-session-start.sh`: fallback = o mesmo texto. (3) `.cursor/skills/covenant-flow/SKILL.md`: uma linha na secção Release (D6). (4) `test_paging.py`: G1–G5, G7; unbound **não** usa `subir lote` como needle de dump; G3 afirma unread intacto. G6 = teste T16 existente sem toque em `process_event`/`t16`. (5) produto `oalansilva/covenant-flow`: mesmo delta + tag patch livre após `v1.1.13` + `implantar --pin` Cripto; `clients.dsh.auto: false` (G8).
- MUST NOT: Σ / yaml transitions / `fechar_release` / `M_lote`; `backend/` / `frontend/src/`; Auto dsh; vendor DeepSeek; dual-write T0–T17; crescer `AGENTS.md`; executar lote PROD; rotas de catálogo / HTML / `DESIGN.md` de produto.
- Homologação: dump `:3080` (critério 3 do issue). Homologação ≠ `./restart`; 3080 ≠ systemd; cwd = `canonical_paths.dev`. Pytest **não** substitui o dump.

## Risks / Trade-offs

- [Stub mais longo ainda cabe em Lost in the Middle] → uma linha; teto ≤20; G1 conta linhas. Sem runbook T16 no stub.
- [Needle `subir lote` nos testes Todo vs unbound] → G4 mantém dump-forbid em Todo; G1/G2 permitem a frase só no stub unbound. Apply MUST fatiar o tuple `PLAYBOOK` por fixture.
- [Fallback bash dessincroniza da constante Python] → G5 afirma `UNBOUND_PAGE in ctx`; falha se os textos divergirem.
- [Próximo `--pin` reverte o stub se o produto não levar o delta] → D7: tag + pin. Irmãos na mesma pele: rebase no tip.
- [`unread_page()` continua a proibir playbook com card bound] → aceite; Entra = só sem card. Residual nomeado, não P0.
- [Chat `suba a release` ≠ δ] → D3: wording autoriza **carregar** overlay/playbook; `process_event fechar_release` continua a medir `M_lote`. NLU ≠ δ para T1/T7/T15/T18/Write.
- [Homologação `:3080` ≠ worktree] → dump é Apply/homologação; goldens não substituem. Este card **não** corre lote PROD.
- [Cursor/Grok já cooperavam; o stub novo chega-lhes] → G1/G2 preservam #613 (sem dump always-on). Risco de regressão = despejar playbook; mitigado pelos needles `release-guard` / `deploy PROD`.

## Migration Plan

Aditivo sobre `pin: v1.1.13`. Ordem Apply: `UNBOUND_PAGE` + G1/G2 → fallback + G5 → skill uma linha → G3/G4/G7 regressão → produto tag + `--pin` + G8. Sessões dsh já abertas mantêm o header antigo até novo assemble; não há migrate de banco. Rollback = pin anterior + revert da constante. Sem rebuild frontend. Homologação = dump `:3080` depois do pin no cwd canónico.

## Open Questions

Nenhuma bloqueante (três decisões de operador fechadas no issue). Residual: `unread_page()` com a ordem antiga — fora deste card.

## UI impact

UI impact: none

## live_route

live_route: N/A harness-only; dsh Moore page / T16 closeout; no product route

## surface

surface: new

## Prototype

N/A — `UI impact: none`. Harness-only: compilador Moore / closeout T16 no dsh. Sem rota de produto. Sem clone de `/monitor` `/favorites` `/combo/*` ou `landing`. Sem HTML. Sem `DESIGN.md` de produto. Sem pipeline Impeccable visual. Playwright desta coluna = N/A.

## Prototype Validation

N/A — sem superfície visual de produto. Aceite = dump dsh `:3080` + goldens G1–G8, não um protótipo HTML.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Snapshot Impeccable = N/A justificado (sem tela Cripto; crítico desta rodada verifica tokens e escopo, não um snapshot visual).

## Design Critique

Crítico isolado (sem-tela, 1 critic, inherit, sem transcript). Snapshot: `.impeccable/critique/821-card-821-dsh-unbound-t16-moore.md`. Prototype: N/A justificado.

- P0: (nenhum) — n/a
- P1: (nenhum) — n/a
- P2: (nenhum) — n/a
- P3: fatiar `PLAYBOOK` (`subir lote`) unbound vs Todo; G1 sem needle positivo de `subir lote`; dual constante Python/bash; linha Release + tag após `v1.1.13`; residual `unread_page()` / sessões dsh já abertas — **accepted** (detalhe de Apply)

Pendências não bloqueantes: Apply fatiar needles; G5 igualdade Python/bash; `unread_page()` fora do Entra.

Design Agent verdict: PASS
