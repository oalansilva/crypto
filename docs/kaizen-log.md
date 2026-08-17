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
| 2026-08-14 | Fechamento de release como gate: `RELEASE_DATE` canônica, doc única sem placeholder exigida no `pre`/`post`, entrada de `/kaizen release` em `kaizen-log.md` pré-condição do `post`, `RELEASE_BRANCHES` obrigatório com ausência local+remota, `main` local sincronizada como blocker, ordem canônica no AGENTS.md e spawn vazio de subagent como erro explícito de handoff | card #518 (relacionado a F-3/F-6/F-7 da auditoria 2026-08-14) | issues #518, change `card-518-kaizen-release-gate`, `scripts/release-guard` |

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

---

## 2026-08-09 — Auditoria pós-release: release kaizen 421-440 (`/kaizen release`)

- **Release/card**: 2026-08-09 — pacote kaizen #421/#422/#423/#428/#430/#438/#439/#440 (PR #451 merge `4e7c125f`; docs #452/#453; limpeza dívida #454/#455 `c25e662f`).
- **Fontes consultadas**: board (176 itens), issues/comentários 421-440, PRs 443-455 + checks, git/refs/worktrees/stash + release-guard audit, OpenSpec validate 144/144 + status (8 changes do pacote), docs/release-2026-08-09.md, opencode DB (45 sessões, mode=ro).
- **Sessões analisadas**: 45 no window — custo total $2.505; pacote ≈ $0.05/card; todos 10/10 completed na sessão de implementação (`ses_0198` $0.417); erros pré-fix #439 (5 file_not_found, 3 webfetch 404) e pré-fix #440/#423 (ses_0212 "Casual greeting" $0.385/4.1M tokens, 4 todos incompletos) sem reincidência pós-fix.

