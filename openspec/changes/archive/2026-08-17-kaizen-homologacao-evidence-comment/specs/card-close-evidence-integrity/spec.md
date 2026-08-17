## ADDED Requirements

### Requirement: Recuperação retroativa idempotente da evidência de homologação
O helper `scripts/post-card-evidence-comment.sh` SHALL permitir registrar retroativamente a transição `homologado` somente após validar argumentos, consultar comentários existentes e aplicar dedupe pelo marcador canônico da transição.

#### Scenario: Dry-run de homologação retroativa
- **WHEN** o operador executa `--transition homologado --dry-run` com card e commit válidos e sem comentário existente
- **THEN** o helper mostra o corpo canônico pretendido, incluindo `Homologado por Alan na develop.`, e não publica comentário

#### Scenario: Comentário canônico já existe
- **WHEN** o card já contém comentário com o marcador `Homologado por Alan na develop.`
- **THEN** o helper reporta dedupe e não publica outro comentário, mesmo que o comentário existente não contenha referência reconhecível de commit

#### Scenario: Falha ao consultar comentários
- **WHEN** o helper não consegue listar ou interpretar os comentários existentes do card
- **THEN** ele termina com erro e MUST NOT publicar comentário

#### Scenario: Post retroativo após dry-run
- **WHEN** a homologação humana preexistente foi confirmada, o dry-run foi revisado e não há duplicata
- **THEN** a execução sem `--dry-run` publica exatamente um comentário canônico de homologação

#### Scenario: Saneamento da release 2026-08-11
- **WHEN** os cards 456, 457, 458, 463 e 464 são processados individualmente após confirmação da homologação por Alan
- **THEN** cada card termina com exatamente um comentário canônico de homologação e o pacote passa na validação correspondente do guard
