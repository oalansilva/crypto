## Why

Reduzir a espera da Descoberta preservando a busca integral e os resultados do motor entregue em #945. O briefing abaixo é cópia literal do issue #1091.

## Problema

O operador da Descoberta espera a otimização de cada combinação para comparar candidatos e decidir quais estratégias acompanhar. Mesmo após a aceleração entregue em #945, há trabalho repetido no motor que aumenta essa espera sem acrescentar qualidade à análise.

Um experimento isolado de 12/10/2026, sobre o motor atual, mediu **34,19 s → 24,91 s de mediana (−27,1%)** combinando cache da identificação dos dados, compilação dos loops numéricos com Numba e cache por indicador. Foram mantidas as **21.210 tentativas** e o resultado completo permaneceu idêntico no cenário principal. O ganho adicional sobre o cache da identificação dos dados, sozinho, foi de aproximadamente 8%.

Esta história evolui o motor entregue em #945, que está em **Pronto**; não reabre aquele card nem reutiliza sua antiga meta de 10×.

## História

**Como** operador da Descoberta,
**quero** que as otimizações terminem mais rápido, avaliando as mesmas combinações e preservando os mesmos resultados,
**para** comparar e acompanhar estratégias com menos espera, mantendo a confiança nos parâmetros escolhidos, nas operações simuladas e na validação fora do treino.

## Entra

- Reduzir o tempo de otimização no caminho comum da Descoberta, mantendo a mesma análise e os mesmos resultados para o operador. A abordagem experimental escolhida e seus limites de evidência estão registrados abaixo; o detalhamento dos mecanismos pertence ao Design.
- Acelerar o processamento mantendo a busca completa: mesmos parâmetros candidatos, número de tentativas, rodadas, filtros, critérios de desempate, score e seleção de vencedores.
- Preservar os indicadores calculados pela TA-Lib, sinais, operações, custos, stops, métricas, Deep 15m, divisão treino/holdout, aquecimento dos indicadores e veredito GO/NO-GO. Preservar também o comportamento do fallback diário quando ele for aplicável.
- Aplicar a melhoria no motor compartilhado pelos consumidores existentes, sem criar um atalho exclusivo para um template ou modificar os contratos das telas/API.
- Garantir coerência e limite de memória dos caches. Reutilização exige dados, janela e parâmetros efetivos equivalentes; alterações nos candles ou separação treino/holdout não podem reaproveitar valores incorretos. Nenhuma tentativa pode modificar um resultado cacheado que outra tentativa utiliza.
- Medir separadamente execução aquecida e primeira execução com compilação JIT. Registrar versões compatíveis das dependências e preservar um caminho de reversão validado.

**Critérios de aceite**

- [ ] **Equivalência completa:** com os mesmos dados e configurações, a versão atual e a otimizada produzem os mesmos parâmetros vencedores, indicadores, sinais, lista de operações (datas, preços, lucro e motivo de saída), métricas de treino/holdout e veredito GO/NO-GO. A comparação não pode ocultar diferenças usando arredondamentos ou tolerâncias numéricas. Campos operacionais voláteis, se existirem, devem ser identificados explicitamente antes da comparação.
- [ ] **Busca intacta:** o cenário de referência continua executando as 21.210 tentativas, com as mesmas regras e zero falhas. Empates continuam determinísticos. A aceleração não escolhe estratégias usando informações do holdout.
- [ ] **Desempenho — ganho consistente, sem piso percentual:** por decisão de Alan, aceitar redução consistente do tempo do motor no cenário de referência mesmo abaixo de 25%, preservando resultados idênticos e a busca integral. **25% permanece como objetivo, não como piso obrigatório de aceite.** Comparar cinco execuções por versão, alternadas, no mesmo ambiente, com os mesmos dados locais, três workers e motor aquecido. A mediana da versão otimizada deve ser menor e a redução deve aparecer na maioria dos cinco pares de medições, sem depender apenas de uma execução favorável. Registrar os tempos individuais, a dispersão, a versão do código e as dependências. O valor absoluto de 24,91 s é evidência experimental, não SLA geral nem limite de tempo para CI.
- [ ] **Abrangência:** cobrir os 14 templates do catálogo usado na investigação, pelo menos dois símbolos e as direções long/short nos testes de equivalência do motor; incluir janelas distintas, cache fria/quente, sequência A → B → A, invalidação por mudança de dados, stops extremos, ausência de sinais e conflitos entre stop e saída por lógica. Documentar templates com avisos preexistentes, sem confundir igualdade de saída com validade da estratégia.
- [ ] **Cenários adicionais:** repetir a medição de Multi-MA/AAVE short e EMA+RSI/1INCH long, preservando o resultado completo e sem regressão de tempo sustentada nas repetições. O percentual de ganho pode variar entre estratégias.
- [ ] **Operação:** registrar custo de compilação inicial e consumo de memória; demonstrar caches limitados e ausência de contaminação entre execuções. Validar reversão e os consumidores existentes do motor, preservando os contratos de execução e apresentação.
- [ ] **Evidência durável:** versionar ou anexar, no artefato técnico do card, o benchmark reproduzível, a identificação dos dados e código de referência e os relatórios de tempo/equivalência. Não depender apenas dos arquivos temporários da investigação.

**Não entra**

- Optuna, busca aleatória, redução de tentativas ou de cobertura, alterações no grid, score, fórmulas, indicadores ou limiares GO/NO-GO.
- Pool persistente entre descobertas, aumento de concorrência do sweep ou mudança na quantidade de workers: são experimentos separados.
- Redesign da Descoberta, mudanças nos resultados exibidos, novos modos de busca ou novas configurações para o operador.
- Promessa de aceleração de 10× mantendo resultados idênticos, garantia de ganho percentual para todo cenário, melhoria de rentabilidade ou correção de problemas preexistentes das estratégias/métricas.
- Publicação em produção como parte da criação ou do refinamento desta história; entrega segue os gates normais do board.


## What Changes

- Cache seguro da identificação das janelas, compilação dos núcleos numéricos e avaliação condicionada do cache por indicador.
- Equivalência exata, benchmark pareado e reversão ao motor atual.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `combo-optimizer`: acrescentar contrato de aceleração incremental, equivalência completa, isolamento dos caches e evidência reproduzível do #1091.

## Impact

Motor compartilhado em combo_optimizer.py, combo_strategy.py e deep_backtest.py; dependências backend, testes e benchmark. Contratos públicos e telas preservados. Numba/llvmlite serão validados e pinados no Apply.
