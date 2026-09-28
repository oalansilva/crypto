# Tasks — card-1045-jev-diagnostico-recalibracao

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa. Usar as skills do repo em `.cursor/skills/` (openspec-apply-change na implementação). Gate: Design → Aprovação de Design → Pronto para Dev (`design-critic`). Não reabrir #1029, #1006, #1008, #1001 nem o gate de regime do #1025. Não criar base nova, Drive ou backtest externo. PROD é T16.

## 1. Relatório da régua (somente leitura)

- [x] 1.1 — Em `scripts/scalp_jev_eval.py`, corrigir a homogeneidade: amostra elegível vazia, `model` ou `confidence_origin` ausente ou `unknown` não são homogéneos; distinguir «homogénea» de «não verificada» com a contagem de janelas afectadas; sem homogeneidade verificada não propor limiar.
- [x] 1.2 — Reportar benchmark de viés casado (comprar-e-segurar e regra aleatória com a mesma fracção de BUY, semente gravada), contribuição preditiva por faixa, regime e horizonte, fracção de BUY e acurácia do sinal ao lado da do buy-and-hold. O mesmo custo `2 × taxa por perna` nos três. Drift à parte da contribuição.
- [x] 1.3 — Reportar, lado a lado, break-even com e sem custo da geometria em uso e o acerto por barreira (alvo, stop, saída por tempo). Horizontes candidatos 15 min, 1 h, 4 h e 24 h na vela mais fina já guardada. Barreira que não cabe na vela fica indeterminada, não acerto zero. Propor alternativa cujo break-even com custo seja inferior ao acerto, ou declarar não operável. A régua não grava alvo, stop, horizonte, tamanho nem versão.

## 2. Persistência na base já existente

- [x] 2.1 — Migração Alembic no Postgres do scalp: um diagnóstico por dia UTC fechado, versões aplicadas com impressão digital única, calibração global que nasce pausada. Sem inventar versão no backfill. Sem motor novo.
- [x] 2.2 — Sem versão aplicada, a entrada continua no env do #1030 e fecha em caso de valor inválido.

## 3. Diagnóstico diário e aplicação

- [x] 3.1 — Uma corrida por dia UTC já fechado, depois das 00:15 UTC, no processo que já arranca o loop do scalp. Só janelas já terminadas. Segunda corrida no mesmo dia devolve o mesmo diagnóstico e não aplica outra vez. Sem comando de terminal no uso cotidiano. `não medido` ou dado vencido nesse dia fica bloqueado e não é reescrito mais tarde.
- [x] 3.2 — Aplicar só o desfecho de confiança por regime declarado (número, filtro desligado, regime parado ou regime reaberto), sem banda de passo, sem alterar alvo, stop, horizonte ou tamanho. Posterior cronológica com chão de 200 janelas independentes não sobrepostas, medidas e elegíveis; abaixo disso o diagnóstico aparece e a confiança fica. Troca comparável só quando a nova perde menos, com custo, mesmo que continue negativa. Reabrir não exige bater zero se a posterior confirmar que o regime deixou de estar fechado. Se nenhum candidato de geometria ou horizonte bater o break-even, não adoptar parâmetro nenhum.
- [x] 3.3 — Bloquear promoção, com motivo explícito que não seja apresentado como prejuízo, quando a medição falha, o dado está vencido, a cobertura não chega, a amostra não está verificada, o custo não é a taxa real conhecida, ou o benchmark não se calcula. Contribuição 0,00 bp não bloqueia por si. Calibração pausada não aplica e mesmo assim grava o diagnóstico. Falha não limpa kill nem mexe no interruptor.
- [x] 3.4 — Suposição de intervalo (visível no `design.md`, sujeita à aprovação): a confiança pode mudar no dia fechado seguinte se a posterior for nova (fora da escolha e da validação da versão vigente). Não muda duas vezes no mesmo dia. Sem quarentena de vários dias.
- [x] 3.5 — Suposição de reversão automática (visível no `design.md`, sujeita à aprovação): num dia posterior, amostra nova de pelo menos 200 que não validou a troca, se a versão aplicada passar a perder mais do que a imediatamente anterior, reverter para essa anterior sem inventar número. Não reverter no dia da aplicação nem por falha de medição.

## 4. Versão consumida e comandos do operador

