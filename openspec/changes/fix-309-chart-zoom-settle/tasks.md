## 1. Viewport settled

- [x] 1.1 Prop `viewportReady` + apply default só uma vez por key quando ready
- [x] 1.2 ChartModal passa `viewportReady={!loading && !analysisTradesLoading}`
- [x] 1.3 Inicializar `analysisTradesLoading=true` antes do primeiro effect de análise
- [x] 1.4 Fixar altura desktop do canvas com limites para eliminar reflow assíncrono
- [x] 1.5 Limitar a espera da análise e liberar loading com fallback em timeout

## 2. Wheel scoped

- [x] 2.1 Mover listener de wheel de `shellRef` para `chartRef`

## 3. Validação

- [x] 3.1 Atualizar teste de contrato + E2E zoom
- [x] 3.2 OpenSpec validate
- [x] 3.3 Cobrir contrato do estado inicial, timeout, range pós-merge e altura desktop estável
- [x] 3.4 Rodar testes focados, build e Playwright visual na branch
- [x] 3.5 Após integração, executar restart DEV e repetir o fluxo de zoom no bundle servido
