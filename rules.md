# Regras Operacionais do Projeto

Este arquivo define as regras obrigatorias e curtas do projeto. O `AGENTS.md` detalha como executar cada regra na pratica.

## Escopo dos arquivos

- `rules.md`: politica normativa, curta e obrigatoria. Use para decidir o que nunca pode ser pulado.
- `AGENTS.md`: manual operacional detalhado. Use para comandos, ordem de execucao, mapeamento OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Em caso de duvida ou conflito, siga a regra mais restritiva. Se ainda houver ambiguidade, pare e registre o conflito antes de alterar codigo, card ou Git.

## Regras obrigatorias

1. Sempre usar OpenSpec para qualquer alteracao de codigo, independente de tamanho ou complexidade.
   - Toda mudanca de codigo deve ter trilha em `openspec/changes/<change>/` antes da implementacao e evidencia de validacao antes do fechamento.

2. Quando Alan pedir implementacao por card (`#99`, por exemplo), localizar o card no GitHub Project, criar/usar uma branch propria da change a partir de `develop`, mover para `In Progress`, executar o fluxo OpenSpec ate `/opsx:verify`, integrar em `develop`, rodar `./restart` e so entao mover para `Done`.
   - Branch padrao: `change-<id>-<slug>` ou `card-<id>-<slug>`.
   - Commits locais na branch da change sao permitidos.
   - Nessa etapa nao arquivar OpenSpec, nao abrir PR para `main` e nao publicar.

3. Fluxo das colunas do GitHub Project:
   - `In Progress`: card em execucao.
   - `Done`: codigo implementado e validado tecnicamente em `develop`.
   - `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
   - `Pronto`: alteracao ja subiu para `main`/producao.

4. Quando Alan disser que um card esta homologado, mover somente de `Done` para `Homologado`.
   - Nao abrir PR, nao mergear em `main`, nao arquivar OpenSpec e nao fazer commit por esse evento.
   - Termos como `homologado`, `homologuei`, `aprovado em develop` ou `cards homologados` nunca autorizam release, commit, PR ou merge.

5. Quando Alan pedir `subir lote`, `fechar lote`, `fechar release` ou equivalente, executar o fechamento de producao dos cards `Homologado`: listar cards e commits incluidos, revisar pendencias locais, rodar validacao final completa, arquivar OpenSpec, subir para GitHub, abrir/reusar PR para `main`, fazer merge manual e so depois mover os cards incluidos para `Pronto`.
   - Nao usar auto-merge.
   - So comandos explicitos de lote/release autorizam qualquer acao em `main`.
   - Se `develop` contiver mudanca nao homologada, nao fazer merge direto `develop -> main`; usar branch `release-*` com somente conteudo aprovado ou pedir decisao de Alan.

6. Commits locais em branch de change/card sao permitidos e nao exigem suite completa a cada commit.
   - Evitar commit direto em `develop` enquanto a implementacao estiver parcial.
   - Integrar em `develop` somente quando a change estiver pronta para teste integrado/homologacao, preferencialmente com commit claro ou squash referenciando o card.
   - Durante o card, rodar testes proporcionais/focados; testes completos ficam para fechamento de lote/release.

7. Stash nao e armazenamento principal de entrega.
   - Antes de iniciar segunda change, rode `git status --short` e isole o trabalho em branch/worktree propria.
   - Use stash apenas como protecao temporaria, sempre com nome, hash, arquivos incluidos, motivo e comando de recuperacao.
   - Branches de change devem ser apagadas no fechamento final, depois que o conteudo entrar em `main`/`Pronto`, e somente se nao houver commits exclusivos pendentes.

8. Sempre utilizar subagentes quando houver tarefa de desenvolvimento, investigacao, validacao ou revisao tecnica com ganho claro de paralelismo.
   - O agente principal continua responsavel por escopo, consolidacao, evidencias e fechamento.

9. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

10. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, isolamento por branch, pedido explicito de lote/release ou merge manual.

11. Usar a skill `caveman` em modo `lite` como padrao de comunicacao com Alan.
   - Manter respostas curtas, diretas e sem filler, preservando clareza tecnica, seguranca e ordem correta em instrucoes criticas.
   - Desativar somente quando Alan pedir explicitamente `stop caveman` ou `normal mode`.

12. Toda tela, componente visual ou funcionalidade com impacto de UI/UX deve seguir obrigatoriamente o `DESIGN.md`.
   - Vale para telas novas e antigas, ajustes pequenos, refactors visuais, cards de produto e correcoes de interface.
   - Antes de implementar, consultar `DESIGN.md` e registrar no OpenSpec/hand-off quais tokens, componentes, padroes e excecoes foram aplicados.
   - Validacao visual e tecnica deve confirmar aderencia ao `DESIGN.md`; se houver desvio necessario, registrar justificativa antes de fechar a entrega.
