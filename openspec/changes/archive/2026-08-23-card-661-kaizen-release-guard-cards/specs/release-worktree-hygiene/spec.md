# release-worktree-hygiene Delta Specification

## MODIFIED Requirements

### Requirement: Evidência kaizen da release bloqueia o post

Antes de concluir o `post`, o release guard MUST exigir que `docs/kaizen-log.md` esteja versionado e contenha um heading de nível 2 iniciado pela data canônica da release e identificado como auditoria de release por `Kaizen release` ou `/kaizen release`. Além do heading, o `post` MUST validar a materialização Kaizen descrita na spec `kaizen-continuous-improvement` (tabela cujo `###` começa com `Cards kaizen criados`: 1–3 issues novas sem linhas inválidas, ou dedupe `coberto por` com todos os `#N` em fluxo, ou marcador `Sem achados acionáveis` sem linhas de dados). Se houver dedupe e o snapshot do Project 1 estiver indisponível, o `post` MUST falhar fechado. Ausência do heading ou falha da materialização MUST ser blocker em `post`. O `post` bem-sucedido SHALL ocorrer antes de mover os cards do pacote para `Pronto`.

#### Scenario: Não existe entrada kaizen da data
- **WHEN** o log não contém heading canônico da data da release
- **THEN** o `post` falha com blocker de evidência kaizen

#### Scenario: Heading existe sem marcador de release
- **WHEN** o log contém um heading da data, mas ele não identifica `Kaizen release` nem `/kaizen release`
- **THEN** o `post` falha com blocker de evidência kaizen

#### Scenario: Heading e materialização válidos
- **WHEN** o log contém o heading canônico da data e a materialização Kaizen (cards, dedupe em fluxo ou sem achados acionáveis) passa
- **THEN** o gate de evidência kaizen passa

#### Scenario: Heading presente mas materialização inválida
- **WHEN** o heading canônico existe e a materialização falha (tabela ausente/vazia sem marcador, linha inválida, dedupe terminal/ausente, >3 cards, ou board down com dedupe)
- **THEN** o `post` falha com blocker de materialização Kaizen

#### Scenario: Board snapshot down com dedupe
- **WHEN** a materialização depende de checar cobertura de dedupe e o snapshot do Project 1 falhou ou está incompleto
- **THEN** o `post` falha fail-closed
