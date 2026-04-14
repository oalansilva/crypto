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
- A busca textual por `Abrir Kanban` e `Kanban Real` no código frontend ativo não encontrou ocorrências além dos artifacts de change.
