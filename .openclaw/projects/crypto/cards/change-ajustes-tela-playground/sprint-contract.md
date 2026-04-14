# Contrato de sprint

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta sprint
Ajustes tela playground

## Fora de escopo
- Alterações no backend/workflow de Kanban.
- Mudanças em componentes dedicados à rota/funcionalidade Kanban, exceto a manutenção operacional da tela de revisão Kanban (legacy/runtime).

## Comportamentos esperados
- Remover de texto/cta visível da área de playground qualquer referência explícita a Kanban/Kaban.
- Garantir que os exemplares citados como resíduos (“Abrir Kanban”, “Kanban Real”) não aparecem em UI/rotas do playground.
- Manter a funcionalidade restante do playground intacta.

## Sensores obrigatorios
- build: required, command=`npm --prefix frontend run build`
- playwright: required, command=`(checagem visual manual de tela principal no /)`

## Evidencias esperadas
- Registro de busca em código: ausência de `Abrir Kanban` / `Kanban Real` em `frontend/src` para a tela de playground.
- Registro da busca global por `kanban`, `Kanban`, `Kaban` com escopo discriminado (playground x módulo Kanban).
- Screenshot/validado visual do `/` (Playground) sem os textos removidos.
- Resultado de consulta ao workflow canônico mostrando card `ajustes-tela-playground` em `Approval` (somente leitura desta etapa).

## Riscos conhecidos
- A palavra `kanban` ainda aparece em componentes de operação (KanbanPage, Workflow API e layout) e não deve ser tratada como resíduo da playground para este work item.

## Resultado técnico desta rodada (DEV)
- Fonte canônica consultada: card `ajustes-tela-playground` em `Approval` (confirmação por card endpoint e board endpoint).
- Busca textual no `frontend/src` por `\bkanban\b`, `Kaban`, `Abrir Kanban`, `Kanban Real` retornou ocorrências concentradas em:
  - frontend/src/pages/ComboSelectPage.tsx (ícone Lucide `Kanban`)
  - frontend/src/pages/KanbanPage.tsx (módulo Kanban operacional)
  - frontend/src/components/Layout.tsx (detecção de rota `/kanban`)
  - frontend/src/components/ProjectSelector.tsx (ícone `FolderKanban`)
  - frontend/src/index.css (estilos `.kanban-page`)
- Não foram encontradas ocorrências literais de `Abrir Kanban` ou `Kanban Real` fora de artefatos históricos.
- Work item DEV `63436f67-33db-4795-ba15-abf9e1e5aee7` concluído: inventário completo de referências iniciais executado.
- Tasks técnicas marcadas como concluídas no `tasks.md`: 1, 2, 3, 4 e 5.
