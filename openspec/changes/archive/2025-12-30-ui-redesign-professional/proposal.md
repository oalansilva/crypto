# Proposta: Redesign Profissional da Interface

## Objetivo
Transformar a aplicação de backtesting em uma ferramenta visualmente atraente, intuitiva e profissional, seguindo as melhores práticas de design de produtos financeiros/trading.

## Análise do Problema Atual

### Problemas Identificados
1. **Densidade Visual Excessiva**: Muitos elementos competindo por atenção
2. **Hierarquia Fraca**: Difícil identificar o que é mais importante
3. **Falta de Consistência**: Estilos diferentes entre componentes
4. **Espaçamento Inadequado**: Elementos muito próximos, causando claustrofobia visual
5. **Tipografia Inconsistente**: Tamanhos e pesos de fonte sem padrão claro

## Princípios de Design

### 1. **Minimalismo Funcional**
- Remover elementos desnecessários
- Focar no essencial: configurar e executar backtests
- "Menos é mais" - cada elemento deve ter um propósito claro

### 2. **Hierarquia Visual Clara**
- Usar tamanho, cor e espaçamento para guiar o olhar
- Elementos primários (ações principais) devem se destacar
- Elementos secundários (configurações avançadas) devem ser discretos

### 3. **Consistência de Sistema**
- Design tokens: cores, espaçamentos, tipografia padronizados
- Componentes reutilizáveis com comportamento previsível
- Linguagem visual uniforme em toda a aplicação

### 4. **Respiração Visual**
- Espaçamento generoso entre seções (24-32px)
- Padding interno consistente (16-24px)
- Uso de white space como elemento de design

### 5. **Feedback Visual**
- Estados claros: hover, active, disabled, loading
- Transições suaves (200-300ms)
- Indicadores de progresso visíveis

## Proposta de Redesign

### Sistema de Design

#### Paleta de Cores
```
Background:
- Primary: #0a0f1c (dark navy)
- Secondary: #1a1f2e (lighter navy)
- Elevated: #242938 (card background)

Accent:
- Primary: #3b82f6 (blue-500)
- Secondary: #8b5cf6 (purple-500)
- Success: #10b981 (green-500)
- Warning: #f59e0b (amber-500)
- Danger: #ef4444 (red-500)

Text:
- Primary: #ffffff
- Secondary: #94a3b8 (slate-400)
- Tertiary: #64748b (slate-500)
```

#### Tipografia
```
Headings:
- H1: 32px / 700 / Inter
- H2: 24px / 700 / Inter
- H3: 18px / 600 / Inter
- H4: 16px / 600 / Inter

Body:
- Large: 16px / 400 / Inter
- Regular: 14px / 400 / Inter
- Small: 12px / 400 / Inter
- Tiny: 10px / 500 / Inter (uppercase, tracking-wide)
```

#### Espaçamento
```
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px
```

#### Componentes Base

**Button:**
- Height: 40px (md), 48px (lg)
- Padding: 16px-24px
- Border-radius: 12px
- Font: 14px / 600

**Input:**
- Height: 48px
- Padding: 12px-16px
- Border-radius: 12px
- Border: 1px solid rgba(255,255,255,0.1)

**Card:**
- Padding: 24px
- Border-radius: 16px
- Background: rgba(255,255,255,0.03)
- Border: 1px solid rgba(255,255,255,0.05)

### Layout Proposto

#### 1. **Página Principal (Playground)**
```
┌─────────────────────────────────────────┐
│ Header (Logo + Navigation)              │
├─────────────────────────────────────────┤
│                                         │
│  Hero Section                           │
│  - Título grande                        │
│  - Descrição curta                      │
│  - CTA: "New Backtest" (destaque)       │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  Quick Start Presets (Grid 3 cols)     │
│  ┌──────┐ ┌──────┐ ┌──────┐           │
│  │ SMA  │ │ RSI  │ │  BB  │           │
│  └──────┘ └──────┘ └──────┘           │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  Recent Backtests (Table)               │
│                                         │
└─────────────────────────────────────────┘
```

#### 2. **Modal de Backtest (Wizard de 3 Etapas)**

**Etapa 1: Market Setup**
- Symbol (grande, destaque)
- Timeframe (segmented control)
- Date range (side-by-side)

**Etapa 2: Strategy Selection**
- Grid de cards (3-4 colunas)
- Cada card: ícone + nome + descrição curta
- Seleção visual clara (border highlight)

**Etapa 3: Risk & Parameters**
- Seção de Risk Management (destaque)
- Parâmetros de estratégia (colapsável, se não selecionada)
- Review summary (sidebar)

**Footer fixo:**
- Back button (secundário)
- Next/Run button (primário, destaque)

#### 3. **Strategy Builder**

**Layout de 2 Colunas:**

**Coluna Esquerda (40%):**
- Search bar (topo)
- Category list (vertical nav)
- Indicator cards (scrollable)

**Coluna Direita (60%):**
- Tabs: "Indicators" | "Logic"
- Tab "Indicators": Lista de selecionados + configuração
- Tab "Logic": Editor de condições (syntax highlighting)

### Componentes a Redesenhar

1. **CustomBacktestForm.tsx**
   - Transformar em wizard multi-step
   - Adicionar progress indicator
   - Melhorar feedback visual

2. **StrategyBuilder.tsx**
   - Simplificar sidebar de categorias
   - Melhorar cards de indicadores
   - Adicionar preview de código

3. **Playground.tsx**
   - Hero section mais impactante
   - Preset cards maiores e mais visuais
   - Melhor tabela de histórico

4. **ResultsPage.tsx**
   - Dashboard de métricas mais visual
   - Gráficos maiores e mais legíveis
   - Tabs para organizar informações

## Verificação

- [ ] Usuário consegue criar um backtest em ≤ 3 cliques
- [ ] Interface parece profissional e confiável
- [ ] Hierarquia visual é clara e intuitiva
- [ ] Aplicação funciona bem em diferentes tamanhos de tela
- [ ] Feedback visual é consistente e claro

## Próximos Passos

1. Criar sistema de design tokens (CSS variables)
2. Implementar componentes base reutilizáveis
3. Redesenhar página principal (Playground)
4. Transformar formulário em wizard
5. Polir Strategy Builder
6. Atualizar página de resultados
