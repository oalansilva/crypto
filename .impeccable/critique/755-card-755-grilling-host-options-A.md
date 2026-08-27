# Snapshot — Assessment A · card #755 `card-755-grilling-host-options`

- Card: #755 P2 kaizen Operacao — grilling mostra todas as opções no Grok e no Cursor
- Change: `card-755-grilling-host-options`
- Critic: Assessment A (crítica isolada de Design; sem transcript do pai)
- Modelo: inherit
- UTC: 2026-08-27T02:26:59Z
- Tuple: `q=Design` `bound_card=755` `q_git=card-755-grilling-host-options` (`.grok/rules/process-fsm-page.md`). Write produto deny. `enabled_events`: recriticar, submeter_design, cancelar.
- UI impact: **none** (justificado: harness/skills/specs/testes de processo; nenhuma rota, shell, componente ou copy de produto; host TUI = vendor, Non-Goal)
- Prototype: N/A (sem HTML em `frontend/public/prototypes/`; `openspec validate card-755-grilling-host-options --type change --strict` = valid)
- Impeccable visual / Playwright / detector: N/A justificado
- Method: leitura do body grelhado #755 + comentário canônico; `proposal.md` / `design.md` / `tasks.md`; change specs `grill-card` + `cursor-harness`; specs atuais; `.cursor/skills/{grill-card,grilling,alan-workflow}/SKILL.md` (trecho Grill-card); stubs `.grok/skills/{grill-card,grilling}`; `scripts/process-fsm/test_grill_card.py` (read-only)

---

## Brief

**Problema:** o card da ferramenta do host (`ask_user_question` / `AskUserQuestion`) pode pintar só a recomendada; o operador confirma a seta ou escreve Other.

**Outcome:** Q fechada com N≥2 alternativas reais no card, nos dois clientes; recomendada primeiro `(Recommended)`; Other não conta; Q aberta sem `options[]` fictícias; pai relaying 1:1; vendor Matt e stubs #668 intactos.

**Direction:** lei no adapter `grill-card` + uma linha de relay no `alan-workflow`; dump filho→pai estruturado; needles pytest; sessão real = Homologado (Alan), não QA.

**Scope:** skills/specs/testes de processo. Fora: TUI vendor, FSM, #667/#668, `grok_stubs.py`, produto, protótipo.

---

## Critique

### 1. Fidelidade ao #755 grelhado

Body (fronteira vazia, rodada 1: Q1=B, Q2=A, Q3=A, Q4=B, Q5=A) está sintetizado, não reentrevistado.

| Entra do issue | Onde no Design |
| --- | --- |
| Lei nos dois clientes; vendor Matt não reescrito | D1 + Non-Goals + Apply contract |
| Canônico `grill-card` + **uma linha** Grill-card em `alan-workflow` | D1, D6; tasks 1.1–1.2 |
| Q fechada N≥2 reais; recomendada primeiro `(Recommended)`; Other não conta | D2; spec ADDED; task 1.1 |
| Q aberta: markdown e/ou Other; proibido `options[]` fictícias | D3; spec Open question |
| Relaying: pai chama o host com todas as options; filho lista N opções, não só `➡️` | D5 dump; D6; spec child dump + `cursor-harness` |
| Fallback Matt: escolhas no **corpo**; seta só recomenda | D4; spec Markdown fallback |
| Comentário canônico idempotente; #755 já tem um — não postar outro | D8; spec Canonical already exact / Frontier reopens / text wrong; task 5.2 |
| Needles pytest; sessão real = Homologado, não QA | D9; tasks 3.1–3.2, 5.2 |
| `UI impact: none`; sem gate/hook/evento FSM; `AGENTS.md` always-on não cresce | D10; spec No FSM change; task 5.1 |

Residuais de história que o issue mandou o Design fechar:

- Forma do dump filho→pai → **D5** (lista `Opções:`, recomendada primeiro; rejeita “só o bloco Matt”).
- Relay só em `grill-card` vs mínimo `cursor-harness` → **D6** (`cursor-harness` mínimo porque a linha é do orquestrador).

