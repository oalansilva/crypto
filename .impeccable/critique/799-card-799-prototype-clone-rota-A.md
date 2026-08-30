# Snapshot — Assessment A · card #799 `card-799-prototype-clone-rota`

- Card: #799 — kaizen: protótipo de tela existente MUST clonar a página /rota, não galeria de estados (recidiva #792)
- Change: `openspec/changes/card-799-prototype-clone-rota/`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B)
- Modelo: inherit
- UTC: 2026-08-30T00:00:23Z
- Round: 1
- Board: Project 1 · **Status=Design** (medido)
- Tuple: worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-799-prototype-clone-rota` · branch `card-799-prototype-clone-rota` · HEAD `30e567c9` · change ainda untracked. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md` / proposal / tasks / specs / produto / HTML / `process_event`.
- Digest `design.md` **medido**: sha256 `82798318d659d5764d86e7a185296c7cc74a56258613c752a0f6cef0bdee7e3b` · **1765** palavras (`wc -w`) · 13370 bytes
- `openspec validate card-799-prototype-clone-rota --type change --strict`: **valid**
- UI impact: **none** (harness/processo; zero rota/shell/componente/token/copy de produto)
- Prototype: **N/A** — `UI impact: none`; zero `frontend/public/prototypes/*799*`; aceite = predicado composto `G_design` + skill/A/B no próximo Design UI affected. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright desta coluna.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto)
- Method: issue #799 body (DoD grelhado + Q1–Q5=A 2026-08-29); `proposal.md` / `design.md` D1–D12 + Apply contract / `tasks.md` 1–5; deltas `design-route-clone-gate` + `impeccable-design-gate` + `process-fsm-event` + `llm-flow-emission`; factos live `G_design` / skill / proto #792 / board.

---

## Brief (só neste snapshot)

Alan no T7 do #792 abriu o Monitor real e o r1 era galeria 2×2; A/B passaram por “fidelidade shell”. O teste observável live ainda é chrome. #799 endurece o harness: T5 recusa `UI impact: affected` + rota existente sem landmarks/`copied`; skill/A/B deixam de tratar sidebar 224px como clone. Não redesenha o HTML do #792 (Pronto). `UI impact: none`.

---

## 1. Escopo vs grill #799 (Q1–Q5 congeladas)

Body live: fronteira vazia; Q1–Q5=A (2026-08-29). Design não reentrevista e não inventa Qs.

| Q congelada | Onde no pacote | Contradição? |
| --- | --- | --- |
| Q1=A skill+A/B **e** `G_design`; T5 recusa landmarks/`copied` falhos | D1; proposal; spec `design-route-clone-gate` + `process-fsm-event`; tasks 2.1 / 3.2 / 4.1 | **não** |
| Q2=A catálogo versionado + HTML estático; T5 offline | D2 + D6; spec “Static HTML read”; task 1.2; Non-Goal Playwright autenticado em `submeter_design` | **não** |
| Q3=A `copied` = soma `COPIED:start`/`COPIED:end`; 0/ausente ⇒ recusa | D3 + D8; spec cenários missing/zero; task 3.1 | **não** |
| Q4=A fail-closed sem chave HEAD; autor não semeia na mesma change de produto | D4; spec “Versioned landmark catalog is fail-closed”; task 3.1 worktree-only | **não** |
| Q5=A `live_route:` / `surface: existing\|new` parseável; existing exige catálogo; new/`N/A` justificado isenta; affected+proto sem campo ⇒ recusa | D5 regex; campos neste `design.md`; spec “Parseable live_route”; `llm-flow-emission` ADDED | **não** |

Residual da grelha (formato do catálogo / rotas a semear / sintaxe do campo) **fechado** em D5–D6: YAML `version: 1`; chaves `/monitor` `/favorites` `/combo/discovery` `/combo/select`; linhas autónomas `live_route:` / `surface:`.

**Não entra — não reaberto:** patch #792; `frontend/src/**` / `backend/**`; #673 / #530 / #792 como Apply; fork `$impeccable critique`; medidor $; pixel-perfect de dados; credencial PROD em `process_event`; Playwright dentro de T5; fail-open sem chave; self-service de landmarks na change de produto; ausência de campo = tela nova; exigir catálogo para tela nova.

Este `design.md` documenta o formato Q5 com `live_route: N/A harness-only; no product route` + `surface: new` **sem** disparar catálogo (D12). Regex D5 aceita essa linha.

---

## 2. Factos live `G_design` (medidos nesta onda)

