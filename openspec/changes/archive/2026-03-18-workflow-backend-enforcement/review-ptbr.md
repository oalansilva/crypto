# Review PT-BR: Workflow Backend Enforcement

## Resumo

Implementar validações automáticas no backend para evitar erros de workflow.

## O que muda

- **Validação de aprovação**: API rejeita aprovação se links de review estiverem faltando
- **Story-Bug**: Story não pode fechar se tiver bug aberto
- **Comentário obrigatório**: Exige status, evidence e next_step ao mudar de stage
- **Verificação de sync**: Endpoint para checar se DB e OpenSpec estão sincronizados
- **Auto-update no homologation**: DB atualiza automaticamente quando Alan aprova

## Por que isso importa

Hoje as regras estão em arquivos markdown e dependem de humano seguir. Com validação no backend, erros são bloqueados automaticamente.

## Tasks

8 grupos de tasks (24 itens total)

## Próximo passo

Implementar as tasks via Codex CLI.
