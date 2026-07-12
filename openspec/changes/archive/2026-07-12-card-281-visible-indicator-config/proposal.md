## Why

O gráfico informa estratégia, timeframe e candles, mas pode ocultar os períodos e limites que geram o sinal. Sem essa configuração operacional, o trader não consegue interpretar nem conferir a decisão exibida.

## What Changes

- Exibir no cabeçalho um resumo legível dos indicadores e parâmetros efetivos de toda estratégia.
- Exibir para cada indicador seu tipo, período/configuração, cor, função e valor no candle selecionado.
- Tornar visíveis a traders autorizados os parâmetros funcionais necessários para interpretar entrada, saída e risco, inclusive em estratégias protegidas.
- Manter código-fonte, credenciais, diagnósticos internos e regras proprietárias desnecessárias protegidos.
- Cobrir médias, osciladores, momentum, volatilidade, volume e futuros indicadores derivados do manifesto canônico.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `strategy-transparency`: exigir visibilidade universal e legível da configuração funcional de indicadores no gráfico.
- `strategy-secret-visibility`: distinguir configuração operacional pública de segredos internos.

## Impact

- Backend: geração e serialização do manifesto de transparência para estratégias públicas/protegidas.
- Frontend: cabeçalho e legenda do gráfico em desktop/mobile.
- Testes: contratos backend e Playwright do modal.
- Runtime: DEV, sem mudança de parâmetros ou lógica de execução.
