## Context

Card [#899](https://github.com/oalansilva/crypto/issues/899). Status observado: **Design**. Briefing = issue grelhado (DoD completo; Q1–Q4 aceite Alan). Este Design **não** reabre as decisões de operador nem entrevista Alan. **Não** invoca `grill-card`.

Testemunha: recusa dsh no **#689**, 2026-09-11, `:3080`, **antes** de tentar o filho autor. Três leituras:

1. Página Design (`.cursor/process-fsm.yaml` `context_file[Design]`): `OpenSpec + crítica; sintetizar do issue grelhado, não reentrevistar. Write produto deny.`
2. «dsh não faz Design» — única linha `Cliente dsh:` hoje é grill (`dsh não spawna filho grill`) em `## Grill-card`.
3. «Design no dsh não conta» — bloco Modos Cursor: `Grok / OpenCode / dsh fora (InstantiationService e Landlock/`uid_map` são Cursor; #822 não autoriza alargar.)` Recorte **#880**, não T5.

O Guard **já** allow OpenSpec em Design: `test_d7_edit_openspec_design_allowed`; spec `process-fsm-guard` *Design OpenSpec write is not write_produto*. `enabled_tools[Design]` = `write_openspec, write_prototype, gist, task_critique`. `page()` injeta tupla + `enabled_events` + stub; **não** lista `enabled_tools`. Spec `process-fsm` exige sintetizar + não reentrevistar; **não** exige `Write produto deny` no stub Design (isso é unbound).

Mesma classe do **#821** (stub Moore unbound lido como deny de T16): carve-out no stub + uma linha no runbook; DoD humano = dump `:3080`; pin = próximo patch livre (Apply confere).

Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.14`, `clients.dsh.auto: false`.

UI impact: none
live_route: N/A harness-only; Moore stub and runbook text; no product route
surface: new

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Pedido de Design no dsh com card já em `Status=Design`: o root **não** termina o turno recusando só porque a página diz que produto é deny.
- Stub Design continua a mandar sintetizar o issue grelhado e a **não** reentrevistar; MUST nomear OpenSpec/protótipo **allow**; `Write produto deny` permanece só para produto.
- Root **spawna** 1 Design-autor; o pai **não** escreve OpenSpec/protótipo no próprio turno (excepção: só `## Design Critique` depois do A/B). Linha grill intacta; não se aplica a Design.
- «Grok / OpenCode / dsh fora» **não** é deny de T5/`G_design`. `G_design` mede ficheiros.
- Paging ≤20 linhas. Sem `enabled_tools` na página. Goldens pytest do stub + `page()` `q=Design`. Homologação = dump autenticado **só no dsh** (`:3080`).

**Non-Goals:**

- Guard `decide()` / `test_d7` (já allow). Deny de produto fora de I1 intacto.
- #689 produto (convite admin). Este card **não** escreve OpenSpec do #689.
- Conserto do nascimento vazio / 400 do filho isolado (#839) como trabalho.
- Conversa principal a escrever o Design se o ajudante não abrir (Q4=A: fica para outro card; nessa falha o operador ainda muda de cliente).
- Pai a escrever OpenSpec no próprio transcript no caminho feliz (Q2=A).
- Auto dsh (`clients.dsh.auto` permanece `false`).
- `AGENTS.md` always-on a crescer. Playbook de 12 colunas no stub. `unread_page()`. T7/T1/T15/T18. Estado/evento/hook/`enabled_tools` novo. Dual-write T0–T17.
- Código de serviço / ecrã fonte (`backend/` / `frontend/src/`). HTML / `DESIGN.md` de produto. Emprestar rotas de catálogo `/monitor` `/favorites` `/combo/*` ou `landing`. Impeccable/Playwright visual.
- Alargar o schema da página (listar `enabled_tools`; inject só no dsh). Analogia #821 rejeitou inventar aresta na página.

## Decisions

1. **Alavanca = rewording de `context_file[Design]` no yaml (compilador único `page()`).**  
   Recidiva: o modelo leu `Write produto deny` na mesma frase que manda sintetizar OpenSpec e recusou **antes** de tentar o filho. Ler `covenant-flow` **não** chega se o header ainda empacota as duas ordens. Inject só dsh seria dual-write da lei e deixaria Cursor/Grok/OpenCode com o stub antigo. Listar `enabled_tools` na página alargaria o schema (#821 rejeitou inventar aresta). `paging.py` já injeta o stub yaml verbatim — **não** muda o compilador neste card. **Escolha:** carve-out no stub yaml. Os quatro injectores passam a ver OpenSpec/protótipo allow sem despejar tools. Alternativa rejeitada: só skill. Alternativa rejeitada: inject dsh paralelo. Alternativa rejeitada: crescer `AGENTS.md`. Alternativa rejeitada: `unread_page()`.

2. **Texto pinado do stub Design (uma linha; página ≤20).**  
   `.cursor/process-fsm.yaml` `context_file[Design]`:

   `OpenSpec + crítica; sintetizar do issue grelhado, não reentrevistar. OpenSpec/protótipo allow. Write produto deny.`

   MUST conter `sintetizar`. MUST conter `não reentrevistar`. MUST conter a substring `OpenSpec/protótipo allow`. MUST conter `Write produto deny`. MUST NOT empacotar só `Write produto deny` sem o carve-out. `page()` bound `q=Design` MUST ter ≤20 linhas e MUST NOT conter `enabled_tools`. Envelope intacto (tupla, `enabled_events: recriticar, submeter_design, cancelar`, footer overlay on-demand). Alternativa rejeitada: duas linhas de runbook Design no stub (teto Moore). Alternativa rejeitada: listar `write_openspec` / `write_prototype` na página (schema). Alternativa rejeitada: tirar `Write produto deny` do stub Design (o Entra pede que permaneça para produto).

3. **Spawn vive no runbook, não no stub.**  
   `page()` corre no assemble; **não** vê o turno. O stub diz o que é allow/deny de escrita. Quem spawna é o root: uma linha `Cliente dsh:` na tabela de filhos / coluna Design. NLU ≠ δ continua. Chat «faz o Design» **não** é T5; é o pedido que autoriza spawnar o autor. Alternativa rejeitada: «root spawna» no stub Moore (mistura orquestração com paging; analogia #821). Alternativa rejeitada: o pai escrever OpenSpec no próprio turno (Q2=A).

4. **Linha pinada `Cliente dsh:` Design; grill intacta.**  
   Em `.cursor/skills/covenant-flow/SKILL.md`, imediatamente a seguir à tabela de filhos (a linha Design = «1 filho autor»), **uma** linha:

   `Cliente dsh: em Design, root spawna 1 Design-autor; o pai não escreve OpenSpec no próprio turno; a excepção grill não se aplica.`

   MUST ser prefixada `Cliente dsh:`. MUST mandar spawnar 1 Design-autor. MUST dizer que o pai não escreve OpenSpec no próprio turno. MUST dizer que a excepção grill não se aplica. Secção `## Grill-card` MUST conservar `Cliente dsh: dsh não spawna filho grill.` intacta. Excepção de escrita do pai continua: só `## Design Critique` depois do A/B (já no runbook). Alternativa rejeitada: apagar ou reescrever a linha grill. Alternativa rejeitada: ensinar o root a virar autor neste card (Q4=A).

5. **Modos Cursor: a mesma frase, ou a linha seguinte, não é T5.**  
   No bloco `## Modos Cursor (terminal vs Desktop+SSH)`, a frase `Grok / OpenCode / dsh fora (InstantiationService e Landlock/`uid_map` são Cursor; #822 não autoriza alargar).` permanece. Imediatamente a seguir (mesma frase **ou** linha seguinte):

   `«Grok / OpenCode / dsh fora» não é deny de T5/`G_design`.`

   Recorte #880 intacto (InstantiationService / Landlock no workbench Cursor). `G_design` continua a medir ficheiros (`proposal.md` + `design.md` + `tasks.md` + `specs/**` + clone gate). Alternativa rejeitada: apagar «dsh fora» (fura #880). Alternativa rejeitada: só o stub sem esta frase (terceira recusa da testemunha).

6. **Nucleo via pin; δ / Guard / produto UI intocados.**  
   `process-fsm.yaml` `context_file[Design]` e a skill `covenant-flow` são nucleus (`implantar --pin` copia). Apply: delta no produto `oalansilva/covenant-flow`, `git ls-remote --tags`, próximo patch livre após `v1.1.14`, rebase no tip (irmãos que partilham pele), `implantar --pin` no Cripto. `clients.dsh.auto: false`. MUST NOT editar `guard.py` `decide()`, `process_event.py`, `paging.py` (schema / `enabled_tools` na página / `UNBOUND_PAGE` / `unread_page()`), `backend/`, `frontend/src/`. `test_d7_edit_openspec_design_allowed` permanece verde sem mudança. Alternativa rejeitada: só patch no consumidor (o próximo `--pin` reverte o stub).

### Golden cases (pytest `scripts/process-fsm`, sem GitHub, sem dump live)

| # | Caso | Esperado |
| --- | --- | --- |
| G1 | yaml `context_file[Design]` | contém `sintetizar` e `não reentrevistar`; contém `OpenSpec/protótipo allow`; contém `Write produto deny`; **não** é só `Write produto deny` sem o carve-out |
| G2 | `page()` bound `q=Design` `card-<id>-*` | stub G1 no ctx; `q=Design`; ≤20 linhas; `enabled_events` presentes; `enabled_tools` **ausente** do ctx |
| G3 | `covenant-flow` tabela/coluna Design | linha prefixada `Cliente dsh:` com spawn 1 Design-autor e pai não escreve OpenSpec; «excepção grill não se aplica» |
| G4 | `covenant-flow` `## Grill-card` | `Cliente dsh: dsh não spawna filho grill.` intacta |
| G5 | `## Modos Cursor` | contém `Grok / OpenCode / dsh fora` **e** `não é deny de T5` / `G_design` no mesmo bloco ou linha seguinte |
| G6 | `test_d7_edit_openspec_design_allowed` | verde **sem** diff em `guard.py` `decide()` |
| G7 | `AGENTS.md` + stubs | `AGENTS.md` ≤40 linhas não vazias; stubs `.dsh/` `.grok/` `.opencode/` de `covenant-flow` ≤8; sem dual-write T0–T17 |
| G8 | overlay | `clients.dsh.auto` é false; `pin` = tag cravada após `v1.1.14` |

Homologação humana (não substitui G1–G8; bloqueia Auto): dump autenticado `http://127.0.0.1:3080` (ou `:3080`) dum turno Design-bound em que o root **spawna** o autor (needle `design-autor` / `subagent`) **ou** o filho escreve sob `openspec/changes/`. Root a citar `Write produto deny` / «dsh não spawna autor» / «não conta no T5» como motivo para **não** spawnar = falha. Pytest **não** substitui. Dump Cursor/Grok/OpenCode **não** é critério. Ajudante que **não abre**, depois de o root ter tentado sem recusar pelas três leituras, **não** é falha deste card (Q4=A).

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#899`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica. Este filho autor **não** chama `process_event`, **não** T5, **não** commit/push.
- (1) `.cursor/process-fsm.yaml` `context_file[Design]` = texto D2. **Não** editar `enabled_tools`, transitions, `unread_page()`, `UNBOUND_PAGE`. (2) `.cursor/skills/covenant-flow/SKILL.md`: linha D4 (tabela Design) + frase D5 (Modos Cursor). Linha grill (G4) intacta. (3) Goldens G1–G7 em `scripts/process-fsm` (`test_paging.py` e extensão de `test_cursor_host_modes.py` / `test_grill_card.py` conforme o sítio do needle). G6 = `test_d7` existente sem toque em `decide()`. (4) produto `oalansilva/covenant-flow`: mesmo delta + tag patch livre após `v1.1.14` + `implantar --pin` Cripto; `clients.dsh.auto: false` (G8).
- MUST NOT: Σ / yaml transitions / `enabled_tools` novo; `guard.py` `decide()`; `paging.py` schema; `backend/` / `frontend/src/`; Auto dsh; dual-write T0–T17; crescer `AGENTS.md`; rotas de catálogo / HTML / `DESIGN.md` de produto; OpenSpec do #689; conserto #839.
- Homologação: dump `:3080` (critério 6 do issue). Homologação ≠ `./restart`; 3080 ≠ systemd. Pytest **não** substitui o dump.

## Risks / Trade-offs

- [Stub mais longo ainda cabe em Lost in the Middle] → uma linha; teto ≤20; G2 conta linhas. Sem runbook Design no stub.
- [Linha `Cliente dsh:` Design vs linha grill] → G3/G4 fatiam secções; grill MUST NOT mudar. Prefixo igual, corpo distinto.
- [«dsh fora» #880 vs T5] → G5 afirma as duas needles no mesmo bloco; MUST NOT apagar a frase #880.
- [Próximo `--pin` reverte o stub se o produto não levar o delta] → D6: tag + pin. Irmãos na mesma pele: rebase no tip.
- [Ajudante isolado 400 / não abre] → Q4=A: **não** é falha deste card; fica noutro card (#839). Pass = root tenta o autor sem as três recusas.
- [Root a recusar só com as três leituras] → dump `:3080` falha. Goldens não substituem.
- [Chat «faz o Design» ≠ δ] → D3: wording autoriza **spawnar** o autor; `process_event submeter_design` continua a medir `G_design`. NLU ≠ δ para T1/T7/T15/T18/Write.
- [Cursor/Grok já cooperavam; o stub novo chega-lhes] → G1/G2 preservam sintetizar + não reentrevistar + `Write produto deny`. Risco de regressão = tirar o deny de produto; mitigado pelo needle `Write produto deny`.

## Migration Plan

Aditivo sobre `pin: v1.1.14`. Ordem Apply: stub yaml D2 + G1/G2 → skill D4/D5 + G3/G4/G5 → G6/G7 regressão → produto tag + `--pin` + G8. Sessões dsh já abertas mantêm o header antigo até novo assemble; não há migrate de banco. Rollback = pin anterior + revert do stub. Sem rebuild frontend. Homologação = dump `:3080` depois do pin, num card Design-bound (não o #689 produto).

## Open Questions

Nenhuma bloqueante (Q1–Q4 fechadas no issue). Residual: ajudante que não abre (#839 / outro card). `unread_page()` fora.

## UI impact

UI impact: none

## live_route

live_route: N/A harness-only; Moore stub and runbook text; no product route

## surface

surface: new

## Prototype

N/A — `UI impact: none`. Harness-only: stub Moore Design / runbook `covenant-flow`. Sem rota de produto. Sem clone de `/monitor` `/favorites` `/combo/*` ou `landing`. Sem HTML. Sem `DESIGN.md` de produto. Sem pipeline Impeccable visual. Playwright desta coluna = N/A.

## Prototype Validation

N/A — sem superfície visual de produto. Aceite = dump dsh `:3080` + goldens G1–G8, não um protótipo HTML.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Snapshot Impeccable = N/A justificado (sem tela Cripto; crítico desta rodada verifica tokens e escopo, não um snapshot visual).

## Design Critique

Crítico isolado (sem-tela, 1 critic). Conferido contra issue #899 (Q1=A três recusas; Q2=A root spawna 1 autor e o pai não escreve OpenSpec; Q3=A dump autenticado só no dsh `:3080`; Q4=A fallback 400 noutro card). Teto 1+1+1. Sem segundo rework.

### Tokens: PASS

- `UI impact: none`
- `live_route: N/A harness-only; Moore stub and runbook text; no product route`
- `surface: new`

Linhas próprias e parseáveis. Sem-tela: ausência + justificativa curta; **não** empresta `/monitor`, `/favorites`, `/combo/*` nem `landing`. Prototype / Impeccable / Playwright desta coluna = N/A justificado. copied vs generated = N/A (sem proto).

### P0

Nenhum.

### P1

Nenhum.

### P3 (aceitos para Apply)

- Sítio exacto da linha `Cliente dsh:` (logo após a tabela de filhos vs `### Design — teto e validação`).
- Goldens G1–G5: `test_paging.py` vs extensão de `test_cursor_host_modes.py` / `test_grill_card.py`; G5 = mesma frase ou linha seguinte.
- Tag patch livre após `v1.1.14` (`git ls-remote --tags`); sessões dsh já abertas com header antigo até novo assemble.
- `tasks.md` 1.3: «`fsm.py` (exceto o yaml stub)» — o stub vive em `.cursor/process-fsm.yaml`.

sem P0/P1; P3 aceitos para Apply. Residual Q4=A / #839 fora do Entra.
