# Regras Operacionais do Projeto

Este arquivo define as regras obrigatorias e curtas do projeto. O `AGENTS.md` detalha como executar cada regra na pratica.

## Escopo dos arquivos

- `rules.md`: politica normativa, curta e obrigatoria. Use para decidir o que nunca pode ser pulado.
- `AGENTS.md`: manual operacional detalhado. Use para comandos, ordem de execucao, mapeamento OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Em caso de duvida ou conflito, siga a regra mais restritiva. Se ainda houver ambiguidade, pare e registre o conflito antes de alterar codigo, card ou Git.
- Regras gerais do modo de trabalho do Alan ficam na skill global `alan-workflow` (`/root/.codex/skills/alan-workflow/SKILL.md`). Este arquivo deve manter somente regras normativas especificas do projeto cripto.

## Regras obrigatorias

1. Siga `alan-workflow` para o ciclo global de card, OpenSpec, evidencias, status, release, higiene Git/worktree/stash e fechamento.
   - No cripto, OpenSpec e obrigatorio para qualquer alteracao de codigo, independente de tamanho ou complexidade.
   - Toda mudanca de codigo deve ter trilha em `openspec/changes/<change>/` antes da implementacao e evidencia de validacao antes do fechamento.

2. Quando Alan pedir implementacao por card (`#99`, por exemplo), aplique `alan-workflow` com os overlays do cripto.
   - Board: GitHub Project `MVP Cripto - Beta Fechado` / Project 1.
   - Branch base de implementacao: `develop`.
   - Branch padrao: `change-<id>-<slug>` ou `card-<id>-<slug>`.
   - Integracao tecnica antes de homologacao: merge/squash em `develop`.
   - Runtime de validacao: `./restart` e URL do sistema servindo o resultado novo.
   - Nessa etapa nao arquivar OpenSpec, nao abrir PR para `main` e nao publicar.

3. No cripto, o campo `Status` e a fonte principal das colunas. O campo `Fluxo`, quando existir, e substatus/legado; se houver divergencia, `Status` prevalece.
   - `Todo`: backlog ou pronto para comecar.
   - `In Progress`: Codex/Clara esta trabalhando ou validando tecnicamente.
   - `Done`: Done tecnico; codigo implementado, validado tecnicamente e integrado em `develop`, aguardando teste/aprovacao do Alan.
   - `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
   - `Pronto`: alteracao ja subiu para `main`/producao com evidencia; este e o fechamento final.
   - `Cancelado`: nao sera feito ou foi substituido.
   - Nao descreva `Status=Done` como card fechado/finalizado; use `Done tecnico` ou `aguardando homologacao`.

4. Homologacao e release seguem `alan-workflow`.
   - No cripto, homologacao e aprovacao funcional em `develop`.
   - So comandos explicitos de lote/release autorizam qualquer acao em `main`.

5. Quando Alan pedir `subir lote`, `fechar lote`, `fechar release` ou equivalente, execute `alan-workflow` com fechamento de producao dos cards `Homologado`.
   - Nao usar auto-merge.
   - Se `develop` contiver mudanca nao homologada, nao fazer merge direto `develop -> main`; usar branch `release-*` com somente conteudo aprovado ou pedir decisao de Alan.
   - Usar `scripts/release-guard pre` antes de abrir/mesclar PR e `scripts/release-guard post` depois da publicacao.

6. Branches e testes seguem `alan-workflow`; no cripto, evitar commit direto em `develop` enquanto a implementacao estiver parcial.
   - Integrar em `develop` somente quando a change estiver pronta para teste integrado/homologacao, preferencialmente com commit claro ou squash referenciando o card.

7. Siga `alan-workflow` para higiene Git/worktree/stash; no cripto, stash nao e armazenamento principal de entrega.
   - Antes de iniciar segunda change, rode `git status --short` e isole o trabalho em branch/worktree propria.
   - Use stash apenas como protecao temporaria, sempre com nome, hash, arquivos incluidos, motivo e comando de recuperacao.
   - Branches de change devem ser apagadas no fechamento final, depois que o conteudo entrar em `main`/`Pronto`, e somente se nao houver commits exclusivos pendentes.

8. Sempre utilizar subagentes quando houver tarefa de desenvolvimento, investigacao, validacao ou revisao tecnica com ganho claro de paralelismo.
   - O agente principal continua responsavel por escopo, consolidacao, evidencias e fechamento.

9. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

10. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md` e em `alan-workflow`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, isolamento por branch, pedido explicito de lote/release ou merge manual.

11. Usar a skill `caveman` em modo `lite` como padrao de comunicacao com Alan.
   - Manter respostas curtas, diretas e sem filler, preservando clareza tecnica, seguranca e ordem correta em instrucoes criticas.
   - Desativar somente quando Alan pedir explicitamente `stop caveman` ou `normal mode`.

12. Toda tela, componente visual ou funcionalidade com impacto de UI/UX deve seguir obrigatoriamente o `DESIGN.md`.
   - Vale para telas novas e antigas, ajustes pequenos, refactors visuais, cards de produto e correcoes de interface.
   - Antes de implementar, consultar `DESIGN.md` e registrar no OpenSpec/hand-off quais tokens, componentes, padroes e excecoes foram aplicados.
   - Validacao visual e tecnica deve confirmar aderencia ao `DESIGN.md`; se houver desvio necessario, registrar justificativa antes de fechar a entrega.
