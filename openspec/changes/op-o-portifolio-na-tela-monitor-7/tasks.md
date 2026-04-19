---
spec: openspec.v1
id: op-o-portifolio-na-tela-monitor-7
title: Tasks - Opção Portifolio na tela Monitor
card: "#110"
change_id: op-o-portifolio-na-tela-monitor-7
stage: PO
status: draft
owner: Alan
created_at: 2026-04-19
updated_at: 2026-04-19
---

# Tasks: Opção Portifolio na tela Monitor

**Card:** #110 | `op-o-portifolio-na-tela-monitor-7`

- [x] PO: Opção Portifolio na tela Monitor

## DESIGN
- [ ] T1: Definir estado visual read-only/disabled do campo Portfólio no Monitor para `cryptomoeda` com Binance configurada
- [ ] T2: Definir copy/mensagem contextual indicando que o valor vem da Carteira/Binance
- [ ] T3: Definir fallback visual para carteira vazia, indisponível ou sem posição elegível

## DEV
- [ ] T4: Identificar de forma canônica quando o ativo do Monitor é do tipo `cryptomoeda`
- [ ] T5: Detectar condição de Binance configurada para ativar a regra derivada
- [ ] T6: Tornar o campo/opção Portfólio somente leitura na UI quando a regra estiver ativa
- [ ] T7: Popular o valor exibido a partir da Carteira/ativos comprados do usuário
- [ ] T8: Preservar comportamento atual para ativos não cripto ou sem Binance configurada
- [ ] T9: Bloquear no backend/regra de negócio qualquer alteração manual de Portfólio quando a regra derivada estiver ativa
- [ ] T10: Tratar fallback para ausência de posição elegível, erro de sincronização ou carteira indisponível

## QA
- [ ] T11: Validar cenário `cryptomoeda` + Binance configurada + carteira disponível
- [ ] T12: Validar cenário `cryptomoeda` + Binance configurada + carteira vazia/indisponível
- [ ] T13: Validar cenário de ativo não `cryptomoeda` sem bloqueio indevido
- [ ] T14: Validar que payload manual não sobrescreve Portfólio quando a regra derivada estiver ativa

## Critérios de conclusão
- [ ] T15: Portfólio fica bloqueado apenas no escopo correto
- [ ] T16: Valor exibido vem da Carteira quando a regra estiver ativa
- [ ] T17: Existe feedback claro em fallback/erro
- [ ] T18: Backend impede alteração manual indevida
