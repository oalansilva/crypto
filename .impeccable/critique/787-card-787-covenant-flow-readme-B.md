# Snapshot — card #787 `card-787-covenant-flow-readme` (Assessment B)

- Card: #787
- Change: `card-787-covenant-flow-readme`
- Critic: isolated Design Critic B (detector posture; no transcript inherit; no Assessment A)
- UTC: 2026-08-29T14:34:16Z
- Tuple: hooks `q=None` `bound_card=⊥` `q_git=develop` (sessão unbound). Write produto deny. Esta onda só `.impeccable/critique/**`.
- UI impact: **none** (README + description GitHub do produto de processo `oalansilva/covenant-flow`; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-787-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Sem superfície visual nova ou alterada. Impeccable visual / `DESIGN.md` / Playwright desta coluna = N/A.
- `design.md` sha256: `f4b1bcb5757b411d4428fdd111b3f574873097552c9688b66010b8b19494eb47` (~1649 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + spec delta `covenant-flow`)
- `openspec validate card-787-covenant-flow-readme --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).
- Browser gate: **N/A (no UI)**.

---

## Brief

Visitante do GitHub privado `oalansilva/covenant-flow` (tag live `v1.1.1`, README 37 linhas EN) não vê o que o produto *é*: o primeiro bloco útil é clone + `install.sh --init` / `--pin v1.1.1` + Layout. Card #787: um README PT-BR (estranho → 12 colunas → Install/Pin/Layout), description GitHub congelada, tag patch `v1.1.2`, re-pin Cripto só depois do bump. Não reabre #773/#784. `UI impact: none`.

Audience: estranho no GitHub (convidado ou Alan daqui a meses). Outcome: orientar-se sem abrir a skill `covenant-flow` como primeiro passo. Direction: um ficheiro; clone não é o primeiro parágrafo; lei T0–T17 fica no yaml/skill. Scope: produto `README.md` + `gh repo edit --description` + tag `v1.1.2` + overlay `pin: v1.1.2`; payload do pin **não** inclui README.

---

## Probes (live, este worktree, pré-Apply)

### Produto `oalansilva/covenant-flow`

- Checkout `/srv/apps/dev/covenant-flow`: `main` == `origin/main` == peel de **`v1.1.1`** (`edf245e` «dsh Guard injects AGENTS.md stub…»). Tag `v1.1.2` **não** existe.
- Description GitHub live (EN, em-dash U+2014): `Covenant Flow — portable 12-column process (nucleus + adapters)`. Homepage vazia. Repo privado.
- `README.md`: 37 linhas, inglês. H1 «portable process product». Primeiro parágrafo = «Private GitHub repository…» (ainda não é o `git clone`; o **primeiro bloco útil** é `## Install` com clone + `--init` / `--pin v1.1.1`). Sem quatro clientes, sem Auto vs cooperativo, sem walkthrough das 12 colunas, sem `Cancelado`, sem paths `/home/ubuntu/backups/covenant-flow-pre-773-*` / SHA `94f8ed41`.
- Sem `CONTRIBUTING.md`, sem `LICENSE`, sem `docs/` de install.
- Working tree **sujo** (1 linha, fora deste card): `.agents/skills/design-critic/SKILL.md` troca URL hardcoded `https://dev.criptofarol.com.br/prototypes/…` por overlay `environments.dev.url`. Não está no tag `v1.1.1`.

### `install.sh --pin` (live)

- `--pin` exige `vMAJOR.MINOR.PATCH`; `latest` / placeholder **morre** no regex linha 92.
- `copy_tree` copia nucleus, adapters, `.agents/skills/{impeccable,design-critic,playwright-cli}`, helpers, `AGENTS.md` gerado. **Zero** referências a `README.md`. Não há `copy_tree` da raiz do produto. Canal v1 = working tree de `SOURCE` (default = dir do script), **não** checkout da tag.
- Overlay Cripto deste worktree: `pin: v1.1.1`. `SCHEMA_MAJOR = 1`. `clients.cursor.auto: true`; grok/opencode/dsh `false`.

### Yaml das 12 colunas (produto)

`Em Refinamento`, `Todo`, `Design`, `Aprovação de Design`, `Pronto para Dev`, `Em desenvolvimento`, `Code Review`, `QA`, `Done`, `Homologado`, `Pronto`, `Cancelado`. Terminais: `Pronto`, `Cancelado`. Gates humanos T1/T7/T15 = as três transições da frase D5 (sem IDs no README).

### Issue #787 ↔ pacote

Body grelhado (Q1–Q8 aterraram em Entra/Não entra; letras Q* só no `design.md`). DoD 1–6 mapeia D1–D9 + spec ADDED + tasks 1–5. Relacionado: #773 Pronto / #784 Done **não reabrir**. Issues GitHub #773/#784 continuam `state: OPEN` (board ≠ `gh issue close`).

---

## Hunt (furos pedidos) — contrato vs live

| Furo | Contrato | Live | Disposition |
| --- | --- | --- | --- |
| Tabela T0–T17 no README | D2/D5/Q2; spec req walkthrough MUST NOT table T0–T17/I1–I9; frase de gates **sem** IDs T*; tasks 1.3 | README live não tem a tabela (também não tem walkthrough) | **CLOSED** |
| Auto em Grok/OpenCode/dsh | D6 + spec MUST NOT claim Auto nos três; Auto = só `clients.cursor.auto: true`; não autoriza cruzar colunas; tasks 1.2 | Overlay live: cursor true, três `false`. README live não reivindica Auto (também não nomeia os quatro) | **CLOSED** |
| Clone como primeiro parágrafo | D4 ordem 1–4 **antes** de Install; spec: before any clone/`install.sh` **e** clone ≠ first paragraph; tasks 1.1 / 5.2 | Live: clone é o primeiro **bloco útil**, não o primeiro parágrafo. O AND «before any clone explains…» é o que o live falha e o contrato corrige | **CLOSED** |
| Segundo ficheiro | Non-Goals; spec MUST NOT `CONTRIBUTING.md` / `docs/` install; tasks 1.5 | Ausentes no produto | **CLOSED** |
| Pin copiar README | D9 + spec cenário pin; `install.sh` sem `README.md`; tasks 4.2 | Confirmado: pin não lista README | **CLOSED** |
| Host backup paths | Apply contract + spec AND `covenant-flow-pre-773-*` / `94f8ed41`; main spec cenário existente **não** alterado | README live já limpo (#773) | **CLOSED** |
| Description não exacta | Q8 / D8 / task 2.1: `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)` (U+2014 + á/ú) | Live EN a substituir; homepage intacta | **CLOSED** |
| `--pin latest` | D7 / task 1.4 MUST NOT `latest` nem placeholder; exemplo = `v1.1.2` | Regex live já recusa `latest` | **CLOSED** |
| Reabrir #773/#784 | Non-Goals; spec THEN remain closed; tasks 4.2; MUST NOT reescrever skills/`install.sh` | Issues GitHub OPEN; Status de board é que não se arrasta. Risco operacional: worktree produto sujo (P2) | **CLOSED no contrato** |
| Schema major bump | Patch `v1.1.2` não `v2.0.0`; schema overlay inalterado; proposal «Não é BREAKING» | `SCHEMA_MAJOR=1`; tag `v1.1.2` ainda não existe | **CLOSED** |
| Cancelado em falta | D5 12.ª linha «coluna terminal»; spec twelve yaml names including Cancelado; tasks 1.3 | Yaml tem `Cancelado` terminal | **CLOSED** |
| Nomes EN das colunas | Non-Goals = não traduzir *para* inglês; D5 = **nomes do yaml** (inclui `Code Review`/`QA`/`Done`/`Todo`/`Design` que *são* o yaml) | Yaml misto PT/EN tokens | **CLOSED** |
| Apply order produto-primeiro vs Cripto-primeiro | Apply contract 1→2→3→4: README produto → description → commit+tag `v1.1.2` → **depois** `implantar --pin v1.1.2` no worktree Cripto. Issue: «Cripto só re-pin depois do bump». Tasks 1 / 2 / 3 / 4 na mesma ordem | Pin live `v1.1.1`; `--pin` **não** verifica que a tag existe (só semver) — inverter 4 antes de 3 mentiria o overlay; o contrato numera produto primeiro | **CLOSED** |

---

## Critique (contrato vs live)

Issue #787 sintetizado sem reabrir Qs. Pacote OpenSpec:

| Entra | Onde |
| --- | --- |
| README PT-BR, estranho primeiro, clone ≠ 1.º parágrafo | D1/D4; spec «orients a stranger»; tasks 1.1 / 5.2 |
| Quatro clientes + Auto ≠ coluna | D6; spec clients; task 1.2 |
| 12 colunas yaml + Cancelado + 1 frase de gates sem T* | D2/D5; spec walkthrough; task 1.3 |
| Description exacta no mesmo entregável | D3/D8; spec description; tasks 2.1 / 5.2 |
| `--pin` = tag do entregável `v1.1.2`; não `latest` | D7/D9; spec pin example; tasks 1.4 / 3.1 |
| Pin não copia README; sem segundo ficheiro; sem backup host | D9; spec pin + host paths; tasks 1.5 / 4.2 |
| Produto primeiro, depois re-pin Cripto | Apply contract 1–4; proposal Impact; tasks 3 → 4 |
| Sem schema major; sem reabrir #773/#784; zero UI Cripto | D9; Non-Goals; tasks 3.1 / 4.2 / 5.2 |

`## Open Questions` = nenhuma. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido.

D5 (12 linhas) = os 12 `states` do yaml, na ordem, com significados alinhados à skill `covenant-flow` (tecto uma linha; residual dual-write aceite no issue). Frase dos 3 gates = T1/T7/T15 em nomes de coluna, sem IDs. D6 omite o parêntese `T1/T7/T15` do vocabulário do issue (correcto: README MUST NOT dual-write eventos).

Q7 + «só re-pin depois do bump» ⇒ tag nova `v1.1.2` (a árvore `v1.1.1` é imutável e continua com README EN). Alternativas rejeitadas em D9 são as certas.

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **`--pin` copia o working tree de `SOURCE`, não o objecto git da tag.** `install.sh` não faz checkout de `v1.1.2`. Live: `/srv/apps/dev/covenant-flow` está em `v1.1.1` **com** diff sujo em `.agents/skills/design-critic/SKILL.md` (ficheiro que o pin **copia**). Apply `git add -A` ou pin a partir desse SOURCE sujo **não** é no-op de peles e viola Não entra (reescrever skill) / parece follow-on de #773. Disposition: Apply MUST `git add` **só** `README.md` ao taggar `v1.1.2`; stash/restaurar o dirty; pin a partir da árvore **limpa** da tag (cwd do produto = peel `v1.1.2`, ou `--source` desse checkout). O contrato já diz MUST NOT reescrever skills; este P2 é higiene do canal v1, não furo de DoD.
- **`gh repo edit` (passo 2) publica a description antes do push do README (passo 3).** Crash entre 2 e 3 = description PT-BR + README EN no GitHub. Disposition: Apply SHOULD empurrar o README (commit+push na `main` do produto) no mesmo turno que a description; rollback já está definido.
- **Cenário spec «Fresh clone» omite o AND «primeiro consumidor = Cripto»** que o SHALL da mesma requirement inclui. D4.2 e task 1.1 pinam. Disposition: Apply MUST seguir D4/1.1, não só a lista AND do cenário.
- **Spec Auto «until a deny essay PASS»** (e o «até» do AGENTS.md) pode ler-se como Auto a desbloquear depois do ensaio. D6 + MUST NOT reivindicar Auto nos três fecham se o Apply copiar D6, não o «até» sozinho.

### P3

- Skill `implantar` continua a exemplificar `--pin v1.1.1` (D9 residual aceite; Não entra reescrever skills).
- Vocabulário Auto do issue traz `T1/T7/T15`; D6 já os tirou. Apply MUST NOT colar o vocabulário do issue no README (vazaria IDs fora da «tabela», ainda assim dual-write de eventos; Q2 proíbe).
- Frase de gates no spec delta está em inglês; canónico do README = D5 PT-BR (semicolons, uma frase).
- Spec main `covenant-flow` ainda diz «three client adapters» no cenário de clone fresco; #782 já é quatro. Fora de escopo arquivar.
- Spec «#773 and #784 remain closed» ≠ `gh issue close` (continuam OPEN no GitHub; Status de board Pronto/Done). Apply MUST NOT fechar as issues.
- D5 Cancelado = «não será feito (coluna terminal)» sem «a partir de qualquer coluna» (tecto uma linha; aceite no issue).
- Secção Pin MAY conservar a frase live «quebra de schema overlay = major `v2.0.0`» para `v1.1.2` não parecer BREAKING; não é requisito (schema inalterado).

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM yaml: sem task de estado/evento/`enabled_tools`. T1/T7 Alan; T5 parent. I1–I9 / T0–T17 não reabertos no README (proibido tabela e IDs na frase de gates).
- Product UI Cripto: zero `frontend/src/` / `backend/` no Apply contract.
- Auto: overlay live cursor true / três false; README MUST NOT reivindicar Auto nos três.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados; tag patch não major.

---

## Trace

1. Live README EN, 37 linhas, Install-first; description EN; pin `v1.1.1`; `install.sh` sem `README.md`; regex recusa `latest`; 12 states yaml incluem `Cancelado`; sem CONTRIBUTING/docs; produto dirty 1 linha em design-critic.
2. Issue #787 DoD 1–6 = estranho PT-BR, quatro clientes, 12 linhas + 1 frase gates, description exacta, pin = tag do entregável, sem segundo ficheiro / sem copiar README / sem reabrir #773/#784.
3. Design D1–D9 + Apply contract produto-primeiro 1–4 pinam o DoD e escolhem `v1.1.2` porque `v1.1.1` é imutável (README EN).
4. Spec ADDED cobre stranger / clients / walkthrough / description / pin-no-README; `openspec validate --strict` verde.
5. Tasks 1.1–1.5 / 2.1 / 3.1 / 4.1–4.2 / 5.2 são o ouro que o Apply falha se inverter Cripto-primeiro, meter tabela T*, reivindicar Auto, `--pin latest`, omitir Cancelado, ou copiar README.

---

## Disposition

Zero P0/P1 abertos. Os treze furos pedidos estão fechados no contrato (tabela T0–T17, Auto nos não-Cursor, clone-first, segundo ficheiro, pin copiar README, backup host, description exacta, `--pin latest`, reabrir #773/#784, major bump, Cancelado, nomes EN, ordem produto-primeiro). Residuais P2 (`--pin` = worktree não tag + dirty design-critic live; `gh repo edit` antes do push; AND Cripto omitido no cenário; «até ensaio» legível como Auto) não colapsam o DoD se Apply seguir D4–D9 / tasks 1.5 / 3.1 / 4.2. Dual-write T0–T17, Auto, `CONTRIBUTING.md`, schema `v2.0.0`, e Cripto-primeiro estão fechados no texto. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
