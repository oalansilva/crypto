# Snapshot — Assessment A · card #819 `card-819-clone-pagina-viva`

- Card: #819 — clone da página viva no URL canónico do proto (gate T5 + briefing Design-autor; recidiva #799/#790)
- Change: `card-819-clone-pagina-viva`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested critic)
- Modelo: inherit
- UTC: 2026-09-04T19:14:46Z
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não editar `design.md` / proposal / tasks / specs / HTML live.
- Board (prompt pai): **Status=Design**. `UI impact: none` não saltou coluna.
- Digest `design.md` **medido**: sha256 `c4277d3b1f9435e414280b11a05087478a0161aa448e98cb44f1b8c9664f91c6` · **1353** palavras (`wc -w`) · 10380 bytes · 123 linhas
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto)
- UI impact: **none** (harness: helper T5 + catálogo + skills + testes/fixtures reconstruídas). Nenhuma rota, shell, componente, token ou copy de produto.
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*819*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. O próximo Design de copy visível na landing **não** herda este N/A.
- Method: `proposal.md` / `design.md` D1–D8 + Apply contract / Risks / `tasks.md` 1–4; deltas `design-route-clone-gate` / `impeccable-design-gate` / `process-fsm-event` / `llm-flow-emission`. Disco live (pré-Apply): `design_clone_gate.py`, `route-landmarks.yaml`, landing v4, evidência #790 (`index.html` vs `landing.html`). Q1–Q4=A congeladas 2026-09-03; este Design não as reabre.

---

## Brief (só neste snapshot)

Problema: no T7 Alan não vê a página como vai ficar. Em superfície já existente o Design salta o proto (`UI impact: none` / copy-only) ou entrega um painel ANTES/DEPOIS; o clone fiel, quando existe, fica noutro ficheiro da pasta. Recidiva #799; evidência live #790 (URL canónico = directory index = painel; `landing.html` irmão = clone v4).

Outcome: o URL canónico (`…/prototypes/<slug>/` → `index.html`) é a página viva + delta; copy visível recusa Prototype N/A; painel+irmão falha T5; clone v4 como index passa e não falha por o path conter `790`; N superfícies ⇒ index = primária clonada; briefing Design-autor cola o mesmo texto em `design-critic` e na coluna Design de `covenant-flow` (não dual-write `.dsh`/`.grok`).

Direction: máquina = `canonical_proto_html` + chave pública `landing` + skip UI none só se **não** existing; mentira `none`/`new` sem chave = skill/A/B. Este card é harness (`live_route: N/A` justificado, `surface: new`, sem proto dir) e **deve** permanecer Prototype N/A.

Scope: `design_clone_gate.py`, `route-landmarks.yaml`, testes/fixtures reconstruídas, dois skills. Fora: HTML publicado #790/#792/#799, `frontend/src`, pixel-perfect, auto dsh, redesenhar landing, Σ/evento novo, proto HTML deste card.

---

## 1. Escopo vs grill Q1–Q4=A (2026-09-03)

Qs congeladas; Design não reentrevista. Recorte mapeado:

| Q | Grill (não reabrir) | Contrato neste Design | Implementável no Apply? |
| --- | --- | --- | --- |
| **Q1=A** | Copy visível (landing / Ajuda / Perfil) = a página mudou ⇒ proto obrigatório; copy-only N/A recusado | D5–D6: existing/catálogo sem proto recusa mesmo com `UI impact: none`; D3: «Copy visível … Prototype N/A é recusado»; spec `Visible copy cannot use Prototype N/A`. Mentira `none`/`new` = skill/A/B (Q aceite). Ajuda/Perfil **não** semeados; `live_route: /help` fail-closed | **Sim** — máquina no declarado; skill no visível; residual de mentira aceite |
| **Q2=A** | URL canónico **é** a página viva, não um painel, mesmo com clone-irmão; briefing = clone live page not 6-state panel; N superfícies ⇒ URL principal = primária clonada | D2 `canonical_proto_html` (index; fallback exactamente um `*.html`; extras não concatenam); D3 texto exacto; D4 index=primária; spec painel+sibling recusa; concatenate MUST NOT passar | **Sim** |
| **Q3=A** | Não reabrir Apply do HTML publicado #790/#792/#799 | Non-Goals + Apply MUST NOT nesses paths; D7 fixtures reconstruídas, não `cp` live; proposal «Não reabre HTML publicado» | **Sim** |
| **Q4=A** | Design **não** chega à aprovação se painel/N/A em superfície existente | D5 remove skip incondicional; D6 ordem existing→medir; T5 recusa painel+irmão e existing sem proto (`process-fsm-event` + tasks 2.1–2.2). Este harness N/A+new **ainda** transita | **Sim** |

