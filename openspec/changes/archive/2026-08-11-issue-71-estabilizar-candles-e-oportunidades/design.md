## Context

Os fluxos de beta usam `Monitor` como tela principal, então o atraso em endpoints de dados afeta diretamente a perceção de congelamento.
Hoje, o endpoint `/api/opportunities` faz coleta paralela por estratégia e pode ficar bloqueado quando um provider externo fica lento.
O endpoint de candles já suporta `4h/1d`, mas a regra atual para ativos de bolsa impede o uso prático do modo `4h` que o frontend pode solicitar.

## Goals / Non-Goals

**Goals:**

- Entregar resposta de candles em `4h` e `1d` para uso do Monitor sem erro estrutural.
- Impedir que falhas pontuais em coleta de oportunidades travem o endpoint inteiro.
- Entregar proteção por timeout no fluxo de coleta em lote de oportunidades.

**Non-Goals:**

- Alterar estratégia de recomendação financeira da tela.
- Introduzir novas fontes de dados principais além das já existentes (CCXT/US stocks/EOD, Yahoo fallback).
- Redesenhar o schema geral de respostas além do necessário para os cenários acima.

## Decisions

- Manter `stooq` como fonte principal de `stock/1d`, e usar `Yahoo` explicitamente para `stock/4h` via agregação nativa já existente.
  - Alternativas: manter erro para `stock/4h` ou tentar “forçar” stooq com agregação manual. Forçar stooq continua inválido por contrato e não evita falhas de forma limpa.
- Adicionar timeout por lote no consumo de providers em `OpportunityService` (na agregação paralela), em vez de apenas depender de timeout de socket dos providers.
  - Alternativas: aguardar todos os futures sem timeout (mais simples, mais arriscado), ou impor timeout por tarefa com processos separados (mais pesado).
- Manter o modelo de resposta atual de `opportunities` (lista de cards) e registrar falhas como entradas não retornadas (skip) para evitar cartões ambíguos.

## Risks / Trade-offs

- [Risco] Provider lento ainda pode continuar executando em background após timeout.
  - [Mitigação] O endpoint retorna antes, mantendo timeouts curtos; threads remanescentes só afetam recursos pontualmente e o limite de workers é pequeno.
- [Risco] Ajustar `4h` para stocks muda comportamento existente para erro de timeframe inválido.
  - [Mitigação] Cobertura de regressão no teste de integração para validar fluxo explícito (`stock 4h` agora via Yahoo).
- [Risco] Timeout agressivo pode marcar providers legítimos como falha em rede lenta.
  - [Mitigação] Tempo configurável por variável (`OPPORTUNITIES_FETCH_TIMEOUT_SECONDS`) e logs de causa para ajuste operacional.
