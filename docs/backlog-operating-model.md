# Modelo Operacional do Backlog

## Objetivo

Este projeto usa dois artefatos complementares:

- **GitHub Projects + Issues**: fonte operacional de execucao, ligada a issue, PR, commit, teste e evidencia.
- **SharePoint Excel `crypto_backlog_po.xlsx`**: visao executiva de produto, roadmap, decisao de negocio e evidencia consolidada.

Telegram e chat servem para alinhamento rapido. Nao sao fonte da verdade.

## Regra Principal

Nao existem dois backlogs ativos. Um item escolhido para execucao vive no GitHub Project. A planilha nao deve duplicar status tecnico; ela recebe resumo ou evidencia apenas quando isso muda produto, roadmap, beta ou negocio.

Um item so e considerado concluido quando tiver evidencia registrada.

Exemplos de evidencia:

- link de PR;
- commit;
- print ou video;
- resultado de teste;
- log de validacao;
- feedback real de usuario beta;
- decisao registrada em documento.

## Fluxo

1. Ideias e escopo amplo ficam na planilha.
2. Itens escolhidos para execucao viram GitHub Issue.
3. Issues entram no GitHub Project.
4. PRs e commits fecham ou referenciam issues.
5. Evidencia volta para a planilha quando afetar decisao de produto, beta ou negocio.

## Colunas do GitHub Project

- `Backlog`: item conhecido, mas nao pronto para execucao.
- `Ready`: pronto para fazer, com criterio de pronto claro.
- `In progress`: trabalho ativo.
- `Blocked`: depende de decisao, acesso, dado ou correcao anterior.
- `Validate`: precisa de teste, revisao ou evidencia.
- `Done`: concluido com evidencia.

## Campos Recomendados

- `Prioridade`: `P0`, `P1`, `P2`.
- `Frente`: `Produto`, `Monitor`, `Dados`, `Backtest`, `Grafico`, `Acesso`, `Risco`, `QA`, `Comercial`, `Operacao`, `Seguranca`, `Metricas`.
- `Tipo`: `Produto`, `Codigo`, `QA`, `Comercial`, `Operacao`, `Seguranca`, `Metrica`.
- `Semana`: semana de execucao ou revisao.
- `Evidencia`: link ou descricao curta da prova de conclusao.

## WIP

No maximo 5 itens ativos por semana.

Regra pratica:

- ate 3 itens tecnicos;
- ate 1 item comercial/validacao;
- ate 1 item operacional/risco.

Se passar disso, o projeto parece estar andando mais do que realmente esta.

## Ritual Semanal

Toda semana revisar:

1. O que destrava o beta fechado?
2. O que esta bloqueado?
3. O que ja tem evidencia?
4. O que aproxima dos 10 primeiros clientes?
5. Quais 5 itens entram na semana?

## Criterio de Saude

O backlog esta saudavel quando:

- P0 cabe em poucas semanas;
- cada item tem proximo passo claro;
- bloqueios aparecem explicitamente;
- itens concluidos tem evidencia;
- o trabalho ativo aproxima o beta fechado ou os primeiros clientes.
