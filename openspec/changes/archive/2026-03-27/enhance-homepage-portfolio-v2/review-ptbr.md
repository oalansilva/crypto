---
spec: openspec.v1
id: enhance-homepage-portfolio-v2
title: Review PT-BR - HomePage Portfolio Allocation
card: "#60"
change_id: enhance-homepage-portfolio-v2
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Review PT-BR: HomePage Portfolio Allocation

**Card:** #60 | `enhance-homepage-portfolio-v2`

---

## Resumo Executivo

Este card adiciona uma seção de alocação de portfólio na homepage, permitindo ao usuário visualizar sua exposição por ativo.

### O que este card faz:
- Gráfico doughnut de alocação
- Percentual e valor por ativo
- Total do portfólio
- Design responsivo
- Estados adequados (loading, empty, error)

### O que este card NÃO faz:
- Não gera sinais
- Não faz rebalanceamento
- Não tem histórico

---

## Pontos de Atenção

1. **Independente:** Este card não depende de nenhum outro e nenhum depende dele.

2. **Recharts:** Usar biblioteca já disponível no projeto.

3. **Limite de itens:** Max 8 no chart para não poluir visualização.

---

## Checklist de Validação

- [ ] Doughnut chart renderizando corretamente
- [ ] Cores consistentes com tema
- [ ] Responsivo em mobile
- [ ] Estados funcionando (loading, empty, error)
- [ ] Limite de 8 itens no chart

---

## Status: PRONTO PARA APROVAÇÃO

Este card está pronto para avançar para DEV.

---
