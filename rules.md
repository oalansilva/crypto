# Regras Operacionais do Projeto

Este arquivo define as regras obrigatorias e curtas do projeto. O `AGENTS.md` detalha como executar cada regra na pratica.

## Escopo dos arquivos

- `rules.md`: politica normativa, curta e obrigatoria. Use para decidir o que nunca pode ser pulado.
- `AGENTS.md`: manual operacional detalhado. Use para comandos, ordem de execucao, mapeamento OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Em caso de duvida ou conflito, siga a regra mais restritiva. Se ainda houver ambiguidade, pare e registre o conflito antes de alterar codigo, card ou Git.
- Regras gerais do modo de trabalho do Alan ficam em `.cursor/skills/covenant-flow/` neste repo. O Cursor Agent aplica os overlays deste arquivo e de `AGENTS.md`. Não depender de `~/.codex/skills/` nem de disco hermes para essas skills.

## Regras obrigatorias

1. Siga `covenant-flow` para o ciclo global de card, OpenSpec, evidencias, status, release, higiene Git/worktree/stash e fechamento.
   - No cripto, OpenSpec e obrigatorio para qualquer alteracao de codigo, independente de tamanho ou complexidade.
   - Toda mudanca de codigo deve ter trilha em `openspec/changes/<change>/` antes da implementacao e evidencia de validacao antes do fechamento.

2. Quando Alan pedir implementacao por card (`#99`, por exemplo), aplique `covenant-flow` com os overlays do cripto.
   - Board: GitHub Project `MVP Cripto - Beta Fechado` / Project 1.
   - Branch base de implementacao: `develop`.
   - Branch padrao: `change-<id>-<slug>` ou `card-<id>-<slug>`.
   - Integracao tecnica antes de homologacao: merge/squash em `develop`.
   - Runtime de validacao: `./restart` e URL do sistema servindo o resultado novo.
   - Nessa etapa nao arquivar OpenSpec, nao abrir PR para `main` e nao publicar.

