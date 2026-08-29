# Snapshot — Assessment A · round 6 · card #786 `card-786-dsh-grill-root`

- Card: #786 — Harness: dsh grelha no root com `ask_user_question`, sem `subagent`
- Change: `card-786-dsh-grill-root`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; round 6)
- Modelo: inherit
- UTC: 2026-08-29T15:42:10Z
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Prompt: worktree `card-786-dsh-grill-root`; Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido (round 6)**: sha256 `3cd3bc9a06d067ce25f5f722798789c4e1aff04dbf28e89e7a777c72fffe9ece` · **2589** palavras (`str.split` = `wc -w`) · 19850 bytes · 156 linhas
- Digest round 5 (referência): `3cf434925a6b727dacec92ed68e1ea8f8e1d5c620baca29ac5424a370dfb2104` · 2511 palavras · 19225 bytes — **artefactos mudaram**
- `openspec validate card-786-dsh-grill-root --type change --strict`: **valid**
- Issue #786: OPEN; Project 1 `Status=Design` (`optionId=bd47fbe8`); fronteira vazia; Q1–Q6 = A
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto)
- UI impact: **none** (harness/skills/plugin de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*786*`; aceite visível = `ask_user_question` na GUI dsh (vendor) + deny grill-shaped no plugin. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright desta coluna.
- Overlay live: `pin: v1.1.1`; `clients.dsh.auto: false`. Plugin/lib live **ainda sem** `isGrillShapedSpawn` (esperado em Design; não é P0/P1).
- Method: issue #786 (Q1–Q6 = A; T1 canónico exacto); `proposal.md` / `design.md` D1–D10 + G1–G11/N1–N3/P1; `tasks.md` 1–8; deltas `grill-card` `process-harness` `covenant-flow`; live skill `grill-card`. Adversário = Apply TDD que verdeia **os asserts listados** em 4.6/D10/spec THEN (não a prosa «MUST instruct»). Simulador: `_plain` honesto (lower; strip `` ` `` / `*` / `**`; `_word_` sem comer `ask_user_question`; colapsar ws) + `_heading_section` live + counts + Precondição + offset H2 + substring **contígua** `root chama ask_user_question` em `_plain(dsh)`.

---

## Brief (só neste snapshot)

Round 6: o autor alega o P0 r5 fechado — N2 exige substring contígua `root chama ask_user_question` (não tokens `root` **e** `chama ask_user_question` soltos) mais três fixtures copiáveis (2 RED + 1 GREEN). Re-ler o pacote. Teste desta ronda: se N2 ainda verdeia `nunca chama` / trunc `não chama.` + verbo noutro sítio / quote sem contig, BLOCK. Sinónimos (`não pergunta`) **com** o contig = P2 / dump 8.1. `UI impact: none`.

---

## O que o patch r6 fecha (medido; não basta)

Seis asserts `_plain` **byte-idênticos** (strip + contig) em `design.md` D10, `tasks.md` 4.6 e `specs/grill-card/spec.md`. File-level N2: `_plain(dsh)` MUST conter a substring **contígua** `root chama ask_user_question` (D4, D10, 4.6, spec THEN). `_plain = lower+ws` **falha** o 1.º (`**não**`) **e** o 6.º (backticks → contig).

| HYP | N2 4.6/D10/spec THEN (contig) | Fecha o quê |
| --- | --- | --- |
| Live skill (sem headings cliente) | **RED** (heading + contig + Precondição) | — |
| r4-A: dsh = `runtime root ask_user_question` (dois tokens, sem verbo) | **RED** `dsh missing contig` | P0 r4-B / P1 r4-A |
| r4-C: `O runtime root não chama ask_user_question.` | **RED** missing contig **e** `banned polarity` | polaridade exacta |
| **r5-nunca:** `O runtime root nunca chama ask_user_question.` | **RED** `dsh missing contig` | **P0 r5** — `nunca` entre `root` e `chama` |
| **r5-trunc:** `O runtime root não chama. chama ask_user_question.` | **RED** `dsh missing contig` | **P0 r5** — verbo noutro período |
| **r5-quote:** dump `chama ask_user_question` + `nao pergunta` | **RED** `dsh missing contig` | **P0 r5** — sem `root chama` |
| `jamais chama` only | **RED** `dsh missing contig` | mesmo predicado, outro advérbio |
| Precondição com `filho` / L22 leftover | **RED** | P1 r4-B |
| INTENDED-GOOD: `O runtime root chama \`ask_user_question\`.` | **GREEN** | caminho feliz |
| contig + `não pergunta` no mesmo ramo | **GREEN** | **não** é P0 — P2 / 8.1 |

