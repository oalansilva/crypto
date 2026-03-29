# Projeto Formal — Evolução da Operação Multiagente no Kadro

## 1. Título
**Evolução da Operação Multiagente no Kadro, preservando os agentes atuais e o fluxo Kanban existente**

---

## 2. Objetivo
Estruturar uma evolução operacional do ambiente atual do projeto `crypto` para tornar o trabalho com agentes mais previsível, auditável, escalável e robusto **sem substituir**:

- o **Kadro/Kanban** atual
- os agentes já criados (**main, PO, DESIGN, DEV, QA**)
- o modelo atual de **workflow DB como fonte operacional**
- o uso de **OpenSpec como camada de artefatos**

A proposta visa melhorar a forma de trabalho, reduzir drift entre camadas, padronizar handoffs e consolidar o fluxo multiagente sobre a arquitetura que já existe.

---

## 3. Escopo

### 3.1 Dentro do escopo
- Revisar a operação atual dos agentes existentes.
- Revisar o fluxo atual do Kadro/Kanban.
- Propor ajustes operacionais e estruturais sem trocar a base do sistema.
- Formalizar responsabilidades por agente.
- Formalizar Definition of Done por etapa do fluxo.
- Padronizar handoffs/comentários no Kanban.
- Reduzir reconciliações manuais entre runtime/Kanban/OpenSpec.
- Melhorar o uso de `change`, `story`, `bug`, locks e dependências.
- Consolidar um modelo operacional mais disciplinado para execução multiagente.

### 3.2 Fora do escopo
- Substituir o Kadro por outra ferramenta.
- Criar uma nova arquitetura radical de agentes.
- Introduzir uma malha complexa de novos agentes persistentes.
- Reescrever todo o fluxo do projeto `crypto`.
- Trocar OpenSpec ou workflow DB por outro sistema.
- Adotar plugin próprio, webhooks complexos ou automação pesada como primeira etapa.

---

## 4. Estado atual avaliado

### 4.1 Agentes existentes
O ambiente já possui os agentes corretos para o processo atual:
- **main** — coordenação geral e interface com Alan
- **PO** — planejamento e preparação dos artefatos
- **DESIGN** — prototipação e decisões de interface quando aplicável
- **DEV** — implementação
- **QA** — validação e evidências

### 4.2 Fluxo atual do Kadro/Kanban
O fluxo existente é adequado e deve ser preservado:
1. `Pending`
2. `PO`
3. `DESIGN`
4. `Alan approval`
5. `DEV`
6. `QA`
7. `Homologation`
8. `Archived`

### 4.3 Base arquitetural atual
A arquitetura atual já possui bons fundamentos:
- **workflow DB / Kanban** como fonte operacional de verdade
- **OpenSpec** como camada de artefatos
- comentários/handoffs no Kanban como superfície de coordenação
- tipagem de trabalho com `change`, `story` e `bug`
- uso crescente de Playwright e QA baseada em evidência

---

## 5. Diagnóstico dos problemas atuais

### 5.1 Drift entre camadas
Há divergência ocasional entre:
- runtime / workflow DB / Kanban
- OpenSpec
- coordination legacy
- metadados derivados

Isso gera necessidade de reconciliação manual e abre espaço para inconsistências em archive, homologação, path de artifacts e estado de stage.

### 5.2 Handoff ainda pouco padronizado
Os papéis dos agentes existem, mas falta um contrato operacional estrito e uniforme para:
- o que significa “pronto” em cada etapa
- o comentário mínimo obrigatório
- a evidência mínima exigida
- o estado mínimo do runtime antes de declarar conclusão

### 5.3 Main ainda atua como reconciliador excessivo
Hoje o agente principal acumula funções demais:
- coordenação
- reconciliação de estado
- auditoria manual
- mediação de falhas de processo

### 5.4 Paralelismo ainda pouco disciplinado
A base suporta `change`, `story`, `bug`, locks e dependências, mas a operação ainda não usa esse modelo com consistência suficiente.

### 5.5 Regras distribuídas demais
As regras existem, mas estão espalhadas entre:
- prompts e memória
- AGENTS.md
- docs/coordination
- OpenSpec
- código do workflow

