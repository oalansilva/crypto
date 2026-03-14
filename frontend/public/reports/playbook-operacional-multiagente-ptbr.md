# Playbook Operacional Multiagente

Este é o contrato operacional da Fase 1 para o modelo multiagente atual do projeto `crypto`.

## Escopo

Este playbook padroniza como o time atual opera **sem trocar**:
- o fluxo atual do Kadro / Kanban
- os agentes persistentes atuais (`main`, `PO`, `DESIGN`, `DEV`, `QA`)
- o workflow DB como fonte operacional de verdade
- o OpenSpec como camada de artefatos

Ele define a forma de trabalho da **Fase 1**:
- responsabilidades explícitas por papel
- contrato padrão de handoff/comentário
- evidência mínima esperada
- Definition of Done por coluna
- regra explícita de que etapa só fecha com **runtime + handoff**
- `docs/coordination/*.md` como **espelho/auditoria**, não como superfície operacional viva

## Estrutura preservada

### Agentes persistentes
- `main`
- `PO`
- `DESIGN`
- `DEV`
- `QA`

### Fluxo do Kadro / Kanban
- `Pending`
- `PO`
- `DESIGN`
- `Alan approval`
- `DEV`
- `QA`
- `Alan homologation`
- `Archived`

## Regras operacionais centrais

1. **Kanban é a superfície principal de operação.**
2. **Workflow DB / runtime é a fonte operacional de verdade.**
3. **OpenSpec é a camada de artefatos/documentação.**
4. **`docs/coordination/*.md` é espelho/auditoria, não operação viva.**
5. **Uma etapa só conta como concluída quando runtime + handoff estiverem atualizados no mesmo turno.**
6. **QA é gate real de qualidade.**
7. **O chat principal com Alan deve continuar gerencial.**
8. **Trabalho técnico pesado deve continuar fora do chat principal.**

## Responsabilidades por papel

### `main` — Coordenador / Orquestrador
Responsável por:
- coordenar a execução
- decidir o próximo passo
- escolher o agente da vez
- consolidar resultados
- manter comunicação gerencial com Alan

Não deve:
- absorver por padrão a execução técnica pesada
- declarar etapa concluída sem atualização do runtime
- mascarar drift ou inconsistência operacional

### `PO`
Responsável por:
- transformar demanda em mudança planejada
- preparar artefatos de planning
- definir escopo e critérios
- publicar links de revisão

Só pode concluir a etapa quando:
- os artifacts mínimos existirem
- os links estiverem publicados
- o runtime refletir o estado correto
- o próximo passo estiver explícito

### `DESIGN`
Responsável por:
- decidir se há necessidade de protótipo
- produzir protótipo quando aplicável
- registrar a etapa como `done` ou `skipped`
- publicar o link do protótipo/evidência

Só pode concluir a etapa quando:
- o protótipo existir ou o `skipped` estiver justificado
- o handoff estiver registrado
- o runtime estiver coerente

### `DEV`
Responsável por:
- implementar a entrega aprovada
- atualizar testes necessários
- publicar handoff para QA

Só pode concluir a etapa quando:
- a implementação estiver pronta
- a validação mínima tiver sido executada
- o handoff estiver publicado
- o runtime estiver atualizado
- o próximo passo para QA estiver claro

### `QA`
Responsável por:
- validar comportamento real
- produzir evidências
- abrir `bug` quando houver defeito real
- promover apenas entregas realmente verificadas

Só pode concluir a etapa quando:
- a validação real tiver sido executada
- as evidências estiverem publicadas
- bugs reais tiverem sido registrados quando necessário
- o runtime estiver atualizado
- o handoff para Alan estiver pronto

## Contrato padrão de handoff / comentário

Toda transição de etapa deve deixar um comentário/handoff curto no Kanban.

### Estrutura padrão
- **Status:** `ready | blocked | failed | approved`
- **Mudou:** resumo curto e objetivo
- **Evidência:** links, arquivos, testes ou artefatos
- **Próximo passo:** quem assume agora

### Evidência mínima por papel
- **PO:** links dos artifacts de planning
- **DESIGN:** link do protótipo ou justificativa de `skipped`
- **DEV:** arquivos alterados relevantes, testes mínimos ou evidência de implementação
- **QA:** evidências de validação real (logs, screenshots, summaries, traces, relatórios)

## Definition of Done por coluna

### `Pending` → `PO`
- item válido e claro
- pronto para ser puxado por PO

### `PO` → `Alan approval`
- proposal / review-ptbr publicados
- design / tasks quando aplicável
- links publicados no card
- runtime atualizado
- handoff publicado

### `DESIGN` → `Alan approval`
- protótipo entregue ou `skipped` justificado
- link publicado
- runtime atualizado
- handoff publicado

### `DEV` → `QA`
- implementação pronta
- testes mínimos executados
- comentário DEV publicado
- runtime atualizado
- próxima validação explicitada

### `QA` → `Alan homologation`
- validação real executada
- evidências publicadas
- bugs reais registrados se existirem
- comentário QA publicado
- runtime atualizado

### `Alan homologation` → `Archived`
- homologação aprovada
- runtime atualizado
- archive completa runtime + OpenSpec
- metadados/path consistentes

## Regra de reconciliação de drift

Se houver divergência entre:
- runtime / workflow DB / Kanban
- OpenSpec
- `docs/coordination/*.md`

A prioridade operacional é:
1. **runtime / workflow DB / Kanban**
2. **OpenSpec**
3. **coordination markdown (espelho)**

Quando houver drift:
- o turno seguinte deve priorizar reconciliação
- não deve haver declaração enganosa de etapa concluída
- a inconsistência deve ser tornada visível no handoff quando relevante

## Checklist prático por turno

Antes de encerrar um turno, o agente responsável deve confirmar:
- atualizei o runtime/Kanban?
- deixei handoff/comentário?
- o próximo dono está claro?
- a evidência mínima existe?
- ficou algum drift aberto?

Se sim, o turno está operacionalmente consistente.

## Limites desta fase

Este playbook **não** endurece ainda:
- alinhamento profundo das instruções dos agentes
- uso disciplinado de `story`, `bug`, locks e dependências
- fechamento end-to-end de homologation/archive com redução máxima de reconciliação

Esses itens pertencem à **Fase 2**.
