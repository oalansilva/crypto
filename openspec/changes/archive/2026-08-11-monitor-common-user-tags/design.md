## Context

A tabela do Monitor já usa `showTechnicalColumns` para diferenciar admin de usuário comum. A limpeza das tags deve seguir a mesma lógica para não remover contexto operacional de admin.

## Goals / Non-Goals

**Goals:**
- Deixar a tag de carteira compreensível em português.
- Reduzir ruído da tag `Strategy` para usuário comum.
- Manter estrelas como classificação principal da estratégia.

**Non-Goals:**
- Não alterar favoritos, preferências ou persistência de carteira.
- Não mudar labels internos de modo `Price/Strategy` no card expandido.
- Não alterar dados retornados pela API.

## Decisions

- Renderizar `Carteira` para todos os usuários.
  - Racional: é mais claro que `Portfolio` no produto em português.
- Renderizar `Strategy` somente para admin.
  - Racional: usuário comum já entende a linha como estratégia/sinal e ganha mais com menos tags.

## Risks / Trade-offs

- [Risk] Algum teste procurar o texto `Portfolio` na linha.
  - Mitigation: atualizar cobertura E2E para a nova copy.
