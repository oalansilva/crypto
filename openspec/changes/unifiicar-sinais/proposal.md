# Proposal: Unificar Sinais das Três Telas

## User Story

**Como** trader  
**Eu quero** ver um único sinal consolidado por ativo que combina AI Dashboard, On-chain e Signals  
**Para** ter uma decisão clara sem precisar interpretar múltiplos sinais contraditórios

---

## Value Proposition

- **Decisão simplificada** — um sinal claro por ativo
- **Sem confusão** — não há sinais contraditórios para interpretar
- **Visão consolidada** — três fontes combinadas em uma

---

## Problem Statement

Hoje existem três fontes de sinais separados:
- `/ai-dashboard` — sinais de IA
- `/signals/onchain` — sinais on-chain
- `/signals` — sinais gerais

O usuário precisa navegar entre 3 telas e interpretar sinais que podem ser contraditórios.

---

## ⚠️ Scope Change (Alan)

**Original approach (REJECTED):**
- Mostrar sinais de cada fonte separadamente com badges
- Filtros por fonte
- Indicador de "força" baseado em quantas fontes concordam

**New approach (REQUIRED):**
- Um único sinal consolidado por ativo
- Combina as três fontes (AI, On-chain, Signals) em um só
- Interface mostra apenas o sinal final unificado

---

## Scope In

- Criar sinal único consolidado que combina AI Dashboard + On-chain + Signals
- Exibir um único sinal por ativo (não três sinais separados)
- Mostrar indicação do que contribuiu para o sinal (opcional: quais fontes confirmaram)
- Substituir a view de sinais existente pelo sinal unificado

**Funcionalidades:**
- Lista de ativos com UM sinal consolidado cada
- Sinal pode ser: Compra Forte, Compra, Neutro, Venda, Venda Forte
- Cada sinal consolidado indica a combinação das três fontes
- (Opcional) Tooltip ou expandable mostrando breakdown por fonte

---

## Scope Out

- Não altera a lógica de geração de sinais de cada fonte
- Não remove as telas individuais (podem coexistir para debugging)
- Não é sobre executar trades automaticamente
- Não mostra sinais separados por fonte na interface principal

---

## Signal Consolidation Logic

| AI | On-chain | Signals | Resultado |
|----|----------|---------|-----------|
| Bullish | Bullish | Bullish | Compra Forte |
| Bullish | Bullish | Neutral | Compra |
| Bullish | Neutral | Bearish | Neutro |
| Bearish | Bearish | Bearish | Venda Forte |
| ... | ... | ... | ... |

**Lógica exata a ser definida por DEV** — pode usar voting, weighted average, ou outro algoritmo.

---

## UX Design Direction

1. **Base:** Usar `/ai-dashboard` como tela principal
2. **Um sinal por ativo:** BTC tem UM sinal consolidado, não três
3. **Indicador de direção:** Compra/Venda com força
4. **Breakdown (opcional):** Hover/tap mostra contribuição de cada fonte

**Exemplo de UI:**
```
BTC  →  Compra Forte ↑↑
      └─ AI: Alta | On-chain: Confirma | Signals: Compra
      
ETH  →  Neutro
      └─ AI: Alta | On-chain: Fraco | Signals: Neutro
```

---

## Dependencies

- APIs de cada fonte devem continuar existindo
- Nova lógica de consolidação/agregação necessária
- Pode precisar de nova API ou endpoint que agrega os três sinais

---

## Risks

1. **Lógica de consolidação** — como combinar sinais conflitantes?
2. **Performance** — buscar de três fontes pode ser lento
3. **Ausência de sinal** — se uma fonte falha, consolidação ainda funciona?
4. **Manutenção** — código mais complexo

---

## ICE Score

- Impact: 8 (decisão mais rápida e clara)
- Confidence: 7 (escopo mais claro agora)
- Ease: 4 (lógica de consolidação complexa)
- **ICE: 224**

---

## Prototyping

**⚠️ Prototype obrigatório** — UI de unificação complexa precisa de protótipo antes de Alan approval.
DESIGN deve criar protótipo em `prototype/prototype.html` ou `prototype.html`.
