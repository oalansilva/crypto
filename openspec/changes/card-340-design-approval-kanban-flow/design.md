## Context

Hoje há três representações que precisam convergir: o campo `Status` do GitHub Project 1, o Kanban interno persistido no workflow DB e as instruções operacionais consumidas por Codex/Cursor. O fluxo atual começa a execução cedo demais, usa nomes legados (`Pending`, `PO`, `DESIGN`, `DEV`, `Homologation`, `Archived`) e não distingue crítica do agente de aprovação humana.

Alan é o decisor humano do gate visual. O gesto desejado é simples: revisar a entrega em `Aprovação de Design` e arrastar o card para `Pronto para Dev`. Esse gesto precisa ser equivalente no GitHub Project e no Kanban interno, sem permitir que um agente ou uma chamada anônima se passe por Alan.

## Goals / Non-Goals

**Goals:**

- Adotar a sequência canônica `Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`.
- Transformar o arraste de Alan em aprovação humana explícita, persistida e vinculada à versão revisada do design.
- Exibir `design.md`, protótipo/evidência e crítica do Designer Agent antes do início do desenvolvimento.
- Permitir bypass para trabalho sem interface somente com impacto de UI e justificativa explícitos.
- Fazer Codex, Cursor, GitHub Project e Kanban interno obedecerem ao mesmo contrato.

**Non-Goals:**

- Criar um editor visual completo dentro do produto.
- Substituir Figma, HTML navegável ou outra ferramenta de prototipação.
- Publicar a mudança em `main`; este card termina tecnicamente em `develop` para homologação.
- Automatizar a decisão humana de Alan com uma pontuação de IA.

## Decisions

### 1. Um vocabulário canônico, com aliases apenas na migração

As labels visíveis e os valores persistidos usarão exatamente os nomes em português definidos no fluxo. Entradas legadas serão aceitas somente no limite de migração e convertidas de forma idempotente. Valor desconhecido será erro; nunca haverá fallback silencioso para desenvolvimento.

Alternativa considerada: manter valores técnicos em inglês e traduzir apenas a UI. Rejeitada porque o GitHub Project, comentários operacionais e agentes continuariam divergindo.

### 2. O gate humano é uma transição autenticada

`Aprovação de Design -> Pronto para Dev` exige sessão válida e usuário autorizado como aprovador de design. O backend deriva a identidade da sessão; `actor` enviado pelo cliente não concede permissão. A aprovação grava aprovador, instante, digest do `design.md` e referência/digest do protótipo.

Se `design.md` ou o protótipo mudar depois da aprovação, a aprovação fica obsoleta e o card deve retornar ao gate de design antes de começar desenvolvimento.

Alternativa considerada: comentário ou checkbox como aprovação. Rejeitada porque o arraste solicitado por Alan deixaria de ser a ação canônica e haveria dois sinais concorrentes.

### 3. Entrega de design mínima e verificável

Para `ui_impact = affected`, a entrada em `Aprovação de Design` exige:

- `design.md` da change;
- uma seção `Prototype` com URL, caminho versionado ou wireframe verificável;
- uma seção `Design Critique` com avaliação de produto, UX, acessibilidade, responsividade e estados vazios/erro/loading;
- veredito explícito do Designer Agent.

O Kanban mostra esses dados em um bloco `Entrega de design`, com links e estado de validade. Para `ui_impact = none`, o card pode ir de `Todo` a `Pronto para Dev` somente com justificativa não vazia registrada.

Alternativa considerada: exigir Figma em todos os cards. Rejeitada porque mudanças pequenas podem ser bem especificadas por wireframe HTML/Markdown e trabalhos sem UI não devem criar artefatos artificiais.

### 4. Uma mesma máquina de estados no backend

O serviço de transições será a autoridade. Rotas, reconciliação e stage gates reutilizarão a mesma definição, evitando matrizes duplicadas. Retornos controlados serão permitidos antes de `Done` (`Aprovação de Design -> Design`, `Code Review -> Em desenvolvimento`, `QA -> Em desenvolvimento`); `Done`, `Homologado` e `Pronto` obedecem à regra de não regressão.

`Cancelado` e `Pronto` são terminais. Arquivar OpenSpec não move automaticamente o card para `Pronto`, pois publicação em `main` é uma evidência separada.