---

## 6. Direção proposta
A proposta não é trocar a estrutura atual.

A proposta é:

> **manter Kadro + agentes atuais + workflow DB + OpenSpec, e profissionalizar a operação multiagente em cima dessa base**.

Em resumo:
- preservar a arquitetura atual
- reduzir ambiguidade operacional
- transformar handoffs em contratos claros
- reduzir drift
- melhorar governança de execução
- preparar terreno para escalar com segurança depois

---

## 7. Princípios do novo modelo operacional
1. **Kanban continua sendo a superfície principal de operação**.
2. **Workflow DB continua sendo a fonte operacional de verdade**.
3. **OpenSpec continua sendo a camada de artefatos**.
4. **Coordination legacy passa a ser espelho/auditoria, não superfície principal de operação**.
5. **Agentes existentes são mantidos**.
6. **Cada stage só pode ser concluído com runtime atualizado + comentário/handoff publicado**.
7. **QA continua sendo gate real de qualidade**.
8. **Main continua sendo a interface gerencial com Alan**.
9. **Trabalho técnico pesado continua fora do chat principal**.
10. **Paralelismo deve existir, mas sob regras explícitas de ownership, locks e dependências**.

---

## 8. Modelo operacional preservado

### 8.1 Agentes mantidos
- `main`
- `PO`
- `DESIGN`
- `DEV`
- `QA`

### 8.2 Fluxo mantido
- `Pending`
- `PO`
- `DESIGN`
- `Alan approval`
- `DEV`
- `QA`
- `Homologation`
- `Archived`

---

## 9. Estrutura do projeto em 2 fases

# Fase 1 — Padronizar a operação

## 9.1 Objetivo da fase 1
Organizar a forma de trabalho sem alterar a arquitetura base.

A prioridade aqui é reduzir ambiguidade e parar de depender de reconciliação manual como comportamento normal.

## 9.2 Resultado esperado da fase 1
Ao final da fase 1, o sistema deve operar com:
- papéis mais claros por agente
- handoffs padronizados
- Definition of Done por coluna
- regra explícita de fechamento de stage
- coordination legacy rebaixado para espelho

## 9.3 Atividades da fase 1

### Atividade 1 — Formalizar responsabilidades por agente
Definir de forma explícita o que cabe a:
- main
- PO
- DESIGN
- DEV
- QA

#### Entregáveis
- tabela de responsabilidades
- critérios de entrada e saída por agente
- responsabilidades que não podem ficar implícitas

#### Benefício
- menos ambiguidade operacional
- menos variação de comportamento entre turns

---

### Atividade 2 — Criar contrato padrão de handoff
Padronizar o comentário obrigatório de transição entre etapas.

#### Estrutura proposta
- **Status:** `ready | blocked | failed | approved`
- **Mudou:** resumo curto
- **Evidência:** links, arquivos, testes, artefatos
- **Próximo passo:** quem assume agora

#### Entregáveis
- template de comentário por tipo de etapa
- exemplos de handoff PO / DESIGN / DEV / QA

#### Benefício
- melhora legibilidade do card
- facilita auditoria
- reduz handoff incompleto

---

### Atividade 3 — Definir Definition of Done por coluna
Formalizar o critério de pronto para cada coluna do fluxo.

#### Colunas cobertas
- Pending
- PO
- DESIGN
- Alan approval
- DEV
- QA
- Homologation
- Archived

#### Entregáveis
- checklist por coluna
- regras de promoção de stage

#### Benefício
- reduz subjetividade
- diminui etapa “pronta no discurso, incompleta no runtime”

---

### Atividade 4 — Tornar explícita a regra de fechamento de stage
Toda etapa só pode ser declarada concluída se houver simultaneamente:
1. runtime atualizado
2. handoff/comentário publicado
3. artefatos consistentes com o estado

#### Entregáveis
- regra operacional consolidada
- exemplos de comportamento correto/incorreto

#### Benefício
- elimina completion “meia-boca”
- reduz drift entre fala, card e runtime

---

### Atividade 5 — Rebaixar coordination legacy para espelho
Formalizar que `docs/coordination/*.md` não é mais a operação viva.