| Afirmação do issue / design | Medição |
| --- | --- |
| `files_g_design` L165–170 só 3 md + `specs/**/*.md` | **bate** — `process_event.py` L165–170; sem landmarks/`copied`/URL |
| T5 `guard: G_design` no yaml | **bate** — `.cursor/process-fsm.yaml` T5 L121; sem Σ novo proposto |
| `g_design` injectado nos testes legais | **bate** — `test_process_event.py` usa `g_design=True` (vários T5) |
| `design-critic` L63 = sidebar 224px + `--bg-*` | **bate** — L63 |
| Catálogo no disco | **ausente** — `scripts/process-fsm/route-landmarks.yaml` não existe |
| Folha de tokens no disco | **ausente** — `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` não existe |
| `declare_ui_impact` T3 sem predicado em `process_event.py` | **bate** — yaml T3 tem a action; zero hits no `.py` |
| Spec main `impeccable-design-gate` “clone the current shell/nav/tokens/density” | **bate** — `openspec/specs/impeccable-design-gate/spec.md` L102 |
| HTML live r2 #792 | **bate** — `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` sha256 `1a1ff265162784ca5708a76de22e6565ae85fb2832b90daec73cc40ac12f90c3` · 95314 B · `class="signals"` / `table.signals` · `Operar` · `COPIED:start`/`COPIED:end` |
| Galeria r1 `068581d6…` · 21275 B · “21275 vs 0” | **bate** o pin nas críticas r1 A/B (`21275` gerado, não copiado). Blob r1 **não** está no histórico git deste worktree (só r2 em `80166268`) |
| #792 board | **Pronto** (medido). Issue ainda OPEN. Design não o reabre |
| Landmarks D6 vs produto | `/monitor` `table.signals` + thead Status/Preço/Distância/7d/Risco até stop/Tags + `Operar` (`MonitorStatusTab.tsx` L1219–1230, L1392). `/favorites` `table.fav-strategies` + “Estratégias favoritas”/Symbol/Estratégia/Ações. `/combo/discovery` textos H1 + “Preflight” (substring de “Preflight do servidor”) + “Rascunho de varredura”. `/combo/select` `.combo-page` + “Available Templates”. Rotas em `App.tsx` L65–73 |

Proto resolve já em `process_event.py` L318–320: `frontend/public/prototypes/<inferred_change>/`. D7 reutiliza esse path.

---

## 3. Regressão produto / harness

| Risco | Contrato |
| --- | --- |
| Produto Cripto (`backend/**`, `frontend/src/**`) | Apply contract + task 5.1 MUST NOT |
| Proto live #792 `frontend/public/prototypes/card-792-monitor-risco-explicito/**` | MUST NOT escrever; fixture r1 vive em `scripts/process-fsm/fixtures/792-r1-gallery.html` |
| `DESIGN.md` / pipeline Impeccable HTML / Playwright em T5 | Non-Goals + D2 + D11 |
| Σ yaml (`states`, evento, hook, `enabled_tools`) | D11; T5 continua `guard: G_design` |
| Testes legais T5 com `g_design=True` | D7 + task 2.2: override **permanece**; default `g_design is None` é que mede o composto |
| Cards já em Aprovação / Pronto / Done | Migration: **não** reavaliados por T5 |
| #792 / #673 / #530 | Non-Goals; #792 Pronto confirmado |

`files_g_design` composto é **BREAKING** só para o predicado T5 em `UI impact: affected` + proto de tela existente — alinhado ao Why. UI none + 3 md + specs continua a transitar (spec `process-fsm-event` cenário “T5 still accepts UI none”).

---

## 4. Riscos operacionais

- **Evasão `surface: new` em tela existente.** Grill já aceitou; máquina não adivinha. Skill/A/B (fidelidade). D Open Questions P2.
- **Toggle Antes/Depois morto passa T5.** Q2=A (T5 offline). Skill/A/B P0 se o controlo não muda a vista (D10).
- **Primeiro seed do catálogo.** Este card é UI none / `N/A`; seed = Apply, não Design de produto a furar Q4.
- **Lookup HEAD vs worktree.** SHALL D4 é fail-closed. O parentético `git diff --quiet HEAD --` **não** vê untracked: se o yaml ainda não existe em HEAD, um ficheiro novo untracked pode parecer “quiet” e ser lido. Apply MUST tratar “path ausente em HEAD” como miss (não fallback para untracked).
- **`live_route: /…` e `surface: new` no mesmo `design.md`.** D5 dispara os dois ramos. Apply MUST fail-closed: path que começa por `/` exige catálogo/`copied` mesmo com `surface: new`.
- **Fixture r1 bytes exactos.** Pin sha256 `068581d6…` / 21275 B está nas críticas r1; **não** está no git deste worktree (histórico do path só tem r2). Apply MUST recuperar o blob (backup/transcript/outro clone) **ou** o task 1.3 fica bloqueado no Apply — não no Design. MUST NOT inventar HTML novo nem tocar no path live #792.
- **`affected` sem proto.** D7 deixa `clone_gate` True (skill/A/B bloqueiam PASS visual). Não alarga Q1. Residual aceite.
- **Match estático `table.signals` vs `class="signals"`.** D6 pede substring e aceitar os dois. Apply MUST não tokenizar só `signals` (falso positivo). r1 falha por não ter `table.signals`; r2 live tem CSS `table.signals` **e** `class="signals"`.
- Sem credencial PROD / sessão Alan em `process_event`. Sem evento novo.