Fixtures RED/GREEN copiáveis (congelam `_plain` para **não** comer `nunca` / o ponto do trunc e fabricar contig):

```
assert "root chama ask_user_question" not in _plain("O runtime root nunca chama ask_user_question.")
assert "root chama ask_user_question" not in _plain("O runtime root não chama. chama ask_user_question.")
assert "root chama ask_user_question" in _plain("O runtime root chama `ask_user_question`.")
```

Dois-token (r5 N2: `root` **e** `chama ask_user_question` soltos) ainda **GREEN** em nunca/trunc/quote/`jamais`. Contig **RED** nos quatro. O golden agora distingue E de nunca/trunc/quote.

P1-1 r1 (origem JS vs `decide()`) **permanece fechado**: G1–G9 via `apply`+pre-execute; G5 `Task`/`spawn_subagent`/`task` → `next()`; G11 `decide()` allow; N3 `guard.py` sem as três needles.

---

## Teste da ronda: N2 RED com root instruído a **não** perguntar (sem contig)

`_plain` = o helper que **passa** os seis fixtures (não no-op; não special-case das seis strings). `full, cursor, dsh = map(_plain, (text, _heading_section(…Cursor e Grok), _heading_section(…dsh)))`. Quatro frases com `full.count == cursor.count >= 1`. Precondição Status+id. H2 Perguntas nested sob Cursor. dsh checks = 4.6 literal **incluindo** `"root chama ask_user_question" in dsh`.

| HYP | dsh (após `_plain`) | N2 r5 (dois tokens) | N2 r6 (contig) |
| --- | --- | --- | --- |
| **nunca** | `o runtime root nunca chama ask_user_question.` | GREEN | **RED** |
| **trunc** | `o runtime root não chama. chama ask_user_question.` | GREEN | **RED** |
| **quote** | `…chama ask_user_question… root nao pergunta…` | GREEN | **RED** |
| intended | `o runtime root chama ask_user_question.` | GREEN | **GREEN** |
| `não pergunta` **depois** do contig | `root chama ask_user_question. … não pergunta` | GREEN | GREEN (P2) |

`nunca chama ask_user_question` contém `chama ask_user_question` e **não** contém `root chama ask_user_question`. O TDD mínimo **também** pode ser o intended (`root chama ask_user_question`). Isso **colapsa** os HYP r5: o golden **distingue** E de nunca/trunc/quote. Apply que segue 4.6/D10/spec THEN não verdeia um ramo dsh que só instrui a não perguntar.

---

## 1. Escopo vs grill #786 (Q1–Q6 = A)

Body live: fronteira vazia; Q1–Q6 = A; comentário canónico exacto. Design não reentrevista. Recorte mapeado (D1–D7, tasks, specs). Não entra — não reaberto.

---

## 2. Superfície visual

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy | **none** |
| `backend/` de app | **none** |
| Protótipo HTML / Playwright / `DESIGN.md` | **N/A** |
| Card GUI dsh `ask_user_question` `:3080` | **vendor** — não prototipar |
| Texto de skills / deny reason | processo |

`UI impact: none` + Prototype N/A justificados.

---

## Achados

