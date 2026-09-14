## MODIFIED Requirements

### Requirement: Closeout requires explicit main to develop sync after release-* merge
Após merge do PR `release-* → main` que carrega o archive (e demais paths de closeout do pacote), o runbook SHALL tornar **obrigatório e explícito** o sync `main → develop` no closeout desse caminho, de forma que `origin/main` fique ancestral de `origin/develop` (produção contida na develop) antes do `scripts/release-guard post` final e da promoção dos cards a `Pronto`. Extra na develop SHALL ser aviso, não blocker. Árvores idênticas MUST NOT ser exigidas. O sync MUST ser **um** PR de merge normal `main → develop`. O runbook MUST recusar: PR que substitui a ponta de develop pela árvore de produção; merge que descarta o lado da develop; apagar o Done da ponta e devolvê-lo depois. Se o primeiro `post` falhar porque develop não contém produção, o runbook SHALL orientar completar o merge normal e reexecutar `post`. Overlay passo 5b SHALL usar este predicado (containment + extra = aviso), não árvores idênticas.

#### Scenario: Post sees develop containing production after one merge-normal PR
- **WHEN** o lote entrou em `main` via `release-*` e ainda não está em `origin/develop`
- **THEN** o closeout documenta um único PR merge normal `main → develop` como passo obrigatório
- **AND** após esse merge, `release-guard post` valida alinhamento com produção contida na develop
- **AND** extra na develop é aviso, não blocker

#### Scenario: First post fails before sync
- **WHEN** o operador roda `scripts/release-guard post` após o merge em `main` mas antes do sync `main → develop`
- **AND** `origin/main` não é ancestral de `origin/develop`
- **THEN** o `post` falha (develop não contém produção)
- **AND** o runbook orienta completar o merge normal `main → develop` e reexecutar `post`

#### Scenario: Three-PR dance and replace-develop are refused
- **WHEN** o closeout documenta o sync pós-produção
- **THEN** o runbook recusa substituir a develop pela ponta de produção, merge que descarta o outro lado, e restore do Done
- **AND** o padrão de um merge normal (ensaio: #924) é o aceite
- **AND** o padrão #926 e a sequência #913+#914+#915 MUST NOT ser o aceite
