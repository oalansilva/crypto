Título: Scalp Jev: veredicto de todos os gates de entrada, origem da confiança, versão do modelo e faixa de toxicidade por ciclo
Card criado a partir da homologação do #1025 (23/09). É o **pré-requisito de #1029 e #1030**: sem ele não existe dado para calibrar nada.

Este card é **SEM-TELA** (backend/log; nada de UI, nada de painel); a homologação do #1025 (23/09) é a evidência de partida.

## Problema

Quem opera o scalp BTCUSDT não consegue saber por que cada ciclo foi recusado. A recusa por confiança acontece antes das outras e esconde o veredicto de custo, de regime e de toxicidade — então não existe dado para escolher nenhum limiar.

## História

Como operador do scalp Jev, quero que cada ciclo registre o veredicto de todas as regras de entrada e diga de onde veio cada número do modelo, para eu poder calibrar a decisão com dado em vez de suposição.

## Entra

- Todo ciclo com resposta do modelo passa a registrar, **no mesmo registro**, o veredicto de cada regra de entrada — custo, custo com folga, regime, toxicidade e confiança — mesmo quando uma regra anterior já recusou o ciclo. Hoje a primeira recusa encerra o registro e os veredictos seguintes não aparecem em lugar nenhum.
- O registro passa a dizer **de onde veio a confiança** usada (o campo de confiança da resposta ou a probabilidade da opção escolhida). Hoje os dois são fundidos num valor só e não se sabe qual falhou.
- A **versão do modelo** que respondeu passa a ser gravada em todo registro, e a chamada passa a pedir uma versão fixa em vez do apelido que muda sozinho quando o fornecedor publica.
- A leitura de **toxicidade** deixa de ser um corte único em 0,5: passa a ter corte de sim, corte de não e uma faixa de incerteza entre eles, todos visíveis no registro.
- O **tempo limite** da chamada ao modelo passa a ser compatível com a latência real medida no DEV.

Critérios observáveis:

- Dado um ciclo recusado por confiança, existe registro com o veredicto de custo, de regime e de toxicidade para esse mesmo ciclo.
- Dado um ciclo com resposta do modelo, existe registro com a origem da confiança e com a versão do modelo.
- Dado um valor de toxicidade dentro da faixa de incerteza, o registro marca a decisão como indeterminada — nem "tóxico" nem "não tóxico".
- O comportamento de compra/venda **não muda**: com a mesma entrada, o resultado da decisão antes e depois deste card é o mesmo.

Factos desta grelha (DEV, 23/09):

- O tempo limite da chamada ao modelo e a recusa de resposta atrasada são hoje o **mesmo número**: 1,5 s. No registro de diagnóstico do DEV, **20 de 63** chamadas entre 19:13 e 19:44 estouraram esse tempo (**~32%**). Nas que respondem, a mediana é **0,32 s** (844 registros no ficheiro); quando a chamada estoura, o registro guarda só o tempo do corte, não o tempo real da resposta.
- Nas **766** chamadas de 1 Hz da janela 13:26–13:44 **não houve nenhum estouro**: a lentidão é do fornecedor, não do nosso ritmo de chamada.
- A chamada que estoura o tempo não traz veredicto nenhum: o registro fecha como erro e o ciclo termina recusado por atraso.
- Os valores de toxicidade no registro vão de **0,34 a 0,79**, com **10 registros entre 0,45 e 0,49** (logo abaixo do corte de hoje) e **8 entre 0,54 e 0,59** (logo acima).
- A chamada pede hoje o apelido `jev-latest`, e a versão que respondeu não fica gravada em lugar nenhum: o registro cru que a mostraria está desligado e não há nenhuma linha com versão no ficheiro do DEV.
- A confiança usada é o **campo de confiança da resposta quando ele existe**; só quando ele não existe é que se cai na probabilidade da opção escolhida.
- As regras de entrada decidem hoje **em ordem e param na primeira recusa**, e o que fica registrado é só o primeiro motivo: o veredicto de custo/regime/toxicidade nunca chega a ser calculado quando a confiança recusa antes.

