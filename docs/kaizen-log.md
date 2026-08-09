# Kaizen Log — Melhoria Contínua de Processo

> **Princípio:** quanto mais o processo é usado, melhor ele fica. Cada execução gera
> evidência; o Kaizen audita; correções aprovadas viram regras/skills/scripts; o próximo
> ciclo valida se a fricção foi eliminada (métricas de recorrência caem).
>
> **Regra de recorrência:** um mesmo padrão de fricção registrado em 2+ auditorias
> tem sua severidade elevada em um nível e vira candidato a promoção de regra
> (`AGENTS.md`/`rules.md`) ou skill. Proposta de exceção ao limite de 3 cards/release
> para padrões recorrentes: pendente de aprovação de Alan (Kaizen propõe, Alan aprova).
>
> **Segurança:** trechos de sessões (máx. 2-3 linhas) são permitidos SOMENTE neste
> arquivo local. Issues públicas levam métricas agregadas e IDs.

---

## 2026-08-09 — Auditoria inicial (card #420)

- **Escopo**: implementação da v1 do Agente Kaizen (card #420, `Status=Todo`).
- **Fonte**: board Project 1, sessões opencode (escopo release ainda não definido).
- **Resultado**: criação da infraestrutura do Kaizen (agent, command, este log,
  label `kaizen`, regras AGENTS/rules).
- **Cards criados**: (a preencher após auditoria de teste da release 2026-08-08).

---

## Template de entrada de auditoria

```markdown
## YYYY-MM-DD — <Escopo> (</kaizen card <id> | /kaizen release <nome> | /kaizen>)

- **Release/card**: <nome ou id>
- **Fontes consultadas**: <board | git | openspec | ci | sessoes | tech-debt>
- **Sessões analisadas**: <n> sessões | <custo/tokens agregados> | <erros por tipo>
- **Custo/eficácia por card**: <card> → <custo> → <status final no board>

### Achados
- F-<n> [severity: blocker|major|minor|info] <título>
  - Evidência: <IDs de sessão/mensagem/tool, PR, commit, item do board>
  - Causa raiz: <...>
  - Correção proposta: <...> (tipo: regra|script|doc|skill|tech-debt)
  - Esforço: <S|M|L> | Prioridade: <P0|P1|P2>
  - Status: <proposto | aprovado | recusado | implementado | verificado>
  - Card: #<issue>

### Trechos de sessão (evidência local)
- <2-3 linhas, sem payload privado/tokens/raciocínio íntegro>

### Padrões recorrentes (2+ ocorrências → severidade +1 e promoção de regra)
- <padrão> | <ocorrências> | <promoção sugerida>
```

## Histórico de mudanças de processo (regras/skills/scripts)

| Data | Mudança | Origem | Evidência |
| --- | --- | --- | --- |
| 2026-08-09 | Criação do Agente Kaizen (agent, command, log, label, regras) | card #420 | issues #420, kaizen-log |

## 2026-08-09 — Auditoria de teste: release 2026-08-08 (`/kaizen release`)

- **Release/card**: 2026-08-08 — cards 361, 384, 395, 399 (todos `Pronto`).
- **Fontes consultadas**: board Project 1 (167 itens), issues + comentários, git/refs/worktrees/stash + `release-guard audit`, `openspec validate --all`, PRs #386/#391-394/#396/#398/#400-406/#409/#411-412, opencode DB (37 sessões, 1686 msgs, 6848 parts, 29 todos — read-only), npm audit frontend.
- **Sessões analisadas**: 3 no escopo da release (validação #395+#399: $0.385 / 4.1M tokens; 2 subagentes vision gpt-5.6-luna $0.006). Cards 361/384 executados no Codex — sessões indisponíveis no DB (limitação).
- **Custo/eficácia por card**: 361/384 (Codex, sem sessão) → `Pronto`; 395/399 → `Pronto` com sessões no DB.

### Métricas
- **Board**: Pronto 150, Cancelado 10, Homologado 3 (#385/#413/#416), Em desenvolvimento 2, Todo 2. Divergência `Status` vs `Fluxo` em 100/167 itens (campo legado); #416 `Homologado` com `Fluxo=Backlog`.
- **Git**: 14 warnings / 0 blockers no release-guard; 6 worktrees extras (2 dirty), refs órfãs de releases anteriores (runtime-card-362-develop, rollback-card-362-369, runtime-develop-card369, release-post-20260802, sync-main-into-develop-20260803, release-20260803-cards-366-374); sem stashes.
- **OpenSpec**: `validate --all` 149/149 PASS; 4 changes arquivadas (2026-08-08); 47 changes ativas com idade variada (higiene pendente).
- **Sessões**: erros de tool 0; `step-finish unknown` 2 (card #385, fora do pacote); todos pendentes 4 (sessão #399); drift de roteamento 49 msgs gpt-5.6-luna em sessão deepseek (card #385, $0.58).

### Achados
- F-1 [major] Card #384: `Design Agent verdict: BLOCKED` às 18:38Z seguido de implementação sem aprovação registrada às 19:30Z (mesmo dia). Correção: exigir comentário/arraste de aprovação de Alan + resolução de BLOCKED registrada no design.md. Esforço S | P0.
- F-2 [major] Card #395: zero evidência de gate de Design/Aprovação (criação 00:51 → Done 01:15). Correção: checklist de gates no PR/commits de integração (design.md/verdict mesmo para tooling). Esforço S | P1.
- F-3 [minor] OpenSpec republicado em múltiplos Gists por change (#361: 3 gists; #399: 3 gists) — spam de comentários. Correção: helper atualizar gist-id existente. Esforço S | P2.
- F-4 [minor] Fragmentação de PRs por card (5 em #384, 4 em #399) + commit vazio de retrigger. Correção: agrupar ajustes pós-review; retrigger via `workflow_dispatch`. Esforço M | P2.
- F-5 [minor] Refs/worktrees de releases anteriores não classificados; preserve/change-413-wallet-zebra-20260808 dirty com WIP após `Homologado`. Correção: estender `release-guard post` (inventário runtime-*/rollback-*/preserve). Esforço M | P1.
- F-6 [minor] Todos do opencode nunca fechados na sessão de validação do #399. Correção: `/opsx:verify`/Done exige todos `completed` ou remoção justificada. Esforço S | P2.
- F-7 [info] Release inicialmente fechada `Pronto` sem deploy PROD — corrigida no mesmo dia (regra + skill). Correção (validação): `release-guard pre` checa evidência de deploy PROD. Esforço S | P1.
- F-8 [info] Tech debt: sheetJS/xlsx 5 high + 3 moderate sem fix upstream. Esforço M | P2.
- F-9 [info] vision-router gravou 49 msgs gpt-5.6-luna na sessão principal deepseek (card #385, $0.58) — auditar transform para garantir vision só em sessão filha; #416 endereça troca de modelo. Esforço M | P2.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #421 — Exigir evidência de aprovação de Design antes de aplicar código | P0 | F-1, F-2 | Todo |
| #422 — release-guard: exigir deploy PROD antes de Pronto e inventariar refs órfãs | P1 | F-5, F-7 | Todo |
| #423 — publish-openspec-card-artifacts: atualizar gist existente + retrigger CI sem commit vazio | P2 | F-3, F-4 | Todo |

### Backlog kaizen (para releases seguintes — 2+ ocorrências elevam severidade)
- F-6: sincronizar todos do opencode no fechamento de card (P2).
- F-8 + F-9: avaliar substituição de sheetJS/xlsx e auditar custo/modelID do vision-router (P2).

### Trechos de sessão (evidência local)
- `ses_0212ac001ffe` — todo `in_progress`: "Teste unitário do plugin vision-router (data URL -> persistir -> placeholder -> …)" + 3 pendentes com card #399 já Done.
- `ses_020c4438effey9rj5N` — 49 msgs assistant modelID=gpt-5.6-luna em sessão deepseek, custo total $0.5789.
- `ses_020e33491ffe` — subagent vision gpt-5.6-luna sem erros; roteamento visual esperado (exceção do #399).

### Limitações
- Cards 361/384 executados no Codex — sessões ausentes do opencode DB.
- Timestamps de itens do board não expostos via `gh project item-list`.
- `npm audit` com snapshot local (sem rede completa).

## 2026-08-09 — Auditoria pós-release: release 2026-08-09 (`/kaizen release`)

- **Release/card**: 2026-08-09 — card 420 (Agente Kaizen). Pacote único `Homologado`.
- **Fontes consultadas**: board (170 itens), issues #385/#413/#416/#420, git/refs/worktrees/stash + release-guard audit, OpenSpec (validate 151/151, archive, specs), CI PRs #424/#425/#426, opencode DB (14 sessões no window, read-only).
- **Sessões analisadas**: 14 no window (08-08→09) — custo total $0.2526, 1.69M tokens in, 0 todos incompletos, 0 drift, 0 `step-finish unknown`, 2 erros de tool (1 `task` "Unknown agent type: kaizen" no bootstrap; 1 edit miss). Sessão principal #420 `ses_01c171a3` $0.1153 → Done.

### Métricas
- **Board**: Pronto 150, Done 3 (#385/#413/#416), Homologado 1 (#420 — movido a Pronto após esta auditoria), Todo 4 (#195 + kaizen #421/#422/#423). Divergências Status vs Fluxo legadas (#416, #395, #361, #384, #353, #355).
- **Git**: release-guard audit PASS (15 warnings/0 blockers); refs órfãs antigas persistem (F-6 da auditoria 08-08, card #422 ainda Todo); refs da própria release pendentes de limpeza.
- **OpenSpec**: validate 151/151; **F-1: change card-420 duplicada em develop (ativa + arquivada)** — corrigida no mesmo turno via PR #427.
- **Sessões**: custo baixo, sem alucinação significativa; 2 spawns vision gpt-5.6-luna pós-merge #419 (troca qwen3.7-plus não propaga para sessões em voo).

### Achados
- F-1 [major] Archive OpenSpec não propagou para develop — change card-420 duplicada (ativa + arquivada). Causa: sync back `main -> develop` adicionou o archive sem remover a pasta ativa. **Corrigido imediatamente** (PR #427, `972d620a`). Proposta: `release-guard post` detecta duplicação change ativa+arquivada. Esforço S | P1.
- F-2 [major] Regressão de status `Homologado -> Done` em #385/#413/#416 sem evidência de autorização. Causa: rework/closure iniciado sem classificar regressão; regra "só avança" não prevê retorno. Proposta: regra/checklist — rework pós-Homologado exige comentário de Alan autorizando regressão. Esforço S | P1.
- F-3 [minor] Divergência de título #416: board "MiMo-V2.5" vs issue "Qwen3.7 Plus" vs implementação qwen3.7-plus. Proposta: regra de sync título board/issue no fechamento. Esforço S | P2.
- F-4 [minor] Troca de modelo do vision não propaga para sessões/spawns em voo (2 spawns gpt-5.6-luna pós-merge). Proposta: troca de modelo de agente exige sessão nova. Esforço S | P2.
- F-5 [info] Erro `task` "Unknown agent type: kaizen" durante bootstrap do próprio agente. Proposta: não invocar subagent recém-criado no mesmo turno. Esforço S | P2.
- F-6 [info] Refs da release pendentes de limpeza pós-Pronto; refs antigas persistem (depende de #422). Esforço M | P2.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #428 — release-guard post detecta change OpenSpec duplicada ativa+arquivada | P1 | F-1 | Todo |
| #429 — rework pós-Homologado exige comentário de autorização e classificação no card | P1 | F-2 | Todo |
| #430 — sync título board/issue + sessão nova após troca de modelo de subagent | P2 | F-3, F-4 | Todo |

### Backlog kaizen (releases seguintes)
- F-5: checklist de fechamento — não invocar subagent recém-criado no mesmo turno (P2).
- F-6: limpeza de refs órfãs antigas (já em #422) + refs da release após Pronto (P2).

### Trechos de sessão (evidência local)
- `ses_01c171a3` — 1× task error "Unknown agent type: kaizen" (bootstrap do próprio agente; recuperado; 5/5 todos completed, $0.1153).
- `ses_01c807cb` (tree) — spawns vision `ses_01c08305`/`ses_01c05d64` pós-merge #419 ainda com gpt-5.6-luna; título de sessão "trocar GPT Luna por MiMo-V2.5" divergente do issue.

### Limitações
- Timestamps de itens do board não expostos via `gh project item-list`.
- Evidência de arraste de aprovação não visível via API (só comentários).
- Validação de deploy/URL PROD pertence ao fechamento da sessão principal (executada: source e2c89d4d, services ativos, endpoints ok).

---

## Auditoria pós-release 2026-08-09 — cards #385, #413, #416 (release develop->main #437)

- **Escopo**: release 2026-08-09 (cards #385 Monitor Spot Binance, #413 carteira leitura, #416 roteamento visual qwen3.7-plus). Deploy PROD `27f9e1bf` validado antes da auditoria (regra 14).
- **Board**: 173 itens — Pronto 151, Cancelado 10, Todo 7, Homologado 3 (#385/#413/#416), Em desenvolvimento 2. Prioridade P0=30, P1=77, P2=11, vazia=55; sem Responsável: 21 (inclui #413/#416).
- **Git**: worktree único, 0 stashes; origin/develop ancestral de origin/main com trees idênticas; branches/worktrees do pacote limpas; guard post PASS.
- **OpenSpec**: validate 150/150 pré-archive; 3 changes do pacote arquivadas + 4 delta specs sincronizadas (`monitor-direct-spot-trading` nova, `user-preferences-binance-credentials`, `external-balances`, `visual-analysis-routing`); 148/148 pós-archive.
- **CI**: PR #437 MERGED (27f9e1bf); 20 checks pass + 6 skipping condicionais esperados (qa-gate base develop, deploy-staging var inativa).
- **Sessões**: 41 no window, custo $2.01; #385 ≈ $1.23, #413 ≈ $0.10, #416 ≈ $0.06; nenhuma sessão cara sem Done.

### Achados
- F-1 [minor P1] Evidência documental do deploy PROD ficou só no worktree (doc do pacote com placeholders em develop/main); dois docs de release da mesma data em paralelo. Proposta: antes de `Pronto`, commitar doc preenchida (com seção kaizen); uma doc canônica por release. Esforço S.
- F-2 [minor P2] Campos do board incompletos em cards da release (#413 Responsável/Prioridade/Tipo vazios; #416 Responsável vazio; título board vs issue divergente). Proposta: `release-guard post` valida campos do pacote e título board/issue. Esforço S.
- F-3 [minor P2] Caminhos inventados na delegação visual do #413 (4× File not found + respawns) e 3× webfetch 404. Proposta: path-check antes de delegar ao vision; sem respawn por arquivo inexistente. Esforço S.
- F-4 [minor P2] Títulos de sessão não informativos em sessões caras ("Casual greeting" 4.1M tokens $0.38). Proposta: título descritivo obrigatório em sessões de trabalho. Esforço S.
- F-5 [minor P1] Reincidência (2ª auditoria): todos do opencode nunca concluídos (card-399) e comentário OpenSpec duplicado no card. Proposta: `/opsx:verify`/Done exige todos completed; helper atualiza gist/comentário existente; elevar #423 para P1. Esforço S.
- F-6 [info] 2× `step-finish unknown` e spawns vision gpt-5.6-luna pós-merge #419 — já conhecidos, cobertos por #430. Sem ação nova.

### Cards kaizen (máx 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #43X — release-guard post valida evidência documental e campos do board antes de Pronto | P1 | F-1, F-2 | Todo |
| #43X — path-check antes de delegar análise visual; zero respawn por arquivo inexistente | P2 | F-3 | Todo |
| #43X — fechamento exige todos completed + título de sessão informativo; elevar #423 a P1 | P2 | F-4, F-5 | Todo |

### Backlog kaizen (releases seguintes)
- F-6: troca de modelo não propaga para sessões em voo (já em #430).

### Trechos de sessão (evidência local)
- `ses_01d6…` — 4× `File not found: /tmp/opencode/bl413/{old,new}-{desktop-table,mobile-cards}.png` após delegação vision da sessão principal do #413.
- `ses_01db…` — 3× `webfetch 404` em `docs.github.com/en/rest/attachments/...`, `.../issues/issue-comments`, `github.com/git/git/actions/runs/1`.
- `ses_0212ac…` — todo `in_progress` nunca atualizado ("Teste unitário do plugin vision-router ...") + 3 pendentes; título "Casual greeting", 4.1M tokens, $0.38.
- `ses_01c807→ses_01c083/ses_01c05d` — spawns vision gpt-5.6-luna 2 min após merge #419 (sessão em source sem pull; worktree do card já usava qwen3.7-plus).

### Limitações
- Timestamps do board não expostos via `gh project item-list`.
- Evidência de arraste `Aprovação de Design -> Pronto para Dev` não verificável via API (só comentários).
- Cards 361/384 executados no Codex — fora do opencode DB.
