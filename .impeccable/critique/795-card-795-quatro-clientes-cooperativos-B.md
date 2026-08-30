# Snapshot — card #795 `card-795-quatro-clientes-cooperativos` (Assessment B)

- Card: #795
- Change: `card-795-quatro-clientes-cooperativos`
- Critic: isolated Design Critic B (detector posture; no transcript inherit; no Assessment A)
- UTC: 2026-08-30T00:01:50Z
- Tuple: hooks `q=None` `bound_card=⊥` `q_git=develop` (sessão unbound). Write produto deny. Esta onda só `.impeccable/critique/**`.
- Board Project 1 Status=**Design**. Q1–Q4 congeladas **A**.
- UI impact: **none** (claim Auto no overlay + texto hardcoded de `render_agents()` / `AGENTS.md` / bloco README do produto `oalansilva/covenant-flow`; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-795-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Sem superfície visual nova ou alterada. Impeccable visual / `DESIGN.md` / Playwright desta coluna = N/A. Detector de pele (hook.mjs) **não** é o objeto deste card.
- `design.md` sha256: `2206886e474fd54df969c94ba8257924a8d00e814ba0260b97a3a097a384aaa2` (1507 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + spec deltas `covenant-flow` + `process-harness`)
- `openspec validate card-795-quatro-clientes-cooperativos --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).
- Browser gate: **N/A (no UI)**.

---

## Brief

Alan opera quatro clientes com a mesma lei, mas o Cursor é a exceção no *claim* Auto (overlay Cripto `clients.cursor.auto: true` + stub «Auto permitido»). Grok, OpenCode e dsh já são cooperativos até ensaio deny. Card #795: contrato yaml+stub cooperativo; `render_agents()` hardcode quatro cooperativos (yaml **não** interpola); README bloco Clientes no mesmo tag/pin; tag patch (esperado `v1.1.5`); pin Cripto `clients.cursor.auto: false`. Não reabre #787 como Apply nem #784/#782 (peles). Auto IDE/CLI fora. `UI impact: none`.

Audience: Alan nos quatro clientes + visitante do GitHub do produto. Outcome: um claim cooperativo, mesma lei, sem o chat virar autorização de coluna. Direction: hardcode no produto + overlay Cripto `false` + bloco README; sem schema major. Scope: `render_agents` + README Clientes/`--pin` + overlay `clients.cursor.auto` + specs `covenant-flow` / `process-harness`.

---

## Probes (live, este worktree, pré-Apply)

### Overlay Cripto + `render_agents` / stub

- `.covenant-flow/overlay.yaml`: `pin: v1.1.4`; `clients.cursor.auto: true`; grok/opencode/dsh `false`.
- `SCHEMA_MAJOR = 1`; `CLIENT_KEYS = ("cursor", "grok", "opencode")`. Extra `dsh` aceite.
- `validate_overlay` exige as três `CLIENT_KEYS`; **não** lê o boolean `auto`. Fixture `clients.cursor.auto: false` → **PASS** (sondado neste turno).
- `render_agents()` (`scripts/process-fsm/overlay.py` L412–441) hardcode duas linhas de clientes. Corpo da função **não** referencia `overlay["clients"]`. `auto` no fonte = só as strings «Auto permitido» / «modo Auto».
- Sonda: `render_agents(overlay_true) == render_agents(overlay_false) ==` stub live. Q2=A (não interpolar) **já é o mecanismo live**; o card muda o *texto* hardcoded, não o canal.
- `AGENTS.md` coincide com o hardcode: 14 linhas não vazias (≤40). Linha 11: `Clientes: Cursor Agent (Auto permitido); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).` Linha 12: `Não reivindique modo Auto no Grok, no OpenCode nem no dsh.`
- `guard.py` **não** lê `clients.*.auto`. Flip do boolean = claim de máquina, não δ.
- `empty_template` já emite `auto: false` nas três chaves.
- `docs/crypto-overlay.md` sem «Auto permitido» / `clients.cursor.auto`. Skill `covenant-flow` sem essas frases.

### Produto `oalansilva/covenant-flow`

- Checkout `/srv/apps/dev/covenant-flow`: `main` == `origin/main` == peel **`v1.1.4`** (`eb375f6`). Tags: `v1.1.4` … `v1.0.0`. **`v1.1.5` livre.**
- Description GitHub (congelada #787): `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`.
- README bloco **Clientes** (live): «Auto — só Cursor, overlay `clients.cursor.auto: true`» + «Cooperativo — Grok, OpenCode e dsh…». Exemplo `--pin v1.1.4`. Sem `approvalMode` / Run Everything. Sem tabela T0–T17. Sem `CONTRIBUTING.md`.
- `install.sh --pin`: regex `vMAJOR.MINOR.PATCH` (recusa `latest`); `copy_tree` **sem** `README.md`; no fim `set_pin` + `render_agents(overlay)` escreve `AGENTS.md`. Copia `.dsh/` sempre.
- Working tree produto **sujo** (1 linha, fora deste card): `.agents/skills/design-critic/SKILL.md`. `--pin` copia o working tree de `SOURCE`, não o objecto git da tag.

### Goldens live

- `test_agents_md_is_stub`: quatro nomes; proíbe Auto Grok/OpenCode/dsh; exige `cooperativo` (já passa via «cooperativos» dos três); **não** exige ausência de «Auto permitido» — live **passa** com a frase.
- `test_harness_mdc_body_budget` já proíbe «Auto permitido» no `harness.mdc` (não no stub).
- Pin-tests cravam `v1.1.4` (`test_pin_copies_dsh_without_injecting_clients_dsh`, needle em `test_grill_card.py`).

### Specs main vs leftovers

- Spec main `covenant-flow`: bloco Auto = Cursor `clients.cursor.auto: true` (herdado #787, change arquivada). Pin example ainda cita `v1.1.2` no texto main.
- Spec main `process-harness` Always-on: três clientes + SHALL «Cursor Auto is allowed».
- Leftover **não arquivado** `openspec/changes/card-782-dsh-adapter`: Always-on já quatro nomes **e** ainda SHALL «Cursor Auto is allowed». `card-784` / `card-786` sem essa frase.
- Issues GitHub #787/#784/#782 continuam `state: OPEN` (board ≠ `gh issue close`). Board: #795 **Design**; #787 **Homologado**.

---

## Hunt (furos pedidos) — contrato vs live

| Furo | Contrato | Live | Disposition |
| --- | --- | --- | --- |
| Overlay `clients.cursor.auto` | Q1=A / D1 / spec overlay `false` / tasks 5.1 | Live `true`; `validate_overlay` não lê o boolean; `false` já PASS | **CLOSED** |
| `render_agents` | D2/D5 exacto; spec ADDED duas linhas; tasks 1.1–1.2 | Hardcode «Auto permitido»; não interpola `clients` | **CLOSED** |
| `AGENTS.md` «Auto permitido» | D5 `(cooperativo)` + 2.ª linha nomeia Cursor; spec MUST NOT; tasks 3.1 / 5.2 / 6.2 | Presente no stub live (14 linhas) | **CLOSED** |
| README produto | Q4=A / D6 / spec MODIFIED Clientes; tasks 2.1–2.3 | Auto = só Cursor `true`; `--pin v1.1.4` | **CLOSED** |
| Pin/tag | D7/D8 `v1.1.5` confirm origin; spec patch; tasks 3.3 / 4.1–4.2 / 5.2 | Peel `v1.1.4`; `v1.1.5` livre; pin não copia README; regex recusa `latest` | **CLOSED** |
| Dual-write T0–T17 / lei | Non-Goals; tasks 1.3 / 5.3; spec MUST NOT Guard/yaml/adapters; stub live sem tabela | Stub sem `T0–T17`; skins não tocadas; D5/D6 sem tabela/IDs de lei | **CLOSED** |
| Reabrir #787/#784/#782 | Issue + D4/D8; spec pin #773/#784/#787; tasks 2.3 / 5.3 | #787 Homologado; issues GitHub OPEN; leftovers 782/784/786 no `changes/` | **CLOSED no contrato** (P2 archive-order; P3 lista spec omite #782) |
| Interpolar `clients.*.auto` no stub | Q2=A ≠ B; D2; spec MUST NOT + cenário true/false; task 1.2 | Live já não interpola (true==false) | **CLOSED** (P2: golden 3.2 é MAY) |

---

## Critique (contrato vs live)

Issue #795 sintetizado sem reabrir Q1–Q4. Pacote OpenSpec:

| Entra | Onde |
| --- | --- |
| Overlay Cripto `clients.cursor.auto: false` | D1; spec overlay; tasks 5.1 |
| `render_agents()` hardcode D5; nunca «Auto permitido» | D2/D5; spec ADDED; tasks 1.1–1.2 / 3.1 |
| Yaml **não** interpola o stub | D2; spec cenário true/false; task 1.2 |
| README Clientes D6 no mesmo tag; sem Auto=Cursor `true`; Auto ≠ coluna | D4/D6; spec MODIFIED; tasks 2.1–2.2 |
| `--pin` = tag do entregável; pin não copia README | D7; spec pin; tasks 2.3 / 4.x |
| Produto primeiro, depois pin Cripto; stub via pin, não hand-edit | D8; Apply contract 1–5; tasks 5.2 |
| Specs MODIFIED `covenant-flow` + `process-harness` (tira «Cursor Auto is allowed») | proposal; D4; spec Always-on |
| Sem schema major; `CLIENT_KEYS` três; Guard/T0–T17 intactos; Q3 IDE fora | D3/D7; tasks 1.2–1.3 / 5.3 |
| #787 não reabre como Apply; sem rewrite geral README | D4; tasks 2.3 / 5.3 |
| Ensaio deny só nos três; Cursor cooperativo por contrato | D5/D6; spec Always-on |

`## Open Questions` = nenhuma. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido.

