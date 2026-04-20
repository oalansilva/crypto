# Design

## Contexto
O bug do Monitor nao pede redesign amplo, mas exige um tratamento visual que elimine qualquer falso positivo de `EXIT` quando timeframe, candle ou frescor nao estiverem alinhados.

## Direcao
Introduzir um estado visual `INCONCLUSIVO` sincronizado entre badge, marcador de grafico e bloco de contexto.

O objetivo e simples:
- `EXIT` so existe quando tudo fecha 100%
- qualquer divergencia cai para um estado neutro e explicado
- o fallback nao pode parecer uma quase-venda

## Regras visuais

### EXIT confirmado
Usar o azul atual somente quando todos os itens abaixo forem verdadeiros:
- estado resolvido = `EXIT`
- timeframe exibido = timeframe do sinal
- candle exibido = candle de referencia do sinal
- payload fresco
- badge, marcador e contexto apontam para o mesmo estado

### INCONCLUSIVO
Usar estado neutro em qualquer um destes casos:
- timeframe divergente
- candle divergente
- payload stale
- campos ausentes
- conflito entre badge, grafico e metadado
- loading sem confirmacao final

## Linguagem visual
- `EXIT confirmado`: azul ja existente, reservado exclusivamente para saida valida
- `Holding`: verde ja existente
- `INCONCLUSIVO`: fundo ardósia/zinco, texto claro, borda discreta, sem cor de acao
- `Motivo do bloqueio`: chips neutros com baixo contraste cromatico e alta legibilidade textual

## Comportamento esperado
- badge principal em caixa alta curta: `INCONCLUSIVO`
- mensagem principal objetiva: `EXIT bloqueado ate alinhar contexto`
- marcador neutro no grafico, sem seta de saida
- bloco de contexto com `timeframe`, `candle` e `freshness`
- linha de motivo explicando por que o estado foi bloqueado

## Rejeicoes explicitas
- nao usar `EXIT` com tooltip de aviso
- nao esconder o problema removendo contexto
- nao usar a mesma aparencia para loading e saida confirmada
- nao reaproveitar azul de confirmacao em cenarios ambiguos

## Notas para DEV
- o marcador neutro deve substituir a seta de saida quando `isUncertain = true`
- o contexto minimo visivel para QA deve expor timeframe, candle e frescor
- o azul de `EXIT` nao pode aparecer em nenhum fallback

## Notas para QA
Validar que:
- nenhum caso inconclusivo usa rotulo `EXIT`
- nenhum caso inconclusivo desenha seta acima do candle
- o motivo do bloqueio aparece no card
- a combinacao badge + grafico + contexto e deterministica com o mesmo payload
