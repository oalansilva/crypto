# AGENTS.md — Guia rapido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## Escopo deste arquivo

- `rules.md` define as regras obrigatorias curtas do projeto.
- `AGENTS.md` define como executar essas regras na pratica: comandos, status, evidencias, OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Use os dois arquivos. Em conflito real, aplique a regra mais restritiva e registre a ambiguidade antes de alterar codigo, card ou Git.

## TL;DR

- **Branch padrão:** trabalhe em `develop` para trabalho diário de implementação e validações.
- **Comunicação padrão com Alan:** usar sempre a skill `caveman` em modo `lite`: curto, direto, sem filler, mantendo clareza técnica. Só desligar se Alan pedir explicitamente `stop caveman` ou `normal mode`.
- **Fluxo de status:** `In Progress` = em execução; `Done` = codificado e validado tecnicamente em `develop`; `Homologado` = Alan testou e aprovou em `develop`; `Pronto` = já subiu para `main`/produção.
- **Fluxo de produção:** implemente e valide diretamente em `develop`; acumule cards homologados quando fizer sentido; para liberar produção, abra PR `develop -> main`, resolva checks/políticas bloqueantes quando possível e realize o merge manual quando permitido, sem auto-merge.
- **Regra de fluxo:** use somente `develop` e `main`; sem criação de branches por tasks usuais.
- **Regra de merge de release/lote:** após abrir um PR de `develop -> main` dentro de um fechamento de lote/release solicitado por Alan, execute o merge manualmente quando os checks estiverem verdes e não houver bloqueios.
- **Regra de autonomia operacional:** dentro de fechamento de lote/release solicitado por Alan, após validação e evidência, o agente tem autonomia para repetir tentativas manuais de merge até resolução de bloqueios resolvíveis no repositório, sem pedir nova autorização.
- **Regra de implementação por card:** ao receber pedido com número de card (ex.: `#99`), localizar o card no board `github.com/users/oalansilva/projects/1`, mover para `In Progress`, executar usando OpenSpec e subagents conforme o escopo, rodar `/opsx:verify`, executar `./restart`, e só então mover o card para `Done`. Não arquivar nem commitar nesta etapa.
- **Regra de homologação direta por card (solicitação do cliente):** quando Alan disser que um card está homologado, mova o card de `Done` para `Homologado` sem abrir PR, sem merge em `main` e sem arquivar OpenSpec automaticamente. Homologação aqui significa aprovação funcional em `develop`.
- **Guardrail anti-release acidental:** as frases `card homologado`, `cards homologados`, `está homologado`, `homologuei`, `aprovado em develop` ou equivalentes significam somente atualizar status para `Homologado`. Elas **não autorizam** commit, PR, merge, archive, release ou qualquer ação em `main`.
- **Regra de release/lote:** quando Alan pedir `subir lote`, `fechar lote`, `fechar release` ou equivalente, selecione os cards `Homologado`, rode validação final, arquive as changes OpenSpec correspondentes, faça commit único do lote em `develop`, push, PR `develop -> main`, merge manual, atualize `develop` e mova os cards incluídos para `Pronto`.
- **Regra de não regressão de status:** depois que um card estiver em `Done`, nunca mova de volta para `In Progress` durante homologação, archive, commit, PR ou merge. Se aparecer falha, ajuste necessário ou reteste, corrija e reteste mantendo o status atual. O card só avança: `Done` -> `Homologado` -> `Pronto`.
- **Regra de confiabilidade por testes:** em qualquer etapa, se surgir erro de testes (locais ou CI), corrija, revalide e só então siga para próxima etapa de encerramento.
- **Regra de validação OpenSpec global:** `openspec validate --all` verde é critério padrão de fechamento. Se falhar por changes antigas fora do card, valide os specs afetados pelo card como evidência parcial, mas resolva a sujeira global antes do encerramento: corrija ou arquive as changes antigas, inclusive por archive manual quando a CLI/skill não conseguir concluir.
- **Regra de checks em execução:** teste, build ou CI iniciado precisa ser acompanhado até terminar. Status como "build está rodando" é atualização intermediária, não evidência final para `Done`, release/lote, commit, PR ou merge.
- **Regra de commit único por lote/release:** não faça commit durante implementação nem ao mover card para `Homologado`. O commit ocorre no fechamento do lote/release, após homologação funcional dos cards incluídos. Se CI/checks falharem depois do push, corrija preservando um commit final sempre que tecnicamente possível (ex.: amend + push seguro); se isso não for possível sem risco, registre a exceção e o motivo.
- **Regra de worktree limpo no fechamento:** antes de `Done`, release/lote, commit, PR ou merge, rode `git status --short` e não deixe nenhum arquivo modificado solto sem classificação. Arquivos da entrega entram no commit único do lote; alterações alheias/preexistentes ficam fora do commit e devem ser preservadas com stash nomeado ou registro equivalente e reportadas com caminho e motivo. Nunca descarte alteração alheia sem pedido explícito.
- **Banco padrão:** PostgreSQL é obrigatório em runtime, QA e scripts operacionais (`DATABASE_URL` e `WORKFLOW_DATABASE_URL` em formato PostgreSQL).
- **Não usar SQLite** como banco de operação. Em runtime/QA/Homologação, use apenas PostgreSQL (`DATABASE_URL` e `WORKFLOW_DATABASE_URL`).
- **Funcionalidades novas:** siga OpenSpec por padrão antes de implementar (`openspec/changes/<change>/` com proposal/spec/design/tasks quando aplicável).
- **Regra obrigatória de criação via OpenSpec:** ao iniciar uma mudança por card, execute o fluxo ` /opsx:new ──► /opsx:ff ──► /opsx:apply ──► /opsx:verify ` antes de mover para `Done`; execute `/opsx:archive` somente no fechamento de lote/release para produção.
  - Se o projeto ainda não estiver inicializado com OpenSpec, rode `openspec init` e então comece o fluxo.
