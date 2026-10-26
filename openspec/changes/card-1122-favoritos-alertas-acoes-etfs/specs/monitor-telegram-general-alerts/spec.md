## REMOVED Requirements

### Requirement: General alert scans use curated Monitor catalog
**Reason**: Card #1122 (decisão de Alan, 26/10/2026): cada usuário recebe alertas dos próprios favoritos marcados "Alertar"; o catálogo curado do admin deixa de ser a origem dos alertas, inclusive na cripto.
**Migration**: A varredura passa a seguir `favorite-telegram-alerts` ("Alertas saem dos favoritos de cada usuário"). Quem recebia só pelo catálogo segue a transição decidida por Alan no Design.

### Requirement: General alert scans remain intentionally scoped
**Reason**: O escopo por catálogo sai junto com a origem por catálogo.
**Migration**: O filtro de estrelas do sistema continua valendo sobre o nível do próprio favorito (`favorite-telegram-alerts`); o dono escolhe o escopo com "Alertar".

### Requirement: General scanner preserves daily curated scope
**Reason**: A fonte deixa de ser o catálogo curado.
**Migration**: A cadência diária (timer das 08:05 BRT) continua fora do código e sem mudança (`monitor-telegram-alerts`); a fonte é a de `favorite-telegram-alerts`.
