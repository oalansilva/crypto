## 1. Preparar snapshots e orçamento remoto

- [ ] 1.1 Adicionar loaders de Project e PRs invocados como statements no shell principal, preenchendo `BOARD_JSON`/`BOARD_STATE` e `PRS_JSON`/`PRS_STATE`; permitir `$(gh ...)` dentro do loader, mas nunca invocar o loader em `$(...)` [D1]
- [ ] 1.2 Carregar os dois snapshots uma vez no início de `post|audit` e manter `pre` sem `item-list`, `pr list` ou inventário de idade [D1, D3, D7]
- [ ] 1.3 Validar exit code, JSON, `.items` array, `totalCount` presente como inteiro não negativo e igualdade exata; ausência, malformação ou mismatch para menos/mais define `BOARD_STATE=failed` [D1]
- [ ] 1.4 Buscar PRs com `number,headRefName,headRepositoryOwner` e exigir array de topo com `headRefName` e `headRepositoryOwner.login` não vazios em cada item; objeto, entrada malformada ou 1.000 itens define `PRS_STATE=failed` [D1]
- [ ] 1.5 Consultar REST `rate_limit` apenas após falha, no máximo uma vez por execução, incluindo `graphql.remaining/reset` sem substituir a causa original e sem retry ou polling [D5]
- [ ] 1.6 Corrigir a paginação de idade para no máximo 19 requisições totais, contando a página inicial, e emitir warning parcial/truncado se `hasNextPage` permanecer verdadeiro [D6, D7]

## 2. Migrar decisões para lookups locais fail-closed

- [ ] 2.1 Implementar lookup local de card pela chave `(repository=oalansilva/crypto, issue number canônico)` com resultado `terminal|non-terminal|unknown`, rejeitando outro repositório e incluindo chave ausente/duplicada e Status ausente [D2, D4]
- [ ] 2.2 Migrar `card_is_terminal()` e inventário de branches para o lookup local, removendo `item-list` por branch [D1, D2]
- [ ] 2.3 Indexar PRs por `(headRepositoryOwner.login, headRefName)` e substituir `gh pr list --head` por lookup local de `(oalansilva, branch)`; fork homônimo não corresponde e snapshot falho nunca produz `pr_open=no` [D1, D2]
- [ ] 2.4 Migrar checks de título, changes terminais, campos e homologação para `BOARD_JSON`, sem novas listagens [D1, D4]
- [ ] 2.5 Reportar qualquer snapshot `failed` imediatamente e globalmente: blocker em `post`, warning em `audit`, mesmo sem consumidor relevante [D3]

## 3. Canonicalizar o pacote de release

- [ ] 3.1 Normalizar `RELEASE_CARDS` uma vez por trim, remoção de zeros à esquerda e dedupe, validando inteiros entre 1 e 2147483647 [D4]
- [ ] 3.2 Em `post`, bloquear token inválido antes de qualquer chamada remota; em `audit`, emitir warning, pular chamadas dependentes do pacote e continuar checks independentes [D4]
- [ ] 3.3 Exigir exatamente um item com Status pela tupla `(repository=oalansilva/crypto, ID canônico)`, rejeitar correspondência de outro repositório e reutilizar o item qualificado nos checks de campos e homologação [D4]
- [ ] 3.4 Preservar “not applicable” para Status conhecido diferente de `Homologado|Pronto`, sem ampliar política de elegibilidade [D8]

## 4. Cobrir comportamento com fake gh e contadores

- [ ] 4.1 Estender o fake `gh` com log externo process-safe para contar, inclusive entre subprocessos, `item-list`, `pr list`, páginas de idade, rate limit e comments REST [D1, D5, D7]
- [ ] 4.2 Provar que múltiplas branches e checks executam exatamente um `item-list` e um `pr list`; provar que um segundo run refaz ambos [D1]
- [ ] 4.3 Provar que JSON válido com exit code não zero, JSON inválido, `totalCount` ausente/malformado/negativo e mismatch de tamanho para menos ou para mais falham [D1]
- [ ] 4.4 Provar pelo log externo que JSON de PRs não-array (incluindo `{}`), item sem `headRefName`, item sem `headRepositoryOwner.login`, JSON inválido ou 1.000 itens define `PRS_STATE=failed` e nunca resulta em `pr_open=no` [D1, D2]
- [ ] 4.5 Provar card ausente, duplicado, sem Status ou com mesmo número apenas em outro repositório como blocker/`unknown` de `post` e warning de `audit` [D2, D4]
- [ ] 4.6 Provar a mesma falha como blocker em `post` e warning em `audit`, inclusive sem consumidores relevantes [D3]
- [ ] 4.7 Provar trim, zeros, dedupe de `480,0480`, limites numéricos e token inválido: `post` sem qualquer chamada remota; `audit` sem chamadas dependentes do pacote e com checks independentes ativos [D4]
- [ ] 4.8 Provar o teto total de 19 páginas de idade, warning quando `hasNextPage=true` após a 19ª, ausência da 20ª requisição e a matriz de `pre|post|audit` [D6, D7]
- [ ] 4.9 Provar que comments REST por card permanecem permitidos sem alterar contadores GraphQL [D7]
- [ ] 4.10 Provar zero chamadas de rate limit no caminho de sucesso, no máximo uma quando ambos os snapshots falham e preservação da causa original [D5]
- [ ] 4.11 Provar que PR de outro `headRepositoryOwner.login` com o mesmo `headRefName` resulta em `pr_open=no` para a chave alvo, enquanto `(oalansilva, headRefName)` resulta em `pr_open=yes` [D2]

## 5. Validar e registrar evidências

- [ ] 5.1 Rodar a validação OpenSpec da change e corrigir inconsistências entre proposal, design, spec e tasks
- [ ] 5.2 Rodar os testes focados de `backend/tests/integration/test_release_guard.py`
- [ ] 5.3 Após reset da cota e autorização de implementação, medir uma execução real de `audit` e registrar o delta GraphQL de uma listagem do Project, uma listagem global de PRs e das páginas de idade, sem multiplicidade por branch [D7]
- [ ] 5.4 Registrar review, QA, orçamento observado e runtime no handoff do card
