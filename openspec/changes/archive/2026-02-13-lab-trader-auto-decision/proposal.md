# Change Proposal: lab-trader-auto-decision

## Why

Atualmente o sistema para em `needs_user_confirm` esperando aprovação humana do trader, mesmo tendo um agente "trader" LLM disponível. Isso cria um gargalo manual desnecessário que interrompe o fluxo autônomo do Lab.

O agente trader deve avaliar a **estratégia** (resultado do backtest, métricas) e dar o veredito (approved/rejected/needs_adjustment) automaticamente. Quando aprovado, a estratégia e o template devem ser salvos nos favoritos sem intervenção humana.

## What

Modificar o fluxo do LangGraph no Lab para:
1. Remover a pausa `needs_user_confirm` antes do trader_validation
2. Agente trader LLM avalia o resultado da estratégia e retorna veredito automaticamente
3. Quando **approved**: salvar estratégia nos favoritos + salvar template automaticamente
4. Quando **rejected**: finalizar run
5. Quando **needs_adjustment**: voltar para dev_implementation automaticamente

## Success Criteria

- [ ] Lab executa trader_validation automaticamente sem parar para confirmação humana
- [ ] Agente trader avalia resultado da estratégia (métricas) e retorna veredito via LLM
- [ ] Quando approved: estratégia salva nos favoritos automaticamente
- [ ] Quando approved: template salvo automaticamente
- [ ] Quando rejected: run finaliza sem salvar
- [ ] Quando needs_adjustment: volta para dev_implementation automaticamente
- [ ] Não há estado `needs_user_confirm` relacionado ao trader review