D5 fecha o residual da grelha (frase exacta). Alternativas rejeitadas (uma linha «quatro até ensaio»; omitir 2.ª linha; interpolar yaml; major `v2.0.0`; só yaml ou só stub) são as certas. Q3 não vaza `approvalMode` para o README (D6).

Live já prova que o canal **não** interpola: o furo é o literal «Auto permitido» + overlay Cripto `true` + README Auto=Cursor + spec main «Cursor Auto is allowed». O contrato aponta esses quatro sítios e o pin que regenera o stub.

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **Golden de interpolação é MAY.** Spec cenário *Yaml auto does not drive the stub* e D2/task 1.2 pinam Q2=A. Task 3.2 / Apply contract ponto 3 = MAY. `test_agents_md_is_stub` lê `AGENTS.md` do disco; com overlay Cripto `false` (passo 5.1) um `render_agents` que interpolasse ainda emitiria D5 e passaria 3.1. Live hoje já não interpola; o risco é Apply *introduzir* interpolação. Disposition: Apply SHOULD promover 3.2 a MUST, ou 3.1 invocar `render_agents()` com fixture `clients.cursor.auto: true` e afirmar as duas linhas D5.
- **`--pin` copia o working tree de `SOURCE`, não o objecto da tag.** Produto live `v1.1.4` com diff sujo em `.agents/skills/design-critic/SKILL.md` (ficheiro que o pin **copia**). Task 1.3 MUST NOT reescrever skills. Disposition: Apply MUST `git add` só `overlay.py` / README / goldens ao taggar `v1.1.5`; stash/restaurar o dirty; pin a partir da árvore **limpa** da tag.
- **Leftover `card-782-dsh-adapter` (não arquivado) ainda SHALL «Cursor Auto is allowed» no Always-on.** Se 782 arquivar *depois* de 795, o main `process-harness` regride. #784/#786 não reafirmam essa frase. Disposition: archive 782 antes/com 795, ou o leftover MUST deixar de afirmar Cursor Auto. Não colapsa o DoD deste card se 795 for o último write dessa requirement.