### Métricas
- **Board**: Pronto 154, Homologado 8 (pacote), Cancelado 11, Em desenvolvimento 2 (#197/#259), Todo 1 (#195). Pacote 8/8 com campos (Resp/Prio/Tipo) e título board==issue sincronizados (fix #430/#438 funcionando).
- **Git**: 1 worktree limpa, 0 stashes; refs órfãs runtime-*/preserve/*: 0; guard audit PASS (2 warnings, 0 blockers). Branches da release em origin aguardando closeout pós-Pronto.
- **OpenSpec**: validate 144/144; 8 changes do pacote ativas e completas (archive pendente no fechamento); ~33 changes antigas de cards terminais ainda ativas (F-3).
- **CI**: PRs 443-450 qa-gate verde; PRs 451-455 verdes (qa-gate skipping condicional em PR→main, padrão já documentado).
- **Sessões**: pacote limpo — 0 loops, 0 todos eternos, 0 título genérico em sessão cara (pós-fix).

### Achados
- F-1 [minor→major por recorrência, P1] Comentários de evidência de Done duplicados em 8/8 cards do pacote (postado 2×, formato diferente). Causa: post em lote sem dedupe. Proposta: helper verifica commit ref existente antes de postar; regra 1 evidência por transição. Esforço S.
- F-2 [minor, P1] Guard post não inventaria branches `change-*/card-*/release-*` (só runtime-*/preserve/*): dívida de releases antigas (08-03, mai-jul) sem enforcement. Proposta: estender inventário + checklist de deleção no closeout. Esforço M.
- F-3 [minor, P2] ~33 changes OpenSpec de cards Pronto/Cancelado nunca arquivadas. Proposta: rodada `/opsx:bulk-archive` + check no guard. Esforço M.
- F-4 [minor, P2] Cards presos há 2 auditorias: #197/#259 em Em desenvolvimento, #195 em Todo. Proposta: triagem no próximo turno. Esforço S.
- F-5 [info, P2] Homologado sem comentário padrão "Homologado por Alan" nos 8 cards (arraste/chat não verificável via API). Proposta: warn no guard (extensão #438). Esforço S.
- F-6 [info] "Modelo antigo pós-merge" — 2 spawns vision gpt-5.6-luna 2-5 min pós-merge #419; nenhum além desse par; regra #430 validada.
- F-7 [info] ses_0212 (pré-fix) permanece no DB como recorrência que motivou #440/#423; sem ação nova.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #456 — dedupe de comentários de evidência no fechamento (1 por transição) | P1 | F-1 | Todo |
| #457 — release-guard post inventaria change-*/card-*/release-* + deleção no closeout | P1 | F-2 | Todo |
| #458 — bulk-archive de changes de cards terminais + check no guard | P2 | F-3 | Todo |

### Backlog kaizen (releases seguintes)
- F-4: triagem dos cards presos #197/#259/#195.
- F-5: check de comentário de homologação no guard post (extensão #438).
- F-6/F-7: observabilidade (sem ação nova).

### Trechos de sessão (evidência local)
- `ses_0198` — 10/10 todos completed; 3× edit oldString; 1× PermissionDenied ao editar skill global (helper) antes da versão do repo — sem impacto.
- `ses_0212` — 1 todo in_progress + 3 pending nunca atualizados (card-399); título "Casual greeting", $0.38 (pré-fix #440/#423).

### Limitações
- Timestamps do board não expostos via `gh project item-list`.
- Evidência de arraste/homologação não verificável via API (só comentários).

---

## 2026-08-11 — Auditoria release 2026-08-11 (cards 463, 464, 456, 457, 458) (/kaizen release)

- **Escopo**: release 2026-08-11 — cards 463, 464, 456, 457, 458 (merge main `412ed9ad`/`5619c22a`, deploy PROD validado).
- **Fonte**: board Project 1 (184 itens), PRs 465-479 + checks, `scripts/release-guard audit`, `openspec validate --all` (131/131), 35 sessões opencode na janela 08-09..08-12 (`~/.local/share/opencode/opencode.db`, mode=ro), curl PROD.
- **Métricas**: pacote 5/5 com 1 comentário Done cada; **zero duplicação** (dedupe #456 funcionou — cards 456/457/458 postados pós-merge do helper, 463/464 pré-merge, sem duplicatas); CI 15/15 runs success; 0 branches órfãs/worktrees/stashes pós-closeout; 4 changes ativas = pacote (archive pendente no closeout); custo de sessão do pacote ≈ $0.70 (vs $2.50 da release anterior, ~20× menor).

### Achados
- F-1 [recorrência, P1] Card #195 "Backup de ambiente" preso em Em Refinamento desde 05-12 (3ª auditoria reportando o mesmo card — estava em Todo na 08-09, agora Em Refinamento). Proposta: triagem + aviso de idade por coluna no guard audit. Esforço S.
- F-2 [recorrência, P1] 5/5 cards do pacote em Homologado sem o comentário padrão "Homologado por Alan na develop." (mesma lacuna F-5 da auditoria 08-09; transição por arraste/chat não passa pelo helper). Proposta: guard post com RELEASE_CARDS exige comentário de homologação (warn audit / blocker post) + post retroativo em dry-run. Esforço S.
- **Saneamento F-2 (card #480, 2026-08-13):** dry-run validado e comentário canônico postado exatamente uma vez nos cards [#456](https://github.com/oalansilva/crypto/issues/456#issuecomment-5287148541), [#457](https://github.com/oalansilva/crypto/issues/457#issuecomment-5287148517), [#458](https://github.com/oalansilva/crypto/issues/458#issuecomment-5287148509), [#463](https://github.com/oalansilva/crypto/issues/463#issuecomment-5287148552) e [#464](https://github.com/oalansilva/crypto/issues/464#issuecomment-5287148514), usando a evidência da release/merge `412ed9ad`; consulta posterior contou `1` ocorrência por card. O `release-guard` passou a validar o pacote informado em `RELEASE_CARDS`: warning em `audit`, blocker em `post`, com consulta fail-closed e dedupe numérico dos IDs.
- F-3 [minor, P2] Título board divergente da issue no #463 (rename pós-Done; Title não editável via API Projects v2; nota postada sem aprovação explícita). Proposta: regra de nota de divergência + warn no guard. Esforço S.
- F-4 [info, P2] Branches do pacote deletadas antes do movimento para Pronto (closeout técnico precede etapa kaizen→Pronto). Proposta: documentar ordem canônica no AGENTS.md. Esforço S.
- F-5 [info, P2] `main` local desatualizado pós-release (comparação oficial por origin correta). Proposta: passo de atualização de main local no closeout. Esforço S.
- F-6 [info, P2] Sessão paralela swing trade fora do pacote (kimi-k3, $2.44) — validar se foi escolha de Alan; herança interna consistente. Esforço S.

### Cards criados (máx 3/release — regra kaizen)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| (a criar) — guard exige evidência de homologação no closeout + post retroativo | P1 | F-2 | Em Refinamento |
| (a criar) — triagem de cards presos por coluna + alerta de idade no guard | P1 | F-1 | Em Refinamento |
| (a criar) — divergência board/issue em rename pós-Done exige nota + warn | P2 | F-3 | Em Refinamento |

### Backlog kaizen (releases seguintes)
- F-4: ordem canônica de deleção de branches (doc AGENTS.md).
- F-5: atualização de `main` local no closeout (guard post warn).
- F-6: validar modelo padrão de sessão (kimi-k3 vs deepseek-v4-flash).

### Trechos de sessão (evidência local)
- `ses_013f` — 1 erro isolado de tool (JSON parse em heredoc), sem repetição; demais sessões do pacote 6/6, 7/7, 7/7 todos completed.
- Dedupe #456: cards 456/457/458 com comentário único "Implementação concluída" formato "Commit/merge: PR N (sha)" pós-merge do helper; 463/464 pré-merge sem duplicata.

### Limitações
- Timestamps por coluna não expostos via `gh project item-list` (usado updatedAt global via GraphQL).
- Evidência de arraste/homologação não verificável via API (só comentários) — motiva F-2.

## 2026-08-12 — Triagem do card #195 (card #481 kaizen)

- **Ação**: triagem do #195 "Backup de ambiente" concluída — decisão **Cancelado** (estado já aplicado no board em 11/08; nota formal registrada no card em 12/08: https://github.com/oalansilva/crypto/issues/195#issuecomment-5272103735).
- **Motivo**: escopo de backup de ambiente (openclaw, skills, apps, banco) coberto por operação do ambiente Oracle (snapshots/backups de infra DEV/PROD); card sem dono operacional ativo e preso há 3 auditorias kaizen.
- **Implementado (card #481)**: `release-guard audit` ganhou bloco `card_age_inventory` — inventário de cards por coluna com idade em dias (GraphQL `updatedAt` do item), warn informativo para >30 dias (default, configurável via `CARD_AGE_THRESHOLD_DAYS`), limite por coluna (`CARD_AGE_MAX_PER_COLUMN`, default 5), paginação até 20 páginas, falha de obtenção como warn sem interromper. Somente em `audit`; pre/post inalterados.

## 2026-08-17 — Cards #530/#531 (kaizen UI do #469)

- **Ação**: regras de apply/verify após o #469 ter marcado tasks de UI `[x]` sem código e ter implementado a Discovery pelo contrato de API em vez do protótipo aprovado.
- **#530**: `/opsx:apply` com `UI impact: affected` carrega o protótipo aprovado como spec de layout; API não é spec de UI.
- **#531**: `/opsx:verify` e Code Review exigem evidência por task de UI contra o protótipo; Playwright `[ ]` bloqueia Done. Skill `openspec-verify-change` e `opsx-verify.md` passam a tratar `[x]` sem implementação como CRITICAL.
- **Evidência base**: PR #528 / card #469 — tasks 6.2–6.10 `[x]` sem implementação; 7.8/7.9 `[ ]` em Done.

## 2026-08-17 — Kaizen release (release 2026-08-17, cards 469/502/503/504/516/517/518/562)

- **Release/card**: 2026-08-17 — cards 469, 502, 503, 504, 516, 517, 518, 562 (Homologado → Pronto após deploy PROD).
- **Fontes consultadas**: board Project 1, git/worktrees/stash + `release-guard pre` PASS, `openspec validate --all` 148/148, PR #564, transcripts Cursor desta sessão, CI push/PR no SHA `f4b89208`.
- **Sessões analisadas**: sessão Cursor do lote (cutover #562, cancelamento #550/#559, isolamento #549, deploy PROD). Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: pacote já Homologado na abertura do lote; closeout nesta sessão até PROD `91f5620e`.

### Métricas
- **Board**: pacote 8 Homologado; 2 Cancelados no mesmo dia (#550/#559) por conflito com #562; #549 em Em Refinamento isolado.
- **Git**: worktrees extras e WIP do #469/OpenSpec do #549 bloqueariam o `pre`; isolados em `card-549-unify-strategy-title-description` e `card-469-idempotency-normalization-wip`.
- **CI**: e2e da *push* em `develop` falhou (timeout em `walkforward-prototype-check` contra URL viva DEV); e2e do PR #564 verde; rerun da push passou depois do protótipo 200 em DEV. `qa-gate` skip no PR para `main` é regra do workflow (`base_ref == develop`).
- **OpenSpec**: archive do pacote + leftovers Pronto/Cancelado; skip-specs em deltas incompatíveis; spec `cursor-harness` promovida no closeout.

### Achados
- F-1 [major] E2E funcional `walkforward-prototype-check.spec.mjs` navega `https://dev.criptofarol.com.br/prototypes/...` (não o preview do CI). Push harness-only (#562) falhou 30s no seletor enquanto DEV reconstruía. Correção: apontar o spec ao servidor Playwright local/`preview` do job, não à URL DEV. Esforço S | P0.
- F-2 [major] 8 cards Homologados sem comentário canônico até o closeout (helper postou retroativo). Correção: o arraste para Homologado deve disparar o helper no mesmo turno. Esforço S | P1.
- F-3 [minor] `gh project item-list` ainda estoura GraphQL no meio do lote (remaining 89). Correção: listagens de closeout sem `content.body`. Esforço S | P1.

### Padrões recorrentes
- E2E acoplado a DEV vivo | 1 ocorrência nesta release (candidato a regra se repetir) | promoção: spec Playwright local
- Homologado sem comentário canônico | recorrência vs #480/#518 | helper existe, falta o turno do arraste

### Cards kaizen propostos (máx. 3; não criados neste closeout — Alan aprova)
- P0: desacoplar e2e de protótipo da URL DEV (F-1)
- P1: comentário de homologação no mesmo turno do arraste (F-2)
- P1: item-list do board sem body no closeout (F-3)

## 2026-08-17 — Kaizen release (lote 2, cards 529/530/531/553/554/566/567/568)

- **Release/card**: 2026-08-17 lote 2 — cards 529, 530, 531, 553, 554, 566, 567, 568 (Homologado → Pronto após deploy PROD).
- **Fontes consultadas**: board Project 1, git/worktrees/stash + `release-guard pre` PASS / `audit` PASS, `openspec validate --all` 143/143 (código) e 142/142 (archive), PR #578, transcripts Cursor (`0c0d840f` implementação; `0b02d24f` closeout), CI do PR #578.
- **Sessões analisadas**: sessão de implementação dos 8 cards (worktrees) e sessão de closeout desta release. Sem consulta a `opencode.db`.
- **Custo/eficácia por card**: pacote já Homologado na abertura do lote; closeout até PROD `2261ad56`. F-1 do lote 1 (e2e DEV vivo) entrou neste pacote como #568 e foi publicado.

### Métricas
- **Board**: 8 Homologado no lote; fora: #569 Aprovação de Design, 2 Em Refinamento (#549 e gerador de templates).
- **Git**: 9 worktrees extras bloqueavam `pre`; 8 mergeadas removidas; WIP do #569 commitado em `059f6f38` e ref local apagada. Stash 0.
- **CI**: PR #578 verde (e2e 4m49s); `qa-gate` skip no PR para `main`.
- **OpenSpec**: 8 changes arquivadas; 7 specs novas; skip `02-agent-chat-favorites.md` (já Hermes).
- **PROD**: installer Discovery + dispatcher/Celery active; health 200; bundle `index-DbfcRxXg.js`.

### Achados
- F-1 [major] Homologado sem comentário canônico nos 8 cards até o closeout (helper retroativo). Recidiva do F-2 do lote 1 no mesmo dia. Esforço S | P1.
- F-2 [major] `pre` trata doc canônica do dia como PR documental e exige `PROD_DEPLOY_EVIDENCE`; o segundo pacote reusou a evidência `91f5620e` do lote 1 para abrir o PR de código #578. Esforço M | P1.
- F-3 [minor] Extra worktree e branch local in-flight (#569) falham o `pre` sem `PRESERVED_BRANCHES` (só vale em post/audit). Esforço S | P2.

### Padrões recorrentes
- Homologado sem comentário canônico | 2 ocorrências no mesmo dia (lotes 1 e 2) | promoção: helper no turno do arraste
- E2E acoplado a DEV vivo | corrigido neste lote (#568)

### Trechos de sessão (evidência local)
- `0c0d840f` — implementação sequencial 568→554→553→566→529→530→531→567 em worktrees.
- `0b02d24f` — closeout: `git branch -D card-569-code-review-bugbot` após push `059f6f38` para o `pre` passar.

### Cards kaizen criados (máx. 3/release)
| Card | Prioridade | Origem | Status |
| --- | --- | --- | --- |
| #579 — comentário Homologado no mesmo turno do arraste | P1 | F-1 (recidiva lote 1 F-2) | Em Refinamento |
| #580 — segundo pacote no mesmo dia vs doc canônica no pre | P1 | F-2 | Em Refinamento |
| #581 — worktree extra / branch in-flight no pre | P2 | F-3 | Em Refinamento |

## 2026-08-14 — Kaizen release (release 2026-08-14, cards 470/480/481/482/489/491/509)

- **Ação**: auditoria kaizen pós-release concluída (read-only). F-1 a F-8 registrados abaixo.
- **F-1 (P0)**: rate limit GraphQL como evento central do closeout — guard legado consumia ~4.900 pontos/execução (`gh project item-list --limit 500` paginado); reset de ~1h; nasceu o bug #509. Medição pós-fix: **204 pontos** por execução (item-list 500 + pr list 100), delta ~24x menor. Change `card-509-release-guard-graphql-budget` concluída (tasks 5.1–5.4) e **arquivada** em 2026-08-14 com sync de spec `release-worktree-hygiene`; `openspec validate --all` 137/137.
- **F-2 (P1)**: check de changes OpenSpec terminais do guard cego para nomes sem id de card e in-progress em card terminal → card kaizen proposto.
- **F-3 (P1)**: doc de release fragmentada em 6 PRs + PR de DAG #515; ordem canônica proposta (deploy → doc única sem placeholder → 1 PR).
- **F-4 (P2)**: 8 warns de título board/issue sem nota (#469/#472 batch do #470); notas postadas apenas em #470/#491.
- **F-5 (P2)**: frontier como sessão principal na transição do #491 (~$4.5, pré-regra formal); títulos genéricos em sessões caras.
- **F-6 (P1)**: `/kaizen release` executado após `Pronto` com spawn vazio (0 messages) — kaizen-log sem entrada até esta edição; ordem canônica como gate proposto.
- **F-7 (P2)**: 17 branches da release pendentes de deleção; `main` local stale (recorrência da auditoria 08-11).
- **F-8 (P2)**: 3 todos abertos em sessão do #491; erros isolados de tool (webfetch 404, read not found) sem loop.
- **Cards kaizen criados**: 3 (P0 bug #509 follow-up; P1 bug check changes terminais; P1 story ordem canônica de fechamento), todos em `Status=Em Refinamento`.
- **Trechos de sessão (evidência local)**: `ses_00240169` — "Rate limit GraphQL zerou (0/5000, reset em ~57min) — o guard post consome ~4900 pontos por execução"; guard post com RELEASE_CARDS classificou branches como "preserved (card in flight; not deleted)" e o post passou (caso fail-open residual). `ses_000d79ef` — spawn kaizen com 0 messages/0 parts.
