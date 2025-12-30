# Proposta: Redesign Premium da Interface de Backtest

## Objetivo
Transformar o formulário de backtest atual (utilitário e denso) em uma interface moderna, profissional e visualmente agradável ("Premium UI"), aplicando princípios de design hierárquico, espaçamento consistente e estética glassmorphism.

## Por Quê
A interface atual sofre de problemas de alinhamento, falta de hierarquia visual e inputs pouco convidativos. Uma ferramenta de análise financeira deve transmitir precisão e clareza. O redesign visa melhorar drasticamente a usabilidade (UX) e a percepção de qualidade (UI).

## O Que Muda

### Conceito Visual (Design System)
- **Estilo:** Glassmorphism refinado (fundo translúcido com blur, bordas sutis).
- **Cores:** Paleta escura profunda (`bg-slate-950` base) com acentos vibrantes (Azul elétrico, Roxo neon) apenas para ações principais e estados ativos.
- **Espaçamento:** Aumento do white-space (padding/gap) para reduzir a carga cognitiva.
- **Tipografia:** Títulos claros, labels em caixa alta/menores (`text-xs uppercase`) para distinção, e valores em destaque.

### Mudanças Específicas no Formulário (`CustomBacktestForm.tsx`)

1.  **Layout Estrutural:**
    - Abandonar a lista vertical única.
    - Adotar um **Grid Responsivo**: Configurações gerais à esquerda, Estratégias e Parâmetros à direita (ou topo/baixo com cards distintos).
    - Container principal com sombra suave e bordas arredondadas (`rounded-2xl`).

2.  **Componentes de Input:**
    - **Selects/Inputs:** Substituir os inputs padrão por componentes estilizados com altura maior (`h-12`), ícones internos e feedback de foco.
    - **Seletores de Botão:** Para opções curtas (ex: Mode, Timeframe), usar grupos de botões segmentados (Segmented Controls) em vez de dropdowns, facilitando o clique único.

3.  **Seção de Estratégias:**
    - Cards de seleção de estratégia com ícones grandes e descrições curtas.
    - Estado "Selecionado" com borda brilhante (glow effect).

4.  **Parâmetros Dinâmicos:**
    - Área dedicada para parâmetros que se anima/expande suavemente quando uma estratégia é selecionada.
    - Sliders para valores numéricos onde apropriado (opcional) ou inputs numéricos claros.

5.  **Action Bar:**
    - Botão "Run Backtest" grande, fixo ou em destaque, com gradiente e animação de hover.

## Verificação
- A interface deve parecer um "painel de controle de nave espacial" moderno, não um formulário de imposto de renda.
- Todos os textos devem ser legíveis com alto contraste.
- Alinhamento perfeito de grids.
