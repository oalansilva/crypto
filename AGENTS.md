# AGENTS.md — Guia rapido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## Escopo deste arquivo

- `rules.md` define as regras obrigatorias curtas do projeto.
- `AGENTS.md` define como executar essas regras na pratica: comandos, status, evidencias, OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Use os dois arquivos. Em conflito real, aplique a regra mais restritiva e registre a ambiguidade antes de alterar codigo, card ou Git.

## Processo global do Alan

- Regras gerais de processo ficam na skill global `alan-workflow` quando ela estiver disponível no cliente. Codex e Cursor continuam sujeitos aos mesmos gates versionados neste `AGENTS.md` e em `rules.md`; o roteamento automático Sol/Luna desta política é suportado e validado somente no Codex.
- Use essa skill para comunicacao curta, evidencias antes de concluir, OpenSpec no card antes de implementar, higiene Git/worktree/release, classificacao de pendencias, seguranca de output e fechamento sem pendencia. No cripto, o fluxo local `Todo`/`Design`/`Aprovação de Design`/`Pronto para Dev`/`Em desenvolvimento`/`Code Review`/`QA`/`Done`/`Homologado`/`Pronto`/`Cancelado` prevalece sobre qualquer vocabulário global antigo.
- Este `AGENTS.md` deve manter apenas regras especificas do cripto: branches `develop/main`, Project 1, release guard, PostgreSQL, Drive/docs, comandos de backend/frontend, workflow DB e papeis dos agentes.
- Se uma regra geral precisar mudar para todos os projetos, atualize `alan-workflow`; nao duplique a regra aqui.

## TL;DR

