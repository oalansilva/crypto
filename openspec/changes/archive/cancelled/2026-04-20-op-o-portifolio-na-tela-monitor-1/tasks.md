# Tasks: Opção Portifolio na tela Monitor - 1

## PO Tasks
- [x] Definir a regra de produto para Portfólio automático em Monitor quando o ativo for criptomoeda e houver Binance configurada.
- [x] Delimitar escopo para manter o comportamento atual em ativos não cripto e em usuários sem Binance configurada.
- [x] Especificar critérios de aceite para bloqueio de edição, origem do valor e proteção contra bypass.
- [x] Registrar revisão executiva em PT-BR para decisão rápida.

## DESIGN Tasks
- [x] Criar protótipo do estado bloqueado do campo Portfólio na tela Monitor para ativos de criptomoeda com Binance configurada.
- [x] Definir texto explicativo visível informando que o valor do Portfólio é preenchido automaticamente pela Carteira.
- [x] Mostrar contraste entre os estados bloqueado e editável, cobrindo os cenários com e sem Binance configurada.
- [x] Garantir que o protótipo deixe claro que a regra vale apenas para criptomoedas.

## DEV Tasks
- [x] Detectar no Monitor se o ativo é do tipo criptomoeda e se o usuário possui conexão Binance configurada.
- [x] Preencher o valor de Portfólio a partir dos ativos da Carteira quando a regra de bloqueio estiver ativa.
- [x] Desabilitar a edição manual do campo Portfólio nesse cenário, preservando o comportamento atual nos demais casos.
- [x] Exibir mensagem explicativa informando a origem automática do valor.
- [x] Rejeitar no backend tentativas de alteração manual do Portfólio quando a regra estiver ativa, para evitar bypass por API.
- [x] Definir comportamento determinístico para casos em que a Carteira não retorne dados válidos, sem permitir inconsistência silenciosa.

## QA Tasks
- [ ] Validar que, para ativo de criptomoeda com Binance configurada, o campo Portfólio aparece bloqueado na tela Monitor.
- [ ] Validar que, nesse mesmo cenário, o valor exibido vem da Carteira do usuário.
- [ ] Validar que ativos não cripto continuam com o campo Portfólio editável.
- [ ] Validar que ativos de criptomoeda sem Binance configurada continuam com o campo Portfólio editável.
- [ ] Validar que a UI exibe texto explicativo claro sobre o preenchimento automático pela Carteira.
- [ ] Validar, com evidência funcional, que tentativas de alteração manual por backend/API são rejeitadas quando a regra estiver ativa.
