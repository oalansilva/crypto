# Snapshot — Assessment A · card #795 `card-795-quatro-clientes-cooperativos`

- Card: #795 — Processo: quatro clientes cooperativos; Cursor deixa de ser exceção Auto
- Change: `card-795-quatro-clientes-cooperativos`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested critic)
- Modelo: inherit
- UTC: 2026-08-30T00:01:03Z
- Round: 1
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Prompt do pai: worktree `card-795-quatro-clientes-cooperativos`; Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `2206886e474fd54df969c94ba8257924a8d00e814ba0260b97a3a097a384aaa2` · **1507** palavras (`wc -w`) · 10598 bytes
- UI impact: **none** (overlay `clients.cursor.auto` + texto hardcoded de `render_agents()` / stub `AGENTS.md` / bloco README do produto de processo; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*795*`; aceite = yaml cooperativo + stub hardcoded + README bloco Clientes no mesmo pin. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright.
- `openspec validate card-795-quatro-clientes-cooperativos --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois de A/B)
- Method: issue #795 body (DoD + vocabulário; Q1–Q4 congeladas A); `proposal.md` / `design.md` D1–D8 + Apply contract / `tasks.md` 1–6; delta `specs/covenant-flow/spec.md` + `specs/process-harness/spec.md`; main specs «Auto is Cursor `true`» e «Cursor Auto is allowed»; produto live `/srv/apps/dev/covenant-flow` tag **`v1.1.4`**; overlay Cripto `pin: v1.1.4` `clients.cursor.auto: true`; `render_agents()` + `test_agents_md_is_stub` + `guard.py` (zero `auto`); `gh api` tags origin até `v1.1.4`.

---

## Brief (só neste snapshot)

Alan quer uma forma padrão: Cursor cooperativo como Grok, OpenCode e dsh — sem o chat virar autorização de coluna. Live (pin `v1.1.4`): overlay Cripto `clients.cursor.auto: true` + stub «Cursor Agent (Auto permitido)»; Guard já é o mesmo deny nos quatro. Card #795: Q1=A yaml+stub cooperativos; Q2=A `render_agents` hardcode (yaml não conduz o stub); Q3=A IDE/CLI Auto fora; Q4=A README bloco do estranho neste card / mesmo pin. Não reabrir #787 como Apply. `UI impact: none`.

---

## Rubrica (UI none)

### 1. Escopo vs grill #795 (Q1–Q4 congeladas A)

Body live: fronteira vazia. Design não reentrevista. Letras D1–D4 batem com o Entra (não com um transcript de Qs). Residuais da grelha (frase exacta PT-BR; tag patch) fechados em D5/D6/D7.

| Q congelada (prompt + issue) | Onde no pacote |
| --- | --- |
| Q1=A yaml+stub cooperativo | D1; proposal What; spec «Cripto overlay cooperative claim» + `render_agents` hardcode; tasks 1.1 / 5.1 |
| Q2=A `render_agents` hardcode (yaml não conduz o stub) | D2; spec «MUST NOT interpolate» + cenário fixture `true` não muda o texto; tasks 1.2 / 3.2 |
| Q3=A IDE/CLI Auto fora de escopo | D3; Non-Goals; spec MUST NOT `approvalMode` / Run Everything; tasks 1.3 / 2.2 / 5.3 |
| Q4=A README bloco do estranho neste card / mesmo pin | D4 + D6 + D8; spec stranger block four cooperative; tasks 2.1–2.3 / 6.2 |

Frases exactas D5 (stub), verificadas no design, spec ADDED e task 1.1:

`Clientes: Cursor Agent (cooperativo); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).`

`Não reivindique modo Auto no Cursor, no Grok, no OpenCode nem no dsh.`

Ensaio deny **só** nos três — Cursor cooperativo por contrato (Q1), não por ensaio pendente. Alternativa «os quatro até ensaio deny» rejeitada em D5.

**Não entra — não reaberto:** pular colunas; chat/NLU como δ; `implemente` como autorização; herdar Auto para Grok/OpenCode/dsh; «Todos Auto»; interpolar `clients.*.auto` no stub (Q2 ≠ B); reabrir #787 como Apply; reescrita geral do README; `gh repo edit` da description; código `backend/**`/`frontend/src/**`; Guard / T0–T17 / `CLIENT_KEYS` / `SCHEMA_MAJOR`; config local IDE/CLI (`approvalMode` / Run Everything); hand-edit do stub no Cripto; `docs/crypto-overlay.md`; HTML / Impeccable visual / Playwright / rewrite `DESIGN.md`.

Proposal «New Capabilities: (nenhuma)» correcto.

### 2. Regressão Guard / T0–T17 / `CLIENT_KEYS` / `SCHEMA_MAJOR` / #787 Apply

