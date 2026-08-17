# card evidence comments Specification

## Purpose
Garantir 1 comentário de evidência por transição de card (Done/Homologado/Pronto), sem duplicação em fechamento em lote.

## ADDED Requirements

### Requirement: Dedupe de comentário de evidência por transição
O fluxo de fechamento de card SHALL postar no máximo 1 comentário de evidência por transição (Done/Homologado/Pronto) por card, identificado pela combinação de transição + commit ref.

#### Scenario: Mesmo commit ref já comentado
- **WHEN** um comentário de evidência para a mesma transição e mesmo commit ref já existe no card
- **THEN** nenhum comentário duplicado é postado e o helper reporta o comentário existente

#### Scenario: Transição diferente ou commit ref diferente
- **WHEN** a transição ou o commit ref é diferente de um comentário já existente
- **THEN** um novo comentário de evidência é postado com o formato canônico

#### Scenario: Formato de referência diverge (URL vs PR N (sha))
- **WHEN** um comentário existente referencia o mesmo commit com formato diferente (ex.: URL vs "PR N (sha)")
- **THEN** o helper normaliza a referência (extração do SHA) e não duplica o comentário

### Requirement: Formato canônico de comentário de evidência
O helper SHALL usar os templates exatos de `AGENTS.md` (Implementação concluída / Homologado por Alan / Publicado em main) para as transições Done, Homologado e Pronto.

#### Scenario: Postagem via helper
- **WHEN** um comentário de evidência é postado via helper
- **THEN** o texto segue o template canônico da transição correspondente no `AGENTS.md`
