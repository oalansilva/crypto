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
