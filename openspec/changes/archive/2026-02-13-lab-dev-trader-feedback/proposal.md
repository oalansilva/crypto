# Change Proposal: lab-dev-trader-feedback

## Why

Quando o Trader rejeita uma estratégia e solicita mudanças estruturais (ex: "mude para momentum", "adicione filtro de volume"), o Dev Senior atualmente NÃO recebe essas instruções no contexto quando faz retry. Ele só ajusta parâmetros (RSI 14→11) em vez de fazer as mudanças estruturais solicitadas pelo Trader.

Isso resulta em loops de otimização infrutíferos onde o Dev melhora in-sample mas degrada holdout, sem nunca implementar as mudanças solicitadas.

## What Changes

Modificar o fluxo do Lab para:
1. Quando `dev_needs_retry=True` e existe `trader_verdict` com `required_fixes`, passar essas instruções explicitamente para o Dev Senior
2. O Dev Senior deve receber uma mensagem customizada: "O Trader rejeitou e pediu: [lista de ajustes]"
3. O Dev deve implementar mudanças estruturais solicitadas, não apenas otimizar parâmetros

## Success Criteria

- [ ] Quando Trader rejeita com required_fixes, Dev recebe essas instruções no retry
- [ ] Mensagem do Dev inclui feedback do Trader explicitamente
- [ ] Dev implementa mudanças estruturais (ex: pivotar estratégia) quando solicitado
- [ ] Não apenas otimiza parâmetros existentes