`Open Questions: Nenhuma` — coerente. Proposal/design/tasks/specs não reabrem a fronteira.

Comentário no issue (2026-08-27T01:53:53Z, `oalansilva`): texto **exato** `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` D8 + task 5.2 (deixar; não duplicar) batem com o AC.

### 2. Escopo vs Non-Goals (#667 / #668 / vendor Matt / stubs / FSM)

| Non-Goal | Status no recorte |
| --- | --- |
| Reescrever `.cursor/skills/grilling/SKILL.md` | Fora. Vendor atual = cópia Matt (`❓` + `➡️`); needles exigem que continue assim e **sem** nomes de ferramenta |
| Mudar TUI Grok/Cursor | Fora. Contrato de **uso** de `options[]`, não patch de produto vendor |
| Gate/hook/evento FSM; `.cursor/process-fsm.yaml` | Fora. Spec `cursor-harness` “No FSM change”; `enabled_tools` Em Refinamento permanece `[issue_edit, comment]` (teste atual). Host tool ≠ `enabled_tools` |
| Reabrir #667 (porta) | Delta **evolui** a spec `grill-card` (apresentação da Q + comentário idempotente) sem mexer bind Status+`#<id>`, DoD no body, proibição T1/`CONTEXT.md`/`/opsx:*` |
| Reabrir #668 (adapters / gerador) | Stubs `.grok/skills/{grill-card,grilling}` continuam “MUST Read o canônico”; **não** nomeiam a ferramenta (grep atual: 0 hits). `grok_stubs.py` não entra nas tasks |
| Options fictícias para Q aberta | D3 + spec + Não entra |
| Dual-write Hermes / `~/.codex` | Não entra; test_grill_card já cobre ausência |
| Sessão real como gate de QA / Done técnico | D9; Homologado (Alan) |
| `AGENTS.md` always-on cresce | Spec + task 5.1 |

Proposal “New Capabilities: (nenhuma)” está certo: ADDED requirements em capabilities já existentes, não spec nova.

Apply contract + task 5.1 fecham o recorte de ficheiros: só `grill-card` SKILL, **uma linha** `alan-workflow` Grill-card, deltas OpenSpec, testes em `scripts/process-fsm`. Zero `frontend/src/`, zero produto `backend/`, zero yaml, zero stubs, zero vendor.

### 3. Regressão de processo (T1 / T7 / dual / FSM / grill bind)

- **T1:** filho continua proibido de `process_event priorizar` e `gh project item-edit` Status. Comentário canônico ainda é espera de Alan. Idempotência **não** arrasta coluna nem republica T1. Sem aresta nova.
- **T7:** Alan-only. `UI impact: none` não pula colunas (design-critic + alan-workflow). T7 permanece; Gist ≠ crítica. Snapshot visual N/A; este ficheiro é o snapshot da crítica de processo.
- **Dual A/B:** intacto (esta onda). `tasks.md` “Design-critic / Impeccable N/A” é no bloco **Apply** (não correr design-critic na implementação). Não lê-lo como skip de A/B na coluna Design.
- **FSM:** sem estado/evento/hook/`enabled_tools`. `process-harness` e gerador sem delta (issue AC Design).
- **Grill bind:** Status=Em Refinamento + N no prompt; sem exigir `card-N-*`. Spec Unbound/wrong column intacta. Design deste #755 não grelha de novo.
- **Pai magro / filho isolado:** D5/D6 reforçam: filho não chama host; pai relaying. Não reabre #729 (um chat por card).

Intenção de gate intacta. Sem P0/P1 de regressão.

### 4. Riscos operacionais pedidos

