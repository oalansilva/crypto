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
- [ ] Definir estado visual read-only/disabled do campo Portfólio no Monitor para `cryptomoeda` com Binance configurada
- [ ] Definir copy/mensagem contextual indicando que o valor vem da Carteira/Binance
- [ ] Definir fallback visual para carteira vazia, indisponível ou sem posição elegível

## DEV
- [ ] Identificar de forma canônica quando o ativo do Monitor é do tipo `cryptomoeda`
- [ ] Detectar condição de Binance configurada para ativar a regra derivada
- [ ] Tornar o campo/opção Portfólio somente leitura na UI quando a regra estiver ativa
- [ ] Popular o valor exibido a partir da Carteira/ativos comprados do usuário
- [ ] Preservar comportamento atual para ativos não cripto ou sem Binance configurada
- [ ] Bloquear no backend/regra de negócio qualquer alteração manual de Portfólio quando a regra derivada estiver ativa
- [ ] Tratar fallback para ausência de posição elegível, erro de sincronização ou carteira indisponível

## QA
- [ ] Validar cenário `cryptomoeda` + Binance configurada + carteira disponível
- [ ] Validar cenário `cryptomoeda` + Binance configurada + carteira vazia/indisponível
- [ ] Validar cenário de ativo não `cryptomoeda` sem bloqueio indevido
- [ ] Validar que payload manual não sobrescreve Portfólio quando a regra derivada estiver ativa

## Critérios de conclusão
- [ ] Portfólio fica bloqueado apenas no escopo correto
- [ ] Valor exibido vem da Carteira quando a regra estiver ativa
- [ ] Existe feedback claro em fallback/erro
- [ ] Backend impede alteração manual indevida
