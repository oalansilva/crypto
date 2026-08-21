## ADDED Requirements

### Requirement: Pre on release-* does not require archive on origin/develop
Quando a branch corrente corresponde a `release-*`, `scripts/release-guard pre` SHALL permitir PASS sem exigir que o archive OpenSpec do pacote (nem a remoção da change ativa correspondente) já esteja presente em `origin/develop`. O `pre` MUST NOT emitir blocker cujo remédio prescrito seja publicar o archive em `origin/develop` antes de abrir o PR `release-* → main`. O guard permanece read-only. Comportamentos existentes que suportam este caminho (diff `origin/main...HEAD` para classificação code/documental em `release-*`; exclusão da branch corrente `release-*` do inventário de branches locais não mergeadas no `pre`) MUST ser preservados. Lacunas sobre a ref local `develop` com archive ainda não publicado em `origin/develop` pertencem ao card #618 e MUST NOT ser “consertadas” expandindo este requisito além do aceite do #617.

#### Scenario: Pre passes with archive only on release-* HEAD
- **WHEN** `scripts/release-guard pre` roda com `current_branch` matching `release-*`
- **AND** o HEAD da `release-*` contém o archive OpenSpec do pacote
- **AND** `origin/develop` ainda não contém esse archive
- **THEN** o `pre` NÃO falha por ausência do archive em `origin/develop`
- **AND** o comando pode atingir PASS quanto a essa condição (outros blockers legítimos de higiene permanecem)

#### Scenario: Pre does not prescribe push archive to develop first
- **WHEN** o archive existe apenas na tip da `release-*` usada pelo lote
- **THEN** a saída do `pre` MUST NOT instruir o operador a fazer push do archive para `origin/develop` como pré-condição do PR de release

#### Scenario: Existing release-* pre behaviors remain
- **WHEN** `pre` classifica o unpublished diff com branch corrente `release-*`
- **THEN** o diff usado é `origin/main...HEAD` (não `origin/main...origin/develop`)
- **AND** a seção de branches locais do `pre` não trata a própria `release-*` corrente como branch local não mergeada bloqueante