#### Novo papel
- espelho
- histórico
- auditoria

#### Entregáveis
- definição clara do papel do legado
- alinhamento do time/agentes com isso

#### Benefício
- reduz fonte paralela de verdade
- diminui drift estrutural

---

### Atividade 6 — Consolidar o playbook operacional
Juntar as regras principais em um único playbook de operação.

#### Entregáveis
- documento único de operação
- resumo prático de como o time trabalha

#### Benefício
- menos regra espalhada
- mais previsibilidade

---

## 9.4 Critério de saída da fase 1
A fase 1 estará completa quando:
- handoffs estiverem padronizados
- DoD por coluna estiver definido
- agentes estiverem operando com papéis claros
- coordination legacy estiver explicitamente fora da operação viva
- fechamento de stage exigir runtime + handoff

---

# Fase 2 — Endurecer a execução e reduzir drift

## 10.1 Objetivo da fase 2
Depois da operação estar clara, melhorar a robustez do motor operacional.

A fase 2 não deve começar antes da fase 1 estar suficientemente estável.

## 10.2 Resultado esperado da fase 2
Ao final da fase 2, o sistema deve operar com:
- instruções dos agentes alinhadas ao playbook
- melhor uso de `story`, `bug`, locks e dependências
- archive/homologation mais confiáveis
- menos drift runtime ↔ OpenSpec ↔ metadados
- ownership e paralelismo mais disciplinados

## 10.3 Atividades da fase 2

### Atividade 1 — Alinhar instruções dos agentes ao playbook
Atualizar instruções dos agentes para refletir a operação padronizada definida na fase 1.

#### Entregáveis
- instruções revisadas de main / PO / DESIGN / DEV / QA
- consistência entre comportamento esperado e comportamento instruído

#### Benefício
- menos dependência de memória tácita
- execução mais estável

---

### Atividade 2 — Formalizar uso de `story`, `bug`, locks e dependências
Melhorar a execução interna das changes sem mexer no quadro principal.

#### Entregáveis
- regra de decomposição de change em stories
- regra de abertura e vínculo de bugs
- uso explícito de locks/dependências
- definição de ownership por run/agente

#### Benefício
- melhor paralelismo
- menos colisão de execução
- melhor rastreabilidade de retrabalho

---

### Atividade 3 — Melhorar automação de homologation e archive
Fortalecer o fechamento end-to-end para reduzir reconciliação manual.

#### Entregáveis
- fluxo mais confiável de homologation → archived
- validações de consistência entre runtime e OpenSpec
- redução de falhas parciais no archive

#### Benefício
- menos correção manual
- mais confiança no fechamento das changes

---

### Atividade 4 — Reduzir drift entre runtime, OpenSpec e metadados
Melhorar consistência de paths, estados e artefatos derivados.

#### Entregáveis
- reconciliação mais robusta
- metadados/path mais consistentes
- menos discrepância pós-archive

#### Benefício
- reduz bugs de processo
- melhora confiabilidade do quadro

---

### Atividade 5 — Refinar ownership e paralelismo
Definir melhor quando o trabalho pode ocorrer em paralelo e sob quais limites.

#### Entregáveis
- regra prática de WIP por change
- ownership por item
- critérios de bloqueio/desbloqueio

#### Benefício
- paralelismo útil, sem bagunça
- menos overlap entre agentes

---

## 10.4 Critério de saída da fase 2
A fase 2 estará completa quando:
- instruções dos agentes refletirem o playbook
- stories/bugs/locks/dependencies estiverem sendo usados com mais disciplina
- homologation/archive funcionarem com menos intervenção manual
- houver redução perceptível de drift entre runtime e OpenSpec

---

## 11. Papel formal de cada agente

### main — Coordenador / Orquestrador
**Responsabilidade principal:**
- coordenar a execução
- decidir o próximo passo
- escolher o agente da vez
- consolidar resultados
- manter comunicação gerencial com Alan

**Não deve:**
- virar executor técnico principal em tarefas pesadas
- esconder drift ou inconsistência operacional
- declarar etapa concluída sem atualização do runtime

