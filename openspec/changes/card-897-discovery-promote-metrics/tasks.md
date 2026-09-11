# Tasks — card-897-discovery-promote-metrics

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Promoção e GET

- [x] 1.1 — Promoção da Descoberta copia Sharpe, negócios, win rate, retorno e Max DD (e PF se existir) do snapshot para as chaves que a grade já lê, sem apagar origem/varredura/result id/identity/snapshot.
- [x] 1.2 — GET de favoritos já promovidos da Descoberta cujo snapshot já tem os números (inclui `#193`) devolve essas chaves preenchidas, sem exigir nova promoção.
- [x] 1.3 — Favorito combo-saved: contrato de GET/grade inalterado.

## 2. Persistência do terceiro backtest

- [x] 2.1 — Regenerar/persistir trades nas velas atuais NÃO sobrescreve as chaves do snapshot que a grade e o resumo lêem.
- [x] 2.2 — Abrir o gráfico e voltar à grade: Sharpe/Trades/Win%/Return/Max DD da linha Descoberta permanecem os do snapshot.

## 3. Análise

- [x] 3.1 — Resumo de `/combo/results` (retorno, acerto, Max DD, negócios) de favorito da Descoberta vem do snapshot; Max DD não é «Indisponível» se o snapshot tem Max DD.
- [x] 3.2 — Se a lista de operações for das velas atuais, renderizar etiquetas visíveis e distintas: resumo = janela de treino da Descoberta; lista = velas atuais.

## 4. UI e evidência

- [x] 4.1 — Grade `/favorites` alinhada ao proto (`index.html`): linha Descoberta preenchida, linha combo-saved igual à de hoje, landmarks intactos.
- [x] 4.2 — Análise alinhada ao proto extra (`analise.html`): resumo snapshot + janela rotulada.
- [x] 4.3 — Testes: promoção flatten, GET `#193`/já promovidos, persistência não sobrescreve, resumo/etiqueta; Playwright `/favorites` e `/combo/results` desktop+mobile contra o proto.
- [x] 4.4 — `openspec verify` desta change.
