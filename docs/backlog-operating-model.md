# Modelo Operacional do Backlog

## Objetivo

Este projeto usa dois artefatos complementares:

- **GitHub Projects + Issues**: fonte operacional de execucao, ligada a issue, PR, commit, teste e evidencia.
- **SharePoint Excel `crypto_backlog_po.xlsx`**: visao executiva de produto, roadmap, decisao de negocio e evidencia consolidada.
- **`docs/project-hub.md`**: ponto unico de consulta rapida para objetivo, status atual, bloqueios, decisoes e proximos passos.

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

- `Status` e a fonte principal das colunas:
  - `Todo`: backlog ou pronto para comecar.
  - `In Progress`: trabalho ativo.
  - `Code Review`: diff pronto para revisao Codex antes do commit.
  - `QA`: SHA revisado em validacao automatizada, incluindo `qa-gate` e Playwright visual.
  - `Done`: Done tecnico; QA verde, integrado em `develop`, restart/runtime validados e aguardando Alan.
  - `Homologado`: Alan aprovou funcionalmente em `develop`.
  - `Pronto`: publicado/operacional em producao com evidencia.
  - `Cancelado`: item substituido ou descartado.
- Caminho normal: `Todo -> In Progress -> Code Review -> QA -> Done -> Homologado -> Pronto`.
- Falha que exige alteração: `QA -> In Progress -> Code Review -> QA`.
- `Fluxo` e substatus/legado: `Backlog`, `Ready`, `In-progress`, `Code Review`, `QA`, `Blocked`, `Validate` e `Done`. Quando houver equivalência, espelhar o `Status`; `Validate` permanece para histórico.

## Regra de Revisao da Clara

Quando Clara concluir um entregavel de produto, operacao, validacao, metrica ou copy:

- registrar evidencia no issue e encaminhar para `QA` quando a entrega entrar no ciclo técnico;
- aguardar `qa-gate`/Playwright visual ou a dispensa autorizada quando aplicável;
- mover para `Done` somente após QA verde e evidência técnica;
- aguardar revisão/homologação de Alan.

Clara nao deve usar `Pronto` como estado de revisao. Se ainda faltar execucao real, o card deve ficar em `In Progress`.

## QA visual

Playwright visual é obrigatório por padrão em todo card, inclusive sem mudança de frontend. A dispensa só vale quando Alan registra no card `QA visual dispensado por Alan.` com motivo e a label `qa-visual-skip` está aplicada. O CI preserva artifacts de falha; baseline visual atualizado faz parte do diff revisado.

Fluxo rápido (ver `AGENTS.md` / `alan-workflow` Visual QA): em mudança de UI intencional, atualizar baselines no DEV Linux com `npm --prefix frontend run test:e2e:visual -- --update-snapshots`, revisar só o `diff.png` dos cenários alterados, commit dos `*-snapshots/` e deixar o CI revalidar. Não usar loop de vision em todos os artifacts do CI para “passar” o teste — o Playwright já compara pixels.

## Regra de Release

Quando Alan pedir `gerar release`, `criar release`, `fechar release`, `subir lote` ou equivalente para cards no nome da Clara ou do Alan:

- levantar todos os cards `Homologado` incluídos no pacote, independente do responsavel;
- revisar se decisões, status e entregáveis estão refletidos na documentação do projeto/produto;
- sincronizar Markdown local e Google Docs/Drive correspondentes;
- publicar/encerrar a release com evidência;
- mover esses cards de `Homologado` para `Pronto`.

Para cards de `Codex`, confirmar commits/branches, PRs, testes e merge em `main`. Para cards de `Clara` ou `Alan`, confirmar documentação local em `docs/` e Google Drive quando aplicável.

## Campos Recomendados

- `Prioridade`: `P0`, `P1`, `P2`.
- `Frente`: `Produto`, `Monitor`, `Dados`, `Backtest`, `Grafico`, `Acesso`, `Risco`, `QA`, `Comercial`, `Operacao`, `Seguranca`, `Metricas`.
- `Tipo`: `Produto`, `Codigo`, `QA`, `Comercial`, `Operacao`, `Seguranca`, `Metrica`.
- `Owner`: somente `Codex`, `Alan` ou `Clara`.
- `Semana`: semana de execucao ou revisao.
- `Evidencia`: link ou descricao curta da prova de conclusao.

Regra de owner:

- `Codex`: execucao tecnica, codigo, infra, QA tecnico e seguranca.
- `Clara`: produto, operacao, copy, validacao, metricas e evidencia executiva.
- `Alan`: decisao, aprovacao, input pessoal, canal, lista de pessoas ou escolha final.

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
