# Snapshot — Assessment A · card #787 `card-787-covenant-flow-readme`

- Card: #787 — Produto: README do covenant-flow para quem não conhece o projeto
- Change: `card-787-covenant-flow-readme`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested critic)
- Modelo: inherit
- UTC: 2026-08-29T14:32:11Z
- Round: 1
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Prompt do pai: worktree `card-787-covenant-flow-readme`; Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `f4b1bcb5757b411d4428fdd111b3f574873097552c9688b66010b8b19494eb47` · **1649** palavras (`wc -w`) · 11291 bytes
- UI impact: **none** (documentação do produto de processo `oalansilva/covenant-flow`; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*787*`; aceite = texto no GitHub do núcleo + description. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright.
- `openspec validate card-787-covenant-flow-readme --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois de A/B)
- Method: issue #787 body (DoD + vocabulário; Q1–Q8 congeladas no Entra); `proposal.md` / `design.md` D1–D9 + Apply contract / `tasks.md` 1–5; delta `specs/covenant-flow/spec.md`; main spec cenário «Product README does not require host backup paths»; README live `/srv/apps/dev/covenant-flow/README.md` (37 linhas, EN); `install.sh` `copy_tree` (sem `README.md`); skill `implantar` exemplo `v1.1.1`; yaml 12 `states`; overlay Cripto `pin: v1.1.1`; `gh repo view` description EN live.

---

## Brief (só neste snapshot)

Visitante do GitHub privado `oalansilva/covenant-flow` (convidado ou Alan daqui a meses) não consegue dizer o que o produto *é*: README live começa em clone / `install.sh --init` / `--pin v1.1.1` / Layout. Card #787: um README PT-BR, estranho primeiro, 12 colunas uma linha + uma frase de gates, description GitHub congelada, exemplo `--pin` = tag do entregável (`v1.1.2`), `--pin` continua a não copiar README. Não reabrir #773/#784. `UI impact: none`.

---

## 1. Escopo vs grill #787 (Q1–Q8 congeladas)

Body live: fronteira vazia. Design não reentrevista. Letras D1–D8 batem com o Entra/vocabulário (não com um transcript de Qs).

| Q congelada (prompt + issue) | Onde no pacote |
| --- | --- |
| Q1 PT-BR | D1; proposal What; spec «single root README.md written in PT-BR»; task 1.1 |
| Q2 walkthrough 12 colunas sem tabela T | D2; Non-Goals; spec walkthrough MUST NOT T0–T17/I1–I9 table; task 1.3 |
| Q3 description GitHub no mesmo entregável | D3; Apply contract passo 2; task 2.1 |
| Q4 um README, estranho primeiro, clone não é o 1.º parágrafo | D4 ordem 1–7; spec «Clone MUST NOT be the first paragraph»; task 1.1 |
| Q5 uma linha/coluna + uma frase dos 3 gates | D5 texto canónico + frase exacta do vocabulário do issue; task 1.3 |
| Q6 quatro clientes + Auto vs cooperativo | D6; spec clients + MUST NOT claim Auto on Grok/OpenCode/dsh; task 1.2 |
| Q7 exemplo `--pin` = tag do entregável | D7 + D9 bump `v1.1.2`; spec pin example `v1.1.2`; task 1.4 / 3.1 |
| Q8 description exacta PT-BR | D8 string exacta; spec; task 2.1; proposal |

Frase congelada (Q8 / D8), verificada byte-a-byte no issue, proposal, design, spec e task 2.1:

`Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`

Frase dos 3 gates (vocabulário do issue = D5), sem IDs T*:

*Alan prioriza Em Refinamento→Todo; só Alan Aprovação de Design→Pronto para Dev; Alan homologa Done→Homologado.*

Doze nomes D5 = 12 `states` do yaml (incluindo `Cancelado` terminal), mesma ordem.

**Não entra — não reaberto:** segundo ficheiro; nomes EN das colunas; tabela T0–T17/I1–I9; parágrafo por coluna; hooks/OpenSpec/release no README; reescrever skills/hooks/yaml/`install.sh`/`AGENTS.md`/adapters; README viaja no pin; overlay no produto; reabrir #773/#784; código `backend/**`/`frontend/src/**`; canal v1 submodule/gitignore/marketplace/template-clone; LICENSE; homepage; `--pin latest` / placeholder.

Vocabulário Auto: issue cita T1/T7/T15; D6 e task 1.2 **strippam** os IDs («não autoriza cruzar colunas; o agente não arrasta»). Correcto: Q5/Q2 proíbem T* no README.

Proposal «New Capabilities: (nenhuma)» correcto.

---

## 2. Fidelidade live (não é Apply)

### README produto (`/srv/apps/dev/covenant-flow/README.md`)