| Superfície | Live medido | Contrato deste card |
| --- | --- | --- |
| `guard.py` / hooks | **zero** leitura de `clients.*.auto` (rg vazio) | Task 1.3 / 5.3 MUST NOT alterar Guard; aceite issue: mesmo deny de sempre |
| `validate_overlay` | exige `CLIENT_KEYS`; **não** lê o boolean `auto` | D2 + spec + task 1.2 inalterado quanto a `auto` |
| `CLIENT_KEYS` | `("cursor", "grok", "opencode")` | Permanece três; extra `dsh` aceite |
| `SCHEMA_MAJOR` | `1` | Permanece 1; tag **patch** (não `v2.0.0`) |
| T0–T17 / `process-fsm.yaml` | fora do recorte | Task 1.3 MUST NOT |
| #787 Homologado (README PT-BR, description, pin não copia README) | spec main ainda SHALL Auto=Cursor `true`; `install.sh` sem `README.md` | Este card **MODIFIED** o bloco Clientes; MUST NOT reabrir #787 como Apply; description / 12 colunas / frase dos 3 gates intactas; pin continua a não copiar README |
| #782 / #784 peles | stub live já nomeia dsh; change #782 ainda unarchived SHALL «Cursor Auto is allowed» | Não reabrir como Apply (adapters/hooks) |

`rsync --delete` das peles e `copy_tree` sem README são #773/#787; este card não os alarga.

### 3. Riscos operacionais

- **`clients.*.auto` vestigial** (aceite Q2=A): overlay Cripto mesmo assim grava `false`. Um leitor do yaml pode achar que `true` ligaria Auto no stub — o hardcode impede. D6 nomeia o facto.
- **Tag `v1.1.5`:** origin live = `v1.1.4` (`gh api` tags: `v1.1.4` … `v1.0.0`; sem `v1.1.5`). D7 + task 4.1: Apply confirma origin; se ocupada, próximo patch (nunca major).
- **Ordem produto → pin Cripto (D8):** commit+tag no `oalansilva/covenant-flow` → `implantar --pin` no worktree; `AGENTS.md` regenerado, não hand-edit. `--pin` não faz checkout da tag: copia SOURCE no disco + `set_pin`. Sem push do commit/tag, o visitante GitHub não vê o README e o exemplo `--pin v1.1.5` mente no remoto. Apply MUST publicar no origin **antes** do re-pin. SOURCE produto tem dirty de 1 linha em `.agents/skills/design-critic/SKILL.md` (fora deste card) — pin a partir do objecto tagado limpo.
- **`test_agents_md_is_stub` hoje passa com «Auto permitido»:** afirma quatro nomes e proíbe Auto Grok/OpenCode/dsh; **não** exige nem proíbe «Auto permitido». Task 3.1 acrescenta o assert de ausência. Sem isso o hardcode cooperativo não tem rede.
- **Pin-tests `v1.1.4`:** `test_pin_copies_dsh_without_injecting_clients_dsh` (`--pin v1.1.4` + `overlay["pin"] == "v1.1.4"`) e needle em `test_grill_card.py`. Task 3.3 + gate 3.4 `pytest scripts/process-fsm`. Skill `implantar` linha 38 ainda `--pin v1.1.4` — **não entra** (skills).
- **Change #782 unarchived:** Always-on ainda SHALL «Cursor Auto is allowed» (quatro nomes). Se o lote arquivar #782 **depois** de #795 sem tratar #795 como texto sobrevivente, a spec main reintroduz Cursor Auto. Não é reabrir #782 como Apply; é ordem de archive. #786 não toca o claim Auto.
- **Auto IDE/CLI residual no host:** Q3=A; fora. Claim ≠ toggle. D6 MUST NOT mencionar `approvalMode` / Run Everything. A frase live «pode correr sem prompt de permissão por ferramenta» **sai** (era mistura Q3).
- **Rollback** nomeado: pin Cripto `v1.1.4` + tag produto `v1.1.4`. Sem migration / rebuild.

### 4. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, tokens, copy de ecrã CriptoFarol | **none** — fora |
| `backend/` de app | **none** |
| Protótipo HTML / Playwright / `DESIGN.md` consumidor | **N/A** — zero `prototypes/*795*` |
| Rubrica Impeccable visual | **N/A** |
| Overlay Cripto `clients.cursor.auto` | claim de máquina; **entra** (Q1); não é UI |
| `render_agents()` / `AGENTS.md` stub | texto de processo; **entra** (Q1/Q2) |
| README produto bloco **Clientes** + exemplo `--pin` | docs de processo; **entra** (Q4); resto #787 intacto |
| GitHub description / homepage / LICENSE | **fora** (não `gh repo edit`) |
| Skill `covenant-flow` / `implantar` / `docs/crypto-overlay.md` | **não** reescrita |
| `install.sh` copy list / Guard / yaml law / adapters | **não** reescrita |
| Config local IDE/CLI Cursor | **fora** (Q3) |

