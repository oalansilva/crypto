# Overlay cripto (on-demand)

Carregue com `Read docs/crypto-overlay.md` quando a tarefa precisar de portas/URLs, Drive, PostgreSQL ou release-guard/lote/PROD. O stub always-on da raiz é `AGENTS.md`. Este arquivo **não** entra em toda sessão.

## Escopo deste arquivo

- `rules.md` define as regras obrigatorias curtas do projeto.
- Este overlay detalha como executar essas regras na pratica: comandos, status, evidencias, OpenSpec/OPSX, GitHub Project, Git e responsabilidades dos agentes.
- Use o stub `AGENTS.md` + este overlay. Em conflito real, aplique a regra mais restritiva e registre a ambiguidade antes de alterar codigo, card ou Git.

## Processo global do Alan

- Runbook de processo: skill `.cursor/skills/alan-workflow/` **neste repo** (GitHub). Overlay cripto (board, ports, Drive, PostgreSQL, release-guard, `./restart`) fica neste arquivo. Lei humana: `rules.md`. Always-on curto: `.cursor/rules/harness.mdc`.
- **Em qualquer pedido de release, publicação, lote, deploy, produção ou operação que possa afetar DEV/PROD, carregue também `.cursor/skills/alan-workflow-ambientes/`** (mapa DEV/PROD e deploy PROD antes de `Pronto`).
- Board: skill `.cursor/skills/github-project-board/`. Não tratar `~/.codex/skills/` nem `/srv/knowledge/hermes-second-brain/skills/` como canônico destas três skills.
- No cripto, o fluxo é `Em Refinamento -> Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto` (detalhe na skill). `Todo` não é código. Pedido `implemente` não pula Design.
- Se uma regra geral de processo precisar mudar, edite `.cursor/skills/alan-workflow/` neste repo (não dual-write hermes/Codex).

## TL;DR

