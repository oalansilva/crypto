## Context

O frontend atual possui um design system parcial com tokens de cores, tipografia e componentes, porém:
- Tema light como padrão (usuário quer dark)
- Design tokens existentes funcionam como base, mas precisam de adaptação para dark
-multiple pages e componentes que precisam de padronização
- Sem sistema formal de design (tokens dispersos no CSS)

O redesign afetará todas as telas e componentes existentes.

## Goals / Non-Goals

**Goals:**
- Criar design system completo com tema dark como padrão
- Garantir contrast ratio WCAG AA (mínimo 4.5:1 para texto)
- Padronizar todos os componentes e telas
- Melhorar responsividade (mobile, tablet, desktop)
- Criar experiência visual profissional e consistente

**Non-Goals:**
- Mudar funcionalidades existentes
- Adicionar novas features
- Alterar arquitetura do código
- Modificar fluxos de usuário

## Decisions

### 1. Abordagem de Tema
**Decisão:** Implementar CSS variables com suporte a theme switching
**Rationale:** Mais flexível que soluções JS-heavy, permite transição suave e suporte futuro a light mode

### 2. Paleta de Cores Dark
**Decisão:** Usar base neutra escura com acentos estratégicos
**Alternativas consideradas:**
- Pure black (#000): muito harsh
- Gray900 (#111827): bom, mas preciso de mais profundidade
- Slate/Zinc 900-950: melhor para hierarquia visual
**Seleção:** Zinc/Slate com accent em emerald/cyan para fintech/crypto

### 3. Tipografia
**Decisão:** Manter Plus Jakarta Sans (já carregada) por ser moderna e legible
**Rationale:** Excelente para UI, boa legibilidade em diferentes tamanhos

### 4. Componentes
**Decisão:** Criar biblioteca de componentes base com variantes
**Alternativas:**
- Usar shadcn/ui: adiciona dependência, pode ser overkill
- Criar do zero com CSS variables: mais controle, zero dependências
**Seleção:** Extender tokens existentes com variantes dark

### 5. Responsividade
**Decisão:** Mobile-first com breakpoints Tailwind
**Breakpoints:**
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## Risks / Trade-offs

- **[Risk]** Transição de light para dark pode quebrar componentes que usam cores hardcoded
  → **Mitigation:** Auditoria de componentes e uso consistente de CSS variables
  
- **[Risk]** Contraste insuficiente em alguns casos
  → **Mitigation:** Testar com axe-core ou manual, priorizar text-primary over text-secondary

- **[Risk]**工作量 grande (todas as telas)
  → **Mitigation:** Priorizar componentes base primeiro, depois páginas

- **[Risk]** Regressão visual em páginas não testadas
  → **Mitigation:** Checklist de validação por página

## Migration Plan

1. **Fase 1 - Design System Core**
   - Definir CSS variables dark
   - Atualizar tokens de cores
   - Criar utilities de tema

2. **Fase 2 - Componentes Base**
   - Button, Input, Card, Badge
   - Sidebar, Navbar
   - Modals, Dropdowns

3. **Fase 3 - Páginas**
   - Landing/Home
   - Lab e Run
   - Monitor
   - Kanban
   - Combo/Optimize
   - Demais páginas

4. **Fase 4 - Validação**
   - Teste de responsividade
   - Verificação de contraste
   - Teste em diferentes dispositivos