3. No cripto, o campo `Status` e a fonte principal das colunas. O campo `Fluxo`, quando existir, e substatus/legado; se houver divergencia, `Status` prevalece.
   - `Em Refinamento`: primeira coluna e entrada obrigatoria de todo card novo; Alan escolhe, prioriza (campo `Prioridade`) ou cancela o card antes de ir para `Todo`. Cards kaizen tambem nascem aqui.
   - `Todo`: backlog ou pronto para comecar.
   - `Design`: Designer/Critic Agent prepara prototipo, critica e evidencias.
   - `Aprovação de Design`: entrega de design completa aguardando Alan.
   - `Pronto para Dev`: Alan aprovou o design por arraste; desenvolvimento liberado.
   - `Em desenvolvimento`: o Cursor Agent/Clara esta trabalhando ou validando tecnicamente.
   - `Code Review`: diff pronto para os reviewers locais (`diff-reviewer` + `code-reviewer`, `inherit`/readonly) antes do commit; achados bloqueantes corrigidos ou classificados. Pré-commit: uncommitted vs HEAD. Fechamento: `origin/develop...HEAD` na branch do card, antes de QA. `/review-bugbot` só se Alan pedir. Autofix não commita na branch existente. Agent Review automático pós-commit permanece desligado.
   - `QA`: SHA revisado em validacao automatizada; `qa-gate` e Playwright visual precisam atingir resultado terminal verde.
   - `Done`: Done tecnico; QA verde, codigo integrado em `develop`, `./restart` e runtime validados, aguardando teste/aprovacao do Alan.
   - `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
   - `Pronto`: alteracao ja subiu para `main`/producao com evidencia **incluindo deploy em PROD** (source PROD no commit publicado + services reiniciados + URL publica validada); este e o fechamento final.
   - `Cancelado`: nao sera feito ou foi substituido (terminal; acionavel inclusive a partir de `Em Refinamento`).
   - Caminho obrigatório de todo card: `Em Refinamento -> Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`.
   - **Guardrail anti-bypass de Design:** nenhum card pode pular `Em Refinamento` (entrada obrigatoria), `Design`, `Aprovação de Design` ou `Pronto para Dev`. Vale para UI e não-UI, remoções, bugs, docs técnicas com card e pedidos `implemente`/`pode codar`. Não existe bypass `Todo -> Pronto para Dev` nem `Todo -> Em desenvolvimento`.
   - Somente Alan autenticado aprova `Aprovação de Design -> Pronto para Dev`; agentes nunca autoaprovam. Mudança no design/protótipo aprovado invalida o gate.
   - **Evidência obrigatória:** nenhum codigo e aplicado sem evidencia registrada de aprovacao de Design (comentario de Alan no card ou arraste `Aprovação de Design -> Pronto para Dev`). Vale para todo card, inclusive `UI impact: none`, remocoes, bugs e tooling. Veredito `BLOCKED` exige secao de resolucao no `design.md` (o que bloqueou, como foi resolvido, quem aprovou) antes de avancar; `BLOCKED` sem resolucao bloqueia o card.
   - **Checklist de gates no PR/commit de integracao:** o PR e o commit de squash devem listar change OpenSpec, `design.md`/verdict, `UI impact` e evidencia de aprovacao de Design (link do comentario ou arraste), inclusive para tooling/docs; `/opsx:verify` valida a checklist e PR sem gates nao e integrado.
   - **`UI impact: affected` no apply:** o protótipo aprovado (`frontend/public/prototypes/<slug>/`) é a spec de layout. Contrato de API não substitui o protótipo. Handoff sem consulta ao protótipo bloqueia o apply.
   - Task de UI só fecha `[x]` com evidência no código/spec. `/opsx:verify` e Code Review tratam `[x]` sem implementação como CRITICAL. Task de Playwright/frontend `[ ]` bloqueia `Done`.
   - Código de produção / `/opsx:apply` só depois de `Status=Pronto para Dev`. Pedido de implementação antecipa OpenSpec/Design, não autoriza pular colunas.
   - Falha de QA que exige codigo: `QA -> Em desenvolvimento -> Code Review -> QA`; falha de infraestrutura permanece em `QA` para rerun documentado.
   - Nao descreva `Status=Done` como card fechado/finalizado; use `Done tecnico` ou `aguardando homologacao`.

4. Todo card em `Status=Design` usa o contrato canônico `.agents/skills/design-critic/SKILL.md` antes da implementação.
   - No Cursor, invoca-se a skill `design-critic` (carregada de `.agents/skills/`). Grok lê o stub e o mesmo canônico (MUST Read). Sem fork da lei em `.grok/`.
   - **Avaliação** (UI affected) permanece intacta: pipeline `context -> shape -> prototype -> critique -> audit -> targeted fixes -> polish -> browser gate`, rubrica, dual critic, detector, browser, zero P0/P1. O `DESIGN.md` não pode ser sobrescrito. O hook `.cursor/hooks.json` roda o detector automaticamente em edições de UI e no fim de turno.
   - **Emissão:** chat e seções Impeccable/Design Critique de `design.md` levam só bullets P0–P3, disposition e verdict. Proibido tabela Nielsen, ensaio de personas ou Brief/Critique/Audit/Trace integrais no chat ou no `design.md`. Relatório longo em `.impeccable/critique/` (git-tracked), linkado no card; apply e Code Review **não lêem** o snapshot. Snapshot vazio em UI affected ⇒ `BLOCKED`.
   - Assessment A e Assessment B usam `Task` isolada no mesmo modelo do chat, prompt autocontido, **sem inherit de transcript**; podem escrever só `.impeccable/critique/**`. Sem crítica isolada o veredito permanece `BLOCKED`; não usar fallback.
   - Com `UI impact: none`, ainda passa por `Design` e `Aprovação de Design`; a entrega de design é enxuta (decisão, escopo, riscos, `Design Critique` em bullets) e registra explicitamente a ausência de superfície visual nova.
   - Com `UI impact: none`, registrar Impeccable como `N/A` com justificativa; isso não reduz nenhum gate.
   - Protótipo HTML, quando houver, deve ser navegável em `frontend/public/prototypes/<slug>/` via URL DEV; o Gist OpenSpec lista só Markdown e nunca HTML. Design/critics usam URL + digest, não dump de HTML.
   - **Fidelidade ao sistema atual:** quando a tela/rota/shell já existir no produto, o protótipo MUST partir do UI atual (shell, nav, tokens, densidade, componentes) e redesenhar só a mudança em cima dele, para Alan validar o delta. Proibido inventar layout/marketing paralelo. Tela nova (ainda inexistente) pode ser desenhada do zero, ainda assim obedecendo `DESIGN.md` e o shell do app quando for superfície autenticada.
   - **Validação obrigatória do protótipo:** antes de `Design Agent verdict: PASS`, abrir a URL final em navegador real, validar desktop/mobile, estado padrão, interações e asserts dos critérios críticos. Para remoção, provar que o elemento não está visível/existe no estado final. HTTP 200, build, leitura do HTML ou `curl` não bastam. Registrar URL, viewports, ações/asserts e resultado em `design.md` (`## Prototype Validation`). Qualquer falha ou navegador indisponível mantém `BLOCKED`.
   - Depois de qualquer alteração no protótipo ou rebuild/restart, repetir a validação no navegador; evidência anterior fica inválida.
   - O agente pode mover somente `Design -> Aprovação de Design` quando a evidência estiver completa; nunca pode executar a aprovação humana.

5. Homologacao e release seguem `covenant-flow`.
   - No cripto, homologacao e aprovacao funcional em `develop`.
   - So comandos explicitos de lote/release autorizam qualquer acao em `main`.

6. Quando Alan pedir `subir lote`, `fechar lote`, `fechar release` ou equivalente, execute `covenant-flow` + `covenant-flow-environments` com fechamento de producao dos cards `Homologado`.
   - Nao usar auto-merge.
   - Se `develop` contiver mudanca nao homologada, nao fazer merge direto `develop -> main`; usar branch `release-*` com somente conteudo aprovado ou pedir decisao de Alan.
   - Usar `scripts/release-guard pre` antes de abrir/mesclar PR e `scripts/release-guard post` depois da publicacao.
   - **Deploy em PROD e obrigatorio antes de mover qualquer card para `Pronto`:** em `/srv/apps/prod/criptofarol/source`, atualizar para o commit publicado (`git fetch origin && git reset --hard origin/main`), aplicar migrations (`alembic upgrade head`), buildar o frontend (`VITE_APP_ENV=production`) e reiniciar os services PROD afetados, validando o endpoint publico `https://criptofarol.com.br`. Merge em `main` sem deploy e validacao em PROD nao autoriza `Pronto`.

7. Branches e testes seguem `covenant-flow`; no cripto, evitar commit direto em `develop` enquanto a implementacao estiver parcial.
   - Integrar em `develop` somente quando a change estiver pronta para teste integrado/homologacao, preferencialmente com commit claro ou squash referenciando o card.

8. Siga `covenant-flow` para higiene Git/worktree/stash; no cripto, stash nao e armazenamento principal de entrega.
   - Antes de iniciar segunda change, rode `git status --short` e isole o trabalho em branch/worktree propria.
   - Use stash apenas como protecao temporaria, sempre com nome, hash, arquivos incluidos, motivo e comando de recuperacao.
   - Branches de change devem ser apagadas no fechamento final, depois que o conteudo entrar em `main`/`Pronto`, e somente se nao houver commits exclusivos pendentes.

9. Sempre utilizar subagentes quando houver tarefa de desenvolvimento, investigacao, validacao ou revisao tecnica com ganho claro de paralelismo.
   - O agente principal continua responsavel por escopo, consolidacao, evidencias e fechamento.
   - O modelo selecionado no chat do Cursor define o LLM da tarefa; todo subagent/`Task` deve herdar esse modelo (`inherit`) salvo pedido explícito de Alan.
   - Papéis e prompts podem variar; nenhum subagent troca de modelo por conta própria nem aplica roteamento Sol/Pro/Qwen.
   - Para critica ou revisao independente, usar Task isolada instruída a não editar; a sessão principal consolida e corrige.
   - **Análise de imagem:** a sessão lê pixels com `Read` depois do path-check. Sem `vision-router` e sem Qwen obrigatório.
   - **Gate Design:** a sessão Cursor escreve artifacts e o protótipo; crítica em Task isolada no mesmo modelo. Sem lease, packet, `design_artifact_write` ou attestation OpenCode.

10. PostgreSQL e obrigatorio em runtime, QA, homologacao e scripts operacionais.
   - Nao usar SQLite como banco de operacao.

11. Apos validacao e evidencia, o agente tem autonomia para executar o fluxo manual de fechamento previsto no `AGENTS.md` e em `covenant-flow`, sem solicitar nova autorizacao para cada etapa.
   - Essa autonomia nao autoriza pular teste, OpenSpec, homologacao, isolamento por branch, pedido explicito de lote/release ou merge manual.

12. Toda tela, componente visual ou funcionalidade com impacto de UI/UX deve seguir obrigatoriamente o `DESIGN.md`.
   - Vale para telas novas e antigas, ajustes pequenos, refactors visuais, cards de produto e correcoes de interface.
   - Antes de implementar, consultar `DESIGN.md` e registrar no OpenSpec/hand-off quais tokens, componentes, padroes e excecoes foram aplicados.
   - Validacao visual e tecnica deve confirmar aderencia ao `DESIGN.md`; se houver desvio necessario, registrar justificativa antes de fechar a entrega.

13. Playwright visual e obrigatorio no QA de todo card por padrao, inclusive sem mudanca em `frontend/**`.
   - Dispensa so vale com label `qa-visual-skip` e comentario explicito de Alan no card no formato `QA visual dispensado por Alan.` seguido de motivo.
   - Label isolada, comentario isolado, filtro de path ou variavel de repositorio nao autorizam skip.
   - Rota nova em `App.tsx` sem spec Playwright funcional+visual falha o job `new-route-playwright-coverage` e portanto o `qa-gate`. O inventário `frontend/tests/e2e/route-coverage-inventory.json` grandfather as rotas atuais; skip silencioso de rota nova e proibido.
   - `Done` exige `qa-gate` verde, artifacts/evidencias quando aplicaveis, integracao em `develop`, `./restart` e URL servindo o resultado novo.

14. Kaizen e a melhoria continua de processo: quanto mais o processo e usado, melhor ele fica.
   - Toda release/lote roda `/kaizen release` apos o deploy PROD validado e antes de mover cards para `Pronto`; evidencia em `docs/kaizen-log.md`.
   - O Kaizen audita board, Git hygiene, OpenSpec, CI, tech debt e sessões Cursor (transcripts do projeto), detectando onde o modelo se perde ou alucina.
   - Melhorias sao registradas como cards: 1 card por melhoria, formato PO, label `kaizen`, **sempre em `Status=Em Refinamento`** (entrada obrigatoria de todo card novo; nunca em coluna de execucao), seguindo o fluxo normal do board (`Em Refinamento -> Todo -> ...`).
   - **Maximo 3 cards kaizen por release**; a priorizacao (campo `Prioridade` P0/P1/P2, regra severidade x frequencia / esforco) define os 3 que entram; o restante fica no backlog kaizen.
   - Kaizen propoe, Alan aprova: o agente nunca implementa mudancas de regra/skill/script sem aprovacao explicita; pode propor melhorias de skills e pesquisar alternativas (busca read-only).
   - Issues publicas: apenas metricas agregadas e IDs; trechos de sessoes somente em `docs/kaizen-log.md`.
