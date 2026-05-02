## Context

O produto já tem suporte parcial a ações: seletor US Stocks em Combo Configure, endpoint NASDAQ-100, providers Stooq/Yahoo, filtros de ações em Favoritos/Monitor e testes com `AAPL`/`NVDA`. Para o MVP, Alan definiu que o foco é apenas Crypto.

## Goals / Non-Goals

**Goals:**
- Remover ações dos fluxos operacionais visíveis do usuário.
- Bloquear endpoints operacionais que hoje permitem uso de ações no MVP.
- Manter o Monitor e Favoritos coerentes quando existirem dados legados de ações.
- Atualizar testes para o contrato crypto-only.

**Non-Goals:**
- Apagar providers Stooq/Yahoo ou histórico técnico de suporte a ações.
- Migrar ou deletar dados legados de favoritos em banco.
- Arquivar OpenSpec, commitar, abrir PR ou fazer merge.

## Decisions

- Decisão: tratar símbolo cripto como par contendo `/`, seguindo padrão já usado pelo repo.
  Alternativa considerada: manter classificação genérica em `asset_classification`. Rejeitada para este card porque manteria ações como caminho válido no MVP.

- Decisão: filtrar itens não cripto na UI em vez de mostrar mensagens por item.
  Alternativa considerada: exibir ações desabilitadas. Rejeitada porque o pedido é remover ações, não explicar indisponibilidade.

- Decisão: endpoint NASDAQ-100 responde indisponível no MVP, e candles rejeita símbolos não cripto.
  Alternativa considerada: remover rotas. Rejeitada para reduzir risco de import/route regressions e dar erro explícito a clientes antigos.

- Decisão: manter código/provider legado fora do caminho operacional.
  Alternativa considerada: remoção ampla de providers, schemas e serviços. Rejeitada por blast radius alto para uma entrega de implementação.

## Risks / Trade-offs

- [Dados legados de ações em favoritos] -> UI filtra da experiência principal; banco não é migrado neste card.
- [Testes antigos esperam ações] -> atualizar cobertura para crypto-only e endpoints bloqueados.
- [Clientes externos chamando ações] -> retorno explícito evita uso silencioso fora do MVP.

