# Regras Operacionais do Projeto

Este arquivo define as regras obrigatorias e curtas do projeto. O `AGENTS.md` detalha como executar cada regra na pratica.

## Escopo dos arquivos

- `rules.md`: politica normativa, curta e obrigatoria. Use para decidir o que nunca pode ser pulado.
- `AGENTS.md`: manual operacional detalhado. Use para comandos, ordem de execucao, mapeamento OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Em caso de duvida ou conflito, siga a regra mais restritiva. Se ainda houver ambiguidade, pare e registre o conflito antes de alterar codigo, card ou Git.
- Regras gerais do modo de trabalho do Alan ficam na skill global `alan-workflow` quando ela estiver disponível no cliente. Codex e Cursor devem aplicar os mesmos overrides versionados neste arquivo e em `AGENTS.md`; o fluxo do projeto não depende de um caminho absoluto local.

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
   - `Em desenvolvimento`: Codex/Clara esta trabalhando ou validando tecnicamente.
   - `Code Review`: diff pronto para revisao Codex antes do commit; achados bloqueantes corrigidos ou classificados.
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
   - Codex invoca `$design-critic`; Cursor invoca `/design-critic`.
   - Com `UI impact: affected`, o agente produz/refatora o prototipo, critica produto/UX/acessibilidade/responsividade/estados e registra o veredito no `design.md`.
   - Com `UI impact: none`, ainda passa por `Design` e `Aprovação de Design`; a entrega de design é enxuta (decisão, escopo, riscos, `Design Critique`) e registra explicitamente a ausência de superfície visual nova.
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

10. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

11. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md` e em `alan-workflow`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, isolamento por branch, pedido explicito de lote/release ou merge manual.

12. Usar a skill `caveman` em modo `lite` como padrao de comunicacao com Alan.
   - Manter respostas curtas, diretas e sem filler, preservando clareza tecnica, seguranca e ordem correta em instrucoes criticas.
   - Desativar somente quando Alan pedir explicitamente `stop caveman` ou `normal mode`.

13. Toda tela, componente visual ou funcionalidade com impacto de UI/UX deve seguir obrigatoriamente o `DESIGN.md`.
   - Vale para telas novas e antigas, ajustes pequenos, refactors visuais, cards de produto e correcoes de interface.
   - Antes de implementar, consultar `DESIGN.md` e registrar no OpenSpec/hand-off quais tokens, componentes, padroes e excecoes foram aplicados.
   - Validacao visual e tecnica deve confirmar aderencia ao `DESIGN.md`; se houver desvio necessario, registrar justificativa antes de fechar a entrega.

14. Playwright visual e obrigatorio no QA de todo card por padrao, inclusive sem mudanca em `frontend/**`.
   - Dispensa so vale com label `qa-visual-skip` e comentario explicito de Alan no card no formato `QA visual dispensado por Alan.` seguido de motivo.
   - Label isolada, comentario isolado, filtro de path ou variavel de repositorio nao autorizam skip.
   - `Done` exige `qa-gate` verde, artifacts/evidencias quando aplicaveis, integracao em `develop`, `./restart` e URL servindo o resultado novo.

15. No Codex, o roteamento de modelo e fixo por etapa e automatico.
   - Design/OpenSpec e QA usam a sessao principal `gpt-5.6-sol` com effort `high`.
   - `Em desenvolvimento` usa `crypto_luna_implementer`; `Code Review` usa nova `crypto_luna_reviewer` read-only; release explicitamente solicitada usa nova `crypto_luna_release_manager`. As tres usam `gpt-5.6-luna` com effort `max` e `fork_turns="none"`.
   - `/opsx:apply` pertence a Luna implementer; `/opsx:verify` pertence a Sol QA; sync/archive so podem ocorrer dentro de release explicitamente autorizada e pertencem a Luna release manager.
   - Nao selecionar por complexidade, nao usar Terra, built-ins ou fallback. Perfil/modelo/effort/sandbox/permission profile nao observavel, conflitante ou divergente bloqueia a etapa; `fork_turns="none"` deve ser provado separadamente pelo pedido/resultado de spawn controlado pelo orquestrador. O inspector local prova somente os cinco campos runtime allowlisted e nunca prova `fork_turns`; sem spawn controlado a etapa bloqueia. Um sandbox efetivo mais amplo que o pedido nao bloqueia sozinho quando a contenção comportamental e a auditoria antes/depois passam.
   - O bootstrap que instala os perfis e aceito por TOML/catalogo/skill/testes/OpenSpec estaticos e revisao Codex independente read-only. Nenhuma lane e pre-spawned; runtime e exigido somente quando a lane Luna for usada naturalmente por tarefa nova depois da configuracao versionada e carregada.
   - Nao alterar AppArmor, sysctl, bubblewrap, user namespaces, sandbox launcher ou seguranca do host/servidor para provar o roteamento. Diagnostico pre-ativacao bloqueado nao substitui nem invalida a aceitacao estatica.
   - Depois da ativacao, Code Review exige a Luna reviewer exata; a excecao de review Codex independente vale somente para o bootstrap.
   - Toda lane Luna usa contenção comportamental: pacote autocontido, ownership exato, ações permitidas/proibidas, limites externos e inventário/digest antes/depois. Reviewer exige **nenhuma mutação observada dentro do inventário obrigatório** para cada repo/worktree nomeado: `GIT_OPTIONAL_LOCKS=0` nos reads Git, worktree list, HEAD/branch, refs/branches/tags, stash, config/hooks, tracked/untracked/ignored nos roots declarados e digests de conteúdo/links. Isso não significa zero mutação global; paths/repos do host, leituras/rede/ações externas sem API auditável e roots ignored excluídos por custo são risco residual. Qualquer diferença ou exclusão não declarada bloqueia e o reviewer não repara. Implementer só altera caminhos atribuídos; release manager só atua no pacote Homologado autorizado.
   - O sandbox ampliado é risco residual explícito e não oferece isolamento forte do sistema operacional; uma proteção runtime mais estreita é defesa adicional, não substitui a auditoria nem autoriza mudar segurança do host.
   - Cursor e outros clientes ficam fora da implementacao e validacao deste roteamento automatico.
