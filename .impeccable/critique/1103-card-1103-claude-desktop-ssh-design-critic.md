# Card #1103 — Design Critic, rodada 1 (sem-tela)

- Papel: design-critic (filho único da crítica; teto 1 autor + 1 crítico + 1 rework).
- Captura: `cf-1103-design-critic-1.json` (attempt `e177c452-0611-44c9-9374-c22e03c24853`, banda `juizo`, par capturado `claude-opus-5-5` / `high`).
- Objeto: `openspec/changes/card-1103-claude-desktop-ssh/` (proposal, design, 5 specs, tasks), branch `card-1103-claude-desktop-ssh`.
- Fonte: `gh issue view 1103` (body + 6 comentários: 6183362427, 6183698630, 6183722826, 6183874513, 6184024579, 6184214645).
- Nielsen/personas: N/A (sem tela do produto; superfície é o app do fornecedor).

## Verdict: rework

## Rubrica

1. **Tokens** — OK. `design.md` linhas 1–3: `UI impact: none`, `live_route: N/A — harness de processo; ...`, `surface: none`. Batem com o regex de `design_clone_gate.parse_live_route` (`N/A` + justificativa). Sem rota de catálogo emprestada.
2. **Cópia literal** — OK. Diff (ignorando linhas vazias) entre o body do #1103 e `proposal.md` de `## Problema` até antes de `## What Changes`: idêntico.
3. **Critérios observáveis (4)**:
   - C1 `implemente` em Todo: requisito "Process guarantees in the app equal the terminal" + cenário + task 8.2. OK.
   - C2 sessão e filhos lado a lado: requisito "Alan follows ..." + cenário + tasks 4.8/8.3. OK.
   - C3 handoff com cliente/superfície/modelo; evidência faltante reprova: requisito + cenário + tasks 4.1/4.8/8.3. **Furado pelo achado 8** (abaixo): no caminho feliz, a coleta devolve `terminal_unavailable` para filho em segundo plano, então o gate reprova falsamente.
   - C4 etapa sem proteção para visível: requisito "Missing protection ..." + cenário `hooks_inactive`. Task 8.2 não inclui os negativos `AI_AGENT` ausente (listado em design §11) nem `hooks_inactive`; o cenário do spec fica sem task viva.
4. **Residual** — OK. Os 36 itens dos comentários A–E estão em R1–R36 com origem; IDs de comentário conferidos contra as URLs reais. Cada R tem requisito e task (R21 sem teste, aceitável). Nenhum item esquecido.
   - Ressalva R34: task 8.1 (marcada `after-qa`) diz "se ausente, implementar a página no `SessionStart` de `/source` e repetir" — mudança de código depois do QA, sem onda de review. O spec `process-harness` já declara a regra incondicional ("A session opened in `/source` SHALL receive the page"), e o #1101 já está em `develop` (T14 feito), então a reavaliação pedida pelo comentário D pode acontecer no Apply.
5. **Não entra** — OK, com classificação:
   - **R26** (T16 confere o pai no evento): regra existente. `card-1101-claude-code-adapter/specs/claude-code-harness/spec.md:146` já diz MUST recusar T16 com pai fora de `claude/execucao`; o design só aplica no `process_event fechar_release` do cliente `claude`, sem aresta, ator ou reason novo. Não é gate novo. P3: restringir ao cliente `claude` e reusar `observe-parent` + `load_execucao_pair`.
   - **R28** (T5 checa tokens): `G_design` já existe (`files_g_design` → `clone_gate_ok`); o check de tokens já existe em `review_process_checklist._check_design_tokens` (precommit). O design endurece o predicado de um guard existente com uma regra existente, e Alan pôs o item no escopo declarando que não muda gates. Não é gate novo. P3: reusar a mesma função/semântica do precommit para não divergir.
   - §5 (deny de `mcp__ccd_*` com card vinculado): regra de Guard que aplica "filho de etapa só com captura e receipt"; não é gate da FSM. P3: a ferramenta de título usada em §6 precisa estar classificada como permitida, senão a regra "não classificada = deny" bloqueia o próprio `#<id>` no título.
