## MODIFIED Requirements

### Requirement: Diagnóstico de rate limit ocorre somente após falha
Após uma ou mais falhas de snapshot, o release guard SHALL imprimir remaining e reset dos **cabeçalhos GraphQL** da resposta da fotografia que falhou, no máximo uma vez por execução (Q2=A). O loader da fotografia MUST capturar esses cabeçalhos na mesma chamada GraphQL (`item-list` / equivalente `gh api graphql --include`). MUST NOT consultar o endpoint REST `GET /rate_limit` nem imprimir `.resources.graphql.remaining` do contador REST. MUST NOT abrir uma segunda query GraphQL só para ler cota. MUST NOT reabrir a fotografia completa do board além da uma por execução (#509). O diagnóstico MUST preservar a causa original. O guard MUST NOT imprimir esse diagnóstico preventivamente e MUST NOT executar retry, polling ou espera automática.

#### Scenario: Snapshot falha com diagnóstico disponível
- **WHEN** uma carga de snapshot GraphQL falha e os cabeçalhos dessa resposta informam remaining e reset
- **THEN** a mensagem inclui esses valores (não o contador REST) e preserva a falha original conforme o modo

#### Scenario: REST remaining 5000 is not printed as GraphQL quota
- **WHEN** uma fotografia GraphQL falha com cabeçalhos remaining=0 e o REST `GET /rate_limit` reportaria `resources.graphql.remaining=5000`
- **THEN** o diagnóstico imprime remaining=0 e o reset GraphQL
- **AND** o guard faz zero chamadas `GET /rate_limit` para este diagnóstico

#### Scenario: Snapshot é carregado com sucesso
- **WHEN** os snapshots são válidos
- **THEN** o guard não imprime diagnóstico de cota GraphQL preventivamente

#### Scenario: Ambos os snapshots falham
- **WHEN** Project e PRs falham na mesma execução
- **THEN** o guard imprime o diagnóstico de cabeçalhos GraphQL no máximo uma vez e preserva as falhas originais
