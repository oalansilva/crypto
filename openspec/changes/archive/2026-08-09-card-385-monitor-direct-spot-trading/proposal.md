## Why

O Monitor hoje apoia a decisão, mas obriga o usuário a sair do Cripto Farol para executar uma compra ou liquidar uma posição na Binance. O card #385 reduz essa ruptura com um fluxo Spot explícito e seguro: compra por valor em USDT e venda integral a mercado.

## What Changes

- Adicionar ao Monitor ações transacionais de compra e venda para pares cripto cotados em USDT.
- Permitir compra Spot `MARKET` informando quanto USDT usar, enviada à Binance como `quoteOrderQty`.
- Permitir venda Spot `MARKET` sempre para 100% do saldo `free` do ativo base, arredondado conforme os filtros do símbolo.
- Exigir revisão e confirmação explícita antes de enviar uma ordem real, com símbolo, lado, valor/quantidade, saldo e aviso de variação de preço.
- Usar exclusivamente as credenciais Binance do usuário autenticado com permissão Spot Trading, sem fallback global e sem permissão de saque.
- Validar filtros e saldos, impedir submissões duplicadas, reconciliar resultados incertos e exibir estados de sucesso, parcial, rejeição e falha sem vazar dados sensíveis.
- Atualizar a orientação de credenciais em Meu Perfil para cobrir compra, venda e proteção Spot no Monitor.

## Capabilities

### New Capabilities
- `monitor-direct-spot-trading`: Compra Spot por valor em USDT e venda Spot integral a mercado diretamente no Monitor, com confirmação, idempotência, reconciliação e estados operacionais seguros.

### Modified Capabilities
- `user-preferences-binance-credentials`: A orientação de permissão Spot Trading passa a cobrir compra e venda direta, além da proteção de stop existente.

## Impact

- Frontend do Monitor e do modal/gráfico, com nova superfície transacional responsiva e acessível.
- Backend FastAPI, serviço de ordens assinadas Binance Spot e integração com saldos/filtros do símbolo.
- Credenciais Binance por usuário, copy de Meu Perfil e mensagens de permissão.
- Testes unitários/de rota, contrato da integração Binance, Playwright funcional/visual e validação em DEV sem enviar ordens reais fora de um ambiente explicitamente controlado.
