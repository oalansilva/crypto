## REMOVED Requirements

### Requirement: General alert scans use curated Monitor catalog
**Reason**: Card #1122 (decisões de Alan de 26/10 e 27/10/2026): cada usuário recebe alertas das estratégias próprias que acompanha no Monitor (com estrela e alerta ligado); o catálogo curado do admin deixa de ser a origem dos alertas, inclusive na cripto, e não alerta ninguém.
**Migration**: A varredura passa a seguir `favorite-telegram-alerts` ("Alertas saem das estratégias que cada usuário acompanha no Monitor"). Quem recebia só pelo catálogo segue "Transição de quem recebia pelo catálogo".

### Requirement: General alert scans remain intentionally scoped
**Reason**: O escopo por catálogo sai junto com a origem por catálogo.
**Migration**: O escopo é o que a pessoa acompanha no Monitor: favorito próprio com estrela e alerta ligado. O filtro de estrelas do sistema deixa de mudar quem recebe (`favorite-telegram-alerts`).

### Requirement: General scanner preserves daily curated scope
**Reason**: A fonte deixa de ser o catálogo curado.
**Migration**: A cadência diária (timer das 08:05 BRT) continua fora do código e sem mudança (`monitor-telegram-alerts`); a fonte é a de `favorite-telegram-alerts`.
