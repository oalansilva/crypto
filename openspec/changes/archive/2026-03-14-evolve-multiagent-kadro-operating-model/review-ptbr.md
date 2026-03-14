# Revisão PT-BR — evolve-multiagent-kadro-operating-model

## Resumo
Esta change **não troca** o Kadro e **não troca** os agentes atuais.

Ela propõe melhorar **como o time trabalha** em cima da estrutura que já existe.

Hoje o problema principal não é falta de arquitetura. O problema principal é operação:
- handoff ainda inconsistente
- drift entre runtime / Kanban / OpenSpec / espelhos legacy
- reconciliação manual demais
- pouca disciplina explícita no fechamento de cada stage

## O que a change propõe
A proposta foi organizada em **2 fases**.

### Fase 1 — padronizar a operação
Objetivo: deixar o trabalho mais claro sem mexer pesado no motor.

Inclui:
- responsabilidades formais por agente (`main`, `PO`, `DESIGN`, `DEV`, `QA`)
- handoff padrão no Kanban
- Definition of Done por coluna
- regra de que um stage só fecha com **runtime + handoff**
- `docs/coordination/*.md` como espelho/auditoria, não operação viva

### Fase 2 — endurecer a execução
Objetivo: depois que o processo estiver claro, melhorar o motor.

Inclui:
- alinhar instruções dos agentes com o playbook
- disciplinar melhor `change`, `story`, `bug`, locks, dependências e ownership
- melhorar homologation/archive
- reduzir drift entre runtime, OpenSpec e metadados

## Por que isso ajuda
- mantém o quadro atual
- mantém o time atual
- reduz bagunça operacional
- melhora previsibilidade
- prepara o modelo para crescer sem reinventar tudo

## O que a change não faz
- não cria uma arquitetura nova do zero
- não adiciona um monte de agentes novos
- não troca Kadro por outra ferramenta
- não tenta automatizar tudo logo na primeira fase

## Leitura executiva
A lógica da change é:

**primeiro padronizar o trabalho, depois endurecer a execução**.

Esse é o menor caminho para melhorar sem complicar demais.
