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
- Registro de busca em código: ausência de `Abrir Kanban` / `Kanban Real` em `frontend/src`.
- Screenshot/validado visual do `/` (Playground) sem os textos removidos.
- Resultado de consulta ao workflow canônico mostrando card `ajustes-tela-playground` em `Approval` (somente leitura desta etapa).

## Riscos conhecidos
- A palavra `kanban` ainda aparece em componentes de operação (KanbanPage, workflow API) e não deve ser tratada como resíduo da playground para este work item.

## Resultado técnico desta rodada (DEV)
- Fonte canônica consultada: card `ajustes-tela-playground` em `Approval`.
- Componente da tela playground identificado: `frontend/src/pages/HomePage.tsx` (via `Route path="/"` em `frontend/src/App.tsx`).
- A busca textual exata por `Abrir Kanban` e `Kanban Real` no `frontend/src` retornou zero resultados (case-sensitive).
- Há referências a `Kanban` em áreas funcionais do fluxo Kanban (`frontend/src/pages/KanbanPage.tsx`, `components/Layout.tsx`, `components/ProjectSelector.tsx`, `index.css`), alinhadas ao risco registrado e fora do escopo desta limpeza.
- Item DEV `3d92c704-5b7c-4738-8e0f-de8c142ce2db` concluído: não há residências textuais dos alvos em outras telas de playground.
- Tasks técnicas marcadas como concluídas no `tasks.md`: 3, 4 e 5.
