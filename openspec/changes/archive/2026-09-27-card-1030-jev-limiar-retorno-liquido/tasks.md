# Tasks — card-1030-jev-limiar-retorno-liquido

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> Gate antes de implementar: **Design → Aprovação de Design → Pronto para Dev** — só o `Status=Pronto para Dev` (aprovação humana do Alan) libera `/opsx:apply`; o agente não cruza `Aprovação de Design → Pronto para Dev`.
> Usar as skills do projeto disponíveis no Cursor quando aplicável (`.cursor/skills/`, `.agents/skills/`), com o runbook `covenant-flow`; a crítica de Design é a skill `design-critic`.
> `UI impact: none` nesta entrega: nada de painel/Monitor, `/api/scalp/status`, rota, HTML, base de dados nova, backtest ou PROD. Os tokens do gate estão no `design.md`.

## 1. Régua: acurácia e retorno líquido por faixa e por regime

- [x] 1.1 — Em `scripts/scalp_jev_eval.py`, acrescentar à estatística por faixa (`_stats`, `:462-485`) a **acurácia** = fracção dos ciclos com preço cuja realização assinada a 900 s é positiva, mantendo `expectancy_net_bp`; a tabela de faixas passa a mostrar `n`, `n com preço`, **acurácia** e **retorno líquido**.
- [x] 1.2 — Reportar as faixas de confiança (`confidence_bucket`, largura 0,1) **por regime de mercado** (calmo/ativo), com o **tamanho da amostra** de cada faixa; faixa sem amostra suficiente é declarada como tal.
- [x] 1.3 — A acurácia é **reportada**, nunca critério de escolha do limiar (decisão 1 do `design.md`); nenhum limiar nasce da acurácia.

## 2. Régua: limiar por retorno líquido esperado e cobertura