**Pai vs filho no host tool — fechado como decisão, residual de Apply.**  
D5: filho isolado devolve dump com N labels + recomendação; **não** chama a ferramenta (operador está no chat do pai). D6: quem chama = pai; mapeamento 1:1, mesma ordem, recomendada primeiro; `cursor-harness` + uma linha `alan-workflow`. Spec child dump AND “isolated child MUST NOT call”. Task 1.1 ecoa.  
Tensão residual: needles **exigem** `AskUserQuestion` e `ask_user_question` **dentro** de `grill-card/SKILL.md` (lido pelo filho). Se Apply gravar “chame AskUserQuestion…” sem a frase **quem chama é o pai**, o filho dispara o card numa sessão que Alan não vê, ou o pai + filho duplicam o card. O Apply contract já manda deixar explícito. Needles **não** afirmam “filho não chama” / dump `Opções:`. Homologado (sessão real) é o gate TUI, como o issue pediu. **P2 residual, não furo de desenho.**

**Comentário duplicado — fechado.**  
D8 + três cenários (já exacto → deixar; fronteira reabre → não segundo; texto errado → editar/minimizar). Task 5.2: não postar outro em #755 (já há o exacto). Não há caminho de Apply que peça `gh issue comment` neste card.

**Options fictícias — fechado.**  
D3 + spec “Open question has no fake options” + Non-Goal. Q fechada com 1 option + Other como “segunda via” foi alternativa rejeitada (D2).  
Nota Grok: `ask_user_question` exige `options` (cada option: `label`+`description`). Q aberta no Grok **não pode** usar o card sem inventar opções → cai em markdown no chat, que o contrato já permite. Cursor permite AskUserQuestion open-ended. Apply deve tratar Grok Q aberta = markdown, nunca dummy A/B. **P2 de clareza, não contradição.**

Outros riscos do design (modelo ignora skill e manda 1 option; TUI trunca `description` → nome no **label**; Other parece terceira via) estão nomeados e aceites; needles não provam TUI.

### 5. Superfície visual — classificação

Nenhuma superfície de produto nova ou alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy de produto | **none** — fora do recorte (task 5.1) |
| `backend/` de produto | **none** |
| Protótipo HTML / Playwright | **N/A** — sem pasta `prototypes/*755*`; Prototype N/A no design |
| Rubrica Impeccable (fidelidade/carga/a11y/viewport) | **N/A** — sem UI de produto |
| Card TUI `AskUserQuestion` / `ask_user_question` | **vendor** — Non-Goal mudar TUI; este card só o contrato de `options[]` |
| Markdown de skills | processo, não UI de produto |

`UI impact: none` está justificado e alinhado ao issue. Não falta protótipo do card do host: prototipar TUI vendor seria escopo proibido.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: Needles em `grill-card` exigem os nomes das ferramentas no skill do **filho**; o conjunto 3.1 não tem needle de “filho não chama” / dump D5 / “quem chama é o pai”. Apply tem de conservar a frase D5 no canônico; Homologado apanha card duplo ou colapso.
- P2: Cenários Grok/Cursor da spec falam em `ask_user_question.options[]` / `AskUserQuestion.options[]` no “grill round” sem dizer **parent-called**. D5/D6 e o cenário Child dump fecham; Apply não deve ler isso como o filho chamar a tool.
- P2: Schema Grok exige `options[]` → Q aberta no Grok = só markdown (nunca dummy). Implícito em D3; vale uma frase no Apply do skill.
- P3: `cursor-harness` nomeia a tool Grok (adapter Cursor). Aceitável (D6 mínimo); a lei dual-client vive em `grill-card` + linha `alan-workflow`.
- P3: Batch da rodada (um call com todas as Q fechadas vs um call por Q) não está no Design. O vendor Matt já manda a fronteira inteira numa rodada; não bloqueia.
- P3: `tasks.md` “Design-critic / Impeccable N/A” é Apply; A/B desta coluna não se salta.

## Disposition

Nenhum P0/P1. P2 residuais = fidelidade de Apply + Homologado (Alan), não recriticar o recorte. Não editar `design.md` por estes P2.

## Verdict

**PASS** (zero P0/P1 aberto; P2 residual ok)

## Snapshot

`.impeccable/critique/755-card-755-grilling-host-options-A.md`

Visual/Playwright: N/A (`UI impact: none`).
