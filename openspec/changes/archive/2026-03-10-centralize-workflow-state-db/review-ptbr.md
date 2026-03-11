# Revisão PT-BR — centralize-workflow-state-db

## Problema
Hoje o estado do fluxo está espalhado em vários lugares:
- OpenSpec
- `docs/coordination`
- Kanban
- comentários / handoffs

Isso gera drift, reconciliação manual e confusão para humanos e agentes.

## Proposta
Criar um **banco de dados Postgres self-hosted na VPS** para virar a **fonte operacional de verdade** do workflow.

## O que fica no banco
- changes
- work items (ex.: `story` / `bug`)
- relações pai-filho entre itens
- tasks
- comments
- approvals
- handoffs
- artifacts
- histórico de status

## O que continua em arquivo
OpenSpec continua existindo como camada de documentação:
- proposal
- design
- specs
- tasks

## Direção sugerida
- Postgres = estado operacional
- suporte a **múltiplos projetos** desde o início
- OpenSpec = artefato/documentação
- Kanban passa a ler do banco
- `docs/coordination/*.md` sai do caminho operacional
- As changes ativas atuais deverão ser migradas para o novo modelo depois que o DEV implementar a base

## Regras adicionais importantes
- uma **story/proposta só pode ser finalizada quando todos os bugs filhos estiverem finalizados**
- os bugs filhos viram **pré-requisitos** para encerrar a story
- o sistema deve suportar **múltiplas stories ativas em paralelo**
- agentes também devem poder trabalhar **em paralelo**, com travas/dependências para evitar conflito

## Direção de uso
- a ideia é que **você consulte o fluxo principalmente pelo Kanban**, usando menos o chat
- os **agentes também devem se coordenar pelos comentários do card**, inclusive citando uns aos outros

## Pré-requisitos explícitos nesta change
- instalar e configurar o **Postgres** na VPS
- definir credenciais/segredos e persistência
- validar conectividade do app antes da camada de workflow

## Benefícios esperados
- menos inconsistência
- menos reconciliação manual
- agentes encontrando estado mais facilmente
- Kanban mais confiável
- menos custo cognitivo / mais automação