- **Observação de fluxo OpenSpec:** use os comandos nesta ordem para mudanças novas; ajuste a cadência apenas com justificativa explícita.
- **Subagents:** use subagents sempre que houver ganho claro de paralelismo, investigação independente, validação especializada ou aceleração sem duplicar trabalho.
- OpenSpec é a camada de especificação técnica (artifacts).
- Workflow DB e OpenSpec são fontes de operação e evidência.

## De-para OpenSpec/OPSX no Codex

Quando o cliente Codex não interpretar `/opsx:*` como slash command, trate o texto como intenção operacional e acione a skill local equivalente. Não substitua a skill por criação manual de arquivos.

Regra obrigatória:
- Primeiro use a skill OpenSpec correspondente.
- Depois execute a CLI `openspec` indicada pela própria skill.
- Só crie ou edite arquivos em `openspec/changes/<change>/` seguindo `openspec instructions ... --json`.
- Não invente artefatos manualmente fora do fluxo da skill.
- Ao final de cada etapa, registre no handoff/status qual skill foi usada, qual comando CLI foi executado e qual evidência foi produzida.

De-para principal:

| Intenção / comando | Skill Codex obrigatória | CLI base | Resultado esperado |
| --- | --- | --- | --- |
| `/opsx:new <change>` | `$openspec-new-change` | `openspec new change "<change>"`; `openspec status --change "<change>"`; `openspec instructions <artifact-id> --change "<change>"` | Cria apenas o scaffold da change, mostra status e instrução do primeiro artifact. Não cria artifacts ainda. |
| `/opsx:ff <change>` | `$openspec-ff-change` | `openspec status --change "<change>" --json`; `openspec instructions <artifact-id> --change "<change>" --json` | Gera todos os artifacts necessários para ficar pronto para implementação, respeitando dependências e templates retornados pela CLI. |
| `/opsx:apply <change>` | `$openspec-apply-change` | `openspec status --change "<change>" --json`; `openspec instructions apply --change "<change>" --json` | Lê `contextFiles`, implementa as tasks pendentes e marca checkboxes em `tasks.md` somente após concluir cada item. |
| `/opsx:verify <change>` | `$openspec-verify-change` | `openspec list --json` quando a change estiver ambígua; `openspec status --change "<change>" --json`; `openspec instructions apply --change "<change>" --json` | Verifica completude, corretude e coerência entre artifacts, specs, tasks, design, testes e implementação real. |
| `/opsx:archive <change>` | `$openspec-archive-change` | `openspec status --change "<change>" --json`; avaliar sync de specs; mover para `openspec/changes/archive/YYYY-MM-DD-<change>/` | Arquiva somente no fechamento de lote/release após homologação, checando artifacts, tasks, delta specs e registrando warnings se algo ficar incompleto. |

