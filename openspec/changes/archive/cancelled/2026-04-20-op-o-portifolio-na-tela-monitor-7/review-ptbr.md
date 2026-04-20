---
spec: openspec.v1
id: op-o-portifolio-na-tela-monitor-7
title: Review PT-BR - Opção Portifolio na tela Monitor
card: "#110"
change_id: op-o-portifolio-na-tela-monitor-7
stage: PO
status: draft
owner: Alan
created_at: 2026-04-19
updated_at: 2026-04-19
---

# Review PT-BR: Opção Portifolio na tela Monitor

**Card:** #110 | `op-o-portifolio-na-tela-monitor-7`

## Resumo

Fechei a regra de produto assim:
- vale apenas para ativos do tipo **criptomoeda**
- com **Binance configurada**, o campo/opção **Portfólio** no Monitor fica **somente leitura**
- o valor exibido deve vir da **Carteira** com base nos ativos comprados do usuário
- para ativos que não são cripto, o comportamento atual continua

## Decisão de produto

Para destravar DEV e QA sem ambiguidade:
1. o gatilho da etapa é **Binance configurada**
2. o Portfólio vira **campo derivado**, sem edição manual nessa condição
3. se a carteira estiver vazia ou indisponível, o campo continua bloqueado e a UI precisa mostrar feedback claro
4. a proteção não pode ficar só na interface, precisa existir também na regra de backend

## Principais cuidados

- não aplicar o bloqueio em ativos não cripto
- evitar divergência entre o valor exibido no Monitor e a Carteira
- definir mensagem clara para estado sem posição elegível ou erro de sincronização

## Próximo passo

**DESIGN** deve detalhar o comportamento visual do campo read-only e o fallback de mensagem antes da implementação.

## Ação necessária

- **Alan:** nenhuma agora
- **Scrum Master / Orchestrator:** pode seguir com handoff para DESIGN
- **DESIGN:** definir estado visual e mensagem contextual
- **DEV:** aguardar handoff de design e implementar regra derivada em UI + backend
- **QA:** usar a matriz cripto vs não cripto e carteira disponível vs indisponível na validação futura