---

### PO — Product Owner
**Responsabilidade principal:**
- transformar demanda em mudança planejada
- preparar artefatos
- definir escopo e critérios
- publicar links de revisão

**PO só pode concluir a etapa quando:**
- artifacts mínimos existirem
- links estiverem publicados no card/comentário
- runtime refletir o estado correto
- o próximo passo estiver explícito para Alan

---

### DESIGN
**Responsabilidade principal:**
- decidir e produzir protótipo quando houver UI
- registrar se a etapa foi `done` ou `skipped`
- publicar o link do protótipo/evidência visual

**DESIGN só pode concluir a etapa quando:**
- o protótipo existir ou a decisão de `skipped` estiver justificada
- comentário/handoff estiver registrado
- runtime estiver coerente

---

### DEV
**Responsabilidade principal:**
- implementar a entrega aprovada
- atualizar testes necessários
- publicar handoff para QA

**DEV só pode concluir a etapa quando:**
- o código estiver implementado
- a validação mínima tiver sido executada
- comentário/handoff estiver no card
- runtime estiver atualizado
- próximo passo estiver entregue claramente para QA

---

### QA
**Responsabilidade principal:**
- validar comportamento real
- produzir evidências
- abrir `bug` quando houver defeito real
- promover apenas entregas realmente verificadas

**QA só pode concluir a etapa quando:**
- houve validação real
- evidências foram publicadas
- bugs reais foram abertos quando necessário
- runtime foi atualizado
- comentário/handoff para Alan estiver pronto

---

## 12. Definition of Done por coluna

### Pending → PO
- item válido e claro
- pronto para ser puxado por PO

### PO → Alan approval
- proposal/review-ptbr publicados
- design/tasks quando aplicável
- links no card
- runtime atualizado
- handoff publicado

### DESIGN → Alan approval
- protótipo entregue ou `skipped` justificado
- link publicado
- runtime atualizado
- handoff publicado

### DEV → QA
- implementação pronta
- testes mínimos executados
- comentário DEV publicado
- runtime atualizado
- próxima validação explicitada

### QA → Homologation
- validação real executada
- evidências publicadas
- bugs reais registrados se existirem
- comentário QA publicado
- runtime atualizado

### Homologation → Archived
- homologação aprovada
- runtime atualizado
- archive completa runtime + OpenSpec
- metadados/path consistentes

---

## 13. Critérios de sucesso do projeto
O projeto será considerado bem-sucedido quando:
1. nenhuma etapa for declarada concluída sem runtime atualizado e handoff publicado
2. PO, DESIGN, DEV e QA operarem com contrato claro e previsível
3. Alan puder confiar no Kadro como superfície principal de consulta
4. OpenSpec e runtime permanecerem mais sincronizados
5. houver redução perceptível de drift, retrabalho e reconciliação manual
6. a arquitetura atual continuar preservada, porém com operação melhor

---

## 14. Riscos

### 14.1 Risco de burocracia excessiva
**Mitigação:** handoffs curtos e operacionais.

### 14.2 Risco de regras continuarem espalhadas
**Mitigação:** playbook único e instruções alinhadas.

### 14.3 Risco de o legado seguir como fonte paralela
**Mitigação:** tratar coordination legacy só como espelho/auditoria.

---

## 15. Recomendação executiva final
A melhor decisão para o projeto `crypto` **não é trocar o Kadro nem substituir os agentes já criados**.

A melhor decisão é:

> **manter a estrutura atual e evoluir a operação em duas fases: primeiro padronizar o trabalho, depois endurecer o motor operacional**.

---

## 16. Próximo passo recomendado
Abrir uma change específica com foco em executar este projeto.

**Nome sugerido:**
`evolve-multiagent-kadro-operating-model`

### Ordem recomendada de execução
1. executar **Fase 1** por completo
2. validar operação real com o novo padrão
3. só então iniciar **Fase 2**

---

## 17. Resumo final em uma frase
**O sistema atual já tem a arquitetura certa; o que falta é transformar essa arquitetura em um modo de operação disciplinado, padronizado e confiável — em duas fases, na ordem certa.**
