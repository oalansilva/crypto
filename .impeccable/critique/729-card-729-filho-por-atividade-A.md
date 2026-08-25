# Snapshot — card #729 `card-729-filho-por-atividade` — Assessment A

- Card: #729
- Change: `card-729-filho-por-atividade`
- Critic: Assessment A (isolated Design critic; no parent transcript inherit)
- UTC: 2026-08-25
- UI impact: none (justificado: harness/skills/docs; nenhuma rota, shell, componente ou copy de produto; Prototype N/A; Impeccable/Playwright N/A)
- Branch: `card-729-filho-por-atividade` (worktree HEAD `refs/heads/card-729-filho-por-atividade`). `git status -sb` não executado neste isolado (sem shell). Sem `MERGE_HEAD` / rebase no gitdir do worktree.
- Tuple: `.grok/rules/process-fsm-page.md` ausente. Path bind = 729 / `card-729-filho-por-atividade`. `q` de board não resolvido aqui (sem product write).
- Surfaces lidas: issue #729 (body grelhado, fronteira vazia); `openspec/changes/card-729-filho-por-atividade/{proposal,design,tasks}.md` e `specs/{llm-flow-emission,cursor-harness,grill-card}/spec.md`; specs atuais `openspec/specs/{llm-flow-emission,cursor-harness,grill-card}/spec.md`; runbook `.cursor/skills/alan-workflow/SKILL.md` § Um chat por coluna; `.agents/skills/design-critic/SKILL.md`; `.cursor/skills/grill-card/SKILL.md`; `.cursor/skills/openspec-apply-change/SKILL.md`; `.cursor/agents/{diff-reviewer,code-reviewer}.md`; stubs Grok; `docs/backlog-operating-model.md` gate-de-design; `docs/decision-log.md` #673; `scripts/process-fsm/test_grill_card.py`; `.cursor/process-fsm.yaml` `context_file`.

---

## Brief (operacional)

Sucessor do D8 do #673: o custo é contexto de **atividade**, não o título do transcript. Um chat `#<id>` (Em Refinamento → Done técnico); pai orquestra; filhos/ondas isolados (grill, Design-autor, Apply-coluna, QA, A/B, dois reviewers); recusa no mesmo chat sem “abra `#id Apply`”; grill bind = Status=Em Refinamento + `#<id>` no prompt (não branch `card-<id>-*`); T1/T7 Alan-only; dual critic/reviewer intactos; sem evento/hook/`enabled_tools` na FSM; `AGENTS.md` always-on não cresce; `UI impact: none`.

Audience: operador do harness (Cursor + Grok). Outcome: não trocar de chat nem misturar as cinco atividades no prefixo do pai. Direction: runbook/skills/specs, não δ. Scope: `alan-workflow`, `design-critic`, `grill-card`, `openspec-apply-change`, docs de gate, specs `llm-flow-emission` / `cursor-harness` / `grill-card`, testes de string.

---

## Critique

### Escopo vs issue #729

