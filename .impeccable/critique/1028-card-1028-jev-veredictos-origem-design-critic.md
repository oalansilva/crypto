# Relatório do crítico de Design — card #1028

**Papel:** filho isolado **Design-crítico (sem-tela)**. Read-only sobre os artefactos; a única escrita é este relatório.
**Change:** `openspec/changes/card-1028-jev-veredictos-origem/`
**Branch/worktree:** `card-1028-jev-veredictos-origem` @ `/srv/apps/dev/criptofarol/crypto-worktrees/card-1028-jev-veredictos-origem`
**Briefing:** issue #1028 (lido por `gh api repos/oalansilva/crypto/issues/1028 --jq '.body'`).
**Sem-tela:** backend/log. Prototype N/A. Impeccable N/A.
**Nota:** este relatório não edita nem escreve a secção `## Design Critique` do `design.md` (é do pai). Não fiz commit, push, `process_event`, Gist, comentário na issue nem `gh project item-edit`.

## Verificações executadas

1. **Briefing verbatim.** Comparei, por secção, o body do issue com `proposal.md`:
   - `## Problema` → **IDENTICAL**
   - `## História` → **IDENTICAL**
   - `## Entra` → **IDENTICAL**
   Sem reentrevista; a história vem do issue.
2. **Factos citados no design conferidos no worktree** (amostra): `scalp_engine.py:16` `JEV_LATE_MS = 1500`; `:19` `JEV_TARGET_MS = 30000`; ordem das recusas `:204/212/220/235/245/253/265/273/282/292/300/308/319/327/335/347/355/365/392`, verde `:403` (bate certo com o design); `:277` `jev.latency_ms > JEV_LATE_MS`; `scalp_jev.py:33` `_JEV_MODEL = "jev-latest"`; `:156` `"model": _JEV_MODEL`; `:204` `_noul_yes` = `noul >= 0.5`; `:208-218` `_side_confidence` (campo da resposta quando existe; senão `probabilities[choice]`; senão `0`); `:305` `timeout = JEV_LATE_MS/1000.0`; `scalp_window.py:122` `passes_entry_hurdle` (custo), `:135` `passes_regime_gate` (custo maker + 50% de folga = token `regime`); `scalp_jev_log.py:357-361` `log_cycle_refusal` grava só `user=` e `skip_reason=`; `:93-108` DEV-only + `raw_payload_enabled()`; `scalp_service.py:830-831` registra só quando `result.skipped`; `scripts/scalp_jev_eval.py:90-94` regexes; `test_scalp_direcional_jev.py:376` fixture `"model": "jev-1.13.0"`, `:466` `timeout == JEV_LATE_MS/1000.0`, `:468` `body["model"] == "jev-latest"`.
3. **Régua read-only (#1025).** `KVRe` só é aplicado às linhas `scalp jev call return` (`scalp_jev_eval.py:179-182`); `RefusalRe` (`:92`) lê `RefusalRe = re.search(r"\sscalp cycle refused user=(\S+) skip_reason=(\S+)")` e usa `group(2)` como token. Campos aditivos **depois** de `skip_reason` não a quebram.
4. **`openspec validate card-1028-jev-veredictos-origem --strict`** → `Change 'card-1028-jev-veredictos-origem' is valid`.
5. **Modified Capabilities.** `grep -i jev|scalp|confidence|toxic` sobre `openspec/specs/` e procura por `jev-latest|scalp cycle refused|book_toxic|JEV_LATE|low_confidence|scalp jev` → sem spec vigente que cubra este contrato. `Modified: (nenhuma)` é coerente.
6. **Tasks.** `tasks.md` com todas as caixas `- [ ]` (não marcado). Execução só após T8.
7. **`design.md` não contém `## Design Critique`** (secção reservada ao pai) — confirmado.

### Nota de leitura (não é achado)

O `## Entra` lista «custo, custo com folga, regime, toxicidade e confiança» — cinco nomes para quatro gates do código: «custo» = `hurdle` (`passes_entry_hurdle`) e «custo com folga» = `regime` (`passes_regime_gate`, maker cost + 50% de slack). O design usa o conjunto `{hurdle, regime, toxic_book, low_confidence, jev_late, hold}` e declara a fronteira dos gates de dimensionamento (`t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust`), que **não leem a resposta**. Mapeamento fiel ao Entra (as «5» do Entra são 4 gates + a redundância nominal). Sem-tela e sem nada do `## Não entra` no contrato, nas specs ou nas tasks.

## Rúbrica (1–7)

1. **Fidelidade ao briefing grelhado — PASS.** `Problema`, `História` e `Entra` copiados verbatim (diff por secção = IDENTICAL). Os 4 critérios observáveis do Entra estão traduzidos: (a) recusa por confiança com veredicto de custo/regime/toxicidade → `scalp-jev-entry-verdicts` Requisito 1 + cenário 1; (b) ciclo com resposta com origem da confiança e versão → `scalp-jev-entry-verdicts` Requisito 2 + `scalp-jev-model-version`; (c) toxicidade na faixa → indeterminada → `scalp-jev-toxicity-band`; (d) compra/venda não muda → `scalp-jev-entry-verdicts` Requisito 3 + `scalp-jev-call-timeout` Requisito 2 + tasks 6.1/6.3. O `Entra` do tempo limite (3 s) → `scalp-jev-call-timeout`.
2. **Escopo — PASS.** Nada do `## Não entra` entrou: limiar de confiança não muda (`CONFIDENCE_MIN` fica; só `not_applicable` quando removido); a pergunta ao modelo fica (`scalp-jev-model-version` Requisito 3); nada de painel/Monitor/`/api/scalp/status` (Requisito «log-only» + decisão 8); sem base de dados/dashboard/exportação/Drive/backtest; DEV-only (`RUN_SCALP_LOOP=1`, unit PROD intocado). Nenhuma task implementa algo fora do contrato visível.
3. **Contrato visível — PASS.** As decisões do dono estão no Apply contract com os valores exactos: faixa de toxicidade **só etiqueta** + decisão continua `book_toxic = (noul >= 0,5)`; cortes **0,4 / 0,6** (inclusive nos extremos); tempo limite **3 s** com a recusa **1,5 s** inalterada; versão fixa **nesta entrega** (nunca `jev-latest`) + versão que respondeu gravada em todo registro; veredicto dos gates no **mesmo** registro (recusado `scalp cycle refused` e enviado `scalp cycle sent`); **não-regressão** da decisão de compra/venda.
4. **Coerência interna — PASS.** Requisitos × cenários × tasks × decisões × riscos alinhados; nenhuma task fora do contrato visível; `tasks.md` não marcado. O spec de entrada e o design usam o mesmo conjunto de gates; o de timeout, o de toxicidade e o de versão não se contradizem com as decisões 1–8. Uma ressalva de completude (registro para fechos sem token de gate) fica em **P3 aceito** — não é contradição e não muda a decisão nem a aceitação.
5. **Tokens do gate no autor — PASS.** Em `design.md`, em linha própria parseável: `UI impact: none` · `live_route: N/A registro de veredictos em ficheiro de log; sem tela de produto` · `surface: new`. Sem rota de catálogo emprestada (declara explicitamente que nunca empresta `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`). Prototype **N/A** e Impeccable **N/A** declarados.
6. **Riscos e alternativas — PASS.** Cada decisão 1–8 tem alternativa rejeitada real (recalcular no serviço; prefixo novo; segundo registro; decidir pela faixa; manter o apelido; subir o `JEV_LATE_MS`; revisão visual; expor no Monitor). Riscos com mitigação: regressão da decisão (teste por cenário), divergência valor/origem (uma só função), faixa lida como mudança (cenário `noul = 0,45`), bloqueio do loop até 3 s (cadência 30 s), `last_jev_elapsed_ms` com latência real (default 30 s domina), quebra da régua (prefixo/chave preservados), versão pinada errada (valor do DEV + rollback por configuração). Nenhum risco é, na verdade, mudança de decisão de trading deixada em aberto.
7. **N/A (sem tela) — PASS.** Sem protótipo, sem acessibilidade visual, sem clone de página viva (nada de HTML/rota/landing); declarado explicitamente (Prototype N/A, Impeccable N/A, «sem rota autenticada, sem landing, sem HTML»).

## Achados

```
FINDING
gravidade: P3
classe: implementacao
conserto_obvio: sim
conserto_proposto: declarar no Apply contract o prefixo/`skip_reason` dos fechos com resposta que hoje não deixam registro (rejeição do broker, stand-in sem `live_send`, `rest_open` a bloquear o envio), para a cláusula "todo ciclo com resposta do modelo deixa um registro" ser implementável sem inventar chave
bloqueia_merge: nao
file: openspec/changes/card-1028-jev-veredictos-origem/tasks.md:10
summary: task 1.2 só nomeia refused/sent; `tick_user` fecha com `skipped=None` (logo sem registro) em rejeição do broker, stand-in sem `live_send` e `rest_open` a bloquear o envio (`scalp_service.py:813-818,1361`), fechos que existem com resposta do modelo
```

```
FINDING
gravidade: P3
classe: implementacao
conserto_obvio: sim
conserto_proposto: fixar no contrato que `skip_reason` fica imediatamente a seguir a `user=` (campos aditivos só depois), mantendo a adjacência que `RefusalRe` exige
bloqueia_merge: nao
file: scripts/scalp_jev_eval.py:92
summary: a régua do #1025 faz `RefusalRe.search(r"scalp cycle refused user=(\S+) skip_reason=(\S+)")`; o design deixa "ordem dos campos" como P3 e, se o Apply inserir campos aditivos antes de `skip_reason`, a régua deixa de ver as recusas
```

```
FINDING
gravidade: P3
classe: implementacao
conserto_obvio: sim
conserto_proposto: circunscrever o requisito ao registro de retorno e ao registro do ciclo (como já fazem os cenários), ou dizer que o registro de entrada leva a versão pedida, não a que respondeu
bloqueia_merge: nao
file: openspec/changes/card-1028-jev-veredictos-origem/specs/scalp-jev-model-version/spec.md:3
summary: "Every diagnostic record of a model call ... SHALL carry the model version that answered" inclui por letra o registro de entrada (`log_call_entry`), escrito antes da resposta e que não pode trazer a versão que respondeu
```

## P3 aceitos (detalhe de Apply)

- Prefixo/`skip_reason` dos fechos com resposta que hoje não deixam registro (rejeição do broker, stand-in sem `live_send`, `rest_open` a bloquear o envio) — a cláusula do contrato "todo ciclo com resposta do modelo deixa um registro" já os cobre na intenção; falta só o formato do nome. Resolvido no Apply.
- Adjacência `user= ... skip_reason=` na linha `scalp cycle refused` (campos aditivos depois) para a régua read-only do #1025 continuar a casar. Formato/ordem de chaves = P3 do autor; registado como aceito e verificado no Apply.
- Alcance do requisito de versão no registro de entrada (`log_call_entry`), que precede a resposta. Wording; os cenários já fecham no registro de retorno + registro do ciclo.
- Nomes/forma exacta das chaves dos veredictos (`hurdle=` … vs mapa `gates={...}`), separador e ordem; nome/valor concreto da versão pinada (facto de DEV) e se mantém override por env; nome da constante do tempo limite (3 s); conjunto exacto dos gates de dimensionamento; rótulo `unknown` sem `noul` e `not_applicable` com `SCALP_CONFIDENCE_MIN=none`; transporte de `model`/origem da confiança até ao serviço. Todos já declarados como P3 pelo autor.

## Veredito

`PASS`

Sem P0/P1/P2. Três P3 «detalhe de Apply», aceitos: ficam registados e resolvem-se no Apply, sem reabrir como P0/P1. Contagem: **P0 0 · P1 0 · P2 0 · P3 3**.
