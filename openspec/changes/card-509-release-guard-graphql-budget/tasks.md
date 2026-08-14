## 1. Snapshots e loaders no release-guard

- [ ] 1.1 Adicionar `ensure_board_snapshot` e `ensure_pr_snapshot` no shell principal (statements simples, sem command substitution), gravando `BOARD_JSON`/`BOARD_STATE` e `PRS_JSON`/`PRS_STATE`
- [ ] 1.2 Validar completude do Project: `.items` array e `length == totalCount`; truncamento ou JSON inválido ou exit != 0 produz `BOARD_STATE=failed`
- [ ] 1.3 Validar listagem de PRs: JSON válido, `headRefName` presente; atingir o limite configurado (1.000) ou falhar produz `PRS_STATE=failed`
- [ ] 1.4 Invocar os loaders uma única vez no início dos modos `post`/`audit` (antes de qualquer consumidor) e nunca dentro de subshell
- [ ] 1.5 Em falha de snapshot, consultar `gh api rate_limit` (REST) e incluir `graphql.remaining` e `reset` na mensagem quando disponíveis; sem retry loop
- [ ] 1.6 Corrigir a paginação de idade: contar a página inicial no limite total (máx. 19 requisições: 1 inicial + 18 adicionais)

## 2. Consumidores migrados para o snapshot único

- [ ] 2.1 Migrar o check de títulos board/issue (audit) para ler `BOARD_JSON` sem nova chamada
- [ ] 2.2 Migrar o check de changes OpenSpec terminais (post/audit) para ler `BOARD_JSON`
- [ ] 2.3 Migrar `card_is_terminal` para lookup local tri-state (`terminal`/`non-terminal`/`unknown`) a partir do snapshot, removendo `gh project item-list` por branch
- [ ] 2.4 Substituir `gh pr list --head` por branch por lookup na fotografia global de PRs; falha nunca vira `pr_open=no` (vira `unknown`)
- [ ] 2.5 Migrar o check de campos do pacote (post/audit) para ler `BOARD_JSON`
- [ ] 2.6 Migrar o check de evidência de homologação (post/audit) para ler `BOARD_JSON`
- [ ] 2.7 Em `post`, `BOARD_STATE=failed`/`PRS_STATE=failed`/qualquer `unknown` dependente registra blocker; em `audit`, warning explícito

## 3. Normalização e validação do pacote

- [ ] 3.1 Normalizar `RELEASE_CARDS` uma única vez: trim, remoção de zeros à esquerda, dedupe e validação numérica (1..2147483647); formato inválido bloqueia em `post` antes de consultas
- [ ] 3.2 Validar que cada ID normalizado aparece exatamente uma vez no snapshot do Project e possui Status; ausente/duplicado/sem Status é blocker em `post`
- [ ] 3.3 Reutilizar o mesmo snapshot para campos obrigatórios e evidência de homologação sem consultas duplicadas

## 4. Testes (fake gh com contador)

- [ ] 4.1 Estender o fake `gh` com contadores de chamadas (`item-list`, `pr list`, REST comments)
- [ ] 4.2 Múltiplas branches + checks ativos produzem exatamente 1 `item-list` e 1 `pr list`
- [ ] 4.3 Segunda execução refaz os downloads (sem cache persistente)
- [ ] 4.4 JSON válido com exit != 0 e truncamento (`items.length < totalCount`) produzem snapshot `failed`
- [ ] 4.5 Card ausente, duplicado ou sem Status em `RELEASE_CARDS` bloqueia `post`
- [ ] 4.6 PR truncada ou JSON inválido produz `failed` (nunca `pr_open=no`)
- [ ] 4.7 Mesma falha: blocker em `post`, warning em `audit`; incluir caso sem consumidores relevantes ativos (falha global imediata)
- [ ] 4.8 Paginação de idade respeita o limite total de 19 requisições
- [ ] 4.9 Normalização de `RELEASE_CARDS`: trim, zeros à esquerda, dedupe (`480,0480`), intervalo e token inválido (sem consulta remota)

## 5. Validação e fechamento

- [ ] 5.1 Rodar `openspec validate --change card-509-release-guard-graphql-budget`
- [ ] 5.2 Rodar `backend/tests/integration/test_release_guard.py` com os novos cenários
- [ ] 5.3 Após reset da cota, medir delta `graphql.used` de uma execução real de `audit` (esperado: ~202 + idade, sem multiplicidade por branch)
- [ ] 5.4 Registrar evidências de review, QA e runtime no fechamento do card