De-para complementar:

| Intenção / comando | Skill Codex obrigatória | Uso correto |
| --- | --- | --- |
| `/opsx:continue <change>` | `$openspec-continue-change` | Continuar a criação do próximo artifact pronto, usando `openspec status` e `openspec instructions`, sem pular dependências. |
| `/opsx:sync <change>` | `$openspec-sync-specs` | Sincronizar delta specs de `openspec/changes/<change>/specs/` para `openspec/specs/` antes ou durante o archive, conforme avaliação da skill. |
| `/opsx:bulk-archive` | `$openspec-bulk-archive-change` | Arquivar várias changes concluídas, uma a uma, preservando evidência e warnings por change. |
| `/opsx:onboard` | `$openspec-onboard` | Fazer onboarding guiado do fluxo OpenSpec antes de iniciar implementação quando o contexto operacional estiver confuso. |

Fluxo canônico para implementação por card:

```text
/opsx:new <change>
  -> usar $openspec-new-change
  -> criar scaffold e identificar primeiro artifact

/opsx:ff <change>
  -> usar $openspec-ff-change
  -> gerar artifacts até apply-ready

/opsx:apply <change>
  -> usar $openspec-apply-change
  -> implementar tasks e atualizar tasks.md

/opsx:verify <change>
  -> usar $openspec-verify-change
  -> validar artifacts versus implementação e testes
```

Fechamento de lote/release após homologação:

```text
/opsx:archive <change>
  -> usar $openspec-archive-change
  -> sincronizar specs quando aplicável e arquivar a change
```

Se o agente criar `proposal.md`, `design.md`, `tasks.md`, `specs/**` ou mover arquivos para `archive/` sem declarar a skill OpenSpec usada, considere o fluxo incompleto e corrija antes de avançar para DEV, QA, homologação ou merge.

### Falhas antigas em `openspec validate --all`

- Primeiro confirme a change atual: `openspec status --change "<change>" --json` precisa estar completo e os specs afetados pelo card precisam validar individualmente.
- Se `openspec validate --all` falhar por changes antigas, trate como bloqueio de higiene do repo, não como exceção permanente. Investigue cada change quebrada, corrija artifacts quando ela ainda estiver ativa ou arquive quando estiver concluída/obsoleta.
- Use primeiro a skill OpenSpec adequada, normalmente `$openspec-archive-change`. Se a CLI/skill falhar por estado antigo ou inconsistente, o archive manual é permitido como exceção operacional: mover para `openspec/changes/archive/YYYY-MM-DD-<change>/`, sincronizar specs quando aplicável, preservar evidência no handoff e registrar por que o caminho manual foi usado.
- Depois do saneamento, rode novamente `openspec validate --all`. Validação parcial serve apenas como evidência intermediária para o escopo do card, não como fechamento final.

## Fluxo Git operacional (sempre)

- Trabalhe sempre em `develop`; não crie `feature/*`, `bugfix/*` ou outras branches para tarefas isoladas.
- Não faça commit durante a implementação (nem por subetapas) nem ao mover card para `Homologado`. O único commit ocorre no fechamento de lote/release.
- Abra PR de `develop` para `main` para liberar produção somente quando Alan pedir explicitamente `subir lote`, `subir release`, `fechar lote`, `fechar release` ou equivalente claro. Homologação de card não é pedido de release.
- O merge em `main` é o passo final de produção. Após merge, os cards incluídos no lote avançam de `Homologado` para `Pronto`.
- **Regra mandatória nova (independente do tamanho):** antes de qualquer alteração de código, iniciar sempre com OpenSpec em `openspec/changes/<change>/` (proposta, escopo, critérios e evidência) e só então codar.
- **Regra de autonomia operacional:** dentro de fechamento de lote/release solicitado por Alan, após validação e evidência, o agente deve executar ações de merge e retentativas manuais previstas no fluxo sem solicitar autorização adicional do usuário.
- Sempre que houver PR aberto de lote/release e o bloqueio for apenas de checks ainda pendentes, o agente deve repetir a tentativa manual de merge até completar (ou até novo bloqueio de política/conflito que exija revisão humana).
- Se o merge for bloqueado por checks, conflitos ou políticas resolvíveis por alteração no repo, o agente deve investigar, corrigir, revalidar e preservar a regra de commit único sempre que tecnicamente seguro.
- Se o bloqueio depender de permissão/admin/review humano/configuração externa não editável pelo repo, o agente deve registrar o motivo exato no PR e na resposta final, sem mascarar o bloqueio como concluído.
- Após merge em `main`, atualize `develop` para refletir o estado da produção.
- Antes de preparar o commit único do lote/release, classifique todo `git status --short`: entrega atual, alteração alheia/preexistente, artifact gerado ou lixo descartável. A entrega atual entra no commit; alteração alheia não entra no commit do lote e não pode ficar perdida no worktree. Preserve com `git stash push -m "preserve unrelated before <release/change>: <paths>" -- <paths>` ou mecanismo equivalente e reporte o identificador.

