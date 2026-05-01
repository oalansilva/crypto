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

3. Quando Alan disser que um card esta homologado, executar o fechamento: revisar pendencias locais, rodar `/opsx:verify`, corrigir falhas, rodar `/opsx:archive`, fazer o commit unico de encerramento, subir para `develop`, abrir/reusar PR para `main`, fazer merge manual e so depois mover o card para `Homologado`.
   - Nao usar auto-merge.

4. O unico commit da entrega deve acontecer apos homologacao confirmada por Alan.
   - Se CI/checks falharem depois do push, corrija preservando um commit final sempre que tecnicamente seguro; se nao for seguro, registre a excecao e o motivo.

5. Sempre utilizar subagentes quando houver tarefa de desenvolvimento, investigacao, validacao ou revisao tecnica com ganho claro de paralelismo.
   - O agente principal continua responsavel por escopo, consolidacao, evidencias e fechamento.

6. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

7. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, commit unico ou merge manual.
