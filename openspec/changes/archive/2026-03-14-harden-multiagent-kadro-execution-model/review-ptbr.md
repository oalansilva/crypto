# Revisão PT-BR — harden-multiagent-kadro-execution-model

## Resumo
Esta change cobre **só a fase 2**.

Ela assume que a fase 1 já foi concluída e que o time já tem:
- responsabilidades claras
- handoff padrão
- Definition of Done por coluna
- regra de stage = runtime + handoff

## O que entra
- alinhar instruções dos agentes ao novo playbook
- disciplinar melhor `change`, `story`, `bug`, locks, dependências e ownership
- melhorar homologation/archive
- reduzir drift runtime ↔ OpenSpec ↔ metadados

## O que não entra
- redefinir a estrutura atual do time
- trocar Kadro
- recriar a fase 1

## Leitura executiva
Esta é a change para **endurecer a execução** depois que a operação já estiver padronizada.
