## Why

O fluxo canônico pula diretamente de `Todo` para desenvolvimento e não oferece um gate visual no qual um agente de design prepara e critica a solução, Alan aprova o protótipo por arraste e só então o Dev começa. Isso torna a aprovação implícita, favorece interfaces genéricas e deixa Codex, Cursor, GitHub Project e Kanban interno com contratos operacionais divergentes.

## What Changes

- **BREAKING**: substituir `In Progress` por `Em desenvolvimento` no campo `Status` e em todos os consumidores do workflow.
- Introduzir as etapas canônicas `Design`, `Aprovação de Design` e `Pronto para Dev` antes de `Em desenvolvimento`.
- Tornar o arraste `Aprovação de Design -> Pronto para Dev` uma aprovação humana auditável e restrita a Alan.
- Exigir `design.md`, evidência/protótipo versionado e crítica do agente para cards com impacto de UI antes da aprovação humana.
- Permitir que mudanças sem UI pulem as etapas de design apenas com `UI impact: none` e justificativa auditável.
- Atualizar GitHub Project 1, Kanban interno, APIs, validações, testes e documentação para o mesmo fluxo.
- Compartilhar o contrato operacional entre Codex e Cursor sem manter duas cópias divergentes.

## Capabilities

### New Capabilities

Nenhuma. A mudança aprofunda capacidades de workflow e Kanban já existentes.

### Modified Capabilities

- `kanban`: adicionar as colunas de design, aprovação por drag-and-drop, evidência visual no card e a nova ordem canônica.
- `workflow-state-db`: persistir e validar os novos estados, a aprovação humana vinculada à versão do design e os handoffs usados por Codex e Cursor.

## Impact

- GitHub Project 1: opções e documentação do campo `Status`; cards atuais preservam identidade e histórico.
- Backend: enums/modelos, transições, reconciliação, rotas, erros e testes do workflow.
- Frontend: colunas, drag-and-drop, detalhes/evidências do card e testes Kanban/Playwright.
- OpenSpec/agentes: contexto e regras de `design.md`, `AGENTS.md`, `rules.md` e instruções compartilhadas Codex/Cursor.
- Operação: preflight antes de `/opsx:apply`, migração compatível do status legado e evidência automática de aprovação.