Proposal/design/tasks cobrem o Entra: um `#<id>`; pai magro (`process_event`, git, recusas, handoff, relaying); mapa de spawns com Status batendo; grill no cwd `develop` sem worktree; Design→QA no worktree pós-T1; ondas A/B e reviewers do pai; Apply = um filho-coluna com fatia interna; default global `inherit` não vira isolado; Homologado/Release fora; specs e skills listadas no issue; Não entra (chat multi-card, um crítico só, `isolation=worktree`, spawn por task, nested spawn, auto-Apply antes de T8, dual-write `.grok/skills/`, reabrir #530/#569/#613/#667/#668) está nos Non-Goals.

Não há superfície visual nova/alterada sem classificação. Prototype N/A e Impeccable N/A neste card são coerentes com o issue.

### Regressão de gates (T1 / T7 / dual / FSM)

- **T1:** grill child comenta espera T1; `process_event priorizar` continua proibido no skill/spec. Sem aresta nova.
- **T7:** recusa `implemente` sem `Pronto para Dev` no mesmo chat; texto canônico “Apply só depois de Pronto para Dev (T7 teu)”. Alan-only T7 não vira evento Agent.
- **Dual critic/reviewer:** ondas de 2 disparadas pelo pai; spec `cursor-harness` e decisão 5 proíbem nested. #569/#673 não reabertos como avaliação.
- **FSM:** decisão 9 + spec `llm-flow-emission` / `cursor-harness`: sem estado/evento/hook/`enabled_tools`. `process-fsm.yaml` `context_file` e T0–T17 ficam. `AGENTS.md` stub não ganha a regra.
- **T14:** QA filho = checks; `integrar_develop` permanece no pai (δ). Correto.
- **Browser / snapshot UI-affected:** este card é none; o runbook alvo não apaga o gate de navegador nem o snapshot obrigatório quando UI affected. Dual critic continua condição de PASS.

Intenção: sem regressão de gate. Furo operacional abaixo pode **na prática** aninhar A/B no Design-autor ou fazer o pai escrever o veredito — isso sim reabre o buraco do #673.

### Role split Design: escritor de `## Design Critique`, polish e `process_event`

Contrato novo (spec `cursor-harness` + design D2/D5 + issue):

- Pai **MUST NOT** author `design.md` nem protótipo.
- Critics **MUST NOT** editar `design.md` / protótipo / produto (só `.impeccable/critique/**`).
- Design-autor **MUST NOT** spawnar A/B (nested proibido) e filho **não** chama `process_event`.
- `## Design Critique` + verdict **MUST** viver em `design.md`.
- Achado P0/P1 no A/B exige patch de protótipo/`design.md` e re-onda.

`design-critic` hoje é um único skill em que **a mesma sessão** (1) escreve OpenSpec/protótipo, (2) spawna A/B, (3) faz polish/browser, (4) grava `## Design Critique`, (5) move `Design → Aprovação de Design`. Task 1.2 só diz: autor = filho; pai não escreve `design.md`/protótipo; pai spawna A/B; cair “Um chat por coluna”. Não há discriminador de papel nem exceção de síntese.

O cenário da spec é mais estreito que o SHALL (“não `/opsx:new`/`/opsx:ff` nem patch de protótipo”), enquanto o SHALL proíbe author de `design.md` inteiro. #673 D3 dava a consolidação da crítica ao pai; #729 tira essa casa sem nomear outra.

Sem uma frase canônica, Apply cai em um destes:

1. Design-autor carrega o skill inteiro → nested A/B e/ou `process_event` no filho.
2. Pai grava `## Design Critique` (e polish) → pai executa Design.
3. Ninguém grava o veredito → PASS impossível / T7 cego.

Isso é buraco de desenho da coluna Design, não detalhe cosmética.

**Contrato que falta (mínimo):**

- Design-autor: OpenSpec + protótipo; **para** após artefatos; MUST NOT spawn A/B; MUST NOT `process_event`.
- Pai: spawna autor, depois onda A/B; **MAY** escrever só `## Design Critique` (síntese dos bullets) **ou** resume o autor com os bullets A/B para gravar essa seção — escolher uma e gravar na spec/task 1.2.
- Se A/B devolver P0/P1: pai **resume** o Design-autor (não nested); autor pacha; pai re-spawna A/B.
- Pai dono de `process_event` `Design → Aprovação de Design` e do publish/handoff/proxies.
- Browser/detector de B continuam na onda; polish de protótipo é atividade do autor, não do pai.

### Inherit default leak

`alan-workflow` L17 hoje: “Task/subagent usa `inherit` salvo pedido explícito no chat.” Stubs Grok: “Map Cursor Task `inherit` to `spawn_subagent` inherit.”

Spec nova: filhos de atividade + A/B + reviewers **MUST NOT** inherit parent transcript; inherit de **modelo**; lista fechada; resto continua inherit.

Task 1.1 reescreve a seção “Um chat por coluna”. **Não** manda alterar L17 nem fixar flags de spawn (Cursor: modelo `inherit` + prompt autocontido / sem transcript; Grok: `spawn_subagent` inherit de modelo, não de conversa). Se Apply só trocar o heading D8, L17 continua a vazar o prefixo do pai para grill/Design/Apply — o problema que o card existe para cortar.

### Grill bind (Status + `#<id>`, não branch)

Issue/spec/task 1.3: precondição `card-<id>-*` **sai**; bind = Status=Em Refinamento + id no prompt; executor = filho; pai relaying; cwd `develop`. Isso é necessário (T1 ainda não ocorreu; `resolve.py` em `develop` é `bound_card=⊥`).

Risco residual real: bind virou **prompt**, não path. Filho com `gh issue edit` pode grelhar N errado se o pai omitir/trocar o id. Mitigação no design (“recusa sem `#<id>` + Status”) não exige:

- consultar Project 1 Status **da issue N do prompt** (não do `bound_card` do cwd);
- recusar se N ≠ título `#<id>` do chat pai;
- manter “Não editar issue de outro card”;
- atualizar frontmatter (`Use when bound_card is set` / `unbound sessions`).

`test_grill_card.py` ainda `assert "bound_card" in text`. Task 3.2 cobre “não exigir `card-<id>-*`”; precisa atualizar esse assert senão Apply quebra o teste ou deixa o texto antigo.

Não é P1: o Entra está certo; a mitigação precisa ser normativa no skill (query Status de N).

### Pai ainda executa / nested spawn

Issue e D2/D5 já classificam: pai executando as cinco = achado de processo no Code Review; nested = proibido, ondas nascem do pai. Sem gate FSM (aceite). O furo **não** é a política; é o skill `design-critic` / apply skill ainda descrevendo a sessão única como executor.

Apply skill hoje não spawna reviewers nem chama `process_event` — menos perigoso que `design-critic`. Falta na task 1.4: filho Apply retorna ao terminar tasks; pai `pedir_review`; filho MUST NOT spawn reviewers / T14.

Git: issue diz pai dono de commit/push; task 1.4 não delimita. Residual: commit na `card-*` pelo filho Apply vs pai. Não bloqueia se o pai continua dono de `process_event` + push/`integrar_develop`.

### Tasks vs Apply contract

Presentes e alinhadas ao Entra: 1.1–1.4 skills, 2.1–2.2 docs, 3.1–3.3 specs/testes/validate, 4.1 zero produto, 4.2 comentário, 4.3 nota de homologação nos dois clientes.

Faltam (ou estão implícitas demais):

- 1.2: discriminador autor vs pai (Critique, polish/resume, `process_event`, sem nested).
- 1.1: L17 inherit + lista fechada + recusa-no-mesmo-chat; grill spawn no `develop`.
- 1.3: frontmatter + query Status da issue N + não editar outro card.
- 1.4: filho não `process_event` / não onda de review.
- 3.2: atualizar `test_grill_card.py` (não exigir branch; não deixar o assert de `bound_card` prender o texto velho).

Grok: D9 MUST Read canônico; dual-write `.grok/skills/` é Não entra. Stubs já são ponte. Task 4.3 cobre homologação. Sem task extra de cópia.

`github-project-board` não cita “um chat por coluna”; não é gap do Entra.

Título da spec `llm-flow-emission` / cenário “New column starts a new chat” ficam ingleses/legado; conteúdo já é spawn no mesmo `#<id>`. Nit.

### UI / produto

Nenhuma superfície. Tasks 4.1 proíbe `frontend/src/` e produto `backend/`. Prototype N/A justificado.

---

## Audit

- A11y / responsive / browser: N/A (`UI impact: none`).
- Gates T1/T7/T15/T16 / dual / yaml: intenção intacta; sem aresta nova.
- Isolamento: lista fechada correta na decisão; L17 e `design-critic` monolítico contradizem a decisão até o Apply contract ser fechado.
- Grill em `develop`: coerente com T1 Alan-only e `enabled_tools` Em Refinamento `[issue_edit, comment]`.
- Snapshot deste card: skill/design dizem N/A justificado na **emissão** T7; este arquivo é evidência da crítica isolada (A), git-tracked, não input de Apply/Review.

---

## Trace

1. Issue #729 — Entra/Não entra, mapa de spawns, grill bind Status+`#<id>`, recusa sem “abra `#id Apply`”, dual ondas do pai, sem FSM.
2. `proposal.md` — capabilities modificadas só nas três specs existentes.
3. `design.md` D1–D11 + Apply contract + riscos (vendor dump, pai executa, nested, relaying, bind sem branch).
4. `tasks.md` 1.1–4.3 — skills/docs/specs/testes; furo nas tarefas de papel/inherit/frontmatter.
5. Spec deltas vs `openspec/specs/*` atuais (D8 “abra chat novo” ainda canônico).
6. `alan-workflow` § Um chat por coluna + L17 inherit.
7. `design-critic` item 6 + author=sessão + handoff move coluna + “outro chat `#id Apply`”.
8. `grill-card` precondição `bound_card` + `card-<id>-*` + frontmatter unbound.
9. `test_grill_card.py` needle `bound_card`.
10. Reviewers já `model: inherit` + prompt “do not inherit Design/Apply transcript”.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

- **P1 — Coluna Design sem dono legal após o split.** Pai MUST NOT author `design.md`; critics MUST NOT edit `design.md`; Design-autor MUST NOT spawn A/B nem `process_event`; `## Design Critique` é obrigatório. Task 1.2 / Apply contract / spec `cursor-harness` não escolhem quem sintetiza o veredito, quem faz polish após P0/P1, nem quem move `Design → Aprovação de Design`. Resultado provável: nested spawn **ou** pai executando Design **ou** T7 sem crítica. Fechar com discriminador de papel + uma via explícita (pai só `## Design Critique` **ou** resume do autor) + pai-only `process_event`.
- **P1 — Default `inherit` (alan-workflow L17 + stub Grok) não está no Apply contract.** Spec exige filhos/ondas sem transcript do pai; L17 manda inherit salvo pedido explícito. Task 1.1 não manda reescrever essa linha nem as flags de spawn. Sem isso o isolado vaza o prefixo — regressão do objetivo do #729.

### P2

- **P2 — Grill bind errado.** Bind por prompt é o Entra certo (T1 ainda não criou `card-<id>-*`). Mitigação incompleta: skill/task 1.3 MUST exigir issue id no prompt, query Status **dessa** N, recusa se N ≠ `#<id>` do pai ou Status ≠ Em Refinamento, e frontmatter sem “bound_card is set / unbound sessions”. Filho não edita outro issue.
- **P2 — Pai executa atividade / nested spawn.** Política já está no issue (achado de Code Review; ondas do pai). Falta normativa no `openspec-apply-change`: filho Apply não `process_event`, não spawna reviewers, retorna ao pai para `pedir_review`/git.
- **P2 — Task 3.2 vs `test_grill_card.py`.** O teste atual exige a string `bound_card` no skill. Apply que só apaga o bind de branch sem atualizar o teste fica vermelho ou preserva texto velho.
- **P2 — Fronteira de git.** Issue: pai commit/push. Task 1.4 não delimita commit na `card-*` pelo filho Apply. Residual aceitável se T14/push/`process_event` ficam no pai.

### P3

- **P3 —** Cenário `llm-flow-emission` ainda se chama “New column starts a new chat” (corpo já é spawn no mesmo `#<id>`).
- **P3 —** Sem skill QA dedicado; 1.1 precisa nomear o spawn QA (checks/evidência) e T14 no pai — cabe no runbook.
- **P3 —** Dual-write `.grok/skills/` continua Não entra; stubs MUST Read bastam (4.3 homologa os dois clientes).
- **P3 —** Residual #673: vendor pode injetar retorno integral do filho no pai; contrato de saída curto já aceito.

### Disposition

P1 abertos: o split Design não fecha o ciclo crítica→veredito→T7, e o inherit global não está no contrato de Apply. P2/P3 são guard-rails de Apply e resíduos do issue (bind prompt, pai executa, testes, git). Prototype N/A. Sem P0 de gate FSM/T1/T7/dual **na intenção**; os P1 são o mecanismo que faria esses gates falharem na operação.

Não emitir PASS até:

1. `design.md` + spec `cursor-harness` + task 1.2 nomearem o escritor de `## Design Critique`, o resume de polish, e o pai como único `process_event` da coluna Design; Design-autor MUST NOT spawn A/B.
2. Task 1.1 + Apply contract incluírem a lista fechada de isolados e a reescrita de alan-workflow L17 (inherit de **modelo**, não de transcript).

### Verdict

**BLOCKED**
