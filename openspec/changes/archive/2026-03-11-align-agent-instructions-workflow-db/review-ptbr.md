# Revisão PT-BR — align-agent-instructions-workflow-db

## Objetivo
Atualizar as instruções/prompts dos agentes para que todos passem a operar corretamente no novo modelo:
- **workflow DB** como fonte operacional
- **Kanban** como lugar principal de consulta/handoff
- **OpenSpec** como artefato/documentação

## O que precisa refletir nas instruções
- work items tipados: `change`, `story`, `bug`
- bug filho bloqueia fechamento da story
- múltiplas stories/agentes podem trabalhar em paralelo
- locks/dependências/WIP continuam valendo
- comentários do Kanban como canal padrão entre agentes

## Arquivos-alvo
- `crypto/AGENTS.md`
- memória/instruções globais que ainda apontem para o modelo antigo
- eventuais arquivos específicos de agentes