- **Branch padrão:** cada card/change usa branch própria a partir de `develop` (`change-<id>-<slug>` ou `card-<id>-<slug>`). `develop` é integração/homologação; `main` é produção.
- **Comunicação padrão com Alan:** usar sempre a skill `caveman` em modo `lite`: curto, direto, sem filler, mantendo clareza técnica. Só desligar se Alan pedir explicitamente `stop caveman` ou `normal mode`.
- **Colunas/Status:** no cripto, o campo `Status` e a fonte principal das colunas visuais. O fluxo obrigatório de **todo** card é `Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`; `Cancelado` é terminal. **Proibido** pular `Design`, `Aprovação de Design` ou `Pronto para Dev` (inclusive com `UI impact: none`, remoção, bug ou pedido `implemente`). O arraste `Aprovação de Design -> Pronto para Dev` é a aprovação humana de Alan. `Done` continua sendo Done tecnico e `Pronto` continua exigindo `main`/produção com evidencia.
- **Roteamento automático Codex:** a sessão principal usa `gpt-5.6-sol`/`high` em Design/OpenSpec e QA; `crypto_luna_implementer` usa `gpt-5.6-luna`/`max` em desenvolvimento; uma nova `crypto_luna_reviewer` Luna Max read-only executa Code Review; e uma nova `crypto_luna_release_manager` Luna Max conduz release explicitamente autorizada. Toda lane Luna usa `fork_turns="none"`; não usar Terra, built-ins ou fallback.
- **Exceção de bootstrap do roteamento:** a change que instala os perfis é aceita por validação estática reproduzível e revisão Codex independente read-only. Nenhuma lane é pre-spawned para prova; evidência runtime passa a ser obrigatória somente quando a lane Luna for usada naturalmente por tarefa nova após os perfis serem versionados e carregados. Não alterar AppArmor, sysctl, bubblewrap, sandbox launcher ou segurança do host/servidor para provar o roteamento.
- **Fluxo de produção:** implemente em branch da change, integre em `develop` para homologação, acumule cards homologados quando fizer sentido; para liberar produção, abra PR `develop -> main` quando `develop` contiver só conteúdo homologado do pacote, ou use `release-*` quando precisar congelar apenas parte aprovada. Resolva checks/políticas bloqueantes quando possível e realize o merge manual quando permitido, sem auto-merge.
- **Regra de fluxo:** não implemente diretamente em `main`; não implemente diretamente em `develop` salvo ajuste mínimo autorizado por Alan. Branch por change é o padrão.
- **Regra de merge de release/lote:** após abrir um PR para `main` dentro de um fechamento de lote/release solicitado por Alan, execute o merge manualmente quando os checks estiverem verdes e não houver bloqueios.
- **Regra de autonomia operacional:** dentro de fechamento de lote/release solicitado por Alan, após validação e evidência, o agente tem autonomia para repetir tentativas manuais de merge até resolução de bloqueios resolvíveis no repositório, sem pedir nova autorização.
- **Regra de implementação por card:** seguir `alan-workflow`; no cripto, usar o board `github.com/users/oalansilva/projects/1`, criar/usar branch propria da change a partir de `develop`, **sempre** concluir o gate `Design -> Aprovação de Design` e só então aguardar `Status=Pronto para Dev`, mover para `Status=Em desenvolvimento` antes de aplicar tarefas de código, mover para `Status=Code Review` antes do commit, rodar o review read-only aplicável no diff exato (Luna reviewer depois da ativação; Codex independente apenas no bootstrap), commit/push do SHA revisado, mover para `Status=QA`/`Fluxo=QA`, aguardar `qa-gate` e Playwright visual verdes, integrar por PR em `develop`, executar `./restart`, validar a URL e so entao mover o card para `Status=Done` como Done tecnico. Nao arquivar nem publicar em `main` nesta etapa.
- **Regra de conclusão de correção:** para qualquer correção de bug ou ajuste solicitado por Alan, só diga `concluído` depois de validar, fazer merge/integração da branch de trabalho em `develop`, executar `./restart` e confirmar que a URL do sistema está servindo o bundle/resultado novo. Antes disso, reporte como `corrigido na branch`, `validado localmente` ou `aguardando integração`, conforme o estado real.
- **Regra de homologação direta por card (solicitação do cliente):** seguir `alan-workflow`; no cripto, homologacao significa aprovacao funcional em `develop`.
- **Guardrail anti-release acidental:** seguir `alan-workflow`; no cripto, homologacao nao autoriza `main`, PR, merge, archive ou release.
- **Regra de release/lote:** seguir `alan-workflow`; no cripto, selecione todos os cards `Homologado` incluídos no pacote, confirme commits/branches, rode validação final completa, arquive OpenSpec, push, PR para `main`, merge manual, atualize `develop` e mova os cards incluídos para `Pronto`.
- **Regra documental de release da Clara/Alan:** quando Alan pedir `gerar release`, `criar release`, `fechar release`, `subir lote` ou equivalente para cards no nome da Clara ou do Alan, antes de publicar/encerrar o pacote, pegue todos os cards `Homologado` por Alan e com `Responsavel=Clara` ou `Responsavel=Alan` incluídos na release e revise se as decisões, status e entregáveis desses cards estão refletidos na documentação do projeto/produto. A documentação precisa ficar atualizada tanto nos Markdown locais quanto nos Google Docs/Drive correspondentes. Depois da release publicada/encerrada com evidência, mova esses cards de `Homologado` para `Pronto`. Cards de `Codex` seguem o fluxo técnico próprio do Codex no mesmo pacote.
- **Regra de não regressão de status:** depois que um card estiver em `Done`, nunca mova de volta para `Em desenvolvimento` durante homologação, archive, commit, PR ou merge. Se aparecer falha, ajuste necessário ou reteste, corrija e reteste mantendo o status atual. O card só avança: `Done` -> `Homologado` -> `Pronto`.
- **Regra de confiabilidade por testes:** em qualquer etapa, se surgir erro de testes (locais ou CI), corrija, revalide e só então siga para próxima etapa de encerramento.
- **Regra de validação OpenSpec global:** `openspec validate --all` verde é critério padrão de fechamento. Se falhar por changes antigas fora do card, valide os specs afetados pelo card como evidência parcial, mas resolva a sujeira global antes do encerramento: corrija ou arquive as changes antigas, inclusive por archive manual quando a CLI/skill não conseguir concluir.
- **Regra de checks em execução:** seguir `alan-workflow`; no cripto, isso vale para testes locais, `openspec validate`, build e CI antes de `Code Review`, `QA`, `Done`, release/lote, commit, PR ou merge. Check `running`, `cancelled` ou skip sem dispensa autorizada nao e evidencia final.
- **Regra de espera de CI:** use um unico watcher nativo por PR com timeout explicito: `timeout 35m gh pr checks <PR> --watch --fail-fast --interval 20`. Nao filtre apenas checks marcados como required, porque todos os checks iniciados precisam terminar e OpenSpec pode nao estar na protecao de `main`. Esperas acima de 60 segundos rodam em background quando o cliente suportar. Sao proibidos loops `for`/`while` com `sleep`, consultas repetidas pelo modelo e subagent criado apenas para polling. Timeout, falha, check ausente ou bloqueio encerram a tentativa sem merge; depois do verde, consulte mergeabilidade uma vez e faca no maximo uma tentativa manual para o estado observado. Qualquer falha exige diagnostico e uma nova verificacao completa de prontidao antes de outra tentativa.
- **Regra de commits e testes:** commits locais na branch da change são permitidos e não exigem suíte completa a cada commit, mas exigem o review read-only aplicável do diff antes de cada commit. Durante o card, rode testes proporcionais/focados; testes completos ficam para fechamento de lote/release.
- **Regra de worktree limpo no fechamento:** seguir `alan-workflow`; no cripto, trabalho de outra change deve ir para branch/worktree própria e a integração padrão acontece em `develop` antes de produção.
- **Regra de varredura da release:** seguir o inventario/classificacao de `alan-workflow`; no cripto, integre o que deve entrar em `develop`, publique em `main` via PR/merge manual quando permitido e só então limpe branches/worktrees.
- **Regra de guard automatizado de release:** antes de abrir/mesclar PR de release, rode `scripts/release-guard pre`; depois do merge/publicação e antes de reportar limpeza final, rode `scripts/release-guard post`. Se qualquer modo estrito falhar, pare e classifique/corrija todos os bloqueios antes de seguir. Use `scripts/release-guard audit` para diagnostico sem bloqueio durante desenvolvimento.
- **Regra de comparação oficial:** estado publicado deve ser comparado contra `origin/develop` e `origin/main` depois de `git fetch --prune origin`. `main` local ou `develop` local atrasados servem apenas como alerta, nunca como prova final de merge ou falta de merge.
- **Regra anti-stash órfão:** seguir `alan-workflow`; nenhuma release/lote pode terminar com stash novo ou antigo sem classificacao explicita.
- **Banco padrão:** PostgreSQL é obrigatório em runtime, QA e scripts operacionais (`DATABASE_URL` e `WORKFLOW_DATABASE_URL` em formato PostgreSQL).
- **Não usar SQLite** como banco de operação. Em runtime/QA/Homologação, use apenas PostgreSQL (`DATABASE_URL` e `WORKFLOW_DATABASE_URL`).
- **Funcionalidades novas:** siga OpenSpec por padrão antes de implementar (`openspec/changes/<change>/` com proposal/spec/design/tasks quando aplicável).
- **Regra obrigatória de criação via OpenSpec:** ao iniciar uma mudança por card, execute o fluxo ` /opsx:new ──► /opsx:ff ──► /opsx:apply ──► /opsx:verify ` antes de mover para `Done`; execute `/opsx:archive` somente no fechamento de lote/release para produção.
  - Se o projeto ainda não estiver inicializado com OpenSpec, rode `openspec init` e então comece o fluxo.