6. **Pasta própria do app** — OK. Explicada em linguagem de operador (§3, citação). Coerente com "falha visível sem fallback": recusa visível, recuperação na mesma sessão por `EnterWorktree`, nenhuma troca de superfície, nada apagado nem adotado.
7. **Ensaio real** — OK. Dono: Alan opera no app (Windows/SSH, `/source`, worktree do app desligado); pai conduz. Sequência: Migration Plan 1–5 + §11 + tasks 8.1–8.5. Evidência definida (§11 "O que é evidência"). Dependência do card empilhado explícita (sobre o SHA com QA verde do #1103; T14 dele depois do T14 do #1103). Gates do card de ensaio: T1/T7 de Alan; nenhum gate fora de Alan. P3: o spec diz "Evidence SHALL be recorded on the card" sem dizer qual; §11 e 8.5 dizem #1103 (por bloco) + card de ensaio. Alinhar no Apply.
8. **Achado do pai (handback em segundo plano)** — **NÃO coberto. P1 contrato.**
   - Código: `claude_evidence._handbacks` (linha ~482) só aceita `queue-operation`/`enqueue` com `<agent-message from="<agentId>">`. Em `extract`, quando `toolUseResult.status` não é `completed` com conteúdo inline, cai em `_handbacks`; sem match → `terminal_unavailable` (retryable, nunca resolve).
   - Host observado (2.1.300, CLI, este pai): o spawn retorna `toolUseResult.status = "async_launched"` (com `agentId`, `resolvedModel`), e a conclusão chega como `queue-operation` com `<task-notification><task-id>{agentId}</task-id><tool-use-id>{call_id}</tool-use-id><output-file>…</output-file><status>completed</status><summary>…</summary><result>…</result></task-notification>`. O host lança todo `Agent` deste pai em segundo plano.
   - Efeito: o Design-autor deste card ficou `terminal_unavailable` no `claude_proxy.py` com filho `completed` e par igual à captura. No app (2.1.295) o mesmo padrão é provável; sem correção, C3 reprova no caminho feliz e o ensaio do card inteiro (§11/8.3) não fecha.
   - O design afirma em §9 "Nada no contrato de evidência muda além da superfície" — isso é falso diante do host real. Nem §8 (tabela de falhas), nem Riscos, nem tasks citam spawn em segundo plano.
9. **Filho da grelha sem `effort`** — OK, registrado: Context, tabela "Primeira sessão real pelo app" (filho `grill-card #1103` sem `effort`, rodou `medium`, sem heartbeat; registro na conta instalado ~02:59) e parágrafo seguinte. Coberto por cenário "Spawn without effort in the app" e task 8.2.

## Achados

- P1 | contrato | handback em segundo plano (`async_launched` + `<task-notification>`) não reconhecido; §9 afirma contrato inalterado | rework
- P2 | contrato | R34 implementado condicionalmente depois do QA (task 8.1) | rework
- P2 | contrato | C4 sem task viva para `AI_AGENT` ausente e `hooks_inactive` no app | rework
- P3 | detalhe de Apply | R26 = regra existente do #1101 no evento; só cliente `claude` | aceito
- P3 | detalhe de Apply | R28 = predicado de `G_design` com a mesma função do precommit | aceito
- P3 | detalhe de Apply | ferramenta de título `mcp__ccd_*` classificada como permitida | aceito
- P3 | detalhe de Apply | fixture do app com filho com `effort` explícito (a grelha teve filho sem `effort`) | aceito
- P3 | detalhe de Apply | local da evidência do ensaio (#1103 vs card de ensaio) alinhado entre spec, §11 e 8.5 | aceito