### P3

- Spec pin cenário lista `#773, #784, and #787` e omite **#782** (o issue e o Context do design pedem as peles). Tasks 1.3/5.3 já proíbem tocar adapters/Guard.
- D6 bullet **Auto** MUST NOT reivindica Auto só em Grok/OpenCode/dsh; o stub D5 nomeia também o Cursor. Assimétrico, não colapsa (título D6 já diz «os quatro são cooperativos»).
- MODIFIED pin requirement leva «This change SHALL rewrite `render_agents()`» para o main após archive (inverte o «AGENTS.md MUST NOT be rewritten» do #787). A ADDED `render_agents` já cobre o rewrite. Follow-on README-only terá de re-MODIFY.
- Skill `implantar` continua a exemplificar `--pin v1.1.4` (Não entra reescrever skills).
- Spec main `covenant-flow` / `process-harness` ainda dizem «three adapters» / Always-on de três clientes; leftover #782. Fora de escopo arquivar neste card.
- Spec «#787 remain closed» ≠ `gh issue close` (OPEN no GitHub; Status Homologado). Apply MUST NOT fechar a issue nem arrastar #787/#784/#782.
- `clients.*.auto` vestigial para stub e Guard (aceite Q2=A). Residual: leitor do yaml pode achar que `true` ligaria o stub — hardcode + README D6 impedem.
- Auto IDE/CLI residual no host (Q3=A). Claim ≠ toggle.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM yaml: sem task de estado/evento/`enabled_tools`. T1/T7 Alan; T5 parent. I1–I9 / T0–T17 não reabertos no stub/README/JS.
- Product UI Cripto: zero `frontend/src/` / `backend/` no Apply contract.
- Auto: overlay live cursor `true` / três `false`; contrato grava os quatro `false`; stub MUST NOT «Auto permitido»; README MUST NOT Auto=Cursor `true`; MUST NOT herdar Auto aos três.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados; tag patch não major.
- Detector de pele `hook.mjs` / adapters: fora de escopo (não reabre #782).

---

## Trace

1. Live: overlay `cursor.auto: true`; `render_agents` hardcode «Auto permitido» (não interpola); stub 14 linhas; README Auto=Cursor; pin `v1.1.4`; `v1.1.5` livre; `validate_overlay` ignora o boolean; Guard não lê `auto`; pin não copia README; produto dirty 1 linha em design-critic.
2. Issue #795 DoD + Q1–Q4=A = yaml+stub cooperativos, hardcode sem interpolar, IDE fora, README Clientes neste pin, sem reabrir #787/#784/#782, sem Guard/T0–T17/schema major.
3. Design D1–D8 + Apply contract produto-primeiro 1–5 pinam D5/D6 e `v1.1.5` (Apply confirma origin).
4. Specs MODIFIED/ADDED cobrem README, pin, hardcode D5, overlay `false`, Always-on sem «Cursor Auto is allowed»; `openspec validate --strict` verde.
5. Tasks 1.1–1.2 / 2.1–2.3 / 3.1 / 5.1–5.2 são o ouro que o Apply falha se interpolar (1.2), deixar «Auto permitido», reivindicar Auto=Cursor no README, pinar antes do tag, hand-editar o stub, ou esquecer `clients.cursor.auto: false`.

---

## Disposition

Zero P0/P1 abertos. Os oito furos pedidos estão fechados no contrato (overlay `auto`, `render_agents`, stub «Auto permitido», README, pin/tag, dual-write, reabrir #787/#784/#782, interpolar yaml). Residuais P2 (golden 3.2 MAY; `--pin`=worktree sujo; leftover #782 Always-on «Cursor Auto is allowed») não colapsam o DoD se Apply seguir D2/D5–D8 / tasks 1.2–1.3 / 3.1 / 5.1–5.2 e 795 for o último write do Always-on. Dual-write T0–T17, Auto nos três, `approvalMode`, major `v2.0.0`, e #787-como-Apply estão fechados no texto. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
