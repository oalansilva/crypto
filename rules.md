# Regras Operacionais do Projeto

Este arquivo define as regras obrigatorias e curtas do projeto. O `AGENTS.md` detalha como executar cada regra na pratica.

## Escopo dos arquivos

- `rules.md`: politica normativa, curta e obrigatoria. Use para decidir o que nunca pode ser pulado.
- `AGENTS.md`: manual operacional detalhado. Use para comandos, ordem de execucao, mapeamento OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Em caso de duvida ou conflito, siga a regra mais restritiva. Se ainda houver ambiguidade, pare e registre o conflito antes de alterar codigo, card ou Git.
- Regras gerais do modo de trabalho do Alan ficam na skill global `alan-workflow` quando ela estiver disponível no cliente. O opencode aplica os mesmos overrides versionados neste arquivo e em `AGENTS.md`; o fluxo do projeto não depende de um caminho absoluto local.

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
   - `Design`: Designer/Critic Agent prepara prototipo, critica e evidencias.
   - `Aprovação de Design`: entrega de design completa aguardando Alan.
   - `Pronto para Dev`: Alan aprovou o design por arraste; desenvolvimento liberado.
   - `Em desenvolvimento`: opencode/Clara esta trabalhando ou validando tecnicamente.
   - `Code Review`: diff pronto para revisao antes do commit; achados bloqueantes corrigidos ou classificados.
   - `QA`: SHA revisado em validacao automatizada; `qa-gate` e Playwright visual precisam atingir resultado terminal verde.
   - `Done`: Done tecnico; QA verde, codigo integrado em `develop`, `./restart` e runtime validados, aguardando teste/aprovacao do Alan.
   - `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
   - `Pronto`: alteracao ja subiu para `main`/producao com evidencia; este e o fechamento final.
   - `Cancelado`: nao sera feito ou foi substituido.
   - Caminho obrigatório de todo card: `Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`.
   - **Guardrail anti-bypass de Design:** nenhum card pode pular `Design`, `Aprovação de Design` ou `Pronto para Dev`. Vale para UI e não-UI, remoções, bugs, docs técnicas com card e pedidos `implemente`/`pode codar`. Não existe bypass `Todo -> Pronto para Dev` nem `Todo -> Em desenvolvimento`.
   - Somente Alan autenticado aprova `Aprovação de Design -> Pronto para Dev`; agentes nunca autoaprovam. Mudança no design/protótipo aprovado invalida o gate.
   - Código de produção / `/opsx:apply` só depois de `Status=Pronto para Dev`. Pedido de implementação antecipa OpenSpec/Design, não autoriza pular colunas.
   - Falha de QA que exige codigo: `QA -> Em desenvolvimento -> Code Review -> QA`; falha de infraestrutura permanece em `QA` para rerun documentado.
   - Nao descreva `Status=Done` como card fechado/finalizado; use `Done tecnico` ou `aguardando homologacao`.

4. Todo card em `Status=Design` usa o contrato canônico `.agents/skills/design-critic/SKILL.md` antes da implementação.
   - No opencode, invoca-se a skill `design-critic` (tool skill carregada automaticamente de `.agents/skills/`).
   - Com `UI impact: affected`, o agente produz/refatora o prototipo, critica produto/UX/acessibilidade/responsividade/estados e registra o veredito no `design.md`.
   - Com `UI impact: affected`, também exige o pipeline do Impeccable na ordem `context -> shape -> prototype -> critique -> audit -> targeted fixes -> polish -> browser gate`, com `Impeccable Brief`, `Impeccable Critique`, `Impeccable Audit` e `Impeccable Trace` versionados. O `DESIGN.md` não pode ser sobrescrito. O plugin `.opencode/plugin/impeccable-hook.ts` roda o detector automaticamente em edições de UI e no fim de turno.
   - Assessment A e Assessment B devem ser critics read-only separados e herdar exatamente o mesmo LLM/modelo e versão da sessão principal do opencode. Se a igualdade não for observável, o veredito é `BLOCKED`; não usar fallback.
   - Com `UI impact: none`, ainda passa por `Design` e `Aprovação de Design`; a entrega de design é enxuta (decisão, escopo, riscos, `Design Critique`) e registra explicitamente a ausência de superfície visual nova.
   - Com `UI impact: none`, registrar Impeccable como `N/A` com justificativa; isso não reduz nenhum gate.
   - Protótipo HTML, quando houver, deve ser navegável em `frontend/public/prototypes/<slug>/` via URL DEV; o Gist OpenSpec lista só Markdown e nunca HTML.
   - **Fidelidade ao sistema atual:** quando a tela/rota/shell já existir no produto, o protótipo MUST partir do UI atual (shell, nav, tokens, densidade, componentes) e redesenhar só a mudança em cima dele, para Alan validar o delta. Proibido inventar layout/marketing paralelo. Tela nova (ainda inexistente) pode ser desenhada do zero, ainda assim obedecendo `DESIGN.md` e o shell do app quando for superfície autenticada.
   - **Validação obrigatória do protótipo:** antes de `Design Agent verdict: PASS`, abrir a URL final em navegador real, validar desktop/mobile, estado padrão, interações e asserts dos critérios críticos. Para remoção, provar que o elemento não está visível/existe no estado final. HTTP 200, build, leitura do HTML ou `curl` não bastam. Registrar URL, viewports, ações/asserts e resultado em `design.md` (`## Prototype Validation`). Qualquer falha ou navegador indisponível mantém `BLOCKED`.
   - Depois de qualquer alteração no protótipo ou rebuild/restart, repetir a validação no navegador; evidência anterior fica inválida.
   - O agente pode mover somente `Design -> Aprovação de Design` quando a evidência estiver completa; nunca pode executar a aprovação humana.