Exemplo mínimo:
```bash
git switch develop
git pull
# ...alterações locais...
# ...validações locais e evidências...
# quando Alan pedir subir lote/release:
git add .
git commit -m "feat: fechar lote homologado"
git push
gh pr create --base main --head develop --title "..."
gh pr merge --merge --delete-branch=false

# após merge:
git pull
# mover cards incluídos para Pronto
```

Checklist de rotina (diária/por mudança):

1. `git switch develop`
2. `git pull`
3. aplicar alteração
4. validar localmente e preparar evidências
5. antes do commit: revisar `git status --short` e resolver todo arquivo solto sem incluir alteração alheia no card
6. se Alan homologar em `develop`, mover card de `Done` para `Homologado`, sem commit e sem PR
7. quando Alan pedir subir lote/release: arquivar OpenSpec das changes homologadas e rodar validação final
8. `git add .`
9. `git commit -m "tipo: mensagem do lote"`
10. `git push`
11. `gh pr create --base main --head develop --title "<titulo>" --body "descricao breve"`
12. Se houver pontos de falha antes do fechamento, investigue e corrija antes do commit de encerramento; evite novo ciclo de commit em lote para não quebrar a regra de commit único.
13. Faça o merge manualmente em `main` em seguida: `gh pr merge --merge --delete-branch=false`.
14. Após merge: `git pull`
15. Mover cards incluídos no lote para `Pronto`

Em entrega de código por card, use subagents por padrão para acelerar descoberta, implementação e validação, respeitando escopo e evitando trabalho duplicado.

Padrão de commit recomendado:
- `feat: adicionar fluxo de merge develop->main`
- `fix: corrigir validação de entrada no endpoint de backtest`
- `chore: atualizar documentação e scripts de desenvolvimento`
- `refactor: simplificar regra de configuração`
- `docs: registrar padrão operacional no AGENTS`

## Regras de operação

- Responsabilidade única: o agente principal conduz descoberta, planejamento, implementação, validação e fechamento, mesmo quando usar subagents para acelerar partes independentes.
- Novo requisito de produto/UX/tech deve gerar um item novo no GitHub (Issue) antes de virar tarefa ativa da sprint/turno; mudanças relacionadas a itens já fechados devem ser registradas em issue filha/linkada.
- Toda funcionalidade nova deve seguir o fluxo OpenSpec sempre que houver mudança de comportamento, UX, API, regra de negócio, dados, segurança, monitoramento ou operação. Antes de codar, crie/atualize `openspec/changes/<change>/` com escopo, decisões, tarefas e critérios de aceite proporcionais ao tamanho da mudança.
- Mudanças pequenas e localizadas podem usar OpenSpec enxuto, mas não devem pular a etapa quando alterarem contrato do produto ou comportamento observável.
- Sempre que possível, acelere o processo com subagents em tarefas médias/grandes, especialmente para mapear código, revisar riscos, validar UI/Playwright, investigar bugs ou dividir backend/frontend. O agente principal continua responsável por consolidar resultados e evitar trabalho duplicado.
- Registre em `openspec/changes/<change>/` e no PR:
  - status atual
  - decisões de escopo
  - evidências de teste/PR
- Para promover produção, trabalhe em `develop` (sem branch extra), junte os cards `Homologado` no lote/release pedido por Alan, abra PR de `develop -> main`, resolva checks/políticas bloqueantes quando forem corrigíveis por código/configuração do repo, realize o merge manual do PR e então mova os cards incluídos para `Pronto`.
- Política adicional: quando houver falha recorrente de unit tests de DB, aplique isolamento por teste (reset de tabelas/fixtures) antes de alterar regras de negócio.
- Ao registrar bloqueios de CI, incluir evidência e impacto de `Unit tests` e `Backend format` no comentário do PR, e manter esta orientação em `AGENTS.md` para repetição.
- Em workflows com `push` e `pull_request`, a `concurrency.group` deve diferenciar `github.event_name`; caso contrário, o run de `pull_request` pode cancelar o run de `push` do mesmo SHA em `develop`, deixando checks obrigatórios como `cancelled` e bloqueando o merge em `main`.

