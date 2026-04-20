# Review PT-BR — remover /signals/onchain

## Resumo

- Projeto: `crypto`
- Change ID: `remover-signals-onchain`
- Objetivo: remover a capability `/signals/onchain` de forma completa e segura

## O que foi definido

- A remoção cobre rota, navegação, permissões, integrações internas e referências conhecidas.
- Não haverá tela substituta, redirect temporário ou redesign nesta change.
- O foco é retirar a funcionalidade sem gerar regressão nas demais áreas de signals.

## Decisão necessária

- Não há decisão pendente do Alan para fechar o escopo do PO.
- Próxima validação é operacional: confirmar na implementação todos os pontos de entrada conhecidos.

## Tradeoffs

- Prós: simplifica o produto, reduz manutenção e elimina fluxo indesejado.
- Contras: qualquer link salvo ou integração esquecida pode gerar ruído pós-remoção.

## Próximo passo

- Próximo owner recomendado: `DEV`
- Próxima ação: implementar a remoção completa e entregar evidência para QA validar navegação, rota e referências impactadas.

## Artefatos

- `openspec/changes/remover-signals-onchain/proposal.md`
- `openspec/changes/remover-signals-onchain/review-ptbr.md`
- `openspec/changes/remover-signals-onchain/tasks.md`
