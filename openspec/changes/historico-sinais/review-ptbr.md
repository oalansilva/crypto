---
spec: openspec.v1
id: historico-sinais
title: Review PT-BR - Histórico de Sinais
card: "#57"
change_id: historico-sinais
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Review PT-BR: Histórico de Sinais

**Card:** #57 | `historico-sinais`

---

## Resumo Executivo

Este card implementa o histórico de sinais de trading, permitindo consultar sinais passados e suas métricas básicas.

### O que este card faz:
- Armazena todos os sinais gerados pelo Card #53
- Permite filtrar por ativo, tipo, período, confidence e status
- Trackeia status do sinal (ativo, disparado, expirado)
- Salva snapshot dos indicadores no momento da geração
- Fornece métricas básicas de performance

### O que este card NÃO faz:
- Não exibe gráficos avançados (Card #56)
- Não faz backtesting automatizado
- Não envia notificações

---

## Pontos de Atenção

1. **Dependência do Card #53:** O histórico só faz sentido após Card #53 gerar sinais.API deve ser projetada para receber sinais de #53.

2. **Volume de dados:** Com 90 dias de retenção e sinais frequentes, a tabela pode crescer. Índices adequados são essenciais.

3. **Indicators snapshot:** É importante salvar o estado dos indicadores no momento do sinal para análise posterior.

---

## Checklist de Validação

- [ ] Tabela PostgreSQL com índices apropriados
- [ ] Endpoint GET /signals/history com todos os filtros
- [ ] Endpoint PUT /signals/{id}/status para atualizar
- [ ] Snapshot de indicadores salvo com cada sinal
- [ ] Retenção de 90 dias configurada
- [ ] Paginação funcionando corretamente

---

## Status: PRONTO PARA APROVAÇÃO

Este card está pronto para avançar para DESIGN.

---
