# Review PT-BR

## Resumo
O problema foi enquadrado como bug de semântica funcional do Monitor, não só de renderização. O sinal de `EXIT` no gráfico só pode aparecer quando a regra de saída estiver confirmada no contexto atual, com a mesma fonte de verdade para badge, marcador e metadados.

## Decisão necessária
Aprovar a direção de produto abaixo:
- qualquer inconsistência, stale, loading ou conflito deve cair para estado neutro/inconclusivo
- `EXIT confirmado` não pode continuar aparecendo com contexto divergente

## Trade-off principal
- **Opção recomendada:** fallback neutro em qualquer inconsistência, mais seguro e validável
- **Opção descartada:** manter EXIT com aviso textual, porque o visual continuaria induzindo erro

## Escopo do pacote PO
- alinhar regra funcional e representação visual do sinal de saída
- exigir uma única resolução de estado para gráfico, badge e contexto
- bloquear EXIT quando timeframe/candle/frescor não baterem
- exigir contexto mínimo visível para QA validar

## Risco relevante
A API canônica do workflow retornou este card/change como `Canceled`, em divergência com o contexto recebido do item claimado em `PO`. Registrei essa divergência no handoff para o Scrum Master/runtime reconciliar.

## Próximo passo recomendado
- **Próximo owner:** DESIGN, se houver ajuste visual para estado neutro/inconclusivo; caso contrário, DEV pode implementar diretamente após saneamento do estado canônico do card.
- Se for UI, o protótipo continua obrigatório antes de qualquer avanço para approval.
