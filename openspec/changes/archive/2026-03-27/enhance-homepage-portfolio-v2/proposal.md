---
spec: openspec.v1
id: enhance-homepage-portfolio-v2
title: HomePage Portfolio Allocation
card: "#60"
change_id: enhance-homepage-portfolio-v2
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Proposal: HomePage Portfolio Allocation

**Card:** #60  
**change_id:** `enhance-homepage-portfolio-v2`  
**Estágio:** DESIGN  
**User Story:** Como usuário, quero ver a alocação do meu portfólio na homepage para entender minha exposição a cada ativo.

---

## 1. User Story & Objetivos

**User Story:**
> Como usuário, quero ver a alocação do meu portfólio na homepage para entender minha exposição a cada ativo e balancear melhor minhas posições.

**Critérios de aceite:**
- Gráfico de pizza/torre mostrando alocação por ativo
- Percentual e valor em USD de cada ativo
- Total do portfólio exibido
- Atualização em tempo real ao mudar holdings
- Design responsivo

**Decisão-chave:** Este card é independente dos cards de sinais e indicadores. Pode ser implementado em paralelo.

---

## 2. Conexões com Outros Cards

### Este card depende de:
- Nenhum (é independente)

### Outros cards dependem deste:
- Nenhum (é auto-contido)

### Notas:
- Este card foca apenas na visualização de alocação
- Não gera sinais ou recomendações
- Integra com dados existentes de portfólio

---

## 3. Decisões Definidas

| Item | Decisão |
|------|---------|
| Tipo de gráfico | Doughnut chart (mais moderno que pizza) |
| Dados | Consumidos da API existente de portfólio |
| Cores | Paleta consistente com tema dark |
| Responsivo | Mobile-first |
| Infraestrutura | $0 — frontend apenas |

---

## 4. Escopo

### Dentro do escopo
- [ ] Componente de gráfico de alocação
- [ ] Exibição de percentual e valor por ativo
- [ ] Total do portfólio
- [ ] Design responsivo
- [ ] Estados: loading, empty, error

### Fora do escopo
- [ ] Rebalanceamento automático
- [ ] Alertas de concentração
- [ ] Histórico de alocação (Card futuro)

---

## 5. Arquitetura

```
┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  Portfolio   │
│  (React)     │◀────│    API       │
└──────────────┘     └──────────────┘
```

**Stack:**
- Frontend: React + TypeScript (existing)
- Charting: Recharts ou similar
- API: Endpoints existentes de portfólio

---

## 6. API (Existente)

O frontend já tem acesso aos dados de portfólio via API existente.

**Dados necessários:**
```json
{
  "portfolio": [
    { "asset": "BTC", "amount": 0.5, "value_usd": 50000 },
    { "asset": "ETH", "amount": 5.0, "value_usd": 15000 }
  ],
  "total_value_usd": 65000
}
```

---

## 7. Custos

| Recurso | Custo |
|---------|-------|
| Frontend (reativo) | $0 |
| Recharts | $0 (MIT) |
| **Total** | **$0/mês** |

---

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Dados de portfólio indisponíveis | Estado empty com mensagem |
| Muitos ativos (poluição visual) | Limitar a top 8 + "outros" |

---

## 9. Próximo Passo

Após DESIGN, passar para Alan approval.

---