Não entra (e não foi alargado): Apply de HTML #790/#792/#799; `frontend/src`; pixel-perfect; auto dsh; redesenhar landing; saltar proto em copy visível; Playwright dentro de `submeter_design`; Σ/evento novo; rewrite `DESIGN.md`.

Residuais 1–5 da grelha fechados como *como* (YAML exacto, função, regex, briefing colado, ordem do predicado, nomes de fixture). `Open Questions: Nenhuma Q da grelha aberta`.

---

## 2. Superfície visual (classificação)

Nenhuma superfície visual nova ou alterada ficou sem classificação.

| Superfície | Classificação | Proto deste card |
| --- | --- | --- |
| Rotas autenticadas `/monitor` `/favorites` `/combo/*` | Intactas no catálogo; este card não as redesenha | N/A |
| Landing pública v4 (`frontend/public/prototypes/cripto-farol-landing-v4/index.html`, live `https://criptofarol.com.br/`) | **Existente**; entra no catálogo como chave `landing` `kind: public` (semente de landmarks, não clone HTML deste card) | N/A neste card; **obrigatório** no próximo Design de copy visível |
| Painel #790 + `landing.html` irmão | Evidência / fixture reconstruída; MUST NOT patch live | N/A |
| Ajuda / Perfil | Existentes no produto; **não** semeados; copy visível = skill/A/B + T5 fail-closed se declarados sem chave | N/A |
| Harness (helper, YAML, skills, testes) | `UI impact: none` + `live_route: N/A` justificado + `surface: new` | Prototype N/A **correcto** |

`## Prototype` / `## Prototype Validation` / pipeline Impeccable desta coluna = N/A justificado. Snapshot visual N/A no `design.md`. Este ficheiro é o snapshot da crítica de processo.

Este card **não** salta proto por engano: não há copy visível nem rota de produto. O anti-padrão #790 (N/A em copy visível) fica fechado para o **próximo** Design, não para este.

---

## 3. Disco live vs D1–D8 (sonda deste isolado)

### Gate e catálogo (pré-Apply = furo actual)

`scripts/process-fsm/design_clone_gate.py`:

- `evaluate_clone_gate`: `if ui == "none": return True` (L208–209) — skip incondicional; copy-only #790 passa T5. D5–D6 removem isto.
- `concatenate_proto_html` (L87–91) junta `sorted(proto_dir.glob("*.html"))` — `landing.html` mascara `index.html`. D2 substitui.
- `LIVE_ROUTE_RE` = `(\/\S+|N/A)` — sem `landing`. D1 alarga para `(\/\S+|landing|N/A)` com `N/A` ainda token fechado (não há identificador genérico `\S+` na alternativa; ordem `landing` vs `N/A` não colide).
- `routes_from_catalog` só chaves que começam por `/`. D1 inclui `kind: public`.
- `requires_existing_clone` / `is_new_exempt` só tratam `/`. D5 trata `landing`.

`scripts/process-fsm/route-landmarks.yaml` `version: 1`: só `/monitor` `/favorites` `/combo/discovery` `/combo/select`. Sem `landing`. Sem `kind`. D1 semeia; as quatro `/` permanecem (default `kind: authenticated` se omitido).

`.cursor/process-fsm.yaml` T5: `from: Design`, `event: submeter_design`, `guard: G_design` — intacto (D8). Spec `process-fsm-event` não mexe Σ.

### D1 selectors/texts na landing v4 (disco)

`frontend/public/prototypes/cripto-farol-landing-v4/index.html`:

| Needle D1 | Presente |
| --- | --- |
| classe `faq-section` (selector `.faq-section`) | sim — `<section class="section faq-section" id="faq">` |
| classe `button-primary` (selector `.button-primary`) | sim — CTA e botões do funil |
| `Comprar ou vender cripto? O Cripto Farol responde.` | sim — `h1#hero-title` |
| `FAQ` | sim — nav + kicker |
| `Quero meus 6 meses grátis` | sim — `.button.button-primary` |

