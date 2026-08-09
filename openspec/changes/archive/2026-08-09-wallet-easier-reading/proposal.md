## Why

A tabela de saldos da carteira usa fundo uniforme em todas as linhas, o que dificulta a leitura horizontal dos dados de cada ativo (valores, PnL e participação). Além disso, há textos descritivos redundantes que poluem a tela.

## What Changes

- Aplicar zebra striping (cores de fundo intercaladas) nas linhas da tabela de saldos da carteira no desktop, com tom sutil que preserve contraste, cores semânticas e hover.
- Remover a frase do subtítulo do header: "Saldos lidos da Binance Spot por chave API read-only. O Cripto Farol não solicita e-mail nem senha da Binance."
- Remover a nota técnica sob o título Balances: "Layout responsivo: tabela no desktop e cards no mobile."
- Remover o chip "Binance · read-only" do header da página (decisão de Alan de simplificar o status visual).
- Cards mobile permanecem inalterados (sem zebra).

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `external-balances`: adicionar requisito de apresentação legível da tabela (zebra) e remoção dos textos descritivos redundantes e do chip de status da página.

## Impact

- Frontend apenas: `frontend/src/pages/ExternalBalancesPage.tsx` (linhas da tabela, textos e chip).
- Sem mudança de API, backend, banco ou contrato de dados.
- Baseline do Playwright visual da tela de carteira precisará ser atualizada.
