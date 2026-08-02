## Context

O Cripto Farol já possui um fluxo canônico por `Status`, perfis project-scoped em `.codex/agents/`, skills OpenSpec geradas e uma skill global `alan-workflow`. Hoje os perfis não fixam modelo, a sessão principal não fixa Sol High e as instruções ainda permitem seleção genérica de subagentes. A mudança é transversal ao processo, mas não altera o backend de workflow: Kanban continua controlando estados e autorizações; o Codex controla o roteamento de modelos.

Stakeholders: Alan como aprovador de Design, homologação e release; Codex como orquestrador; agentes Luna como executores de desenvolvimento, review e release.

UI impact: none. A mudança afeta somente instruções, skills, configuração Codex e testes de contrato; nenhuma tela, componente, rota ou comportamento visual do produto muda.

Estado de rework: a primeira versão de configuração e testes já existia na branch quando Alan revisou a decisão em 2026-08-02. Esse trabalho preexistente fica preservado e congelado; tasks afetadas foram reabertas e nenhuma nova edição de implementação pode ocorrer enquanto o card estiver em `Design` ou `Aprovação de Design`.

## Goals / Non-Goals

**Goals:**

- Fixar a sessão principal do projeto em `gpt-5.6-sol` com esforço `high`.
- Acionar automaticamente perfis Luna Max distintos em desenvolvimento, Code Review e release.
- Manter Code Review em thread nova, independente da implementação e read-only.
- Fazer `/opsx:verify` e a aceitação técnica de QA retornarem ao Sol High.
- Falhar fechado quando o perfil/modelo/esforço esperado não estiver disponível ou observável.
- Validar o bootstrap por TOML, testes de contrato e validators; observar o runtime apenas no uso real de cada lane depois da instalação.
- Manter regras globais no `alan-workflow` e detalhes do Cripto no contrato project-scoped, sem editar adaptadores OpenSpec gerados.

**Non-Goals:**

- Introduzir roteamento por complexidade, Terra ou fallback de modelo.
- Alterar estados, transições ou persistência do backend/Kanban.
- Automatizar eventos assíncronos fora de uma tarefa Codex ativa.
- Mudar aprovações humanas, critérios de QA, branch strategy ou release guard.
- Alterar UI/UX do produto.
- Alterar AppArmor, sysctl, bubblewrap ou qualquer política de segurança do servidor para provar o roteamento.
- Iniciar antecipadamente implementer, reviewer ou release manager apenas como smoke test.

## Decisions

### 1. Manter Sol High como sessão principal

Configurar o projeto para iniciar a sessão principal em `gpt-5.6-sol`/`high`. A sessão principal gera/refina OpenSpec e Design, publica artifacts, escolhe a ação determinada pelo estágio e reassume em QA. Isso evita uma troca mutável de modelo dentro da mesma thread.

Alternativa rejeitada: trocar manualmente o modelo no composer a cada etapa. Não é automática, não é auditável e permite divergência entre cards.

### 2. Usar três perfis Luna Max project-scoped

Criar perfis exatos e separados:

- `crypto_luna_implementer`: workspace-write; executa `/opsx:apply`, implementação e testes focados somente após `Pronto para Dev`.
- `crypto_luna_reviewer`: read-only; recebe diff exato em nova thread e retorna findings sem implementar correções.
- `crypto_luna_release_manager`: conduz somente release explicitamente solicitada com cards homologados; não altera código.

Todos fixam `gpt-5.6-luna`/`max`. O nome exato do perfil é parte do contrato; perfis built-in ou semelhantes não são fallback válido.

Todo spawn Luna usa obrigatoriamente `fork_turns="none"` e um role packet autocontido. O pacote inclui card/change, Status e gate observado, branch/worktree, objetivo, arquivos sob ownership, interfaces, restrições, artifacts/diff/SHA aplicáveis, comandos de verificação e formato de retorno. Nenhuma lane depende do histórico da sessão Sol para entender ou executar seu escopo.

Alternativa rejeitada: reutilizar a thread implementadora no review. O contexto compartilhado preservaria pressupostos e reduziria independência.

### 3. Centralizar o roteamento em uma skill Codex canônica

