## Context

O modal `ChartModal` calcula o badge por `resolveOpportunitySignal`. Hoje qualquer incerteza de candle/timeframe/entrada visivel força `effectiveSection = wait`, mesmo quando o payload do Monitor ja classificou o ativo como `HOLDING` ou `EXIT_SIGNAL`. O layout padrao `algorithmic` tambem oculta o painel lateral onde ficam contexto, risco e historico.

## Goals / Non-Goals

**Goals:**
- Preservar o estado principal do Monitor no modal para evitar `Compra` na lista e `Espera` no detalhe.
- Manter aviso de incerteza como explicacao contextual.
- Abrir o modal com contexto, risco/stop e historico visiveis.
- Cobrir regressao com teste E2E do fluxo de grafico.

**Non-Goals:**
- Nao alterar regra backend de sinal, recomendacao financeira ou payload de oportunidades.
- Nao redesenhar o modal completo.
- Nao mudar marcadores historicos quando o timeframe exibido nao for o da estrategia.

## Decisions

- Manter `section` resolvida pelo status mesmo quando `isUncertain=true`.
  - Racional: a incerteza deve explicar confianca/freshness, nao substituir a leitura principal aprovada pelo Monitor.
  - Alternativa considerada: desligar `requireCurrentCandleMatch` no modal. Rejeitada porque perderia a explicacao de divergencia de candle.
- Iniciar `ChartModal` em modo `compact`.
  - Racional: este modo ja contem `Signal Context`, `Risco / Stop` e `Historico de sinais`, reduzindo mudanca visual e reaproveitando componentes existentes.
  - Alternativa considerada: duplicar painel lateral no modo `algorithmic`. Rejeitada por maior risco de layout e duplicacao.

## Risks / Trade-offs

- [Risk] Testes antigos esperam `Espera` quando ha mismatch de candle.
  - Mitigation: atualizar a expectativa para estado principal consistente e mensagem de revisao visivel.
- [Risk] Modo compacto reduz area inicial do grafico em desktop.
  - Mitigation: preservar alternancia para `Algoritmica` e manter controles atuais.
