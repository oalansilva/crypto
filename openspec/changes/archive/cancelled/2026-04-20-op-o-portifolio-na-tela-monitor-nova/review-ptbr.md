# Review PT-BR

## Resumo
Na tela Monitor, para ativos do tipo criptomoeda, quando o usuário tiver conexão Binance válida para leitura da carteira, a opção `Portfolio` não poderá ser alterada manualmente. O valor exibido deverá vir dos holdings atuais da carteira integrada.

## Decisão necessária
Aprovar a direção de produto abaixo:
- para cripto com Binance válida, `Portfolio` vira estado derivado e bloqueado
- a origem da verdade passa a ser a carteira integrada do usuário
- em falha de sincronização, o campo continua bloqueado com indicação de indisponibilidade/desatualização
- para ativos não cripto ou sem Binance válida, o comportamento atual é preservado

## Trade-off principal
- **Opção recomendada:** travar o controle e derivar o valor da carteira, garantindo consistência com a origem real
- **Opção descartada:** manter toggle manual com sugestão da Binance, porque ainda permitiria divergência

## Escopo do pacote PO
- limitar a regra a ativos classificados como criptomoeda
- ativar a regra apenas com conexão Binance válida para leitura
- derivar `Portfolio` a partir dos holdings atuais da carteira integrada
- impedir edição manual enquanto a regra estiver ativa
- manter o bloqueio mesmo sem posição, exibindo estado derivado inativo
- prever fallback visual para sync indisponível ou desatualizado
- preservar comportamento atual fora do cenário elegível

## Riscos relevantes
- atraso de sync pode mostrar estado derivado desatualizado
- mapeamento incorreto entre ativo do Monitor e ativo da carteira pode gerar bloqueio indevido
- sem explicação visual, o usuário pode interpretar o bloqueio como erro

## Próximo passo recomendado
- **Próximo owner:** DESIGN
- Motivo: há mudança visível de comportamento em UI, e o fluxo exige protótipo antes de seguir para approval
- **Status canônico atual:** card já consta em `DESIGN` na API do workflow

## Artefatos
- `openspec/changes/op-o-portifolio-na-tela-monitor-nova/proposal.md`
- `openspec/changes/op-o-portifolio-na-tela-monitor-nova/review-ptbr.md`
- `openspec/changes/op-o-portifolio-na-tela-monitor-nova/tasks.md`
