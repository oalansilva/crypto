## REMOVED Requirements

### Requirement: Mobile Kanban MUST show one stage at a time
**Reason:** UI mobile do Kanban interno (`/kanban`) foi descontinuada; board oficial é o GitHub Project 1.
**Migration:** Operar cards no Project 1 (mobile/desktop via GitHub). Remover testes/protótipos que dependam da página interna.

### Requirement: Mobile Kanban MUST support swipe and tab stage navigation
**Reason:** Navegação mobile era da página `/kanban` removida.
**Migration:** Sem superfície interna; Project 1 no cliente GitHub.

### Requirement: Mobile Kanban MUST provide a touch-friendly card layout
**Reason:** Layout de cards mobile era da UI interna.
**Migration:** N/A no produto Cripto Farol após remoção da rota.

### Requirement: Task detail MUST open as a full-screen bottom sheet
**Reason:** Bottom sheet era da UI Kanban interna.
**Migration:** Detalhe do card no GitHub Issue/Project.

### Requirement: Mobile Kanban MUST define performance protections
**Reason:** Proteções de renderização eram da UI interna.
**Migration:** N/A após remoção da página.
