## Why

Favoritos e Monitor ainda apresentam identidades genéricas e, em alguns caminhos, tratam os detalhes da estratégia como copy protegida. Isso impede que o trader autenticado entenda e audite os indicadores, regras, direção e risco que já determinam a decisão exibida. O card #361 alinha a apresentação ao comportamento executado sem alterar a lógica de sinais.

## What Changes

- Revisar o catálogo de nomes e descrições públicas para que cada estratégia ativa seja distinta, específica e coerente com seus indicadores, direção e timeframe.
- Expor na superfície autenticada de Favoritos e Monitor o detalhe técnico efetivo já disponível no manifesto: indicadores, parâmetros, regras de entrada/saída, filtros, thresholds e stops quando existirem.
- Remover o fallback de copy genérica/ofuscada para o trader autenticado, mantendo fora do contrato apenas segredos, credenciais, código-fonte e dados diagnósticos.
- Fazer Favoritos e Monitor consumirem a mesma identidade e o mesmo nível de detalhe, com estados explícitos quando a configuração confiável estiver indisponível.
- Atualizar testes de catálogo, display name, descrição, detalhe técnico e equivalência entre as duas telas.

## Capabilities

### New Capabilities

<!-- Nenhuma capacidade nova; o card amplia uma capacidade já versionada. -->

### Modified Capabilities

- `strategy-transparency`: tornar a identidade e o detalhe técnico do manifesto transparentes e consistentes nas superfícies autenticadas de Favoritos e Monitor, preservando a exclusão de segredos e a regra executada.

## Impact

- Backend: `strategy_descriptions`, `strategy_transparency`, schemas/serialização e testes de catálogo.
- Frontend: componentes e utilitários de detalhe de estratégia em Favoritos, Monitor e modais/gráficos compartilhados.
- API: evolução do payload autenticado de transparência; sem mudança de regras de entrada, saída, backtest ou sinais.
- UI impact: affected. O shell existente permanece; o delta é a hierarquia de identidade e a seção/painel responsivo de detalhes técnicos.
