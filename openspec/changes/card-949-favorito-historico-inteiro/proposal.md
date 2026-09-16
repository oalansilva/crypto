## Why

Quem promove ou salva um favorito depois de uma validação walk-forward 70/30 fica com o favorito preso na janela de **treino** (testemunho: BTC 1d 17/08/2017 → 24/12/2023), embora o período esteja marcado como «todo». O 70/30 é a validação da busca; o favorito é a estratégia viva. Operar e analisar no pedaço de treino mente o tempo todo.

## What Changes

- Descoberta continua split 70/30: ranking, cobertura, Calmar da grelha e GO/NO-GO **não mudam**.
- Ao **promover** da Descoberta (período «todo») depois de 70/30: o favorito nasce no histórico inteiro (primeira vela → agora). Não herda o fim do treino.
- Ao **salvar** no Combo depois de 70/30: o favorito cobre o **período escolhido na tela, completo**. «Todo» → primeira vela → agora. 6 meses / 2 anos → esses 6 meses / 2 anos todos. **Não** amplia 6 meses ou 2 anos para «todo o histórico» (Q3).
- Depois de salvo neste card (Q1): lista, resumo, gráfico e atualização de Favoritos mostram os números **desse período completo**. O treino 70/30 fica na Descoberta como evidência da busca — **não** é o número da lista.
- O retrato da busca (janela de treino, Calmar da grelha, veredito) permanece consultável na Descoberta e **não** é apresentado como desempenho do período completo.
- Só **novos** promover / salvar (Q2). Quem já está na lista fica com a janela de treino até alguém salvar de novo.
- Preview do período completo no modal de promover **não entra**.

Fora: ranking 100%; acabar com o 70/30; migrar já salvos; mostrar treino na lista ou treino+completo lado a lado; #948 «Já existe»; Combo sem 70/30; gráfico/setas #917; Monitor; Telegram.

## Capabilities

### New Capabilities

- `favorite-chosen-period-after-walk-forward`: contrato visível de que promover/salvar **depois** de 70/30 grava e mostra o período escolhido na tela, completo (não a janela de treino); «todo» = primeira vela → agora; 6 meses / 2 anos = esses meses/anos, sem virar «todo»; só daqui pra frente; lista/resumo/gráfico/atualização leem esse período; a grelha Decidir permanece 70/30.

### Modified Capabilities

- `favorites`: lista, resumo, gráfico e atualização de um favorito **novo** deste card mostram o período escolhido completo e os números desse período — não o treino da grelha. Favoritos já salvos não mudam até um novo save (Q2).
- `discovery-promotion`: promover um candidato validado em 70/30 com período «todo» persiste histórico inteiro (primeira vela → agora), não as datas de treino. O retrato da varredura continua na Descoberta.
- `favorite-backtest-refresh`: a atualização de um favorito **novo** deste card corre e mostra o período completo gravado (aberto até hoje no «todo»), nunca o treino no lugar dele.

## Impact

- Frontend: `/favorites` (coluna Período + métricas da linha nova; resumo/gráfico abertos a partir da linha); `/combo/discovery` (grelha 70/30 intacta; promover deixa de copiar o fim do treino para o favorito); `/combo/results` (salvar depois de 70/30 e análise da linha nova). Rota viva do save Combo = `/combo/results` (`Salvar nos Favoritos`). `/combo/select` é só catálogo de templates — sem copy deste card. `/combo/configure` tem o toggle 70/30; Combo sem 70/30 não muda. Sem `/monitor`.
- Backend: persistência de `start_date`/`end_date`/`period_type` no promover e no save Combo pós-70/30; refresh do favorito novo usa essa janela. Sem backfill dos já salvos.
- Specs: nova `favorite-chosen-period-after-walk-forward`; delta em `favorites`, `discovery-promotion`, `favorite-backtest-refresh`. `walk-forward-oos-gate` intocado.
- Protótipo: clone `/favorites` (canónico) + extra `/combo/discovery` + extra `/combo/results` (análise do favorito novo «todo») + extra `/combo/results` (Combo 2 anos + 70/30 + salvar).
