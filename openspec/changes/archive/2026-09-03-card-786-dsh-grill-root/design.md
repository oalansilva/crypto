## Context

Card [#786](https://github.com/oalansilva/crypto/issues/786). Pele dsh already-on pinada no Cripto em `v1.1.1` (#784). Q1–Q6 da grelha estão fechadas no issue (todas A); este Design não as reabre. Relacionado e **não** reaberto: #608, #720, #773, #782, #784, #755. Não re-grelhar #701.

Plugin live `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt", "skills"]`. `tools/pre-execute` corre `isCordisRestricted` (só `cordis_*`) depois `runGuard` + `denyFromDecision` (write-like fail-closed). `subagent` **não** é write-like (`WRITEISH` = `write`/`edit`/`bash` + `str_replace_editor` mutante); hoje o spawn **allow** e chama `next()`. Deny listener **antes** de `registerProvider`; try/catch para throw do provider não saltar o deny. Esse contrato #784 MUST permanecer.

Lei live do host (`/tmp/deepseek-harness`, não vendorar): `ToolExecution.arguments` é objeto JSON já parseado (`unknown`, lossless JSON). Schema `tool-subagent`: campos de topo `description` (3–5 palavras, display) e `prompt` (tarefa autocontida); `run_in_background` opcional. Preset `standard` expõe `subagent` **e** `subagent_fork` (`toolName` no yaml). `backgroundMode: continuable` no web → default background. Só `agents.roots()` pode `ctx.userQuestions.ask()`; owned child = `DELEGATED_CALLER` (rejeição antes do provider UI). Docs: `docs/subsystems/user-questions.md`.

Fixture negativa `session-5a6c8c5c-c041-4a1e-9f7f-f830f0c7054b` (dump `/tmp/dsh-session-5a6c8c5c.jsonl`): cwd `/srv/apps/dev/criptofarol/source`, `delegationDepth=0`, preset `standard`, “refine o card 701”. Root: `skill` `covenant-flow` → `read` canónico grill-card → `tool/call` `subagent` com `arguments` `{"description":"grill-card 701","prompt":"#701 — grill-card (isolado)\n..."}`. **0×** `ask_user_question`. Child `0be27c63-f361-4c57-92bc-e2d92d5d3f65`: `delegationDepth=1`, `mode=continuable`, `provider=spawn`; `gh issue edit 701` + comentário canónico T1; **0×** ask. Causa: MUST Read do canónico Cursor (“pai spawna”). Isolamento Cursor: `.cursor/hooks.json` `preToolUse` matcher `Write|StrReplace|Delete|EditNotebook` **não** vê `Task`; o plugin dsh **não** corre no Cursor. OpenCode chama `runGuard` em todo `tool.execute.before` — por isso a regra **não** pode viver em `guard.py` `decide()` (Task deny fora de escopo).

Needles #755 live em `scripts/process-fsm/test_grill_card.py`: `HOST_TOOLS`, `DOD_NEEDLES`, pai relaying `todas as options` / `não colapsa`, child/Grok stubs **não** nomeiam host tool, vendor Matt intacto. Overlay Cripto `pin: v1.1.1`. `dsh_stubs.py` / `AGENTS.md` / `grok_stubs.py` / `process-fsm.yaml` **não** são a alavanca deste card.

**UI impact: none.** Harness/hooks/docs de processo. Nenhuma rota, shell, componente ou copy de produto.

## Goals / Non-Goals

**Goals:**

- No dsh, grelha em Em Refinamento pergunta na GUI (`ask_user_question` no **runtime root**) **antes** do comentário canónico T1.
- Root executa `skill` grill-card + grilling e `gh issue edit`. MUST NOT `subagent` / `subagent_fork` grill-shaped, inclusive `run_in_background: false`.
- Lei no canónico com ramo **rotulado de cliente** (Cursor/Grok/OpenCode não aplicam “nunca spawnar”).
- Fail-closed: spawn grill-shaped deny no plugin mesmo se o modelo ignorar a skill. Fail-open: `subagent` não-grelha continua.
- Pin produto `v1.1.2` → Cripto. Goldens pytest do deny + needles #755 verdes. Write deny #784 não regride.

**Non-Goals:**

- Reabrir #608/#720/#773/#782/#784/#755. Re-grelhar #701. Vendorar `deepseek-harness`. Auto dsh. Dual-write T0–T17. Mudar `process-fsm.yaml` / Σ / colunas.
- Deny **global** de todo `subagent`. Deny de `Task` / `spawn_subagent` no Cursor/Grok. Matcher novo no `.cursor/hooks.json`. Regra nova em `guard.py` `decide()`.
- Excepção / stubs longos em `dsh_stubs.py`. Linha de grelha no `AGENTS.md`. Editar `grok_stubs.py` ou nomear host tool em `.grok/skills/*`.
- Porta 3080 em `environments.dev.services` / systemd. Produto `backend/` / `frontend/src/`. UI / HTML. Pin major. Dump D5 como caminho feliz dsh.

## Decisions

1. **Q1 — dsh runtime root executa a grelha; MUST NOT spawn.**  
   O root lê a skill, corre grilling, edita o body, chama `ask_user_question` (N≥2, `(Recommended)` primeiro; Other não conta). Sem dump D5. Alternativa rejeitada: `subagent` blocking (`run_in_background: false`) — o filho continua `DELEGATED_CALLER`. Alternativa rejeitada: relay D5 via continuable (Q1≠C).

2. **Q2 — DoD humano = dump autenticado `:3080`; goldens pytest também.**  
   PASS humano: um turno «refine/grelha o card N» (N em Em Refinamento, fronteira com decisão, plugin pinado, cwd = `canonical_paths.dev`, preset `standard`) com `tool/call` `ask_user_question` no root **antes** de qualquer comentário canónico T1 novo, e **sem** `subagent`/`subagent_fork` grill-shaped. Fixture `5a6c8c5c` = só o furo (0× ask, 1× continuable). Homologação ≠ `./restart`; 3080 ≠ systemd; **não** bloqueia T14. Apply ainda exige goldens G1–G11 (plugin `apply` + N2/N3). Alternativa rejeitada: só dump, sem pytest.

3. **Q3 — #755 inalterado; sem sessão live Cursor/Grok.**  
   `HOST_TOOLS`, `DOD_NEEDLES`, pai spawn, child MUST NOT chamar host, Grok stubs sem host tool, `grok_stubs.py` intocado. Frontmatter `grill-card` **pode** continuar a falar em spawn prompt.

4. **Q4 — texto canónico com dois ramos rotulados; copy spawn/host/D5 só em Cursor e Grok (match markdown-insensitive).**  
   Headings **exactos**: `## Cliente: Cursor e Grok` e `## Cliente: dsh`. Copy **live hoje** (ênfase markdown): Precondição `Este filho escreve o body de N e **não** chama a ferramenta do host.`; Perguntas H2 **`## Perguntas da rodada (host)`** (não `## Perguntas da rodada`); `O filho **não** chama a ferramenta do host.`; `Quem chama \`AskUserQuestion\` (Cursor) / \`ask_user_question\` (Grok) é o **pai**.`. N2 usa `_plain()` (lowercase; colapsar whitespace; strip `*` / `**` / `_word_`; strip backticks; MUST NOT apagar `_` em `ask_user_question`) — um `_plain` no-op `lower+whitespace` **passa** o copy live `**não** chama` ainda em Precondição; o P1 é o primeiro fixture de D10.  
   Depois do Apply, essas frases (após `_plain`) MUST viver **somente** sob `## Cliente: Cursor e Grok`. `## Precondição` MAY manter Status=`Em Refinamento` + id N; após `_plain` MUST NOT conter `filho`, `spawna`, `relaying`, `dump d5`, `ask_user_question`, `askuserquestion`, `não chama`. O H2 `## Perguntas da rodada` / `## Perguntas da rodada (host)` MUST NOT permanecer secção **partilhada** de topo: **mover** o corpo para debaixo de Cursor e Grok (MAY `###` nested) **ou** substituir por dois ramos rotulados. `## Cliente: dsh` após `_plain` MUST conter a substring **contígua** `root chama ask_user_question`; MUST NOT conter `não chama ask_user_question`; MUST NOT conter `não chama a ferramenta do host`. (Tokens `root` e `chama ask_user_question` **separados** GREEN-em-falso: `root nunca chama ask_user_question` e `root não chama.` … `chama ask_user_question` — D10 RED.) Sinónimos (`não pergunta`, etc.) ficam P2 / dump 8.1. `_plain` strip backticks: `O runtime root chama \`ask_user_question\`.` casa `root chama ask_user_question`. Como (DoD / `gh issue edit`) MAY ficar partilhado **sem** essas frases. Covenant-flow Grill-card: uma linha `Cliente dsh:`. Stubs thin; `dsh_stubs.py` intacto.

5. **Q5 — `AGENTS.md` não cresce.**  
   Sem linha de grelha dsh no stub always-on. Lei fica na skill (on-demand) + Guard (fail-closed).

6. **Q6 — deny no plugin dsh, não em `decide()`.**  
   `tools/pre-execute` deny `subagent` e `subagent_fork` quando a heurística grill-shaped bate. **Não** Cursor/Grok hook. **Não** `guard.py` `decide()` (OpenCode `runGuard` em todo `tool.execute.before` transformaria isto em Task deny). `isCordisRestricted` **não** ganha o matcher (só `cordis_*`).

7. **Pin `v1.1.2`, mesma ordem que #784.**  
   Overlay live `pin: v1.1.1`. Canal: produto `oalansilva/covenant-flow` depois `implantar --pin`. Patch, não major (`SCHEMA_MAJOR` 1; `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`). Sem evidência de tag intermédia. Teste `test_pin_copies_dsh_without_injecting_clients_dsh` live crava `v1.1.1`; Apply MUST subir o esperado para `v1.1.2`.

8. **Heurística de deny (pinada) — só JS do plugin, nunca `decide()`.**  
   O deny grill-shaped **nasce** em `isGrillShapedSpawn(tool, args)` em `dsh_plugin_lib.js`, chamado por `.dsh/plugin/process-fsm-guard.js` no listener `tools/pre-execute` **antes** de `runGuard` / `decide()`. `guard.py` **MUST NOT** aprender este matcher (`decide()` inalterado). G1–G9 que passassem só porque `decide()` deny deixariam o OpenCode `tool.execute.before` a deny `Task`/`task` com prompt `grill-card` e partiriam #755.
   - **Tools:** nome exacto `subagent` **ou** `subagent_fork`. Qualquer outro nome (incl. Cursor `Task`, Grok `spawn_subagent`, OpenCode `task`, `write`) → esta regra não deny.
   - **Needle:** substring `grill-card` após `toLowerCase()`, via `String.prototype.includes` — **não** regex, **não** `grill_card` / `grill card`.
   - **Campos (shape live 5a6c8c5c + `ToolExecution.arguments` objeto):** se `args` é objecto, concatenar strings `args.description` e `args.prompt`. Se `args` é string, `JSON.parse`; parse fail → varrer a string crua. **Nested:** também `JSON.stringify(args)`.
   - **`run_in_background`:** irrelevante para o match.
   - **Mensagem:** `{ kind: "deny", reason: "process-fsm-guard deny reason=dsh_grill_spawn" }`. `next()` **não** é chamado.
   - **Fail-open:** `subagent` sem o needle → (3) `runGuard` → não write-like → `next()`.
   - Alternativa rejeitada: matcher em `guard.py` `decide()`. Alternativa rejeitada: só unitário Python/`isGrillShapedSpawn("Task")===false` sem passar pelo `apply` do plugin.

9. **Ordem em `apply(ctx)` e prova G1–G9 pelo plugin JS.**  
   Ordem do listener: (1) `isGrillShapedSpawn` deny; (2) `isCordisRestricted`; (3) `runGuard` + `denyFromDecision`; (4) `next()`. Secções 40/50 e `registerProvider` **depois** do listener, try/catch intacto. **G1–G9 MUST** `import { apply } from` `.dsh/plugin/process-fsm-guard.js` e disparar `ctx.events["tools/pre-execute"]` (mesmo padrão que `test_plugin_deny_on_illegal_product_write_without_throw` / D13) — **não** um teste de helper Python que Apply pudesse meter em `decide()`. G10 MAY unit-test o helper **JS**. G5 MUST incluir Cursor `Task`, Grok `spawn_subagent` **e** OpenCode `task` com prompt contendo `grill-card` e afirmar `nextCalled === true` **via esse `apply`+pre-execute** (prova que `decide()` não ganhou match prompt-wide). G11 (barato): `decide()` Python em payload sem path, `tool=Task`, prompt com `grill-card` continua `permission: allow` (sem evento FSM novo).

10. **Needles N2 — `_plain()` congelado; substring contígua dsh; Precondição Status+id.**  
    Em `test_grill_card.py` definir `_plain(text)`: lowercase; colapsar whitespace; strip ênfase `*` / `**` / `_word_`; strip backticks; MUST NOT apagar `_` dentro de `ask_user_question`. Unit asserts **exactos** (um `_plain = lower+whitespace` no-op **falha** o primeiro):

    ```
    assert "não chama a ferramenta do host" in _plain("**não** chama a ferramenta do host")
    assert _plain("ask_user_question") == "ask_user_question"
    assert "o pai spawna" in _plain("O **pai** spawna")
    ```

    N2 no ficheiro (após `_plain`): `full.count(frase) == cursor.count(frase)` e `cursor.count >= 1` para `não chama a ferramenta do host`, `o pai spawna`, `dump d5`, `quem chama`.  
    `## Cliente: dsh` após `_plain`: MUST conter a substring **contígua** `root chama ask_user_question`; MUST NOT conter `não chama ask_user_question`; MUST NOT conter `não chama a ferramenta do host`. RED fixtures (tokens separados GREEN-em-falso):

    ```
    assert "root chama ask_user_question" not in _plain("O runtime root nunca chama ask_user_question.")
    assert "root chama ask_user_question" not in _plain("O runtime root não chama. chama ask_user_question.")
    assert "root chama ask_user_question" in _plain("O runtime root chama `ask_user_question`.")
    ```

    Sinónimos (`não pergunta`, etc.) ficam P2 / dump 8.1.  
    `## Precondição` após `_plain`: MUST NOT conter `filho`, `spawna`, `relaying`, `dump d5`, `ask_user_question`, `askuserquestion`, `não chama`.  
    H2 `perguntas da rodada` (com ou sem `(host)`) fora dos dois H2 cliente → fail. Nested `###` permitido. N1/N3 inalterados.

### Golden cases (pytest `scripts/process-fsm`, sem GitHub)

G1–G9: **obrigatório** `import { apply } from` `.dsh/plugin/process-fsm-guard.js` + `ctx.events["tools/pre-execute"]` (como D13 / deny-write #784). **Proibido** satisfazer G1–G9 só com unitário Python/`decide()`.

| # | Caso | Esperado |
| --- | --- | --- |
| G1 | `apply` + `pre-execute` `subagent` `arguments: { description: "grill-card 701", prompt: "…" }` | `{ kind: "deny" }`, reason contém `dsh_grill_spawn`, `nextCalled === false` |
| G2 | idem `subagent_fork` needle só em `prompt` (`Grill-Card`) | deny, `next` não chamado |
| G3 | mesmo G1 com `run_in_background: false` | deny (Q1: nem blocking) |
| G4 | `apply` + `subagent` sem needle | `next()` chamado |
| G5 | `apply` + `pre-execute` para `Task`, `spawn_subagent` **e** OpenCode `task`, cada um com `prompt` contendo `grill-card` | `nextCalled === true` em **todos**; reason **não** é `dsh_grill_spawn` |
| G6 | `apply` + `arguments` string JSON `{"description":"grill-card 701","prompt":"x"}` | deny |
| G7 | `apply` + `edit` produto ilegal | deny write; `next` false |
| G8 | `apply` + `cordis_define` | deny `cordis_restrict` |
| G9 | `registerProvider` throw + G1 e G7 no mesmo `apply` | `apply` não throw; ambos deny; `next` false |
| G10 | `isGrillShapedSpawn` **JS** unitário (objecto/string/nested; negativo `grill_card`) | só `grill-card` (case-insensitive) é true; **não** substitui G1–G9 |
| G11 | Python `decide({tool: "Task", args: {prompt: "grill-card 701"}})` sem path | `permission: allow` (sem evento FSM novo; prova que `decide()` não deny prompt-wide) |
| N1 | `test_grill_card.py` #755 (`HOST_TOOLS`, `DOD_NEEDLES`, Grok stubs, vendor Matt) | verdes |
| N2 | `_plain` fixtures (**não** + RED contíguo); count exclusivo das quatro frases no Cursor e Grok; dsh tem substring contígua `root chama ask_user_question` e não tem `não chama ask_user_question` / host-prohibition; Precondição sem `filho`/`spawna`/`relaying`/`dump d5`/`ask_user_question`/`askuserquestion`/`não chama`; H2 Perguntas (host) não fica irmão de Precondição; covenant-flow `Cliente dsh:` | verdes |
| N3 | `guard.py` fonte **sem** `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`; `dsh_stubs.py` / `grok_stubs.py` / `process-fsm.yaml` inalterados; `AGENTS.md` ≤40 sem `ask_user_question`; stub dsh grill-card ≤8 + MUST Read | verdes |
| P1 | pin-test `implantar --pin` (quando `install.sh` existe) | espera `v1.1.2`; `clients.dsh.auto: false` |

## Apply contract

- Ordem: (1) commit no produto `oalansilva/covenant-flow` tag **`v1.1.2`**; (2) `implantar --pin v1.1.2` no Cripto. Zero produto UI.
- Deny grill-shaped: **somente** `isGrillShapedSpawn` em `dsh_plugin_lib.js` chamado de `.dsh/plugin/process-fsm-guard.js` **antes** de `runGuard`. `guard.py` `decide()` MUST NOT ganhar o matcher (ficheiro inalterado; N3 lê a fonte).
- Skills: copy spawn/host/D5/`**não** chama` **somente** sob `## Cliente: Cursor e Grok`. `## Precondição` só Status+id N (após `_plain` sem `filho`/`spawna`/`relaying`/`dump d5`/`ask_user_question`/`askuserquestion`/`não chama`). H2 Perguntas (host) **não** fica partilhado. `## Cliente: dsh` tem substring contígua `root chama ask_user_question`; sem `não chama ask_user_question`. Uma linha `Cliente dsh:` em covenant-flow.
- Goldens: G1–G9 via `import { apply } from` o plugin JS; G5 `Task`/`spawn_subagent`/`task` + `next()`; G11 `decide()` allow; N2 `_plain` com fixtures **não** + RED contíguo `root chama ask_user_question` + exclusão das quatro frases + Precondição Status+id + H2 Perguntas; N3 `guard.py` sem needle. G10 JS MAY. **Não** editar `guard.py`, `.cursor/hooks.json`, `dsh_stubs.py`, `grok_stubs.py`, `process-fsm.yaml`, `AGENTS.md`.
- Cripto no pin: `.dsh/` + skills canónicas + `scripts/process-fsm/` atualizados; overlay `pin: v1.1.2`; `clients.dsh.auto: false`.
- Homologação (não bloqueia apply/T14; bloqueia Auto): dump autenticado `:3080` (Q2). Fixture `5a6c8c5c` não substitui.

## Risks / Trade-offs

- [Skill canónica lida por Cursor/OpenCode/Grok] → N2 usa `_plain()` (live `**não** chama` e H2 `## Perguntas da rodada (host)`). Residual aceite: modelo ignora o rótulo — Guard Cursor não deny `Task`.
- [Needle `includes('grill-card')`] → falso positivo se um `subagent` legítimo citar a skill no prompt. Aceite (Q6 fail-closed). Falso negativo `grill_card` aceite. Residual: description `refine 701` sem substring — só a skill + DoD humano.
- [arguments string vs objecto] → G1 objecto; G6 string do dump. Residual: host muda o campo `arguments` — dump Q2 falha visível.
- [OpenCode `runGuard` em todo tool] → matcher **fora** de `decide()`; G5+G11+N3 fecham o atalho Python. Residual aceite: Apply que “simplifica” para `decide()` falha G5/G11/N3 visível.
- [Plugin omitido / `--patch` ausente] → spawn allow (#782). Residual aceite; DoD humano exige plugin pinado.
- [Homologação `:3080`] → cwd canónico DEV ≠ worktree; 3080 ≠ systemd; ≠ `./restart`. Residual 8.x: turno com fronteira de decisão real; Alan responde na GUI. Não bloqueia T14.
- [Canonical comment vs rodada aberta] → skill: não postar T1 novo enquanto Qs abertas. Residual: modelo posta na mesma; Guard **não** intercepta `gh` comment (fora de Q6). DoD humano + needles de texto.
- [Pin-test `v1.1.1`] → Apply actualiza para `v1.1.2` ou o teste falha visível (não é buraco live se P1 for seguido).
- [Stubs Grok e description] → se o canónico mudar a `description` YAML, `grok_stubs.py` CI falha até regenerar. Apply MUST NÃO mudar description **ou** regenerar stubs thin sem host tool.

## Migration Plan

Aditivo sobre `v1.1.1`. Ordem Apply: (1) helper JS + G10; (2) plugin listener **antes** de `runGuard` + G1–G9 **via `apply`** + G5/G11/N3; (3) skills: copy live-bold **somente** sob Cursor e Grok; H2 Perguntas (host) não fica partilhado; `_plain` N2; (4) tag `v1.1.2`; (5) pin Cripto. Rollback = pin `v1.1.1`. Sem migration de banco. Sem rebuild frontend. Homologação = dump `:3080`, não `./restart`.

## Open Questions

Nenhuma bloqueante (Q1–Q6 = A). P0 r5 (tokens `root`+`chama ask_user_question` separados) fechado: N2 exige substring contígua `root chama ask_user_question`. Residuais P2 / dump 8.1: sinónimos (`não pergunta`).

## UI impact

**none** — harness/skills/plugin de processo. Nenhuma rota, shell, componente ou copy de produto. Nenhuma superfície visual nova ou alterada. O aceite visível é o card `ask_user_question` na GUI dsh, não uma tela Cripto.

## Prototype

N/A — `UI impact: none`. Não há tela Cripto a prototipar; o aceite é ritual dsh (root pergunta, Guard deny spawn grill-shaped) + texto canónico rotulado. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Detector Impeccable da pele dsh permanece o de #782/#784; este card não o altera.

## Design Critique

- **P0:** nenhum (r6).
- **P1 r1 (closed):** deny grill-shaped podia nascer em `guard.py` `decide()` (OpenCode negaria `Task`). Disposition: **closed** — G1–G9 via `import { apply }` do plugin JS; G5 `Task`/`spawn_subagent`/`task` + `next()`; G11 `decide()` allow; N3 fonte de `guard.py` sem needle.
- **P1 r2–r5 (closed):** N2 presença-only / substring unbolded / `_plain` no-op / tokens `root`+`chama ask_user_question` separados. Disposition: **closed** — `_plain` com fixtures `**não** chama`; exclusão das frases só em `## Cliente: Cursor e Grok`; Precondição Status+id; H2 Perguntas não partilhado; contig `root chama ask_user_question` + RED `nunca`/frase partida.
- **P2 (accepted-residual):** sinónimos (`não pergunta`); modelo ignora ramo rotulado (Guard Cursor não deny `Task`); linha `Cliente dsh:` vs tabela «1 filho»; FN `includes('grill-card')`; plugin omitido; 8.1 dump `:3080` não bloqueia T14; `AskUserQuestion` no dsh; MAY vs SHALL `gh issue edit`.
- **P3 (accepted-residual):** envelope `questions[]`; G10 MAY vs 4.3; frontmatter spawn prompt; pin-test live ainda `v1.1.1` até Apply.
- Prototype: N/A — harness, sem superfície visual.
- Snapshot: `.impeccable/critique/786-card-786-dsh-grill-root-A.md` e `…-B.md` (r6 **PASS**). Apply e Code Review não lêem essa pasta.
- **Design Agent verdict: PASS**
