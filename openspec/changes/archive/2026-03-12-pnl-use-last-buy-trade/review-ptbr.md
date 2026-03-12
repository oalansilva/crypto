## Resumo para revisão

Objetivo desta change:
- ajustar o PnL da tela `/external/balances` para **não fazer média das compras antigas**.

Nova regra:
- para cada moeda, o preço de compra de referência deve considerar **somente o último trade de compra** daquela moeda.

Exemplo:
- se houve compras a 10, 12 e 15, o sistema não deve usar média.
- deve usar **15** como referência de compra para o PnL atual.

Fora de escopo:
- mudar modelo para FIFO/LIFO;
- refazer PnL realizado;
- mexer em outras telas sem necessidade.

Critério de aceite:
- `/external/balances` passa a mostrar/calcular o PnL com base apenas no último trade de compra da moeda.