- 37 linhas, inglês; H1 «portable process product».
- Primeiro bloco útil = `git clone` + `--init` / `--pin v1.1.1` + Layout. É exactamente o furo do issue.
- Não lista Cursor/Grok/OpenCode/dsh nem Auto vs cooperativo. Não walkthrough das 12 colunas.
- HEAD = tag **`v1.1.1`** (`edf245e`). Sem `CONTRIBUTING.md`. Sem `.covenant-flow/` no produto (D4.2). Homepage GitHub vazia. Description live EN: `Covenant Flow — portable 12-column process (nucleus + adapters)` — D3/D8 substituem.

### `install.sh` — pin **não** copia README

`copy_tree` (rsync -a --delete) só: nucleus yaml/hooks/rules/commands/agents/skills; adapters `.grok/` `.opencode/` `.dsh/`; `.agents/skills/{impeccable,design-critic,playwright-cli}`; `scripts/process-fsm/`; `release-guard`; `post-card-evidence-comment.sh` opcional; `AGENTS.md` gerado via `render_agents`. **Zero** menção a `README.md` no script. Confirmado por grep. D9 e spec cenário «Pin still does not copy README» são fiéis. Este card MUST NOT adicionar `README.md` à lista (Não entra; tasks 1.5 / 4.2).

### Main spec — cenário host-backup permanece

`openspec/specs/covenant-flow/spec.md` cenário **Product README does not require host backup paths** (paths `/home/ubuntu/backups/covenant-flow-pre-773-*`, SHA `94f8ed41`) **não** é MODIFIED. Delta ADDED reforça a mesma proibição no README novo. Apply contract passo 1 nomeia os paths. #773 portability intacta.

### Overlay Cripto

`.covenant-flow/overlay.yaml` live `pin: v1.1.1`. Re-pin é o passo 4, depois do bump.

---

## 3. Regressão #773 / #784

| Risco de reabrir | Contrato |
| --- | --- |
| #773 Pronto (produto + pin + README sem host backup) | Não entra reescrever `install.sh`/schema/canal; spec host-backup permanece; pin payload inalterado |
| #784 Done (dsh always-on) | Não entra adapters/hooks; re-pin é no-op de peles se SOURCE = `v1.1.1` + só README |
| README copiado para o consumidor | `copy_tree` sem README; tasks 4.2 / spec AND «consumer tree does not receive a copy» |
| Código Cripto | Apply contract + task 4.2 MUST NOT `backend/**` `frontend/src/**` |

Não reabrir. `rsync --delete` das peles é comportamento #773; este card não o alarga.

---

## 4. Riscos operacionais (pedido mínimo)

### Tag `v1.1.2` sem payload de README no pin vs Q7

`--pin` não faz checkout da tag: valida semver, copia SOURCE no disco, `set_pin`. README nunca entra no payload. Sem bump, o exemplo `--pin v1.1.1` mentiria (tag `v1.1.1` fica com README inglês; `main` divergiria). D7+D9: commit README → tag patch `v1.1.2` (não major; schema intacto) → exemplo `v1.1.2` → re-pin Cripto só para `pin: v1.1.2`. Alternativas rejeitadas (só `main`; re-pin sem bump) batem o issue («só re-pin depois do bump» + Q7). Residual aceite no design: re-pin é alinhamento de etiqueta, não docs no consumidor.

### Skill `implantar` residual `v1.1.1`

Produto e consumidor: `.cursor/skills/implantar/SKILL.md` linha 38 ainda `--pin v1.1.1`. Não entra reescrever skills. D9 + risco 3 documentam. Superfície do estranho = README do produto, não a skill.

### Dual-write significados de coluna vs skill

Issue já aceita. D5 é tecto (uma linha + uma frase). Linhas D5 são abreviação fiel da tabela da skill `covenant-flow` (grelha→afiação; omite `grill-card` / «Não reentrevistar» / T1). Sem contradição. Homologado→Pronto (T16) de fora da frase dos 3 gates: Q5.

### T0–T17 no README

D2/D5/spec/task 1.3 proíbem tabela e IDs na copy. D5 walkthrough e a frase de gates **não** têm `T*`. Menções T0–T17 no `design.md` são proibição / «lei permanece no yaml». Auto no README sem T1/T7/T15. **false** como furo de copy.

### Auto reivindicado para Grok / OpenCode / dsh

D6 + spec SHALL + task 1.2: Auto = só Cursor `clients.cursor.auto: true`; os três = cooperativo `auto: false` até ensaio deny PASS. MUST NOT reivindicar Auto nesses três. **false**.

### Apply contract (README + `gh repo edit` + tag + re-pin Cripto)

Os quatro entregáveis do issue estão nos passos 1–4 e nas tasks 1–4:

1. README produto PT-BR D4–D7
2. `gh repo edit … --description` string exacta; LICENSE/homepage intocados (task 2.2)
3. commit + tag patch `v1.1.2` (não `v2.0.0`)
4. `implantar --pin v1.1.2` no worktree Cripto; overlay `pin:`; MUST NOT copiar README

Rollback nomeado. Sem migration / rebuild. Task 5.1 validate; 5.2 UI none + clone não é 1.º parágrafo + description exacta.