### 5. Board progressivo, sem esconder a ordem

O desktop oferece duas lentes para reduzir rolagem sem alterar o status:

- `Produto e Design`: Todo, Design, Aprovação de Design, Pronto para Dev.
- `Entrega`: Pronto para Dev, Em desenvolvimento, Code Review, QA, Done, Homologado, Pronto.

Uma visão `Todas` mantém a sequência completa. No mobile, o usuário escolhe uma etapa por vez. O drawer oferece o mesmo comando acessível de aprovação do drag-and-drop para teclado/touch.

#### Prototype

Wireframe funcional a implementar na rota existente `/kanban`:

```text
+---------------------------------------------------------------+
| Kanban   [Produto e Design] [Entrega] [Todas]                  |
+----------------+----------------+----------------+-------------+
| Todo           | Design         | Aprovação      | Pronto Dev  |
|                |                | de Design      |             |
| [card]         | [card]         | [card]         | [card]      |
|                |                |  design.md  ✓  |             |
|                |                |  protótipo  ✓  |             |
|                |                |  crítica    ✓  |             |
+----------------+----------------+----------------+-------------+
                                    arraste → aprova como Alan
```

### 6. Contrato versionado para Codex e Cursor

`AGENTS.md` e `rules.md` continuam normativos. Os adaptadores OpenSpec oficiais de Codex e Cursor serão versionados e gerados pela mesma versão da CLI. As instruções documentarão o de-para `/opsx:*` (Codex/intenção) e `/opsx-*` (comandos Cursor), sem alterar a ordem operacional.

## Design Critique

- **Produto:** o novo gate reduz retrabalho, mas só gera valor se a entrega mostrar a hipótese de produto e não apenas pixels. O template de `design.md` deve exigir problema, usuário e resultado esperado.
- **UX:** onze colunas simultâneas seriam difíceis de escanear; as lentes progressivas reduzem carga cognitiva e preservam uma visão completa quando necessária.
- **Acessibilidade:** drag-and-drop isolado excluiria teclado e touch. O drawer terá ação equivalente, foco visível, nome acessível e feedback de erro.
- **Responsividade:** no mobile, uma coluna selecionável evita miniaturas ilegíveis e rolagem horizontal excessiva.
- **Estados do sistema:** loading, vazio, erro de transição, aprovação obsoleta e bypass sem UI precisam de mensagens explícitas.
- **Design Agent verdict:** PASS para implementação, condicionado à autenticação server-side do aprovador e à invalidação por mudança da versão aprovada.

## Risks / Trade-offs

- [Status legados perderem posição] -> preservar IDs das opções existentes no GitHub Project, renomear `In Progress` in-place e migrar o workflow DB idempotentemente.
- [Agente simular aprovação humana] -> ignorar identidade fornecida pelo cliente e autorizar pelo usuário autenticado no servidor.
- [Duas máquinas de estados divergirem] -> centralizar transições e fazer rotas/reconciliação consumirem o mesmo serviço.
- [Gate burocrático para backend puro] -> bypass `ui_impact = none` com justificativa auditável.
- [Design aprovado mudar silenciosamente] -> comparar digests e invalidar a aprovação antes do handoff ao Dev.
- [Board largo demais] -> lentes Produto e Design/Entrega, visão Todas opcional e navegação por etapa no mobile.

## Migration Plan

1. Adicionar metadados de impacto/entrega/aprovação e migração idempotente do workflow DB.
2. Centralizar a máquina de estados e rejeitar status desconhecidos.
3. Atualizar API e Kanban interno com autenticação e entrega de design.
4. Atualizar opções do Project 1 preservando IDs e registrar a nova ordem no readme.
5. Versionar instruções Cursor/Codex e atualizar regras/documentação.
6. Reconciliar cards ativos, executar testes de backend/frontend e QA visual.

Rollback: o código aceita aliases legados durante a janela de migração; as opções novas do Project podem ser mantidas sem perda de cards. Não remover colunas/metadados persistidos no rollback inicial.

## Open Questions

Nenhuma decisão bloqueante. A ferramenta concreta de protótipo continua livre por card, desde que a evidência seja versionada ou tenha uma versão/digest verificável.
