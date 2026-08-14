## ADDED Requirements

### Requirement: Validação de evidência de homologação no pacote
O `release-guard` SHALL validar, em `audit` e `post`, a presença do comentário canônico `Homologado por Alan na develop.` nos cards `Homologado` ou `Pronto` informados explicitamente em `RELEASE_CARDS`.

#### Scenario: Audit encontra comentário ausente
- **WHEN** `release-guard audit` recebe `RELEASE_CARDS` com um card `Homologado` ou `Pronto` sem o comentário canônico
- **THEN** o guard emite warning identificando o card e termina sem blocker por esse achado

#### Scenario: Post encontra comentário ausente
- **WHEN** `release-guard post` recebe `RELEASE_CARDS` com um card `Homologado` ou `Pronto` sem o comentário canônico
- **THEN** o guard emite blocker identificando o card e termina com falha

#### Scenario: Consulta de comentário indisponível
- **WHEN** `RELEASE_CARDS` está definido e a consulta ao GitHub, paginação ou parsing JSON de um card não pode ser concluída
- **THEN** o guard falha fechado conforme o modo: warning em `audit` e blocker em `post`

#### Scenario: Pacote com evidência completa
- **WHEN** todos os cards `Homologado` ou `Pronto` de `RELEASE_CARDS` têm ao menos um comentário contendo o marcador canônico por comparação fixa case-insensitive
- **THEN** a validação de evidência de homologação passa

#### Scenario: RELEASE_CARDS ausente
- **WHEN** `release-guard audit` ou `release-guard post` roda sem `RELEASE_CARDS`
- **THEN** o guard informa que a validação de comentários do pacote foi pulada e não varre todo o histórico do board

#### Scenario: Identificador inválido ou duplicado
- **WHEN** `RELEASE_CARDS` contém valor não numérico ou o mesmo card mais de uma vez
- **THEN** valores inválidos são reportados conforme a severidade do modo e duplicatas válidas são consultadas uma única vez