## Como rodar (VPS / dev)

### Backend (FastAPI)
- Porta padrão: **8003**
- Logs (quando usamos nohup): `/tmp/uvicorn-8003.log`

Exemplo:
```bash
cd backend
nohup ../backend/.venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn-8003.log 2>&1 &
```

### Frontend (Vite)
- Porta padrão: **5173**
- Logs (quando usamos nohup): `/tmp/vite-5173.log`

Exemplo:
```bash
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/vite-5173.log 2>&1 &
```

## Testes / checks

- Todo teste, build, lint, `openspec validate` ou CI iniciado precisa terminar antes de virar evidência. Se ainda estiver rodando, informe como status parcial e continue acompanhando até sucesso, falha corrigida ou bloqueio real.
- Em `Done`, rode validação OpenSpec da change e os testes proporcionais do card. Em fechamento de lote/release, rode validação OpenSpec global e checks finais; se a global falhar por changes antigas, saneie/arquive essas changes antes de concluir; não deixe a falha global herdada para Alan.

- Backend:
```bash
./backend/.venv/bin/python -m pytest -q
```

- Frontend build:
```bash
npm --prefix frontend run build
```

## Documentos úteis

- Visão geral: `README.md`
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- Workflow OpenSpec/Codex: `openspec/changes/` e `openspec/specs/`

## Convenções de UI/UX (Lab)

- Para qualquer tarefa em `frontend/`, use a skill local `$crypto-frontend` como padrão inicial de qualidade e validação visual.
- **Upstream** deve ser uma conversa fluida (Humano ↔ Trader) para clarificar inputs/constraints/risco.
- O label "validator" na UI/copy deve aparecer como **Trader**.

## Agentes e responsabilidades

O time é composto por 5 agentes, cada um com papel definido:

### main — Project Manager / Team Leader
**Template base:** Orion (productivity)

Orquestra o time, coordena workflow, delegation, status reports, prazos.
- Mantém conversa com Alan curta/gerencial, usando `caveman lite` como padrão permanente
- Consulte workflow DB e OpenSpec como fonte principal.
- Move status de mudança no workflow, celebra marcos, identifica riscos proativamente
- Fornece próximo passo após completar tarefa
- Pede clarifying questions quando necessário
- Dá estimates de tempo quando possível

### PO — Product Manager
Define especificações, gerencia backlog, Requirements, escopo do produto.
- Define taxonomia de work items (`change`, `story`, `bug`) e dependências
- É dono dos artefatos OpenSpec da change: `proposal.md`, `specs/**`, `design.md`, `tasks.md` e `review-ptbr.md`
- Só libera DEV depois de approval
- **Quando não há change ativa (todas arquivadas), o PO deve puxar a change de maior prioridade no status `Pending` para iniciar planejamento no próximo turno.**

### DESIGN — UX/UI Researcher
**Template base:** UX Researcher (creative)

Foca em UX/prototipação e pesquisa de usuário.
- Publica protótipos e decisões visuais na seção de handoff da change
- Complementa a planning package com protótipo visual e decisões de UX para DEV/QA
- Desenha pesquisas de usuário e scripts de entrevista
- Analisa feedback de usuários (tickets, reviews, pesquisas)
- Identifica problemas de usabilidade
- Gera relatórios com recomendações baseadas em evidências

### DEV — Software Engineer + Code Reviewer
**Template base:** Lens (development)

Implementa código +レビュー automática.
- Implementa com base no workflow DB + notas de handoff como runtime
- Respeita taxonomia `change`/`story`/`bug`, ownership, locks e dependências
- Faz code review: bugs, security issues, logic errors
- Scaneia vulnerabilidades (SQL injection, XSS, hardcoded secrets)
- Avalia qualidade (A-F), sugere melhorias

### QA — Tester + Bug Hunter
**Template base:** Trace (development)