Criar uma skill project-scoped de roteamento por estágio em `.codex/skills/`. Ela aciona os perfis exatos no Codex e não altera os adapters OpenSpec gerados. Cursor e outros clientes ficam fora do escopo por decisão de Alan; não haverá adapter, teste ou promessa de roteamento automático fora do Codex.

O mapa obrigatório será:

| Operação/Status | Executor |
| --- | --- |
| `/opsx:new`, `/opsx:ff`, explore/continue, publicação e `Design` | sessão principal Sol High |
| `Em desenvolvimento` e `/opsx:apply` | `crypto_luna_implementer` |
| `Code Review` | nova thread `crypto_luna_reviewer` |
| `QA` e `/opsx:verify` | sessão principal Sol High |
| sync/archive dentro de release explicitamente autorizada | nova thread `crypto_luna_release_manager` |

Alternativa rejeitada: editar `.codex/skills/openspec-*`. Esses arquivos são gerados pela CLI e não podem receber política local isolada.

### 4. Separar autoria de código, OpenSpec e design durante rework

O Sol em QA inspeciona o SHA/diff revisado, executa `/opsx:verify` e confirma resultados terminais de testes, build, CI, Playwright e runtime aplicáveis. Sol não corrige código em QA.

- Finding que exige somente código retorna para `Luna implementer -> nova Luna reviewer -> Sol QA`.
- Correção de artifact OpenSpec que não altera o design aprovado permanece com Sol High e depois reinicia Code Review/QA quando afetar o diff ou evidência.
- Mudança em `design.md`, protótipo ou decisão aprovada invalida a aprovação e retorna obrigatoriamente a `Design/Sol -> Aprovação de Design/Alan` antes de novo desenvolvimento.

### 5. Tornar a release uma execução Luna delimitada

A release manager Luna só inicia após pedido explícito de Alan e inventário de cards `Homologado`. O perfil solicita `danger-full-access`, necessário para Git/GitHub, worktrees, documentação externa e Drive; esse acesso amplo é aceito somente no lane de release autorizado e é limitado por instruções que proíbem alteração de código e ações fora do pacote.

Ela executa documentação, OpenSpec sync/archive, validações completas, release guards, PR/CI/merge manual, reconciliação e evidências. Falha que exige código interrompe a release. O card permanece em `Homologado` pela regra de não regressão; o trabalho técnico passa por `Luna implementer -> nova Luna reviewer -> Sol QA` sem mover o Status para trás.

### 6. Dividir regras globais e locais com changes coordenadas

Atualizar `alan-workflow` por uma change/branch própria em seu repositório de origem, com commit e rollback independentes vinculados ao card #362. Esta change repo-local não editará arquivos fora de `allowedEditRoots`. Manter no `AGENTS.md`/`rules.md` apenas nomes de status, perfis, comandos e guardrails específicos do Cripto. Um teste de contrato validará TOML e trechos normativos para reduzir drift.

### 7. Validar estaticamente no bootstrap e observar no uso real

Esta change instala os perfis que as tarefas Codex seguintes carregarão. Sua aceitação de bootstrap usa validação estática reproduzível: parse dos TOML, nomes exatos, modelos, efforts, sandboxes, skill, instruções, catálogo disponível e testes de contrato. O catálogo é o cache local oficial do Codex em `${CODEX_HOME:-$HOME/.codex}/models_cache.json`; a validação deve comprovar `gpt-5.6-sol` com effort `high` e `gpt-5.6-luna` com effort `max` em `supported_reasoning_levels`. Não é necessário iniciar antecipadamente as três lanes para aceitar a configuração, e o perfil de release nunca é iniciado sem uma release autorizada.

Depois que a configuração estiver versionada e uma tarefa nova carregar os perfis, cada lane observa o roteamento no momento em que sua etapa realmente ocorrer. Usar primeiro os metadados públicos do spawn/detalhes. Eles devem identificar o agent type selecionado e, quando expostos, modelo, effort, sandbox e permission profile. Se qualquer campo obrigatório — agent type, modelo, effort, sandbox ou permission profile — for omitido e o rollout local estiver disponível, usar um inspector read-only project-scoped que localiza somente o rollout do thread id exato, emite JSON allowlisted e recusa zero/múltiplos matches ou valores ausentes/conflitantes.

