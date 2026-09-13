## Why

No dsh web (`:3080`), com um card já em `Status=Design`, o root recusa a etapa **antes** de tentar o filho autor. Lê o stub Moore `context_file[Design]` (`Write produto deny` na mesma frase que manda sintetizar OpenSpec) como deny de OpenSpec e de spawn; lê «dsh não faz Design» (única `Cliente dsh:` hoje é grill); lê «Grok / OpenCode / dsh fora» (#880) como deny de T5/`G_design`. O Guard já permite OpenSpec em Design (`test_d7`). Workaround = outro cliente. Recidiva em todo card Design no dsh enquanto o stub empacotar as duas ordens na mesma frase.

## What Changes

- O stub yaml `context_file[Design]` deixa de ser lido como deny de OpenSpec / protótipo / spawn do autor. Continua a mandar sintetizar o issue grelhado e a **não** reentrevistar. MUST nomear OpenSpec/protótipo **allow**. `Write produto deny` permanece só para produto (`product_globs`).
- `page()` bound `q=Design` injeta esse stub; página ≤20 linhas; **não** lista `enabled_tools` (schema da página intacto; analogia #821).
- Uma linha prefixada `Cliente dsh:` na coluna/tabela Design do runbook `covenant-flow`: root **spawna** 1 Design-autor; o pai **não** escreve OpenSpec/protótipo no próprio turno (excepção continua: só `## Design Critique` depois do A/B); a linha grill **não** se aplica a Design. Linha `Cliente dsh:` da secção Grill-card intacta.
- No bloco Modos Cursor, «Grok / OpenCode / dsh fora» **não** é deny de T5/`G_design`. `G_design` mede ficheiros. Recorte #880 (InstantiationService / Landlock) intacto.
- Goldens pytest do stub Design + `page()` `q=Design` + needles do runbook. Homologação: dump autenticado **só no dsh** (`:3080`). Pytest não substitui. Dump noutro cliente não é critério.
- Nucleus via produto `oalansilva/covenant-flow` + `implantar --pin` no Cripto. Pin = próximo patch livre após origin (`v1.1.14` vigente). `clients.dsh.auto` permanece `false`.
- **Não** muda Σ / estado / evento / hook / `enabled_tools`. **Não** mexe `guard.py` `decide()` / `test_d7`. **Não** cresce `AGENTS.md`. **Não** dual-write lei em `.dsh/` / `.grok/` / `.opencode/`. **Não** reabre #689 / #839 / #821 / #880 como trabalho.

## Capabilities

### New Capabilities

- (nenhuma) — OpenSpec em Design já é allow no Guard; T5/`G_design` já mede ficheiros; este card alinha o stub Moore e o runbook para o modelo não recusar a coluna.

### Modified Capabilities

- `process-fsm`: `context_file[Design]` MUST mandar sintetizar o issue grelhado e não reentrevistar; MUST nomear OpenSpec/protótipo allow; MUST manter `Write produto deny` para produto. Sem estado/evento/`enabled_tools` novo. Spec actual **não** exigia `Write produto deny` no stub Design (isso era unbound); este card **mantém** a frase no Design e acrescenta o carve-out.
- `process-fsm-paging`: `page()` bound `q=Design` MUST conter o stub yaml (sintetizar + não reentrevistar + OpenSpec/protótipo allow + `Write produto deny`); MUST ter ≤20 linhas; MUST NOT listar `enabled_tools`. Compilador único; quatro injectores. Sem alargar o schema da página.
- `covenant-flow`: uma linha `Cliente dsh:` na coluna/tabela Design (root spawna 1 Design-autor; pai não escreve OpenSpec; grill exception não se aplica); linha grill intacta; bloco Modos Cursor diz que «Grok / OpenCode / dsh fora» não é deny de T5/`G_design`. Pin = próximo patch livre após `v1.1.14`. `clients.dsh.auto: false`. Dump autenticado `:3080` = DoD humano.

## Impact

- Altera (Apply, após Pronto para Dev): `.cursor/process-fsm.yaml` `context_file[Design]`, `.cursor/skills/covenant-flow/SKILL.md` (linha Design + frase T5 ≠ #880), goldens em `scripts/process-fsm` (`test_paging.py` e/ou `test_cursor_host_modes.py`). Nucleus via produto `oalansilva/covenant-flow` + `implantar --pin` no Cripto.
- Não toca `guard.py` `decide()`, `paging.py` schema (`enabled_tools` na página), `process_event.py`, Σ / transitions, `backend/` / `frontend/src/`, dual-write Hermes / stubs `.dsh/` `.grok/` `.opencode/`, Auto dsh, `unread_page()`, `AGENTS.md` (tamanho/substância), HTML / `DESIGN.md` de produto, #689 produto, #839 nascimento 400.
- `UI impact: none`. Prototype N/A. Impeccable/Playwright desta coluna = N/A.
- Origem: issue #899. Homologação: dump autenticado `http://127.0.0.1:3080` (ou `:3080`) de turno Design-bound em que o root **spawna** o autor (needle `design-autor` / `subagent`) **ou** o filho escreve sob `openspec/changes/`. Root a recusar só com as três leituras = falha. Ajudante que não abre depois de tentativa sem as três recusas **não** é falha deste card (Q4=A).