`selector_matches` já resolve classe em `class="…"` (não exige o ponto no HTML). Semente D1 casa com a página viva. `/monitor` **não** ganha `kind: public`.

`FAQ` sozinho é substring do painel #790 (`h2` «Landing v4 — FAQ»). Não é load-bearing: o painel **não** tem h1 v4, CTA, `.faq-section` nem `.button-primary`. Os quatro needles restantes recusam o painel mesmo sem concatenar.

### Evidência #790 (não patchar)

`frontend/public/prototypes/card-790-copy-spot/index.html` (URL canónico / directory index):

- h1: `Copy alinhada ao Spot — telas alteradas`
- 6× `<h2>` (secções 1–6); substring `DEPOIS` = 5 (h2.6 Onboarding sem tag DEPOIS) — Context do design diz «6× h2 DEPOIS»; D7 pede `≥6 h2 DEPOIS` na **fixture** (reconstrução, não `cp`)
- link `./landing.html`
- `COPIED` = 0
- sem `.faq-section` / `button-primary` / h1 v4 / CTA

`…/card-790-copy-spot/landing.html` (irmão, **não** canónico):

- clone v4: h1, CTA, `faq-section`, `button-primary`
- `COPIED` = 0 (concatenate live **também** falharia `copied`; o furo T5 do #790 foi o skip `ui==none`, não só o concatenate)
- D7: sibling de teste MUST ter `COPIED` positivo para o concatenate antigo passar e o index-only falhar — correcto; MUST NOT copiar/patchar estes paths live

Clone v4 como único `index.html` + `copied>0` ⇒ PASS contra `landing`, **independentemente** de o path da fixture conter `790`.

### Skills a patchar (D3)

`.agents/skills/design-critic/SKILL.md` L16 / L63: operacionalização **só** rota autenticada. Task 3.1 substitui pelo briefing D3 (autenticada **ou** HTML público `landing`; nunca 6 estados / painel como URL canónico).

`.cursor/skills/covenant-flow/SKILL.md`: coluna Design é a linha da tabela «1 filho autor» + célula `Design` nas Colunas — **não** há parágrafo de clone. Task 3.2 cola o **mesmo** bloco D3 aí (dsh lê este runbook). MUST NOT `.dsh/**` nem `.grok/**`.

---

## 4. Especificidade do Apply contract

Ficheiros exactos (8 itens), MUST NOT listado, YAML `landing` completo, regex `LIVE_ROUTE_RE`, nome `canonical_proto_html`, ordem D6 do predicado, briefing D3 entre aspas para colar, nomes de fixture D7, casos de teste 2.1–2.2 (catálogo 4 `/` + `landing`; 790-painel+sibling FAIL; v4-index PASS ≠ path 790; harness N/A+new sem proto PASS; existing/`landing` sem proto FAIL; UI none+existing recusa).

D6 é load-bearing contra o live `if ui == "affected" and not has_proto: return True` (L214–215): se Apply deixar este short-circuit **antes** de `if existing: medir`, `affected` + existing sem proto voltaria a passar. Tasks 2.1–2.2 («existing / `landing` sem proto FAIL») fecham a ordem. «Resto como hoje» preserva `ui is None and not has_proto → True` (`test_t5_writes_sidecar` usa `design.md` = `# d\n`).

`test_t5_default_g_design_ui_none_transitions` hoje só escreve `UI impact: none` (sem N/A+new). Após D6, `requires_existing_clone(None, None)` é falso ⇒ o skip harness ainda passa. Task 2.2 acrescenta o caso forte N/A+new **e** as recusas; o teste fraco não reabre Q4.

---

## 5. Residuais fechados como *como*

| Residual | *Como* |
| --- | --- |
| 1 catálogo landing | YAML exacto; `kind: public`; `routes_from_catalog` `/` **ou** public; regex; fail-closed HEAD; `/help` `/profile` não semeados |
| 2 medir index | `canonical_proto_html`; fallback exactamente um `*.html`; 0 ou ≥2 sem index ⇒ string vazia ⇒ recusa |
| 3 briefing | Texto exacto em `design-critic` **e** coluna Design `covenant-flow`; não `.dsh`/`.grok` |
| 4 N superfícies | index = primária; extras no comentário; T5 ignora extras; skill/A/B P0 se painel das N |
| 5 evasão UI none | Máquina: `existing` se `/` ou `landing` ou `surface==existing`; `is_new_exempt` falso se chave de catálogo; skip none só se **não** existing. Mentira sem chave = A/B |
| 6 ordem do gate | parse → `existing` → none∧¬existing True → existing ⇒ HEAD + canonical + landmarks + copied |
| 7 fixtures | paths `scripts/process-fsm/fixtures/790-*.html`; não live `card-790-copy-spot/**` |
| 8 Σ | T5 yaml intacto; só helper Python |

---

## 6. Regressão de produto e operacional

- **Produto CriptoFarol:** zero `frontend/src`, zero `backend/`, zero HTML live de proto. Semente YAML aponta `source:` à v4 vigente; não reescreve a landing. `/monitor` permanece autenticada.
- **#790/#792/#799 HTML:** fora do Apply. Fixtures reconstruídas. Concatenate hole testável **só** com sibling `COPIED>0` (live irmão tem `copied=0`).
- **Cards já em Aprovação/Pronto/Done:** não reavaliados (Migration).
- **Chicken-egg HEAD:** o primeiro Design de copy da landing precisa da chave `landing` **já** em HEAD ⇒ este card merge primeiro. Spec: produto MUST NOT semear `landing` na mesma change para bypass. Intencional.
- **Σ / G_design:** predicado composto continua; yaml T5 não muda.

---

## 7. Riscos operacionais (já no design.md)

Nenhum eleva a P0/P1:

- Mentira `UI impact: none` / `surface: new` em copy visível **sem** chave de catálogo → skill/A/B (Q aceite).
- Proto de um só ficheiro não chamado `index.html` → fallback D2.
- Ajuda/Perfil sem chave → fail-closed T5 se declarados; semente futura.
- Pin dsh/`.grok/` desactualizado → lei só nos dois canónicos; stub dsh já aponta ao runbook.

---

## Achados

- P0: (nenhum)
- P1: (nenhum) — Q1–Q4 têm *como* de máquina e/ou skill; testes 2.1–2.2 trancam painel+irmão, v4-index, harness N/A, existing sem proto; D1 casa com v4 no disco; este card N/A está justificado (harness) e não classifica mal nenhuma tela.
- P2: Mentira `none`/`new` em copy visível **sem** `existing` nem chave (`landing`/`/…`). Máquina não adivinha. Já em Risks / D5. Disposition: **accepted-residual**.
- P2: N superfícies — T5 só mede o index; clones extra são honor-system + P0 de A/B se o index for painel. D4. Disposition: **accepted-residual**.
- P2: Ajuda/Perfil copy visível sem chave no catálogo. Fail-closed se `live_route: /help`; skill recusa N/A; semente fica para card futuro. Disposition: **accepted-residual**.
- P3: Context «6× h2 DEPOIS» vs live #790 (6× `h2`, 5× substring `DEPOIS`). Fixture D7 é reconstrução `≥6 h2 DEPOIS`, não `cp`. Landmarks do painel falham na mesma. Disposition: **accepted-residual**.
- P3: `design-critic` L65 ainda diz isenção `surface: new` / `N/A` sem «unless chave de catálogo». Tasks 3.1 nomeiam L16/L63 (D3); T5 `is_new_exempt` falso para `landing` mesmo assim. Disposition: **accepted-residual**.
- P3: `FAQ` é substring do painel; h1+CTA+`.faq-section`+`.button-primary` são os discriminadores (verificados no disco). Disposition: **accepted-residual**.
- Dual-write `.dsh`/`.grok`; patch live #790/#792/#799; `frontend/src`; Σ nova; proto HTML deste card; superfície visual sem classificar; reabrir Q1–Q4: **false**.

---

## Disposition

Zero P0/P1 abertos. Recorte Q1–Q4=A congelado; Non-Goals não alargados. Apply contract executável após Pronto para Dev. Residuais P2/P3 são limites conhecidos (mentira sem chave, extras N, catálogo Ajuda/Perfil, nits L65/FAQ/contagem DEPOIS) — aceites, não bloqueiam. UI none harness sem superfície visual por classificar. Prototype N/A deste card é o comportamento correcto; o próximo Design de copy da landing é que MUST clonar v4 no `index.html`.

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; harness T5/catálogo/skills; nenhuma tela CriptoFarol neste card (copy visível da landing exige proto no **próximo** Design).
Snapshot: `.impeccable/critique/819-card-819-clone-pagina-viva-A.md`
