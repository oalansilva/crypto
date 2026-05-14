# AGENTS.md — Guia rapido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## Escopo deste arquivo

- `rules.md` define as regras obrigatorias curtas do projeto.
- `AGENTS.md` define como executar essas regras na pratica: comandos, status, evidencias, OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Use os dois arquivos. Em conflito real, aplique a regra mais restritiva e registre a ambiguidade antes de alterar codigo, card ou Git.

## TL;DR

- **Branch padrão:** cada card/change usa branch própria a partir de `develop` (`change-<id>-<slug>` ou `card-<id>-<slug>`). `develop` é integração/homologação; `main` é produção.
- **Comunicação padrão com Alan:** usar sempre a skill `caveman` em modo `lite`: curto, direto, sem filler, mantendo clareza técnica. Só desligar se Alan pedir explicitamente `stop caveman` ou `normal mode`.
- **Fluxo de status:** `In Progress` = em execução; `Done` = codificado e validado tecnicamente em `develop`; `Homologado` = Alan testou e aprovou em `develop`; `Pronto` = já subiu para `main`/produção.
- **Fluxo de produção:** implemente em branch da change, integre em `develop` para homologação, acumule cards homologados quando fizer sentido; para liberar produção, abra PR `develop -> main` quando `develop` contiver só conteúdo homologado do pacote, ou use `release-*` quando precisar congelar apenas parte aprovada. Resolva checks/políticas bloqueantes quando possível e realize o merge manual quando permitido, sem auto-merge.
- **Regra de fluxo:** não implemente diretamente em `main`; não implemente diretamente em `develop` salvo ajuste mínimo autorizado por Alan. Branch por change é o padrão.
- **Regra de merge de release/lote:** após abrir um PR para `main` dentro de um fechamento de lote/release solicitado por Alan, execute o merge manualmente quando os checks estiverem verdes e não houver bloqueios.
- **Regra de autonomia operacional:** dentro de fechamento de lote/release solicitado por Alan, após validação e evidência, o agente tem autonomia para repetir tentativas manuais de merge até resolução de bloqueios resolvíveis no repositório, sem pedir nova autorização.
- **Regra de implementação por card:** ao receber pedido com número de card (ex.: `#99`), localizar o card no board `github.com/users/oalansilva/projects/1`, criar/usar branch própria da change a partir de `develop`, mover para `In Progress`, executar usando OpenSpec e subagents conforme o escopo, rodar `/opsx:verify`, integrar em `develop`, executar `./restart`, e só então mover o card para `Done`. Não arquivar nem publicar em `main` nesta etapa.
- **Regra de homologação direta por card (solicitação do cliente):** quando Alan disser que um card está homologado, mova o card de `Done` para `Homologado` sem abrir PR, sem merge em `main` e sem arquivar OpenSpec automaticamente. Homologação aqui significa aprovação funcional em `develop`.
- **Guardrail anti-release acidental:** as frases `card homologado`, `cards homologados`, `está homologado`, `homologuei`, `aprovado em develop` ou equivalentes significam somente atualizar status para `Homologado`. Elas **não autorizam** commit, PR, merge, archive, release ou qualquer ação em `main`.
- **Regra de release/lote:** quando Alan pedir `subir lote`, `fechar lote`, `fechar release`, `criar release`, `gerar release` ou equivalente, selecione apenas os cards `Homologado` cujo responsavel seja `Codex`; ignore cards de outros responsaveis, pois nao sao de codigo. Depois confirme commits/branches incluídos, rode validação final completa, arquive as changes OpenSpec correspondentes, push, PR para `main`, merge manual, atualize `develop` e mova os cards incluídos para `Pronto`.
- **Regra documental de release da Clara/Alan:** quando Alan pedir `gerar release`, `criar release`, `fechar release`, `subir lote` ou equivalente para cards no nome da Clara ou do Alan, antes de publicar/encerrar o pacote, pegue todos os cards `Homologado` por Alan e com `Responsavel=Clara` ou `Responsavel=Alan` incluídos na release e revise se as decisões, status e entregáveis desses cards estão refletidos na documentação do projeto/produto. A documentação precisa ficar atualizada tanto nos Markdown locais quanto nos Google Docs/Drive correspondentes. Depois da release publicada/encerrada com evidência, mova esses cards de `Homologado` para `Pronto`. Cards de `Codex` ficam fora deste fluxo e seguem o fluxo técnico próprio do Codex.
- **Regra de não regressão de status:** depois que um card estiver em `Done`, nunca mova de volta para `In Progress` durante homologação, archive, commit, PR ou merge. Se aparecer falha, ajuste necessário ou reteste, corrija e reteste mantendo o status atual. O card só avança: `Done` -> `Homologado` -> `Pronto`.
- **Regra de confiabilidade por testes:** em qualquer etapa, se surgir erro de testes (locais ou CI), corrija, revalide e só então siga para próxima etapa de encerramento.
- **Regra de validação OpenSpec global:** `openspec validate --all` verde é critério padrão de fechamento. Se falhar por changes antigas fora do card, valide os specs afetados pelo card como evidência parcial, mas resolva a sujeira global antes do encerramento: corrija ou arquive as changes antigas, inclusive por archive manual quando a CLI/skill não conseguir concluir.
- **Regra de checks em execução:** teste, build ou CI iniciado precisa ser acompanhado até terminar. Status como "build está rodando" é atualização intermediária, não evidência final para `Done`, release/lote, commit, PR ou merge.
- **Regra de commits e testes:** commits locais na branch da change são permitidos e não exigem suíte completa a cada commit. Durante o card, rode testes proporcionais/focados; testes completos ficam para fechamento de lote/release.
- **Regra de worktree limpo no fechamento:** antes de iniciar nova change, antes de `Done`, release/lote, commit, PR ou merge, rode `git status --short` e não deixe nenhum arquivo modificado solto sem classificação. Trabalho de outra change deve ir para branch/worktree própria. Stash é só proteção temporária, sempre nomeado com hash, arquivos, motivo e comando de recuperação.
- **Regra de varredura da release:** quando Alan pedir `suba a release`, `subir release`, `salvar tudo`, `subir para develop/main`, `limpar branches`, `limpar worktrees` ou equivalente, trate como fechamento completo de release: primeiro faça inventário de todos os worktrees e branches (`git worktree list`, `git status -sb` em cada diretório e commits `ahead`). Classifique cada item como `integrar`, `já integrado`, `preservar` ou `descartar somente com autorização explícita`. Integre o que deve entrar, valide, envie para `develop`, publique em `main` via PR/merge manual quando permitido e só então limpe branches/worktrees. Antes de remover branch ou diretório temporário, prove que o commit/patch entrou em `main` ou registre por que deve ser preservado. Nunca apague worktree/branch com arquivo modificado, não rastreado ou commit `ahead` sem commit/merge/cherry-pick confirmado.
- **Banco padrão:** PostgreSQL é obrigatório em runtime, QA e scripts operacionais (`DATABASE_URL` e `WORKFLOW_DATABASE_URL` em formato PostgreSQL).
- **Não usar SQLite** como banco de operação. Em runtime/QA/Homologação, use apenas PostgreSQL (`DATABASE_URL` e `WORKFLOW_DATABASE_URL`).
- **Funcionalidades novas:** siga OpenSpec por padrão antes de implementar (`openspec/changes/<change>/` com proposal/spec/design/tasks quando aplicável).
- **Regra obrigatória de criação via OpenSpec:** ao iniciar uma mudança por card, execute o fluxo ` /opsx:new ──► /opsx:ff ──► /opsx:apply ──► /opsx:verify ` antes de mover para `Done`; execute `/opsx:archive` somente no fechamento de lote/release para produção.
  - Se o projeto ainda não estiver inicializado com OpenSpec, rode `openspec init` e então comece o fluxo.
