# Change Proposal: Lab - Salvar Template Apenas se Aprovado pelo Trader

## Why

Atualmente, o Lab cria e salva templates no banco de dados `combo_templates` durante o fluxo de desenvolvimento, mesmo quando a estratégia ainda está em draft ou é rejeitada pelo trader. Isso resulta em:

1. **Poluição do banco de dados**: Templates inválidos ou descartados permanecem persistidos
2. **Confusão na UI**: A tela `/combo/select` exibe templates que nunca foram aprovados
3. **Overhead de manutenção**: É necessário limpar manualmente templates obsoletos
4. **Semântica incorreta**: O banco `combo_templates` deveria conter apenas estratégias validadas e aprovadas para uso

A solução é **só persistir o template no banco quando o trader aprovar explicitamente**. Templates em draft ou rejeitados devem ser mantidos apenas em memória ou em estruturas temporárias (ex: `lab_runs` logs), não no `combo_templates`.

## What Changes

Modificar o fluxo do Lab para:
1. Durante desenvolvimento: Template existe apenas no contexto da run do Lab (não salvo no banco)
2. Quando aprovado pelo trader: Copiar/criar o template no `combo_templates` com nome apropriado
3. Quando rejeitado: Descartar - nada é salvo no banco permanente

## Success Criteria

- [ ] Templates de draft não aparecem na tela `/combo/select`
- [ ] Templates só são criados em `combo_templates` após aprovação do trader
- [ ] Fluxo de rejeição não deixa resíduos no banco
- [ ] Templates aprovados são corretamente nomeados e persistidos