- **Skills:** `.cursor/skills/alan-workflow`, `alan-workflow-ambientes`, `github-project-board` (arquivos reais no GitHub). OpenSpec: `.cursor/skills/openspec-*`. Design: `.agents/skills/design-critic`.
- **Branch padrão:** cada card/change usa branch própria a partir de `develop` (`change-<id>-<slug>` ou `card-<id>-<slug>`). `develop` é integração/homologação; `main` é produção.
- **Board:** `github.com/users/oalansilva/projects/1`. Campo `Status` manda. Alan é o único que arrasta `Aprovação de Design -> Pronto para Dev`. Código só com `Pronto para Dev`.
- **OpenSpec no card:** Gist `crypto openspec <change>` **superset** do issue; republicar o mesmo Gist. Helper: `.cursor/skills/alan-workflow/scripts/publish-openspec-card-artifacts.sh`.
- **Banco:** PostgreSQL (`DATABASE_URL`, `WORKFLOW_DATABASE_URL`). Não usar SQLite em runtime/QA.
- **Release:** `alan-workflow` + `alan-workflow-ambientes`; `scripts/release-guard pre|post`; deploy PROD obrigatório antes de `Pronto`. Detalhe das 12 colunas, gates e higiene: skill `alan-workflow` + `rules.md` §3.
- **Colunas/Status:** no cripto, o campo `Status` e a fonte principal das colunas visuais. `Em Refinamento` é a **primeira coluna** (antes de `Todo`) e a **entrada obrigatória de todo card novo**: em `Em Refinamento`, Alan escolhe, prioriza (campo `Prioridade`) ou cancela o card antes de ir para `Todo`. O fluxo obrigatório de **todo** card é `Em Refinamento -> Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`; `Cancelado` é terminal (acionável inclusive a partir de `Em Refinamento`). Cards kaizen também nascem em `Em Refinamento`. **Proibido** pular `Design`, `Aprovação de Design` ou `Pronto para Dev` (inclusive com `UI impact: none`, remoção, bug ou pedido `implemente`). O arraste `Aprovação de Design -> Pronto para Dev` é a aprovação humana de Alan. `Done` continua sendo Done tecnico e `Pronto` continua exigindo deploy em PROD (source PROD no commit publicado + services reiniciados + URL pública validada) com evidencia; merge em `main` sozinho não é evidência de `Pronto`.
- **Fluxo de produção:** implemente em branch da change, integre em `develop` para homologação, acumule cards homologados quando fizer sentido; para liberar produção, abra PR `develop -> main` quando `develop` contiver só conteúdo homologado do pacote **e** o push/archive em `develop` for permitido; use `release-*` quando precisar congelar só parte aprovada **ou** quando a proteção de `develop` (`qa-gate`) recusar o push do archive/closeout mesmo com pacote só Homologado. Resolva checks/políticas bloqueantes quando possível e realize o merge manual quando permitido, sem auto-merge.
- **Regra de fluxo:** não implemente diretamente em `main`; não implemente diretamente em `develop` salvo ajuste mínimo autorizado por Alan. Branch por change é o padrão.
- **Regra de merge de release/lote:** após abrir um PR para `main` dentro de um fechamento de lote/release solicitado por Alan, execute o merge manualmente quando os checks estiverem verdes e não houver bloqueios.
- **Regra de autonomia operacional:** dentro de fechamento de lote/release solicitado por Alan, após validação e evidência, o agente tem autonomia para repetir tentativas manuais de merge até resolução de bloqueios resolvíveis no repositório, sem pedir nova autorização.
- **Regra de implementação por card:** seguir `alan-workflow`; no cripto, usar o board `github.com/users/oalansilva/projects/1`, criar/usar branch propria da change a partir de `develop`, **sempre** concluir o gate `Design -> Aprovação de Design` e só então aguardar `Status=Pronto para Dev`, mover para `Status=Em desenvolvimento` antes de aplicar tarefas de código, mover para `Status=Code Review` antes do commit, rodar os reviewers locais (`diff-reviewer` + `code-reviewer`) no diff não commitado vs HEAD, commit do SHA, rodar `diff-reviewer` em `origin/develop...HEAD` **ainda na branch do card** antes de `QA`, push, mover para `Status=QA`/`Fluxo=QA`, aguardar `qa-gate` e Playwright visual verdes, integrar por PR em `develop`, executar `./restart`, validar a URL e so entao mover o card para `Status=Done` como Done tecnico. Nao arquivar nem publicar em `main` nesta etapa.
- **Regra de conclusão de correção:** para qualquer correção de bug ou ajuste solicitado por Alan, só diga `concluído` depois de validar, fazer merge/integração da branch de trabalho em `develop`, executar `./restart` e confirmar que a URL do sistema está servindo o bundle/resultado novo. Antes disso, reporte como `corrigido na branch`, `validado localmente` ou `aguardando integração`, conforme o estado real.
- **Regra de homologação direta por card (solicitação do cliente):** seguir `alan-workflow`; no cripto, homologacao significa aprovacao funcional em `develop`.
- **Guardrail anti-release acidental:** seguir `alan-workflow`; no cripto, homologacao nao autoriza `main`, PR, merge, archive ou release.
- **Regra de release/lote:** seguir `alan-workflow` e `alan-workflow-ambientes`; no cripto, selecione todos os cards `Homologado` incluídos no pacote, confirme commits/branches, rode validação final completa, arquive OpenSpec, abra PR para `main` (via `develop` ou `release-*`), merge manual, **execute o deploy em PROD** (`/srv/apps/prod/criptofarol/source`: `git fetch origin && git reset --hard origin/main`, `alembic upgrade head`, build do frontend com `VITE_APP_ENV=production`, restart dos services PROD afetados e validação do endpoint público `https://criptofarol.com.br`). No caminho archive-via-`release-*`, após o merge em `main` o sync `main → develop` é **obrigatório** antes do `post` final (árvores idênticas); reexecute `scripts/release-guard post` depois do sync se o primeiro `post` falhar por diverge. Só então mova os cards incluídos para `Pronto`. Deploy em PROD é parte obrigatória do fechamento; merge em `main` sem deploy e validação em PROD não autoriza `Pronto`.
- **Ordem canônica de fechamento de release (card #518):** 1) merge manual do PR da release; 2) deploy em PROD e captura da evidência final; 3) execução de `/kaizen release` ainda com os cards em `Homologado`; 4) atualização conjunta de `docs/release-<data>.md` e `docs/kaizen-log.md` em um único commit/PR documental; 5) merge do PR documental e `git switch main && git pull --ff-only origin main`; **5b) no caminho archive-via-`release-*` (card #617): sync obrigatório `main → develop` (PR ou merge) para árvores idênticas — inserir aqui, não substituir os demais passos**; 6) deleção local e remota das branches declaradas do pacote; 7) `RELEASE_DATE=... RELEASE_CARDS=... RELEASE_BRANCHES=... PROD_DEPLOY_EVIDENCE=... scripts/release-guard post` (reexecutar se o sync 5b ainda não tiver rodado ou as árvores divergirem); 8) somente após PASS, promoção dos cards para `Pronto`. O `post` exige `RELEASE_BRANCHES` não vazio com branches ausentes local+remota, entrada canônica de `/kaizen release` em `docs/kaizen-log.md` na data **mais materialização Kaizen** (1–3 cards novos, dedupe `coberto por #N` em fluxo, ou `Sem achados acionáveis` — #661), doc canônica sem placeholder e `main` local sincronizada (`--ff-only`); o guard permanece read-only. **Uma doc canônica por data** (`docs/release-YYYY-MM-DD.md`); vários pacotes no mesmo dia atualizam o mesmo arquivo após cada deploy (proibido `-lote2.md`). O `pre` de um PR de código (diff `origin/main...origin/develop`, ou `origin/main...HEAD` em `release-*`, com qualquer path fora do allowlist `docs/**` / `openspec/changes/archive/**` / `openspec/specs/**` / `AGENTS.md` / `rules.md`) **não** herda `PROD_DEPLOY_EVIDENCE` do lote anterior só porque a doc do dia já existe. O `pre` de um PR documental (unpublished vazio ou ⊆ allowlist) continua exigindo evidência **deste** pacote + doc sem placeholder. O `post` amarra a evidência ao commit de código/PROD deste lote (ancestral de `origin/main` cujo `evidence..origin/main` ⊆ allowlist, com abreviação ≥7 na doc). Não relaxar deploy PROD antes de `Pronto`.
- **Regra de spawn vazio de subagent (card #518):** após qualquer delegação via Task tool, verifique que o resultado contém ao menos uma mensagem e uma part utilizável. `0 messages`, `0 parts`, sessão ausente ou erro de criação são **falha explícita**: a etapa permanece incompleta, o handoff registra `ERROR: subagent spawn failed/empty` com identificador e impacto, e não há fallback silencioso nem alegação de que a etapa delegada ocorreu.
- **Regra documental de release da Clara/Alan:** quando Alan pedir `gerar release`, `criar release`, `fechar release`, `subir lote` ou equivalente para cards no nome da Clara ou do Alan, antes de publicar/encerrar o pacote, pegue todos os cards `Homologado` por Alan e com `Responsavel=Clara` ou `Responsavel=Alan` incluídos na release e revise se as decisões, status e entregáveis desses cards estão refletidos na documentação do projeto/produto. A documentação precisa ficar atualizada tanto nos Markdown locais quanto nos Google Docs/Drive correspondentes. Depois da release publicada/encerrada com evidência, mova esses cards de `Homologado` para `Pronto`. Cards de harness/tooling seguem o mesmo fluxo técnico no mesmo pacote.
- **Regra de não regressão de status:** depois que um card estiver em `Done`, nunca mova de volta para `Em desenvolvimento` durante homologação, archive, commit, PR ou merge. Se aparecer falha, ajuste necessário ou reteste, corrija e reteste mantendo o status atual. O card só avança: `Done` -> `Homologado` -> `Pronto`.
- **Regra de confiabilidade por testes:** em qualquer etapa, se surgir erro de testes (locais ou CI), corrija, revalide e só então siga para próxima etapa de encerramento.
- **Regra de validação OpenSpec global:** `openspec validate --all` verde é critério padrão de fechamento. Se falhar por changes antigas fora do card, valide os specs afetados pelo card como evidência parcial, mas resolva a sujeira global antes do encerramento: corrija ou arquive as changes antigas, inclusive por archive manual quando a CLI/skill não conseguir concluir.
- **Regra de checks em execução:** seguir `alan-workflow`; no cripto, isso vale para testes locais, `openspec validate`, build e CI antes de `Code Review`, `QA`, `Done`, release/lote, commit, PR ou merge. Check `running`, `cancelled` ou skip sem dispensa autorizada nao e evidencia final.
- **Regra de espera de CI:** use um unico watcher nativo por PR com timeout explicito: `timeout 35m gh pr checks <PR> --watch --fail-fast --interval 20`. Nao filtre apenas checks marcados como required, porque todos os checks iniciados precisam terminar e OpenSpec pode nao estar na protecao de `main`. Esperas acima de 60 segundos rodam em background quando o cliente suportar. Sao proibidos loops `for`/`while` com `sleep`, consultas repetidas pelo modelo e subagent criado apenas para polling. Timeout, falha, check ausente ou bloqueio encerram a tentativa sem merge; depois do verde, consulte mergeabilidade uma vez e faca no maximo uma tentativa manual para o estado observado. Qualquer falha exige diagnostico e uma nova verificacao completa de prontidao antes de outra tentativa.
- **Regra de commits e testes:** commits locais na branch da change são permitidos e não exigem suíte completa a cada commit, mas exigem os reviewers locais (`diff-reviewer` + `code-reviewer`) no diff não commitado vs HEAD antes de cada commit de implementação. Durante o card, rode testes proporcionais/focados; testes completos ficam para fechamento de lote/release.
- **Regra de worktree limpo no fechamento:** seguir `alan-workflow`; no cripto, trabalho de outra change deve ir para branch/worktree própria e a integração padrão acontece em `develop` antes de produção.
- **Regra de varredura da release:** seguir o inventario/classificacao de `alan-workflow`; no cripto, integre o que deve entrar em `develop`, publique em `main` via PR/merge manual quando permitido e só então limpe branches/worktrees.
- **Regra de guard automatizado de release:** antes de abrir/mesclar PR de release, rode `scripts/release-guard pre`; depois do merge/publicação e antes de reportar limpeza final, rode `scripts/release-guard post`. Se qualquer modo estrito falhar, pare e classifique/corrija todos os bloqueios antes de seguir. Use `scripts/release-guard audit` para diagnostico sem bloqueio durante desenvolvimento. Worktree extra ou branch local in-flight no `pre` exige `PRESERVED_BRANCHES=<branch1,branch2>` (trim, match exato); o `pre` não consulta o board. Extra já mergeada em `origin/develop` vira warn (remover no closeout, sem commit vazio). Dirty classificada na lista vira warn; dirty em branch mergeada só é permitida se o único path for `docs/release-${RELEASE_DATE}.md` (rename porcelain é blocker).
- **Regra de evidência de deploy PROD no guard:** `release-guard post` (e `pre` após a publicação) exige `PROD_DEPLOY_EVIDENCE` com `<commit-publicado> services=<svcs> url=<url-publica>` antes de mover cards para `Pronto`; sem evidência, o guard falha em modo estrito. No `pre` antes do merge a evidência ainda não é exigida (deploy ocorre após o merge).
- **Regra de inventário de refs órfãs no guard post:** `release-guard post` lista refs `runtime-*`/`rollback-*`/`release-post-*`/`sync-*`/`preserve/*` e worktrees em branch órfã, exigindo classificação (integrar/preservar/limpar com autorização) e sinalizando WIP não commitado; itens não classificados são blockers no fechamento.
- **Regra de evidência documental e campos do board no guard post:** antes de mover cards para `Pronto`, o `release-guard post` valida: doc de release commitada e sem placeholders (TBD/TODO/lorem/`<!--`/FIXME), uma doc canônica por data (2+ docs da mesma data com conteúdo divergente = blocker) e campos do board (Responsável/Prioridade/Tipo) preenchidos; no fechamento, exporte `RELEASE_CARDS=<n1,n2,...>` com os cards do pacote para o guard validar exatamente o pacote (cards fora do pacote com campos faltando são warn/dívida legada, não bloqueiam). Falha do próprio check (gh/jq) também é blocker (fail-closed).
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
- **Roteamento de LLM:** o modelo selecionado no chat do Cursor é a fonte única do LLM/modelo da tarefa (hoje Grok 4.6). Todo subagent/`Task` deve herdar esse modelo (`inherit`) salvo pedido explícito de Alan no chat. Papéis e prompts podem variar; não há Sol/Pro/Qwen obrigatórios nem fallback de modelo.
- **Análise de imagem:** a sessão Cursor lê pixels com a ferramenta `Read` depois de confirmar que o path existe. Se o modelo do chat não aceitar imagem, declare o bloqueio ou peça a Alan um modelo com visão. Não exigir `vision-router`, Qwen nem subagent `vision` do OpenCode.
- **Gate Design:** a sessão Cursor escreve os artefatos OpenSpec e o protótipo (quando UI). Em seguida dispara `Task` isolada no mesmo modelo, instruída a não editar, para a crítica. Sem lease, packet selado, `design_artifact_write` ou attestation OpenCode. A main publica e pode mover somente `Design -> Aprovação de Design`.
- OpenSpec é a camada de especificação técnica (artifacts).
- Workflow DB e OpenSpec são fontes de operação e evidência.
- **Regra de documentação produto/Drive:** documentos de produto/projeto que existem no Google Drive e em `docs/*.md` devem ser mantidos sincronizados. Drive é a fonte de consulta/revisão para Alan; Markdown local/GitHub é espelho versionado e backup técnico. Não editar manualmente nos dois lugares de forma divergente. Ao atualizar definição aprovada, atualize o `.md` local e sincronize o Google Doc correspondente, ou atualize o Drive e depois espelhe localmente. Para código e documentação técnica de implementação, GitHub continua mandando.
- **Caminhos locais/versionados de documentação:** use `crypto/docs/project-hub.md` como hub central do projeto; `crypto/docs/decision-log.md` para decisões relevantes; `crypto/docs/mvp-scope.md` para escopo do MVP; `crypto/docs/backlog-operating-model.md` para modelo operacional do backlog/release; `crypto/docs/landing-page.md` para definição/copy da landing; `crypto/docs/brand-system.md` para marca, tom e identidade; `crypto/docs/beta-*.md` para materiais do beta, validação, convite, Telegram e conteúdo; `crypto/docs/release-*.md` para registro de release; e `crypto/docs/kaizen-log.md` para o log de melhoria contínua de processo (quanto mais o processo é usado, melhor ele fica — cada auditoria alimenta regras/skills/scripts).
- **Fontes externas de consulta/status:** use o Google Drive da Clara, na pasta do projeto cripto (`https://drive.google.com/drive/folders/1OE0D_nsb7BAMQ_ntZXUonnsfX9MtXhT9`), com documentos de texto sempre na subpasta `Docs` (`1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx`) e planilhas na subpasta `Planilhas` quando aplicável; o GitHub Project `MVP Cripto - Beta Fechado` como fonte operacional dos cards/status; e Issues/PRs do GitHub quando o item tiver evidência técnica ou comentário de release.
- **Regra prática de sincronização:** documento de produto/processo atualiza local em `crypto/docs/` e sincroniza no Drive. Execução/status atualiza GitHub Project e, quando houver código, Issue/PR. Não edite Drive e Markdown de forma divergente.
- **DoD de documentação sincronizada:** uma atualização documental só está concluída quando os dois lados estão atualizados e conferidos: Markdown local/versionado em `crypto/docs/` e Google Doc/Sheet correspondente no Drive. Se apenas o Drive foi atualizado, espelhe imediatamente no Markdown local; se apenas o Markdown local foi atualizado, sincronize imediatamente no Drive. Não mova card para `Pronto`, não feche release e não reporte documentação como concluída sem evidência dos dois lados.
- **Passo obrigatório de Drive em release:** ao criar/subir release, depois de atualizar os Markdown locais, sincronize os documentos aplicáveis no Google Drive da Clara. Para usar `gog` sem TTY, carregue `GOG_KEYRING_PASSWORD` do Bitwarden Secrets Manager (`Crypto` / `GOG_KEYRING_PASSWORD`). Primeiro liste a subpasta `Docs` com `gog drive ls --account claravalente840@gmail.com --parent 1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx --json --no-input`; se já existir Google Doc equivalente, atualize o mesmo ID com `gog docs write <docId> --file <arquivo.md> --markdown --replace --pageless --no-input`; se não existir, crie diretamente nessa subpasta com `gog docs create "<titulo-sem-prefixo>" --account claravalente840@gmail.com --parent 1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx --file <arquivo.md> --pageless --no-input`. Nunca crie documentos soltos na raiz da pasta do projeto. Ao final, valide com `gog drive ls --account claravalente840@gmail.com --parent 1X01niQNrPh2wLy5WqJb2iBN8QnzTKGBx --json --no-input` e registre os links/evidência da sincronização.

## De-para OpenSpec/OPSX no Cursor

O projeto usa o Cursor Agent como ferramenta única de desenvolvimento. As skills OpenSpec são geradas pela CLI e versionadas em `.cursor/skills/` e `.cursor/commands/`. Trate `/opsx:*` como a intenção canônica e `/opsx-*` como o slash command do Cursor. Se o cliente não interpretar uma das formas, trate o texto como intenção operacional e acione a skill local equivalente. Não substitua a skill por criação manual de arquivos.

No **Cursor**, as skills do projeto carregam de `.cursor/skills/` (`alan-workflow`, `alan-workflow-ambientes`, `github-project-board`, OpenSpec, kaizen) e `.agents/skills/` (design-critic, impeccable, playwright-cli). Os commands `/opsx-*` e `/kaizen` vivem em `.cursor/commands/`. O hook Impeccable está em `.cursor/hooks.json` e chama `.agents/skills/impeccable/scripts/hook.mjs`. Invocar `/opsx-new` ou a skill `openspec-new-change` tem o mesmo efeito.

Os arquivos em `.cursor/skills/openspec-*` e `.cursor/commands/opsx-*.md` são adaptadores oficiais. Atualize-os com a mesma CLI:

```bash
openspec init --tools cursor --force
```

Regra obrigatória:
- Primeiro use a skill OpenSpec correspondente.
- Depois execute a CLI `openspec` indicada pela própria skill.
- Só crie ou edite arquivos em `openspec/changes/<change>/` seguindo `openspec instructions ... --json`.
- Não invente artefatos manualmente fora do fluxo da skill.
- Ao final de cada etapa, registre no handoff/status qual skill foi usada, qual comando CLI foi executado e qual evidência foi produzida.

De-para principal:

| Intenção canônica | Comando Cursor | Skill obrigatória | CLI base | Resultado esperado |
| --- | --- | --- | --- | --- |
| `/opsx:new <change>` | `/opsx-new <change>` (`.cursor/commands/opsx-new.md`) | `$openspec-new-change` | `openspec new change "<change>"`; `openspec status --change "<change>"`; `openspec instructions <artifact-id> --change "<change>"` | Cria apenas o scaffold da change, mostra status e instrução do primeiro artifact. Não cria artifacts ainda. |
| `/opsx:ff <change>` | `/opsx:ff <change>` | `$openspec-ff-change` | `openspec status --change "<change>" --json`; `openspec instructions <artifact-id> --change "<change>" --json` | Gera todos os artifacts necessários para ficar pronto para implementação, respeitando dependências e templates retornados pela CLI. |
| `/opsx:apply <change>` | `/opsx:apply <change>` | `$openspec-apply-change` | `openspec status --change "<change>" --json`; `openspec instructions apply --change "<change>" --json` | Lê `contextFiles` e implementa as tasks pendentes. Em **todo** card, só começa código depois de `Pronto para Dev`. |
| `/opsx:verify <change>` | `/opsx:verify <change>` | `$openspec-verify-change` | `openspec list --json` quando a change estiver ambígua; `openspec status --change "<change>" --json`; `openspec instructions apply --change "<change>" --json` | Verifica completude, corretude e coerência entre artifacts, specs, tasks, design, testes e implementação real. |
| `/opsx:archive <change>` | `/opsx:archive <change>` | `$openspec-archive-change` | `openspec status --change "<change>" --json`; avaliar sync de specs; mover para `openspec/changes/archive/YYYY-MM-DD-<change>/` | Arquiva somente no fechamento de lote/release após homologação, checando artifacts, tasks, delta specs e registrando warnings se algo ficar incompleto. |

Antes de executar `/opsx:apply` em qualquer change vinculada a card/issue, siga `alan-workflow` e publique os artefatos OpenSpec no card. Convencao local do Gist: descricao `crypto openspec <change>` e comentario no card do Project 1.

**Republicação de artefatos (sem Gist sprawl):** ao republicar os artefatos OpenSpec de uma change já publicada, use `publish-openspec-card-artifacts.sh --gist-id <id>` com o Gist da publicação anterior (e `--comment-id <id>` para atualizar o comentário existente) — nunca criar novo Gist nem novo comentário para a mesma change. O Gist novo só é criado na primeira publicação. Depois da republicação, registre o `gist_url`/`comment_url` atualizados no handoff.

**Retrigger de CI sem commit vazio:** para reagendar checks sem mudança de código, use `workflow_dispatch` em vez de commit vazio, ex.:
```bash
gh workflow run <workflow-name>.yml --repo oalansilva/crypto --ref <branch> [--field <name>=<value>]
# ou, para reagendar todos os checks do PR:
gh pr checks <PR> --watch --fail-fast --interval 20
```
Commit vazio como retrigger é proibido. Agrupe ajustes pós-review de um card em um único commit/PR, evitando PRs fragmentados por ajuste.

De-para complementar:

| Intenção canônica | Comando Cursor | Skill obrigatória | Uso correto |
| --- | --- | --- | --- |
| `/opsx:explore [change]` | `/opsx:explore [change]` | `$openspec-explore` | Explorar decisões e riscos sem implementar código; pode preparar artifacts quando solicitado. |
| `/opsx:continue <change>` | `/opsx:continue <change>` | `$openspec-continue-change` | Continuar a criação do próximo artifact pronto, usando `openspec status` e `openspec instructions`, sem pular dependências. |
| `/opsx:sync <change>` | `/opsx:sync <change>` | `$openspec-sync-specs` | Sincronizar delta specs de `openspec/changes/<change>/specs/` para `openspec/specs/` antes ou durante o archive, conforme avaliação da skill. |
| `/opsx:bulk-archive` | `/opsx:bulk-archive` | `$openspec-bulk-archive-change` | Arquivar várias changes concluídas, uma a uma, preservando evidência e warnings por change. |
| `/opsx:onboard` | `/opsx:onboard` | `$openspec-onboard` | Fazer onboarding guiado do fluxo OpenSpec antes de iniciar implementação quando o contexto operacional estiver confuso. |

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
  -> todo card novo entra em Em Refinamento (primeira coluna; Alan escolhe/prioriza/cancela)
  -> mover para Todo após refinamento e seguir o fluxo normal
  -> mover para Design; declarar UI impact affected|none com justificativa
  -> invocar design-critic; concluir design.md + Design Critique
  -> se UI impact = affected: Prototype verificável também obrigatório
  -> se UI impact = none: Prototype pode ser N/A explícito, sem pular colunas
  -> mover para Aprovação de Design e aguardar Alan
  -> Alan aprova arrastando para Pronto para Dev
  -> proibido bypass Em Refinamento/Todo->Pronto para Dev ou Todo/Design->Em desenvolvimento

/opsx:apply <change>
  -> usar $openspec-apply-change
  -> somente com Status=Pronto para Dev: mover para Em desenvolvimento
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

### Designer/Critic Agent compartilhado

- O contrato canônico fica em `.agents/skills/design-critic/SKILL.md` (fonte única; não duplique regras em outros diretórios).
- No Cursor, invoque a skill `design-critic` (carregada de `.agents/skills/` e referenciada pelo harness). Pedido equivalente em linguagem natural também deve acionar a skill durante `Status=Design` de **qualquer** card.
- O Designer/Critic Agent prepara a entrega de design: com UI, produz/refatora o protótipo e critica produto/UX/a11y/responsividade/estados; sem UI nova, registra decisão enxuta e ausência de superfície visual. Resolve achados bloqueantes no escopo e registra `Design Agent verdict` no `design.md`.
- **Impeccable (pipeline formal via skill):** para `UI impact: affected`, executar a skill local em `context -> shape -> prototype -> critique -> audit -> targeted fixes -> polish -> browser gate`, registrar `Impeccable Brief`, `Impeccable Critique`, `Impeccable Audit` e `Impeccable Trace`, e manter `DESIGN.md` sem sobrescrita. Assessment A e B usam `Task` isolada no **mesmo modelo do chat**, instruída a não editar. Sem crítica isolada, o veredito é `BLOCKED`. Para `UI impact: none`, registrar Impeccable como `N/A` com justificativa e manter todos os gates.
- **Impeccable (hook Cursor):** `.cursor/hooks.json` dispara o detector (`.agents/skills/impeccable/scripts/hook.mjs`) em `afterFileEdit` e `stop`. O hook não substitui a crítica, o audit nem o browser gate; findings durante edição servem de alerta.
- O agente só pode mover `Design -> Aprovação de Design` quando `design.md` e `Design Critique` estiverem completos e, se `UI impact: affected`, o `Prototype` também. Nunca pode mover `Aprovação de Design -> Pronto para Dev`, autoaprovar ou alegar identidade de Alan.
- **Protótipos HTML navegáveis (Cripto):** publicar em `frontend/public/prototypes/<change-or-card-slug>/` (preferir `index.html`). URL canônica: `https://dev.criptofarol.com.br/prototypes/<change-or-card-slug>/`. No DEV, o Caddy encaminha `/prototypes*` para `criptofarol-dev-prototypes.service` (`127.0.0.1:5176`, `scripts/dev_prototype_server.py`), que lê `source/frontend/{public,dist}` **e** `crypto-worktrees/*/frontend/public/prototypes/` e **nunca** faz fallback SPA. Protótipo só no worktree do card já responde na URL pública; não copiar para `source` nem rebuild do preview só para o Alan abrir o link. Ausência = HTTP 404 HTML (não o React). Helper: `publish-openspec-card-artifacts.sh` com `--prototype-url` (nunca HTML no Gist).
- **Fidelidade do protótipo ao sistema atual:** se a tela/rota/shell já existir, o protótipo deve clonar a UI atual (sidebar/header, tokens de `DESIGN.md`/`index.css`, tipografia, densidade, estados) e redesenhar apenas o delta do card por cima. Alan valida diferença, não uma tela inventada. Se a tela ainda não existir, desenhar a nova superfície alinhada a `DESIGN.md` e ao shell autenticado do app; não usar layouts genéricos/marketing.
- **Browser gate antes do PASS:** abrir a URL final do protótipo em navegador real (preferir Playwright), em desktop e mobile, e exercitar estado padrão + todas as interações relevantes. Transformar critérios críticos em asserts; em remoções, provar `count=0`/`not visible`/`display:none` no estado final. Verificar console/page errors. Registrar comando/URL/viewports/asserts em `design.md` sob `## Prototype Validation`. `curl`, HTTP 200, build ou inspeção estática não substituem esse gate.
- **Evidência vinculada à versão:** qualquer alteração posterior em HTML/CSS/JS, rebuild ou restart invalida a validação anterior e exige nova execução. Sem navegador disponível ou com assert falhando, manter `Status=Design` e `Design Agent verdict: BLOCKED`.

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
- `release-*`: branch opcional para (a) congelar pacote quando `develop` contiver mudanças ainda não homologadas, ou (b) carregar o archive/closeout OpenSpec quando o push em `develop` for recusado pela proteção (`qa-gate`/checks required), **mesmo** se `develop` só tiver conteúdo Homologado. Nesse caso `release-* = origin/develop + archive` → PR para `main`; depois sync `main → develop` obrigatório antes do `post` final.

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
4. Cards novos entram em `Status=Em Refinamento` (primeira coluna): Alan escolhe/prioriza/cancela; após refinamento, mover para `Status=Todo`. Executar OpenSpec (`/opsx:new`, `/opsx:ff`) e publicar os artifacts no card.
5. Mover para `Status=Design`, invocar `design-critic`, concluir `design.md` + `Design Critique` (e `Prototype` quando UI impact = affected), mover para `Status=Aprovação de Design` e **aguardar Alan** arrastar para `Pronto para Dev`. Pedidos como `implemente` / `pode codar` **não** autorizam pular este gate.
6. Somente em `Pronto para Dev`, mover para `Status=Em desenvolvimento`, executar `/opsx:apply` e `/opsx:verify` e implementar.
   - **`UI impact: affected`:** `/opsx:apply` carrega `design.md` + o protótipo aprovado (`frontend/public/prototypes/<change-or-card-slug>/`) como **spec de UI** antes de editar `frontend/src`. Contrato de API é fonte de dados/integração, não de layout. O handoff/PR registra o path do protótipo, os elementos seguidos e qualquer desvio justificado; ausência desse registro bloqueia o apply. Antes de `Code Review`, comparar a rota entregue com o protótipo (layout, componentes, estados, a11y, responsividade) e registrar o resultado.
7. Rodar testes proporcionais/focados e validação OpenSpec da change.
8. Mover card para `Status=Code Review` e sincronizar `Fluxo=Code Review` quando existir.
9. Rodar os reviewers locais no diff não commitado vs HEAD (prompts abaixo) antes do commit. Se houver rework grande, voltar para `Em desenvolvimento`; se forem ajustes pequenos, manter `Code Review` e repetir o review.
   - **`UI impact: affected`:** o review inclui o item bloqueante "UI tasks: implementadas e verificadas contra o protótipo". Task `[x]` sem o controle/estado no código é blocker de commit. `/opsx:verify` confronta tasks × implementação × protótipo; comparação ausente bloqueia `Done`.
   - Task de Playwright/frontend `[ ]` bloqueia `Done` em qualquer card. `/opsx:verify` trata UI/`frontend` `[x]` sem implementação como CRITICAL.
10. Fazer commit do SHA revisado. Ainda na branch do card e **antes** de `Status=QA`, rodar `diff-reviewer` em `origin/develop...HEAD` nesse SHA (reuso se este run já existir). Depois push, mover para `Status=QA` e sincronizar `Fluxo=QA` quando existir.
11. Abrir PR para `develop`, aguardar `qa-gate` terminal verde e corrigir qualquer falha antes da integração.
12. Integrar em `develop` quando pronto, preferencialmente com squash/commit único por card referenciando o card.
13. Executar `./restart` e validar a URL/runtime.
14. Mover para `Status=Done` com comentário de evidência tecnica, citando o `diff-reviewer` uncommitted, o `diff-reviewer` vs `develop` e o `code-reviewer`. Se o SHA mudou depois do passo 10 (rework de QA), repetir `origin/develop...HEAD` **na branch do card** antes de integrar em `develop` — nunca depois do squash em `develop` (diff vazio).

### Code Review local (reviewers inherit/readonly)

Em `Status=Code Review`, o revisor padrão é o par versionado `diff-reviewer` + `code-reviewer` (`Task` `generalPurpose`, `model: inherit`, read-only), não um `Task` genérico e não `/review-bugbot`. A sessão principal corrige ou classifica achados; os reviewers não editam. Autofix **não** commita na branch existente. Agent Review automático pós-commit permanece desligado. O produto Bugbot no dashboard permanece Off de propósito (custo).

**Pré-commit** (todo commit de implementação). Lançar os dois Tasks; o prompt de cada um é o corpo do arquivo + o diff vs HEAD:

```text
Worktree: <worktree absoluta>
Diff: uncommitted changes versus HEAD
```

**Fechamento** (obrigatório uma vez no SHA, **ainda na branch do card**, imediatamente após o commit de implementação e **antes** de `Status=QA`). Nunca depois do squash em `develop` (diff vazio). Reuso só se este run já existir para o mesmo SHA. Só o `diff-reviewer` é obrigatório neste momento (`code-reviewer` MAY reusar o run pré-commit):

```text
Worktree: <worktree absoluta>
Diff: origin/develop...HEAD
```

**`/review-bugbot` e `/review-security`** são opcionais. Só disparam se Alan pedir no card. Não ligar por glob de path. O `diff-reviewer` local já cobre auth/credencial/trading/wallet/API via `.cursor/BUGBOT.md`.

**Spawn vazio:** 1 retry. Se persistir, registrar `ERROR: subagent spawn failed/empty`. A sessão principal MAY completar o review e citar residual no Done. Fallback nunca é o caminho feliz.

Regras que os reviewers locais lêem: `.cursor/BUGBOT.md` (raiz + aninhados). Files `.cursor/rules/*.mdc` **não** substituem esse contrato.

### Colunas Kanban

- O campo `Status` e a fonte principal das colunas. O campo `Fluxo`, quando existir, e substatus/legado; se houver divergencia, `Status` prevalece.
- `Em Refinamento`: primeira coluna e entrada obrigatória de todo card novo; Alan escolhe, prioriza (campo `Prioridade`) ou cancela o card antes de ir para `Todo`. Cards kaizen também nascem aqui.
- `Todo`: backlog ou pronto para comecar.
- `Design`: Designer/Critic Agent prepara evidências da solução (protótipo quando houver UI; decisão enxuta quando não houver).
- `Aprovação de Design`: entrega completa aguardando decisão humana de Alan. Coluna obrigatória para todo card.
- `Pronto para Dev`: design aprovado por Alan via arraste; único status que libera desenvolvimento.
- `Em desenvolvimento`: o Cursor Agent/Clara está implementando, investigando, validando ou corrigindo achados de review.
- `Code Review`: diff pronto para os reviewers locais (`diff-reviewer` + `code-reviewer`) antes do commit; achados bloqueantes precisam ser corrigidos ou classificados. Generic `Task` sem esses prompts não é o revisor do caminho feliz. `/review-bugbot` só se Alan pedir.
- `QA`: SHA revisado em validacao automatizada; `qa-gate`, Playwright visual e demais checks obrigatorios precisam terminar verdes.
- `Done`: Done tecnico; QA verde, implementação técnica revisada, integrada em `develop`, restart/runtime validados, aguardando teste/aprovacao do Alan.
- `Homologado`: Alan testou/aprovou funcionalmente em `develop`.
- `Pronto`: conteúdo do card entrou em `main`/produção com evidencia; este e o fechamento final.
- `Cancelado`: nao sera feito ou foi substituido.

O arraste `Aprovação de Design -> Pronto para Dev` aprova a versão específica do `design.md` e, quando existir, do protótipo. Apenas Alan autenticado pode executá-lo. Se uma dessas evidências mudar, a aprovação fica obsoleta e o desenvolvimento deve permanecer bloqueado até nova aprovação. Retornos controlados antes de `Done` são `Aprovação de Design -> Design`, `Code Review -> Em desenvolvimento` e `QA -> Em desenvolvimento`. Se um agente tiver avançado indevidamente para `Em desenvolvimento` sem passar por `Design`/`Aprovação de Design`/`Pronto para Dev`, deve regredir o card para `Design` (ou `Aprovação de Design` se a evidência de design já estiver completa), preservar o trabalho em branch e parar o `/opsx:apply` até a aprovação humana.

**Evidência obrigatória de aprovação de Design:** nenhum código é aplicado (nem `/opsx:apply`, nem edição de arquivos de implementação) sem evidência registrada de aprovação de Design: comentário explícito de Alan no card ou arraste `Aprovação de Design -> Pronto para Dev` no board. A regra vale para todo card, inclusive `UI impact: none`, remoções, bugs e tooling — não existe exceção. Se o veredito do design for `BLOCKED`, o `design.md` deve conter seção de resolução (o que bloqueou, como foi resolvido, quem aprovou) antes de qualquer avanço para `Pronto para Dev`/implementação; `BLOCKED` sem resolução registrada bloqueia o card.

**Checklist de gates no PR/commit de integração:** o PR (e o commit de squash de integração) deve listar, mesmo para mudanças de tooling/docs: change OpenSpec, `design.md`/verdict, `UI impact` e evidência de aprovação de Design (link do comentário ou arraste). O `/opsx:verify` valida essa checklist; PR sem os gates registrados não é integrado.

Nunca mover para `Homologado` sem aprovação explícita de Alan. Nunca mover para `Pronto` sem confirmar merge/publicação em `main` **e deploy/validação em PROD** (source PROD no commit publicado + services PROD reiniciados + URL pública `https://criptofarol.com.br` validada).

**Regra de sync título board/issue:** no momento do `Done`, o título do card no board deve ser idêntico ao título da issue (`gh issue edit <id> --title ...` ou edição equivalente quando o board divergir); se uma divergência for aprovada intencionalmente, registre comentário no card com a aprovação. Divergência sem comentário de aprovação é achado de auditoria.

**Regra de rename de issue com card no board:** o `Title` de item do Project v2 vinculado a issue **não é editável via API Projects v2** — renomear a issue não atualiza o título do card no board. Ao renomear uma issue que possui card no board (antes ou depois do `Done`), o autor SHALL postar no card uma nota de divergência com o formato canônico abaixo, registrando motivo e aprovação; sem a nota, o `release-guard audit` emite warn de divergência de título board/issue:

```text
Nota de divergência
Motivo: <motivo do rename e por que o título do board não foi sincronizado>
Aprovado por: <quem aprovou a divergência>
```

Alternativa preferida quando possível: usar o mesmo texto de título na issue e no card via criação/edição combinada. A nota só dispensa o warn enquanto a divergência existir; se o título do board for sincronizável (item criado no board sem issue vinculada), edite o card diretamente em vez de registrar nota.

**Regra de troca de modelo de subagent:** mudar o modelo/configuração de um subagent (ex.: `vision.md`) exige **nova sessão** (ou nova worktree) para validação da mudança — sessões/spawns em voo continuam no modelo antigo, pois a configuração é lida no spawn. Não assumir que o merge da troca propaga para sessões ativas; a auditoria kaizen reporta `modelo antigo pós-merge` nesses casos.

### Comentários obrigatórios no Kanban

Os comentários de evidência nas transições `Done`, `Homologado` e `Pronto` devem ser postados via `scripts/post-card-evidence-comment.sh` (dedupe por transição + commit ref; 1 comentário por transição por card), com `--transition done|homologado|pronto`, `--card <n>` e `--commit <sha>`:

```bash
scripts/post-card-evidence-comment.sh --transition done --card <n> --commit <sha> --pr <n> --branch <branch> --summary "..." --tests "..." --qa "..." --review "..."
scripts/post-card-evidence-comment.sh --transition homologado --card <n> --commit <sha>
scripts/post-card-evidence-comment.sh --transition pronto --card <n> --commit <sha> --package <release> --cards "<lista>" --deploy "<evidência>" --branches "<lista>"
```

O helper usa os templates abaixo, normaliza a referência de commit (URL, "PR N (sha)", "Commit/merge: <ref>") e não posta duplicado (fail-closed se `gh` falhar ao listar comentários). Use `--dry-run` para validar antes de postar.

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
- diff-reviewer (uncommitted vs HEAD): <no findings | achados | spawn failed>
- diff-reviewer (origin/develop...HEAD): <no findings | achados | reuse SHA | spawn failed>
- code-reviewer: <no findings | achados classificados>
- no blocking findings / achados corrigidos ou classificados
Próximo passo: Alan testar/homologar na develop.
```

Ao observar `Status=Homologado` (arraste de Alan **ou** confirmação em chat), no **mesmo turno** — **mesmo se não houver lote/release** — postar obrigatoriamente via `scripts/post-card-evidence-comment.sh --transition homologado`. `--commit` é o SHA de integração em `develop` (ou `origin/develop` HEAD se o squash não estiver à mão). Falha do helper bloqueia tratar Homologado como evidenciado. Retroativo só se o turno anterior falhou. Texto canônico:
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
Deploy PROD: <commit publicado no source PROD, migrations, build, services reiniciados, URL validada>
Branches limpas: <lista ou pendência>
Status final: pronto.
```

### Release em lote

- Vários cards podem ficar em `Homologado` aguardando publicação conjunta.
- Quando Alan pedir `subir lote`, `fechar lote`, `fechar release`, `criar release`, `gerar release` ou equivalente, liste todos os cards `Homologado` incluídos no pacote, independente do responsavel. Para cards de harness/tooling, liste os commits/branches que entram no pacote.
- Para cards da Clara ou Alan: reviso a documentação do projeto antes de fechar, atualizando Markdown local e Drive quando aplicável.
- Se `develop` contiver só conteúdo homologado do pacote **e** o push/archive em `develop` for permitido, use PR `develop -> main`.
- Se `develop` contiver mudança não homologada, não faça merge direto `develop -> main`; crie `release-*` a partir de `main` e inclua somente commits/branches aprovados, ou peça decisão de Alan.
- **Terceiro caminho (card #617):** se o push do archive/closeout em `refs/heads/develop` for recusado por proteção (`qa-gate` ou equivalente), **mesmo** com pacote só Homologado, não force bypass admin nem “publique o archive em `develop` primeiro”. Crie `release-YYYY-MM-DD` a partir de `origin/develop`, commit o archive (e docs/kaizen do pacote) nessa branch, rode `scripts/release-guard pre` com HEAD em `release-*` (PASS **não** exige archive já em `origin/develop`), abra PR `release-* → main`, merge, deploy PROD, depois sync explícito `main → develop` (PR ou merge) e reexecute `scripts/release-guard post` até árvores idênticas. A ordem canônica #518 (kaizen, PR documental, `RELEASE_BRANCHES`, `post`) permanece; este caminho **insere** o uso de `release-*` + sync, não a substitui.
- Antes de mover cards para `Pronto`, confirme que cada card realmente entrou no merge para `main` **e que o deploy em PROD foi executado e validado** (source PROD no commit publicado + services PROD reiniciados + URL pública validada).
- **Regra de deleção das branches do pacote:** após os cards do pacote moverem para `Pronto`, as branches `change-*`/`card-*`/`release-*` do pacote devem ser deletadas (local e remota) no closeout. O `release-guard post` inventaria e valida: sem `RELEASE_BRANCHES`, lista todas como pendência de classificação (warn/blocker); com `RELEASE_BRANCHES=<branch1,branch2,...>`, exige ausência local+remota. Branch de card não terminal (em fluxo) ou com worktree ativa é preservada e classificada, não deletada.
- **Regra de inventário do guard:** `scripts/release-guard post|audit` lista branches locais e remotas `change-*`/`card-*`/`release-*` com SHA, estado de merge (patch-equivalent via `git cherry origin/develop`) e PR aberto; em `post` estrito, branches não classificadas (não mergeadas ou não deletadas após `Pronto`) são blockers.
- **Regra de archive de changes de cards terminais:** `scripts/release-guard post|audit` detecta changes OpenSpec ativas com todos os artifacts/tasks done cujo card vinculado está em `Pronto`/`Cancelado` (warn em audit, blocker em post) e exige archive/classificação no closeout. Bulk-archive de changes concluídas usa `/opsx:bulk-archive` (CLI `openspec archive`), com exceção operacional registrada quando deltas antigos estão obsoletos em relação ao main spec (`--skip-specs` com justificativa).

### Testes

- Durante implementação: testes focados/proporcionais ao card, validação OpenSpec da change e evidência no handoff.
- Antes de `Code Review`: checks focados e validação OpenSpec da change precisam ter sinal suficiente para revisar o diff. O review nativo é o par `diff-reviewer` + `code-reviewer` (ver seção Code Review local).
- Antes de `QA`: review precisa estar limpo/classificado e o SHA revisado deve estar commitado/pushado.
- Antes de `Done`: `qa-gate` precisa estar verde, checks iniciados precisam terminar, Playwright visual e artifacts precisam estar registrados, e `./restart`/runtime precisam validar o resultado. Status "rodando", `cancelled` ou skip sem dispensa autorizada nao vale como evidência final.
- **Regra de todos completos no fechamento:** `Done`/`/opsx:verify` exige 0 todos `in_progress`/`pending` na sessão Cursor do card (`TodoWrite`). Sessão com todo não concluído não fecha como Done sem classificação explícita. Sessões de card devem ter título descritivo (card/contexto); título genérico em sessão cara é achado de auditoria kaizen.
- No fechamento de lote/release: `openspec validate --all`, testes completos proporcionais ao pacote, build e CI até resultado final.
- Se teste local ou CI falhar, corrija, revalide e só então siga para próximo status.

### QA visual obrigatorio

- Todo card executa Playwright visual por padrão, inclusive cards sem alteração em `frontend/**`.
- Mudança de UI inclui cobertura desktop/mobile da tela afetada e baseline versionado revisado no diff.
- **Rota nova em `frontend/src/App.tsx`:** o check `scripts/check_new_route_playwright_coverage.py` (job `new-route-playwright-coverage`, dependência do `qa-gate`) falha se o path de produto não estiver no inventário `frontend/tests/e2e/route-coverage-inventory.json` com spec funcional+visual. Aliases `Navigate`, `PrototypeRedirect` e `/prototypes/*` ficam de fora. Rotas já existentes entram no inventário como `covered` ou `grandfathered`; rota nova exige spec **e** atualização do inventário no mesmo diff. Skip silencioso não existe.
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
2. Revisar **somente** o `diff.png` (ou o diff git dos snapshots) dos cenarios que mudaram, uma vez, para confirmar que a mudanca e esperada. Julgamento visual usa `Read` na sessão Cursor depois do path-check.
3. Commitar os novos arquivos em `frontend/tests/e2e/**/*-snapshots/` junto com a mudanca de UI.
4. Push → CI revalida contra a baseline nova.

**Proibido por padrao**

```text
CI falha → baixar artifacts → Read/vision em todos os PNG
→ patch baseline → push → Waiting/polling → repetir
```

Olhar screenshot so para aprovar mudanca intencional (`diff.png` preferivel) ou quando Alan pedir julgamento visual/exploratorio — nesses casos use `Read` na sessão depois de confirmar o path.

**Regra de path-check antes de análise visual (zero respawn):** confirme a existência de cada path (`ls`/glob) e a validade da URL; path inexistente ou URL inválida bloqueia a leitura. Gere o artefato no caminho canônico antes de tentar de novo — proibido repetir o mesmo path inexistente.
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
# in-flight: PRESERVED_BRANCHES=card-569-code-review-bugbot,card-581-release-guard-preserve
RELEASE_DATE=YYYY-MM-DD \
RELEASE_CARDS=<n1,n2,...> \
PRESERVED_BRANCHES="${PRESERVED_BRANCHES:-}" \
scripts/release-guard pre
openspec validate --all
gh pr create --base main --head develop --title "<titulo>" --body "<resumo>"
gh pr merge --merge --delete-branch=false
scripts/release-guard post   # inclui check de change OpenSpec duplicada (ativa + arquivada)
# sync main -> develop (quando necessário neste caminho develop→main) e reexecute post após o merge de sync
```

Publicar com branch de release quando `develop` tiver conteúdo não homologado **ou** quando o push do archive em `develop` for recusado por proteção (`qa-gate`), mesmo com pacote só Homologado:
```bash
# Caso A — develop com não-homologado: base main + cherry-picks aprovados
git switch main && git pull origin main
git switch -c release-YYYY-MM-DD
git cherry-pick <commit-homologado>

# Caso B — archive bloqueado em develop (proteção/qa-gate): base origin/develop + archive
# git fetch origin && git switch -c release-YYYY-MM-DD origin/develop
# (commitar openspec/changes/archive/** + docs/kaizen do pacote nesta branch)

git push origin release-YYYY-MM-DD
RELEASE_DATE=YYYY-MM-DD \
RELEASE_CARDS=<n1,n2,...> \
PRESERVED_BRANCHES="${PRESERVED_BRANCHES:-}" \
scripts/release-guard pre
# pre em release-* NÃO exige archive já em origin/develop; não use "publique archive em develop primeiro"
gh pr create --base main --head release-YYYY-MM-DD --title "<titulo>" --body "<resumo>"
gh pr merge --merge --delete-branch=false
# deploy PROD + evidência (contrato existente), depois:
# sync main → develop (PR ou merge) — OBRIGATÓRIO no caminho archive-via-release-* (Caso B e quando o archive só está na tip da release-*) antes do post final
gh pr create --base develop --head main --title "sync: main → develop após release-YYYY-MM-DD" --body "Alinha árvores para release-guard post"
# merge do sync, então:
scripts/release-guard post
# se o post falhar por árvores divergentes, complete o sync e reexecute o post
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
- Para promover produção, junte todos os cards `Homologado` incluídos no lote/release pedido por Alan. Para cards de harness/tooling, confirme commits/branches incluídos, abra PR para `main`, resolva checks/políticas bloqueantes quando forem corrigíveis por código/configuração do repo e realize o merge manual do PR. Para cards de `Clara` ou `Alan`, revise e atualize a documentação do projeto em Markdown local e Drive quando aplicável. Depois mova os cards incluídos para `Pronto`.
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
- Workflow OpenSpec/Cursor: `openspec/changes/` e `openspec/specs/`

## Convenções de UI/UX (Lab)

- Para qualquer tarefa em `frontend/`, use o `DESIGN.md` como fonte obrigatória de qualidade visual, tokens, componentes, densidade, responsividade e validação.
- Para qualquer tela, componente visual ou funcionalidade com impacto de UI/UX, nova ou antiga, consulte e siga obrigatoriamente o `DESIGN.md` antes de implementar.
  - Registre no OpenSpec/hand-off quais tokens, componentes e padrões do `DESIGN.md` foram aplicados.
  - Não feche implementação visual sem validar aderência ao `DESIGN.md` em desktop/mobile quando aplicável.
  - Se houver desvio necessário do `DESIGN.md`, registre a exceção e a justificativa antes de codar ou fechar a entrega.
- **Upstream** deve ser uma conversa fluida (Humano ↔ Trader) para clarificar inputs/constraints/risco.
- O label "validator" na UI/copy deve aparecer como **Trader**.

## Agentes e responsabilidades

O time é composto por 6 agentes, cada um com papel definido:

### main — Project Manager / Team Leader
**Template base:** Orion (productivity)

Orquestra o time, coordena workflow, delegation, status reports, prazos.
- Mantém conversa com Alan curta e gerencial.
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

### Kaizen — Process Improvement (melhoria contínua)
Audita como o processo está sendo executado e transforma fricções em melhorias. Princípio: **quanto mais o processo é usado, melhor ele fica** — cada auditoria gera evidência, as correções aprovadas viram regras/skills/scripts, e o próximo ciclo valida se a fricção sumiu.
- Execução: `/kaizen` (completa), `/kaizen card <id>` (pós-card), `/kaizen release` (pós-release, obrigatória no fechamento de lote).
- **Read-only na auditoria**: a skill `.cursor/skills/kaizen/SKILL.md` coleta evidências (board, Git, OpenSpec, CI, transcripts Cursor, tech debt); o principal consolida e cadastra.
- **Análise de sessões Cursor** (escopo = release): correlaciona cards do pacote (`#<id>`/`card-<id>`) com transcripts Cursor do projeto e detecta onde o modelo se perde/alucina (caminho/URL inventado, loop sem progresso, custo alto sem `Done`, subagent falhando, TODO eterno).
- **Atua como PO ao registrar melhorias**: 1 card por melhoria (formato `## Proposta (PO)`, critérios de aceite, classificação change/story/bug), labels `kaizen`, campos do board preenchidos, dependências linkadas. **Todo card kaizen é criado em `Status=Em Refinamento`** (entrada obrigatória de todo card novo) e segue o fluxo normal do board a partir daí (`Em Refinamento -> Todo -> ...`) — nunca é criado direto em coluna de execução. **Máximo 3 cards kaizen por release** — a priorização define os 3 que entram; o resto fica no backlog para releases seguintes.
- **Priorização visível**: campo `Prioridade` P0/P1/P2 preenchido na criação (regra severidade × frequência / esforço; P0 = risco/segurança/falha recorrente/alucinação cara → semana atual; P1 = quick win/higiene → próxima; P2 = desejável → backlog); View "Kaizen" no board agrupada por prioridade (criada manualmente no Project 1 — não automatizável via CLI; ver card #420); override humano sempre possível.
- **Propõe, Alan aprova**: Kaizen nunca implementa. Pode propor melhorias de skills e pesquisar alternativas (busca read-only) quando a atual não atender; troca/criação só após aprovação de Alan.
- **Segurança**: issues públicas só com métricas agregadas e IDs; trechos de sessões apenas em `docs/kaizen-log.md`.
- Registro de achados: `docs/kaizen-log.md` (append-only) + `decision-log.md` para mudanças de processo. Padrão recorrente em 2+ auditorias eleva severidade e vira candidato a promoção de regra.

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
- **Regra de auto-trigger:** quando o status da change avança no runtime, acionar o responsável pela nova etapa. Em `Design`, acionar o Designer/Critic Agent; em `Aprovação de Design`, aguardar Alan; em `Em desenvolvimento`, acionar DEV; em `QA`, acionar QA.
- **Regra de validação QA:** Antes de enviar para homologação Alan, QA deve rodar testes E2E (`frontend/tests/*.spec.ts`) e revisar evidências registradas no fluxo operacional.
- Lock padrão fica no nível da **story**; bug filho herda esse lock salvo reassignment explícito.
- Uma **story** só pode ser fechada quando todos os **bugs filhos** estiverem concluídos.
- Antes de promover para `Aprovação de Design`, `Pronto para Dev`, `QA`, `Done`, `Homologado` ou `Pronto`, reconciliar runtime + `openspec/changes/<change>/tasks.md` + handoff e as evidências exigidas pelo gate.

### Uso padrão de subagents

Para tarefas médias ou grandes, o agente principal deve orquestrar subagents quando houver benefício claro de paralelismo, investigação independente ou revisão especializada.

Contrato de modelo:
- A sessão principal define o LLM/modelo e sua versão para todo o turno.
- Cada subagent deve executar no mesmo LLM/modelo da sessão (chat). A função do agente não autoriza trocar de modelo sem pedido explícito de Alan.
- O effort deve acompanhar a sessão principal por padrão. Se divergir por exigência do cliente, registrar a exceção sem alterar o LLM/modelo.
- Antes de aceitar o retorno, verificar a igualdade do modelo na evidência runtime disponível. Sem evidência observável, manter a tarefa na sessão principal.
- Para críticas independentes, usar contextos separados; reviewers permanecem read-only e o agente principal consolida e corrige.
- Não usar fallback nem perfil built-in com outro modelo sem pedido explícito de Alan.

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

Arquitetura preferida no Cursor (`Task` com `inherit`, salvo pedido explícito):
- `generalPurpose` para mapear fluxos, diffs, bugs, OpenSpec e os dois reviewers de Code Review (prompts = `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md`, read-only);
- `bugbot` / `security-review` **somente** quando Alan pedir `/review-bugbot` ou `/review-security` no card (produto gerenciado; não é o caminho feliz);
- análise de imagem na própria sessão via `Read` após path-check;
- Design: a sessão principal escreve artifacts; crítica em `Task` isolada sem editar.

O agente principal continua responsável por consolidar decisões, evitar trabalho duplicado, respeitar o escopo do OpenSpec/workflow DB e entregar o resultado final.

## Engenharia de prompt

Reforço de fluxo de fechamento: `Done` conclui somente a implementação validada em `develop` (Done tecnico); `Homologado` conclui aprovação funcional de Alan em `develop`; `Pronto` conclui produção após merge manual em `main` (via PR `develop -> main`) com validação e evidências registradas.

Se for necessário mudar o tom de um agente (ex: deixar o design mais exploratório ou o DEV mais cauteloso), primeiro atualiza este arquivo com o novo prompt/personalidade e registra no `openspec/changes/<change>/` do fluxo ativo. Nunca altere agentes apenas via jobs sem documentar aqui.