---

## 5. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, tokens, copy de ecrã CriptoFarol | **none** — fora |
| `backend/` | **none** |
| Protótipo HTML deste card / Playwright / `DESIGN.md` | **N/A** — zero `prototypes/*799*` |
| Rubrica Impeccable visual | **N/A** |
| HTML live #792 r2 | **não entra** — path intocado; não é fixture |
| Fixture r1 (Apply) | harness `scripts/process-fsm/fixtures/` — não é UI de produto |
| Catálogo YAML / `design_clone_gate.py` / `process_event.py` / `design-critic` | harness — **entra** |
| Campos `live_route` / `surface` neste `design.md` | formato Q5; **não** é tela |

`UI impact: none` + Prototype N/A justificados. HTML não gerado / não copiado. Snapshot Impeccable visual N/A; este ficheiro é a crítica isolada (T7).

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: Lookup HEAD — `git diff --quiet` não vê untracked. Apply MUST miss se o path não existe em `git show HEAD:…`. Disposition: **accepted-residual** (SHALL D4 é fail-closed; o parentético é residual de implementação).
- P2: Conflito `live_route: /x` + `surface: new`. Apply MUST exigir catálogo/`copied` quando o path começa por `/`. Disposition: **accepted-residual** (Q5 não define AND; fail-closed preserva Q1/Q4).
- P2: Blob r1 `068581d6…` ausente do git deste worktree. Apply MUST achar o blob noutro sítio; MUST NOT patchear o r2 live. Disposition: **accepted-residual** (classificar galeria sem `table.signals`/`copied` já é o aceite 4; o pin exacto é regressão).
- P2: Evasão `surface: new` / `UI impact: none` com proto de tela existente. Grill + D Open Questions. Disposition: **accepted-residual**.
- P2: `affected` sem proto continua a passar T5. D7 + skill. Disposition: **accepted-residual**.
- P3: Distância/7d no catálogo `/monitor` são colunas técnicas (`showTechnicalColumns`). Alan no T7 viu-as; default não-admin pode omitir. Disposition: **accepted-residual**.
- P3: Spec cenário “surface: existing” ilustra lookup `/monitor`. Sem `live_route`, Apply recusa (não há chave). Disposition: **accepted-residual**.
- P3: `surface: new` neste card é vocabulário de isenção Q5, não tela nova de produto. Disposition: **accepted-residual**.
- Dual-write Σ yaml / produto / proto #792 / reabrir Q1–Q5 / superfície visual sem classificar / Design Critique pré-PASS / exigir Playwright desta coluna: **false**.

---

## Disposition

Zero P0/P1. Recorte Q1–Q5=A mapeado (T5+skill; catálogo estático offline; soma `COPIED:*`; fail-closed HEAD; campos parseáveis). DoD grelhado coberto; Não entra intacto. Factos live `G_design` / L63 / hashes r2 / Status Design / #792 Pronto revalidados. Apply contract executável (7 ficheiros harness). Residuais P2/P3 são lookup untracked, conflito de campos, blob r1 fora deste git, evasão já aceite na grelha — não bloqueiam Design. UI none classificada. Sem HTML. Prototype N/A correcto.

Não há re-despacho de autor por P0/P1.

---

## Verdict

**PASS** (zero P0/P1 abertos; Prototype N/A justificado; UI impact none classificado; crítica isolada; snapshot não vazio)

## Snapshot

`.impeccable/critique/799-card-799-prototype-clone-rota-A.md`

Prototype: N/A — `UI impact: none`; harness only; nenhuma tela CriptoFarol a prototipar; aceite = `G_design` composto + skill/A/B no próximo Design UI affected.
