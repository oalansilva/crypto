## Context

Favoritos e Monitor já compartilham `StrategyChartSurface`, mas o componente recebe apenas candles, volume, marcadores e linhas de preço. O backend preserva `indicator_data` em alguns resultados como arrays sem timestamp, enquanto Monitor expõe apenas valores do último candle; a redaction herdada dos cards #106/#210/#220 remove parâmetros e indicadores de usuários comuns. O card #278 substitui essa decisão: comportamento funcional necessário para entender a estratégia passa a ser público, mas código, credenciais, diagnósticos e controles de mutação continuam protegidos.

`ComboTemplate.template_data` e a configuração efetivamente executada são as fontes técnicas existentes. O catálogo atual de copy é útil para identidade, porém contém fallback genérico, nomes internos (`WINNER`, `chain`, datas) e o drift conhecido `ema_rsi_fibonacci`, cujo template executa EMA + RSI sem Fibonacci.

## Goals / Non-Goals

**Goals:**

- Resolver uma identidade e um manifesto público únicos a partir da configuração/lógica efetiva da estratégia.
- Entregar o mesmo contrato em Favoritos e Monitor, com séries timestampadas apenas dos indicadores usados.
- Renderizar preço, volume e osciladores no gráfico compartilhado, com legenda/crosshair e alternativa textual acessível.
- Tornar ausência, incompatibilidade de timeframe e gaps explicitamente observáveis.
- Cobrir todos os templates ativos e impedir drift por testes tabulares.
- Seguir `DESIGN.md`: canvas `#0b0e11`, cards `#1e2329`, hairlines `#2b3139`, ação `#fcd535`, semântica trading verde/vermelho, raio 8px e densidade compacta.

**Non-Goals:**

- Alterar sinais, parâmetros, stops, ranking, performance ou motor de backtest.
- Implementar Fibonacci para preservar um nome incorreto.
- Expor código-fonte, credenciais, tokens, payloads diagnósticos ou APIs de mutação para usuário comum.
- Recalcular indicadores no navegador ou inferir séries por posição de array.

## Decisions

### 1. Manifesto público canônico no backend

Criar um serviço de transparência que combina identidade pública curada com `ComboTemplate.template_data`/configuração efetiva. O manifesto contém `strategy_key`, nome, descrição, parâmetros públicos relevantes, indicadores, função, painel/escala, participação (`entry`, `exit`, `risk`), referências e blocos lógicos não plotáveis.

O catálogo de copy deixa de ser fonte técnica. Metadados visuais por tipo de indicador (rótulo, cor, painel e função) podem ser registrados centralmente; aliases, parâmetros e participação vêm da configuração/lógica executada. Estratégia sem resolução específica retorna estado `unavailable`, nunca identidade genérica silenciosa.

Alternativa rejeitada: manter nomes/descrições no frontend. Isso permitiria drift entre API, Favoritos, Monitor e futuras superfícies.

### 2. Séries timestampadas na origem

Resultados novos armazenam cada ponto como `{timestamp_utc, value}` usando o índice temporal no momento em que o dataframe de execução gera `indicator_data`. A API normaliza, remove NaN/inf, aliases duplicados e colunas não declaradas no manifesto.

Arrays legados só podem ser migrados quando a origem comprovar timestamps correspondentes; caso contrário, a API marca a série como indisponível. O frontend nunca faz `zip` por índice com candles.

Alternativa rejeitada: recalcular EMA/SMA no browser. Isso recriaria apenas parte da lógica, divergiria do backtest e não cobriria RSI/ADX/ROC/MACD/ATR.

### 3. Um contrato para Favoritos e Monitor

Adicionar `strategy_transparency` ao payload de favorito e ao resultado de trades/análise. Monitor usa o mesmo payload canônico do favorito quando há `favorite_id`; sem série compatível, mostra o manifesto e um estado explícito. `is_strategy_protected` continua protegendo internals e ações administrativas, mas não remove o manifesto público.

### 4. Painéis sincronizados no gráfico compartilhado

`StrategyChartSurface` recebe o contrato canônico e cria:

