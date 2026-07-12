## Context

O manifesto canônico já contém indicadores, parâmetros funcionais, cores e séries, mas essas informações ficam abaixo do gráfico e fora da leitura inicial. O título atual mostra apenas estratégia, timeframe, velas e candle de referência. A solução deve funcionar para qualquer indicador descrito pelo manifesto, sem regras específicas por estratégia.

## Goals / Non-Goals

**Goals:**

- Mostrar configuração funcional no primeiro olhar, em desktop e mobile.
- Derivar o resumo do manifesto canônico para suportar indicadores atuais e futuros.
- Exibir nome, configuração, cor e valor contextual de cada indicador.
- Preservar proteção de código-fonte e diagnósticos internos.

**Non-Goals:**

- Expor expressões proprietárias completas, código ou parâmetros internos não usados na decisão.
- Alterar cálculo, parâmetros ou resultado das estratégias.
- Criar configuração manual dentro do gráfico.

## Decisions

### 1. Manifesto canônico como única fonte

O resumo será derivado de `strategy_transparency.indicators[].parameters` e `effective_parameters`, nunca do nome da estratégia. Assim EMA, SMA, RSI, MACD, Bollinger, ADX, ATR, volume e novos indicadores seguem o mesmo contrato.

### 2. Resumo compacto no cabeçalho

O subtítulo terá uma segunda linha/elemento de configuração, com chips coloridos e nomes legíveis. Em telas estreitas poderá quebrar linha sem esconder conteúdo.

### 3. Transparência funcional não é segredo

Períodos, thresholds, direção e risco necessários para interpretar o sinal serão públicos a traders autorizados. Código, aliases diagnósticos, credenciais e controles de mutação permanecem protegidos.

### 4. Fallback explícito

Se o manifesto não comprovar indicadores, a UI mostrará “Configuração dos indicadores indisponível” em vez de omitir silenciosamente ou inventar valores.

## Risks / Trade-offs

- [Muitos indicadores podem deixar o cabeçalho denso] → chips responsivos e resumo por indicador.
- [Parâmetros técnicos podem ter nomes pouco claros] → usar formatadores PT-BR existentes e rótulo do indicador.
- [Manifesto legado incompleto] → fallback explícito e testes de catálogo para impedir recorrência.