- **OpenSpec no card antes de implementar:** seguir `alan-workflow`; neste repo, preferir Gist secreto descrito como `crypto openspec <change>` e comentario no issue/card.
- **Conteúdo do Gist OpenSpec:** somente `proposal.md`, `design.md`, `tasks.md`, `specs/**/*.md`. **Não** colocar HTML/CSS/JS de protótipo no Gist nem listar `prototype/*.html` como arquivo do Gist no comentário.
- **Protótipo HTML:** seção separada no comentário com link HTTP `https://dev.criptofarol.com.br/prototypes/<slug>/` (arquivos em `frontend/public/prototypes/<slug>/`). Helper: `publish-openspec-card-artifacts.sh --prototype-url ...`.
- **Observação de fluxo OpenSpec:** use os comandos nesta ordem para mudanças novas; ajuste a cadência apenas com justificativa explícita.
- **Subagents:** use subagents sempre que houver ganho claro de paralelismo, investigação independente, validação especializada ou aceleração sem duplicar trabalho.
- OpenSpec é a camada de especificação técnica (artifacts).
- Workflow DB e OpenSpec são fontes de operação e evidência.
- **Regra de documentação produto/Drive:** documentos de produto/projeto que existem no Google Drive e em `docs/*.md` devem ser mantidos sincronizados. Drive é a fonte de consulta/revisão para Alan; Markdown local/GitHub é espelho versionado e backup técnico. Não editar manualmente nos dois lugares de forma divergente. Ao atualizar definição aprovada, atualize o `.md` local e sincronize o Google Doc correspondente, ou atualize o Drive e depois espelhe localmente. Para código e documentação técnica de implementação, GitHub continua mandando.
- **Caminhos locais/versionados de documentação:** use `crypto/docs/project-hub.md` como hub central do projeto; `crypto/docs/decision-log.md` para decisões relevantes; `crypto/docs/mvp-scope.md` para escopo do MVP; `crypto/docs/backlog-operating-model.md` para modelo operacional do backlog/release; `crypto/docs/landing-page.md` para definição/copy da landing; `crypto/docs/brand-system.md` para marca, tom e identidade; `crypto/docs/beta-*.md` para materiais do beta, validação, convite, Telegram e conteúdo; e `crypto/docs/release-*.md` para registro de release.
- **Fontes externas de consulta/status:** use o Google Drive da Clara, na pasta do projeto cripto (`https://drive.google.com/drive/folders/1OE0D_nsb7BAMQ_ntZXUonnsfX9MtXhT9`), com documentos de texto sempre na subpasta `Docs` (`1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx`) e planilhas na subpasta `Planilhas` quando aplicável; o GitHub Project `MVP Cripto - Beta Fechado` como fonte operacional dos cards/status; e Issues/PRs do GitHub quando o item tiver evidência técnica ou comentário de release.
- **Regra prática de sincronização:** documento de produto/processo atualiza local em `crypto/docs/` e sincroniza no Drive. Execução/status atualiza GitHub Project e, quando houver código, Issue/PR. Não edite Drive e Markdown de forma divergente.
- **DoD de documentação sincronizada:** uma atualização documental só está concluída quando os dois lados estão atualizados e conferidos: Markdown local/versionado em `crypto/docs/` e Google Doc/Sheet correspondente no Drive. Se apenas o Drive foi atualizado, espelhe imediatamente no Markdown local; se apenas o Markdown local foi atualizado, sincronize imediatamente no Drive. Não mova card para `Pronto`, não feche release e não reporte documentação como concluída sem evidência dos dois lados.
- **Passo obrigatório de Drive em release:** ao criar/subir release, depois de atualizar os Markdown locais, sincronize os documentos aplicáveis no Google Drive da Clara. Para usar `gog` sem TTY, carregue `GOG_KEYRING_PASSWORD` do Bitwarden Secrets Manager (`Crypto` / `GOG_KEYRING_PASSWORD`). Primeiro liste a subpasta `Docs` com `gog drive ls --account claravalente840@gmail.com --parent 1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx --json --no-input`; se já existir Google Doc equivalente, atualize o mesmo ID com `gog docs write <docId> --file <arquivo.md> --markdown --replace --pageless --no-input`; se não existir, crie diretamente nessa subpasta com `gog docs create "<titulo-sem-prefixo>" --account claravalente840@gmail.com --parent 1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx --file <arquivo.md> --pageless --no-input`. Nunca crie documentos soltos na raiz da pasta do projeto. Ao final, valide com `gog drive ls --account claravalente840@gmail.com --parent 1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx --json --no-input` e registre os links/evidência da sincronização.

## De-para OpenSpec/OPSX no Codex e no Cursor

