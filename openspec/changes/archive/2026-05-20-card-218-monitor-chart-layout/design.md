## Context

O anexo do card #218 (`Estrategia.html`) propõe uma pagina de estrategia com:

- bloco principal claro para ativo/estrategia/status;
- grafico grande com toolbar compacta;
- paineis de leitura simples para risco, candle, distancia e historico;
- visual dark, bordas sutis, cards com raio moderado e foco em leitura operacional.

O produto atual abre o grafico em modal a partir do Monitor. A implementacao deve adaptar a linguagem visual do anexo para o modal existente, sem transformar o fluxo em uma pagina nova.

## Decisions

- Manter `ChartModal.tsx` como superficie de entrega do card, pois o pedido e especificamente o grafico do Monitor.
- Reusar `lightweight-charts`, estado de timeframe, cache de candles, marcadores e price lines existentes.
- Trocar a composicao visual para uma grade com grafico principal e rail lateral, inspirada no anexo, usando classes Tailwind ja aceitas no projeto.
- Exibir um resumo superior com ativo, nome publico da estrategia, status atual, timeframe e candle count.
- Exibir cards compactos de contexto abaixo do cabecalho: candle atual, distancia para proximo status, risco/stop e historico.
- Manter parametros/notes no rail lateral, com redacao protegida quando `isProtectedStrategy` for verdadeiro.
- Ajustar testes existentes para validar ausencia dos controles antigos e presenca das novas regioes.

## Risks

- O modal precisa continuar utilizavel em mobile; a grade deve colapsar para uma coluna.
- Mudanca visual nao pode quebrar os test ids usados pelos testes atuais.
- O novo layout nao pode reexpor parametros protegidos.

## Validation

- `openspec validate --all`.
- `npm --prefix frontend run build`.
- `npm --prefix frontend run test:e2e -- tests/e2e/monitor-mobile-cards-timeframe.spec.ts`.
- Inspecao visual via Playwright em desktop e mobile, garantindo grafico renderizado e controles acessiveis.