5. Homologacao e release seguem `alan-workflow`.
   - No cripto, homologacao e aprovacao funcional em `develop`.
   - So comandos explicitos de lote/release autorizam qualquer acao em `main`.

6. Quando Alan pedir `subir lote`, `fechar lote`, `fechar release` ou equivalente, execute `alan-workflow` com fechamento de producao dos cards `Homologado`.
   - Nao usar auto-merge.
   - Se `develop` contiver mudanca nao homologada, nao fazer merge direto `develop -> main`; usar branch `release-*` com somente conteudo aprovado ou pedir decisao de Alan.
   - Usar `scripts/release-guard pre` antes de abrir/mesclar PR e `scripts/release-guard post` depois da publicacao.

7. Branches e testes seguem `alan-workflow`; no cripto, evitar commit direto em `develop` enquanto a implementacao estiver parcial.
   - Integrar em `develop` somente quando a change estiver pronta para teste integrado/homologacao, preferencialmente com commit claro ou squash referenciando o card.

8. Siga `alan-workflow` para higiene Git/worktree/stash; no cripto, stash nao e armazenamento principal de entrega.
   - Antes de iniciar segunda change, rode `git status --short` e isole o trabalho em branch/worktree propria.
   - Use stash apenas como protecao temporaria, sempre com nome, hash, arquivos incluidos, motivo e comando de recuperacao.
   - Branches de change devem ser apagadas no fechamento final, depois que o conteudo entrar em `main`/`Pronto`, e somente se nao houver commits exclusivos pendentes.

9. Sempre utilizar subagentes quando houver tarefa de desenvolvimento, investigacao, validacao ou revisao tecnica com ganho claro de paralelismo.
   - O agente principal continua responsavel por escopo, consolidacao, evidencias e fechamento.
   - A sessao principal do opencode define o LLM/modelo e a versao da tarefa; todo subagent deve herdar exatamente esse mesmo LLM/modelo e versao.
   - Papéis, prompts, sandbox e ownership podem variar, mas nenhum subagent pode trocar de LLM/modelo, usar fallback ou aplicar roteamento fixo Sol/Luna/Terra.
   - Se a igualdade do LLM/modelo nao puder ser imposta e observada, nao criar o subagent; continuar na sessao principal ou registrar o bloqueio.
   - Para critica ou revisao independente, usar contextos separados e manter o subagent read-only; a sessao principal consolida e corrige.

10. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

11. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md` e em `alan-workflow`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, isolamento por branch, pedido explicito de lote/release ou merge manual.

12. Toda tela, componente visual ou funcionalidade com impacto de UI/UX deve seguir obrigatoriamente o `DESIGN.md`.
   - Vale para telas novas e antigas, ajustes pequenos, refactors visuais, cards de produto e correcoes de interface.
   - Antes de implementar, consultar `DESIGN.md` e registrar no OpenSpec/hand-off quais tokens, componentes, padroes e excecoes foram aplicados.
   - Validacao visual e tecnica deve confirmar aderencia ao `DESIGN.md`; se houver desvio necessario, registrar justificativa antes de fechar a entrega.

13. Playwright visual e obrigatorio no QA de todo card por padrao, inclusive sem mudanca em `frontend/**`.
   - Dispensa so vale com label `qa-visual-skip` e comentario explicito de Alan no card no formato `QA visual dispensado por Alan.` seguido de motivo.
   - Label isolada, comentario isolado, filtro de path ou variavel de repositorio nao autorizam skip.
   - `Done` exige `qa-gate` verde, artifacts/evidencias quando aplicaveis, integracao em `develop`, `./restart` e URL servindo o resultado novo.