Codex e Cursor usam as mesmas skills OpenSpec, geradas pela mesma versão da CLI. Trate `/opsx:*` como a intenção canônica escrita na documentação e `/opsx-*` como o alias de slash command disponibilizado pelos adaptadores do Cursor. Se o cliente não interpretar uma das formas como slash command, trate o texto como intenção operacional e acione a skill local equivalente. Não substitua a skill por criação manual de arquivos.

Os arquivos em `.codex/skills/openspec-*`, `.cursor/skills/openspec-*` e `.cursor/commands/opsx-*.md` são adaptadores oficiais gerados. Não edite uma cópia isoladamente. Atualize todos com a mesma CLI:

```bash
openspec init --tools codex,cursor --force
```

Regra obrigatória:
- Primeiro use a skill OpenSpec correspondente.
- Depois execute a CLI `openspec` indicada pela própria skill.
- Só crie ou edite arquivos em `openspec/changes/<change>/` seguindo `openspec instructions ... --json`.
- Não invente artefatos manualmente fora do fluxo da skill.
- Ao final de cada etapa, registre no handoff/status qual skill foi usada, qual comando CLI foi executado e qual evidência foi produzida.

De-para principal:

| Intenção canônica | Alias Cursor | Skill obrigatória | CLI base | Resultado esperado |
| --- | --- | --- | --- | --- |
| `/opsx:new <change>` | `/opsx-new <change>` | `$openspec-new-change` | `openspec new change "<change>"`; `openspec status --change "<change>"`; `openspec instructions <artifact-id> --change "<change>"` | Cria apenas o scaffold da change, mostra status e instrução do primeiro artifact. Não cria artifacts ainda. |
| `/opsx:ff <change>` | `/opsx-ff <change>` | `$openspec-ff-change` | `openspec status --change "<change>" --json`; `openspec instructions <artifact-id> --change "<change>" --json` | Gera todos os artifacts necessários para ficar pronto para implementação, respeitando dependências e templates retornados pela CLI. |
| `/opsx:apply <change>` | `/opsx-apply <change>` | `$openspec-apply-change` | `openspec status --change "<change>" --json`; `openspec instructions apply --change "<change>" --json` | Lê `contextFiles` e implementa as tasks pendentes. Em **todo** card, só começa código depois de `Pronto para Dev`. |
| `/opsx:verify <change>` | `/opsx-verify <change>` | `$openspec-verify-change` | `openspec list --json` quando a change estiver ambígua; `openspec status --change "<change>" --json`; `openspec instructions apply --change "<change>" --json` | Verifica completude, corretude e coerência entre artifacts, specs, tasks, design, testes e implementação real. |
| `/opsx:archive <change>` | `/opsx-archive <change>` | `$openspec-archive-change` | `openspec status --change "<change>" --json`; avaliar sync de specs; mover para `openspec/changes/archive/YYYY-MM-DD-<change>/` | Arquiva somente no fechamento de lote/release após homologação, checando artifacts, tasks, delta specs e registrando warnings se algo ficar incompleto. |

Antes de executar `/opsx:apply` em qualquer change vinculada a card/issue, siga `alan-workflow` e publique os artefatos OpenSpec no card. Convencao local do Gist: descricao `crypto openspec <change>` e comentario no card do Project 1.

### Roteamento automático de modelos no Codex

Invocar `$stage-model-routing` em toda etapa. O roteamento é por estágio, nunca por complexidade:

| Operação/Status | Executor obrigatório |
| --- | --- |
| `/opsx:new`, `/opsx:ff`, explore/continue, publicação e `Design` | sessão principal `gpt-5.6-sol` / `high` |
| `Em desenvolvimento`, `/opsx:apply`, implementação e testes focados | `crypto_luna_implementer` (`gpt-5.6-luna` / `max`) |
| `Code Review` | nova `crypto_luna_reviewer` (`gpt-5.6-luna` / `max`, read-only) |
| `QA`, `/opsx:verify` e aceitação técnica | sessão principal `gpt-5.6-sol` / `high` |
| sync/archive somente dentro de release explicitamente autorizada | nova `crypto_luna_release_manager` (`gpt-5.6-luna` / `max`) |

- Todo spawn Luna usa o agent type exato, `fork_turns="none"` e pacote autocontido conforme `.codex/skills/stage-model-routing/SKILL.md`.
- Depois da ativação, verificar agent type, modelo, effort, sandbox e permission profile efetivos quando a lane Luna for usada. Metadata ausente/divergente bloqueia; não existe fallback para Terra, built-in ou outro effort.
- No bootstrap, validar TOML, catálogo de modelos, skill, testes de contrato e OpenSpec sem iniciar lanes antecipadamente; usar revisão Codex independente read-only no diff exato. A exceção termina para tarefas novas após os perfis serem versionados e carregados.
- Não alterar AppArmor, sysctl, bubblewrap, user namespaces, sandbox launcher ou qualquer política de segurança do host/servidor para executar smoke test. Diagnóstico pre-ativação bloqueado não substitui nem invalida a aceitação estática.
- Após a ativação, Code Review nunca reutiliza a thread implementadora e nunca implementa os próprios findings.
- Sol em QA não corrige código. Código retorna a implementer -> nova reviewer -> Sol QA; OpenSpec permanece com Sol; mudança no design aprovado retorna a Design/Aprovação de Alan.
- Cursor mantém os adapters OpenSpec existentes, mas não faz parte da implementação nem dos testes deste roteamento automático.

De-para complementar:

