# Proposal - Padronizar Menus Web/Desktop

## Why
Os menus do projeto estão inconsistentes:
- AppNav precisa de hamburger para mobile
- ProjectSelector usa `<select>` nativo
- StrategyBuilder sidebar não é colapsável
- Falta padrão de UI entre componentes

## What Changes

### Fase 1: Componentes Base
- Criar `DropdownMenu` reutilizável
- Criar `Popover` para tooltips/actions

### Fase 2: AppNav
- Adicionar hamburger menu para mobile
- Usar DropdownMenu parauser menu
- Aplicar glass morphism consistente

### Fase 3: ProjectSelector
- Substituir `<select>` por Dropdown customizado
- Manter acessibilidade

### Fase 4: Sidebar
- Criar Sidebar colapsável
- Animação suave

### Fase 5: HomePage
- Padronizar atalhos com mesmo componente

## Design Direction (interface-design)
- Trading terminal profissional
- Cores: blue/emerald com glass surfaces
- Rejeitar native selects