- P0: (nenhum aberto). P0 r5 fechado: N2 file-level + spec THEN exigem substring **contígua** `root chama ask_user_question` em `_plain(dsh)`; fixtures RED `nunca` / trunc e GREEN backticks estão nos três artefactos. Simulado neste isolado (nunca/trunc/quote/`jamais` **RED**; intended **GREEN**; r4-A/C e L22 **RED**).
- P1: (nenhum aberto).
- P2: contig + segundo período (`o root não pergunta` / `jamais o faças`) ainda GREEN. Pytest não é parser de polaridade PT/EN. Disposition: **accepted-residual** / dump 8.1 (pedido explícito desta ronda).
- P2: `## Como` / intro MAY ficar com `filho` / `relaying` / `isolado` unlabeled (HYP como = GREEN). N2 só sanitiza Precondição. Disposition: **accepted-residual**.
- P2: N2 não pinea `AskUserQuestion` no Cursor; `options[]` / `(Recommended)` / Other no ramo dsh (ADDED + task 3.1). Disposition: **accepted-residual**.
- P2: Spec dsh MUST dizer que a regra **não** aplica a Cursor, Grok ou OpenCode. N2 não pinea essa frase (intended verdeia com ela). Disposition: **accepted-residual**.
- P2: Tabela covenant-flow `Em Refinamento | 1 filho grill-card` continua global; `## Grill-card` ainda «O **pai** spawna» (uma linha `Cliente dsh:` não desfaz). Guard deny é o backstop do spawn, não do ask. Disposition: **accepted-residual** (teto Q4=A).
- P2: Spec *dsh root does not spawn* usa MAY `gh issue edit`; ADDED requirement usa SHALL. Disposition: **accepted-residual**.
- P2: G1 ainda não stubba `runGuard` a allow; matcher tool-filtered em `decide()` sem as três strings N3 ainda pode verdear G1 via Python. Harm OpenCode pinado por G5/G11. Disposition: **accepted-residual**.
- P2: FN se o modelo omitir a substring `grill-card` (description `refine 701`). Needle pinada. Disposition: **accepted-residual** (Q6).
- P2: Plugin omitido / `--patch` ausente → spawn allow (#782). Disposition: **accepted-residual**.
- P2: Homologação 8.1 não bloqueia T14; pin-test live `v1.1.1` até Apply; modelo que **ignora** um canónico que já manda `root chama ask_user_question`. Disposition: **accepted-residual (Q2 dump)**.
- P3: Task 3.1 não nomeia envelope live `questions[].id` / `questions[].options[].label`. Disposition: **accepted-residual**.
- P3: G10 MAY no design vs obrigatório na task 4.3. Disposition: **accepted-residual**.
- P3: Frontmatter `grill-card` continua “spawn prompt” (Q3 MAY). Disposition: **accepted-residual**.
- P3: Lookup-table `_plain` que só transforma as seis strings-fixture passa os unit asserts; no ficheiro, contig em nunca/trunc **ainda falha** (não precisa de strip). Leftover `**não**` na Precondição sem strip honesto é higiene de teste, não reabre o P0. Disposition: **accepted-residual**.
- Dual-write T0–T17 / segundo plugin / regra em `decide()` / matcher Cursor `Task` / deny global subagent / Auto dsh / produto UI / superfície visual sem classificar / Design Critique pré-PASS / vendor harness / reabrir #755/#784: **false**.

---

## Disposition

Zero P0/P1 abertos. O P0 r5 (tokens `root` e `chama ask_user_question` independentes) está congelado: file-level N2 + spec THEN usam contig; os três fixtures copiáveis impedem `_plain` de fabricar contig a partir de `nunca` / trunc. Residuais (`não pergunta` com contig; rótulo ignorado; dump `:3080`) = P2 conforme 8.1.

Pai: pode `submeter_design` se B também PASS. Sem polish neste transcript. MUST NOT editar `design.md` daqui.

---

## Verdict

**PASS** (zero P0/P1; Prototype N/A justificado; UI impact none classificado; crítica isolada round 6; snapshot não vazio)

## Snapshot

`.impeccable/critique/786-card-786-dsh-grill-root-A.md`