| Intenção canônica | Alias Cursor | Skill obrigatória | Uso correto |
| --- | --- | --- | --- |
| `/opsx:explore [change]` | `/opsx-explore [change]` | `$openspec-explore` | Explorar decisões e riscos sem implementar código; pode preparar artifacts quando solicitado. |
| `/opsx:continue <change>` | `/opsx-continue <change>` | `$openspec-continue-change` | Continuar a criação do próximo artifact pronto, usando `openspec status` e `openspec instructions`, sem pular dependências. |
| `/opsx:sync <change>` | `/opsx-sync <change>` | `$openspec-sync-specs` | Sincronizar delta specs somente dentro de release explicitamente autorizada, antes ou durante o archive conforme avaliação da skill. |
| `/opsx:bulk-archive` | `/opsx-bulk-archive` | `$openspec-bulk-archive-change` | Arquivar várias changes concluídas somente dentro de release explicitamente autorizada, uma a uma, preservando evidência e warnings por change. |
| `/opsx:onboard` | `/opsx-onboard` | `$openspec-onboard` | Fazer onboarding guiado do fluxo OpenSpec antes de iniciar implementação quando o contexto operacional estiver confuso. |

Fluxo canônico para implementação por card:

```text
/opsx:new <change>
  -> usar $openspec-new-change
  -> criar scaffold e identificar primeiro artifact

/opsx:ff <change>
  -> usar $openspec-ff-change
  -> gerar artifacts até apply-ready

publicar artifacts OpenSpec no card
  -> seguir alan-workflow; no cripto, usar Gist `crypto openspec <change>` ou links permanentes
  -> comentar o card com change, arquivos e comandos gh gist view

gate de design obrigatório (todo card)
  -> mover para Design; declarar UI impact affected|none com justificativa
  -> invocar design-critic; concluir design.md + Design Critique
  -> se UI impact = affected: Prototype verificável também obrigatório
  -> se UI impact = none: Prototype pode ser N/A explícito, sem pular colunas
  -> mover para Aprovação de Design e aguardar Alan
  -> Alan aprova arrastando para Pronto para Dev
  -> proibido bypass Todo->Pronto para Dev ou Todo/Design->Em desenvolvimento

/opsx:apply <change>
  -> usar $openspec-apply-change
  -> somente com Status=Pronto para Dev: mover para Em desenvolvimento
  -> implementar tasks e atualizar tasks.md

/opsx:verify <change>
  -> usar $openspec-verify-change
  -> validar artifacts versus implementação e testes
```

Fechamento de lote/release após homologação e pedido explícito de Alan:

```text
/opsx:archive <change>
  -> usar $openspec-archive-change
  -> sincronizar specs quando aplicável e arquivar a change
```

Se o agente criar `proposal.md`, `design.md`, `tasks.md`, `specs/**` ou mover arquivos para `archive/` sem declarar a skill OpenSpec usada, considere o fluxo incompleto e corrija antes de avançar para DEV, QA, homologação ou merge.

### Designer/Critic Agent compartilhado

- O contrato canônico fica em `.agents/skills/design-critic/SKILL.md`. `.codex/skills/design-critic/SKILL.md` e `.cursor/skills/design-critic/SKILL.md` são adaptadores finos e não devem duplicar regras.
- No Codex, invoque `$design-critic`; no Cursor, invoque `/design-critic`. Pedido equivalente em linguagem natural também deve acionar a skill durante `Status=Design` de **qualquer** card.
- O Designer/Critic Agent prepara a entrega de design: com UI, produz/refatora o protótipo e critica produto/UX/a11y/responsividade/estados; sem UI nova, registra decisão enxuta e ausência de superfície visual. Resolve achados bloqueantes no escopo e registra `Design Agent verdict` no `design.md`.
- O agente só pode mover `Design -> Aprovação de Design` quando `design.md` e `Design Critique` estiverem completos e, se `UI impact: affected`, o `Prototype` também. Nunca pode mover `Aprovação de Design -> Pronto para Dev`, autoaprovar ou alegar identidade de Alan.
- **Protótipos HTML navegáveis (Cripto):** publicar em `frontend/public/prototypes/<change-or-card-slug>/` (preferir `index.html`). URL canônica de revisão: `https://dev.criptofarol.com.br/prototypes/<change-or-card-slug>/`. Não use Gist como superfície de visualização de HTML (Gist mostra código-fonte). No comentário do card, o bloco **OpenSpec** lista só Markdown do Gist; o bloco **Protótipo navegável** traz o link HTTP da tela. Após gravar o arquivo em `public/`, rebuild/restart do frontend DEV se necessário para o `preview` servir o `dist/` atualizado. Helper: `publish-openspec-card-artifacts.sh` com `--prototype-url` (nunca faz upload de HTML no Gist).
- **Fidelidade do protótipo ao sistema atual:** se a tela/rota/shell já existir, o protótipo deve clonar a UI atual (sidebar/header, tokens de `DESIGN.md`/`index.css`, tipografia, densidade, estados) e redesenhar apenas o delta do card por cima. Alan valida diferença, não uma tela inventada. Se a tela ainda não existir, desenhar a nova superfície alinhada a `DESIGN.md` e ao shell autenticado do app; não usar layouts genéricos/marketing.
- **Browser gate antes do PASS:** abrir a URL final do protótipo em navegador real (preferir Playwright), em desktop e mobile, e exercitar estado padrão + todas as interações relevantes. Transformar critérios críticos em asserts; em remoções, provar `count=0`/`not visible`/`display:none` no estado final. Verificar console/page errors. Registrar comando/URL/viewports/asserts em `design.md` sob `## Prototype Validation`. `curl`, HTTP 200, build ou inspeção estática não substituem esse gate.
- **Evidência vinculada à versão:** qualquer alteração posterior em HTML/CSS/JS, rebuild ou restart invalida a validação anterior e exige nova execução. Sem navegador disponível ou com assert falhando, manter `Status=Design` e `Design Agent verdict: BLOCKED`.