- [x] 2.1 — Construir a **população elegível** de cada regime: ciclos de janela não sobreposta com resposta que passam `hold`, `jev_late`, `hurdle`, `regime` e `toxic_book` (veredictos do #1028 no registo; predicados puros do #1025 reconstruídos só como detalhe), com o realizado a 900 s disponível.
- [x] 2.2 — Para cada limiar candidato `t`, calcular e mostrar no relatório: **quantos ciclos deixa passar** (cobertura), o **ganho esperado** (média do retorno líquido dos que passam) e o **retorno líquido esperado** = `ganho esperado × cobertura`; retorno líquido do ciclo = realização assinada − `2 × taxa maker por perna`.
- [x] 2.3 — Escolher, por regime, o limiar = **`argmax` do retorno líquido esperado** entre os candidatos com amostra suficiente (decisão 2); o relatório mostra a linha do limiar escolhido com cobertura e retorno líquido esperado.
- [x] 2.4 — Usar a **taxa real por perna** da conta em uso (mesmo valor que a decisão usa, `_fee_terms`) e **registar no relatório a taxa usada e a sua origem** (conta vs fallback conservador `10 bp`); o default só é aceitável como fallback declarado.

## 3. Régua: um limiar por regime, fecho, separação e homogeneidade

- [x] 3.1 — Segmentar pela **fronteira de regime única** (σ da janela em bp, a mesma que a decisão usa — decisão 3), mostrando a mediana da amostra apenas como referência; o relatório declara a fronteira usada.
- [x] 3.2 — Mostrar, para **cada regime** (calmo e ativo), a **faixa que justifica o limiar** daquele regime e o **tamanho da amostra**.
- [x] 3.3 — Marcar como **fechado** o regime cuja população elegível com preço < `MIN_NON_OVERLAPPING_WINDOWS` (30) ou cuja faixa contribuinte < `MIN_BUCKET_TRADES` (20); regime fechado **não opera** e o relatório declara-o.
- [x] 3.4 — Declarar, por regime, se a confiança **separa** ciclos bons de ruins pelo critério da decisão 6 (existe limiar com retorno líquido esperado positivo e estritamente melhor que aceitar tudo, com amostra suficiente); quando não separa, o relatório diz isso explicitamente e propõe o limiar **desligado**.
- [x] 3.5 — Declarar a **homogeneidade** da amostra: versão do modelo (`model=`) e origem da confiança (`confidence_origin=`) do #1028, e o número de janelas excluídas por mistura/origem divergente; sem homogeneidade, não propor limiar (decisão 7).
- [x] 3.6 — Manter a **insuficiência declarada, nunca concluída**: sem relatório suficiente, nenhum valor é proposto e o valor em uso é preservado; a régua continua **read-only** (o teste `test_the_instrument_is_read_only` cobre o ficheiro) e sem o loop do scalp.

## 4. Decisão: política de confiança por regime

- [x] 4.1 — Em `backend/app/services/scalp_engine.py`, o gate `low_confidence` (`:382`) passa a ler a **política do regime** recebida por parâmetro (`numérico` | `desligado` | `fechado`); o motor continua **puro** (sem I/O, sem env) e a decisão dos outros gates fica inalterada.
- [x] 4.2 — `numérico`: comportamento actual do gate com o valor daquele regime. `desligado`: sem recusa `low_confidence` (caminho de remoção existente, decisão por previsão × custo × regime). `fechado`: o ciclo fecha com **token de recusa próprio** (nunca `regime` nem `low_confidence`).
- [x] 4.3 — Fronteira única de regime: em `backend/app/services/scalp_service.py`, calcular o regime de mercado pela **σ da janela** (o mesmo `vol_bp` que segue no payload — `scalp_jev_payload.py:132`) contra a fronteira configurada e injectá-lo no motor; ausente/ inválida → ambos os regimes fechados (falha fechada).
- [x] 4.4 — Em `backend/app/services/scalp_jev_log.py`, o fecho por regime fechado deixa registo visível no ficheiro do #1015 (mesmo logger/ficheiro/tecto/truncagem), com o **token próprio**, o regime de mercado e o veredicto da confiança no mesmo registo; o `RefusalRe`/`KVRe` do #1025 continuam a ler o ficheiro sem alterações.

## 5. Configuração explícita, reversível e com valor em uso preservado

- [x] 5.1 — Configuração por regime (`calm`/`active`) aceitando valor em [0,1], `off|none|disabled` (desligado) ou `closed` (fechado); valor **ausente**, não finito ou fora de [0,1] cai em `fechado`; a fronteira de regime é a **mesma** para a régua e a decisão (fail-closed).
- [x] 5.2 — Com relatório insuficiente, as políticas ficam `fechado`, o **valor em uso é preservado e reportado** e o bot **não opera**; só um relatório suficiente abre um regime com um valor justificado (decisões 5 e 9).
- [x] 5.3 — Nenhum valor numérico adoptado sem relatório suficiente; reverter = repor o valor em configuração.

## 6. Testes, só log, DEV-only e validação

- [x] 6.1 — Testes da régua: acurácia e retorno por faixa com amostra; `argmax` do retorno líquido esperado; cobertura do limiar escolhido; regime fechado por insuficiência; não-separação → limiar desligado; taxa por perna e sua origem; homogeneidade (versão/origem).
- [x] 6.2 — Testes da decisão: política `numérico`/`desligado`/`fechado` por regime; fronteira partilhada; regime fechado com token próprio e veredicto da confiança; `off` sem `low_confidence`; valor em uso preservado; fail-closed de configuração (`nan`/`inf`/fora de [0,1]).
- [x] 6.3 — Não-regressão dos outros gates: gate de regime do #1025, hurdle, toxicidade, geometria alvo/stop/hold e escape agressivo inalterados; a régua do #1025 continua a ler o log (teste existente) — só a leitura da confiança passa a ser por regime.
- [x] 6.4 — Só log e DEV-only: sem `frontend/**`, sem rota, sem HTML, sem painel/Monitor, sem `/api/scalp/status`, sem base de dados nova, sem exportação/Drive, sem backtest; PROD é T16. Sem segredos em artefactos, registos ou evidência.
- [x] 6.5 — `openspec validate card-1030-jev-limiar-retorno-liquido --strict` verde no worktree.

## 7. Gate de Design (não implementar aqui)

- [x] 7.1 — Confirmar `Status=Design` → crítica do `design-critic` → `Aprovação de Design`; **não** avançar para `Pronto para Dev` (T7 é do Alan) nem editar código de produto neste filho.
- [x] 7.2 — Depois de `Pronto para Dev`: `/opsx:apply` com o relatório da régua como gate dos valores — nenhum limiar numérico adoptado sem relatório suficiente. Se o relatório declarar amostra insuficiente, manter as políticas `fechado` e o valor em uso, registando o motivo na evidência.
- [x] 7.3 — Declarar a dependência #1029 na evidência do Apply: a população elegível reflecte a leitura da previsão em vigor; a recalibração depois do #1029 é requisito declarado, não comportamento assumido.
