## Why

Quem promove um candidato da Descoberta chega em Favoritos sem Sharpe, Trades, Win%, Return e Max DD da grade, e no gráfico vê outro conjunto de números (terceiro backtest nas velas atuais). O operador acha que o favorito perdeu a qualidade ou que a promoção falhou. Incidente PROD 2026-09-11 no favorito `#193` (ALPHA/USDT · 1d · Long, `RS-B109ED2C80`).

## What Changes

- Promover a tier 3 deixa no objeto que a grade `/favorites` já lê (não só num envelope aninhado) Sharpe, negócios, win rate, retorno e Max DD do **snapshot da promoção**. Profit Factor entra se o resultado da Descoberta já o tinha.
- Varredura, result id, identity e o snapshot completo **não somem**.
- Favoritos **já promovidos** da Descoberta cujo snapshot já tem os números passam a mostrar esses números na grade — `#193` incluído. Não é preciso promover de novo (Q2=A).
- Abrir o gráfico **não apaga** da grade os números do snapshot nem os troca por outro backtest.
- Persistência de um terceiro backtest (rerrodar nas velas atuais) **não** substitui as chaves que a grade e o resumo lêem.
- O **resumo** da análise (retorno, acerto, Max DD, negócios) vem do snapshot. Max DD **não** aparece «Indisponível» se o snapshot tem Max DD (Q1=A).
- Se a lista de operações no gráfico continuar nas velas atuais, a **janela está rotulada** e distinta da janela do resumo — o operador não confunde 12 negócios atuais com os 30 da Descoberta.
- Favorito antigo salvo pelo combo (não Descoberta): a grade desses continua igual.

Fora: Calmar / ranking / NO-GO (#896); redesign da grade; reconstruir lista/gráfico na janela da Descoberta; combo-saved contract; Monitor; Telegram; recalcular varreduras antigas; mudar dedup/tier 3/idempotência salvo o necessário para os números aparecerem.

## Capabilities

### New Capabilities

- `discovery-favorite-metrics`: contrato visível da grade e da análise para favorito promovido da Descoberta — snapshot nas chaves que a grade já lê, leitura/backfill dos já promovidos (`#193`), resumo da análise a partir do snapshot, janela rotulada quando lista ≠ resumo.

### Modified Capabilities

- `discovery-promotion`: a promoção grava os números do snapshot no sítio que a grade lê, sem apagar origem/varredura/result id/identity/snapshot.
- `favorites-trade-regeneration`: persistir o terceiro backtest **não** sobrescreve as chaves do snapshot que a grade e o resumo lêem.
- `favorites`: a grade de Favoritos mostra os números do snapshot nos já promovidos da Descoberta; favorito combo-saved permanece no contrato atual.

## Impact

- Backend: promoção (`discovery_service` / persistência do favorito), GET de favoritos (flatten/leitura do snapshot já gravado), persistência em `GET /api/favorites/{id}/trades` quando regenera.
- Frontend: `/favorites` (grade lê as mesmas chaves de hoje, agora preenchidas); `/combo/results` aberto pelo ícone de gráfico (resumo do snapshot; etiqueta de janela quando a lista é das velas atuais).
- Specs canónicas: `discovery-promotion`, `favorites`, `favorites-trade-regeneration`; nova `discovery-favorite-metrics`.
- Sem mudança de Calmar, ranking da Descoberta, Monitor, Telegram, ou contrato de favorito salvo pelo combo.