### Falhas antigas em `openspec validate --all`

- Primeiro confirme a change atual: `openspec status --change "<change>" --json` precisa estar completo e os specs afetados pelo card precisam validar individualmente.
- Se `openspec validate --all` falhar por changes antigas, trate como bloqueio de higiene do repo, não como exceção permanente. Investigue cada change quebrada e corrija artifacts ativos; sync/archive de changes concluídas ou obsoletas só pode ocorrer dentro de release explicitamente autorizada.
- Dentro dessa release autorizada, use primeiro a skill OpenSpec adequada, normalmente `$openspec-archive-change`. Se a CLI/skill falhar por estado antigo ou inconsistente, o archive manual é permitido como exceção operacional: mover para `openspec/changes/archive/YYYY-MM-DD-<change>/`, sincronizar specs quando aplicável, preservar evidência no handoff e registrar por que o caminho manual foi usado.
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
3. Declarar `UI impact: affected` ou `UI impact: none` com justificativa não vazia (classificação de evidência; **não** autoriza pular colunas).
4. Executar OpenSpec (`/opsx:new`, `/opsx:ff`) e publicar os artifacts no card.
5. Mover para `Status=Design`, invocar `design-critic`, concluir `design.md` + `Design Critique` (e `Prototype` quando UI impact = affected), mover para `Status=Aprovação de Design` e **aguardar Alan** arrastar para `Pronto para Dev`. Pedidos como `implemente` / `pode codar` **não** autorizam pular este gate.
6. Somente em `Pronto para Dev`, mover para `Status=Em desenvolvimento`, executar `/opsx:apply` com a Luna implementer, implementar e rodar testes focados. `/opsx:verify` fica para Sol em `QA`.
7. Rodar testes proporcionais/focados e validação OpenSpec da change.
8. Mover card para `Status=Code Review` e sincronizar `Fluxo=Code Review` quando existir.
9. Após a ativação, rodar a nova Luna reviewer read-only no diff exato antes do commit. Somente o bootstrap usa revisão Codex independente read-only disponível na tarefa instaladora. Se houver rework grande, voltar para `Em desenvolvimento`; se forem ajustes pequenos, manter `Code Review` e repetir o review.
10. Fazer commit/push do SHA revisado, mover para `Status=QA` e sincronizar `Fluxo=QA` quando existir.
11. Abrir PR para `develop`, aguardar `qa-gate` terminal verde e corrigir qualquer falha antes da integração.
12. Integrar em `develop` quando pronto, preferencialmente com squash/commit único por card referenciando o card.
13. Executar `./restart` e validar a URL/runtime.
14. Mover para `Status=Done` com comentário de evidência tecnica.

### Colunas Kanban

