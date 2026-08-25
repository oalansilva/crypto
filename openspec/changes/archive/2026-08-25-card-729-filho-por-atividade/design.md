## Context

Card [#729](https://github.com/oalansilva/crypto/issues/729) (kaizen P2 Operacao). História grelhada no issue (fronteira vazia, rodadas 1–4, 2026-08-25). Sucessor do D8 do [#673](https://github.com/oalansilva/crypto/issues/673): não reabre avaliação Impeccable; troca o freeze “abra chat novo” por filho-por-atividade no mesmo `#<id>`. Não reabre [#530](https://github.com/oalansilva/crypto/issues/530), [#569](https://github.com/oalansilva/crypto/issues/569), [#613](https://github.com/oalansilva/crypto/issues/613), [#667](https://github.com/oalansilva/crypto/issues/667), [#668](https://github.com/oalansilva/crypto/issues/668).

**UI impact: none.** Harness/skills/docs. Nenhuma superfície de produto. Prototype N/A. Impeccable N/A neste card.

## Goals / Non-Goals

**Goals:**

- Chat `#<id>` de Em Refinamento → Done técnico; Homologado/Release fora.
- Pai orquestra; cinco atividades em filhos/ondas com contexto próprio.
- Recusa no mesmo chat (sem “abra `#id Apply`”); T1/T7 intactos.
- Grill bind por Status+`#<id>` (sem branch).
- Sem evento FSM. `AGENTS.md` always-on não cresce.

**Non-Goals:**

- Chat único atravessando vários cards.
- Filho com `isolation=worktree`; spawn por task; nested spawn.
- Virar o default global `inherit`.
- Um crítico só; medidor de $; dual-write `.grok/skills/`.
- Gate/hook na FSM; produto/UI.

## Decisions

1. **Um chat por card, filho por atividade.**  
   Título `#<id>`. O pai não pede chat novo ao mudar de coluna nesse intervalo. Alternativa rejeitada: manter D8 (UX que o operador recusou). Residual: prefixo do pai ainda cresce com retornos curtos.

2. **Pai magro = não executa as cinco atividades.**  
   Pai: `process_event`, git commit/push, recusas, handoff, relaying do grill. Não grelha, não escreve OpenSpec/protótipo, não implementa, não review, não QA. Se o pai “só mais um patch”, Code Review trata como achado de processo.

3. **Mapa de spawns (Status tem que bater).**

   | Atividade | Spawn | Contexto | Tree |
   | --- | --- | --- | --- |
   | Em Refinamento | 1 filho grill | issue + grilling; uma rodada por spawn | cwd do pai (`develop`); sem branch |
   | Design | 1 filho autor | issue grelhado + folha + URL/digest | worktree `card-<id>-*` pós-T1 |
   | pós-Design | onda A/B do **pai** | URL/digest/screenshot + rubrica | mesmo worktree |
   | Em desenvolvimento | 1 filho apply | loop interno fatiado (task+spec+Apply contract) | mesmo |
   | Code Review | onda 2 reviewers | diff exato | mesmo |
   | QA | 1 filho checks | SHA/checks; T14 no pai | mesmo |

4. **Grill é filho + relaying, bind sem branch.**  
   Skill deixa de exigir `card-<id>-*`. Prompt carrega issue id + Status. Filho edita body e comenta o handoff T1. Pai mostra Qs, recebe respostas, re-despacha. Alternativa rejeitada: pai grelha “porque é conversa” — mistura a atividade no orquestrador.

5. **A/B e reviewers = ondas do pai, não nested.**  
   Dual critic/reviewer intactos (#569/#673). Design child não spawna A/B. Apply child não spawna reviewers.

6. **Apply = um filho-coluna, não um spawn por task.**  
   Fatiamento permanece **dentro** do filho. Aceite: o filho de Apply engorda ao longo das tasks (contexto da atividade).

7. **Default `inherit` global não vira isolado.**  
   Lista fechada: filhos de atividade + A/B + dois reviewers. Resto continua inherit.

8. **Recusa operacional (mesmo chat).**  
   Sem `Pronto para Dev` + `implemente`: uma frase com Status atual + “Apply só depois de Pronto para Dev (T7 teu)” + parar. Sem spawn, sem pedir chat novo, sem arrastar.

9. **Runbook, não δ.**  
   Sem estado/evento/hook/`enabled_tools` no yaml. Lei em `alan-workflow` + `design-critic` + `grill-card` + apply skill. Adapter Grok MUST Read o canônico.

10. **Docs.**  
    `backlog-operating-model` troca a linha do chat-por-coluna. `decision-log` ganha entrada 2026-08-25 #729. A entrada #673 permanece histórica.

11. **Este card é `UI impact: none`.**  
    Sem Impeccable/Playwright/protótipo. Crítica isolada: escopo, regressão de gates, riscos operacionais, ausência de superfície. T7 permanece. Snapshot N/A justificado.

12. **Quem grava `## Design Critique` e quem move T5.**  
    A/B só escrevem `.impeccable/critique/**`. O filho autor escreve o resto de `design.md`/protótipo e **não** spawna A/B. Depois da onda, o **pai** pode gravar **somente** a seção `## Design Critique` (bullets + disposition + verdict + path do snapshot) a partir do retorno curto de A/B — não reescreve o resto do arquivo. `process_event submeter_design` (T5) é **só o pai**. Alternativa rejeitada: resume do filho autor só para colar bullets (hop extra). Se A/B saírem P0/P1, o pai re-despacha o filho autor com os achados; o pai não faz polish.

13. **Inherit dos filhos é flag explícito, não virada global.**  
    A linha “Task/subagent usa inherit salvo pedido explícito” **permanece** para Tasks laterais. O runbook MUST mandar spawn de grill / Design-autor / Apply-coluna / QA / A/B / dois reviewers **sem transcript do pai** (flag isolado / prompt autocontido). Sem essa frase no skill, o default L17 fura o card.

14. **Git e δ não saem do pai.**  
    Filho Apply não commita, não dá push, não chama `process_event`, não spawna reviewers. Devolve “task N done / blocked”. Pai: `iniciar_apply` **antes** do spawn, commit na `card-*`, `pedir_review`, onda de review, `aceitar_sha`, filho QA, T14.

## Apply contract

- Editar só skills/docs/specs/testes listados nas tasks. Zero `frontend/src/` e zero produto `backend/`. Zero `.cursor/process-fsm.yaml`.
- Substituir no runbook qualquer “abra `#id Apply|Review`”, “pedir chat novo com o título da coluna”, “Um chat por coluna” pela recusa-no-mesmo-chat + spawn do filho/onda.
- `alan-workflow`: manter inherit **global**; acrescentar que spawns da lista fechada são isolados (sem transcript). Nomear spawn QA (checks/evidência) e T14 no pai.
- `grill-card`: bind = Status=Em Refinamento **da issue N** + N no prompt igual ao `#<id>` do pai; recusa se faltar id, se N divergir, ou se Status ≠ Em Refinamento; frontmatter/description sem exigir sessão `card-<id>-*` / “unbound sessions” como bloqueio; filho edita só a issue N.
- `design-critic`: autor = filho Design; pai grava só `## Design Critique` após A/B; T5 só o pai; se P0/P1, re-despacha o autor (pai não polish).
- Apply skill: um filho-coluna; loop fatiado interno; filho **não** `process_event`, **não** git commit/push, **não** spawna reviewers.
- Pytest (`scripts/process-fsm`, allow-list; não o yaml): skills não mandam abrir chat novo nem “Um chat por coluna”; `grill-card` não exige branch `card-<id>-*` como bind; ajustar `test_grill_card.py` se ainda afirmar `bound_card` = branch.

## Prototype

N/A — `UI impact: none`. Nenhuma rota, shell, componente ou copy de produto. Harness/skills/docs.

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Design Critique

- P0: nenhum.
- P1 (r1): dono de `## Design Critique` / T5, inherit sem flag, bind grill, git no filho Apply — **fechados** (D12–D14 + SHALL `cursor-harness`/`llm-flow-emission` + tasks 1.1–1.4).
- P2 residual (não bloqueia): Purpose `llm-flow-emission` no archive (task 3.1); `test_grill_card.py` needle (task 3.2); paging Em Refinamento em `develop` (yaml frozen; pai spawna com Status+#id); headings OpenSpec ainda “One chat per column”.
- P3: stub Grok description `bound_card`; identidade de cenário OpenSpec.
- Disposition: dual critic r2/r3 **PASS**. Prototype N/A. Sem superfície de produto.
- Snapshot A r2: `.impeccable/critique/729-card-729-filho-por-atividade-A-r2.md`
- Snapshot B r3: `.impeccable/critique/729-card-729-filho-por-atividade-B-r3.md`
- Snapshot UI Impeccable: N/A justificado (`UI impact: none`)
- `Design Agent verdict: PASS`

## Risks / Trade-offs

- [Vendor injeta retorno integral do filho no pai] → contrato de saída curto (Qs da rodada / bullets / findings). Residual #673 aceito.
- [Pai executa a atividade] → achado de processo no Code Review.
- [Nested spawn] → ondas nascem do pai; aceite da história.
- [Relaying do grill] → cada rodada é spawn/`resume_from`; respostas do Alan entram no prefixo do pai.
- [Bind grill sem branch] → filho pode editar o issue errado se o prompt omitir o id. Mitigação D4/contrato: recusa sem N, se N ≠ `#<id>` do pai, ou Status ≠ Em Refinamento.
- [Quem cola o veredito] → D12: pai só `## Design Critique`; T5 pai; polish via re-spawn do autor.
- Sem medidor de $; economia é proxy.