- **Observação de fluxo OpenSpec:** use os comandos nesta ordem para mudanças novas; ajuste a cadência apenas com justificativa explícita.
- **Subagents:** use subagents sempre que houver ganho claro de paralelismo, investigação independente, validação especializada ou aceleração sem duplicar trabalho.
- OpenSpec é a camada de especificação técnica (artifacts).
- Workflow DB e OpenSpec são fontes de operação e evidência.
- **Regra de documentação produto/Drive:** documentos de produto/projeto que existem no Google Drive e em `docs/*.md` devem ser mantidos sincronizados. Drive é a fonte de consulta/revisão para Alan; Markdown local/GitHub é espelho versionado e backup técnico. Não editar manualmente nos dois lugares de forma divergente. Ao atualizar definição aprovada, atualize o `.md` local e sincronize o Google Doc correspondente, ou atualize o Drive e depois espelhe localmente. Para código e documentação técnica de implementação, GitHub continua mandando.

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

## Git/Kanban Workflow

Este projeto usa branches por change para isolar trabalho, `develop` para integração/homologação e `main` para produção.

### Branches principais

- `main`: branch estável/final. Representa o que já foi publicado ou está pronto para produção.
- `develop`: branch de integração e homologação. Alan testa aqui antes de aprovar.
- `change-<id>-<slug>` ou `card-<id>-<slug>`: branch temporária da entrega de um card/change.
- `release-*`: branch opcional para congelar pacote quando `develop` contiver mudanças ainda não homologadas.

### Regras de branch

- Nunca implementar diretamente em `main`.
- Branch por card/change é o padrão.
- Evitar implementar diretamente em `develop`; exceção só para ajuste mínimo e autorizado por Alan.
- Antes de qualquer alteração de código, iniciar sempre com OpenSpec em `openspec/changes/<change>/` (proposta, escopo, critérios e evidência) e só então codar.
- Antes de iniciar segunda change, rode `git status --short`. Se houver alteração solta, classifique e isole antes de continuar.
- Se a worktree atual estiver suja com outra change, prefira `git worktree add` com branch nova em vez de stash.
- Stash é permitido só como proteção temporária. Sempre registre nome, hash, arquivos, motivo e comando de recuperação; use `git stash apply`, não `pop`, quando recuperar.

### Fluxo de card/change

