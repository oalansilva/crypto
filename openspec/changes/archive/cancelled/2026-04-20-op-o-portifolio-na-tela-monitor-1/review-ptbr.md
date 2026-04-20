# Review PT-BR

## Resumo
- Na tela Monitor, ativos do tipo criptomoeda com conexão Binance configurada não poderão ter o campo Portfólio alterado manualmente.
- Nesse cenário, o valor exibido deve vir automaticamente da Carteira do usuário.
- Para ativos não cripto, ou para usuários sem Binance configurada, o comportamento atual permanece editável.

## Decisão necessária
- Validar a regra de produto de travar o Portfólio para cripto quando houver Binance configurada, usando a Carteira como fonte única do valor exibido.

## Trade-offs principais
- **Pró:** elimina divergência entre Monitor e Carteira para usuários com Binance.
- **Pró:** reduz configuração manual e aumenta previsibilidade do comportamento.
- **Contra:** remove flexibilidade de override manual nesse cenário.
- **Risco a observar:** se o estado de "Binance configurada" ou os dados da Carteira estiverem inconsistentes, o usuário pode ver o campo travado sem entender o motivo.

## Critérios-chave para seguir
- Backend e UI precisam aplicar a mesma restrição.
- A UI precisa explicar claramente que o valor vem automaticamente da Carteira.
- A regra vale somente para ativos do tipo criptomoeda na tela Monitor.

## Próximo passo
- Seguir para DESIGN, com protótipo do estado bloqueado e da mensagem explicativa antes de qualquer avanço para aprovação do Alan.