- O campo `Status` e a fonte principal das colunas. O campo `Fluxo`, quando existir, e substatus/legado; se houver divergencia, `Status` prevalece.
- `Todo`: backlog ou pronto para comecar.
- `Design`: Designer/Critic Agent prepara evidências da solução (protótipo quando houver UI; decisão enxuta quando não houver).
- `Aprovação de Design`: entrega completa aguardando decisão humana de Alan. Coluna obrigatória para todo card.
- `Pronto para Dev`: design aprovado por Alan via arraste; único status que libera desenvolvimento.
- `Em desenvolvimento`: Codex/Clara esta implementando, investigando, validando ou corrigindo achados de review.
- `Code Review`: diff pronto para review Codex antes do commit; achados bloqueantes precisam ser corrigidos ou classificados.
- `QA`: SHA revisado em validacao automatizada; `qa-gate`, Playwright visual e demais checks obrigatorios precisam terminar verdes.
- `Done`: Done tecnico; QA verde, implementação técnica revisada, integrada em `develop`, restart/runtime validados, aguardando teste/aprovacao do Alan.
- `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
- `Pronto`: conteúdo do card entrou em `main`/produção com evidencia; este e o fechamento final.
- `Cancelado`: nao sera feito ou foi substituido.

O arraste `Aprovação de Design -> Pronto para Dev` aprova a versão específica do `design.md` e, quando existir, do protótipo. Apenas Alan autenticado pode executá-lo. Se uma dessas evidências mudar, a aprovação fica obsoleta e o desenvolvimento deve permanecer bloqueado até nova aprovação. Retornos controlados antes de `Done` são `Aprovação de Design -> Design`, `Code Review -> Em desenvolvimento` e `QA -> Em desenvolvimento`. Se um agente tiver avançado indevidamente para `Em desenvolvimento` sem passar por `Design`/`Aprovação de Design`/`Pronto para Dev`, deve regredir o card para `Design` (ou `Aprovação de Design` se a evidência de design já estiver completa), preservar o trabalho em branch e parar o `/opsx:apply` até a aprovação humana.

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
QA:
- SHA/run: ...
- qa-gate: ...
- Playwright visual: ... (ou dispensa autorizada: ...)
Code Review:
- no blocking findings / achados corrigidos ou classificados
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
- Quando Alan pedir `subir lote`, `fechar lote`, `fechar release`, `criar release`, `gerar release` ou equivalente, liste todos os cards `Homologado` incluídos no pacote, independente do responsavel. Para cards de `Codex`, liste os commits/branches que entram no pacote.
- Para cards da Clara ou Alan: reviso a documentação do projeto antes de fechar, atualizando Markdown local e Drive quando aplicável.
- Se `develop` contiver só conteúdo homologado do pacote, use PR `develop -> main`.
- Se `develop` contiver mudança não homologada, não faça merge direto `develop -> main`; crie `release-*` a partir de `main` e inclua somente commits/branches aprovados, ou peça decisão de Alan.
- Antes de mover cards para `Pronto`, confirme que cada card realmente entrou no merge para `main`.

### Testes

- Durante implementação: testes focados/proporcionais ao card, validação OpenSpec da change e evidência no handoff.
- Antes de `Code Review`: checks focados e validação OpenSpec da change precisam ter sinal suficiente para revisar o diff.
- Antes de `QA`: review Codex precisa estar limpo/classificado e o SHA revisado deve estar commitado/pushado.
- Antes de `Done`: `qa-gate` precisa estar verde, checks iniciados precisam terminar, Playwright visual e artifacts precisam estar registrados, e `./restart`/runtime precisam validar o resultado. Status "rodando", `cancelled` ou skip sem dispensa autorizada nao vale como evidência final.
- No fechamento de lote/release: `openspec validate --all`, testes completos proporcionais ao pacote, build e CI até resultado final.
- Se teste local ou CI falhar, corrija, revalide e só então siga para próximo status.

### QA visual obrigatorio

- Todo card executa Playwright visual por padrão, inclusive cards sem alteração em `frontend/**`.
- Mudança de UI inclui cobertura desktop/mobile da tela afetada e baseline versionado revisado no diff.
- Dispensa só é válida com label `qa-visual-skip` e comentário explícito de Alan: `QA visual dispensado por Alan.` seguido de `Motivo:` não vazio.
- Falha de QA que exige fonte retorna para `Em desenvolvimento -> Code Review -> QA`; falha de infraestrutura/flaky permanece em `QA` para rerun com evidência.

#### Fluxo canonico (rapido)

Seguir `alan-workflow` Visual QA. Quem compara pixels e o Playwright; o agente nao precisa ler todos os PNGs para “passar” o teste.

**Sem mudanca visual intencional**

1. Push do SHA revisado.
2. CI roda `npm --prefix frontend run test:e2e:visual`.
3. Igual a baseline → verde. Diferente → falha com artifacts (`actual`/`diff`).
4. Nao abrir todos os screenshots com vision; confiar no resultado do Playwright.

**Com mudanca de UI intencional**

1. No DEV Linux (`/srv/apps/dev/criptofarol/source`), atualizar baselines localmente:
   ```bash
   npm --prefix frontend run test:e2e:visual -- --update-snapshots
   ```
2. Revisar **somente** o `diff.png` (ou o diff git dos snapshots) dos cenarios que mudaram, uma vez, para confirmar que a mudanca e esperada.
3. Commitar os novos arquivos em `frontend/tests/e2e/**/*-snapshots/` junto com a mudanca de UI.
4. Push → CI revalida contra a baseline nova.

**Proibido por padrao**

```text
CI falha → baixar artifacts → Read/vision em todos os PNG
→ patch baseline → push → Waiting/polling → repetir
```

Olhar screenshot so para aprovar mudanca intencional (`diff.png` preferivel) ou quando Alan pedir julgamento visual/exploratorio.
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
scripts/release-guard pre
openspec validate --all
gh pr create --base main --head develop --title "<titulo>" --body "<resumo>"
gh pr merge --merge --delete-branch=false
scripts/release-guard post
```

Publicar com branch de release quando `develop` tiver conteúdo não homologado:
```bash
git switch main
git pull origin main
git switch -c release-YYYY-MM-DD
# incluir apenas commits/branches homologados
git cherry-pick <commit-homologado>
git push origin release-YYYY-MM-DD
scripts/release-guard pre
gh pr create --base main --head release-YYYY-MM-DD --title "<titulo>" --body "<resumo>"
gh pr merge --merge --delete-branch=false
scripts/release-guard post
```

Limpar branches após publicação/Pronto:
```bash
git worktree remove ../crypto-worktrees/change-<id>-<slug> # se usada
git branch -d change-<id>-<slug>
git push origin --delete change-<id>-<slug> # se publicada
```

Em entrega de código por card, use o executor fixo da etapa. Subagents auxiliares podem acelerar descoberta e validação, respeitando escopo e sem substituir Sol/Luna nem duplicar trabalho.

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
- Sempre que possível, acelere descoberta/validação com subagents auxiliares em tarefas médias/grandes, especialmente para mapear código, revisar riscos, validar UI/Playwright ou investigar bugs. Implementação, Code Review, QA e release continuam com o executor fixo da etapa; o agente principal consolida resultados e evita trabalho duplicado.
- Registre em `openspec/changes/<change>/` e no PR:
  - status atual
  - decisões de escopo
  - evidências de teste/PR
- Para promover produção, junte todos os cards `Homologado` incluídos no lote/release pedido por Alan. Para cards de `Codex`, confirme commits/branches incluídos, abra PR para `main`, resolva checks/políticas bloqueantes quando forem corrigíveis por código/configuração do repo e realize o merge manual do PR. Para cards de `Clara` ou `Alan`, revise e atualize a documentação do projeto em Markdown local e Drive quando aplicável. Depois mova os cards incluídos para `Pronto`.
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