`UI impact: none` + Prototype N/A justificados. HTML não gerado / não copiado. Snapshot Impeccable visual N/A; este ficheiro é a crítica isolada (T7).

### 5. Apply contract executável

Os entregáveis do issue estão nos passos 1–5 e nas tasks 1–6:

1. `render_agents()` = D5; sem interpolar; sem «Auto permitido»; schema intacto
2. README só bloco Clientes = D6; `--pin` = tag; sem rewrite geral; sem #787 Apply
3. Goldens + fixture `clients.cursor.auto: true` MAY (prova Q2=A)
4. Tag patch (esperado `v1.1.5`; Apply confirma)
5. Overlay Cripto `false` + `implantar --pin` regenera stub

Spec observável: stub gerado quatro cooperativos; overlay `false` valida; README não afirma Auto=Cursor `true`; pin não copia README.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: Delta spec (EN) vs frases canónicas D5/D6 (PT-BR). Apply MUST emitir D5/D6, não copiar o SHALL inglês para stub/README. Disposition: **accepted-residual** (OpenSpec em EN; copy canónica = D5/D6).
- P2: `clients.*.auto` fica vestigial para stub e Guard (Q2=A). Overlay Cripto mesmo assim grava `false`. Disposition: **accepted-residual** (D6 + risco 1).
- P2: Change unarchived #782 Always-on ainda SHALL «Cursor Auto is allowed». Archive de #782 depois de #795 sem #795 como texto sobrevivente reintroduz Cursor Auto na spec main. Não reabrir #782 como Apply. Disposition: **accepted-residual** — lote trata Always-on Auto de #795 como sobrevivente.
- P2: Apply contract não nomeia `git push` de `main`+tag do produto. Sem push o visitante não vê o README e o exemplo `--pin` mente no remoto. SOURCE produto dirty (1 linha `design-critic`, fora). Disposition: **accepted-residual** — Apply publica no origin antes do re-pin; pin SOURCE = commit tagado limpo.
- P2: Skill `implantar` continua `--pin v1.1.4` depois deste card. Não entra. Disposition: **accepted-residual**.
- P3: Bloco D6 **Auto** MUST NOT reivindica Auto só em Grok/OpenCode/dsh (texto do aceite); o título + D5 já dizem Cursor cooperativo / não reivindicar Auto no Cursor. Disposition: **accepted-residual**.
- P3: `test_agents_md_is_stub` hoje passa com «Auto permitido»; task 3.1 fecha a rede. Disposition: **accepted-residual**.
- P3: Main `process-harness` Always-on ainda é três clientes + «Cursor Auto is allowed» até archive; live stub já tem quatro nomes (#782). Este card MODIFIED a main, não a change #782. Disposition: **accepted-residual**.
- P3: Requirement Cripto-específica no spec portátil (`clients.cursor.auto: false` no primeiro consumidor). Outros consumidores não viram o yaml neste card; o hardcode do produto vale no próximo pin. Disposition: **accepted-residual**.
- Dual-write Guard/T0–T17/`CLIENT_KEYS`/`SCHEMA_MAJOR` / reabrir #787 como Apply / interpolar yaml no stub / Auto IDE/CLI / README no `copy_tree` / superfície visual sem classificar / Design Critique pré-PASS / UI Cripto: **false**.

---

## Disposition

Zero P0/P1 abertos. Recorte Q1=A Q2=A Q3=A Q4=A mapeado no Entra do issue (yaml+stub cooperativos; hardcode sem interpolar; IDE/CLI fora; README bloco do estranho neste card/mesmo pin). Guard não lê `auto` (medido) — `clients.cursor.auto: false` é claim, não δ. #787 não reaberto como Apply; description/walkthrough/gates intactos; pin continua sem copiar README. `CLIENT_KEYS` três, `SCHEMA_MAJOR` 1, tag patch. Apply contract tem produto → tag → pin Cripto. Residuais P2/P3 (spec EN vs D5/D6; yaml vestigial; archive #782; push implícito; `implantar` stale) não bloqueiam. UI none classificada. Sem HTML.

Não há re-despacho de autor por P0/P1.

---

## Verdict

**PASS** (zero P0/P1 abertos; Prototype N/A justificado; UI impact none classificado; crítica isolada; snapshot não vazio)

## Snapshot

`.impeccable/critique/795-card-795-quatro-clientes-cooperativos-A.md`

Prototype: N/A — `UI impact: none`; overlay + stub + README do núcleo; nenhuma tela CriptoFarol a prototipar; aceite = `clients.cursor.auto: false` + hardcode D5 + bloco D6 no mesmo pin.
