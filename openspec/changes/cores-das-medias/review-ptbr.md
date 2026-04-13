# Review PT-BR — Card #89

## Resumo

**Card:** #89 — Cores das Médias  
**Projeto:** crypto  
**Mudar:** Aplicar cores diferenciadas às médias móveis no gráfico TradingView-like do monitor

---

## O que é

Estilização de UI: adicionar cores às médias móveis (SMA, EMA) baseadas no período:
- **Curta (< 20):** 🔴 Vermelho
- **Média (20-50):** 🟠 Laranja
- **Longa (> 50):** 🔵 Azul

**Relação com card #87:** #87 criou a visualização TradingView-like. Este card complementa com estilização de cores.

---

## Decisão Necessária

**Thresholds definidos nesta rodada:**

1. **Curta:** `< 20`
2. **Média:** `>= 20` e `< 50`
3. **Longa:** `>= 50`

**Ainda pendente:**

1. **Cores específicas:** confirmar hex codes finais com DESIGN
2. **Card #87 já implementado?:** precisa existir para esta mudança fazer sentido

---

## Tradeoffs

| | Prós | Contras |
|---|---|---|
| **Cores por período** | Facilita identificação visual | Pode conflitar com cores de的其他 elementos |
| **Padrão TradingView** | Usuários familiarizados | Pode não ser acessível para daltônicos |

---

## Próximo Passo

**Alan approval** → DEV implementation

**Nota:** Depende de card #87 (visualização TradingView) estar implementado primeiro.

---

## Artefatos

- `openspec/changes/cores-das-medias/proposal.md`
- `openspec/changes/cores-das-medias/review-ptbr.md`
- `openspec/changes/cores-das-medias/tasks.md`