Valida + análise profunda de bugs.
- Valida regressões, consistência do workflow DB e critérios de aceite
- Bugs reais viram `bug` rastreável; bugs filhos bloqueiam story
- Análise de erro: parse stack traces, identifica root cause vs symptoms
- Fornece steps de debug em ordem de probabilidade
- Cria bug reports com steps de reprodução e severidade

### Regras operacionais dos agentes
- O **workflow DB** é a fonte operacional de verdade.
- **OpenSpec** define artefatos e a trilha técnica.
- `openspec/changes/<change>/` é o canal padrão entre agentes, com menções `@PO`, `@DESIGN`, `@DEV`, `@QA`, `@Alan`.
- Nenhum agente (PO/DESIGN/DEV/QA) pode considerar sua etapa concluída só com artefatos; é obrigatório atualizar o runtime e registrar handoff no mesmo turno.
- Toda etapa só fecha de verdade com **runtime + handoff registrado**; se um dos dois faltar, o próximo turno deve reconciliar antes de seguir.
- O contrato operacional curto (papéis, handoff, DoD por status, bloqueios) fica consolidado no fluxo operacional do projeto.
- Quando Alan homologar uma change em chat, o orquestrador deve mover o card para `Homologado` no mesmo turno e registrar handoff/status. Archive OpenSpec, commit, PR, merge e mudança para `Pronto` acontecem apenas no fechamento de lote/release.
- `change` é o container raiz da entrega; `story` é a fatia padrão de execução quando houver ownership/dependência própria; `bug` representa defeito real. Não criar cards separados para micro-passos sem necessidade operacional.
- Múltiplas stories/agentes podem trabalhar em paralelo, desde que respeitem **locks**, **dependências** e **WIP**.
- Regra prática de WIP: por padrão, no máximo **2 stories ativas por change** e **1 story ativa por agent run**.
- **Regra de auto-trigger:** Quando o status da change avança no runtime, o agente responsável pela nova etapa deve ser acionado. Ex: status vira PO → acionar PO; vira DEV → acionar DEV; vira QA → acionar QA.
- **Regra de validação QA:** Antes de enviar para homologação Alan, QA deve rodar testes E2E (`frontend/tests/*.spec.ts`) e revisar evidências registradas no fluxo operacional.
- Lock padrão fica no nível da **story**; bug filho herda esse lock salvo reassignment explícito.
- Uma **story** só pode ser fechada quando todos os **bugs filhos** estiverem concluídos.
- Antes de promover para `QA`, `Homologation` ou `Archived`, reconciliar runtime + `openspec/changes/<change>/tasks.md` + handoff.

### Uso padrão de subagents Codex

Para tarefas médias ou grandes, o agente principal deve orquestrar subagents quando houver benefício claro de paralelismo, investigação independente ou revisão especializada.

Use subagents por padrão nestes casos:
- revisão de PR ou comparação `develop -> main`;
- investigação de bug sem causa clara;
- mudanças que envolvam backend + frontend;
- alterações com impacto em banco, segurança, autenticação ou dados financeiros;
- validação de UI com Playwright;
- mudanças OpenSpec com múltiplas etapas.

Não use subagents por padrão nestes casos:
- perguntas conceituais simples;
- alterações pequenas e localizadas;
- comandos diretos;
- ajustes textuais ou documentação pequena.

Arquitetura preferida:
- `code_mapper` para mapear fluxos, arquivos e pontos de edição;
- `pr_explorer` para revisar diffs, PRs e escopo de comparação;
- `browser_debugger` para reproduzir e investigar UI com evidências;
- `reviewer` para revisar riscos, regressões, segurança e testes;
- `worker` built-in para implementação quando necessário.

O agente principal continua responsável por consolidar decisões, evitar trabalho duplicado, respeitar o escopo do OpenSpec/workflow DB e entregar o resultado final.

## Engenharia de prompt

Reforço de fluxo de fechamento: `Done` conclui implementação validada em `develop`; `Homologado` conclui aprovação funcional de Alan em `develop`; `Pronto` conclui produção após merge manual em `main` (via PR `develop -> main`) com validação e evidências registradas.

Se for necessário mudar o tom de um agente (ex: deixar o design mais exploratório ou o DEV mais cauteloso), primeiro atualiza este arquivo com o novo prompt/personalidade e registra no `openspec/changes/<change>/` do fluxo ativo. Nunca altere agentes apenas via jobs sem documentar aqui.
