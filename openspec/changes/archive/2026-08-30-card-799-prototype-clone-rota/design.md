## Context

Card [#799](https://github.com/oalansilva/crypto/issues/799). O briefing é o issue (DoD grelhado). Q1–Q5 fechadas (todas A, 2026-08-29); este Design não as reabre e não inventa Qs novas. Relacionado e **não** reaberto como Apply: #792 (Pronto), #673, #530.

Facto live (grelha): `files_g_design` em `scripts/process-fsm/process_event.py` (L165–170) só exige `proposal.md` + `design.md` + `tasks.md` + algum `specs/**/*.md`. T5 (`submeter_design` / `G_design` em `.cursor/process-fsm.yaml`) **não** lê landmarks, `copied` nem URL viva. `design-critic` L63 operacionaliza clone como sidebar 224px + tokens `--bg-*`. Spec `impeccable-design-gate` exige “clone the current shell/nav/tokens/density”. Proxy `copied vs generated` é só handoff. Catálogo de landmarks **ainda não existe** no disco. `design.md` do #792 declara `/monitor` em prosa, sem campo parseável.

HTML live r2 #792 `1a1ff265162784ca5708a76de22e6565ae85fb2832b90daec73cc40ac12f90c3` (95314 B, `table.signals`, Operar, `COPIED:start`/`COPIED:end`). Galeria r1 `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7` · 21275 B · “21275 vs 0”. Path live r2 **não** é a fixture deste card.

UI impact: none
live_route: N/A harness-only; no product route
surface: new

Harness/processo. Nenhuma rota, shell, componente ou copy de produto. Nenhuma superfície visual nova ou alterada.

## Goals / Non-Goals

**Goals:**

- T5 recusa `UI impact: affected` + rota existente quando landmarks do catálogo ou `copied` falham (Q1=A, skill + A/B **e** `G_design`).
- Catálogo versionado por rota + leitura **estática** do HTML do proto; T5 offline (Q2=A).
- `copied` = soma dos bytes entre pares `COPIED:start`/`COPIED:end`; ausência ou soma 0 ⇒ recusa (Q3=A).
- Sem chave no catálogo para a rota declarada ⇒ T5 recusa (Q4=A). Autor **não** acrescenta a chave na mesma change para furar o gate.
- `design.md` com campo parseável `live_route:` e/ou `surface: existing|new` (Q5=A). existing exige catálogo + landmarks + `copied`. new (ou `live_route: N/A` justificado) isenta catálogo/`copied`. affected + proto sem campo ⇒ recusa.
- Skill/A/B: fidelidade bloqueante = landmarks da rota viva; galeria de estados = P0; URL viva vs proto quando houver sessão; `/login` não é a rota.
- Fixture r1 `068581d6…` MUST ser BLOCKED. Catálogo semeado para `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`.

**Non-Goals:**

- Patchar o protótipo do #792 nem Apply do risco explícito (#792 já Pronto).
- Código de produto (`frontend/src/components/monitor/**`, `backend/`).
- Reabrir #673, #530, #792 como Apply.
- Fork do vendor Impeccable `$impeccable critique`.
- Medidor de $ / usage Cursor.
- Clone pixel-perfect de dados live (valores ilustrativos ok; **topologia** não).
- Credencial de produção ou sessão humana do Alan no `process_event`.
- Playwright autenticado **dentro** de `submeter_design` (Q2 rejeitou B).
- Fail-open quando a chave do catálogo falta (Q4 rejeitou B).
- Self-service de landmarks na mesma change de Design de produto (Q4 rejeitou C).
- Tratar ausência de campo como tela nova (Q5 rejeitou C).
- Exigir chave de catálogo para tela nova (Q5 rejeitou B).
- HTML de protótipo, rewrite de `DESIGN.md`, pipeline Impeccable visual, Playwright desta coluna.

## Decisions

1. **Q1=A — skill + A/B e `G_design`.**  
   T5 recusa se landmarks/`copied` falharem em `UI impact: affected` + superfície existente. Alternativa rejeitada: só skill/A/B (o r1 passou). Alternativa rejeitada: só máquina (A/B ainda cobrem toggle e sessão).

2. **Q2=A — catálogo versionado + HTML estático; T5 offline.**  
   `G_design` lê o HTML do proto no disco. Sem Playwright autenticado em `submeter_design`. A/B MAY abrir URL viva **fora** do T5 quando houver sessão.

3. **Q3=A — `copied` = soma `COPIED:start`/`COPIED:end`.**  
   Marcadores no HTML do proto (comentário ou texto). Vários intervalos somam. Ausência de par ou soma 0 ⇒ recusa. Alternativa rejeitada: proxy do handoff; HTML gerado com as mesmas CSS variables.

4. **Q4=A — fail-closed sem chave.**  
   Rota declarada sem entrada no catálogo ⇒ T5 recusa. Lookup contra o catálogo **em HEAD** (`git show HEAD:scripts/process-fsm/route-landmarks.yaml` quando o path existe em HEAD; senão working tree só se `git diff --quiet HEAD --` nesse path). Chave acrescentada só no working tree da mesma change **não** conta. Este card **semeia** o catálogo (UI none / `live_route: N/A`); não é change de produto a furar o gate.

5. **Q5=A — campo parseável.**  
   Linhas autónomas em `design.md` (não só prosa, não só `## Prototype`):

   ```
   live_route: /monitor
   surface: existing
   ```

   ou

   ```
   live_route: N/A
   surface: new
   ```

   Regex (multiline, âncora de linha, ênfase `*`/`**` ignorada à volta da chave):
   - `^\s*(?:\*{0,2})live_route:(?:\*{0,2})\s+(\/\S+|N/A)(?:\s+\S.*)?\s*$`
   - `^\s*(?:\*{0,2})surface:(?:\*{0,2})\s+(existing|new)\s*$`
   - `UI impact:` → `none` | `affected` (mesma tolerância a `**`)

   `surface: existing` **ou** `live_route:` que começa por `/` ⇒ exige chave + landmarks + `copied`. `surface: new` **ou** `live_route: N/A` com justificação não vazia na mesma linha ou na frase seguinte ⇒ isenta catálogo/`copied`; T5 ainda exige 3 md + specs; skill/A/B cobrem shell+tokens. `UI impact: affected` + proto presente + nenhum dos dois campos ⇒ recusa. Ausência de campo **não** é tela nova.

6. **Catálogo YAML em `scripts/process-fsm/route-landmarks.yaml`.**  
   Residual da grelha (formato / rotas a semear) fechado aqui. `version: 1`. Chaves = path exacto da rota viva. Cada entrada:

   ```yaml
   /monitor:
     selectors: ["table.signals"]
     texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]
   /favorites:
     selectors: ["table.fav-strategies"]
     texts: ["Estratégias favoritas", "Symbol", "Estratégia", "Ações"]
   /combo/discovery:
     selectors: []
     texts: ["Descoberta de estratégias swing", "Preflight", "Rascunho de varredura"]
   /combo/select:
     selectors: [".combo-page"]
     texts: ["Available Templates"]
   ```

   Check estático: concatenar `*.html` sob `frontend/public/prototypes/<q_git>/` (mesmo path que `process_event` já resolve). Cada `selectors[]` MUST aparecer como substring (aceitar `table.signals` e `class="signals"` via o token listado). Cada `texts[]` MUST aparecer como substring. Sem rede.

7. **`files_g_design` passa a predicado composto.**  
   `G_design` = ficheiros OpenSpec presentes **e** `clone_gate`. `clone_gate`:
   - `UI impact: none` (ou campo ausente **neste** caso none-by-default só quando **não** há proto) → True.
   - Precisão: se existe proto em `frontend/public/prototypes/<q_git>/` **e** `UI impact: affected` → aplicar Q5/Q4/Q3/landmarks.
   - Se `UI impact: affected` e **não** há proto → `clone_gate` True só no sentido de catálogo (T5 continua a exigir 3 md + specs); skill/A/B bloqueiam PASS visual. Este card não enfraquece o “affected exige proto” da skill.
   - `UI impact: affected` + proto + sem `live_route`/`surface` → False.
   - existing → HEAD catalog lookup; miss → False; landmarks miss → False; `copied` 0 ou ausente → False.
   - new / `N/A` justificado → skip catálogo/`copied`.
   Helper novo `scripts/process-fsm/design_clone_gate.py` (parse + estático + copied). `process_event.files_g_design` chama o helper. Injecção `g_design=True` nos testes legais T5 existentes **permanece** (override explícito). Testes novos cobrem o default (`g_design is None`) com fixtures.

8. **`copied` bytes.**  
   Percorrer o HTML (UTF-8). Empilhar `COPIED:start` / `COPIED:end` (pares; conteúdo **entre** os marcadores, exclusive). Soma dos `len(segment.encode("utf-8"))`. Marcador em comentário HTML ou texto conta. 0 pares ou soma 0 ⇒ False.

9. **Fixture r1 BLOCKED.**  
   Apply MUST materializar `scripts/process-fsm/fixtures/792-r1-gallery.html` com sha256 **exacto** `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7` (21275 B, sem `table.signals`). Recuperar do histórico git se preciso. MUST NOT escrever em `frontend/public/prototypes/card-792-monitor-risco-explicito/`. Teste: `classify(html, live_route=/monitor)` → BLOCKED (landmarks e/ou `copied`). O HTML live r2 `1a1ff265…` **não** é essa fixture e **não** deve falhar por “ser o path do #792”.

10. **Skill `design-critic` — fidelidade = landmarks, não chrome.**  
    Substituir a operacionalização L63 (sidebar 224px + `--bg-*` como prova de clone de tela existente). Tela existente: partir da página autenticada da rota (`/monitor`, etc.), preservar listagem/cabeçalhos/ações/expand, aplicar só o delta. Folha de tokens = chrome; **não** substitui clone da página. Anti-padrão nomeado: “N estados ⇒ N cards numa grelha” quando o produto é lista+detalhe. Prompt A/B: Playwright (ou equivalente) abre URL viva da rota **e** URL do proto quando houver sessão; P0 se landmark da listagem faltar; sem sessão, `/login` não é a rota. Toggle Antes/Depois: a vista MUST mudar (Antes = clone, Depois = clone+delta); `aria-pressed` sem script = P0 se for a única “prova” de clone. T5 **não** verifica o toggle (offline).

11. **Σ / yaml T5 intactos.**  
    Sem evento, estado, hook ou `enabled_tools` novo. `G_design` continua o `guard:` de T5; só o predicado Python cresce.

12. **`UI impact: none` deste card.**  
    Nenhuma superfície visual de produto. Prototype N/A. Impeccable/Playwright/`DESIGN.md` = N/A. Campos `live_route: N/A` + `surface: new` documentam o formato Q5 sem disparar catálogo.

## Apply contract

Ficheiros exactos (e só estes) neste worktree, após `Status=Pronto para Dev`:

1. `scripts/process-fsm/design_clone_gate.py` — parse `UI impact` / `live_route` / `surface`; soma `copied`; match estático do catálogo; lookup HEAD (D4); `classify` da fixture r1.
2. `scripts/process-fsm/route-landmarks.yaml` — catálogo v1 com as quatro chaves de D6.
3. `scripts/process-fsm/process_event.py` — `files_g_design` composto (ficheiros **e** `clone_gate`); resolve proto em `frontend/public/prototypes/<q_git>/`.
4. `scripts/process-fsm/test_design_clone_gate.py` — existing + landmarks; `copied` 0/ausente; sem chave HEAD; sem campo + proto affected; `surface: new` isenta; r1 sha256 `068581d6…` BLOCKED; override `g_design=True` não é o default.
5. `scripts/process-fsm/fixtures/792-r1-gallery.html` — bytes cujo sha256 é `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7`.
6. `scripts/process-fsm/test_process_event.py` — T5 com `g_design is None` recusa quando o gate de clone falha; T5 legal com UI none / 3 md + specs continua a passar.
7. `.agents/skills/design-critic/SKILL.md` — D10 (landmarks, galeria P0, A/B URL viva, `/login` ≠ rota, toggle).

MUST NOT: `backend/**`, `frontend/src/**`, `frontend/public/prototypes/card-792-monitor-risco-explicito/**`, `DESIGN.md`, `.cursor/process-fsm.yaml` Σ, `CONTEXT.md`, `docs/adr/`.

## Risks / Trade-offs

- **[Risk]** Evasão `surface: new` em tela que já existe. → Mitigation: A/B/skill (fidelidade); o máquina não adivinha sem o campo (residual aceite; Q5 rejeitou C).
- **[Risk]** Toggle Antes/Depois morto passa T5. → Mitigation: T5 offline (Q2=A); skill/A/B P0 se o controle não muda a vista.
- **[Risk]** Catálogo HEAD vs worktree: primeiro seed deste card. → Mitigation: este card é UI none / `N/A`; seed é o Apply, não um Design de produto.
- **[Risk]** Combo viva já é grelha de templates. → Mitigation: landmark é `Available Templates` + `.combo-page`, não `table.signals`. Galeria P0 só quando o produto é lista+detalhe.
- **[Risk]** Folha de tokens ausente no disco live. → Mitigation: chrome **não** substitui clone; apontar a rota. Não criar a folha neste card.

## Migration Plan

Depois do Apply e archive, o próximo Design `UI impact: affected` de rota existente MUST declarar `live_route`/`surface`, clonar landmarks e marcar `COPIED:*`. Cards já em Aprovação / Pronto / Done **não** são reavaliados por T5. Rollback: reverter o predicado composto e o YAML; Σ yaml não muda.

## Open Questions

Nenhuma Q da grelha aberta. Residuais P2 (não bloqueiam): evasão `surface: new` (skill/A/B); sinónimos de landmark além do catálogo semeado; cobertura de rotas autenticadas menores (`/profile`, `/help`) fica para card futuro de catálogo — T5 fail-closed se alguém as declarar sem chave.

## UI impact

**none** — harness/processo (`process_event`, catálogo, skill, testes). Nenhuma rota, shell, componente, token ou copy de produto. Nenhuma superfície visual nova ou alterada.

## Prototype

N/A — `UI impact: none`. Não há tela Cripto a prototipar; o aceite é o predicado `G_design` + skill/A/B no próximo Design UI affected. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2 accepted-residual:** lookup HEAD não vê untracked — Apply MUST miss se o path do catálogo não existir em HEAD. `live_route` + `surface: new` no mesmo ficheiro ⇒ Apply MUST exigir catálogo/`copied`. Blob r1 `068581d6…` não está em `develop` (só PR #802); Apply MUST copiar para fixtures, MUST NOT checkout no path live #792. Spec “selector = substring” vs `class="signals"`. Evasão `surface: new` / `UI impact: none` com proto de tela existente e `affected` sem proto — skill/A/B.
- **P3 accepted-residual:** Distância/7d condicionais; `Operar` é botão; pin pode sobrescrever `design-critic`; folha de tokens ausente; task 3.3 boilerplate.
- **Prototype:** N/A — `UI impact: none`; aceite = predicado T5 + skill/A/B; sem HTML.
- **Snapshot Impeccable:** `.impeccable/critique/799-card-799-prototype-clone-rota-A.md` e `…-B.md` (r1). Apply/Code Review não lêem. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS** — zero P0/P1; A e B isolados; sem superfície visual por classificar; browser N/A justificado.