O handoff público registra apenas agent type, modelo, effort, sandbox e permission profile; thread ids, caminhos de rollout e payloads internos não são publicados. Se a evidência exigida continuar indisponível ou divergente, a lane real bloqueia sem fallback. Isso não retroage para invalidar o bootstrap estaticamente validado nem autoriza mudar a segurança do host.

Como os perfis ainda não estavam instalados quando esta própria change começou, o diff de bootstrap pode usar uma revisão Codex independente e read-only disponível na sessão atual. A obrigatoriedade do perfil exato `crypto_luna_reviewer` passa a valer para tarefas iniciadas depois que a configuração estiver versionada e carregada.

### 8. Distinguir SHA revisado de integração

QA inicial valida o SHA criado a partir do diff sem finding bloqueante da revisão independente aplicável. No bootstrap, essa revisão usa a lane Codex read-only disponível; depois da ativação, usa obrigatoriamente a Luna reviewer. Quando a integração em `develop` gerar outro SHA, o Sol compara a árvore/conteúdo integrado com o SHA revisado e repete validações afetadas antes de Done. Divergência de conteúdo exige novo ciclo completo.

## Risks / Trade-offs

- [Luna implementa e outra Luna revisa dentro da mesma família] → exigir thread fresca/read-only e manter aceitação final independente com Sol High em QA.
- [Spawn Luna pode herdar contexto/modelo da sessão Sol] → exigir `fork_turns="none"`, agent type exato e role packet autocontido em implementer, reviewer e release manager.
- [Configuração de agentes é carregada na criação da tarefa] → exigir nova tarefa após instalação/atualização e registrar essa necessidade no handoff.
- [Modelo ou effort pode estar indisponível no cliente] → falhar fechado na etapa, sem usar Terra, built-in `worker` ou effort diferente.
- [Políticas da sessão podem ampliar sandbox do reviewer] → observar o sandbox efetivo; se não for read-only, bloquear o Code Review em vez de alegar isolamento.
- [Release recebe `danger-full-access`] → permitir spawn somente após pedido explícito, com pacote homologado, instruções sem edição de código e auditoria antes/depois.
- [Regra global e overlay local podem divergir] → fonte canônica global para política geral, adaptadores finos e teste de contrato no repo.
- [QA detecta defeitos mais tarde que um review Sol] → aceitar o custo do ciclo adicional em troca do fluxo único aprovado; o Sol em QA sempre inspeciona o código, não apenas relatórios.
- [Metadados públicos podem omitir algum campo obrigatório] → inspector local allowlisted como fallback para agent type, modelo, effort, sandbox ou permission profile; ausência após os dois caminhos bloqueia a etapa.
- [A própria change não consegue depender de perfis que ainda está instalando] → aceitar o bootstrap por validação estática e review independente atual; exigir os perfis exatos nas tarefas novas após ativação.
- [Sandbox local pode falhar por política do host] → não alterar segurança do servidor para a aceitação; registrar a falha apenas quando uma lane real for executada e tratá-la operacionalmente fora desta change.

## Migration Plan

1. Criar a change coordenada no repositório de origem de `alan-workflow`, atualizar a skill global e registrar seu commit/rollback no card.
2. Adicionar a skill Codex project-scoped; atualizar `AGENTS.md` e `rules.md` sem tocar nos adapters OpenSpec/Cursor gerados.
3. Adicionar os três perfis Luna, o inspector allowlisted e fixar Sol High na configuração project-scoped.
4. Adicionar testes de contrato e fixtures para modelos, efforts, sandbox, limites de estágio e extração segura de runtime.
5. Validar OpenSpec, skill, TOML, inspector, testes focados e diff.
6. Validar estaticamente perfis, pins, sandboxes, skill e testes; depois da integração, carregar a configuração em tarefas novas e coletar evidência runtime somente no uso real de cada lane.
7. Registrar separadamente a alteração do readme do Project 1 e seu conteúdo anterior para rollback.
8. Em rollback, reverter os commits repo-local e global e restaurar o readme do Project; os estados do Kanban e o backend permanecem inalterados.

