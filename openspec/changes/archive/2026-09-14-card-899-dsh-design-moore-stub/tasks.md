Ponto de partida Apply (após Pronto para Dev no mesmo chat `#899`): `openspec/changes/card-899-dsh-design-moore-stub/design.md` Apply contract (D1–D6, G1–G8). Skills: `.cursor/skills/openspec-apply-change`, `covenant-flow`. Zero produto UI. Sem `process_event` neste ficheiro. Design **não** aplica.

## 1. Stub Design (`context_file[Design]`)

- [x] 1.1 `.cursor/process-fsm.yaml` `context_file[Design]`: substituir pelo texto pinado em D2 (`sintetizar`; `não reentrevistar`; `OpenSpec/protótipo allow`; `Write produto deny`)
- [x] 1.2 **Não** editar `enabled_tools`, transitions, estados, eventos, hooks; **não** listar `enabled_tools` na página; **não** editar `paging.py` (`UNBOUND_PAGE`, `unread_page()`, schema)
- [x] 1.3 **Não** editar `guard.py` `decide()`, `process_event.py`, `fsm.py` (exceto o yaml stub)

## 2. Skill canónica (Design + Modos Cursor)

- [x] 2.1 `.cursor/skills/covenant-flow/SKILL.md`: imediatamente a seguir à tabela de filhos, a linha pinada D4 (`Cliente dsh: em Design, root spawna 1 Design-autor; o pai não escreve OpenSpec no próprio turno; a excepção grill não se aplica.`)
- [x] 2.2 `## Grill-card`: conservar `Cliente dsh: dsh não spawna filho grill.` intacta
- [x] 2.3 `## Modos Cursor`: conservar `Grok / OpenCode / dsh fora`; acrescentar a frase D5 (`«Grok / OpenCode / dsh fora» não é deny de T5/`G_design`.`) na mesma frase ou na linha seguinte
- [x] 2.4 `AGENTS.md` **não** cresce. Stubs `.dsh/` `.grok/` `.opencode/` de `covenant-flow` intactos (≤8, MUST Read). Sem dual-write T0–T17

## 3. Goldens pytest `scripts/process-fsm`

- [x] 3.1 G1: yaml `context_file[Design]` — `sintetizar`; `não reentrevistar`; `OpenSpec/protótipo allow`; `Write produto deny`; não empacota só o deny sem carve-out
- [x] 3.2 G2: `page()` bound `q=Design` — stub G1 no ctx; `q=Design`; ≤20 linhas; `enabled_events` presente; `enabled_tools` ausente
- [x] 3.3 G3/G4: skill Design `Cliente dsh:` spawn 1 Design-autor + pai não escreve OpenSpec + excepção grill não se aplica; Grill-card `Cliente dsh: dsh não spawna filho grill.` intacta
- [x] 3.4 G5: `## Modos Cursor` contém `Grok / OpenCode / dsh fora` **e** `não é deny de T5` / `G_design`
- [x] 3.5 G6: `test_d7_edit_openspec_design_allowed` verde **sem** diff em `guard.py` `decide()`. G7: `AGENTS.md` ≤40; stubs ≤8. `pytest scripts/process-fsm -q` sem GitHub

## 4. Produto covenant-flow + pin Cripto

- [x] 4.1 Commit no repo `oalansilva/covenant-flow` (yaml stub Design + linhas skill + goldens) após rebase no tip. Tag = próximo patch livre após `v1.1.14` (`git ls-remote --tags`); não major; não mover `v1.1.14`. Irmãos que tocam o mesmo nucleus — MUST NOT reverter haystacks; se já landed, a tag pinada MUST conter os deltas
- [x] 4.2 `implantar --pin` da tag de 4.1 no Cripto; overlay `pin` = essa tag; `clients.dsh.auto: false` (G8). `install.sh --pin` continua a copiar `.dsh/`; `SCHEMA_MAJOR` 1; `CLIENT_KEYS` três
- [x] 4.3 Não ligar Auto dsh; não systemd 3080; não reabrir #689/#839/#821/#880 como trabalho; não editar `backend/` / `frontend/src/`

## 5. Verificação

- [x] 5.1 `openspec validate card-899-dsh-design-moore-stub --type change --strict` verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 5.2 Stubs `.dsh/skills/` ≤8; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh; `unread_page()` / `UNBOUND_PAGE` intactos; `decide()` intacto; Σ/`enabled_tools` intactos

## 6. Homologação humana (Design especifica; Apply/homologação executa; **não** opcional)

- [x] 6.1 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` (ou `:3080`) dum turno Design-bound (`q=Design`, `bound_card=<id>`, `q_git=card-<id>-*`): o root **spawna** o autor (needle `design-autor` / `subagent`) **ou** o filho escreve sob `openspec/changes/`; **não** deny textual só com `Write produto deny` / «dsh não spawna autor» / «não conta no T5». Pytest G1–G8 **não** substituem este dump. Dump Cursor/Grok/OpenCode **não** é critério. Ajudante que **não abre**, depois de o root ter tentado sem as três recusas, **não** é falha deste card (Q4=A). Homologação ≠ `./restart`; 3080 ≠ systemd. MUST NOT tratar como residual opcional nem como Done só com golden. MUST NOT escrever OpenSpec do #689 nem consertar #839 neste card.

Evidência Apply 2026-09-11: `127.0.0.1:3080` LISTEN (não systemd). Sem cookie: HTTP 401 `dsh web authentication required`. Com cookie de sessão: HTTP 200, HTML `DeepSeek Harness` (24232 B). Browser MCP desta coluna não anexou tab (`No browser tab available`). Sem turno Design-bound (`q=Design`) neste filho Apply; ajudante não abriu. Q4=A — não P0 desta coluna; pytest G1–G8 não substituem o dump. Isolate não bounced; homologação ≠ `./restart`. Sem OpenSpec #689; sem conserto #839.