Decisões fechadas (grelha 23/09):

- A faixa de incerteza da toxicidade **não muda o que o bot faz**: o registro etiqueta cada leitura como não tóxica, indeterminada ou tóxica, e a decisão continua a sair do corte de hoje.
- Os dois cortes ficam em **0,4 e 0,6**: abaixo de 0,4 o registro marca não tóxico, de 0,4 a 0,6 marca indeterminado e acima de 0,6 marca tóxico.
- O tempo limite da chamada ao modelo passa a **3 s** e a recusa de resposta acima de **1,5 s** fica onde está: nenhuma decisão muda e passa a haver registro das respostas entre 1,5 s e 3 s que hoje se perdem.
- O registro passa a gravar a **versão do modelo que respondeu** e a chamada passa a pedir uma **versão fixa** em vez do apelido que muda sozinho quando o fornecedor publica — nesta entrega.

## Não entra

- Mudar o valor do limiar de confiança.
- Mudar a pergunta feita ao modelo (faixas, níveis ou tipos de resposta).
- Expor qualquer coisa no painel/Monitor (decisão do #1015: a recusa e o motivo ficam só no log).
- Base de dados nova, dashboard, exportação/Drive, backtest.
- Produção (PROD é T16, no lote).

## Evidência (homologação do #1025, 23/09)

| Medição | Valor |
|---|---|
| respostas que passam o limiar 0,7 | **0 de 766** |
| confiança observada (log do #1015) | máxima 0,39 · p50 0,06 |
| confiança nas chamadas de hoje (19:10–19:43) | 0,07 a 0,19 |
| registros com veredicto de custo/regime/toxicidade | **0** (todos os ciclos morreram na confiança) |
| valores de toxicidade observados | 0,34 a 0,79 — inclui 0,41 / 0,43 / 0,44 decididos por margem mínima sobre 0,5 |
| tempo limite esgotado | **11 em ~37 chamadas (~30%)** na janela 19:10–19:35 |

Fora do repositório, a documentação pública do fornecedor do modelo recomenda: registrar a versão que respondeu em cada resposta, pinar a versão em vez de usar o apelido, e tratar perguntas de sim/não com dois cortes e uma faixa de incerteza entre eles.

## Como (resumo técnico da solução)

- **Veredicto de todos os gates no mesmo registro, sem mudar a decisão.** As regras de entrada continuam a decidir em ordem e a parar na primeira recusa; o que muda é que a decisão passa a devolver, junto com o primeiro motivo, o veredicto de **cada** gate alimentado pela resposta do modelo (`hurdle` = custo, `regime` = custo com folga, `toxic_book` = toxicidade, `low_confidence` = confiança; mais `jev_late` e `hold`), cada um `pass`/`fail`/`not_applicable`, calculado independentemente. O registro do ciclo passa a levar esse mapa no **mesmo registro**, mesmo quando um gate anterior já recusou. Sem painel, sem rota, sem base de dados: o destino é o ficheiro de log do #1015.
- **Origem da confiança calculada com o valor.** O valor de confiança e a sua origem (`reply_field` — campo de confiança da resposta; `choice_probability` — probabilidade da opção escolhida; `none`) passam a ser produzidos pela mesma função, para que a origem registrada seja exactamente a do número que a decisão consumiu.
- **Versão do modelo pinada e gravada.** A chamada deixa de pedir o apelido `jev-latest` e passa a pedir um identificador de versão fixo (configurado/pinado); a versão que **respondeu** (campo `model` da resposta) passa a ser gravada em todo registro, independentemente do opt-in de payload cru do #1025.
- **Toxicidade com dois cortes e faixa, só etiqueta.** A leitura ganha três rótulos visíveis no registro — **não tóxico** (abaixo de 0,4), **indeterminado** (de 0,4 a 0,6) e **tóxico** (acima de 0,6) — mais `unknown` quando a resposta não traz valor. A decisão de compra/venda continua a sair do corte de hoje (**≥ 0,5**): a faixa etiqueta, não decide.
- **Tempo limite 3 s com a recusa em 1,5 s intacta.** O tempo limite da chamada passa a 3 s; a recusa de resposta acima de 1,5 s (`jev_late`) fica onde está. Nenhuma decisão muda e passa a haver registro das respostas entre 1,5 s e 3 s que hoje se perdem (fecham como erro e não deixam veredicto).
- **Não-regressão observável.** Com a mesma entrada, o resultado da decisão antes e depois é o mesmo: o teste compara a decisão (mesmo `send`/`skip_reason`) antes e depois, e o registro é efeito lateral.
- **Só DEV nesta entrega** (o loop do runtime-worker DEV com `RUN_SCALP_LOOP=1`); o unit PROD não ganha nada. Sem `frontend/**`, sem rota nova, sem base de dados, sem exportação/Drive, sem PROD.

## Capabilities

### New Capabilities

- `scalp-jev-entry-verdicts`: todo ciclo com resposta do modelo deixa **um** registro com o veredicto de cada gate de entrada alimentado pela resposta (custo, custo com folga/regime, toxicidade, confiança, atraso, hold), mesmo quando um gate anterior já recusou; o registro diz a **origem da confiança** usada; a decisão de compra/venda não muda (não-regressão observável); destino é só o log.
- `scalp-jev-model-version`: a chamada pede uma **versão fixa** do modelo (nunca o apelido que muda sozinho) e a **versão que respondeu** é gravada em todo registro.
- `scalp-jev-toxicity-band`: toxicidade lida com **dois cortes (0,4 / 0,6)** e uma **faixa de incerteza** entre eles, com o rótulo visível no registro (não tóxico / indeterminado / tóxico / unknown); a decisão continua pelo corte de hoje (≥ 0,5).
- `scalp-jev-call-timeout`: **tempo limite da chamada = 3 s**, com a recusa de resposta acima de **1,5 s** inalterada; as respostas entre 1,5 s e 3 s passam a ser registradas; nenhuma decisão muda.

### Modified Capabilities

- (nenhuma) — a change **estende os registos do #1015 de forma aditiva** (o prefixo `scalp cycle refused` e a chave `skip_reason` do #1015 são preservados) para a régua read-only do #1025 (`scripts/scalp_jev_eval.py`) continuar a ler o ficheiro sem alterações; nenhum requisito vigente é alterado. O painel, o payload SystemOne, as regras de entrada/saída e a cadência não mudam.

## Impact

- `backend/app/services/scalp_engine.py`: `decide_cycle` passa a devolver, sem alterar a decisão, o veredicto de cada gate alimentado pela resposta; novos valores de contrato (faixa de toxicidade, timeout de 3 s) entram como constantes puras ao lado de `JEV_LATE_MS`; a decisão (`send`/`skip_reason`) fica idêntica.
- `backend/app/services/scalp_jev.py`: `_side_confidence` devolve também a origem da confiança; a toxicidade ganha o rótulo de três estados (o booleano de decisão continua `noul >= 0,5`); a chamada passa a pedir a versão fixa em vez de `_JEV_MODEL = "jev-latest"`; o tempo limite por omissão passa a 3 s; a versão que respondeu (`model`) segue no sinal para o registro.
- `backend/app/services/scalp_jev_log.py`: os registos do diagnóstico ganham os campos aditivos (veredictos por gate, origem da confiança, versão do modelo, rótulo de toxicidade) sem mudar o ficheiro, o tecto de 200 MB nem a truncagem de cauda; o ciclo enviado passa a deixar registro com os veredictos.
- `backend/app/services/scalp_service.py`: `tick_user` escreve o registro do ciclo com o mapa de veredictos, no mesmo fecho de hoje (um só ponto, pré- e pós-chamada).
- Sem `frontend/**`, sem rota nova, sem painel/Monitor, sem base de dados, sem exportação/Drive, sem PROD.
