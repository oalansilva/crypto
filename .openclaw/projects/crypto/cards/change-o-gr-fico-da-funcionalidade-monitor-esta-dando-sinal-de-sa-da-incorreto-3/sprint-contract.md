# Contrato de homologacao

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta homologacao
O gráfico da funcionalidade Monitor esta dando sinal de saída incorreto

## Evidencias consolidadas
- Evidencia Playwright do BTC/USDT mostrando `WAIT` no card e no modal quando a estrategia e `1d` e o grafico exibido e `1h`.
- Mensagem explicita de bloqueio por mismatch de timeframe e, no modal, mismatch de candle atual.
- Evidencia de historico de `ENTRY`/`EXIT` visivel no modal do Monitor quando o timeframe exibido coincide com o timeframe da estrategia.
- Saida de build/typecheck sem erro.

## Decisao esperada
Aprovar para archive ou registrar blocker objetivo.

## Riscos conhecidos
- O endpoint canonico individual do card pode falhar intermitentemente; a board canonica continua sendo a referencia de coluna/status.
- O Playwright local continua falhando no launch do Chromium dentro do sandbox deste worker; a validacao automatizada deste turno precisou rodar fora do sandbox.
- A porta padrao do frontend pode estar ocupada no ambiente; a validacao deve usar a URL efetivamente alocada pelo Vite neste turno (`http://127.0.0.1:4175`).
