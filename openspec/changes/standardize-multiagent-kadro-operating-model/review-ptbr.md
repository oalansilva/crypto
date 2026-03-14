# Revisão PT-BR — standardize-multiagent-kadro-operating-model

## Resumo
Esta change cobre **só a fase 1**.

Ela não mexe no motor profundo do sistema. Ela arruma **como o time trabalha** em cima da estrutura atual.

## O que entra
- responsabilidades formais por agente
- handoff padrão no Kanban
- Definition of Done por coluna
- regra de que um stage só fecha com runtime + handoff
- `docs/coordination/*.md` como espelho/auditoria
- playbook operacional consolidado

## O que não entra
- endurecimento do motor de execução
- ajuste profundo de ownership/locks/dependencies
- archive/homologation hardening
- redução estrutural de drift por automação mais forte

## Leitura executiva
Esta é a change para **padronizar a operação** antes da próxima change, que vai endurecer a execução.