- Para qualquer tarefa em `frontend/`, use o `DESIGN.md` como fonte obrigatória de qualidade visual, tokens, componentes, densidade, responsividade e validação.
- Para qualquer tela, componente visual ou funcionalidade com impacto de UI/UX, nova ou antiga, consulte e siga obrigatoriamente o `DESIGN.md` antes de implementar.
  - Registre no OpenSpec/hand-off quais tokens, componentes e padrões do `DESIGN.md` foram aplicados.
  - Não feche implementação visual sem validar aderência ao `DESIGN.md` em desktop/mobile quando aplicável.
  - Se houver desvio necessário do `DESIGN.md`, registre a exceção e a justificativa antes de codar ou fechar a entrega.
- **Upstream** deve ser uma conversa fluida (Humano ↔ Trader) para clarificar inputs/constraints/risco.
- O label "validator" na UI/copy deve aparecer como **Trader**.

## Agentes e responsabilidades

### Sol High — sessão principal, PO/DESIGN e QA

- Usa `gpt-5.6-sol` / `high` fixado em `.codex/config.toml`.
- Orquestra card/status, é dono de proposal/specs/design/tasks, publica artifacts e nunca autoaprova Alan.
- Em QA, inspeciona o SHA/diff revisado, executa `/opsx:verify`, consolida checks e não corrige código.
- Trata relatórios Luna como claims: inspeciona o diff/estado e repete validações antes de avançar.

### DEV — `crypto_luna_implementer`

- Usa `gpt-5.6-luna` / `max`, `workspace-write`, sempre com `fork_turns="none"`.
- Só executa após `Pronto para Dev` e `Status=Em desenvolvimento`.
- Executa `/opsx:apply`, implementação e testes focados dentro do ownership recebido.
- Não altera design aprovado, não revisa o próprio diff e não conduz release.

### REVIEW — `crypto_luna_reviewer`

- Usa uma nova thread `gpt-5.6-luna` / `max`, read-only, sempre com `fork_turns="none"`.
- Revisa o diff exato antes do commit, com findings por severidade e risco residual.
- Nunca edita nem implementa os próprios findings. Mudança invalida o verdict e exige nova reviewer.
- Exceção única: o bootstrap que instala os perfis usa revisão Codex independente read-only disponível na tarefa instaladora. Tarefas novas após configuração versionada/carregada exigem o perfil exato acima.

### RELEASE — `crypto_luna_release_manager`

- Usa uma nova thread `gpt-5.6-luna` / `max`, `danger-full-access`, sempre com `fork_turns="none"`.
- Só inicia após pedido explícito de Alan e pacote exato de cards `Homologado`.
- Somente dentro dessa release explicitamente autorizada executa documentação, sync/archive, validações, release guards, PR/CI/merge manual, reconciliação e evidências.
- Não altera código. Falha de código para a release sem regredir cards `Done`/`Homologado`.

### Regras operacionais dos agentes

- Workflow DB/Kanban é a fonte operacional; OpenSpec é a camada de artifacts.
- O bootstrap exige validação estática reproduzível + handoff, sem pre-spawn. Evidência runtime segura é coletada somente quando cada lane Luna for usada naturalmente após a ativação.
- Nenhuma aceitação de roteamento autoriza mudar AppArmor, sysctl, bubblewrap, user namespaces, sandbox launcher ou segurança do host/servidor.
- Agentes Luna usam agent type exato, `fork_turns="none"` e pacote autocontido; generic `worker`/`reviewer` não substitui lanes.
- Depois da ativação, o auto-trigger é: `Design` -> Sol; `Aprovação de Design` -> aguardar Alan; `Em desenvolvimento` -> Luna implementer; `Code Review` -> nova Luna reviewer; `QA` -> Sol; release explicitamente solicitada -> nova Luna release manager. Nenhuma lane é pre-spawned para smoke test.
- `change` é o container raiz; `story` é a fatia com ownership/dependência; `bug` é defeito real. No máximo 2 stories ativas por change e 1 por agent run.
- Locks ficam na story; bugs filhos bloqueiam fechamento. Antes de promover qualquer gate, reconciliar Status, tasks, handoff e evidências.
- Depois de Done não regredir Status; reexecutar as lanes técnicas mantendo o estado atual.

### Subagents auxiliares Codex

- `code_mapper`, `pr_explorer` e `browser_debugger` podem apoiar investigação/validação, mas nunca substituir o executor fixo da etapa.
- Não usar o built-in `worker` ou o `reviewer` genérico para desenvolvimento ou Code Review de card.
- O Sol principal continua responsável por escopo, consolidação, evidências e fechamento.

## Engenharia de prompt

Reforço de fluxo de fechamento: `Done` conclui somente a implementação validada em `develop` (Done tecnico); `Homologado` conclui aprovação funcional de Alan em `develop`; `Pronto` conclui produção após merge manual em `main` (via PR `develop -> main`) com validação e evidências registradas.

Se for necessário mudar o tom de um agente (ex: deixar o design mais exploratório ou o DEV mais cauteloso), primeiro atualiza este arquivo com o novo prompt/personalidade e registra no `openspec/changes/<change>/` do fluxo ativo. Nunca altere agentes apenas via jobs sem documentar aqui.
