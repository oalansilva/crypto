## MODIFIED Requirements

### Requirement: Runbook documents release-* archive when develop push is protected
O runbook on-demand de release (`overlay_doc`, Cripto: `docs/crypto-overlay.md`, e a skill `covenant-flow` no consumidor pinado) SHALL documentar o caminho de closeout via branch `release-*` quando o push para `refs/heads/develop` é recusado por branch protection (incluindo required check `qa-gate`), **mesmo** quando `origin/develop` contém somente conteúdo Homologado do pacote. O stub always-on `AGENTS.md` MUST NOT carregar o playbook completo; MUST continuar apontando o overlay on-demand (`overlay_doc`) para tarefas de release. O caminho feliz `develop → main` MUST permanecer documentado para o caso em que o push do archive em `develop` é aceito.

#### Scenario: Protected develop blocks archive push with Homologado-only content
- **WHEN** o operador tenta publicar o archive OpenSpec do lote em `develop` e o remoto recusa com proteção que exige `qa-gate` (ou equivalente)
- **AND** `origin/develop` contém somente conteúdo Homologado do pacote
- **THEN** o runbook instrui criar/usar `release-*` com o archive, abrir PR para `main`, e NÃO exige bypass administrativo da proteção de `develop`

#### Scenario: Happy path develop to main still documented
- **WHEN** o push do archive para `develop` é aceito pela proteção
- **THEN** o runbook ainda documenta PR `develop → main` como caminho feliz
- **AND** `release-*` permanece o fallback sob proteção ou conteúdo não homologado

#### Scenario: Always-on stub stays thin
- **WHEN** um agente lê apenas `AGENTS.md` sem overlay
- **THEN** não encontra o playbook completo de `release-guard`/lote/PROD
- **AND** encontra indicação de carregar o path `overlay_doc` (Cripto: `docs/crypto-overlay.md`) para release
