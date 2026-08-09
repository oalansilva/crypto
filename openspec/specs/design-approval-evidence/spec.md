# design approval evidence Specification

## Purpose
TBD - created by syncing change card-421-design-approval-evidence.
## Requirements

### Requirement: Evidência de aprovação de Design antes de implementação
Nenhum código SHALL ser aplicado sem evidência registrada de aprovação de Design, inclusive em cards `UI impact: none`, remoções e tooling. A evidência é o comentário de Alan no card ou o arraste `Aprovação de Design -> Pronto para Dev` no board.

#### Scenario: Card sem evidência de aprovação
- **WHEN** um card está sem comentário de Alan nem arraste de aprovação de Design no board
- **THEN** nenhum código é aplicado e o card permanece bloqueado até a evidência ser registrada

#### Scenario: UI impact none
- **WHEN** um card declara `UI impact: none`
- **THEN** a exigência de evidência de aprovação permanece válida sem redução de gate

### Requirement: Resolução registrada de veredito BLOCKED
Quando o veredito do design for `BLOCKED`, o `design.md` SHALL registrar a resolução antes de mover para `Pronto para Dev`/implementação: o que bloqueou, como foi resolvido e quem aprovou.

#### Scenario: BLOCKED sem resolução
- **WHEN** o `design.md` registra `Design Agent verdict: BLOCKED` sem seção de resolução
- **THEN** o card não avança para `Pronto para Dev` nem para implementação

#### Scenario: BLOCKED com resolução registrada
- **WHEN** o `design.md` registra a resolução do bloqueio (causa, correção, aprovador)
- **THEN** o card pode avançar para `Pronto para Dev` desde que a evidência de aprovação de Alan exista

### Requirement: Checklist de gates no PR/commit de integração
O PR/commit de integração SHALL listar `design.md`/verdict e a evidência de aprovação de Design, mesmo para mudanças de tooling, validado em `/opsx:verify`.

#### Scenario: PR de integração sem checklist de gates
- **WHEN** um PR/commit de integração não lista o `design.md`/verdict e a evidência de aprovação
- **THEN** `/opsx:verify` falha e a integração é bloqueada

#### Scenario: PR com checklist completo
- **WHEN** um PR/commit de integração lista `design.md`, verdict e evidência de aprovação
- **THEN** `/opsx:verify` valida o gate e a integração pode prosseguir
