# Review PT-BR

## Resumo
Enquadrei o card como ajuste de consistência de produto entre **Monitor** e **Carteira**. Para ativos do tipo criptomoeda, quando houver conexão Binance configurada, a opção `Portfolio` no Monitor não deve mais ser editável manualmente. O valor precisa vir da Carteira, usando os ativos realmente mantidos pelo usuário.

## Decisão necessária
Aprovar a direção de produto abaixo:
- Binance conectado vira fonte de verdade para `Portfolio` no Monitor em ativos crypto
- o controle fica travado/read-only nesses casos
- Monitor precisa explicar visualmente que o valor vem da Carteira/Binance

## Trade-off principal
- **Opção recomendada:** travar o campo e sincronizar com Carteira, garantindo consistência
- **Opção descartada:** permitir override manual com aviso, porque mantém divergência entre Monitor e Carteira

## Escopo do pacote PO
- aplicar a regra só para ativos classificados como criptomoeda
- manter edição manual quando não houver Binance conectado
- derivar o estado do `Portfolio` a partir da Carteira
- exigir fallback determinístico quando Binance estiver conectado mas holdings não puderem ser resolvidos
- exigir mensagem clara de campo sincronizado/bloqueado

## Risco relevante
O principal risco é travar ativos errados por classificação incorreta de tipo de ativo, ou deixar comportamento ambíguo quando a conexão Binance existir mas os holdings não estiverem disponíveis/frescos. Por isso o handoff pede fonte de verdade única, fallback explícito e feedback visual claro.

## Próximo passo recomendado
- **Próximo owner:** DESIGN, porque há mudança de comportamento visível no controle do Monitor e o protótipo continua obrigatório antes de qualquer avanço para approval.
- Depois do protótipo, DEV implementa o travamento e a sincronização com a Carteira.