- [x] 4.1 — A entrada seguinte lê a versão aplicada; `/api/scalp/status` mostra a mesma versão, os valores anterior e novo e o motivo. Posição já aberta sai como estava. O interruptor não é desligado pela troca.
- [x] 4.2 — Pausar e habilitar a calibração no módulo, sem ligar o scalper nem enviar ordem. Reversão manual para a versão anterior registada, sem esperar as 200, efectiva na entrada seguinte; o automático não reaplica essa impressão digital no mesmo dia.

## 5. Painel no Monitor

- [x] 5.1 — `ScalpModule` em `/monitor` alinhado a `frontend/public/prototypes/card-1045-jev-diagnostico-recalibracao/index.html`: a primeira vista mostra estes factos em frase de trader (data, estado dos dados e dos filtros, período, confiança vigente, decisão, motivo, pausa, voltar atrás e histórico), sem prometer que a amostra é válida quando um gate bloqueou. Não usa rótulos técnicos (homogeneidade, break-even, bp, fasquia, contribuição preditiva). O relatório interno (régua) continua técnico; a primeira vista não. Interruptor, T, clip, kill, alvo +35, stop −28 e lookback intactos. Board (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) e Operar intactos. Sem rota nova. Sem landing/Ajuda.

## 6. Provas

- [x] 6.1 — Testes dos critérios observáveis do issue #1045: relatório (break-even com e sem custo, contribuição preditiva distinta do drift, BUY e buy-and-hold, horizontes, não operável sem adoptar parâmetro), homogeneidade (`unknown`, vazio, declarada), um diagnóstico por dia fechado, posterior abaixo de 200 não muda a confiança, troca que perde menos mesmo negativa, sem banda de passo, idempotência, versão consumida na entrada seguinte, posição aberta inalterada, pausa e reversão, falha de medição que não parece prejuízo nem enfraquece o kill.
- [x] 6.2 — Playwright do `/monitor` contra o proto: landmarks da board, módulo scalp desligado, diagnóstico visível, calibração que não liga o interruptor.
- [x] 6.3 — `openspec validate` desta change.

## 7. Correções após a homologação T18

- [x] 7.1 — O relatório e o resumo de trader distinguem falta de homogeneidade verificada de homogeneidade mista, indicam o motivo e a quantidade de janelas afetadas, mostram o período real coberto e não chamam janelas observadas de trades executados. Os bloqueios continuam fail-closed e o histórico diário fechado permanece imutável; o mínimo de 200 considera janelas novas efetivamente medidas e elegíveis.
- [x] 7.2 — Taxa mostrada no Monitor vem do valor considerado e retornado pela API/régua; o sinal de desconto BNB não substitui nem reaplica desconto à taxa retornada.
- [x] 7.3 — A régua recebe o mesmo limite de regime do ambiente consumido pela decisão; reabertura é confirmada pela posterior sem exigir retorno positivo; a frase do sinal compara a regra com o benchmark correto.
- [x] 7.4 — Reversão automática persiste o cutoff da validação que falhou e a impressão digital reutilizada não volta a ser elegível; múltiplas reversões não reutilizam janelas já consumidas.
- [x] 7.5 — A entrada seguinte e `/api/scalp/status` leem a versão/política ativa, inclusive após reversão manual; posição já aberta conserva sua política. `Ligada` explica quando o processamento está habilitado e regimes continuam fechados.
- [x] 7.6 — Somente o runtime-worker DEV com `RUN_SCALP_LOOP=1` detém o loop e instala o log diagnóstico, mantendo fallback local/API-only e o comportamento PROD sem alterar flags/segredos.
- [x] 7.7 — A primeira vista do ScalpModule explica com precisão os estados e a qualidade dos dados sem mudar a estrutura aprovada do protótipo; taxa, bloqueio e janela observada são apresentados sem ambiguidade.
- [x] 7.8 — Testes isolados cobrem casos relatados de relatório, fee, cutoff/reversão, snapshot consumido, inicialização do loop e estados visíveis; validar OpenSpec e contrato do protótipo.

## 8. Correções determinísticas do CI após T13

- [x] 8.1 — Aplicar Black somente aos quatro arquivos apontados por `backend-format`; `black --check backend` termina com 352 arquivos inalterados.
- [x] 8.2 — Registrar `test_scalp_loop_ownership.py` no inventário; alinhar a contagem do contrato de 90 para 91 e validar 91 arquivos sem entradas ausentes, obsoletas, duplicadas ou semânticas.
- [x] 8.3 — Rodar todo `backend/tests/contract` em ambiente isolado: 10 passaram; conferir no PR1068 que `e2e-playwright` e os checks frontend terminaram verdes, sem alterar UI ou snapshots.