Falta nomear `git push origin main` + `git push origin v1.1.2` (passo 2 já é remoto). Sem push, visitante GitHub não vê o README e a tag anunciada não existe no remoto. P2: implicação do entregável GitHub, não furo Q1–Q8. Apply MUST publicar commit+tag no origin **antes** do re-pin. Pin a partir do objecto `v1.1.2` limpo (SOURCE live tem dirty de 1 linha em `.agents/skills/design-critic/SKILL.md`, fora deste card).

---

## 5. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, tokens, copy de ecrã CriptoFarol | **none** — fora |
| `backend/` de app | **none** |
| Protótipo HTML / Playwright / `DESIGN.md` consumidor | **N/A** — zero `prototypes/*787*` |
| Rubrica Impeccable visual | **N/A** |
| `README.md` raiz de `oalansilva/covenant-flow` | docs de processo; **entra** (não é UI Cripto) |
| GitHub description / homepage / LICENSE | description **entra** (Q3/Q8); homepage+LICENSE **fora** |
| Skill `covenant-flow` (tabela de colunas) | runbook operador; **não** reescrita; dual-write aceite |
| Skill `implantar` exemplo `v1.1.1` | **não** reescrita; residual aceite |
| `install.sh` copy list | **não** reescrita; README continua fora |

`UI impact: none` + Prototype N/A justificados. HTML não gerado / não copiado. Snapshot Impeccable visual N/A; este ficheiro é a crítica isolada (T7).

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: Delta spec ilustra a frase dos 3 gates em inglês (*Alan prioritizes* / *homologates*) enquanto Q1+Q5+D5 congelam o PT-BR do issue. Apply MUST usar D5/task 1.3, não copiar o SHALL inglês para o README. Disposition: **accepted-residual** (OpenSpec em EN; copy canónica = D5).
- P2: Tag `v1.1.2` não mete README no payload do pin. D9 escolhe bump+re-pin mesmo assim, senão Q7 mente. Disposition: **accepted-residual** (D9 + risco 1).
- P2: Skill `implantar` continua `--pin v1.1.1` depois deste card. Não entra. Disposition: **accepted-residual**.
- P2: Dual-write uma linha/coluna vs skill. Issue já aceita; D5 não expande. Disposition: **accepted-residual**.
- P2: Apply contract não nomeia `git push` de `main`+tag `v1.1.2`. Sem push o visitante não vê o README. Disposition: **accepted-residual** — Apply publica no origin antes do re-pin; pin SOURCE = commit tagado limpo.
- P3: Significados D5 não estão no delta spec (só «name + meaning»). Tasks 1.3 amarram D5. Disposition: **accepted-residual**.
- P3: Main spec ainda diz «three client adapters» num cenário #773. Fora de recorte; README deste card nomeia quatro. Disposition: **accepted-residual** (não reabrir #782/#784).
- P3: Passo 2 (`gh repo edit`) antes do push do README: description PT-BR com README EN no remoto, janela curta. Disposition: **accepted-residual**.
- P3: Task 5.2 não enumera clientes/gates/`v1.1.2`/pin-não-copia; 1.x e 4.2 cobrem. Disposition: **accepted-residual**.
- P3: D4.5–D4.7 não exigem reter a frase live das quatro recusas de canal; o bloco do estranho já diz canal v1 = copiar+commitar. Disposition: **accepted-residual**.
- Dual-write T0–T17 no README / Auto em Grok OpenCode dsh / README no `copy_tree` / segundo ficheiro / host backup no aceite / superfície visual sem classificar / Design Critique pré-PASS / UI Cripto: **false**.

---

## Disposition

Zero P0/P1 abertos. Recorte Q1–Q8 mapeado no Entra do issue (PT-BR; 12 colunas sem tabela T; description congelada no mesmo entregável; um README estranho-primeiro; uma linha/coluna + uma frase de gates; quatro clientes Auto vs cooperativo; pin = tag do entregável; description exacta). #773/#784 não reabertos; `install.sh` continua sem `README.md` na lista. Host-backup da spec main permanece. Apply contract tem os quatro passos (README, `gh repo edit`, tag `v1.1.2`, re-pin Cripto). Residuais P2/P3 (spec EN vs D5 PT-BR; tag sem payload de docs; `implantar` stale; dual-write; push implícito) não bloqueiam. UI none classificada. Sem HTML.

Não há re-despacho de autor por P0/P1.

---

## Verdict

**PASS** (zero P0/P1 abertos; Prototype N/A justificado; UI impact none classificado; crítica isolada; snapshot não vazio)

## Snapshot

`.impeccable/critique/787-card-787-covenant-flow-readme-A.md`

Prototype: N/A — `UI impact: none`; docs do núcleo no GitHub; nenhuma tela CriptoFarol a prototipar; aceite = README PT-BR + description exacta + tag `v1.1.2` + re-pin sem copiar README.
