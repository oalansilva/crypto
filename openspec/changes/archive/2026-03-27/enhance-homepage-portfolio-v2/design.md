---
spec: openspec.v1
id: enhance-homepage-portfolio-v2
title: HomePage Portfolio Allocation - Design
card: "#60"
change_id: enhance-homepage-portfolio-v2
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Design: HomePage Portfolio Allocation

**Card:** #60 | `enhance-homepage-portfolio-v2`

---

## 1. Visão Geral

Adicionar seção de alocação de portfólio na homepage.

### Layout

```
┌─────────────────────────────────────┐
│  📊 Alocação do Portfólio           │
├─────────────────────────────────────┤
│                                     │
│         ┌───────────┐               │
│        │  Doughnut  │               │
│         │   Chart    │               │
│         └───────────┘               │
│                                     │
│  ● BTC   50%   $50,000             │
│  ● ETH   25%   $25,000             │
│  ● SOL   15%   $15,000             │
│  ● ...                               │
│                                     │
│  ─────────────────────────          │
│  Total: $100,000 USD               │
└─────────────────────────────────────┘
```

---

## 2. Componentes

### PortfolioAllocation

- Container principal
- Estados: loading, empty, error, populated

### DoughnutChart

- Gráfico de rosca
- Cores por ativo (palette)
- Hover: tooltip com detalhes
- Center: total value

### AllocationLegend

- Lista de ativos
- Cor, nome, percentual, valor
- Máximo 8 itens + "outros"

---

## 3. Especificações Visuais

### Cores (Dark Theme)

| Ativo | Cor |
|-------|-----|
| BTC | #F7931A |
| ETH | #627EEA |
| SOL | #9945FF |
| Default | Palette from #14F195 |

### Tipografia

- Título: 18px, semi-bold
- Valores: 14px, regular
- Percentual: 14px, medium

---

## 4. Estados

| Estado | UI |
|--------|-----|
| Loading | Skeleton do chart |
| Empty | "Adicione ativos ao portfólio" |
| Error | "Erro ao carregar portfólio" + retry |
| Populated | Chart + legend |

---

## 5. Responsividade

- Desktop: Chart centralizado + legend ao lado
- Mobile: Chart + legend empilhados verticalmente

---

## 6. Próximo Passo

Passar para Alan approval.

---