- EMA/SMA/Bandas no painel de preço;
- média de volume no painel de volume;
- RSI/ADX/ROC em painel oscilador;
- MACD (linha, sinal, histograma) em painel próprio;
- ATR em painel de volatilidade.

Como `lightweight-charts` 4.2 não possui panes nativos, painéis inferiores usam instâncias separadas com range lógico e crosshair sincronizados. A legenda textual mostra valor do candle sob o cursor e usa o último valor por padrão. Linhas de referência têm rótulo, não dependem só de cor.

### 5. Timeframe e indisponibilidade são gates explícitos

Cada manifesto/série declara timeframe. Mudança de timeframe só mantém indicadores quando a API devolve série recalculada para esse timeframe; caso contrário, o gráfico limpa as séries e mostra mensagem em PT-BR. Dados do timeframe anterior nunca permanecem montados.

### 6. Acessibilidade e responsividade

Legenda e manifesto usam HTML semântico (`ul`/`dl`) como alternativa ao canvas; controles têm nome acessível, `aria-pressed` quando aplicável e alvo mínimo de 44px. Painéis usam scroll vertical no modal e altura compacta no mobile, sem scroll horizontal da página. O modal preserva Escape, restaura foco e mantém ordem de foco previsível.

### 7. Hidratação de favoritos legados no momento da análise

A listagem continua entregando somente o resumo do manifesto para evitar multiplicar milhares de pontos por todos os favoritos. Ao abrir uma análise, o frontend só usa o atalho local quando o manifesto cacheado já contém ao menos uma série `available` com pontos e timeframe compatível. Caso contrário, consulta `/favorites/{id}/trades`, cuja `_favorite_transparency` combina os candles e arrays persistidos quando os comprimentos/timestamps são comprováveis.

Isso corrige favoritos anteriores ao card sem recalcular indicadores no navegador, sem inflar a listagem e sem expor arrays diagnósticos.

### 8. Restart DEV deve atingir apenas serviços DEV

No source canônico `/srv/apps/dev/criptofarol/source`, `./restart` usa os serviços systemd `criptofarol-dev-backend.service` e `criptofarol-dev-frontend.service`, executa migrações/build antes do restart e valida `8004/5175`. O fluxo legado de portas `8003/5173` não pode ser acionado a partir do workspace DEV, pois essas portas pertencem a PROD neste host.

## Risks / Trade-offs

- [Templates gerados podem não existir no seed] → resolver primeiro pelo template/banco/configuração do favorito e marcar indisponível quando não houver fonte técnica confiável.
- [Resultados antigos têm arrays sem timestamp] → não inventar alinhamento; apresentar estado explícito e regenerar apenas em fluxo autorizado.
- [Muitos painéis podem dominar o mobile] → alturas compactas, agrupamento por painel e container vertical rolável.
- [Exposição funcional ultrapassar o necessário] → allowlist do manifesto; nunca serializar código, SQL, expressions cruas diagnósticas, credenciais ou payload completo do template.
- [Catálogo e execução voltarem a divergir] → teste tabular sobre templates ativos, verificação de aliases/params e proibição de fallback/nomes internos.
- [Mudança ampla causar regressão em markers/trades] → preservar `data-testid`, zoom, fontes de trades e E2E atuais de Favoritos/Monitor.

## Migration Plan

1. Introduzir tipos/serviço e campos opcionais, mantendo compatibilidade com consumidores atuais.
2. Corrigir o catálogo público e produzir matriz auditável dos templates ativos.
3. Gerar séries timestampadas em novos resultados e expor o contrato nas APIs.
4. Habilitar manifesto/indicadores no gráfico compartilhado e conectar Favoritos/Monitor.
5. Inverter testes herdados de ocultação, adicionar drift/a11y/E2E e validar desktop/mobile.
6. Rollback: desativar o consumo do campo opcional no frontend; payloads antigos permanecem aceitos.

## Open Questions

- Estratégias legadas sem template/configuração comprovável permanecerão com estado explícito `manifest_unavailable` até regeneração ou cadastro técnico; não haverá fallback inventado.
