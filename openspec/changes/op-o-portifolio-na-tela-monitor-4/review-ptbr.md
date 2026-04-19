# Review PT-BR

## Resumo
Na tela Monitor, para ativos do tipo criptomoeda, quando o usuário tiver conexão Binance configurada, a opção Portfólio não deve ser editável manualmente. Nesse cenário, o valor deve vir da Carteira, de acordo com os ativos comprados do usuário.

## Decisão necessária
Validar o direcionamento de produto: para cripto com Binance conectada, Portfólio deixa de ser escolha manual e passa a ser derivado da Carteira.

## Tradeoffs principais
- Ganho: reduz inconsistência entre Monitor e posição real do usuário.
- Custo: exige tratamento claro de UI para campo bloqueado e para casos de carteira vazia/sem dados.
- Limite: a regra vale apenas para criptomoedas; demais ativos mantêm comportamento atual.

## Escopo aprovado pelo PO
- Travar edição manual de Portfólio apenas no Monitor para ativos cripto com Binance configurada.
- Usar Carteira como origem do valor nesse cenário.
- Preservar comportamento atual fora desse recorte.

## Riscos/atenções
- Estado vazio ou indisponível da Carteira precisa ser claro para o usuário.
- O bloqueio deve parecer intencional, não erro de interface.

## Próximo passo
Seguir para DESIGN após o pacote de artefatos do PO, porque a mudança tem impacto visível de UI e precisa de definição de experiência/indicação visual de campo não editável.