1. Atualizar `develop`.
2. Criar branch `change-<id>-<slug>` ou `card-<id>-<slug>`.
3. Mover card para `In Progress`.
4. Executar OpenSpec (`/opsx:new`, `/opsx:ff`, `/opsx:apply`, `/opsx:verify`) e implementar.
5. Fazer commits locais na branch quando útil. Não rodar suíte completa a cada commit.
6. Rodar testes proporcionais/focados e validação OpenSpec da change.
7. Integrar em `develop` quando pronto para teste integrado, preferencialmente com squash/commit único por card referenciando o card.
8. Executar `./restart`.
9. Mover para `Done` com comentário de evidência.

### Colunas Kanban

- `Done`: implementação técnica concluída, validada proporcionalmente e integrada em `develop`.
- `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
- `Pronto`: conteúdo do card entrou em `main`/produção.

Nunca mover para `Homologado` sem aprovação explícita de Alan. Nunca mover para `Pronto` sem confirmar merge/publicação em `main`.

### Comentários obrigatórios no Kanban

Ao mover para `Done`, comentar:
```text
Implementação concluída.
Branch: change-<id>-<slug>
Integrado em: develop
Commit/merge: <referência, se disponível>
Resumo:
- ...
Testes executados:
- ...
Próximo passo: Alan testar/homologar na develop.
```

Ao mover para `Homologado`, comentar:
```text
Homologado por Alan na develop.
Apto para próximo pacote de release.
```

Ao mover para `Pronto`, comentar:
```text
Publicado em main.
Pacote/release: <nome>
Cards incluídos: <lista>
Commit/merge: <referência, se disponível>
Branches limpas: <lista ou pendência>
Status final: pronto.
```

### Release em lote

- Vários cards podem ficar em `Homologado` aguardando publicação conjunta.
- Quando Alan pedir `subir lote`, `fechar lote`, `fechar release`, `criar release`, `gerar release` ou equivalente, liste apenas cards `Homologado` com responsavel `Codex` e os commits/branches que entram no pacote. Ignore cards de outros responsaveis.
- Se `develop` contiver só conteúdo homologado do pacote, use PR `develop -> main`.
- Se `develop` contiver mudança não homologada, não faça merge direto `develop -> main`; crie `release-*` a partir de `main` e inclua somente commits/branches aprovados, ou peça decisão de Alan.
- Antes de mover cards para `Pronto`, confirme que cada card realmente entrou no merge para `main`.

### Testes

- Durante implementação: testes focados/proporcionais ao card, validação OpenSpec da change e evidência no handoff.
- Antes de `Done`: checks iniciados precisam terminar; status "rodando" não vale como evidência final.
- No fechamento de lote/release: `openspec validate --all`, testes completos proporcionais ao pacote, build e CI até resultado final.
- Se teste local ou CI falhar, corrija, revalide e só então siga para próximo status.

### Comandos esperados

Criar branch em worktree limpa:
```bash
git switch develop
git pull origin develop
git switch -c change-<id>-<slug>
```

Criar branch sem tocar worktree suja:
```bash
git worktree add ../crypto-worktrees/change-<id>-<slug> -b change-<id>-<slug> develop
```

Integrar card em `develop` quando pronto:
```bash
git switch develop
git pull origin develop
git merge --squash change-<id>-<slug>
git commit -m "feat: concluir card #<id> <resumo>"
git push origin develop
```

Publicar lote direto de `develop` quando seguro:
```bash
git switch develop
git pull origin develop
openspec validate --all
gh pr create --base main --head develop --title "<titulo>" --body "<resumo>"
gh pr merge --merge --delete-branch=false
```

Publicar com branch de release quando `develop` tiver conteúdo não homologado:
```bash
git switch main
git pull origin main
git switch -c release-YYYY-MM-DD
# incluir apenas commits/branches homologados
git cherry-pick <commit-homologado>
git push origin release-YYYY-MM-DD
gh pr create --base main --head release-YYYY-MM-DD --title "<titulo>" --body "<resumo>"
gh pr merge --merge --delete-branch=false
```

Limpar branches após publicação/Pronto:
```bash
git worktree remove ../crypto-worktrees/change-<id>-<slug> # se usada
git branch -d change-<id>-<slug>
git push origin --delete change-<id>-<slug> # se publicada
```

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
- Para promover produção, junte apenas os cards `Homologado` com responsavel `Codex` no lote/release pedido por Alan, ignore cards de outros responsaveis, confirme commits/branches incluídos, abra PR para `main`, resolva checks/políticas bloqueantes quando forem corrigíveis por código/configuração do repo, realize o merge manual do PR e então mova os cards incluídos para `Pronto`.
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
- Para qualquer tela, componente visual ou funcionalidade com impacto de UI/UX, nova ou antiga, consulte e siga obrigatoriamente o `DESIGN.md` antes de implementar.
  - Registre no OpenSpec/hand-off quais tokens, componentes e padrões do `DESIGN.md` foram aplicados.
  - Não feche implementação visual sem validar aderência ao `DESIGN.md` em desktop/mobile quando aplicável.
  - Se houver desvio necessário do `DESIGN.md`, registre a exceção e a justificativa antes de codar ou fechar a entrega.
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
