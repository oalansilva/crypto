# Regras Operacionais do Projeto

Este arquivo define as regras obrigatorias e curtas do projeto. O `AGENTS.md` detalha como executar cada regra na pratica.

## Escopo dos arquivos

- `rules.md`: politica normativa, curta e obrigatoria. Use para decidir o que nunca pode ser pulado.
- `AGENTS.md`: manual operacional detalhado. Use para comandos, ordem de execucao, mapeamento OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Em caso de duvida ou conflito, siga a regra mais restritiva. Se ainda houver ambiguidade, pare e registre o conflito antes de alterar codigo, card ou Git.

## Regras obrigatorias

1. Sempre usar OpenSpec para qualquer alteracao de codigo, independente de tamanho ou complexidade.
   - Toda mudanca de codigo deve ter trilha em `openspec/changes/<change>/` antes da implementacao e evidencia de validacao antes do fechamento.

2. Quando Alan pedir implementacao por card (`#99`, por exemplo), localizar o card no GitHub Project, mover para `In Progress`, executar o fluxo OpenSpec ate `/opsx:verify`, rodar `./restart` e so entao mover para `Done`.
   - Nessa etapa nao arquivar OpenSpec e nao fazer commit.

3. Fluxo das colunas do GitHub Project:
   - `In Progress`: card em execucao.
   - `Done`: codigo implementado e validado tecnicamente em `develop`.
   - `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
   - `Pronto`: alteracao ja subiu para `main`/producao.

4. Quando Alan disser que um card esta homologado, mover somente de `Done` para `Homologado`.
   - Nao abrir PR, nao mergear em `main`, nao arquivar OpenSpec e nao fazer commit por esse evento.
   - Termos como `homologado`, `homologuei`, `aprovado em develop` ou `cards homologados` nunca autorizam release, commit, PR ou merge.

5. Quando Alan pedir `subir lote`, `fechar lote`, `fechar release` ou equivalente, executar o fechamento de producao dos cards `Homologado`: revisar pendencias locais, rodar validacao final, arquivar OpenSpec, fazer commit unico do lote em `develop`, subir para GitHub, abrir/reusar PR para `main`, fazer merge manual e so depois mover os cards incluidos para `Pronto`.
   - Nao usar auto-merge.
   - So comandos explicitos de lote/release autorizam qualquer acao em `main`.

6. O unico commit da entrega deve acontecer no fechamento de lote/release, nao durante implementacao nem ao mover card para `Homologado`.
   - Se CI/checks falharem depois do push, corrija preservando um commit final sempre que tecnicamente seguro; se nao for seguro, registre a excecao e o motivo.

7. Sempre utilizar subagentes quando houver tarefa de desenvolvimento, investigacao, validacao ou revisao tecnica com ganho claro de paralelismo.
   - O agente principal continua responsavel por escopo, consolidacao, evidencias e fechamento.

8. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

9. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, commit unico, pedido explicito de lote/release ou merge manual.

10. Usar a skill `caveman` em modo `lite` como padrao de comunicacao com Alan.
   - Manter respostas curtas, diretas e sem filler, preservando clareza tecnica, seguranca e ordem correta em instrucoes criticas.
   - Desativar somente quando Alan pedir explicitamente `stop caveman` ou `normal mode`.
