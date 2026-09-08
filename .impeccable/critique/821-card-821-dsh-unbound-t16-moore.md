# Snapshot — Design critic (sem-tela, 1 critic) · card #821 `card-821-dsh-unbound-t16-moore`

- Card: #821 — kaizen: dsh unbound não pode deny T16 (suba a release) por causa da página Moore
- Change: `card-821-dsh-unbound-t16-moore`
- Critic: 1 isolado (NOT A/B); inherit de modelo; sem transcript do pai; sem nested agent
- Modelo: inherit
- UTC: 2026-09-07T23:46:00Z
- Round: 1 (teto D4 sem-tela = 1 autor + 1 crítico + 1 rework)
- Tuple (este isolado): hook `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Board: Status observado **Design** (prompt). Issue OPEN `kaizen` + `priority:P1` + `front:operacao` + `type:operacao`. REST `GET /repos/oalansilva/crypto/issues/821` (não `gh issue view`). `comments: 2` (recidiva `session-35e78019`; grill-card fronteira vazia).
- Digest `design.md` **medido**: sha256 `ce64f55f95927c09c7cf238e41afeefdd5568fa025fa0a210503c7644e4f4c79` · **1931** palavras (`str.split`) · 13689 bytes · 126 linhas.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto; pai cola depois)
- UI impact: **none** (harness Moore / T16 closeout dsh; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*821*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Justificativa no `design.md` não vazia (aceite = dump autenticado `:3080` + goldens G1–G8). Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- Overlay live: `pin: v1.1.13`; `clients.dsh.auto: false`.
- Gate tokens parseáveis (linhas próprias, duas vezes: header + secções):
  - `UI impact: none`
  - `live_route: N/A harness-only; dsh Moore page / T16 closeout; no product route`
  - `surface: new`
- Clone gate isento via `UI impact: none` + `live_route: N/A`. **Nenhuma** rota de catálogo emprestada (`/monitor` `/favorites` `/combo/*` `landing`).
- Bloco D4 teto: **presente** no `design.md` (texto exacto da skill).
- Method: issue #821 REST; comentários `5576468669` (recidiva) e `5576704601` (grill); proposal / design D1–D7 + Apply contract / Risks / G1–G8 / `tasks.md` 1–7; deltas `process-fsm-paging` + `covenant-flow`; live `paging.py` `UNBOUND_PAGE`, `unread_page()`, `.cursor/hooks/process-fsm-session-start.sh` fallback, `.dsh/plugin/process-fsm-guard.js` `covenant-flow:moore` → `runPage(cwd)`, skill Release, `test_paging.py` `PLAYBOOK`, `AGENTS.md` 14 linhas.

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| `openspec/changes/card-821-dsh-unbound-t16-moore/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-821-dsh-unbound-t16-moore/specs/{process-fsm-paging,covenant-flow}/spec.md` | lido |
| Issue #821 body + 2 comments (REST) | lido |
| `scripts/process-fsm/paging.py` (`UNBOUND_PAGE`, `unread_page`, `page`) | lido (o que o Design muda) |
| `.cursor/hooks/process-fsm-session-start.sh` fallback | lido (hardcode do stub antigo) |
| `.dsh/plugin/process-fsm-guard.js` `covenant-flow:moore` | lido (consome `runPage`; sem segundo stub) |
| `.cursor/skills/covenant-flow/SKILL.md` ## Release | lido (D6 acrescenta uma linha) |
| `scripts/process-fsm/test_paging.py` `PLAYBOOK` | lido (needle `subir lote` a fatiar) |
| `.covenant-flow/overlay.yaml` | lido (`pin: v1.1.13`, `clients.dsh.auto: false`) |
| `AGENTS.md` | lido (14 linhas; ponteiro overlay on-demand já existe) |
| `frontend/src/**`, `backend/` de app, proto HTML 821 | **none** / ausente |
| GUI dsh `:3080` | **vendor** — homologação dump; não prototipar |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

---

## Brief (só neste snapshot)

Nas sessões dsh `session-ffe87792` / `session-766065f3` (2026-09-03) Alan pediu `suba a release` unbound no cwd canónico DEV; root deny T16 em ~8s, 0 tools. Recidiva `session-35e78019` (2026-09-07, `fechar release`): root leu `covenant-flow` e **mesmo assim** deny («sem aresta T16»; «skipping overlay load per guardrails»). Header ainda injeta `Não carregue playbook de release.` + `enabled_events: (unbound)`. δ já avalia `fechar_release` unbound-on-develop; o modelo leu paging como deny. Cursor/Grok cooperam (#613); dsh é o outlier.

Direction: (D1) reword `UNBOUND_PAGE` no compilador único `paging.py` (quatro injectores); (D2) stub pinado sem a ordem absoluta + três wordings de pedido; (D3) excepção always-injected, sem parser per-turn; (D4) fallback bash Cursor = a mesma constante; (D5) `unread_page()` intacto; (D6) uma linha na skill Release, `AGENTS.md` não cresce; (D7) pin produto após `v1.1.13`. DoD humano = **só dsh** dump `:3080` com ≥1 tool do playbook T16; skill+read sozinho falha.

---

## Rubrica (UI none + D4 teto)

### 1. Escopo vs Entra / não entra do issue #821

**Entra — mapeado:**

| Entra (body) | Onde no pacote |
| --- | --- |
| Pedido explícito unbound dsh (`q=None`, `bound_card=⊥`, `q_git=develop`): não deny textual; carrega overlay e segue T16 | D1–D3, D6; Goals; spec paging «Unbound stub is not a T16 deny»; spec covenant-flow «Explicit-release pedido»; tasks 1.1 / 3.1 / 7.1 |
| Write produto em `develop`/unbound continua deny | D2 MUST `Write produto deny`; Non-Goals; Guard `decide()` intocado |
| Texto Moore deixa de ser lido como «proibido fechar release» nessa sessão sem card | D2 MUST NOT `Não carregue playbook de release.`; G1 |
| DoD humano **só dsh** dump `:3080`; ≥1 tool playbook T16; skill+read **falha** | proposal Impact; design Homologação; spec «Human dump remains mandatory and dsh-only»; task 7.1 |
| Não-regressão: idle unbound sem dump always-on; Cursor/Grok no pedido explícito; **sem** dump nos quatro | D1 compilador único + G1/G2 needles `release-guard`/`deploy PROD`; Non-Goal dump quatro clientes |

**Não entra — não reaberto:**

- #613 / #652 / #812 / #782 / #784 / #786 / #817 como trabalho
- Auto dsh (`clients.dsh.auto: false` live e G8)
- Vendor `deepseek-ai/deepseek-harness`
- Σ / `fechar_release` / `M_lote` / `process_event.py` / `t16.py` / `guard.py` `decide()`
- Produto `backend/` / `frontend/src/`
- Dual-write Hermes / `~/.codex/skills/`
- Executar lote PROD neste card
- Exigir `bound_card` para T16
- Segundo card para a recidiva 2026-09-07
- Closeout com card bound + coluna unread (`unread_page()` — D5)
- DoD humano com dump nos quatro clientes
- Rotas de catálogo / HTML / `DESIGN.md` de produto

Proposal «New Capabilities: (nenhuma)» correcto: a excepção já está na lei T16 (`lote_git("develop")`).

### 2. Decisões de operador (grelha, fechadas) — honradas

| Operador | Design |
| --- | --- |
| DoD humano = **só o dsh** | Honrado em proposal, design, spec, task 7.1. Pytest **não** substitui. Dump Cursor/Grok/OpenCode **não** é critério. |
| Prioridade **P1** | Não reabre como P0 de lote; Non-Goals não exigem fechar o lote neste card. |
| Closeout deste card = **só sessão sem card** | D5 `unread_page()` fora; residual nomeado; alternativa «limpar os dois» rejeitada. |

Design **não** reentrevista Alan. Open Questions: nenhuma bloqueante.

### 3. D1–D7 stress-test

**D1 — compilador único vs inject dsh-only.**  
Live: `page()` é o único compilador; dsh `covenant-flow:moore` chama `runPage(cwd)` (plugin L301); Grok `write_grok_page`; OpenCode transform; Cursor `sessionStart` chama `paging.py` com fallback bash. Recidiva: ler a skill **não** chega se o header ainda proíbe o playbook. Inject só dsh seria dual-write da lei e deixaria Cursor fallback + Grok/OpenCode no stub antigo. Alternativas rejeitadas (só skill; inject dsh paralelo; crescer `AGENTS.md`) são as certas. **Aceite.**

**D2 — texto pinado.**  
`bound_card=⊥. Write produto deny. Playbook de release não é always-on. Pedido explícito suba a release / fechar release / subir lote: carregue overlay e inicie T16.`  
MUST `Write produto deny`; MUST três frases; MUST NOT ordem absoluta; MUST NOT stub Homologado / `release-guard` / `deploy PROD`. Nomear `subir lote` como wording ≠ dump (#613). Envelope (tupla, `enabled_events: (unbound)`, footer overlay on-demand) intacto. Não lista `fechar_release` em `enabled_events` (display ≠ lei; inventaria aresta). Uma linha; teto Moore ≤20. **Aceite.** Não é playbook T16 no stub.

**D3 — excepção no stub always-injected, sem parser NLU.**  
`page()` corre no assemble/sessionStart; **não** vê o turno. Idle e explícito partilham o texto: idle = «não despeje»; explícito = «carregue overlay e inicie T16». Chat ≠ δ para T1/T7/T15/T18/Write; `process_event fechar_release` continua a medir `M_lote`. Parser per-turn no dsh seria quarto-cliente-só e não reescreveria o header já lido. **Aceite.**

**D4 — fallback Cursor = a mesma constante.**  
Live fallback L9 hardcodeia o stub antigo. `test_session_start_adapter_fallback` afirma `UNBOUND_PAGE in ctx`. Grok/OpenCode/dsh não têm este hardcode. Alternativa «fallback mínimo sem a excepção» reintroduziria deny T16 se Python falhasse. **Aceite.** Sincronia Python/bash = G5 (detalhe de Apply).

**D5 — `unread_page()` intacto.**  
Live L35–44 ainda diz `Não carregue playbook de release.` com `bound_card=N`. Fora do Entra (operador: só sem card). Residual explícito; G3 afirma a ordem antiga. **Aceite; não é P0/P1 deste card.**

**D6 — uma linha na skill, `AGENTS.md` não cresce.**  
Live Release já nomeia pedido explícito + overlay, **mas não** diz que `bound_card=⊥` / `enabled_events: (unbound)` são display. Recidiva: modelo leu a skill e saltou overlay «per guardrails». A linha fecha esse furo sem dual-write T0–T17 e sem crescer `AGENTS.md` (14 linhas hoje; G7 ≤40). Stubs `.dsh/` `.grok/` `.opencode/` intactos (≤8, MUST Read). **Aceite.**

**D7 — nucleo via pin após `v1.1.13`.**  
`paging.py` é nucleus (`implantar --pin` copia). Patch só no consumidor reverte no próximo pin. Overlay live `pin: v1.1.13`. Tag = próximo patch livre; rebase no tip (irmãos na mesma pele); `clients.dsh.auto: false`; sem major; sem vendor DeepSeek; δ/T16/produto UI intocados. **Aceite.** Número exacto da tag = Apply (G8).

### 4. Gate tokens + Prototype N/A + teto D4 (rubrica, não rodada extra)

- `UI impact: none` — parseável, não vazio.
- `live_route: N/A harness-only; dsh Moore page / T16 closeout; no product route` — ausência + justificativa curta.
- `surface: new` — mesma forma do helper que #850 harness-none; clone isento porque `live_route: N/A` + UI none. **Não** empresta `/monitor` `/favorites` `/combo/*` `landing`.
- Prototype N/A + Prototype Validation N/A + Impeccable N/A: justificativa não vazia.
- Bloco D4 teto colado no `design.md` (texto exacto).
- Sem-tela: 1 crítico desta onda (NOT A/B) — correcto.

### 5. Risco operacional

| Risco | Tratamento | Classe |
| --- | --- | --- |
| Stub novo atinge Cursor/Grok (já cooperavam) | G1/G2 preservam #613 (sem `release-guard` / `deploy PROD` / stub Homologado) | aceite |
| Needle `subir lote` no tuple `PLAYBOOK` actual rebenta unbound | Risks + Apply MUST fatiar por fixture; G4 Todo MAY continuar a proibir; G1/G2 permitem só no unbound | P3 Apply |
| Fallback bash dessincroniza | G5 `UNBOUND_PAGE in ctx` | P3 Apply |
| Próximo `--pin` reverte | D7 tag + `implantar --pin`; rebase irmãos | P3 Apply |
| Sessões dsh já abertas mantêm header antigo | Migration: novo assemble; sem migrate de banco | aceite residual |
| `unread_page()` continua a proibir playbook com card bound | D5; Entra = só sem card | aceite residual |
| Chat `suba a release` ≠ δ | D3: wording autoriza **carregar** playbook; `fechar_release` mede `M_lote` | aceite |
| Homologação `:3080` ≠ worktree / pytest | Task 7.1 MUST; pytest não substitui; card **não** corre lote PROD | aceite |
| Modelo idle unbound passa a carregar overlay porque o stub nomeia T16 | AC2 do issue é dump **da página** always-on, não NLU do idle; página continua sem frames Homologado/release | aceite residual |
| `enabled_events: (unbound)` continua (recidiva citou «sem aresta») | Issue: display ≠ lei; D2 rejeita listar `fechar_release`; D6 nomeia o display | aceite (não inventar aresta) |

### 6. Buracos de produto/contrato visível

Nenhum. O aceite humano (dump `:3080` com tool de playbook T16, não só skill+read) está no contrato e **não** foi tornado residual. Write deny permanece. #613 idle-unbound sem dump permanece. Fronteira unread bound permanece fora. Σ/T16 measurers intocados. Sem superfície Cripto sem classificação.

G1 afirma `suba a release` e `fechar release` como needles positivos; `subir lote` fica no texto D2 mas **não** como needle positivo do golden (para não colidir com dump-forbid). D2/Apply contract/task 1.1 ainda MUST as três frases. Lacuna de golden, não de contrato — P3 Apply.

---

## Critique

### P0

(nenhum aberto)

Contrato visível intacto: Entra/não entra do #821, três decisões de operador, Write deny, #613 idle, DoD dsh-only, Prototype N/A, zero rota de catálogo.

### P1

(nenhum aberto)

D1–D7 honram o Entra. Residual `unread_page()` é fora do Entra (operador), não furo. `enabled_events: (unbound)` como display é facto do issue, não omissão.

### P2

(nenhum)

### P3

- **P3 — fatiar `PLAYBOOK` (`subir lote`) unbound vs Todo.** Live `test_paging.py` L28 `PLAYBOOK = ("release-guard", "subir lote", "deploy PROD")` e L92–93 aplica o tuple ao unbound. D2 põe `subir lote` no stub. Design Risks já manda fatiar por fixture; G4 Todo MAY continuar a proibir. **Aceite / detalhe de Apply.**

- **P3 — G1 não trava `subir lote` como needle positivo.** D2 MUST as três frases; G1/spec unbound THEN só afirmam `suba a release` e `fechar release`. Apply segue D2/task 1.1. **Aceite / detalhe de Apply.**

- **P3 — dual constante Python vs bash fallback.** G5 afirma igualdade. **Aceite / detalhe de Apply.**

- **P3 — wording exacto da linha Release (D6) e tag patch após `v1.1.13` (D7/G8).** Conteúdo pinado; Apply escreve a linha e corre `git ls-remote --tags` + rebase no tip. **Aceite / detalhe de Apply.**

- **P3 — sessões dsh já abertas / `unread_page()` residual.** Migration e D5 nomeiam. **Aceite residual.**

---

## Cobertura do prompt

| Item | Achado |
| --- | --- |
| Escopo vs Entra/não entra | **Fecha.** Nenhum Entra omitido; nenhum Não entra reaberto. |
| Operador: DoD dsh-only / P1 / só sem card | **Honrado.** |
| D1 compilador vs dsh-only | **D1 correcto** (recidiva = header, não skill). |
| D2 stub sem ordem absoluta + pedidos | **Pinado**; #613 needles intactos. |
| D3 sem parser per-turn | **Correcto** (`page()` não vê o turno). |
| D4 fallback Cursor | **G5**; live ainda tem o texto antigo (Apply). |
| D5 `unread_page()` | **Fora**; G3 afirma a ordem antiga. |
| D6 uma linha skill / AGENTS.md | **Honrado** (14 linhas; G7). |
| D7 pin após v1.1.13 | **Honrado**; tag livre = Apply. |
| Gate tokens parseáveis | **Presentes** (UI impact / live_route / surface). |
| Prototype N/A | **Justificado**; sem catálogo emprestado. |
| D4 teto 1+1+1 | **Presente** no design; esta onda = 1 crítico. |
| Dump `:3080` opcional? | **Não.** Task 7.1 MUST NOT residual. |
| Detalhe de implementação reaberto como P0/P1? | **Não.** P3 aceite. |

---

## Disposition

- P0: (nenhum) — **n/a**
- P1: (nenhum) — **n/a**
- P2: (nenhum) — **n/a**
- P3 PLAYBOOK/`subir lote`, G1 needle, fallback bash, linha skill/tag pin, residual unread/sessões velhas: **accepted** (detalhe de Apply / residual nomeado)
- Prototype N/A: **n/a** (justificado)
- Rotas de catálogo: **n/a** (nenhuma emprestada)
- Gate tokens: **present**
- `design.md`: **não editado** por este crítico

Pai: zero P0/P1 abertos → pode publicar `## Design Critique` com estes bullets e submeter. MUST NOT polish a partir daqui. MUST NOT `process_event` neste filho. Sem segundo rework (não há P0 novo de produto).

---

## Verdict

**PASS** — zero P0/P1 abertos. Escopo = Entra do #821. Operador honrado. Tokens parseáveis. Prototype N/A justificado. Sem catálogo emprestado. P3 = detalhe de Apply aceite.

Snapshot: `.impeccable/critique/821-card-821-dsh-unbound-t16-moore.md`

Confirm: este crítico **não** editou `design.md`, proposal, tasks, specs, HTML, `backend/`, `frontend/src/`. Não `process_event`. Não commit.
