# Review PT-BR

## Resumo
Card para ajustar a tela Monitor: para ativos do tipo criptomoeda, quando o usuário tiver conexão Binance configurada, a opção `Portfolio` não deve ser alterável manualmente. O estado deve vir da Carteira/holdings do usuário.

## Decisão necessária
Aprovar a direção de produto abaixo:
- para cripto com Binance conectada, `Portfolio` vira estado derivado e bloqueado
- a origem da verdade passa a ser holdings da carteira integrada
- para ativos não cripto, a regra nova não se aplica

## Trade-off principal
- **Opção recomendada:** travar o controle e derivar o estado da carteira, garantindo consistência
- **Opção descartada:** manter toggle manual com sugestão da Binance, porque continua permitindo divergência da origem real

## Escopo do pacote PO
- restringir a regra a ativos de tipo criptomoeda
- usar status de conexão Binance configurada para ativar a regra
- derivar `Portfolio` a partir dos ativos comprados/holdings da carteira integrada
- impedir edição manual enquanto Binance estiver conectada
- preservar o comportamento atual para ativos não cripto e para contas sem Binance
- deixar critérios de aceite objetivos para QA

## Riscos relevantes
- holdings desatualizados podem gerar percepção de inconsistência
- mapeamento incorreto entre ativo do Monitor e ativo da carteira pode travar estado errado
- sem copy/estado visual claro, o usuário pode não entender por que o controle ficou bloqueado

## Próximo passo recomendado
- **Próximo owner:** DESIGN
- Motivo: há mudança de comportamento visível em UI e o fluxo exige protótipo antes de qualquer avanço para approval
- A UI precisa deixar claro que, nesse cenário, o estado vem da carteira e não do toggle manual

## Artefatos
- `openspec/changes/op-o-portifolio-na-tela-monitor-5/proposal.md`
- `openspec/changes/op-o-portifolio-na-tela-monitor-5/review-ptbr.md`
- `openspec/changes/op-o-portifolio-na-tela-monitor-5/tasks.md`