## Open Questions

Nenhuma. Alan definiu Codex como único cliente desta automação, o fluxo único, os modelos por etapa e Luna Max para release.

## Prototype

N/A. `UI impact: none`: não existe superfície visual nova ou alterada; a entrega é composta por configuração, skills, instruções e testes de contrato.

## Prototype Validation

N/A. Sem protótipo porque não há impacto de UI.

## Design Critique

### Escopo e coerência

- O roteamento fica no Codex/orquestrador, não no backend de workflow, evitando uma garantia falsa em um serviço que não executa modelos.
- Os gates humanos e o Kanban canônico permanecem inalterados.
- `/opsx:apply`, `/opsx:verify` e `/opsx:archive` foram classificados pela ação efetiva, não apenas pelo namespace OpenSpec.

### Riscos operacionais

- O principal risco é o Codex não carregar ou não honrar os pins; a mitigação de bootstrap é validação estática reproduzível, seguida de bloqueio sem fallback e evidência quando cada lane for realmente usada.
- Depois da ativação, o reviewer Luna precisa de thread separada e sandbox observado como read-only; ausência dessa evidência bloqueia Code Review. O bootstrap usa a exceção explícita de revisão Codex independente e read-only.
- Todas as lanes Luna usam `fork_turns="none"` e pacote autocontido; herança do histórico Sol é proibida.
- A release Luna não recebe autorização implícita para publicar ou corrigir código; seu acesso amplo só existe após pedido explícito.
- Correções de OpenSpec permanecem com Sol; mudança no design aprovado retorna à aprovação de Alan.
- Cards em `Done` ou `Homologado` nunca regridem durante correções de release.

### Regressão de produto

Nenhuma superfície de produto, API ou banco é alterada. O risco de regressão concentra-se em instruções contraditórias, coberto por validação de skill/TOML e teste de contrato.

### Crítica independente final

- Finding bloqueante corrigido: a aceitação anterior exigia smoke-spawn do release manager sem release autorizada e criava uma dependência circular dos perfis ainda não instalados. O bootstrap agora usa validação estática e review Codex independente; runtime fica para o uso real pós-ativação.
- Finding bloqueante corrigido: uma falha do sandbox levou à hipótese de alterar AppArmor/sysctl. Mudanças de segurança do servidor foram declaradas fora do escopo e proibidas como critério de aceite.
- Finding bloqueante corrigido: `sync/archive` estava linguisticamente separado da autorização de release. Agora essas ações pertencem à Luna release manager somente dentro de uma release explicitamente autorizada.
- Finding bloqueante corrigido: evidência runtime do agente podia ser confundida com health do aplicativo. QA e `./restart` validam a aplicação/URL; metadata de modelo é coletada apenas quando uma lane é usada.
- Finding bloqueante corrigido: a fonte do catálogo estava implícita. O design agora define o cache oficial do Codex, os dois slugs e os efforts esperados.
- Gate preservado: a implementação preexistente foi congelada, tasks afetadas foram reabertas e nenhuma edição de implementação ocorrerá antes da nova aprovação humana.
- Finding de cobertura reaberto e resolvido: os testes do inspector passaram a cobrir JSON inválido, múltiplos `session_meta`, identidade divergente, conflitos de sandbox/permissão e falha de enumeração sem vazamento de caminhos; tasks 4.1–4.3 foram revalidadas após o rework pós-aprovação.
- Re-review independente final: PASS; bootstrap, release autorizada, separação de runtimes, catálogo reproduzível e entrada em QA ficaram coerentes entre design, tasks e specs.
- Riscos residuais aceitos para implementação: inspector deve manter saída allowlisted; release usa acesso amplo somente após autorização; mudanças global/local/Project precisam de evidências e rollback separados.
- Decisão revisada por Alan em 2026-08-02: nenhuma configuração do servidor será alterada para provar o roteamento; smoke-spawns antecipados deixam de ser critério de aceite.

Prototype: N/A — mudança sem UI.

Design Agent verdict: PASS
